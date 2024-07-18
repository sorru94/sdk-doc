# Device registration

Registering a new device to the an Astarte instance can be performed in two ways:
1. Using the registration utilities in the Astarte instance itself. Such utilities will produce
   a credential secret. Such credential secret can then be transferred to the device an used to
   connect to Astarte.
2. Using the on board registration utilities. This device APIs require an authorization JWT
   generated in the Astarte instance and then transferred to the device. The registration APIs
   will use the JWT token to negotiate a credential secret from the Astarte instance.

Both methods will require a valid device ID to perform the registration.

## On board device registration

Registering the device is performed using the
[Astarte API for device registration](https://docs.astarte-platform.org/astarte/latest/api/index.html?urls.primaryName=Pairing%20API#/agent/registerDevice).
