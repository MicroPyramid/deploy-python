Deploy Django Project with Fabric
===================================

.. image:: https://readthedocs.org/projects/django-spanner/badge/?version=latest
   :target: http://django-spanner.readthedocs.org/en/latest/?badge=latest

 .. image:: https://img.shields.io/pypi/dm/django-spanner.svg
   :target: https://pypi.python.org/pypi/django-spanner
   :alt: Downloads

.. image:: https://img.shields.io/pypi/v/django-spanner.svg
   :target: https://pypi.python.org/pypi/django-spanner
   :alt: Latest Release

.. image:: https://travis-ci.org/MicroPyramid/django-spanner.svg?branch=master
   :target: https://travis-ci.org/MicroPyramid/django-spanner

.. image:: https://coveralls.io/repos/github/MicroPyramid/django-spanner/badge.svg?branch=master
   :target: https://coveralls.io/github/MicroPyramid/django-spanner?branch=master

.. image:: https://img.shields.io/pypi/l/django-spanner.svg
   :target: https://pypi.python.org/pypi/django-spanner/


Setup:
-------

* First, create an YAML file similar to `sample_config.yaml`_ and fill the configuration details.

.. _`sample_config.yaml`: https://github.com/MicroPyramid/django-spanner/blob/master/django_spanner/sample_config.yaml

* Next, create a :code:`fabfile.py` in your project directory and import all functions(fab commands/tasks) from `django_spanner`.

* Finally, call setup() function with your configuration yaml file path.

**Here is an example fabfile** -

.. code-block:: python

    # fabfile.py
    from django_spanner.commands import *
    setup("fabconfig.yaml")


Usage:
-------

* To list all the fab commands:

.. code-block:: python

    fab -l


* To install the requirements on your local system, you can run the command as follows

.. code-block:: python

    fab run_local activate_env_install_requirements
                    (or)
    fab activate_env_install_requirements


* To run a command on staging/live host,

.. code-block:: python

    fab [run_local/run_stage/run_live] <command_name>


NOTE:
-------
By default, all the functions will run on the local system.
