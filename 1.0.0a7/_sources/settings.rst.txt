Plugin Settings
===============

To configure the plugin, you need to open up the settings webserver. To do this, use the main keyword (see :doc:`main_keyword` for more info) to open up the webserver.

General Options
---------------
On the settings website you will see a couple of general plugin options.

Webserver Port
~~~~~~~~~~~~~~
This is where you can customize which port the settings website runs on. By default it is set to ``0``, which lets your system choose a random unused port on startup.

On startup, if the chosen port is already in use or is reserved by your system, the plugin will let your system choose a random port and send you a notification.

Main Keyword
~~~~~~~~~~~~
This is where you can customize the main keyword. Defaults to ``rtfm``. See the :doc:`main_keyword` page for more information.

.. _save_settings:

Saving your settings
--------------------
Your settings will not automatically save, you have to save them manually. To save your settings and trigger a cache reload, press the ``Save Settings & Reload Cache`` button under the ``Plugin Settings`` section in the website. This button is the only method to save any of your settings.

.. image:: /_static/images/save_settings_example_darkmode.png
    :class: only-dark

.. image:: /_static/images/save_settings_example_lightmode.png
    :class: only-light

Adding a manual/doc
-------------------
To add a manual or doc, find the ``Add Manual`` section and input a keyword and location. The location can be a full url (ex: ``https://rtfm.cibere.dev/latest``), url without scheme (ex: ``rtfm.cibere.dev/latest``), or a path (ex: ``C:\Users\cibere\rtfm\docs\_build\html``). When you press ``Add``, the plugin will attempt to match the URL against the current set of presets (see :doc:`presets` for more info), then it will try to guess which format the manual/doc conforms to. If either a preset or type that is supported is found, the doc/manual will be added to the list of docs/manuals on the website. If the manual/doc can't be indexed, you will receive an error.

.. WARNING::

    Adding a manual/doc does NOT save it. See `the saving section <#saving-your-settings>`__ for more info.

Troubleshooting
~~~~~~~~~~~~~~~~
If a manual/doc that you want to use could not be indexed, you have a couple of things you can try:

1. Make sure the location you provided is the exact link to the root of the version of the manual/doc that you want to index. For example, instead of using something like ``https://rtfm.cibere.dev/latest/installing.html#install-from-source``, trim it down to ``https://rtfm.cibere.dev/latest`` instead.
2. Make sure your copy of the plugin is up to date, as there might have been changes that added support for the doc/manual you are trying to use.
3. If neither of the two options above worked, consider opening an `issue request on github <https://github.com/cibere/Flow.Launcher.Plugin.rtfm/issues/new>`__ requesting support for the manual/doc to be added.
4. If neither of the first two options worked and you either don't have a github account or don't want to create one, you can ask for help on the `official flow discord server <https://discord.gg/QDbDfUJaGH>`__.

.. _edit_manual:

Editing a manual/doc
--------------------
The list of manuals/docs that you have currently added will be at the bottom of the website, starting right after the ``Add Manual`` card. There are a couple of visible fields, some editable and others not.

.. WARNING::

    Doc/manual settings do NOT automatically save. See `the saving section <#saving-your-settings>`__ for more info.

Keyword
~~~~~~~
This is the keyword that you use to query the doc/manual. Please ensure that this does not conflict with any keywords from other plugins, as that can cause complications.

If you do not want to use a keyword, setting the keyword to ``*`` will make it work without a keyword.

Use Cache
~~~~~~~~~
This checkbox is used to determine whether or not to cache the manual/doc's index or not. If checked, each query will pull from an internal cache, resulting in fast responses. If unchecked, at the beginning of each query, the plugin will rebuild the cache it has for the manual/doc before giving you a response. This is significantly slower, but useful when actively developing/changing a manual/doc.

If the doc/manual is marked as an `API <#is-api>`__, then you will be unable to edit this checkbox, and it will be indefinetely unchecked.

Type
~~~~
This field shows the type that the doc/manual is marked as. This field is not editable, and is purely for information.

If it is set to ``Preset``, then the doc/manual is connected to a preset (see :doc:`presets` for more info). Otherwise the value will be associated with the format or standard that the doc/manual conforms to, and which was used to index the manual/doc.

Is API
~~~~~~
This checkbox is used to show you if this doc/manual is marked as an API or not. This field is not editable, and is purely for information.

If checked, a web request is made for each query, so caching is not supported. Docs/manuals marked as APIs will be significantly slower than other docs/manuals not marked as APIs, and will typically yield less results per query.