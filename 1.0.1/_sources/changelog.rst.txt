Changelog
=========

New Features
------------
- Add the ability to import and export settings
- Logging System Overhall
    - Added a ``Debug Mode`` to disable 99% of logs
    - Demote most log entries to debug level
    - Add a logs section to the documentation
    - Add a way to disable logs entirely

Bug Fixes
----------
- Fix bug with a requirement being missing
- Fix bug with a debug ``data`` file being created when using rtfm indexed presets
- Fix bug with some presets failing to load on startup due to extra slashes at the end of the url.
- Fix bug with mdn docs preset and mkdocs doctype not re-using json decoders.