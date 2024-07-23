# Data streaming

Each Astarte device SDK can transmit and receive data to one of the interfaces present in its
introspection.

## Individual data transmission and reception

Devices can transmit and receive data for individual interfaces.
Depending on the language and framework used by the SDK it might be required to place the data to
transmit in a dedicated structure.

## Aggregated data transmission and reception

Devices can transmit and receive data for aggregated interfaces.
Depending on the language and framework used by the SDK it might be required to place the data to
transmit in a dedicated structure.

## Reliability support

The devices ensure a level of reliability for all the data to transmitted or received. This level
of reliability is specified in the interfaces definition and is implemented using MQTT QoS levels.

## Data persistence and automatic retransmission

Astarte Device SDKs allow configuring persitence for high enough reliability levels. In case of
connection loss data is stored to memory or disk (according to configuration) and they are
automatically retransmitted as soon as the device is back online.
