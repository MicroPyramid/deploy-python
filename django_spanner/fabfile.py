from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists
from fabric.utils import abort
from fabric import colors
from datetime import datetime
import yaml


config = {}
data = config.get("local") or {}
run_on = "local"
env.hosts = ['localhost']
backup_local_file = ''


def setup(config_file_path):
    global config
    global data
    global backup_local_file

    try:
        config = yaml.load(open(config_file_path))
    except IOError as e:
        print(str(e))
        abort(colors.red("No such file. Please add a configuration "
                         "file same as sample_config.yaml\n"))
    except Exception as e:
        print(str(e))
        abort(colors.red("Please check the configuration file. "
                         "It should be a YAML file same as "
                         "sample_config.yaml\n"))
    else:
        data = config.get("local") or {}
        if data and data.get("project_root"):
            backup_local_file = data.get("project_root") + \
                '/server_db_backup_%s.sql' % str(datetime.now().date())


def run_local():
    global run_on
    global data
    env.hosts = ['localhost']
    run_on = "local"
    data = config.get("local") or {}


def run_stage():
    global run_on
    global data
    env.hosts = []
    run_on = "stage"
    data = config.get("stage") or {}
    if config.get("stage") and config.get("stage").get("servers"):
        env.hosts = list(config.get("stage").get("servers"))


def run_live():
    global run_on
    global data
    env.hosts = []
    run_on = "live"
    data = config.get("live") or {}
    if config.get("live") and config.get("live").get("servers"):
        env.hosts = list(config.get("live").get("servers"))


def get_function():
    if run_on == "local":
        return local
    else:
        if not env.hosts:
            print("Please check the hosts(servers) settings for '%s' "
                  "in the config file." % str(run_on))
            return None
        return run


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


def migrate():
    manage_py("migrate")


def collect_static():
    manage_py("collectstatic")


def rebuild_index():
    manage_py('rebuild_index --noinput')


def restart_celery():
    function = get_function()
    if not function:
        return

    function('supervisorctl restart celeryd')


def deploy():
    activate_env_install_requirements()
    migrate()
    # collect_static()


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


def take_database_backup():
    function = do_database_checks()
    if not function:
        return

    backup_server_file = data.get("project_root") + \
        '/local_db_backup_%s.sql' % str(datetime.now().date())

    if data.get("database").lower() == "mysql":
        function("mysqldump -u %s -p %s > %s" % (
            data.get("db_username"), data.get("db_name"), backup_server_file)
        )
    elif data.get("database").lower() == "postgres":
        function("pg_dump -U %s -h localhost %s > %s" % (
            data.get("db_username"), data.get("db_name"), backup_server_file)
        )
    else:
        pass

    if not run_on == "local":
        get(local_path=backup_local_file, remote_path=backup_server_file)
        function('rm %s' % backup_server_file)


def restore_to_local():
    function = do_database_checks()
    if not function:
        return

    if data.get("database").lower() == "mysql":
        local("mysql -u %s -p %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_local_file))
    elif data.get("database").lower() == "postgres":
        local("psql -U %s -h localhost %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_local_file))
    else:
        pass


def restore_to_server():
    function = do_database_checks()
    if not function:
        return

    backup_server_file = data.get("project_root") + \
        '/local_db_backup_%s.sql' % str(datetime.now().date())

    if data.get("database").lower() == "mysql":
        function("mysql -u %s -p %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_server_file))
    elif data.get("database").lower() == "postgres":
        function("psql -U %s -h localhost %s < %s" % (
            data.get("db_username"), data.get("db_name"), backup_server_file))
    else:
        pass


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


def restart_supervisior():
    function = get_function()
    if not function:
        return

    function('supervisorctl reload')


def restart_server():
    function = get_function()
    if not function:
        return

    function('sudo reboot')


def restart_uwsgi():
    function = get_function()
    if not function:
        return

    function('sudo service uwsgi restart')
