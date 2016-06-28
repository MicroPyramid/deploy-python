Deploy Django Project with Fabric
===================================

Setup:
-------

* First, create an YAML file similar to `sample_config.yaml`_ and fill the configuration details.

.. _`sample_config.yaml`: http://git.micropyramid.com/mp/django-spanner/blob/master/django_spanner/sample_config.yaml

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

