# gNMI API - Interface


## OpenConfig YANG (`xpath_target: OC-YANG`)


### Get Interface Configuration

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet0]/config
```

Response:
```json
{
  "openconfig-interfaces:config": {
    "description": "",
    "enabled": true,
    "mtu": 9100,
    "name": "Ethernet0"
  }
}
```

---

### Update Interface Configuration

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update /openconfig-interfaces:interfaces/interface[name=Ethernet0]/config:@./iface.json
```

iface.json:
```json
{
  "openconfig-interfaces:config": {
    "description": "uplink",
    "enabled": true,
    "mtu": 9100,
    "name": "Ethernet0"
  }
}
```

---

### Update MTU (leaf)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update /openconfig-interfaces:interfaces/interface[name=Ethernet0]/config/mtu:@./mtu.json
```

mtu.json:
```json
{"openconfig-interfaces:mtu": 1500}
```

---

### Get Interface State (read-only)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet0]/state
```

Response:
```json
{
  "openconfig-interfaces:state": {
    "admin-status": "UP",
    "oper-status": "DOWN",
    "enabled": true,
    "mtu": 9100,
    "name": "Ethernet0",
    "description": "",
    "counters": {
      "in-octets": "0",
      "in-pkts": "0",
      "in-unicast-pkts": "0",
      "in-broadcast-pkts": "0",
      "in-multicast-pkts": "0",
      "in-discards": "0",
      "in-errors": "0",
      "out-octets": "0",
      "out-pkts": "0",
      "out-unicast-pkts": "0",
      "out-broadcast-pkts": "0",
      "out-multicast-pkts": "0",
      "out-discards": "0",
      "out-errors": "0"
    }
  }
}
```

---

### Get Interface Counters

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet48]/state/counters
```

Response:
```json
{
  "openconfig-interfaces:counters": {
    "in-broadcast-pkts": "0",
    "in-discards": "14",
    "in-errors": "0",
    "in-multicast-pkts": "21",
    "in-octets": "4883",
    "in-pkts": "21",
    "in-unicast-pkts": "0",
    "out-broadcast-pkts": "5000",
    "out-discards": "0",
    "out-errors": "0",
    "out-multicast-pkts": "21",
    "out-octets": "5434883",
    "out-pkts": "5021",
    "out-unicast-pkts": "0"
  }
}
```

Get single counter leaf:
```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet48]/state/counters/in-octets
```

Response:
```json
{"openconfig-interfaces:in-octets": "4883"}
```

---

### Get Ethernet Port Config (speed + aggregate-id)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet0]/\
openconfig-if-ethernet:ethernet/config
```

Response:
```json
{
  "openconfig-if-ethernet:config": {
    "auto-negotiate": true,
    "openconfig-if-aggregate:aggregate-id": "",
    "port-speed": "openconfig-if-ethernet:SPEED_1GB"
  }
}
```

port-speed values: `SPEED_10MB` | `SPEED_100MB` | `SPEED_1GB` | `SPEED_10GB` | `SPEED_25GB` |
`SPEED_40GB` | `SPEED_50GB` | `SPEED_100GB` | `SPEED_200GB` | `SPEED_400GB`

---

### Update Port Speed

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update /openconfig-interfaces:interfaces/interface[name=Ethernet0]/\
openconfig-if-ethernet:ethernet/config/port-speed:@./spd.json
```

spd.json:
```json
{"openconfig-if-ethernet:port-speed": "openconfig-if-ethernet:SPEED_1GB"}
```

---

### Get Ethernet (config + state combined)

> Use this path to get port-speed from state.
> Leaf path `/ethernet/state/port-speed` is NOT supported on this build.

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet0]/\
openconfig-if-ethernet:ethernet
```

---

