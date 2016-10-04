Features
===========

    * Install requirements in a virtualenv.
    * Migrate database.
    * Execute any management command.
    * Rsync files to destination server(stage/live) with and without settings file.
    * Deploy the django application to server(Installs requirements, migrates database, rsync files, runs uwsgi server).
    * Take database backups(server backups as well as local).
    * Restore local and server databases.
    * Reset local and server databases.
    * Restart server, celery, supervisor, uwsgi.
    * Rebuild index, collect static.


.. note::

    You can execute all these commands in local as well as remote servers.

