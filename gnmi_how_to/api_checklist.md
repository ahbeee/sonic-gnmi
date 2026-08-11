# gNMI API Checklist

DUT: 192.168.8.234  
SONiC: Edgecore-SONiC_202311.6_ec202311_807  
Platform: AS4630-54NPE

## Connection Info

| Mode | Flag | Auth |
|------|------|------|
| noTLS (this DUT) | `-notls` | none |
| Insecure (TLS skip verify) | `-insecure` | `-username admin -password <pw>` |

```bash
docker exec gnmi gnmi_get -notls \
  -target_addr localhost:8080 \
  -xpath_target OC-YANG \
  -xpath <PATH>
```

## xpath_target Reference

| Target | DB No. | Usage | Stream Subscribe |
|--------|--------|-------|-----------------|
| `OC-YANG` | - | All OpenConfig and SONiC YANG paths | once/poll only |
| `APPL_DB` | 0 | Application running data (PORT_TABLE, ROUTE_TABLE...) | ✅ stream |
| `ASIC_DB` | 1 | ASIC configuration and state | ✅ stream |
| `COUNTERS_DB` | 2 | Port/Queue/PG counters | ✅ stream |
| `LOGLEVEL_DB` | 3 | Log level control | ✅ stream |
| `CONFIG_DB` | 4 | Switch configuration (PORT, VLAN...) | ✅ stream |
| `FLEX_COUNTER_DB` | 5 | PFC watchdog counters | ✅ stream |
| `STATE_DB` | 6 | Operational state (PSU/FAN/TEMP) | ✅ stream |
| `OTHERS` | - | Non-DB system paths (/platform/cpu, /proc/*) | sample only |

## Data Type Notes

| Field | Correct Type | Wrong |
|-------|-------------|-------|
| `mtu` (sonic-port/portchannel) | numeric `9100` | string |
| `distance` (static route) | string `"0"` | numeric |
| `kbps` (storm-control) | string `"1000"` | numeric |
| `pms_enable` | `"yes"` / `"no"` | "true"/"false" |
| `flow_control` | `"tx"/"rx"/"both"/"none"` | "on"/"off" |
| `priority` (tacacs) | numeric `1` | string |
| `tcp_port` (tacacs) | numeric `49` | string |
| `collector_port` (sflow) | numeric `6343` | string |
| `ecmp_hash` (hash) | array `["SRC_IP","DST_IP"]` | comma string |
| `nat_timeout` (nat) | numeric `600` | string |
| `local_asn` (bgp) | numeric `65000` | string |
| `sequence_num` (pbr) | string `"10"` | numeric |
| `size` (buffer-pool) | string `"1024"` | numeric |
| `interval` (watermark) | numeric `120` | string |
| `detection_time` (pfcwd) | numeric `200` | string |
| `max_sessions` (ssh) | numeric `10` | string |
| `expiration` (passwh) | numeric `90` | string |
| `inactivity_timeout` (serial) | numeric `300` | string |
| `enabled` (kdump) | boolean `true`/`false` | string |

## Key Field Reference

| Module | List | Key |
|--------|------|-----|
| sonic-aaa | AAA_LIST | `type` |
| sonic-acl | ACL_TABLE_LIST | `aclname` |
| sonic-acl | ACL_RULE_LIST | `aclname` + `rulename` |
| sonic-bgp-global | BGP_GLOBALS_LIST | `vrf_name` |
| sonic-bgp-neighbor | BGP_NEIGHBOR_LIST | `vrf_name` + `neighbor` |
| sonic-bgp-peergroup | BGP_PEER_GROUP_LIST | `vrf_name` + `peer_group_name` |
| sonic-buffer-pg | BUFFER_PG_LIST | `port` + `pg_num` |
| sonic-buffer-pool | BUFFER_POOL_LIST | `name` |
| sonic-buffer-profile | BUFFER_PROFILE_LIST | `name` |
| sonic-buffer-queue | BUFFER_QUEUE_LIST | `port` + `qindex` |
| sonic-counters | COUNTERS_LIST | `name` |
| sonic-dai | DAI_VLAN_LIST | `vlan_name` |
| sonic-dai | DAI_INTERFACE_LIST | `port_name` |
| sonic-device-metadata | DEVICE_METADATA_LIST | `name` |
| sonic-dhcp-relay | DHCP_RELAY_LIST | `name` |
| sonic-dhcp-snooping | DHCPSNP_LIST | `param` (must be `"GLOBAL"`) |
| sonic-dhcp-snooping | DHCPSNP_VLAN_LIST | `vlan_name` |
| sonic-dhcp-snooping | DHCPSNP_TRUST_LIST | `port_name` |
| sonic-dot1p-tc-map | DOT1P_TO_TC_MAP_LIST | `name` |
| sonic-drop-counter | DEBUG_COUNTER_LIST | `name` |
| sonic-dscp-tc-map | DSCP_TO_TC_MAP_LIST | `name` |
| sonic-fdb | FDB_LIST | `vlan` + `macaddr` |
| sonic-flex-counter | FLEX_COUNTER_TABLE_LIST | `name` |
| sonic-hash | SWITCH_HASH_LIST | `name` (must be `"GLOBAL"`) |
| sonic-igmp-snooping | IGMP_SNP_LIST | `name` |
| sonic-image-management | IMAGE_GLOBAL_LIST | `img_key` (must be `"state"`) |
| sonic-interface | INTERFACE_LIST | `portname` |
| sonic-interface | INTERFACE_IPADDR_LIST | `portname` + `ip_prefix` |
| sonic-ipsg | IPSG_GLOBAL_LIST | `param` |
| sonic-ipsg | IPSG_PORT_LIST | `ifname` |
| sonic-kdump | KDUMP_LIST | `name` |
| sonic-ldap | LDAP_SERVER_LIST | `ipaddress` |
| sonic-ldap | LDAP_LIST | `name` (must be `"global"`) |
| sonic-lldp | LLDP_PORT_LIST | `ifname` |
| sonic-local-routing | STATIC_ROUTE_LIST | `vrf` + `prefix` |
| sonic-loopback-interface | LOOPBACK_INTERFACE_LIST | `loIfName` |
| sonic-loopback-interface | LOOPBACK_INTERFACE_IPADDR_LIST | `loIfName` + `ip_prefix` |
| sonic-mclag | MCLAG_DOMAIN_LIST | `domain_id` |
| sonic-mclag | MCLAG_INTERFACE_LIST | `domain_id` + `if_name` |
| sonic-mgmt-interface | MGMT_INTERFACE_LIST | `portname` |
| sonic-mgmt-interface | MGMT_INTERFACE_IPADDR_LIST | `portname` + `ip_prefix` |
| sonic-mirror | MIRROR_SESSION_LIST | `name` |
| sonic-nac | DOT1X_LIST | `param` (must be `"GLOBAL"`) |
| sonic-nac | DOT1X_PORT_LIST | `ifname` |
| sonic-nac | DOT1X_MAB_PORT_LIST | `ifname` |
| sonic-nat | NAT_GLOBAL_LIST | `name` |
| sonic-nat | STATIC_NAT_LIST | `global_ip` |
| sonic-obj-track | OBJ_TRACK_LIST | `session_name` |
| sonic-pbr | PBR_MAP_TABLE_LIST | `mapname` + `sequence_num` |
| sonic-pbr | PBR_INTERFACE_TABLE_LIST | `ifname` |
| sonic-pfc-priority-queue-map | MAP_PFC_PRIORITY_TO_QUEUE_LIST | `name` |
| sonic-pfcwd | PFC_WD_LIST | `ifname` (or `"GLOBAL"`) |
| sonic-poe | POE_LIST | `portname` |
| sonic-policer | POLICER_LIST | `policername` |
| sonic-port | PORT_LIST | `ifname` |
| sonic-port-qos-map | PORT_QOS_MAP_LIST | `ifname` |
| sonic-portchannel | PORTCHANNEL_LIST | `name` |
| sonic-portchannel | PORTCHANNEL_MEMBER_LIST | `name` + `ifname` |
| sonic-portchannel | LAG_TABLE_LIST | `lagname` |
| sonic-portchannel-interface | PORTCHANNEL_INTERFACE_LIST | `pch_name` |
| sonic-portchannel-interface | PORTCHANNEL_INTERFACE_IPADDR_LIST | `pch_name` + `ip_prefix` |
| sonic-queue | QUEUE_LIST | `ifname` + `qindex` |
| sonic-radius | RADIUS_SERVER_LIST | `ipaddress` |
| sonic-radius | RADIUS_LIST | `name` (must be `"global"`) |
| sonic-scheduler | SCHEDULER_LIST | `name` |
| sonic-sflow | SFLOW_COLLECTOR_LIST | `name` |
| sonic-sflow | SFLOW_SESSION_LIST | `port` |
| sonic-static-anycast-gateway | SAG_LIST | `name` (must be `"GLOBAL"`) |
| sonic-storm-control | PORT_STORM_CONTROL_LIST | `ifname` + `storm_type` |
| sonic-stp | STP_LIST | `name` |
| sonic-system-logging | SYSLOG_SERVER_LIST | `host` |
| sonic-system-ntp | NTP_SERVER_LIST | `address` |
| sonic-system-ntp | NTP_LIST | `name` |
| sonic-tacacs | TACPLUS_SERVER_LIST | `ipaddress` |
| sonic-tacacs | TACPLUS_LIST | `name` (must be `"global"`) |
| sonic-tc-dot1p-map | TC_TO_DOT1P_MAP_LIST | `name` |
| sonic-tc-dscp-map | TC_TO_DSCP_MAP_LIST | `name` |
| sonic-tc-priority-group-map | TC_TO_PRIORITY_GROUP_MAP_LIST | `name` |
| sonic-tc-queue-map | TC_TO_QUEUE_MAP_LIST | `name` |
| sonic-vlan | VLAN_LIST | `name` |
| sonic-vlan | VLAN_MEMBER_LIST | `name` + `ifname` |
| sonic-vlan-interface | VLAN_INTERFACE_LIST | `vlanName` |
| sonic-vlan-interface | VLAN_INTERFACE_IPADDR_LIST | `vlanName` + `ip_prefix` |
| sonic-vlan-sub-interface | VLAN_SUB_INTERFACE_LIST | `name` |
| sonic-vrf | VRF_LIST | `vrf_name` |
| sonic-vrrp | VRRP_GROUP_LIST | `vrrp_id` + `parent_interface` |
| sonic-vxlan | VXLAN_TUNNEL_LIST | `name` |
| sonic-vxlan | VXLAN_TUNNEL_MAP_LIST | `name` + `mapname` |
| sonic-watermark | WATERMARK_TABLE_LIST | `table_name` (must be `"TELEMETRY_INTERVAL"`) |
| sonic-wred-profile | WRED_PROFILE_LIST | `name` |
| sonic-xstp | XSTP_GLOBAL_LIST | `param` |
| sonic-xstp | XSTP_MST_LIST | `mstid` |
| sonic-xstp | XSTP_INTERFACE_LIST | `ifname` |

> ⚠️ Key names above are from DUT translib YANG (`/usr/models/yang/`).
> They may differ from CVL YANG (`yang-models/`) due to build-time renaming.
> See `YANG_INCONSISTENCY_NOTES.md` for details.

## JSON Payload Prefix Rule

- OC leaf: `{"openconfig-interfaces:mtu": 9100}`
- SONiC leaf: `{"sonic-port:mtu": 9100}`
- SONiC list: `{"sonic-vlan:VLAN_LIST": [...]}`

---

## 1. Interface

### OpenConfig YANG (`xpath_target: OC-YANG`)

YANG: [openconfig-interfaces.yang](https://github.com/openconfig/public/blob/master/release/models/interfaces/openconfig-interfaces.yang)

#### Ethernet Port (speed / aggregate-id)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 1 | Ethernet config (speed + aggregate-id)<br>`/openconfig-interfaces:interfaces/`<br>`interface[name=Ethernet0]/`<br>`openconfig-if-ethernet:ethernet/config` | ✓ | ✓ | - | ✅ |
| 2 | Port speed (leaf)<br>`.../ethernet/config/port-speed` | ✓ | ✓ | - | ✅ |
| 3 | Aggregate-id (leaf)<br>`.../ethernet/config/`<br>`openconfig-if-aggregate:aggregate-id` | ✓ | ✓ | ✓ | ✅ value=ID number |
| 4 | Standalone link-training<br>`.../ethernet/config/standalone-link-training` | ✗ | - | - | ❌ Not in DB |

#### Ethernet Interface

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 5 | Interface (all)<br>`/openconfig-interfaces:interfaces/`<br>`interface[name=Ethernet0]` | ✓ | - | - | ✅ |
| 6 | Interface state<br>`.../interface[name=Ethernet0]/state` | ✓ | - | - | ✅ |
| 7 | State leaf (mtu/admin-status/oper-status/...)<br>`.../interface[name=Ethernet0]/state/mtu` | ✓ | - | - | ✅ |
| 8 | Ethernet state/port-speed (leaf)<br>`.../openconfig-if-ethernet:ethernet/state/port-speed` | ✗ | - | - | ⚠️ Use #12 |
| 9 | Interface config<br>`.../interface[name=Ethernet0]/config` | ✓ | ✓ | - | ✅ |
| 10 | Config leaf (mtu/description/enabled)<br>`.../interface[name=Ethernet0]/config/mtu` | ✓ | ✓ | - | ✅ |
| 11 | Config TPID (OC path)<br>`.../config/openconfig-vlan:tpid` | ✗ | - | - | ❌ Use #33 |
| 12 | Ethernet (config+state combined)<br>`.../openconfig-if-ethernet:ethernet` | ✓ | - | - | ✅ |
| 13 | Ethernet state (sub-path only)<br>`.../openconfig-if-ethernet:ethernet/state` | ✗ | - | - | ⚠️ Use #12 |

#### Ethernet Port Counter

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 14 | Counters (all)<br>`.../interface[name=Ethernet0]/state/counters` | ✓ | - | - | ✅ |
| 15 | Counter leaf (e.g. in-octets)<br>`.../state/counters/in-octets` | ✓ | - | - | ✅ |

#### Transceiver

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 16 | Transceiver config<br>`.../ethernet/config/transceiver` | ✓ | - | - | ✅ (empty) |
| 17 | Transceiver state<br>`.../ethernet/state/transceiver` | ✗ | - | - | ❌ Requires SFP |

#### PortChannel Interface

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 18 | PortChannel (create/get/delete)<br>`/openconfig-interfaces:interfaces/`<br>`interface[name=PortChannel1]` | ✓ | ✓ | ✓ | ✅ |
| 19 | PortChannel state<br>`.../interface[name=PortChannel1]/state` | ✓ | - | - | ✅ |
| 20 | PortChannel config<br>`.../interface[name=PortChannel1]/config` | ✓ | ✓ | - | ✅ |
| 21 | PortChannel aggregation<br>`.../interface[name=PortChannel1]/`<br>`openconfig-if-aggregate:aggregation` | ✓ | - | - | ✅ |
| 22 | PortChannel counters<br>`.../interface[name=PortChannel1]/state/counters` | ✓ | - | - | ✅ (empty) |

#### Port Breakout Mode

YANG: [openconfig-platform-port.yang](https://github.com/openconfig/public/blob/master/release/models/platform/openconfig-platform-port.yang)

> component name uses port number `1/1`, not `Ethernet0`

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 23 | Get breakout mode<br>`/openconfig-platform:components/`<br>`component[name=1/1]` | ✓ | - | - | ✅ |
| 24 | Set/Delete breakout<br>`.../component[name=1/1]/port/`<br>`openconfig-platform-port:breakout-mode/config` | - | ✓ | ✓ | ✅ Same-value rejected |


### SONiC YANG (`xpath_target: OC-YANG`)

#### SONiC Port

YANG: [sonic-port.yang](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-port.yang)

Base: `/sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]`

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 25 | Port (all fields)<br>`/sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]` | ✓ | ✓ | - | ✅ |
| 26 | `.../speed` | ✓ | ✓ | - | ✅ |
| 27 | `.../alias` | ✓ | ✓ | - | ✅ |
| 28 | `.../description` | ✓ | ✓ | ✓ | ✅ |
| 29 | `.../mtu` | ✓ | ✓ | - | ✅ |
| 30 | `.../admin_status` | ✓ | ✓ | - | ✅ |
| 31 | `.../autoneg` | ✓ | ✓ | - | ✅ |
| 32 | `.../fec` | ✓ | ✓ | ✓ | ✅ |
| 33 | `.../tpid` | ✓ | ✓ | ✓ | ✅ |
| 34 | `.../link_training` | - | ✗ | - | ❌ RJ45 not supported |
| 35 | `.../flow_control` | - | ✗ | - | ❌ Platform not supported |
| 36 | `.../pms_enable` | - | ✓* | - | ⚠️ Requires VLAN member |
| 37 | `.../pms_maximum` | ✓ | ✓ | ✓ | ✅ |
| 38 | `.../pms_violation` | ✓ | ✓ | ✓ | ✅ |

#### SONiC PortChannel

YANG: [sonic-portchannel.yang](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-portchannel.yang)

Base: `/sonic-portchannel:sonic-portchannel`

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 39 | `/PORTCHANNEL` (all) | ✓ | ✓ | ✓ | ✅ |
| 40 | `/PORTCHANNEL/PORTCHANNEL_LIST[name=PortChannel100]` | ✓ | ✓ | ✓ | ✅ |
| 41 | `.../admin_status` | ✓ | ✓ | - | ✅ |
| 42 | `.../static` | ✓ | - | - | ⚠️ Empty if not set |
| 43 | `.../lacp_key` | ✓ | - | - | ⚠️ Empty if not set |
| 44 | `.../mtu` | ✓ | ✓ | - | ✅ |
| 45 | `.../min_links` | ✓ | - | - | ⚠️ Empty if not set |
| 46 | `.../fallback` | ✓ | - | - | ⚠️ Empty if not set |
| 47 | `.../description` | ✓ | ✓ | ✓ | ✅ |
| 48 | `.../pms_maximum` | ✓ | ✓ | ✓ | ✅ |
| 49 | `/PORTCHANNEL_MEMBER/`<br>`PORTCHANNEL_MEMBER_LIST` | ✓ | ✓ | ✓ | ✅ |
| 50 | `.../PORTCHANNEL_MEMBER_LIST`<br>`[name=PortChannel100][ifname=Ethernet4]` | ✓ | - | ✓ | ✅ |
| 51 | `/LAG_TABLE` (state) | ✓ | - | - | ✅ |
| 52 | `/LAG_MEMBER_TABLE` (state) | ✓ | - | - | ✅ |

#### SONiC Counters

YANG: `sonic-counters.yang`

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 53 | Port/Queue/PG counters<br>`/sonic-counters:sonic-counters/`<br>`COUNTERS/COUNTERS_LIST[name=Ethernet0]` | ✓ | - | - | ✅ |

#### SONiC POE

YANG: `sonic-poe.yang`

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 54 | POE information<br>`/sonic-poe:sonic-poe` | ✓ | - | - | ✅ (empty) |

#### SONiC Loopback Interface

YANG: [sonic-loopback-interface.yang](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-loopback-interface.yang)

Base: `/sonic-loopback-interface:sonic-loopback-interface`

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 55 | Loopback (all) | ✓ | ✓ | ✓ | ✅ |
| 56 | `.../LOOPBACK_INTERFACE/`<br>`LOOPBACK_INTERFACE_LIST[loIfName=Loopback10]` | ✓ | ✓ | ✓ | ✅ |
| 57 | `.../nat_zone` | ✓ | ✓ | ✓ | ✅ (IP first) |
| 58 | `.../description` | ✓ | ✓ | ✓ | ✅ |
| 59 | `.../LOOPBACK_INTERFACE_IPADDR_LIST`<br>`[loIfName=Loopback10][ip_prefix=10.10.10.1/32]` | ✓ | ✓ | ✓ | ✅ |


---

## 2. Layer 2

### OpenConfig YANG (`xpath_target: OC-YANG`)

YANG: [openconfig-vlan.yang](https://github.com/openconfig/public/blob/master/release/models/vlan/openconfig-vlan.yang) |
[openconfig-lldp.yang](https://github.com/openconfig/public/blob/master/release/models/lldp/openconfig-lldp.yang)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 60 | VLAN interface<br>`/openconfig-interfaces:interfaces/`<br>`interface[name=Vlan100]` | ✓ | ✓ | ✓ | ✅ |
| 61 | VLAN member (Ethernet trunk)<br>`.../interface[name=Ethernet4]/`<br>`openconfig-if-ethernet:ethernet/`<br>`openconfig-vlan:switched-vlan/config/trunk-vlans` | ✓ | ✓ | ✓ | ✅ |
| 62 | VLAN member (PortChannel trunk)<br>`.../interface[name=PortChannel1]/`<br>`openconfig-if-aggregate:aggregation/`<br>`openconfig-vlan:switched-vlan/config/trunk-vlans` | ✓ | ✓ | ✓ | ✅ |
| 63 | Network Instance for VLAN<br>`/openconfig-network-instance:network-instances/`<br>`network-instance[name=Vlan100]/vlans` | ✓ | ✓ | ✓ | ✅ |
| 64 | LLDP<br>`/openconfig-lldp:lldp` | ✓ | ✓ | - | ✅ (empty) |
| 65 | LLDP interfaces<br>`/openconfig-lldp:lldp/interfaces` | ✓ | - | - | ✅ (empty) |
| 66 | MCLAG<br>`/openconfig-mclag:mclag` | ✓ | ✓ | ✓ | ✅ (empty) |

### SONiC YANG (`xpath_target: OC-YANG`)

YANG: [`sonic-vlan.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-vlan.yang) | [`sonic-lldp.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-lldp.yang) | `sonic-xstp.yang` | [`sonic-fdb.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-fdb.yang) |
`sonic-igmp-snooping.yang` | [`sonic-stp.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-stp.yang) | [`sonic-storm-control.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-storm-control.yang) | [`sonic-switch.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-switch.yang) | [`sonic-mclag.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-mclag.yang)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 67 | VLAN (all)<br>`/sonic-vlan:sonic-vlan/VLAN` | ✓ | ✓ | - | ✅ |
| 68 | VLAN entry<br>`.../VLAN_LIST[name=Vlan100]` | ✓ | - | ✓ | ✅ |
| 69 | VLAN member (all)<br>`.../VLAN_MEMBER/VLAN_MEMBER_LIST` | ✓ | ✓ | ✓ | ✅ |
| 70 | VLAN member entry<br>`.../VLAN_MEMBER_LIST[name=Vlan100][ifname=Ethernet4]` | ✓ | - | ✓ | ✅ |
| 71 | LLDP state<br>`/sonic-lldp:sonic-lldp` | ✓ | - | - | ✅ (empty) |
| 72 | XSTP<br>`/sonic-xstp:sonic-xstp` | ✓ | ✓ | ✓ | ✅ |
| 73 | FDB<br>`/sonic-fdb:sonic-fdb` | ✓ | - | - | ✅ (empty) |
| 74 | IGMP Snooping<br>`/sonic-igmp-snooping:sonic-igmp-snooping` | ✓ | ✓ | ✓ | ✅ (empty) |
| 75 | STP<br>`/sonic-stp:sonic-stp` | ✓ | ✓ | ✓ | ✅ (empty) |
| 76 | Storm Control<br>`/sonic-storm-control:sonic-storm-control` | ✓ | ✓ | ✓ | ✅ |
| 77 | Switch (fdb_aging_time)<br>`/sonic-switch:sonic-switch` | ✓ | ✓ | ✓ | ✅ |
| 78 | MCLAG<br>`/sonic-mclag:sonic-mclag` | ✓ | ✓ | ✓ | ✅ (empty) |

---

## 3. Layer 3

### OpenConfig YANG (`xpath_target: OC-YANG`)

YANG: [openconfig-network-instance.yang](https://github.com/openconfig/public/blob/master/release/models/network-instance/openconfig-network-instance.yang) |
[openconfig-if-ip.yang](https://github.com/openconfig/public/blob/master/release/models/interfaces/openconfig-if-ip.yang) |
[openconfig-local-routing.yang](https://github.com/openconfig/public/blob/master/release/models/local-routing/openconfig-local-routing.yang)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 79 | Network Instance VRF<br>`/openconfig-network-instance:network-instances/`<br>`network-instance[name=default]` | ✓ | ✓ | ✓ | ✅ |
| 80 | VXLAN VNI instance<br>`.../network-instance[name=Vlan200]/`<br>`vlans/vlan[vlan-id=200]` | ✓ | ✓ | ✓ | ✅ |
| 81 | Neighbor Suppress<br>`.../vlan[vlan-id=200]/config/`<br>`openconfig-vxlan:neigh-suppress` | ✓ | ✓ | - | ✅ |
| 82 | IPv4 on interface<br>`/openconfig-interfaces:interfaces/`<br>`interface[name=Ethernet0]/subinterfaces/`<br>`subinterface[index=0]/openconfig-if-ip:ipv4/addresses` | ✓ | ✓ | ✓ | ✅ |
| 83 | IPv6 on interface<br>`.../subinterface[index=0]/`<br>`openconfig-if-ip:ipv6/addresses` | ✓ | ✓ | ✓ | ✅ |
| 84 | DHCP Relay Agent<br>`/openconfig-relay-agent:relay-agent` | ✓ | ✓ | ✓ | ✅ (empty) |
| 85 | Static routes (OC)<br>`/openconfig-local-routing:local-routes/static-routes` | ✗ | - | - | ❌ Module not found |

### SONiC YANG (`xpath_target: OC-YANG`)

YANG: [`sonic-interface.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-interface.yang) | [`sonic-portchannel.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-portchannel.yang) | [`sonic-vlan.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-vlan.yang) |
`sonic-local-routing.yang` | [`sonic-vrf.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-vrf.yang) | [`sonic-vxlan.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-vxlan.yang) | [`sonic-static-anycast-gateway.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-static-anycast-gateway.yang) |
`sonic-arp.yang` | `sonic-vrrp.yang` | `sonic-dhcp-relay.yang` | [`sonic-bgp-global.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-bgp-global.yang) |
[`sonic-bgp-neighbor.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-bgp-neighbor.yang) | [`sonic-bgp-peergroup.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-bgp-peergroup.yang) | [`sonic-vlan-sub-interface.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-vlan-sub-interface.yang) |
[`sonic-obj-track.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-obj-track.yang) | [`sonic-nat.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-nat.yang) | `sonic-pbr.yang`

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 86 | Interface IP<br>`/sonic-interface:sonic-interface/INTERFACE/`<br>`INTERFACE_IPADDR_LIST[portname=Ethernet8]`<br>`[ip_prefix=172.30.0.1/30]` | ✓ | ✓ | ✓ | ✅ |
| 87 | PortChannel IP<br>`/sonic-portchannel-interface:sonic-portchannel-interface` | ✓ | ✓ | ✓ | ✅ |
| 88 | VLAN Interface IP<br>`/sonic-vlan-interface:sonic-vlan-interface/`<br>`VLAN_INTERFACE/VLAN_INTERFACE_IPADDR_LIST`<br>`[vlanName=Vlan200][ip_prefix=10.200.0.1/24]` | ✓ | ✓ | ✓ | ✅ |
| 89 | Static Route<br>`/sonic-local-routing:sonic-local-routing/`<br>`STATIC_ROUTE/STATIC_ROUTE_LIST`<br>`[vrf=default][prefix=172.16.0.0/16]` | ✓ | ✓ | ✓ | ✅ |
| 90 | VRF<br>`/sonic-vrf:sonic-vrf/VRF/VRF_LIST[vrf_name=Vrf1]` | ✓ | ✓ | ✓ | ✅ |
| 91 | VXLAN<br>`/sonic-vxlan:sonic-vxlan` | ✓ | ✓ | ✓ | ✅ |
| 92 | SAG<br>`/sonic-static-anycast-gateway:sonic-static-anycast-gateway` | ✓ | ✓ | ✓ | ✅ |
| 93 | ARP<br>`/sonic-arp:sonic-arp` | ✓ | - | - | ✅ |
| 94 | VRRP<br>`/sonic-vrrp:sonic-vrrp` | ✓ | ✓ | ✓ | ⚠️ Requires VLAN+IP |
| 95 | DHCP Relay<br>`/sonic-dhcp-relay:sonic-dhcp-relay` | ✓ | ✓ | ✓ | ✅ |
| 96 | BGP Global<br>`/sonic-bgp-global:sonic-bgp-global` | ✓ | ✓ | ✓ | ✅ |
| 97 | BGP Neighbor<br>`/sonic-bgp-neighbor:sonic-bgp-neighbor` | ✓ | ✓ | ✓ | ✅ |
| 98 | BGP Peer-group<br>`/sonic-bgp-peergroup:sonic-bgp-peergroup` | ✓ | ✓ | ✓ | ✅ |
| 99 | Subport<br>`/sonic-vlan-sub-interface:sonic-vlan-sub-interface` | ✓ | ✓ | ✓ | ✅ |
| 100 | Object Track<br>`/sonic-obj-track:sonic-obj-track` | ✓ | ✓ | ✓ | ✅ |
| 101 | NAT<br>`/sonic-nat:sonic-nat` | ✓ | ✓ | ✓ | ✅ |
| 102 | PBR<br>`/sonic-pbr:sonic-pbr` | ✓ | ✓ | ✓ | ✅ |

---

## 4. Security

### OpenConfig YANG (`xpath_target: OC-YANG`)

YANG: [openconfig-acl.yang](https://github.com/openconfig/public/blob/master/release/models/acl/openconfig-acl.yang)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 103 | ACL<br>`/openconfig-acl:acl` | ✓ | ✓ | ✓ | ✅ |

### SONiC YANG (`xpath_target: OC-YANG`)

YANG: `sonic-acl.yang` | [`sonic-wred-profile.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-wred-profile.yang) | [`sonic-buffer-pool.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-buffer-pool.yang) |
[`sonic-buffer-profile.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-buffer-profile.yang) | [`sonic-buffer-pg.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-buffer-pg.yang) | [`sonic-buffer-queue.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-buffer-queue.yang) |
[`sonic-dscp-tc-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-dscp-tc-map.yang) | [`sonic-dot1p-tc-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-dot1p-tc-map.yang) | [`sonic-tc-queue-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-tc-queue-map.yang) |
[`sonic-tc-dscp-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-tc-dscp-map.yang) | [`sonic-tc-dot1p-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-tc-dot1p-map.yang) | [`sonic-tc-priority-group-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-tc-priority-group-map.yang) |
[`sonic-pfc-priority-queue-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-pfc-priority-queue-map.yang) | [`sonic-port-qos-map.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-port-qos-map.yang) | [`sonic-pfcwd.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-pfcwd.yang) |
[`sonic-queue.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-queue.yang) | `sonic-aaa.yang` | `sonic-tacacs.yang` | `sonic-radius.yang` |
`sonic-ldap.yang` | `sonic-policer.yang` | `sonic-watermark.yang` | `sonic-nac.yang` |
`sonic-ipsg.yang` | [`sonic-dhcp-snooping.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-dhcp-snooping.yang) | `sonic-dai.yang` | [`sonic-hash.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-hash.yang) |
[`sonic-scheduler.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-scheduler.yang) | [`sonic-passwh.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-passwh.yang) | [`sonic-ssh-server.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-ssh-server.yang)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 104 | ACL<br>`/sonic-acl:sonic-acl` | ✓ | ✓ | ✓ | ✅ |
| 105 | WRED<br>`/sonic-wred-profile:sonic-wred-profile` | ✓ | ✓ | ✓ | ✅ |
| 106 | Buffer Pool<br>`/sonic-buffer-pool:sonic-buffer-pool` | ✓ | ✓ | ✓ | ✅ |
| 107 | Buffer Profile<br>`/sonic-buffer-profile:sonic-buffer-profile` | ✓ | ✓ | ✓ | ✅ |
| 108 | Buffer PG<br>`/sonic-buffer-pg:sonic-buffer-pg` | ✓ | ✓ | ✓ | ✅ |
| 109 | Buffer Queue<br>`/sonic-buffer-queue:sonic-buffer-queue` | ✓ | ✓ | ✓ | ✅ |
| 110 | DSCP-TC Map<br>`/sonic-dscp-tc-map:sonic-dscp-tc-map` | ✓ | ✓ | ✓ | ✅ |
| 111 | DOT1P-TC Map<br>`/sonic-dot1p-tc-map:sonic-dot1p-tc-map` | ✓ | ✓ | ✓ | ✅ |
| 112 | TC-Queue Map<br>`/sonic-tc-queue-map:sonic-tc-queue-map` | ✓ | ✓ | ✓ | ✅ |
| 113 | TC-DSCP Map<br>`/sonic-tc-dscp-map:sonic-tc-dscp-map` | ✓ | ✓ | ✓ | ✅ |
| 114 | TC-DOT1P Map<br>`/sonic-tc-dot1p-map:sonic-tc-dot1p-map` | ✓ | ✓ | ✓ | ✅ |
| 115 | TC-PG Map<br>`/sonic-tc-priority-group-map:sonic-tc-priority-group-map` | ✓ | ✓ | ✓ | ✅ |
| 116 | PFC-PQ Map<br>`/sonic-pfc-priority-queue-map:sonic-pfc-priority-queue-map` | ✓ | ✓ | ✓ | ✅ |
| 117 | Port QoS Map<br>`/sonic-port-qos-map:sonic-port-qos-map` | ✓ | ✓ | ✓ | ✅ |
| 118 | PFC Watchdog<br>`/sonic-pfcwd:sonic-pfcwd` | ✓ | ✓ | ✓ | ⚠️ Requires PFC enabled |
| 119 | Queue<br>`/sonic-queue:sonic-queue` | ✓ | ✓ | ✓ | ✅ |
| 120 | AAA<br>`/sonic-aaa:sonic-aaa` | ✓ | ✓ | ✓ | ✅ |
| 121 | TACACS<br>`/sonic-tacacs:sonic-tacacs` | ✓ | ✓ | ✓ | ✅ |
| 122 | RADIUS<br>`/sonic-radius:sonic-radius` | ✓ | ✓ | ✓ | ✅ |
| 123 | LDAP<br>`/sonic-ldap:sonic-ldap` | ✓ | ✓ | ✓ | ✅ |
| 124 | Policer<br>`/sonic-policer:sonic-policer` | ✓ | ✓ | ✓ | ✅ |
| 125 | Watermark<br>`/sonic-watermark:sonic-watermark` | ✓ | ✓ | ✓ | ✅ |
| 126 | NAC<br>`/sonic-nac:sonic-nac` | ✓ | ✓ | ✓ | ✅ |
| 127 | IP Source Guard<br>`/sonic-ipsg:sonic-ipsg` | ✓ | ✓ | ✓ | ✅ |
| 128 | DHCP Snooping<br>`/sonic-dhcp-snooping:sonic-dhcp-snooping` | ✓ | ✓ | ✓ | ✅ |
| 129 | DAI<br>`/sonic-dai:sonic-dai` | ✓ | ✓ | ✓ | ⚠️ Requires VLAN |
| 130 | Generic Hash<br>`/sonic-hash:sonic-hash` | ✓ | ✓ | ✓ | ✅ |
| 131 | Scheduler<br>`/sonic-scheduler:sonic-scheduler` | ✓ | ✓ | ✓ | ✅ |
| 132 | PW Hardening<br>`/sonic-passwh:sonic-passwh` | ✓ | ✓ | - | ✅ |
| 133 | SSH Server<br>`/sonic-ssh-server:sonic-ssh-server` | ✓ | ✓ | - | ✅ |

---

## 5. System Management

### OpenConfig YANG (`xpath_target: OC-YANG`)

YANG: [openconfig-system.yang](https://github.com/openconfig/public/blob/master/release/models/system/openconfig-system.yang) |
[openconfig-sampling-sflow.yang](https://github.com/openconfig/public/blob/master/release/models/sampling/openconfig-sampling-sflow.yang)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 134 | System hostname<br>`/openconfig-system:system/config` | ✓ | ✓ | - | ✅ |
| 135 | System processes<br>`/openconfig-procmon:processes` | ✗ | - | - | ❌ |
| 136 | sFlow (OC)<br>`/openconfig-sampling-sflow:sampling/sflow` | ✓ | ✓ | ✓ | ✅ |

### SONiC YANG (`xpath_target: OC-YANG`)

YANG: `sonic-image-management.yang` | `sonic-system-service.yang` |
`sonic-system-logging.yang` | `sonic-system-ntp.yang` | `sonic-config-mgmt.yang` |
`sonic-device-metadata.yang` | `sonic-mirror.yang` | [`sonic-sflow.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-sflow.yang) |
`sonic-flex-counter.yang` | `sonic-mgmt-interface.yang` | `sonic-drop-counter.yang` |
[`sonic-kdump.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-kdump.yang) | [`sonic-banner.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-banner.yang) | [`sonic-serial-console.yang`](https://github.com/sonic-net/sonic-buildimage/blob/master/src/sonic-yang-models/yang-models/sonic-serial-console.yang)

| # | Feature | GET | SET | DEL | Status |
|---|---------|-----|-----|-----|--------|
| 137 | Image Mgmt<br>`/sonic-image-management:sonic-image-management` | ✓ | ✓* | - | ⚠️ Read-only nature |
| 138 | System Service<br>`/sonic-system-service:sonic-system-service` | ✗ | - | - | ❌ |
| 139 | Logging<br>`/sonic-system-logging:sonic-system-logging` | ✓ | ✓ | ✓ | ✅ |
| 140 | NTP<br>`/sonic-system-ntp:sonic-system-ntp` | ✓ | ✓ | ✓ | ✅ |
| 141 | Config Mgmt<br>`/sonic-config-mgmt:sonic-config-mgmt` | ✗ | - | - | ❌ |
| 142 | Device Metadata<br>`/sonic-device-metadata:sonic-device-metadata` | ✓ | ✓ | - | ✅ |
| 143 | Mirror<br>`/sonic-mirror:sonic-mirror` | ✓ | ✓ | ✓ | ✅ |
| 144 | sFlow (SONiC)<br>`/sonic-sflow:sonic-sflow` | ✓ | ✓ | ✓ | ✅ |
| 145 | Flex Counter<br>`/sonic-flex-counter:sonic-flex-counter` | ✓ | ✓ | - | ✅ |
| 146 | Mgmt Interface<br>`/sonic-mgmt-interface:sonic-mgmt-interface` | ✓ | ✓ | ✓ | ✅ |
| 147 | Drop Counter<br>`/sonic-drop-counter:sonic-drop-counter` | ✓ | ✓ | ✓ | ✅ |
| 148 | KDUMP<br>`/sonic-kdump:sonic-kdump` | ✓ | ✓ | - | ✅ |
| 149 | Banner<br>`/sonic-banner:sonic-banner` | ✓ | ✓ | ✓ | ✅ |
| 150 | Serial Console<br>`/sonic-serial-console:sonic-serial-console` | ✓ | ✓ | - | ✅ |

### Non-YANG (DB / OTHERS target)

| # | Feature | xpath_target | Path | GET | Status |
|---|---------|-------------|------|-----|--------|
| 151 | PSU Info | `STATE_DB` | `/PSU_INFO` | ✓ | ✅ |
| 152 | FAN Info | `STATE_DB` | `/FAN_INFO` | ✓ | ✅ |
| 153 | Temperature | `STATE_DB` | `/TEMPERATURE_INFO` | ✓ | ✅ |
| 154 | CPU | `OTHERS` | `/platform/cpu` | ✓ | ✅ |
| 155 | Memory | `OTHERS` | `/proc/meminfo` | ✓ | ✅ |
| 156 | Load Average | `OTHERS` | `/proc/loadavg` | ✓ | ✅ |
| 157 | OS Version | `OTHERS` | `/osversion/build` | ✓ | ✅ |
| 158 | Uptime | `OTHERS` | `/proc/uptime` | ✓ | ✅ |

---

## Summary

| Category | Total | ✅ | ❌ | ⚠️ | ☐ |
|----------|-------|----|----|----|---|
| Interface | 59 | 47 | 5 | 7 | 0 |
| Layer 2 | 19 | 19 | 0 | 0 | 0 |
| Layer 3 | 24 | 22 | 1 | 1 | 0 |
| Security | 31 | 28 | 0 | 2 | 1 |
| System Mgmt | 25 | 21 | 4 | 3 | 0 |
| **Total** | **158** | **137** | **10** | **13** | **1** |

> ✅ = Verified on DUT (GET/SET/DEL all tested).
> ❌ = Not supported or node not found.
> ⚠️ = Works but requires preconditions or platform-specific.
> ☐ = Not tested (risk of disrupting DUT).