### Create PortChannel

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /openconfig-interfaces:interfaces/interface[name=PortChannel1]:@./pc.json
```

pc.json:
```json
{
  "openconfig-interfaces:interface": [{
    "name": "PortChannel1",
    "config": {"name": "PortChannel1", "mtu": 9100}
  }]
}
```

---

### Get PortChannel Aggregation

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=PortChannel1]/\
openconfig-if-aggregate:aggregation
```

Response:
```json
{
  "openconfig-if-aggregate:aggregation": {
    "config": {"lag-type": "LACP"},
    "state": {"lag-type": "LACP", "member": [""], "min-links": 0}
  }
}
```

---

### Delete PortChannel

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /openconfig-interfaces:interfaces/interface[name=PortChannel1]
```

---

### Get Port Breakout Mode

> component name uses port number format `1/1`, not `Ethernet0`

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-platform:components/component[name=1/53]
```

Response:
```json
{
  "openconfig-platform:component": [{
    "name": "1/53",
    "port": {
      "openconfig-platform-port:breakout-mode": {
        "config": {"channel-speed": "openconfig-if-ethernet:SPEED_100GB", "num-channels": 1},
        "state": {
          "channel-speed": "openconfig-if-ethernet:SPEED_100GB",
          "num-channels": 1,
          "openconfig-port-breakout-ext:members": ["Ethernet52"],
          "openconfig-port-breakout-ext:status": "Completed"
        }
      }
    }
  }]
}
```

---

### Set Port Breakout Mode (e.g. 1x100G → 4x25G)

> component name uses port number format `1/53` (= Ethernet52)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /openconfig-platform:components/component[name=1/53]/port/\
openconfig-platform-port:breakout-mode/config:@./breakout.json
```

breakout.json:
```json
{
  "openconfig-platform-port:config": {
    "channel-speed": "openconfig-if-ethernet:SPEED_25GB",
    "num-channels": 4
  }
}
```

Response: `op: REPLACE`

After breakout, port splits into multiple members:
```json
{
  "state": {
    "channel-speed": "openconfig-if-ethernet:SPEED_25GB",
    "num-channels": 4,
    "openconfig-port-breakout-ext:members": [
      "Ethernet52", "Ethernet53", "Ethernet54", "Ethernet55"
    ],
    "openconfig-port-breakout-ext:status": "Completed"
  }
}
```

---

### Delete Port Breakout (restore default)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /openconfig-platform:components/component[name=1/53]/port/\
openconfig-platform-port:breakout-mode/config
```

Response: `op: DELETE` — restores to default breakout mode (1x100G).

---

## SONiC YANG (`xpath_target: OC-YANG`)

---

### Get Port (all fields)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]
```

Response:
```json
{
  "sonic-port:PORT_LIST": [{
    "admin_status": "up",
    "alias": "Eth1(Port1)",
    "autoneg": "on",
    "description": "",
    "ifname": "Ethernet0",
    "index": 1,
    "lanes": "2",
    "mtu": 9100,
    "parent_port": "Ethernet0",
    "speed": "1000",
    "subport": 0
  }]
}
```

---

### Update Port Leaf Fields

```bash
# MTU
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update /sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]/mtu:@./mtu.json
# mtu.json: {"sonic-port:mtu": 9100}

# Description
gnmi_set ... -update .../PORT_LIST[ifname=Ethernet0]/description:@./desc.json
# desc.json: {"sonic-port:description": "uplink"}

# FEC
gnmi_set ... -update .../PORT_LIST[ifname=Ethernet0]/fec:@./fec.json
# fec.json: {"sonic-port:fec": "none"}

# TPID
gnmi_set ... -update .../PORT_LIST[ifname=Ethernet0]/tpid:@./tpid.json
# tpid.json: {"sonic-port:tpid": "0x8100"}
```

Deletable fields: `description`, `fec`, `tpid`, `pms_maximum`, `pms_violation`

---

### Create PortChannel (SONiC)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST:@./pch.json
```

