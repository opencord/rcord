# R-CORD Profile

The R-CORD (Residential CORD) profile is `Official`.

### Service Manifest

R-CORD includes the following
[service manifest](https://github.com/opencord/platform-install/blob/master/profile_manifests/rcord.yml):

| Service              | Source Code         |
|-------------|---------------|
| vOLT                 | https://github.com/opencord/olt |
| vSG                   | https://github.com/opencord/vsg |
| vRouter             | https://github.com/opencord/vrouter |
| vTR                   | https://github.com/opencord/vtr |
| ExampleService | https://github.com/opencord/exampleservice |
| VTN                  | https://github.com/opencord/vtn |
| Fabric               | https://github.com/opencord/fabric |
| OpenStack        | https://github.com/opencord/openstack |
| ONOS               | https://github.com/opencord/onos-service |

### Model Extensions

R-CORD extends CORD's core models with the following model specification
([rcord.xproto](https://github.com/opencord/rcord/blob/master/xos/rcord.xproto)),
which represents the *subscriber* that anchors a chain of `ServiceInstances`:

```python
message CordSubscriberRoot (ServiceInstance) {
     option kind = "CordSubscriberRoot";

     required bool firewall_enable = 1 [default = False, null = False, db_index = False, blank = True];
     optional string firewall_rules = 2 [default = "accept all anywhere anywhere", null = True, db_index = False, blank = True];
     required bool url_filter_enable = 3 [default = False, null = False, db_index = False, blank = True];
     optional string url_filter_rules = 4 [default = "allow all", null = True, db_index = False, blank = True];
     required string url_filter_level = 5 [default = "PG", max_length = 30, content_type = "stripped", blank = False, null = False, db_index = False];
     required bool cdn_enable = 6 [default = False, null = False, db_index = False, blank = True];
     required bool is_demo_user = 7 [default = False, null = False, db_index = False, blank = True];
     required int32 uplink_speed = 8 [default = 1000000000, null = False, db_index = False, blank = False];
     required int32 downlink_speed = 9 [default = 1000000000, null = False, db_index = False, blank = False];
     required bool enable_uverse = 10 [default = True, null = False, db_index = False, blank = True];
     required string status = 11 [default = "enabled", choices = "(('enabled', 'Enabled'), ('suspended', 'Suspended'), ('delinquent', 'Delinquent'), ('copyrightviolation', 'Copyright Violation'))", max_length = 30, content_type = "stripped", blank = False, null = False, db_index = False];
	 }
```

### GUI Extensions

R-CORD does not include any GUI extensions.
