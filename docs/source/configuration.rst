Setup
=========

* First, create an YAML file similar to `sample_config.yaml`_ and fill the configuration details.

* Next, create a file named :code:`fabfile.py` in your project directory and import all functions(fab commands/tasks) from `deploy_python`.

* Finally, call the :code:`setup()` function with your configuration yaml file path.


**Here is an example fabfile**  -

.. code-block:: python

    # fabfile.py
    from deploy_python.commands import *
    setup("config_file_name.yaml")


.. _`sample_config.yaml`: https://github.com/MicroPyramid/deploy-python/blob/master/deploy_python/sample_config.yaml

