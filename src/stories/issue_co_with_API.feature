Feature: Register Certificates of Origin using the API
  So that confusion and delay is minimised at the point of import
  As a Delegated Authority (such as a Chamber of Commerce)
  I need to register my CO on the chambers_app API

Scenario: Digitise Legacy (PDF only) process; create CO identity
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  When I `POST {CO identity data} /certificatesOfOrigin`
  Then I recieve an HTTP 201 response
  And my response body gives me the 'status': 'draft'
  And my response body contains a unique 'identifier'

Scenario: Digitise Legacy (PDF only) process; attach PDF
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `draft`
  And I have not yet posted a PDF for the certificate id
  When I `POST {PDF} /certificatesOfOrigin/{CO id}/pdfDoc`
  Then I receive an HTTP 201 response

Scenario: Digitise the Legacy (PDF only) process; update PDF
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `draft`
  And I have already posted a PDF to the certificate
  When I `PUT {PDF} /certificatesOfOrigin/{CO id}/pdfDoc`
  Then I receive an HTTP 201 response

Scenario: Digitise Legacy (PDF only) process; failed double post PDF
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `draft`
  And I have already posted a PDF to the certificate
  When I `POST {PDF} /certificatesOfOrigin/{CO id}/pdfDoc`
  Then I receive an error...

Scenario: Digital CO; attach JSON
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `draft`
  And I have not yet posted a PDF for the certificate id
  When I `POST {JSON} /certificatesOfOrigin/{CO id}/jsonDoc`
  Then I receive an HTTP 201 response

Scenario: Digital CO; update JSON
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `draft`
  And I have already posted a PDF to the certificate
  When I `PUT {PDF} /certificatesOfOrigin/{CO id}/jsonDoc`
  Then I receive an HTTP 201 response

Scenario: Digital CO; failed double post JSON
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `draft`
  And I have already posted a PDF to the certificate
  When I `POST {PDF} /certificatesOfOrigin/{CO id}/jsonDoc`
  Then I receive an error...

Scenario: Submit
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `draft`
  And I have already posted a PDF to the certificate
  When I `PATCH {status=pending} /certificatesOfOrigin/{CO id}`
  Then I recieve an HTTP 202 response
  And my response body includes a user message about pending submission


Scenario: Idempotent re-submittion if still pending
  Given I have a valid API token
  And my token is registered to a valid Delegated Authority
  And I have a valid CO identifier
  And the status of the CO identifier is `pending`
  When I `PATCH {status=pending} /certificatesOfOrigin/{CO id}`
  Then I recieve an HTTP 202 response
  And my response body includes a user message about pending submission
