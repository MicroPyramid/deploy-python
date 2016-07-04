from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists
from fabric.utils import abort
from fabric import colors
from datetime import datetime
import yaml
import curses


config = {}
data = config.get("local") or {}
run_on = "local"
env.hosts = ['localhost']
backup_local_file = ""
backup_server_file = ""


@task
def setup(config_file_path):
    global config
    global data
    global backup_local_file

    try:
        config = yaml.load(open(config_file_path))
    except IOError as e:
        print(str(e))
        abort(colors.red("No such file. Please add a configuration "
                         "file similar to sample_config.yaml\n"))
    except Exception as e:
        print(str(e))
        abort(colors.red("Please check the configuration file. "
                         "It should be a YAML file similar to "
                         "sample_config.yaml\n"))
    else:
        if config is None:
            config = {}
        data = config.get("local") or {}
        if data and data.get("project_root"):
            backup_local_file = data.get("project_root") + \
                '/local_db_backup_%s.sql' % str(datetime.now().date())


@task
def run_local():
    global run_on
    global data
    env.hosts = ['localhost']
    run_on = "local"
    data = config.get("local") or {}


@task
def run_stage():
    global run_on
    global data
    env.hosts = []
    run_on = "stage"
    data = config.get("stage") or {}
    if config.get("stage") and config.get("stage").get("servers"):
        env.hosts = list(config.get("stage").get("servers"))
        backup_server_file = data.get("project_root") + \
            '/server_db_backup_%s.sql' % str(datetime.now().date())


@task
def run_live():
    global run_on
    global data
    env.hosts = []
    run_on = "live"
    data = config.get("live") or {}
    if config.get("live") and config.get("live").get("servers"):
        env.hosts = list(config.get("live").get("servers"))
        backup_server_file = data.get("project_root") + \
            '/server_db_backup_%s.sql' % str(datetime.now().date())


def get_function():
    if not config:
        abort(colors.red("Please check the configuration file. "
                         "It should be a YAML file similar to "
                         "sample_config.yaml\n"))

    if run_on == "local":
        return local
    else:
        if not env.hosts:
            print("Please check the hosts(servers) settings for '%s' "
                  "in the config file." % str(run_on))
            return None
        return run


@task
def activate_env_install_requirements():
    function = get_function()
    if not function:
        return

    if data and data.get("env_path") and data.get("requirements_file"):
        with cd(data.get("env_path")):
            function(
                "/bin/bash -l -c 'source %s/bin/activate && pip install -r %s'"
                % (data.get("env_path"), data.get("requirements_file"))
            )
    else:
        print("Please check the '%s' env and requirements file "
              "paths in the config file." % str(run_on))


def manage_py(command):
    function = get_function()
    if not function:
        return

    if data and data.get("env_path") and data.get("repository_root"):
        with cd(data.get("repository_root")):
            function(
                "/bin/bash -l -c 'source %s/bin/activate && " % (
                    data.get("env_path")
                ) + "python %s/manage.py %s'" % (
                    data.get("repository_root"), command)
            )
    else:
        print("Please check the '%s' env_path and repository_root "
              "in the config file." % str(run_on))


@task
def migrate():
    manage_py("migrate")


@task
def collect_static():
    manage_py("collectstatic")


@task
def rebuild_index():
    manage_py('rebuild_index --noinput')


@task
def restart_celery():
    function = get_function()
    if not function:
        return

    function('supervisorctl restart celeryd')


@task
def deploy():
    activate_env_install_requirements()
    migrate()
    # collect_static()


@task
def rsync_with_settings():
    if (
        config.get("local") and config.get("local").get("repository_root") and
        data and data.get("repository_root")
    ):
        rsync_project(
            local_dir=config.get("local").get("repository_root") + '/',
            remote_dir=data.get("repository_root") + '/',
            exclude=['.git', 'db.sqlite3', 'settings_local.py',
                     '.pyc', '__pycache__', 'CACHE']
        )
    else:
        print("Please check the 'local' and '%s' repository_root paths "
              "in the config file." % str(run_on))


