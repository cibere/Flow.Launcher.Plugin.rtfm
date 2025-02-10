Logs
====

The plugin has an extensive logging system builtin, however the majority of it is set to the debug level, which is disabled by default.

Debug Mode
-----------
Debug mode is available for the cases where detailed logs are needed to debug an issue. Having this enabled can slow down the plugin to some degree, but it should only be somewhat noticeable when caching a large amount of manuals.

What gets logged without debug mode?
------------------------------------
Disabling debug mode does not disable logs. When debug mode is disabled, entries that are info level and above are still logged, for example:

- Webserver startup info (like the port it is running on)
- Start-time settings info from `flogin <https://github.com/cibere/flogin>`__
- Webserver access logs from `aiohttp <https://docs.aiohttp.org/en/stable/>`__
- Warnings (ex: the port the webserver attempted to start on was already taken)
- Errors

Log Location
------------
Logs are stored in a file called ``flogin.log`` in the plugin's root directory. The file is capped at 1mb, however once that limit is reached, the contents will be moved to a file called ``flogin.log.1``. The contents of ``flogin.log.1`` will never be moved, and will just be overriden once ``flogin.log`` fills up again.

This file can also be accessed via the ``Open Log File`` result when using the :doc:`main_keyword` or in any context menu from a result that came from the plugin.

Disabling Logs
--------------
If you want to disable logs completely, head into your plugin's directory and create a file called ``.flogin.prod``.

To find the plugin's directory, open your flow launcher settings menu, head into the plugins tab, and find the ``rtfm`` plugin.

.. NOTE::
    This file is only checked for on startup, so you must restart flow after creating/deleting this file for the changes to take affect.

.. image:: /_static/images/plugin_folder_icon_darkmode.png
    :class: only-dark

.. image:: /_static/images/plugin_folder_icon_lightmode.png
    :class: only-light
