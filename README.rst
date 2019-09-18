bai2
====

Python module for parsing and writing `BAI2`_ files.

**The library is not production ready at the moment** as we don't have enough data to test against, please help us improve it.


Requirements
------------

Only Python 2.7 and Python 3.3+ are supported.


Installation
------------

.. code-block:: bash

    pip install bai2


Usage
-----

To use bai2 in a project

.. code-block:: python

    >>> from bai2 import bai2

    >>> # parse from a file
    >>> with open(<file-path>) as f:
    >>>     bai2_file = bai2.parse_from_file(f)

    >>> # parse from a string
    >>> bai2_file = bai2.parse_from_string(<bai2_as_string>)

    >>> # parse from lines
    >>> bai2_file = bai2.parse_from_lines(<bai2_as_lines>)


The ``parse_from_*`` methods return a ``bai2.models.Bai2File`` object which can be used to inspect the parsed data.

To write a BAI2 file:

.. code-block:: python

    >>> from bai2 import bai2
    >>> from bai2 import models

    >>> bai2_file = models.Bai2File()
    >>> bai2_file.header.sender_id = 'EGBANK'

    >>> bai2_file.children.append(models.Group())

    >>> transactions = [models.TransactionDetail(amount=100)]
    >>> bai2_file.children[0].children.append(models.Account(children=transactions))

    >>> # write to string
    >>> output = bai2.write(bai2_file)


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

.. image:: https://travis-ci.org/ministryofjustice/bai2.svg?branch=master
    :target: https://travis-ci.org/ministryofjustice/bai2

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` or ``tox`` to run all tests.

Distribute a new version to `PyPi`_ by updating the ``__version__`` string in ``bai2`` and run ``python setup.py sdist bdist_wheel upload``.


Copyright
---------

Copyright (C) 2019 HM Government (Ministry of Justice Digital & Technology).
See LICENSE.txt for further details.

.. _BAI2: http://www.bai.org/Libraries/Site-General-Downloads/Cash_Management_2005.sflb.ashx
.. _GitHub: https://github.com/ministryofjustice/bai2
.. _PyPi: https://pypi.org/project/bai2/