@task
def rsync_without_settings():
    if (
        config.get("local") and config.get("local").get("repository_root") and
        data and data.get("repository_root")
    ):
        rsync_project(
            local_dir=config.get("local").get("repository_root") + '/',
            remote_dir=data.get("repository_root") + '/',
            exclude=['.git', 'db.sqlite3', 'settings.py', 'settings_local.py',
                     '.pyc', '__pycache__', 'CACHE']
        )
    else:
        print("Please check the 'local' and '%s' repository_root paths "
              "in the config file." % str(run_on))


# Deploy project to remote host
@task
def deploy_to_server(sync_with_setting="False", debug="False"):
    function = get_function()
    if not function:
        return
    if not data:
        print("Please configure the '%s' settings "
              "in the config file." % str(run_on))
        return

    # Check for required settings
    missing_required = []
    for each in ["project_root", "env_path", "repository_root",
                 "uwsgi_file_path", "uwsgi_file"]:
        if each not in data.keys() or not data.get(each).strip():
            missing_required.append(each)
    if missing_required:
        print("\nPlease configure %s for '%s' in the config file." % (
            ", ".join(missing_required), str(run_on)
        ))
        return

    # All settings are been specified, deploy to the server.
    if not exists(data.get("project_root")):
        # Create a directory if it doesn't exists
        print(
            "'\n{directory}' directory does not exists in '{host}'.\n"
            "Creating missing '{directory}' directory in '{host}' ...".format(
                directory=data.get("project_root").split("/")[-1],
                host=str(run_on)
            )
        )
        function("mkdir -p %s" % data.get("project_root"))

    if not exists(data.get("env_path")):
        # Create a virtualenv if it doesn't exists
        print(
            "\nVirtualenv does not exists in '%s'\n"
            "Creating new virtual environment in '%s' directory ..." % (
                str(run_on), data.get("project_root").split("/")[-1])
        )
        with cd(data.get("project_root")):
            function("virtualenv env")

    # Sync the remote directory with the current project directory.
    if sync_with_setting.lower() == "true":
        rsync_with_settings()
    elif sync_with_setting.lower() == "false":
        rsync_without_settings()

    # Install requirements and run migrate.
    deploy()

    # Change static files mode
    # function("sudo chmod 755 -R %s/static/" % data.get("repository_root"))

    # Restart the nginx server
    # function("sudo service nginx restart")

    if debug.lower() == "true":
        # Run the uWSGI Server
        with cd(data.get("uwsgi_file_path")):
            function("uwsgi --ini %s" % data.get("uwsgi_file"))
    elif debug.lower() == "false":
        if exists("/etc/uwsgi/vassals/%s" % data.get("uwsgi_file")):
            function("rm /etc/uwsgi/vassals/%s" % data.get("uwsgi_file"))

        function("ln -s %s/%s /etc/uwsgi/vassals/" % (
            data.get("uwsgi_file_path"), data.get("uwsgi_file")))

        function("touch /etc/uwsgi/vassals/%s" % data.get("uwsgi_file"))
    else:
        pass
    print("\nSucessfully deployed to the Server")


def do_database_checks():
    function = get_function()
    if not function:
        return False
    if not data:
        print("Please configure the '%s' settings "
              "in the config file." % str(run_on))
        return False
    if not backup_local_file:
        print("Please configure the 'local' project_root settings "
              "in the config file.")
        return False

    # Check for required settings
    missing_required = []
    for each in ["db_name", "db_username", "database", "project_root"]:
        if each not in data.keys() or not data.get(each).strip():
            missing_required.append(each)

    if missing_required:
        print("\nPlease configure %s for '%s' in the config file." % (
            ", ".join(missing_required), str(run_on)
        ))
        return False

    if data.get("database").lower() not in ["mysql", "postgres"]:
        print("\nPlease check the database settings for '%s'. "
              "Valid choices are 'mysql/postgres' only." % str(run_on))
        return False

    return function


@task
def take_server_backup():
    function = do_database_checks()
    if not function:
        return

    if data.get("database").lower() == "mysql":
        run("mysqldump -u %s -p %s > %s" % (
            data.get("db_username"),
            data.get("db_name"),
            backup_server_file
        ))
    elif data.get("database").lower() == "postgres":
        run("pg_dump -U %s -h localhost %s > %s" % (
            data.get("db_username"),
            data.get("db_name"),
            backup_server_file
        ))
    else:
        pass
    # get(local_path=backup_local_file, remote_path=backup_server_file)
    # function('rm %s' % backup_server_file)


