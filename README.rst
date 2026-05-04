> [!IMPORTANT]
> **This repository has moved.**
> Because GitHub's performance has degraded significantly, this repository has moved to Forgejo. Active development continues at **https://git.disroot.org/mrcagney/kml2geojson**.
> This GitHub copy is archived and will not receive updates, issues, or pull requests.
> Please file issues and submit changes on Forgejo.

---

kml2geojson
************
.. image:: https://github.com/araichev/kml2geojson/actions/workflows/test.yml/badge.svg
    
kml2geojson is a Python 3.11+ package to convert KML files to GeoJSON files.
Most of its code is a translation into Python of the Node.js package `togeojson <https://github.com/mapbox/togeojson>`_, but kml2geojson also adds the following features.

- Preserve KML object styling, such as color and opacity
- Optionally create a style dictionary cataloging all the KML styles used
- Optionally create several GeoJSON FeatureCollections, one for each KML folder present

Authors
========
- Alex Raichev (2015-10-03), maintainer



Installation
=============
Install from PyPI via, say, ``uv add kml2geojson``.


Usage
======
Use as a library or from the command line.
For instructions on the latter, type ``k2g --help``.


Documentation
=============
The documentation is built via Sphinx from the source code in the ``docs`` directory then published to Github Pages at `araichev.github.io/kml2geojson_docs <https://araichev.github.io/kml2geojson_docs>`_.


Contributing
===================
If you want to help develop this project, here is some background reading.

- The `KML reference <https://developers.google.com/kml/documentation/kmlreference?hl=en>`_
- Python's `Minimal DOM implementation <https://docs.python.org/3.4/library/xml.dom.minidom.html>`_, which this project uses to parse KML files

Notes
========
- This project's development status is Beta.
- This project uses semantic versioning.
- If you would like to fund additional features to this project, feel free to email me.
- Thanks to `MRCagney <http://www.mrcagney.com/>`_ for periodically donating to this project.
- Constructive feedback and contributions are welcome.
  Please issue pull requests from a feature branch into the ``develop`` branch and include tests.



Maintainer Notes
================
- After pushing to master, update the published docs via ``uv run make -C docs publish-docs-github``

Changes
========

5.1.1, 2026-03-12
-----------------
- Migrated packaging metadata to PEP 621 in ``pyproject.toml`` and switch the
  build backend to Hatchling.
- Updated project URLs to the current repository and documentation site.
- Raised the declared minimum Python version in package metadata.
- Modernized GitHub Actions to use ``uv`` and refresh the Python test matrix.
- Updated README installation and documentation guidance.
- Fixed ``k2g`` CLI output handling for styled and unstyled conversion paths.
- Restructured tests to use one test function per API function with sectioned
  behavioral coverage.
- Added CLI integration tests for the no-style and styled separate-folders paths.

5.1.0, 2022-04-29
-----------------
- Extended ``convert()`` to accept a KML file object.
- Added type hints.
- Updated dependencies and removed version caps.
- Dropped support for Python versions less than 3.8.
- Switched from Travis CI to Github Actions.


5.0.1, 2021-10-11
-----------------
- Re-included the MIT License file and added more metadata to the file ``pyproject.toml`` for a more informative listing on PyPi.


5.0.0, 2021-10-07
-----------------
- Upgraded to Python 3.9 and dropped support for Python versions < 3.6.
- Switched to Poetry.
- Breaking change: refactored the ``convert`` function to return dictionaries instead of files.
- Moved docs from Rawgit to Github Pages.


4.0.2, 2017-04-26
-------------------
- Fixed the bug where ``setup.py`` could not find the license file.


4.0.1, 2017-04-22
-------------------
- Moved the name of a FeatureCollection into a 'name' attribute, because `RFC 7946 says that a GeoJSON FetaureCollection must not have a 'properties' attribute <https://tools.ietf.org/html/rfc7946#section-7>`_
- Stripped leanding and trailing whitespace from text content to avoid cluttered or blank name and description attribute values
- Switched to pytest for testing


4.0.0, 2016-11-24
-------------------
- Moved command line functionality to separate module
- Renamed some functions


3.0.4, 2015-10-15
-------------------
Disambiguated filenames in ``main()``.


3.0.3, 2015-10-13
-------------------
Improved ``to_filename()`` again.


3.0.2, 2015-10-12
-------------------
Improved ``to_filename()`` and removed the lowercasing.


3.0.1, 2015-10-12
-------------------
Tweaked ``to_filename()`` to lowercase and underscore results. 
Forgot to do that last time.


3.0.0, 2015-10-12
------------------
Changed the output of ``build_layers()`` and moved layer names into the GeoJSON FeatureCollections


2.0.2, 2015-10-12
-------------------
- Replaced underscores with dashes in command line options


2.0.1, 2015-10-12
-------------------
- Set default border style for colored polygons
 

2.0.0, 2015-10-08
------------------
- Added documentation
- Tweaked the command line tool options 


1.0.0, 2015-10-05
------------------
- Changed some names 
- Added lots of tests


0.1.1, 2015-10-03
-------------------
Fixed packaging to find ``README.rst``


0.1.0, 2015-10-03
-----------------
First