pch.json:
```json
{
  "sonic-portchannel:PORTCHANNEL_LIST": [{
    "name": "PortChannel100",
    "admin_status": "up",
    "mtu": 9100
  }]
}
```

> Note: `mtu` must be numeric (not string)

---

### Add PortChannel Member

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-portchannel:sonic-portchannel/\
PORTCHANNEL_MEMBER/PORTCHANNEL_MEMBER_LIST:@./m.json
```

m.json:
```json
{"sonic-portchannel:PORTCHANNEL_MEMBER_LIST": [{"name": "PortChannel100", "ifname": "Ethernet4"}]}
```

---

### Delete PortChannel Member

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-portchannel:sonic-portchannel/\
PORTCHANNEL_MEMBER/PORTCHANNEL_MEMBER_LIST[name=PortChannel100][ifname=Ethernet4]
```

---

### Delete PortChannel

> Remove all members first.

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-portchannel:sonic-portchannel/PORTCHANNEL/PORTCHANNEL_LIST[name=PortChannel100]
```

---

### Get LAG State (read-only)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-portchannel:sonic-portchannel/LAG_TABLE
```

Response:
```json
{
  "sonic-portchannel:LAG_TABLE": {
    "LAG_TABLE_LIST": [{"admin_status": "up", "lagname": "PortChannel100", "mtu": 9100, "oper_status": "down"}]
  }
}
```

---

### Get Port Counters (SONiC)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-counters:sonic-counters/COUNTERS/COUNTERS_LIST[name=Ethernet48]
```

Response (partial — contains all SAI_PORT_STAT_* fields):
```json
{
  "sonic-counters:COUNTERS_LIST": [{
    "name": "Ethernet48",
    "SAI_PORT_STAT_IF_IN_OCTETS": "4883",
    "SAI_PORT_STAT_IF_IN_MULTICAST_PKTS": "21",
    "SAI_PORT_STAT_IF_IN_NON_UCAST_PKTS": "21",
    "SAI_PORT_STAT_IF_IN_DISCARDS": "14",
    "SAI_PORT_STAT_IF_OUT_OCTETS": "5434883",
    "SAI_PORT_STAT_IF_OUT_BROADCAST_PKTS": "5000",
    "SAI_PORT_STAT_IF_OUT_MULTICAST_PKTS": "21",
    "SAI_PORT_STAT_IF_OUT_NON_UCAST_PKTS": "5021",
    "SAI_PORT_STAT_ETHER_OUT_PKTS_1024_TO_1518_OCTETS": "3000",
    "SAI_PORT_STAT_ETHER_OUT_PKTS_512_TO_1023_OCTETS": "2000",
    "SAI_PORT_STAT_ETHER_STATS_TX_NO_ERRORS": "5021",
    "..."
  }]
}
```

> Note: For Queue counters use `name=Ethernet48:Q:0`,
> for PG counters use `name=Ethernet48:PG:0`
> (replace `:` with `%3A` in URL encoding if needed).

---

### Create Loopback Interface

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-loopback-interface:sonic-loopback-interface/\
LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_LIST:@./lo.json
```

lo.json:
```json
{"sonic-loopback-interface:LOOPBACK_INTERFACE_LIST": [{"loIfName": "Loopback10"}]}
```

---

### Add Loopback IP Address

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-loopback-interface:sonic-loopback-interface/\
LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_IPADDR_LIST:@./ip.json
```

ip.json:
```json
{"sonic-loopback-interface:LOOPBACK_INTERFACE_IPADDR_LIST": [{"loIfName": "Loopback10", "ip_prefix": "10.10.10.1/32"}]}
```

---

### Delete Loopback IP / Loopback

```bash
# Delete IP first
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-loopback-interface:sonic-loopback-interface/\
LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_IPADDR_LIST[loIfName=Loopback10][ip_prefix=10.10.10.1/32]

# Then delete loopback
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-loopback-interface:sonic-loopback-interface/\
LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_LIST[loIfName=Loopback10]
```