@task
def take_local_backup():
    function = do_database_checks()
    if not function:
        return

    if data.get("database").lower() == "mysql":
        local("mysqldump -u %s -p %s > %s" % (
            data.get("db_username"),
            data.get("db_name"),
            backup_local_file
        ))
    elif data.get("database").lower() == "postgres":
        local("pg_dump -U %s -h localhost %s > %s" % (
            data.get("db_username"),
            data.get("db_name"),
            backup_local_file
        ))
    else:
        pass
    # put(local_path=backup_local_file, remote_path=backup_server_file)
    # local('rm %s' % backup_local_file)


@task
def restore_to_local():
    function = do_database_checks()
    if not function:
        return

    get(local_path=backup_local_file, remote_path=backup_server_file)

    if data.get("database").lower() == "mysql":
        local("mysql -u %s -p %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_local_file))
    elif data.get("database").lower() == "postgres":
        local("psql -U %s -h localhost %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_local_file))
    else:
        pass


@task
def restore_to_server():
    function = do_database_checks()
    if not function:
        return

    put(local_path=backup_local_file, remote_path=backup_server_file)

    if data.get("database").lower() == "mysql":
        function("mysql -u %s -p %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_server_file))
    elif data.get("database").lower() == "postgres":
        function("psql -U %s -h localhost %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_server_file))
    else:
        pass


@task
def reset_local_db():
    function = do_database_checks()
    if not function:
        return

    if data.get("database").lower() == "mysql":
        try:
            local('mysql -u %s -p -e "drop database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
        try:
            local('mysql -u %s -p -e "create database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
    elif data.get("database").lower() == "postgres":
        try:
            local('sudo -u %s psql -c "drop database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
        try:
            local('sudo -u %s psql -c "create database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
    else:
        pass


@task
def reset_server_db():
    function = do_database_checks()
    if not function:
        return

    if data.get("database").lower() == "mysql":
        try:
            function('mysql -u %s -p -e "drop database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
        try:
            function('mysql -u %s -p -e "create database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
    elif data.get("database").lower() == "postgres":
        try:
            function('sudo -u %s psql -c "drop database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
        try:
            function('sudo -u %s psql -c "create database %s"' % (
                data.get("db_username"), data.get("db_name")))
        except:
            pass
    else:
        pass


@task
def restart_supervisior():
    function = get_function()
    if not function:
        return

    function('supervisorctl reload')


@task
def restart_server():
    function = get_function()
    if not function:
        return

    function('sudo reboot')


@task
def restart_uwsgi():
    function = get_function()
    if not function:
        return

    function('sudo service uwsgi restart')


def local_start():

    def highlight_printer(x, y, text, position):
        screen.addstr(x, y, text[0:position])
        screen.addstr(x, y + position, text[position], curses.color_pair(1))
        screen.addstr(x, y + position + 1, text[position + 1:])

    def highlight_line(x, y, text):
        screen.addstr(x, y, text, curses.color_pair(2))

    def perform_action(x, y, action):
        echo = screen.getch(x, y)
        while echo not in [ord('y'), ord('Y'), ord('n'), ord('N')]:
            echo = screen.getch(x, y)
        else:
            if echo == ord('y') or echo == ord('Y'):
                curses.endwin()
                action()
            screen.clear()
            local_start()

    screen = curses.initscr()

    if curses.has_colors():
        curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_GREEN)

    screen.addstr(5, 35,      "+----------------------------+")
    screen.addstr(6, 35,      "|   Management Options       |")
    screen.addstr(7, 35,      "+----------------------------+")
    highlight_printer(8, 35,  "| Backup Local DB            |", 2)
    highlight_printer(9, 35,  "| Update Local env           |", 9)
    highlight_printer(10, 35, "| Collect Static             |", 3)
    highlight_printer(11, 35, "| Rebuild Search Index       |", 17)
    highlight_printer(12, 35, "| Restart Celery             |", 10)
    highlight_printer(13, 35, "| Reset Local DB             |", 6)
    highlight_printer(14, 35, "| Apply Migrations           |", 8)
    highlight_printer(15, 35, "| Quit                       |", 2)
    screen.addstr(16, 35,     "+----------------------------+")

    screen.refresh()
    curses.noecho()
    while 1:
        c = screen.getch()
        if c == ord('b') or c == ord('B'):
            highlight_line(8, 36, " Backup Local DB            ")
            screen.addstr(20, 35, "Are you sure? You want to take the local DB backup?(Y/N):")
            perform_action(20, 93, take_local_backup)
            break
        elif c == ord('l') or c == ord('L'):
            highlight_line(9, 36, " Update Local env           ")
            screen.addstr(20, 35, "Are you sure? You want to update local env?(Y/N):")
            perform_action(20, 85, activate_env_install_requirements)
            break
        elif c == ord('o') or c == ord('O'):
            highlight_line(10, 36, " Collect Static             ")
            screen.addstr(20, 35, "Are you sure? You want to run collect static?(Y/N):")
            perform_action(20, 87, collect_static)
            break
        elif c == ord('i') or c == ord('I'):
            highlight_line(11, 36, " Rebuild Search Index       ")
            screen.addstr(20, 35, "Are you sure? You want to rebuild search index?(Y/N):")
            perform_action(20, 89, rebuild_index)
            break
        elif c == ord('c') or c == ord('c'):
            highlight_line(12, 36, " Restart Celery             ")
            screen.addstr(20, 35, "Are you sure? You want to restart celery?(Y/N):")
            perform_action(20, 83, restart_celery)
            break
        elif c == ord('t') or c == ord('T'):
            highlight_line(13, 36, " Reset Local DB             ")
            screen.addstr(20, 35, "Are you sure? You want to reset local db?(Y/N):")
            perform_action(20, 83, reset_local_db)
            break
        elif c == ord('m') or c == ord('M'):
            highlight_line(14, 36, " Apply Migrations           ")
            screen.addstr(20, 35, "Are you sure? You want to apply migrations?(Y/N):")
            perform_action(20, 85, migrate)
            break
        elif c == ord('q') or c == ord('Q'):
            break  # Exit the while()

    # screen.getch()
    curses.endwin()


def server_start():

    def highlight_printer(x, y, text, position):
        screen.addstr(x, y, text[0:position])
        screen.addstr(x, y + position, text[position], curses.color_pair(1))
        screen.addstr(x, y + position + 1, text[position + 1:])

    def highlight_line(x, y, text):
        screen.addstr(x, y, text, curses.color_pair(2))

    def perform_action(x, y, action):
        echo = screen.getch(x, y)
        while echo not in [ord('y'), ord('Y'), ord('n'), ord('N')]:
            echo = screen.getch(x, y)
        else:
            if echo == ord('y') or echo == ord('Y'):
                curses.endwin()
                action()
            screen.clear()
            server_start()

    screen = curses.initscr()

    if curses.has_colors():
        curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_GREEN)

    screen.addstr(5, 35,      "+----------------------------+")
    screen.addstr(6, 35,      "|   Management Options       |")
    screen.addstr(7, 35,      "+----------------------------+")
    highlight_printer(8, 35,  "| Deploy To Server           |", 2)
    highlight_printer(9, 35,  "| Push Local DB to Server    |", 2)
    highlight_printer(10, 35, "| Backup Server DB           |", 2)
    highlight_printer(11, 35, "| Restore Server DB to Local |", 3)
    highlight_printer(12, 35, "| Update Server env          |", 9)
    highlight_printer(13, 35, "| Restart Server             |", 2)
    highlight_printer(14, 35, "| Restart uWSGI              |", 10)
    highlight_printer(15, 35, "| Collect Static             |", 3)
    highlight_printer(16, 35, "| Rebuild Search Index       |", 17)
    highlight_printer(17, 35, "| Restart Celery             |", 10)
    highlight_printer(18, 35, "| Reset Server DB            |", 11)
    highlight_printer(19, 35, "| Restart Supervisorctl      |", 6)
    highlight_printer(20, 35, "| Apply Migrations           |", 8)
    highlight_printer(21, 35, "| Quit                       |", 2)
    screen.addstr(22, 35,     "+----------------------------+")

    screen.refresh()
    curses.noecho()
    while 1:
        c = screen.getch()
        if c == ord('d') or c == ord('D'):
            highlight_line(8, 36, " Deploy To Server           ")
            screen.addstr(26, 35, "Are you sure? You want to deploy the code?(Y/N):")
            perform_action(26, 84, deploy_to_server)
            break
        elif c == ord('p') or c == ord('P'):
            highlight_line(9, 36, " Push Local DB to Server    ")
            screen.addstr(26, 35, "Are you sure? You want to Push Local DB to Server?(Y/N):")
            echo = screen.getch(26, 92)
            while echo not in [ord('y'), ord('Y'), ord('n'), ord('N')]:
                echo = screen.getch(26, 92)
            else:
                if echo == ord('y') or echo == ord('Y'):
                    curses.endwin()
                    take_local_backup()
                    restore_to_server()
                screen.clear()
                server_start()
            break
        elif c == ord('b') or c == ord('B'):
            highlight_line(10, 36, " Backup Server DB           ")
            screen.addstr(26, 35, "Are you sure? You want to take the server DB backup?(Y/N):")
            perform_action(26, 93, take_server_backup)
            break
        elif c == ord('e') or c == ord('e'):
            highlight_line(11, 36, " Restore Server DB to Local ")
            screen.addstr(26, 35, "Are you sure? You want to Restore the server DB to Local?(Y/N):")
            echo = screen.getch(26, 99)
            while echo not in [ord('y'), ord('Y'), ord('n'), ord('N')]:
                echo = screen.getch(26, 99)
            else:
                if echo == ord('y') or echo == ord('Y'):
                    curses.endwin()
                    take_server_backup()
                    restore_to_local()
                screen.clear()
                server_start()
            break
        elif c == ord('s') or c == ord('S'):
            highlight_line(12, 36, " Update Server env          ")
            screen.addstr(26, 35, "Are you sure? You want to update server env?(Y/N):")
            perform_action(26, 86, activate_env_install_requirements)
            break
        elif c == ord('r') or c == ord('R'):
            highlight_line(13, 36, " Restart Server             ")
            screen.addstr(26, 35, "Are you sure? You want to restart the server?(Y/N):")
            perform_action(26, 87, restart_server)
            break
        elif c == ord('u') or c == ord('U'):
            highlight_line(14, 36, " Restart uWSGI              ")
            screen.addstr(26, 35, "Are you sure? You want to restart the uWSGI?(Y/N):")
            perform_action(26, 87, restart_uwsgi)
            break
        elif c == ord('o') or c == ord('O'):
            highlight_line(15, 36, " Collect Static             ")
            screen.addstr(26, 35, "Are you sure? You want to run collect static?(Y/N):")
            perform_action(26, 87, collect_static)
            break
        elif c == ord('i') or c == ord('I'):
            highlight_line(16, 36, " Rebuild Search Index       ")
            screen.addstr(26, 35, "Are you sure? You want to rebuild search index?(Y/N):")
            perform_action(26, 89, rebuild_index)
            break
        elif c == ord('c') or c == ord('c'):
            highlight_line(17, 36, " Restart Celery             ")
            screen.addstr(26, 35, "Are you sure? You want to restart celery?(Y/N):")
            perform_action(26, 83, restart_celery)
            break
        elif c == ord('v') or c == ord('V'):
            highlight_line(18, 36, " Reset Server DB             ")
            screen.addstr(26, 35, "Are you sure? You want to reset server db?(Y/N):")
            perform_action(26, 84, reset_server_db)
            break
        elif c == ord('a') or c == ord('A'):
            highlight_line(19, 36, " Restart Supervisorctl      ")
            screen.addstr(26, 35, "Are you sure? You want to restart supervisorctl?(Y/N):")
            perform_action(26, 90, restart_supervisior)
            break
        elif c == ord('m') or c == ord('M'):
            highlight_line(20, 36, " Apply Migrations           ")
            screen.addstr(26, 35, "Are you sure? You want to apply migrations?(Y/N):")
            perform_action(26, 85, migrate)
            break
        elif c == ord('q') or c == ord('Q'):
            break  # Exit the while()

    # screen.getch()
    curses.endwin()


@task
def start_live():
    run_live()
    server_start()


@task
def start_local():
    run_local()
    local_start()


@task
def start_stage():
    run_stage()
    server_start()
