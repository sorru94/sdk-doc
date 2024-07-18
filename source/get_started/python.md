# Get started with Python

Follow this guide to get started with the Astarte device SDK for the Python programming language.

## Generating a device ID

Not supported.

## Registering a device

In order for a device to connect to Astarte a registration procedure is required. This registration
will produce a device specific credential secret that will be used when connecting to Astarte.
Some of the Astarte device SDKs provide utilities to perform a device registration directly on
the device. Those APIs will require a registration JWT to be uploaded to the device. Such JWT should
be discarded following the registration procedure.

This step is only useful when registering the device through the APIs using the JWT token.
Registration of a device can also be performed outside the device in the Astarte instance using
tools such as [astartectl](https://github.com/astarte-platform/astartectl), the
[Astarte dashboard](https://docs.astarte-platform.org/astarte/latest/015-astarte_dashboard.html),
or the dedicated
[Astarte API for device registration](https://docs.astarte-platform.org/astarte/latest/api/index.html?urls.primaryName=Pairing%20API).
The generated credential secret should then be loaded manually on the device.

```python
credentials_secret = register_device_with_jwt_token(device_id, realm, jwt_token, pairing_base_url)
```

## Instantiating and connecting a new device

Now that we obtained both a device ID and a credential secret we can create a new device instance.
Some of the SDKs will connect instantly as soon as the device is instantiated while others will
require a call to a `connect` function.
Furthermore, depending on the SDK the introspection of the device might be defined while
instantiating the device or between instantiation and connection.

```python
# declare device options
device = Device(device_id, realm, credentials_secret, pairing_base_url)

# load device interfaces
device.add_interface(json.loads("/examples/interfaces/com.example.Interface.json"))

#register a callback that will be invoked everytime the device successfully connects
device.on_connected(callback)

#connect the device asynchronously
device.connect()
```

## Streaming data

All Astarte Device SDKs include primitives for sending data to a remote Astarte instance.
Streaming of data could be performed for device owned interfaces of `individual` or `object`
aggregation type.

### Streaming individual data

In Astarte interfaces with `individual` aggregation, each mapping is treated as an independent value
and is managed individually.

The snippet bellow shows how to send a value that will be inserted into the `"/test0/value"`
datastream which is defined by `"/%{sensor_id}/value"` parametric endpoint, that is part of
`"org.astarte-platform.genericsensors.Values"` datastream interface.

```python
device.send("org.astarte-platform.genericsensors.Values", "/test0/value", 0.3, timestamp=datetime.now())
```

### Streaming aggregated data

In Astarte interfaces with `object` aggregation, Astarte expects the owner to send all of the
interface's mappings at the same time, packed in a single message.

The following snippet shows how to send a value for an object aggregated interface. In this
examples, `lat` and `long` will be sent together and will be inserted into the `"/coords"`
datastream which is defined by the `"/coords"` endpoint, that is part of `"com.example.GPS"`
datastream interface.

```python
coords = {'lat': 45.409627, 'long': 11.8765254}
device.send_aggregate("com.example.GPS", "/coords", coords, timestamp=datetime.now())
```

## Setting and unsetting properties

Interfaces of `property` type represent a persistent, stateful, synchronized state with no concept
of history or timestamping. From a programming point of view, setting and unsetting properties of
device-owned interface is rather similar to sending messages on datastream interfaces.

The following snippet shows how to set a value that will be inserted into the `"/sensor0/name"`
property which is defined by `"/%{sensor_id}/name"` parametric endpoint, that is part of `"org.astarte-platform.genericsensors.AvailableSensors"` device-owned properties interface.

It should be noted how a property should be marked as unsettable in its interface definition to
be able to use the unsetting method on it.

Set property:
```python
device.send("org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name", "foobar")
```
Unset property:
```python
device.unset_property("org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name")
```
