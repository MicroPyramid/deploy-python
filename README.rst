Deploy Django Project with Fabric
===================================

.. image:: https://readthedocs.org/projects/deploy-python/badge/?version=latest
   :target: http://deploy-python.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/dm/deploy-python.svg
   :target: https://pypi.python.org/pypi/deploy-python
   :alt: Downloads

.. image:: https://img.shields.io/pypi/v/deploy-python.svg
   :target: https://pypi.python.org/pypi/deploy-python
   :alt: Latest Release

.. image:: https://travis-ci.org/MicroPyramid/deploy-python.svg?branch=master
   :target: https://travis-ci.org/MicroPyramid/deploy-python

.. image:: https://coveralls.io/repos/github/MicroPyramid/deploy-python/badge.svg?branch=master
   :target: https://coveralls.io/github/MicroPyramid/deploy-python?branch=master

.. image:: https://img.shields.io/github/license/micropyramid/deploy-python.svg
   :target: https://pypi.python.org/pypi/deploy-python/


Setup:
-------

* First, create an YAML file similar to `sample_config.yaml`_ and fill the configuration details.

.. _`sample_config.yaml`: https://github.com/MicroPyramid/deploy-python/blob/master/deploy_python/sample_config.yaml

* Next, create a :code:`fabfile.py` in your project directory and import all functions(fab commands/tasks) from `deploy_python`.

* Finally, call setup() function with your configuration yaml file path.

**Here is an example fabfile** -

.. code-block:: python

    # fabfile.py
    from deploy_python.commands import *
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

Visit our Django web development page `Here`_

.. _Here: https://micropyramid.com/django-development-services/
