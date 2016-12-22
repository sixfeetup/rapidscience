Local Development
=================

Configuring your environment
----------------------------

The following documents the steps to set up a freshly `git clone`d copy of the project.

First, set up your virtualenv (assumes you have Python 3.4+ installed and that your current working directory is root of this repository)::

    virtualenv -p python3 env
    source env/bin/activate
    pip install -U pip setuptools
    pip install -r requirements/local.txt

If you see SSL errors from `biopython` and `psycopg2`, and you have OpenSSL installed via Homebrew, you might need to set these variables during installation::

    LDFLAGS="-L/usr/local/opt/openssl/lib"
    CPPFLAGS="-I/usr/local/opt/openssl/include"

If you are using `pyenv` (preferred)::

    pyenv virtualenv 3.5.2 rlp
    pyenv activate rlp
    pip install -U pip setuptools
    pip install -r requirements/local.txt

Copy the example environment file::

    cp env.example.chci config/settings/.env

If you are starting with an empty database::

    mkdir log
    touch log/rlp.log
    createuser web
    createdb -O web chci # (or sobc)
    ./manage.py migrate

Load some initial data::

    ./manage.py loaddata contenttypes_contenttype.json
    ./manage.py loaddata auth_permissions.json
    ./manage.py loaddata cms.json

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

