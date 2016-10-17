Local Development
=================

Configuring your environment
----------------------------

The following documents the steps to set up a freshly `git clone`d copy of the project.

First, set up your virtualenv (assumes you have Python 3.4+ installed and that your current working directory is the parent `rlp` directory of this project)::

    pyvenv env
    source env/bin/activate
    pip install -U pip setuptools
    pip install -r requirements-dev.txt

If you are using `pyenv` (preferred)::

    pyenv virtualenv 3.5.2 rlp
    pyenv activate rlp
    pip install -U pip setuptools
    pip install -r requirements-dev.txt

Copy the example settings file::

    cp rlp/settings.py.example rlp/settings.py

If you are starting with an empty database::

    ./manage.py migrate

Now you should be able to successfully::

    ./manage.py runserver 0.0.0.0:8000

This listens on every interface on port 8000.
This is helpful if you need to access the development server from another machine (virtual or otherwise).

Search
------

If you need to test the search feature, you'll need to install elasticsearch and Apache Tika.

First, download elasticsearch 1.x (Haystack does not support Elasticsearch 2.x yet).
Simply unzip the file and run bin/elasticsearch.

Next, download Apache Tika tika-app-1.13.jar and place it in the rlp/bin directory.

With these two items in place, you should now be able to::

    ./manage.py rebuild_index --noinput

