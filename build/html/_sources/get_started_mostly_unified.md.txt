# Getting started guide (Option 2)

All of the Astarte device SDKs are dependent on an Astarte instance running locally or remotely.
As such, if you are not already familiar with setting up an Astarte instance we recommend reading
the [Astarte documentation](https://docs.astarte-platform.org/astarte/latest/001-intro_user.html).
Specifically the
[Astarte in 5 minutes](https://docs.astarte-platform.org/astarte/latest/010-astarte_in_5_minutes.html)
page can help setting up quickly an instance of Astarte for testing purposes.

Assuming a correctly configured Astarte instance is present, any of the Astarte device SDKs can be
used to interact with it.

::::{tab-set}

:::{tab-item} C (ESP32)

## Generating a device ID

A device ID will be required to uniquely identify a device in an Astarte instance.
Some of the Astarte device SDKs provide utilities to generate a deterministic or random device
identifier, in some cases based on hardware information.

This step is only useful when registering a device using a JWT token and the provided Astarte device
SDKs registration APIs. Registration of a device can also be performed outside the device in the
Astarte instance. In such cases the device ID should be obtained via
[astartectl](https://github.com/astarte-platform/astartectl), or the
[Astarte dashboard](https://docs.astarte-platform.org/astarte/latest/015-astarte_dashboard.html).
The device ID should then be loaded manually on the device.

Generating a device ID from device MAC address and other hardware identification bits:
```C
astarte_err_t astarte_hwid_get_id(&hw_id);
```

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

```C
astarte_pairing_config cfg =
{
.base_url = &base_astarte_url;
.jwt = &jwt_token;
.realm = &realm;
.hw_id = &device_id;
.credentials_secret = &credentials_secret;
};

astarte_err_t err = astarte_pairing_register_device(&astarte_pairing_config);
```

## Instantiating and connecting a new device

Now that we obtained both a device ID and a credential secret we can create a new device instance.
Some of the SDKs will connect instantly as soon as the device is instantiated while others will
require a call to a `connect` function.
Furthermore, depending on the SDK the introspection of the device might be defined while
instantiating the device or between instantiation and connection.

```C
// Instantiating a device
astarte_device_config_t cfg = {
    .data_event_callback = astarte_data_events_handler,
    .unset_event_callback = astarte_unset_events_handler,
    .connection_event_callback = astarte_connection_events_handler,
    .disconnection_event_callback = astarte_disconnection_events_handler,
    .credentials_secret = cred_sec,
    .hwid = hwid,
    .realm = realm,
};
astarte_device_handle_t device = astarte_device_init(&cfg);
if (!device) {
    ESP_LOGE(TAG, "Failed to init astarte device");
    return;
}
// Adding an interface
astarte_device_add_interface(device, &device_example_interface);
// Starting a device
if (astarte_device_start(device) != ASTARTE_OK) {
    ESP_LOGE(TAG, "Failed to start astarte device");
    return;
}
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

```C
struct timeval tv;
gettimeofday(&tv, NULL);
uint64_t ts = tv->tv_sec * 1000 + tv->tv_usec / 1000;

astarte_err_t err = astarte_device_stream_double_with_timestamp(device, "org.astarte-platform.genericsensors.Values", "/test0/value", 0.3, ts, 0);
```

### Streaming aggregated data

In Astarte interfaces with `object` aggregation, Astarte expects the owner to send all of the
interface's mappings at the same time, packed in a single message.

The following snippet shows how to send a value for an object aggregated interface. In this
examples, `lat` and `long` will be sent together and will be inserted into the `"/coords"`
datastream which is defined by the `"/coords"` endpoint, that is part of `"com.example.GPS"`
datastream interface.

```C
astarte_bson_serializer_init(&bs);
astarte_bson_serializer_append_double(&bs, "lat", 45.409627);
astarte_bson_serializer_append_double(&bs, "long", 11.8765254);
astarte_bson_serializer_append_end_of_document(&bs);
int size;
const void *coord = astarte_bson_serializer_get_document(&bs, &size);

struct timeval tv;
gettimeofday(&tv, NULL);
uint64_t ts = tv->tv_sec * 1000 + tv->tv_usec / 1000;

astarte_device_stream_aggregate_with_timestamp(device, "com.example.GPS", "/coords", coords, ts, 0);
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
```C
astarte_device_set_string_property(device, "org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name", "foobar");
```
Unset property:
```C
astarte_device_unset_path(device, "org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name");
```
:::

:::{tab-item} C++ (Qt5)

## Generating a device ID

Not supported.

## Registering a device

Registration is done on device instantiation, see the next section.

## Instantiating and connecting a new device

Now that we obtained both a device ID and a credential secret we can create a new device instance.
Some of the SDKs will connect instantly as soon as the device is instantiated while others will
require a call to a `connect` function.
Furthermore, depending on the SDK the introspection of the device might be defined while
instantiating the device or between instantiation and connection.

```C++
// Instantiating a device and declaring the introspection
m_sdk = new AstarteDeviceSDK(QDir::currentPath() + QStringLiteral("./examples/device_sdk.conf").arg(deviceId), QDir::currentPath() + QStringLiteral("./examples/interfaces"), deviceId.toLatin1());
// Connecting to the Astarte instance
connect(m_sdk->init(), &Hemera::Operation::finished, this, &AstarteStreamQt5Test::checkInitResult);
// Setting data handlers
connect(m_sdk, &AstarteDeviceSDK::dataReceived, this, &AstarteStreamQt5Test::handleIncomingData);
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

```C++
m_sdk->sendData("org.astarte-platform.genericsensors.Values", "/test0/value", 0.3, QDateTime::currentDateTime());
```

### Streaming aggregated data

In Astarte interfaces with `object` aggregation, Astarte expects the owner to send all of the
interface's mappings at the same time, packed in a single message.

The following snippet shows how to send a value for an object aggregated interface. In this
examples, `lat` and `long` will be sent together and will be inserted into the `"/coords"`
datastream which is defined by the `"/coords"` endpoint, that is part of `"com.example.GPS"`
datastream interface.

```C++
QVariantHash coords;
coords.insert(QStringLiteral("lat"), 45.409627);
coords.insert(QStringLiteral("long"), 11.8765254);
m_sdk->sendData("com.example.GPS", "/coords", coords, QDateTime::currentDateTime());
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
```C++
m_sdk->sendData(m_interface, m_path, value, QDateTime::currentDateTime());
```
Unset property:
```C++
m_sdk->sendUnset(m_interface, m_path);
```
:::

:::{tab-item} Elixir

## Generating a device ID

A device ID will be required to uniquely identify a device in an Astarte instance.
Some of the Astarte device SDKs provide utilities to generate a deterministic or random device
identifier, in some cases based on hardware information.

This step is only useful when registering a device using a JWT token and the provided Astarte device
SDKs registration APIs. Registration of a device can also be performed outside the device in the
Astarte instance. In such cases the device ID should be obtained via
[astartectl](https://github.com/astarte-platform/astartectl), or the
[Astarte dashboard](https://docs.astarte-platform.org/astarte/latest/015-astarte_dashboard.html).
The device ID should then be loaded manually on the device.

A device ID can be generate randomly:
```elixir
device_id = :crypto.strong_rand_bytes(16)|> Base.url_encode64(padding: false)
```
Or in a deterministic way:
```elixir
device_id = UUID.uuid5(namespace_uuid, payload, :raw)
    |> Astarte.Core.Device.encode_device_id()
```

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

```elixir
{:ok, %{body: %{"data" => %{"credentials_secret" => credentials_secret}}}} = Agent.register_device(client, device_id)
```

## Instantiating and connecting a new device

Now that we obtained both a device ID and a credential secret we can create a new device instance.
Some of the SDKs will connect instantly as soon as the device is instantiated while others will
require a call to a `connect` function.
Furthermore, depending on the SDK the introspection of the device might be defined while
instantiating the device or between instantiation and connection.

```elixir
# declare device options
opts = [pairing_url: pairing_url, realm: realm, device_id: device_id, interface_provider: "./examples/interfaces", credentials_secret: credentials_secret]

# start device and connect asynchronously
{:ok, pid} = Device.start_link(opts)

# blocking (optional)
:ok <- Device.wait_for_connection(device_pid)
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

```elixir
Device.send_datastream(pid, "org.astarte-platform.genericsensors.Values", "/test0/value", 0.3, timestamp: DateTime.utc_now())
```

### Streaming aggregated data

In Astarte interfaces with `object` aggregation, Astarte expects the owner to send all of the
interface's mappings at the same time, packed in a single message.

The following snippet shows how to send a value for an object aggregated interface. In this
examples, `lat` and `long` will be sent together and will be inserted into the `"/coords"`
datastream which is defined by the `"/coords"` endpoint, that is part of `"com.example.GPS"`
datastream interface.

```elixir
coords = %{lat: 45.409627, long: 11.8765254}
Device.send_datastream(pid, "com.example.GPS", "/coords", coords, timestamp: DateTime.utc_now())
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
```elixir
Device.set_property(pid, "org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name", "foobar")
```
Unset property:
```elixir
Device.unset_property(pid, "org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name")
```
:::

:::{tab-item} Go

## Generating a device ID

A device ID will be required to uniquely identify a device in an Astarte instance.
Some of the Astarte device SDKs provide utilities to generate a deterministic or random device
identifier, in some cases based on hardware information.

This step is only useful when registering a device using a JWT token and the provided Astarte device
SDKs registration APIs. Registration of a device can also be performed outside the device in the
Astarte instance. In such cases the device ID should be obtained via
[astartectl](https://github.com/astarte-platform/astartectl), or the
[Astarte dashboard](https://docs.astarte-platform.org/astarte/latest/015-astarte_dashboard.html).
The device ID should then be loaded manually on the device.

A device ID can be generate randomly:
```go
random_id, err := GenerateRandomAstarteId()
```
Or in a deterministic way:
```go
namespaced_id, err := GetNamespacedAstarteDeviceID(namespaceUuid,payload)
```

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

```go
credentials_secret, err := client.Pairing.RegisterDevice(realm, deviceID)
```

## Instantiating and connecting a new device

Now that we obtained both a device ID and a credential secret we can create a new device instance.
Some of the SDKs will connect instantly as soon as the device is instantiated while others will
require a call to a `connect` function.
Furthermore, depending on the SDK the introspection of the device might be defined while
instantiating the device or between instantiation and connection.

```go
// Create device
d, err := device.NewDevice(deviceID, deviceRealm, credentialsSecret, apiEndpoint)
if err != nil {
    fmt.Println(err.Error())
    os.Exit(1)
}

// Load interface - fix this path(s) to load the right interface
byteValue, err := ioutil.ReadFile("/examples/interfaces/com.example.Interface.json")
if err != nil {
    fmt.Println(err.Error())
    os.Exit(1)
}
iface := interfaces.AstarteInterface{}
if iface, err = interfaces.ParseInterface(byteValue); err != nil {
    fmt.Println(err.Error())
    os.Exit(1)
}

if err = d.AddInterface(iface); err != nil {
    fmt.Println(err.Error())
    os.Exit(1)
}

// Set up callbacks
d.OnConnectionStateChanged = func(d *device.Device, state bool) {
    fmt.Printf("Device connection state: %t\n", state)
}

// Connect the device and listen to the connection status channel
c := make(chan error)
d.Connect(c)
if err := <-c; err == nil {
    fmt.Println("Connected successfully")
} else {
    fmt.Println(err.Error())
    os.Exit(1)
}
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

```go
d.SendIndividualMessageWithTimestamp("org.astarte-platform.genericsensors.Values", "/test0/value", 0.3, time.Now())
```

### Streaming aggregated data

In Astarte interfaces with `object` aggregation, Astarte expects the owner to send all of the
interface's mappings at the same time, packed in a single message.

The following snippet shows how to send a value for an object aggregated interface. In this
examples, `lat` and `long` will be sent together and will be inserted into the `"/coords"`
datastream which is defined by the `"/coords"` endpoint, that is part of `"com.example.GPS"`
datastream interface.

```go
coords := map[string]double{"lat": 45.409627, "long": 11.8765254}
d.SendAggregateMessageWithTimestamp("com.example.GPS", "/coords", coords, time.Now())
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
```go
d.SetProperty("org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name", "foobar")
```
Unset property:
```go
d.UnsetProperty("org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name")
```
:::

:::{tab-item} Java/Android

## Generating a device ID

A device ID will be required to uniquely identify a device in an Astarte instance.
Some of the Astarte device SDKs provide utilities to generate a deterministic or random device
identifier, in some cases based on hardware information.

This step is only useful when registering a device using a JWT token and the provided Astarte device
SDKs registration APIs. Registration of a device can also be performed outside the device in the
Astarte instance. In such cases the device ID should be obtained via
[astartectl](https://github.com/astarte-platform/astartectl), or the
[Astarte dashboard](https://docs.astarte-platform.org/astarte/latest/015-astarte_dashboard.html).
The device ID should then be loaded manually on the device.

A device ID can be generate randomly:
```java
String randomID = AstarteDeviceIdUtils.generateId();
```
Or in a deterministic way:
```java
String deviceID = AstarteDeviceIdUtils.generateId(namespaceUuid, payload);
```

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

```java
AstartePairingService astartePairingService = new AstartePairingService(pairing_url, realm);
String credentialsSecret = astartePairingService.registerDevice(jwt_token, device_id);
```

## Instantiating and connecting a new device

Now that we obtained both a device ID and a credential secret we can create a new device instance.
Some of the SDKs will connect instantly as soon as the device is instantiated while others will
require a call to a `connect` function.
Furthermore, depending on the SDK the introspection of the device might be defined while
instantiating the device or between instantiation and connection.

```java
// Device creation
// connectionSource allows to connect to a db for persistency
// The interfaces supported by the device are populated by ExampleInterfaceProvider
AstarteDevice device =
    new AstarteGenericDevice(
        deviceId,
        realm,
        credentialsSecret,
        new ExampleInterfaceProvider(),
        pairingUrl,
        connectionSource);

// ExampleMessageListener listens for device connection, disconnection and failure.
device.setAstarteMessageListener(new ExampleMessageListener());

// Connect the device
device.connect();
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

```java
genericSensorsValuesInterface.streamData("/test0/value", 0.3, DateTime.now());
```

### Streaming aggregated data

In Astarte interfaces with `object` aggregation, Astarte expects the owner to send all of the
interface's mappings at the same time, packed in a single message.

The following snippet shows how to send a value for an object aggregated interface. In this
examples, `lat` and `long` will be sent together and will be inserted into the `"/coords"`
datastream which is defined by the `"/coords"` endpoint, that is part of `"com.example.GPS"`
datastream interface.

```java
Map<String, Double> coords = new HashMap<String, Double>()
{
    {
        put("lat", 45.409627);
        put("long", 11.8765254);
    }
};

exampleGPSInterface.streamData("/coords", coords, DateTime.now());
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
```java
availableSensorsInterface.setProperty("/sensor0/name", "foobar");
```
Unset property:
```java
propertyInterface.unsetProperty("/sensor0/name");
```
:::

:::{tab-item} Python

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
:::

:::{tab-item} Rust

## Generating a device ID

A device ID will be required to uniquely identify a device in an Astarte instance.
Some of the Astarte device SDKs provide utilities to generate a deterministic or random device
identifier, in some cases based on hardware information.

This step is only useful when registering a device using a JWT token and the provided Astarte device
SDKs registration APIs. Registration of a device can also be performed outside the device in the
Astarte instance. In such cases the device ID should be obtained via
[astartectl](https://github.com/astarte-platform/astartectl), or the
[Astarte dashboard](https://docs.astarte-platform.org/astarte/latest/015-astarte_dashboard.html).
The device ID should then be loaded manually on the device.

A device ID can be generate randomly:
```rust
let random_uuid = astarte_sdk::registration::generate_random_uuid();
```
Or in a deterministic way:
```rust
let namespaced_id = astarte_sdk::registration::generate_uuid(namespaceUuid, &payload);
```

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

```rust
let credentials_secret =
    astarte_sdk::registration::register_device(&jwt_token, &pairing_url, &realm, &device_id)
        .await?;
```

## Instantiating and connecting a new device

Now that we obtained both a device ID and a credential secret we can create a new device instance.
Some of the SDKs will connect instantly as soon as the device is instantiated while others will
require a call to a `connect` function.
Furthermore, depending on the SDK the introspection of the device might be defined while
instantiating the device or between instantiation and connection.

```rust
// declare device options
let mut sdk_options =
    AstarteOptions::new(&realm, &device_id, &credentials_secret, &pairing_url);

// load interfaces from a directory
sdk_options
    .add_interface_files("./examples/interfaces")
    .unwrap();

// instance and connect the device.
let mut device = AstarteDeviceSdk::new(&sdk_options).await.unwrap();
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

```rust
/// send data without an explicit timestamp
device.send("org.astarte-platform.genericsensors.Values", "/test0/value", 3).await?;

/// send data with an explicit timestamp
let timestamp = Utc.timestamp(1537449422, 0);
device.send_with_timestamp("org.astarte-platform.genericsensors.Values", "/test0/value", 3, timestamp).await?;
```

### Streaming aggregated data

In Astarte interfaces with `object` aggregation, Astarte expects the owner to send all of the
interface's mappings at the same time, packed in a single message.

The following snippet shows how to send a value for an object aggregated interface. In this
examples, `lat` and `long` will be sent together and will be inserted into the `"/coords"`
datastream which is defined by the `"/coords"` endpoint, that is part of `"com.example.GPS"`
datastream interface.

```rust
use astarte_device_sdk_derive::AstarteAggregate;
/// Coords must derive AstarteAggregate
#[derive(AstarteAggregate)]
struct Coords {
    lat: f64,
    long: f64,
}
[...]
let coords = Coords{lat:  45.409627, long: 11.8765254};

// stream data with an explicit timestamp
let timestamp = Utc.timestamp(1537449422, 0);
device.send_object_with_timestamp("com.example.GPS", "/coords", coords, timestamp).await?;

// stream data without an explicit timestamp
device.send_object("com.example.GPS", "/coords", coords).await?;
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
```rust
device.send("org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name", "foobar").await?;
```
Unset property:
```rust
device.unset("org.astarte-platform.genericsensors.AvailableSensors", "/sensor0/name").await?;
```
:::

::::
