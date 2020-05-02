********************
Certificate API v0.0
********************

Used by Chambers of Commerce for certificate creation - may be integrated to external existing systems.


Auth: any auth mechanism enough to provide the actor may be supported. Currently we support next:

* cookie (to call API from the same browser where the user is logged in)
* base (send username and password with each request)

TODO:

* external providers like OIDC (which theoretically allows actor to be non-user, but some organisation itself)


Certificates list
*****************

``GET /api/certificate/v0/certificate/``


Retrieve paginated list of certificates visible to given actor.
Certificates rendered to short format.

**Response:**

.. code-block::
    json

    {
        "count": 15,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": "56c6aa43-21a4-4bc8-99d2-5a98c6bb5465",
                "status": "draft",
                "created_at": "2019-05-09T16:18:03.435189+10:00",
                "dst_country": "CN"
            },
            "...",
            {
                "id": "080e35ad-9139-4fe6-9380-2b02a328b58e",
                "status": "lodged",
                "created_at": "2019-05-07T18:13:50.265059+10:00",
                "dst_country": "AG"
            }
        ]
    }


Certificate detail
******************

``GET /api/certificate/v0/certificate/{certificate_id}/``

Retrieve complete certificate info. Checks if given certificate is visible to the actor.

**Response:**

.. code-block::
    json

    {
        "id": "080e35ad-9139-4fe6-9380-2b02a328b58e",
        "status": "lodged",
        "created_at": "2019-05-07T18:13:50.265059+10:00",
        "dst_country": "AG",
        "exporter_info": "",
        "producer_info": "",
        "importer_info": "",
        "transport_info": "",
        "remarks": "",
        "item_no": "sadfasd",
        "packages_marks": "afsd",
        "goods_descr": "233223",
        "hs_code": "",
        "invoice_info": "",
        "origin_criterion": "",
        "documents": [
            {
                "id": "ec873ed3-eb64-4c28-a842-365b8eb20264",
                "filename": "img_fMLKoXx.jpg",
                "type": "extra",
                "created_at": "2019-05-09T17:46:38.734251+10:00"
            },
            {
                "id": "797c1bcb-d465-4dd1-8ff1-517243c40dcb",
                "filename": "img_Red0QT4.jpg",
                "type": "extra",
                "created_at": "2019-05-09T17:44:22.807683+10:00"
            }
        ]
    }


Certificate create
******************

``POST /api/certificate/v0/certificate/``

Create draft certificate in the database. After creation user must upload required documents,
prepare the certificate to lodgement and lodge it. The certificate identifier, which is
returned for this request, is used for referencing it in the future.

**Request:**

.. code-block::
    bash

    curl -XPOST http://myusername:mypassword@0.0.0.0:8020/api/certificate/v0/certificate/ \
        -H "Content-Type: application/json" \
        -H "Accept: application/json; indent=2" \
        -d '{
            "id": "080e35ad-9139-4fe6-9380-2b02a328b58e",
            "created_at": "2019-05-07T18:13:50.265059+10:00",
            "dst_country": "AG",
            "exporter_info": "value",
            "producer_info": "value 02",
            "importer_info": "value 03",
            "transport_info": "value 04",
            "remarks": "value 05",
            "item_no": "value 06",
            "packages_marks": "value 07",
            "goods_descr": "value of the goods description, which may be quite long or contain newlines",
            "hs_code": "",
            "invoice_info": "",
            "origin_criterion": ""
        }
        '


**Response:**

Contains short created certificate representation, exactly like in "Certificates list" endpoint.

Possible errors are: unable to find related object, lack of required fields (dst_country),
auth problems.


Certificate partial update
**************************

``PATCH /api/certificate/v0/certificate/{id}/``

Request: JSON with fields which have to be updated. Response - full object representation.

**Request:**

.. code-block::
    bash

    curl -XPOST http://myusername:mypassword@0.0.0.0:8020/api/certificate/v0/certificate/ \
        -H "Content-Type: application/json" \
        -H "Accept: application/json; indent=2" \
        -d '{
            "status": "complete",
            "created_at": "2019-05-07T18:13:50.265059+10:00",
            "dst_country": "AG",
            "exporter_info": "value",
            "producer_info": "value 02",
            "importer_info": "value 03",
            "transport_info": "value 04",
            "remarks": "value 05",
            "item_no": "value 06",
            "packages_marks": "value 07",
            "goods_descr": "value of the goods description, which may be quite long or contain newlines",
            "hs_code": "",
            "invoice_info": "",
            "origin_criterion": ""
        }
        '

**Response:**

Success: full object representation

Error:

.. code-block::
    json

    {
      "non_field_errors": [
        "Can't update object - update is available only for draft or complete status"
      ]
    }

Certificate status update
*************************

``PATCH /api/certificate/v0/certificate/{id}/status/``

Request: JSON with the new status value. Response - short object representation.
Correct status transitions are ``draft`` -> ``complete`` and ``complete`` - ``lodged``.
Draft->complete status change occures automatically once criterias are met. So only correct usage
of this endpoint is to update ``complete`` certificates to ``lodged`` status. This would fire
some background tasks and do upstream processing work. Any such status change is irreversible.

* Draft: organisation is filling the certificate data yet, files are being uploaded
* Complete: certificate is ready to be lodged (all criterias were met), but still can be updated
* Lodged: Certificate is sent to upstream storage, no changes can be made.

**Request:**

.. code-block::
    bash

    curl -XPATCH http://myusername:mypassword@0.0.0.0:8010/api/certificate/v0/certificate/7e1ecef1-ae79-43c4-9291-0e1583c7bfd8/status/ \
        -H "Content-Type: application/json" \
        -H "Accept: application/json; indent=2" \
        -d '{
            "status": "lodged"
        }
        '

**Response:**

Error - can't change status to ``complete`` due to non-met criterial (files not uploaded, etc)
Error - can't change status to given because current status is incorrect (status change is linear,
you can't hop over statuses)
Error - not found object, incorrect JSON request, etc

Success - short certificate representation

Document upload
***************

``POST /api/certificate/v0/certificate/{id}/document/``

Works only for certificates in ``draft`` or ``complete`` state.
This is a multipart/form data request with next fields:

* type - one of the next values:

  * 'Exporters Information Form Update'
  * 'Evidence of origin'
  * 'extra'
  * (more may be added in the future, and some file types may have validations like objects number)

* file - the binary file content
* (more techincal fields may be added, like metadata, etc)

**Request:**

.. code-block::
    bash

    curl -X POST -S \
         -F "type=extra" -F "file=@img.jpg;type=image/jpg" \
         http://myuser:mypass@0.0.0.0:8010/api/certificate/v0/certificate/21cdf6aa-9673-4f1c-b4c4-c715e5d3f648/document/


**Response**

As a result we get short uploaded file information. Also certificate full details start to contain
this file reference.

.. code-block::
    json

    {
        "id":"ec873ed3-eb64-4c28-a842-365b8eb20264",
        "filename":"img_fMLKoXx.jpg",
        "type":"extra",
        "created_at":"2019-05-09T17:46:38.734251+10:00"
    }

Document removal
****************

``DELETE /api/certificate/v0/certificate/{id}/file/{file_id}/``

Works only for certificates in ``draft`` or ``complete`` state.
May change the certificate status from ``complete`` to ``draft`` if removed file was
required for conditions fulfillment.

Return: empty HTTP 204 response.
