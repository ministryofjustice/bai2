bai2
====

Python module for parsing and writing `BAI2`_ files.

**The library is not production ready at the moment** as we don't have enough data to test against, please help us improve it.

Requirements
------------

Only Python 3.7+ is supported.

Installation
------------

.. code-block:: shell

    pip install bai2

Usage
-----

To use bai2 in a project

.. code-block:: python

    from bai2 import bai2

    # parse from a file
    with open(<file-path>) as f:
        bai2_file = bai2.parse_from_file(f)

    # parse from a string
    bai2_file = bai2.parse_from_string(<bai2_as_string>)

    # parse from lines
    bai2_file = bai2.parse_from_lines(<bai2_as_lines>)

The ``parse_from_*`` methods return a ``bai2.models.Bai2File`` object which can be used to inspect the parsed data.

To write a BAI2 file:

.. code-block:: python

    from bai2 import bai2
    from bai2 import models

    bai2_file = models.Bai2File()
    bai2_file.header.sender_id = 'EGBANK'

    bai2_file.children.append(models.Group())

    transactions = [models.TransactionDetail(amount=100)]
    bai2_file.children[0].children.append(models.Account(children=transactions))

    # write to string
    output = bai2.write(bai2_file)

Models
------

Models structure::

    Bai2File
        Bai2FileHeader
        Group
            GroupHeader
            Account
                AccountIdentifier
                TransactionDetail
                AccountTrailer
            GroupTrailer
        Bai2FileTrailer

Section models define a ``header``, a ``trailer`` and a list of ``children`` whilst single models define properties matching the bai2 fields.

Each Model has a ``rows`` property with the original rows from the BAI2 file.

Exceptions
----------

The ``parse`` method might raise 3 exceptions:

1. ``ParsingException``: when the file contains an error and the library can't interpret the data
2. ``NotSupportedYetException``: when the library doesn't support the feature yet
3. ``IntegrityException``: when the control totals or the number of objects reported in the trailers don't match the ones in the file.

Incongruences
-------------

We've noticed that different banks implement the specs in slightly different ways and the parse method might therefore raise an ParsingException.
It is expected to work correctly with files produced by NatWest, RBS, and JP Morgan.

We don't know yet how to deal with these cases as we don't have access to many bai2 files so we can't test it as we would like.

Please let me know if this happens to you.

Development
-----------

.. image:: https://github.com/ministryofjustice/bai2/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/ministryofjustice/bai2/actions/workflows/test.yml

.. image:: https://github.com/ministryofjustice/bai2/actions/workflows/lint.yml/badge.svg?branch=main
    :target: https://github.com/ministryofjustice/bai2/actions/workflows/lint.yml

Please report bugs and open pull requests on `GitHub`_.

To work on changes to this library, it’s recommended to install it in editable mode into a virtual environment,
i.e. ``pip install --editable .``

Use ``python -m tests`` to run all tests locally.
Alternatively, you can use ``tox`` if you have multiple python versions.

[Only for GitHub team members] Distribute a new version to `PyPI`_ by:

- updating the ``VERSION`` tuple in ``bai2/__init__.py``
- adding a note to the `History`_
- publishing a release on GitHub which triggers an upload to PyPI;
  alternatively, run ``python -m build; twine upload dist/*`` locally

History
-------

Unreleased
    Migrated test, build and release processes away from deprecated setuptools commands.
    Switched to `ruff <https://github.com/astral-sh/ruff>`_ for code linting and formatting.
    No significant library changes.

0.11.0 (2023-02-17)
    Adds support for Real Time Payment detail codes 158 and 458 (thanks @LSakey).

0.10.0 (2023-02-16)
    Improve parsing of account identifier records with respect to varying number of commas used by different banks (thanks @forforeach).

0.9.2 (2023-01-13)
    Maintenance release, no library changes.

0.9.1 (2022-12-22)
    Add support for 829 ‘SEPA Payments’ type code (thanks @podj).

0.9.0 (2022-12-21)
    More lenient parsing where integers are expected (thanks @daniel-butler).
    Add support for 827 & 828 ‘SEPA Payments’ type codes (thanks @podj).
    Remove testing for python versions below 3.7 (the library is still likely to work with 3.6).
    Add testing for python 3.11.

0.8.2 (2022-01-26)
    No library changes.
    Add testing for python 3.9 and 3.10.

0.8.0 (2020-11-11)
    Remove support for python versions below 3.6.

0.7.0 (2019-10-03)
    ``rows`` no longer required in BAI2 models (c.f. issue 12 and PR 13).

0.6.0 (2019-09-18)
    Fix regular expression escaping.
    Add python 3.7 testing.

0.5.0 (2018-03-05)
    Updated packaging details and improved python version compatibility.

0.1.0 (2015-08-06)
    Original release.

Copyright
---------

Copyright (C) 2023 HM Government (Ministry of Justice Digital & Technology).
See LICENSE.txt for further details.

.. _BAI2: https://www.bai.org/docs/default-source/libraries/site-general-downloads/cash_management_2005.pdf
.. _GitHub: https://github.com/ministryofjustice/bai2
.. _PyPI: https://pypi.org/project/bai2/
