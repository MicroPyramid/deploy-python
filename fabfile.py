import os
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists
# import django
import datetime
import yaml

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "microsite.settings")
# django.setup()

full_path = os.path.realpath(__file__).split('fabfile.py')[0] + 'config.yaml'
config = yaml.load(open(full_path))
data = config.get("local") or {}
run_on = "local"
env.hosts = ['localhost']


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
    print("get_function")
    print(run_on)
    print(env.hosts)
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

    run('supervisorctl restart celeryd')


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
