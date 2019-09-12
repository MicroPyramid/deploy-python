.. deploy_python documentation master file, created by
   sphinx-quickstart on Sat Jul  2 11:42:15 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Django Spanner
================

Django Spanner is a simple package used to deploy and manage `Django`_ applications. Django Spanner is a set of commands used to deploy and manage django projects. It internally uses `Fabric`_. This can also be called as **Deploying Django with Fabric**.

* You can use this to deploy & manage any django application with just few configurations. Configure once and run many times.

* As well as you can deploy & manage single django application on multiple remote servers (multiple staging servers, multiple live servers). You can specify different configuration for each type of server (stage/live) like here `sample config file`_

* Also used to manage local django project to install requirements, run make migrations, migrate, take database backups and many more...


This package is developed by `MicroPyramid`_ team. Please refer the `github repository`_ for the deploy-python source code. It's free and open source.


Github Repository
********************

    Django Spanner - `https://github.com/MicroPyramid/deploy-python`_


Contents
----------

.. toctree::
   :maxdepth: 2

   features
   installation
   configuration
   commands


.. _`Django`: https://www.djangoproject.com/

.. _`Fabric`: http://www.fabfile.org/

.. _`MicroPyramid`: https://micropyramid.com/

.. _`github repository`: https://github.com/MicroPyramid/deploy-python

.. _`https://github.com/MicroPyramid/deploy-python`: https://github.com/MicroPyramid/deploy-python

.. _`sample config file`: https://github.com/MicroPyramid/deploy-python/blob/master/deploy_python/sample_config.yaml

