Chambers app
============

The "Chambers App" demonstrates how a Customs Authority may use the
inter-government ledger to facilitate exports.

This app is supposed to be semi-realistic;
it does not attempt to be a "single window" for exporters, but it does
to demonstrate by example features that integrate with the ledger.

The app uses an external identity provider, to simulate integration
with a national exporter identification scheme.

For detailed technical documentation, see the `DEVELOPMENT.rst` file.
To just start the local version on Linux or MacOS please use `run.sh` script
and navigate to http://localhost:8010/, more details in the DEVELOPMENT file.

Start locally
-------------

First, cd do the ``src`` folder and create local.env file (may be empty).

To start it without intergov connection (just the UI)::

    $ docker-compose up

With the intergov already started as docker-compose file::

    $ docker-compose -f docker-compose.yml -f demo.yml

Or you could still use the first variant, providing intergov endpoints as env variables
in the local.env file.

Demo workflow
-------------

https://github.com/gs-immi/inter-customs-ledger/issues/198

* Prepare
  * Ensure the app is started fine and linked to some intergov setup
  * Create organisation and users in it
  * login as user of the organisation

As a chamber(organisation) user using the application UI:

* Create a certificate ``/certificates/certificates/create/``
* Fill the certificate, upload required files and get it into the "Complete" status by doing it
* press Lodge button
* observe how certificate changes it's status to "Sent"
* in the background, app:
   * creates certificate file (free format now, EDI3 in the future)
   * uploads that file to the intergov setup
   * creates a message with predicate ``UN.CEFACT.Trade.CertificateOfOrigin.created`` and links it to the uploaded certificate, sends it

Now blockchain worker should either accept it or reject. It happens in the
intergov setup. As a result - new message is being sent to the chambers app
using WebSub notification protocol.

* chambers_app receives notification with predicate ``UN.CEFACT.Trade.CertificateOfOrigin.accepted``
* chambers_app updates the accepted certificate status and (optionally, non-MVP) saves some information about it to be displayed to the user

As the UI user we can see that certificate status has changed to "Accepted" ("Rejected")

When somebody acquittes the certificate (using importer app somewhere else):

* chambers_app receives notification ``UN.CEFACT.Trade.CertificateOfOrigin.acquited``
* chambers_app updates the certificate to reflect it's updated status (as the list of acquisition events for example)
