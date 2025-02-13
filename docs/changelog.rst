Changelog
=========

- Rewrite preset system, so that the parsers are contained in a different repository, and they are loaded via a doctype.
    - This will allow for faster and automatic preset updates, faster caching times, and it will reduce the strain on the hosts.
- Remove the ``Use Cache`` option for non-api presets/doctypes.
- Add a ``Cache Results`` option for doctype entries
- Rewrite settings to reduce code duplication and to stop dumping settings about 5 times every time the save button in the webserver is clicked