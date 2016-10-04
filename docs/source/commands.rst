Commands
===========

Usage
-------

    .. code-block:: python

        fab <run_local/run_stage/run_live> <command_name>


    **List Commands** - shows the list of all available fab commands


        .. code-block:: python

            fab -l


Install Requirements
----------------------

* To install the requirements on your local system:

    .. code-block:: python

        fab run_local activate_env_install_requirements

                (or)

        fab activate_env_install_requirements

* To install the requirements on your remote staging servers:

    .. code-block:: python

        fab run_stage activate_env_install_requirements

* To install the requirements on your remote live servers:

    .. code-block:: python

        fab run_live activate_env_install_requirements


Rsync project to remote server(stage/live)
---------------------------------------------

To rsync project local files to remote destination server -

    * with settings file -

        .. code-block:: python

            fab <run_stage/run_live> rsync_with_settings

    * without settings file -

        .. code-block:: python

            fab <run_stage/run_live> rsync_without_settings


Deploy To Server
------------------

This commands copy local project files to destination(stage/live) servers, installs requirements, applies migrations and finally runs uWSGI server(both in debug and deployment modes)

    .. code-block:: python

            fab <run_stage/run_live> deploy_to_server

    By default, this command rsyncs project files without settings file and runs touch command for project uwsgi file under /etc/uwsgi/vassals/ folder.

    * To rsync with settings file and to run uwsgi in debug mode:

        .. code-block:: python

            fab <run_stage/run_live> deploy_to_server:sync_with_setting='true',debug='true'


    .. note::

        It automatically creates project_root, env in server if not exists


Local database backup
-----------------------

    .. code-block:: python

        fab take_local_backup


Server database backup
------------------------

    .. code-block:: python

        fab <run_stage/run_live> take_server_backup


Restore Server database to Local
---------------------------------

.. code-block:: python

        fab <run_stage/run_live> take_server_backup
        fab restore_to_local


Reset Local database
-----------------------

    .. code-block:: python

        fab reset_local_db


Reset Server database
-----------------------

    .. code-block:: python

        fab <run_stage/run_live> reset_server_db


Run Management Commands
--------------------------

This function is used to run management commands -

    .. code-block:: python

            fab <run_local/run_stage/run_live> manage_py:<management_command_name>

    * To apply migrations

        .. code-block:: python

                fab <run_local/run_stage/run_live> migrate

    * Execute collect static

        .. code-block:: python

                fab <run_local/run_stage/run_live> collect_static

    * Rebuild search index

        .. code-block:: python

                fab <run_local/run_stage/run_live> rebuild_index

    * To restart celery in remote servers

        .. code-block:: python

                fab <run_stage/run_live> restart_celery

    * To restart supervisorctl in remote servers

        .. code-block:: python

                fab <run_stage/run_live> restart_supervisior

    * To restart uwsgi in remote servers

        .. code-block:: python

                fab <run_stage/run_live> restart_uwsgi

    * To restart remote servers

        .. code-block:: python

                fab <run_stage/run_live> restart_server

