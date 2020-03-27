Chambers App Developer Docs
===========================

Inter Customs Ledger Chambers app

Basic Commands
--------------

use manage.sh and pytest.sh files to access these standard Django commands inside the docker container. `run.sh` runs default development server. Default port is 8010 for the Chambers app. All helper scripts have their parameters proxied (so run `./run.sh --build` if you have just updated the requirement files).

Please note that you need to configure allauth to get the github working:
* update admin->sites default site to your actual domain name
* create your github application and save the client key and secret https://django-allauth.readthedocs.io/en/latest/providers.html#github
* create admin -> social account with these details


To create an **superuser account**::

    $ docker-compose run --rm django python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.


Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests
~~~~~~~~~~~~~

::

  $ ./pytest.sh (from outside of the docker container)
  $ py.test (from the inside of the django container)

The helper pytest.sh will run unittests, mypy check and flake8 check.
