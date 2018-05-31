# R-CORD Service

The RCORD Service represents the `Subscriber` in the service chain.

This service expect to be located at the beginning of the chain.

## Service configurations

As now the only possible configuration is to define the kind of access service
that sits next to it. The default (and the only one supported for now) is
'VOLTHA'.

If the R-CORD Service is configured with `access=voltha` it expect that:

- it has only one `provider_service`
- the `provider_service` exposes an API called `has_access_device(onu_serial_number)`
  that returns a boolean (this is used to validate that the ONU the subscriber
  is pointing to really exists)

## RCORDSubscriber

The `RCORDSubscriber` model is the `ServiceInstance` of the `RCORDService`.
This is an example TOSCA you can use to create one:

```yaml
tosca_definitions_version: tosca_simple_yaml_1_0
imports:
  - custom_types/rcordsubscriber.yaml
description: Create a test subscriber
topology_template:
  node_templates:
    #Activate the subscriber
    my_house:
      type: tosca.nodes.RCORDSubscriber
      properties:
        name: My House
        onu_device: BRCM1234
        mac_address: 90:E2:BA:82:FA:81
        ip_address: 192.168.0.1
```

> NOTE: an `onu_device` with the provided serial number must exists in the system.
> For more informations about ONU Devices, please refer to the
> [vOLTService](../olt-service/README.md) guide.

