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

