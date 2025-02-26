Changelog
=========

- Remove the preset system, so that the parsers are contained in a different repository, and they are loaded via a doctype (Preset requests will be located in the `new indexes repository <https://github.com/cibere/Rtfm-Indexes/>`__, however creating preset requests on the plugin's repository is fine).
    - This will allow for faster and automatic preset updates, faster caching times, and it will reduce the strain on the hosts.
    - With the move to their own repository, the manual type has been changed to ``cibere-rtfm-indexes``
- Remove the ``Use Cache`` option
- Add a ``Cache Results`` option for doctype entries
- Rewrite settings to reduce code duplication and to stop dumping settings about 5 times every time the save button in the webserver is clicked
- Strip the plugin's core (~1.5k lines removed) and move them to their own repository so that they can be integrated in other places
- Fix a bug with certain error icons not showing
- Remove the need to have ``image-magik`` installed for nice icons, by switching from google's favicon API to duckduckgo's favicon API.
- Bump dependencies
- Remove the entry children (extra context menu items) for code simplicity, might add them back later
- Fix the previous implementation of legacy compatible settings not actually working very well
- Improve some error messages in the settings webserver
- Update the documentation