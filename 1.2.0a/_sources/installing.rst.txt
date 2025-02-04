Installing
==========

There are 3 main ways to install the plugin:

1. `Install Stable Release From Manifest <#install-stable-release-from-manifest>`__
2. `Install Specific Version <#install-specific-version>`__
3. `Install from source <#install-from-source>`__

Install Stable Release From Manifest
-------------------------------------
To install a stable release of the plugin from flow's plugin manifest, use the following command:

.. code-block:: sh

    pm install rtfm by cibere

Install Specific Version
-------------------------
Want to install a specific version? Well you can by using the `github release page <https://github.com/cibere/flow.Launcher.Plugin.rtfm/releases>`__

1. Find the version you want to download
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install a specific version, head over to the `releases page <https://github.com/cibere/flow.Launcher.Plugin.rtfm/releases>`__ and find the version that you want to install. In my case I'm going to install the `v1.0.0a4 <https://github.com/cibere/Flow.Launcher.Plugin.rtfm/releases/tag/v1.0.0a4>`__ prerelease.

.. image:: /_static/images/v1.0.0a4_prerelease.png
    :target: https://github.com/cibere/Flow.Launcher.Plugin.rtfm/releases/tag/v1.0.0a4

2. Get the archive link
~~~~~~~~~~~~~~~~~~~~~~~~

Now grab the link to the ``zip`` file in the assets section.

.. image:: /_static/images/copy_release_archive.png
    :target: https://github.com/cibere/Flow.Launcher.Plugin.rtfm/releases/tag/v1.0.0a4

3. Install the plugin
~~~~~~~~~~~~~~~~~~~~~~

Finally, install the zip using the package manager:

.. code-block:: sh

    pm install <your link>

    # so in my case it would be

    pm install https://github.com/cibere/Flow.Launcher.Plugin.rtfm/releases/tag/v1.0.0a4

Install From Source
--------------------

If for whatever reason you want to build the plugin yourself, you can.

1. Download Source files
~~~~~~~~~~~~~~~~~~~~~~~~
First, download the source files from `the github page <https://github.com/cibere/flow.Launcher.Plugin.rtfm>`__. This can be done by downloading it as a zip:

.. image:: /_static/images/download_source.png
    :target: https://github.com/cibere/flow.Launcher.Plugin.rtfm

or by cloning it using `git <https://git-scm.org>`__:

.. code-block:: sh

    git clone https://github.com/cibere/flow.Launcher.Plugin.rtfm

2. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

Next, install the plugin's dependencies to a folder called ``lib``. This can be done with the following command:

.. code-block:: sh

    py -m pip install -r requirements.txt -t lib

3. Build the plugin
~~~~~~~~~~~~~~~~~~~~

Then build the plugin by running the ``build_plugin.py`` file while passing the name of the location. In my case, I'm going to name the built plugin ``built_rtfm_plugin.zip``. That can be done by running:

.. NOTE::
    Make sure the name you pass ends with ``.zip``, as the script will create an archive with the chosen name.

.. code-block:: sh

    py build_plugin.py built_rtfm_plugin.zip

4. Install the plugin
~~~~~~~~~~~~~~~~~~~~~~

Now finally, install the plugin by using the package manager.

.. code-block:: sh

    pm install <path to zip>

    # so in my case

    pm install C:\Users\default.MyPC\Downloads\flow.launcher.plugin.rtfm\built_rtfm_plugin.zip