Favicons
========

The plugin will look for and download the favicon for each manual/doc that you are using. If the plugin consistantly chooses the wrong favicon/image to use as the result icons, please create an `issue on the github page <https://github.com/cibere/Flow.Launcher.Plugin.rtfm/issues/new>`__ to let the developers of the plugin know, and so that they can fix it.

SVG Files
----------
In the event that the favicon is an `svg <https://en.wikipedia.org/wiki/SVG>`__ file, the plugin will try to use `ImageMagick <https://imagemagick.org/script/download.php#windows>`__ to convert it to a high quality ``png`` file. If `ImageMagick <https://imagemagick.org/script/download.php#windows>`__ is not installed, the plugin will use an undocumented google API to get a low quality render of the favicon.

Example
~~~~~~~
Without ImageMagick

.. image:: /_static/images/py_logo_wo_imagemagick_example.png

With ImageMagick

.. image:: /_static/images/py_logo_w_imagemagick_example.png