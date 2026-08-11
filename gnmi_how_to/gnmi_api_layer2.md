# gNMI API - Layer 2 (VLAN & Switching)



## OpenConfig YANG (`xpath_target: OC-YANG`)

---

### Create VLAN

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /openconfig-interfaces:interfaces/interface[name=Vlan100]:@./vlan.json
```

vlan.json:
```json
{"openconfig-interfaces:interface": [{"name": "Vlan100", "config": {"name": "Vlan100"}}]}
```

---

### Get VLAN

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Vlan100]
```

Response:
```json
{
  "openconfig-interfaces:interface": [{
    "config": {"enabled": true, "name": "Vlan100"},
    "name": "Vlan100",
    "state": {"admin-status": "UP", "enabled": true, "mtu": 9100, "name": "Vlan100"}
  }]
}
```

---

### Delete VLAN

> Remove members and IP addresses first.

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /openconfig-interfaces:interfaces/interface[name=Vlan100]
```

---

### Remove VLAN Member (OC trunk)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /openconfig-interfaces:interfaces/interface[name=Ethernet4]/\
openconfig-if-ethernet:ethernet/openconfig-vlan:switched-vlan/config/trunk-vlans[trunk-vlans=100]
```

---

## SONiC YANG (`xpath_target: OC-YANG`)

---

### Create VLAN (SONiC)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-vlan:sonic-vlan/VLAN:@./vlan_sonic.json
```

vlan_sonic.json:
```json
{"sonic-vlan:VLAN": {"VLAN_LIST": [{"name": "Vlan100", "vlanid": 100, "admin_status": "up"}]}}
```

---

### Get VLAN (SONiC)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-vlan:sonic-vlan/VLAN/VLAN_LIST[name=Vlan100]
```

Response:
```json
{"sonic-vlan:VLAN_LIST": [{"admin_status": "up", "name": "Vlan100", "vlanid": 100}]}
```

---

### Add VLAN Member

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-vlan:sonic-vlan/VLAN_MEMBER/VLAN_MEMBER_LIST:@./vm.json
```

vm.json:
```json
{"sonic-vlan:VLAN_MEMBER_LIST": [{"name": "Vlan100", "ifname": "Ethernet4", "tagging_mode": "tagged"}]}
```

tagging_mode: `tagged` | `untagged`

---

### Delete VLAN Member

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-vlan:sonic-vlan/VLAN_MEMBER/VLAN_MEMBER_LIST[name=Vlan100][ifname=Ethernet4]
```

---

### Delete VLAN (SONiC)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-vlan:sonic-vlan/VLAN/VLAN_LIST[name=Vlan100]
```

---

### XSTP Configuration

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-xstp:sonic-xstp/XSTP_GLOBAL/XSTP_GLOBAL_LIST:@./xstp.json
```

xstp.json:
```json
{"sonic-xstp:XSTP_GLOBAL_LIST": [{"param": "mode", "value": "rpvst"}]}
```

---

### Storm Control

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-storm-control:sonic-storm-control/\
PORT_STORM_CONTROL/PORT_STORM_CONTROL_LIST:@./sc.json
```

sc.json:
```json
{"sonic-storm-control:PORT_STORM_CONTROL_LIST": [{"ifname": "Ethernet4", "storm_type": "broadcast", "kbps": "1000"}]}
```

> `kbps` must be string. storm_type: `broadcast` | `unknown-unicast` | `unknown-multicast`

---

### Switch Config (FDB aging time)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-switch:sonic-switch/SWITCH/switch:@./sw.json
```

sw.json:
```json
{"sonic-switch:switch": {"fdb_aging_time": 600}}
```

---

### Other Layer 2 Modules (GET only)

All return `{}` when not configured:

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-lldp:lldp

gnmi_get ... -xpath /sonic-lldp:sonic-lldp
gnmi_get ... -xpath /sonic-fdb:sonic-fdb
gnmi_get ... -xpath /sonic-igmp-snooping:sonic-igmp-snooping
gnmi_get ... -xpath /sonic-stp:sonic-stp
gnmi_get ... -xpath /openconfig-mclag:mclag
gnmi_get ... -xpath /sonic-mclag:sonic-mclag
```
