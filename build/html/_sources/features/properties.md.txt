# Properties

Astarte has support for the concept of properties, which are kept synchronized between the server
and the device.

## Setting/unsetting device properties

Device properties can be set in each device and each value change is communicated to the Astarte
instance.
Unsetting properties will be allowed only for properties are defined as unsettable in their
interface definition.

## Setting/unsetting server properties

Server properties are property of the Astarte instance and can't be modified by the device.
However they can be added to the device introspection and any change for their value will be
communicated to the device.
Unsetting properties will be allowed only for properties are defined as unsettable in their
interface definition.

## Properties presistency

Astarte device SDKs store in persistent memory their owned properties.
This ensures a correct synchronization between Astarte and the device in cases of re-connections.
