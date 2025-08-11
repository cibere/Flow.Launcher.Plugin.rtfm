Changelog
=========

v1.4.4
-------
- Fix bug with the plugin not properly starting with flow version 1.20
- Bump aiohttp from 3.12.13 to 3.12.14

v1.4.3
-------
- Bump aiohttp from 3.11.14 to 3.12.13

v1.4.2
-------

- Add a ``Copy Markdown Hyperlink`` to the context menu of results
- fix bug with the gidocgen not working due to an undefined reference at runtime
- Bump aiohttp from 3.11.13 to 3.11.14 

v1.4.1
-------

- fix bug with the plugin not properly started due to files being left out during packaging

v1.4.0
--------

- Add the ability to access manuals with the main keyword via ``{main_keyword} {manual_keyword}``
- Add a ``Condense Keywords`` option to toggle registering manual keywords with flow.
- Display added manuals in main keyword response
  - Due to the keyword change earlier, this will only happen when using the main keyword and no query.
  - Result autocomplete values and callbacks both redirect to the manual keyword or main keyword + manual keyword depending on your ``Condense Keywords`` setting

- fix bug with the icon on the ``Could not find anything. Sorry.`` result not properly displaying the icon
- fix bug with the default settings on a fresh installation not properly resolving to a settings decoder.
- fix bug with old manuals not being removed when saving new settings

- update the documentation to fix incorrect information with the last minor release, and add information from this release.