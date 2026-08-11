# gNMI API - Layer 3


## OpenConfig YANG (`xpath_target: OC-YANG`)

---

### Get Network Instance (VRF)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-network-instance:network-instances
```

Response:
```json
{
  "openconfig-network-instance:network-instances": {
    "network-instance": [
      {
        "config": {
          "type": "openconfig-network-instance-types:L2L3"
        },
        "name": "Vlan100",
        "vlans": {
          "vlan": [{
            "state": {"name": "Vlan100", "vlan-id": 100},
            "vlan-id": 100
          }]
        }
      }
    ]
  }
}
```

---

### IPv4 Address on Interface

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet48]/\
subinterfaces/subinterface[index=0]/openconfig-if-ip:ipv4/addresses
```

Response:
```json
{
  "openconfig-if-ip:addresses": {
    "address": [{
      "config": {
        "ip": "192.168.99.1",
        "openconfig-interfaces-ext:secondary": false,
        "prefix-length": 24
      },
      "ip": "192.168.99.1",
      "state": {
        "ip": "192.168.99.1",
        "openconfig-interfaces-ext:secondary": false,
        "prefix-length": 24
      }
    }]
  }
}
```

---

### DHCP Relay Agent

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-relay-agent:relay-agent
```

---

## SONiC YANG (`xpath_target: OC-YANG`)

---

### Add IP to Ethernet Interface

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-interface:sonic-interface/INTERFACE/INTERFACE_IPADDR_LIST:@./ip.json
```

ip.json:
```json
{"sonic-interface:INTERFACE_IPADDR_LIST": [{"portname": "Ethernet8", "ip_prefix": "172.30.0.1/30"}]}
```

> Key field is `portname` (not `ifname`)

---

### Delete IP from Ethernet Interface

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-interface:sonic-interface/INTERFACE/\
INTERFACE_IPADDR_LIST[portname=Ethernet8][ip_prefix=172.30.0.1/30]
```

---

### Add IP to VLAN Interface

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-vlan-interface:sonic-vlan-interface/\
VLAN_INTERFACE/VLAN_INTERFACE_IPADDR_LIST:@./vip.json
```

vip.json:
```json
{"sonic-vlan-interface:VLAN_INTERFACE_IPADDR_LIST": [{"vlanName": "Vlan200", "ip_prefix": "10.200.0.1/24"}]}
```

---

### Delete IP from VLAN Interface

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-vlan-interface:sonic-vlan-interface/\
VLAN_INTERFACE/VLAN_INTERFACE_IPADDR_LIST[vlanName=Vlan200][ip_prefix=10.200.0.1/24]
```

---

### Create Static Route

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-local-routing:sonic-local-routing/STATIC_ROUTE/STATIC_ROUTE_LIST:@./rt.json
```

rt.json:
```json
{
  "sonic-local-routing:STATIC_ROUTE_LIST": [{
    "prefix": "172.16.0.0/16",
    "vrf": "default",
    "nexthop": "10.200.0.2",
    "ifname": "",
    "distance": "1",
    "nexthop-vrf": ""
  }]
}
```

> `distance` must be string type. Key: `[vrf=default][prefix=172.16.0.0/16]`

---

### Delete Static Route

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-local-routing:sonic-local-routing/\
STATIC_ROUTE/STATIC_ROUTE_LIST[vrf=default][prefix=172.16.0.0/16]
```

---

### Create VRF

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-vrf:sonic-vrf/VRF/VRF_LIST:@./vrf.json
```

vrf.json:
```json
{"sonic-vrf:VRF_LIST": [{"vrf_name": "Vrf1"}]}
```

---

### Delete VRF

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-vrf:sonic-vrf/VRF/VRF_LIST[vrf_name=Vrf1]
```

---

### Other Layer 3 Modules (GET only)

All return `{}` when not configured:

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-portchannel-interface:sonic-portchannel-interface
gnmi_get ... -xpath /sonic-vxlan:sonic-vxlan
gnmi_get ... -xpath /sonic-static-anycast-gateway:sonic-static-anycast-gateway
gnmi_get ... -xpath /sonic-arp:sonic-arp
gnmi_get ... -xpath /sonic-vrrp:sonic-vrrp
gnmi_get ... -xpath /sonic-dhcp-relay:sonic-dhcp-relay
gnmi_get ... -xpath /sonic-bgp-global:sonic-bgp-global
gnmi_get ... -xpath /sonic-bgp-neighbor:sonic-bgp-neighbor
gnmi_get ... -xpath /sonic-bgp-peergroup:sonic-bgp-peergroup
gnmi_get ... -xpath /sonic-vlan-sub-interface:sonic-vlan-sub-interface
gnmi_get ... -xpath /sonic-obj-track:sonic-obj-track
gnmi_get ... -xpath /sonic-nat:sonic-nat
gnmi_get ... -xpath /sonic-pbr:sonic-pbr
```

> Note: `openconfig-local-routing:local-routes` is NOT supported on this build.
> Use `sonic-local-routing` instead.
