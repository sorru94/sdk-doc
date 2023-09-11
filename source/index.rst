.. Astarte device SDKs documentation master file.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

###################
Astarte device SDKs
###################

************
Introduction
************

Astarte Device SDKs are ready to use libraries that provide communication and pairing primitives.
They allow to connect any device to an Astarte instance.
While an SDK is not strictly required to connect an application to Astarte using MQTT, it enables
rapid development and a pleasant developer experience.

Astarte Device SDKs should not be confused with client SDKs, as they are not meant for client to
device communications. If one is interested in an abstraction layer on top of existing APIs instead,
an optional Astarte Client SDK (such as
`astarte-go <https://github.com/astarte-platform/astarte-go>`_ ) is to be used.

Under the hood Astarte Device SDKs make use of MQTT, BSON, HTTP, persistence and crypto libraries
to implement
`Astarte MQTT v1 Protocol <https://docs.astarte-platform.org/astarte/latest/080-mqtt-v1-protocol.html>`_
and all the other useful features.

They can be easily integrated into new or existing IoT projects written in any of the supported
languages or platforms. At the moment the following SDKs are available:

* C

  * ESP 32: `astarte-device-sdk-esp32 <https://github.com/astarte-platform/astarte-device-sdk-esp32>`_

* C++

  * Qt5: `astarte-device-sdk-qt5 <https://github.com/astarte-platform/astarte-device-sdk-qt5>`_

* Elixir: `astarte-device-sdk-elixir <https://github.com/astarte-platform/astarte-device-sdk-elixir>`_
* Go: `astarte-device-sdk-go <https://github.com/astarte-platform/astarte-device-sdk-go>`_
* Java

  * Android: `astarte-device-sdk-java <https://github.com/astarte-platform/astarte-device-sdk-java>`_
  * Generic: `astarte-device-sdk-java <https://github.com/astarte-platform/astarte-device-sdk-java>`_

* Python: `astarte-device-sdk-python <https://github.com/astarte-platform/astarte-device-sdk-python>`_
* Rust: `astarte-device-sdk-rust <https://github.com/astarte-platform/astarte-device-sdk-rust>`_

Further languages and platforms will be supported in the near future.
`Requests for new SDKs <https://github.com/astarte-platform/astarte/issues>`_ are welcome.

*************
SDKs features
*************

===============
MQTT Connection
===============

Astarte Device SDKs make use of platform specific MQTT libraries and they hide all MQTT connection
management details, including smart reconnection (randomized reconnection backoff is used).

====================
Device ID Generation
====================

Some of the Astarte Device SDKs (such as the ESP32) offer optional device id generation utils that
can use the hardware id as seed.

==============================
Automatic Registration (Agent)
==============================

Astarte Device SDKs can provide an optional automatic registration mechanism that can be used on the
field, avoiding any manual data entry or additional operations. This optional component can be
disabled when performing registration during manufactoring process.

====================================
Client SSL Certs Request and Renewal
====================================

Astarte Device SDKs make use of short lived SSL certificates which are automatically renewed before
their expiration.

Astarte Device SDKs take care of the complete process from the certificate generation to the
certificate signing request.

==========================================
Data Serialization and Protocol Management
==========================================

MQTT payloads are format agnostic, hence a serialization format should be used before transmitting
data. For this specific purpose Astarte makes use of `BSON <http://bsonspec.org/>`_ format which
easily maps to JSON.

Astarte Device SDKs take care on user behalf of data serialization to BSON. Last but not least some
additional signaling messages are exchanged such as the introspection, Astarte Device SDKs take
care of automatically sending them and applying data compression when necessary.


=============================================
Data Persistence and Automatic Retransmission
=============================================

Astarte Device SDKs allow configuring persitence and reliability policies. In case of connection
loss data is stored to memory or disk (according to mappings configuration) and they are
automatically retransmitted as soon as the device is back online.

This feature is not available yet on Elixir, ESP32, Go and Python SDKs and might be not avilable on
other platforms with constrained resources.

=====================
Smart Properties Sync
=====================

Astarte has support for the concept of properties, which are kept synchronized between the server
and the device.

Thanks to the
`Astarte MQTT v1 Protocol`_ an incremental approach is employed therefore only changed properties
are synchronized. This feature is not available yet on Elixir, Go and Python SDKs and might be not
avilable on other SDKs with no `session_present` support.

===============
Data Validation
===============

Astarte Device SDKs take care of data validation before sending any data, hence errors are reported
locally on the device improving troubleshooting experience.

This feature is not available yet on ESP32 and is WIP on Rust and Python.

===================
Device Registration
===================

A device must be registered beforehand to obtain its `credentials-secret`. While there are some
manual options (such as using the `astartectl <https://github.com/astarte-platform/astartectl>`_
command or using the
`Astarte Dashboard <https://docs.astarte-platform.org/latest/015-astarte_dashboard.html>`_), almost
all Astarte Device SDKs allow to programmatically register a Device. For Go you can use the
`astarte-go`_ client.

=========
Device id
=========

Device ids are 128-bit long url-safe base64 strings without padding. They can be deterministic
(UUID v5) or random (UUID v4). UUID v5 are obtained from a namespace UUID and a payload (a
string). While all SDKs work with user-provided device ids, some also provide utilities to for
UUID generation.

.. tabs::

   .. group-tab:: C

      C (ESP32) with an unique hardware ID using device MAC address and other identification bits:

      .. code-block:: C

         // deterministic id
         astarte_err_t astarte_hwid_get_id(&hw_id);

   .. group-tab:: C++

      C++ (Qt5): not supported.

   .. group-tab:: Elixir

      Elixir: UUIDv5 can be obtained using the
      `elixir_uuid library <https://github.com/zyro/elixir-uuid>`_.

      .. code-block:: Elixir

         # random id
         device_id = :crypto.strong_rand_bytes(16)|> Base.url_encode64(padding: false)

         #deterministic id
         device_id = UUID.uuid5(namespace_uuid, payload, :raw)
               |> Astarte.Core.Device.encode_device_id()

==============================
Automatic Registration (Agent)
==============================

You can refer to the
`Astarte API for device registration <https://docs.astarte-platform.org/astarte/latest/api/index.html?urls.primaryName=Pairing%20API#/agent/registerDevice>`_
for more details.

.. tabs::

   .. group-tab:: C

      C (ESP32):

      .. code-block:: C

         astarte_pairing_config cfg =
         {
            .base_url = &base_astarte_url;
            .jwt = &jwt_token;
            .realm = &realm;
            .hw_id = &device_id;
            .credentials_secret = &credentials_secret;
         };

         astarte_err_t err = astarte_pairing_register_device(&astarte_pairing_config);

   .. group-tab:: C++

      C++ (Qt5): registration is done on device instantiation, see the next section.

   .. group-tab:: Elixir

      Elixir:

      .. code-block:: Elixir

         {:ok, %{body: %{"data" => %{"credentials_secret" => credentials_secret}}}} = Agent.register_device(client, device_id)
