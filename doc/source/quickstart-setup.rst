DDS Backend Quickstart Guide
============================

This guide is intended to get you up and running with a test
DDS backend environment quickly. Most of the advice given here also
applies to use of the backend in a production environment.

Prerequisites
-------------
At a minimum, you need to have the following in order to run the DDS
backend:

- Python 2.4+
- python-pip
- python-setuptools

Setup
-----
in the dds directory, run ::

  sudo pip install -r requirements.txt

which will download the right versions of software orwell depends on.
In the dds directory, add a file named 'local_settings.py'. Add ::

  DATABASE_ENGINE = 'sqlite3'
  DATABASE_NAME = '/path/to/dds/orwell.db'
  MEDIA_URL = 'http://localhost:8000/media/'

to it. This specifies the sort of database orwell should use. In
this case, it'll use sqlite3 with a database file named orwell.db.
The full path to the database file must be given in order for
harvest to function properly when using orwell's settings file
(see the harvest README for details). DATABASE_NAME isn't
necessary if you use a database other than sqlite. Check the
django documentation for details on how to set up other databases.
You will want to use a database other than sqlite3 in a production
environment, but for testing or development it will work fine.

When you do a full DDS deployment in a production environment, you
will obviously want to use a full relational database, such as
mySQL. If you're just trying to get a system up and running, sqlite
will do.

Running the Backend
-------------------
from the dds directory, run ::

  ./manage.py syncdb
  ./manage.py runserver
