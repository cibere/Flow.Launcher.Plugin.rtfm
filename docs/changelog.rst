Changelog
=========

- Support empty searches
- Update webserver
    - Rewrite webserver backend
    - Rewrite webserver frontend (thanks `Yusyuriv <https://github.com/Yusyuriv>`__)
    - readd the ability to choose a custom port
- Add support for mkdocs
- add more presets. See :doc:`presets` for a list.
- Add proper documentation
- Fix bug with infinitely big log files
- Update build process to not include unneccessary files
- Fix bug with cache being built multiple times simultaneously
- Support star/blank keywords
- Add a ``version`` key to the settings for better backwards compatibility in the future, if the format is ever to change.
- Add a context menu item to copy the url