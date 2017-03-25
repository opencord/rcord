# R-CORD GRAPH GUI EXTENSION

## Platform install integration

Having a profile deployed is required. To add extensions listed in your `profile-manifest` as:

```
enabled_gui_extensions:
  - name: rcord
    path: orchestration/profiles/ecord/xos/gui/rcord
```

Execute: `ansible-playbook -i inventory/mock-rcord deploy-xos-gui-extensions-playbook.yml`
_NOTE: remember to replate `inventory/**` with the actual `cord_profile` you are using_ 
