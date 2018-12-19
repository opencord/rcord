# R-CORD Service

The RCORD Service represents the `Subscriber` in the service chain. This service is always located at the beginning of a chain.

## Models

The R-CORD service has the following three models:

- `RCORDService`. In addition to the standard Service model fields such as `name`, adds the following R-CORD-specific fields:
    - `access`. Type of access service. Currently the only usable value is "voltha".
- `RCORDSubscriber`. This model extends `ServiceInstance` and holds several subscriber-related fields:
    - `creator`. The user that created the subscriber. Data plane services that implement compute resources may be able to leverage the `creator` field to account for ownership of those compute resources.
    - `status`. [`enabled` | `disabled` | `pre-provisioned` | `awaiting-auth` | `auth-failed`]. The status of the subscriber, often determined by the workflow driver.
    - `c_tag`, `s_tag`. VLAN tags associated with this subscriber.
    - `onu_device`. Serial number of subscriber's ONU. Must match an ONU Device in an access service.
    - `mac_address`. MAC address of subscriber.
    - `nas_port_id`.
    - `circuit_id`.
    - `remote_id`.
- `RCORDIpAddress`. Holds an IP address that is associated with a subscriber. These are typically created by the workflow driver, when it handles DHCP messages.
    - `subscriber`. Relation to the subscriber that this IP address applies to.
    - `ip`. IP Address.
    - `description`. A short description of the IP Address.



## Example Tosca - Create a Subscriber

The following TOSCA recipe creates an `RCORDSubscriber`:

```yaml
tosca_definitions_version: tosca_simple_yaml_1_0
imports:
  - custom_types/rcordsubscriber.yaml

description: Pre-provsion a subscriber

topology_template:
  node_templates:

    # Pre-provision the subscriber
    onf_subscriber_1:
      type: tosca.nodes.RCORDSubscriber
      properties:
        name: Sub_BRCM22222222
        status: pre-provisioned
        c_tag: 111
        s_tag: 111
        onu_device: BRCM22222222
        nas_port_id : "PON 1/1/03/1:1.1.1"
        circuit_id: foo1
        remote_id: bar1
```

> NOTE: an `onu_device` with the provided serial number must exist in the system.
> For more informations about ONU Devices, please refer to the
> [vOLTService](../olt-service/README.md) guide.

## Integration with other Services

The R-CORD Service has no western neighbors, as it is always the root of a subscriber service chain. It will have a westbound neighbor, which is typically an access service.

If the R-CORD Service is configured with `access=voltha`, the following requirements apply:

- There is only one `provider_service` linked to the R-CORD Servioce.
- The `provider_service` exposes an API called `has_access_device(onu_serial_number)`
  that returns a boolean. This is used to validate that the ONU the subscriber
  is pointing to really exists.

## Synchronizer workflow

The R-CORD Service synchronizer implements no sync steps as it does not directly interact with any external components. It does implement one model policy.

### RCORDSubscriberPolicy

The policy manages the service chain associated with the subscriber. If the subscriber is in `pre-provisioned` status, then no work is done. Otherwise the policy attempts to bring the service chain into compliance with the status field. Statuses of `enabled` are allocated a service chain. Statuses of `awaiting-auth`, `auth-failed`, or `disabled` are prevented from having a service chain.

The service chain typically proceeds eastbound from the RCORDSubscriber to an access service instance, such as VOLTServiceInstance.  



