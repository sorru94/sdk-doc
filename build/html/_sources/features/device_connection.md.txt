# Device connection

Astarte device SDKs make use of platform specific MQTT libraries and they hide all MQTTs connection
management details.

Astarte devices connect to the remote Astarte instance using mutual TLS authentication.

## Server TLS certificates support

Server authentication is performed using a TLS certificate, as such each device will need to
include a set of root certificates in order to properly verify the server certificate.

## Client TLS certificate support

Client authentication is performed using a TLS certificate issued by the Astarte instance.
This certificate is obtained through the
[Astarte API for device credentials](https://docs.astarte-platform.org/astarte/latest/api/index.html?urls.primaryName=Pairing%20API#/device/obtainCredentials).
Each device will generate a certificate signing request and the Astarte instance will issue a
corresponding x509 certificate.

## Client TLS certificate renewal

Each device SDK is responsible to check the validity of its certificate using the appropriate
[Astarte API for device credentials validation](https://docs.astarte-platform.org/astarte/latest/api/index.html?urls.primaryName=Pairing%20API#/device/obtainCredentials).

Renewal of the certificate can be performed by requesting a fresh certificate to Astarte.

## Reconnection

Astarte device SDKs implement an internal reconnection strategy that uses an exponential backoff
to avoid network overloading.
