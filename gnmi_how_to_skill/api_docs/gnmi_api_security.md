# gNMI API - Security


## OpenConfig ACL (`xpath_target: OC-YANG`)

### Get ACL

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-acl:acl
```

---

## SONiC ACL (`xpath_target: OC-YANG`)

### Create ACL Table

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST:@./acl.json
```

acl.json:
```json
{
  "sonic-acl:ACL_TABLE_LIST": [{
    "aclname": "GNMI_TEST_ACL",
    "type": "L3",
    "stage": "INGRESS",
    "policy_desc": "gNMI test ACL",
    "ports": ["Ethernet0"]
  }]
}
```

### Get ACL

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-acl:sonic-acl
```

Response:
```json
{
  "sonic-acl:sonic-acl": {
    "ACL_TABLE": {
      "ACL_TABLE_LIST": [{
        "aclname": "GNMI_TEST_ACL",
        "policy_desc": "gNMI test ACL",
        "ports": ["Ethernet0"],
        "stage": "INGRESS",
        "type": "L3"
      }]
    }
  }
}
```

### Delete ACL Table

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[aclname=GNMI_TEST_ACL]
```

---

## SONiC WRED Profile

### Create WRED Profile

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST:@./wred.json
```

wred.json:
```json
{
  "sonic-wred-profile:WRED_PROFILE_LIST": [{
    "name": "WRED_GREEN",
    "green_min_threshold": "1000000",
    "green_max_threshold": "2000000",
    "green_drop_probability": "10"
  }]
}
```

### Get WRED Profile

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-wred-profile:sonic-wred-profile
```

Response:
```json
{
  "sonic-wred-profile:sonic-wred-profile": {
    "WRED_PROFILE": {
      "WRED_PROFILE_LIST": [{
        "name": "WRED_GREEN",
        "ecn": "ecn_none",
        "green_drop_probability": "10",
        "green_max_threshold": "2000000",
        "green_min_threshold": "1000000"
      }]
    }
  }
}
```

### Delete WRED Profile

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-wred-profile:sonic-wred-profile/WRED_PROFILE/WRED_PROFILE_LIST[name=WRED_GREEN]
```

---

## SONiC QoS Map (DSCP-TC)

### Create DSCP-TC Map

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-dscp-tc-map:sonic-dscp-tc-map/DSCP_TO_TC_MAP/DSCP_TO_TC_MAP_LIST:@./dscp.json
```

dscp.json:
```json
{"sonic-dscp-tc-map:DSCP_TO_TC_MAP_LIST": [{"name": "GNMI_DSCP_MAP"}]}
```

### Get DSCP-TC Map

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-dscp-tc-map:sonic-dscp-tc-map
```

Response:
```json
{
  "sonic-dscp-tc-map:sonic-dscp-tc-map": {
    "DSCP_TO_TC_MAP": {
      "DSCP_TO_TC_MAP_LIST": [{
        "name": "GNMI_DSCP_MAP",
        "DSCP_TO_TC_MAP_INTERNAL_LIST": [{"dscp": "NULL", "tc_num": "NULL"}]
      }]
    }
  }
}
```

### Delete DSCP-TC Map

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-dscp-tc-map:sonic-dscp-tc-map/DSCP_TO_TC_MAP/DSCP_TO_TC_MAP_LIST[name=GNMI_DSCP_MAP]
```

> Other QoS maps follow the same pattern:
> - `/sonic-dot1p-tc-map:sonic-dot1p-tc-map`
> - `/sonic-tc-queue-map:sonic-tc-queue-map`
> - `/sonic-tc-dscp-map:sonic-tc-dscp-map`
> - `/sonic-tc-dot1p-map:sonic-tc-dot1p-map`
> - `/sonic-tc-priority-group-map:sonic-tc-priority-group-map`
> - `/sonic-pfc-priority-queue-map:sonic-pfc-priority-queue-map`
> - `/sonic-port-qos-map:sonic-port-qos-map`

---

## SONiC Generic Hash

### Set ECMP Hash

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-hash:sonic-hash/SWITCH_HASH/SWITCH_HASH_LIST:@./hash.json
```

hash.json:
```json
{
  "sonic-hash:SWITCH_HASH_LIST": [{
    "name": "GLOBAL",
    "ecmp_hash": ["SRC_IP", "DST_IP", "IP_PROTOCOL", "L4_SRC_PORT", "L4_DST_PORT"]
  }]
}
```

> `name` must be `"GLOBAL"`. `ecmp_hash` is an array (leaf-list).

### Get Hash

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-hash:sonic-hash
```

Response:
```json
{
  "sonic-hash:sonic-hash": {
    "SWITCH_HASH": {
      "SWITCH_HASH_LIST": [{
        "ecmp_hash": ["SRC_IP", "DST_IP", "IP_PROTOCOL", "L4_SRC_PORT", "L4_DST_PORT"],
        "name": "GLOBAL"
      }]
    }
  }
}
```

### Delete Hash

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-hash:sonic-hash/SWITCH_HASH/SWITCH_HASH_LIST[name=GLOBAL]
```

---

## SONiC AAA

### Set AAA Authentication

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-aaa:sonic-aaa/AAA/AAA_LIST:@./aaa.json
```

aaa.json:
```json
{"sonic-aaa:AAA_LIST": [{"type": "authentication", "login": "local"}]}
```

### Get AAA

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-aaa:sonic-aaa
```

Response:
```json
{
  "sonic-aaa:sonic-aaa": {
    "AAA": {
      "AAA_LIST": [{
        "login": "local",
        "readonly_login_mode": "shell",
        "type": "authentication"
      }]
    }
  }
}
```

### Delete AAA

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-aaa:sonic-aaa/AAA/AAA_LIST[type=authentication]
```

---

## SONiC TACACS

### Add TACACS Server

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-tacacs:sonic-tacacs/TACPLUS_SERVER/TACPLUS_SERVER_LIST:@./tacacs.json
```

tacacs.json:
```json
{"sonic-tacacs:TACPLUS_SERVER_LIST": [{"ipaddress": "10.10.10.1", "priority": 1, "tcp_port": 49}]}
```

> `priority` and `tcp_port` must be numeric.

### Get TACACS

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-tacacs:sonic-tacacs
```

Response:
```json
{
  "sonic-tacacs:sonic-tacacs": {
    "TACPLUS_SERVER": {
      "TACPLUS_SERVER_LIST": [{
        "ipaddress": "10.10.10.1",
        "priority": 1,
        "tcp_port": 49
      }]
    }
  }
}
```

### Delete TACACS Server

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-tacacs:sonic-tacacs/TACPLUS_SERVER/TACPLUS_SERVER_LIST[ipaddress=10.10.10.1]
```

---

## SONiC RADIUS

### Add RADIUS Server

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-radius:sonic-radius/RADIUS_SERVER/RADIUS_SERVER_LIST:@./radius.json
```

radius.json:
```json
{"sonic-radius:RADIUS_SERVER_LIST": [{"ipaddress": "10.10.10.2", "priority": 1, "auth_port": 1812}]}
```

### Delete RADIUS Server

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-radius:sonic-radius/RADIUS_SERVER/RADIUS_SERVER_LIST[ipaddress=10.10.10.2]
```

---

## SONiC LDAP

### Add LDAP Server

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-ldap:sonic-ldap/LDAP_SERVER/LDAP_SERVER_LIST:@./ldap.json
```

ldap.json:
```json
{"sonic-ldap:LDAP_SERVER_LIST": [{"ipaddress": "10.10.10.3"}]}
```

### Delete LDAP Server

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-ldap:sonic-ldap/LDAP_SERVER/LDAP_SERVER_LIST[ipaddress=10.10.10.3]
```

---

## SONiC Policer

### Create Policer

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-policer:sonic-policer/POLICER/POLICER_LIST:@./policer.json
```

policer.json:
```json
{
  "sonic-policer:POLICER_LIST": [{
    "policername": "GNMI_POLICER",
    "meter_type": "packets",
    "mode": "sr_tcm",
    "color_source": "blind",
    "cir": "1000",
    "cbs": "1000",
    "pbs": "1000",
    "red_packet_action": "drop",
    "green_packet_action": "forward",
    "yellow_packet_action": "forward"
  }]
}
```

> All fields above are mandatory.

### Get Policer

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-policer:sonic-policer
```

Response:
```json
{
  "sonic-policer:sonic-policer": {
    "POLICER": {
      "POLICER_LIST": [{
        "policername": "GNMI_POLICER",
        "meter_type": "packets",
        "mode": "sr_tcm",
        "color_source": "blind",
        "cir": "1000",
        "cbs": "1000",
        "pbs": "1000",
        "red_packet_action": "drop",
        "green_packet_action": "forward",
        "yellow_packet_action": "forward"
      }]
    }
  }
}
```

### Delete Policer

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-policer:sonic-policer/POLICER/POLICER_LIST[policername=GNMI_POLICER]
```

---

## SONiC Scheduler

### Create Scheduler

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-scheduler:sonic-scheduler/SCHEDULER/SCHEDULER_LIST:@./sched.json
```

sched.json:
```json
{"sonic-scheduler:SCHEDULER_LIST": [{"name": "GNMI_SCHED", "type": "DWRR", "weight": 10}]}
```

> `weight` must be numeric.

### Get Scheduler

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-scheduler:sonic-scheduler
```

Response:
```json
{
  "sonic-scheduler:sonic-scheduler": {
    "SCHEDULER": {
      "SCHEDULER_LIST": [{"name": "GNMI_SCHED", "type": "DWRR", "weight": 10}]
    }
  }
}
```

### Delete Scheduler

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-scheduler:sonic-scheduler/SCHEDULER/SCHEDULER_LIST[name=GNMI_SCHED]
```

---

## SONiC SSH Server

### Set SSH Max Sessions

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-ssh-server:sonic-ssh-server/SSH_SERVER/POLICIES:@./ssh.json
```

ssh.json:
```json
{"sonic-ssh-server:POLICIES": {"max_sessions": 10}}
```

> `max_sessions` must be numeric.

### Get SSH Server

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-ssh-server:sonic-ssh-server
```

Response:
```json
{
  "sonic-ssh-server:sonic-ssh-server": {
    "SSH_SERVER": {
      "POLICIES": {"max_sessions": 10}
    }
  }
}
```

### Delete SSH Setting

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-ssh-server:sonic-ssh-server/SSH_SERVER/POLICIES/max_sessions
```

---

## SONiC Password Hardening

### Set Password Policy

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-passwh:sonic-passwh/PASSW_HARDENING/POLICIES:@./passwh.json
```

passwh.json:
```json
{"sonic-passwh:POLICIES": {"expiration": 90}}
```

> `expiration` must be numeric. This is a container (not a list).

### Get Password Policy

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-passwh:sonic-passwh
```

---

## SONiC ACL Rule

### Create ACL Rule

> ACL Table must exist first.

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-acl:sonic-acl/ACL_RULE/ACL_RULE_LIST:@./rule.json
```

rule.json:
```json
{
  "sonic-acl:ACL_RULE_LIST": [{
    "aclname": "GNMI_TEST_ACL",
    "rulename": "RULE_10",
    "PRIORITY": 10,
    "PACKET_ACTION": "DROP",
    "SRC_IP": "10.0.0.0/8"
  }]
}
```

> `PRIORITY` must be numeric. Key: `aclname` + `rulename`.

### Delete ACL Rule

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-acl:sonic-acl/ACL_RULE/ACL_RULE_LIST[aclname=GNMI_TEST_ACL][rulename=RULE_10]
```

---

## SONiC Buffer

### Create Buffer Pool

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-buffer-pool:sonic-buffer-pool/BUFFER_POOL/BUFFER_POOL_LIST:@./pool.json
```

pool.json:
```json
{"sonic-buffer-pool:BUFFER_POOL_LIST": [{"name": "test_pool", "type": "egress", "size": "1024000", "mode": "dynamic"}]}
```

> `size` must be string. `mode` is mandatory.

### Create Buffer Profile

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-buffer-profile:sonic-buffer-profile/BUFFER_PROFILE/BUFFER_PROFILE_LIST:@./prof.json
```

prof.json:
```json
{"sonic-buffer-profile:BUFFER_PROFILE_LIST": [{"name": "test_profile", "pool": "test_pool", "size": "0", "dynamic_th": 1}]}
```

> `dynamic_th` must be numeric.

### Create Buffer Queue

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-buffer-queue:sonic-buffer-queue/BUFFER_QUEUE/BUFFER_QUEUE_LIST:@./bq.json
```

bq.json:
```json
{"sonic-buffer-queue:BUFFER_QUEUE_LIST": [{"port": "Ethernet0", "qindex": "0", "profile": "test_profile"}]}
```

> Key: `port` + `qindex`.

### Delete (reverse order)

```bash
gnmi_set ... -delete /sonic-buffer-queue:..../BUFFER_QUEUE_LIST[port=Ethernet0][qindex=0]
gnmi_set ... -delete /sonic-buffer-profile:..../BUFFER_PROFILE_LIST[name=test_profile]
gnmi_set ... -delete /sonic-buffer-pool:..../BUFFER_POOL_LIST[name=test_pool]
```

---

## SONiC Port QoS Map

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-port-qos-map:sonic-port-qos-map/PORT_QOS_MAP/PORT_QOS_MAP_LIST:@./pqm.json
```

pqm.json:
```json
{"sonic-port-qos-map:PORT_QOS_MAP_LIST": [{"ifname": "Ethernet0", "dscp_to_tc_map": "MY_DSCP_MAP"}]}
```

> Referenced map must exist first.

---

## SONiC PFCWD

### Set PFC Watchdog Global

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-pfcwd:sonic-pfcwd/PFC_WD/PFC_WD_LIST:@./pfcwd.json
```

pfcwd.json:
```json
{"sonic-pfcwd:PFC_WD_LIST": [{"ifname": "GLOBAL", "POLL_INTERVAL": 100}]}
```

> `POLL_INTERVAL` must be numeric. Per-port requires PFC priority enabled.

### Delete PFCWD

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-pfcwd:sonic-pfcwd/PFC_WD/PFC_WD_LIST[ifname=GLOBAL]
```

---

## SONiC Queue

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-queue:sonic-queue/QUEUE/QUEUE_LIST:@./queue.json
```

queue.json:
```json
{"sonic-queue:QUEUE_LIST": [{"ifname": "Ethernet0", "qindex": "0"}]}
```

> Key: `ifname` + `qindex`. Add `scheduler` field to bind a scheduler profile.

---

## SONiC TACACS Global

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-tacacs:sonic-tacacs/TACPLUS/TACPLUS_LIST:@./tacplus.json
```

tacplus.json:
```json
{"sonic-tacacs:TACPLUS_LIST": [{"name": "global", "auth_type": "login", "timeout": 5}]}
```

> Key `name` must be `"global"`. `timeout` is numeric.

---

## SONiC RADIUS Global

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-radius:sonic-radius/RADIUS/RADIUS_LIST:@./radius_g.json
```

radius_g.json:
```json
{"sonic-radius:RADIUS_LIST": [{"name": "global", "auth_type": "pap", "timeout": 5}]}
```

---

## SONiC LDAP Global

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-ldap:sonic-ldap/LDAP/LDAP_LIST:@./ldap_g.json
```

ldap_g.json:
```json
{"sonic-ldap:LDAP_LIST": [{"name": "global", "timeout": 5}]}
```

---

## SONiC Watermark

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-watermark:sonic-watermark/WATERMARK_TABLE/WATERMARK_TABLE_LIST:@./wm.json
```

wm.json:
```json
{"sonic-watermark:WATERMARK_TABLE_LIST": [{"table_name": "TELEMETRY_INTERVAL", "interval": 120}]}
```

> `table_name` must be `"TELEMETRY_INTERVAL"`. `interval` is numeric.

---

## SONiC NAC (802.1X)

### Set DOT1X Global

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-nac:sonic-nac/DOT1X/DOT1X_LIST:@./dot1x.json
```

dot1x.json:
```json
{"sonic-nac:DOT1X_LIST": [{"param": "GLOBAL"}]}
```

> Key `param` must be `"GLOBAL"`. Leaf: `admin_status`.

### Set DOT1X Port

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-nac:sonic-nac/DOT1X_PORT/DOT1X_PORT_LIST:@./dot1x_port.json
```

dot1x_port.json:
```json
{"sonic-nac:DOT1X_PORT_LIST": [{"ifname": "Ethernet4"}]}
```

### Delete DOT1X Port

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-nac:sonic-nac/DOT1X_PORT/DOT1X_PORT_LIST[ifname=Ethernet4]
```

---

## SONiC IP Source Guard

### Set IPSG Port

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-ipsg:sonic-ipsg/IPSG_PORT/IPSG_PORT_LIST:@./ipsg.json
```

ipsg.json:
```json
{"sonic-ipsg:IPSG_PORT_LIST": [{"ifname": "Ethernet4"}]}
```

### Delete IPSG Port

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-ipsg:sonic-ipsg/IPSG_PORT/IPSG_PORT_LIST[ifname=Ethernet4]
```

---

## SONiC DHCP Snooping

### Set DHCP Snooping Global

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-dhcp-snooping:sonic-dhcp-snooping/DHCPSNP/DHCPSNP_LIST:@./dhcpsnp.json
```

dhcpsnp.json:
```json
{"sonic-dhcp-snooping:DHCPSNP_LIST": [{"param": "GLOBAL", "IPv4": "enable"}]}
```

> Key `param` must be `"GLOBAL"`.

### Delete DHCP Snooping

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-dhcp-snooping:sonic-dhcp-snooping/DHCPSNP/DHCPSNP_LIST[param=GLOBAL]
```

---

## SONiC DAI (Dynamic ARP Inspection)

### Set DAI on VLAN

> VLAN must exist first.

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-dai:sonic-dai/DAI_VLAN/DAI_VLAN_LIST:@./dai.json
```

dai.json:
```json
{"sonic-dai:DAI_VLAN_LIST": [{"vlan_name": "Vlan100"}]}
```

### Delete DAI VLAN

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-dai:sonic-dai/DAI_VLAN/DAI_VLAN_LIST[vlan_name=Vlan100]
```

---

## SONiC Password Hardening (full fields)

### Get Password Policy

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-passwh:sonic-passwh
```

Response:
```json
{
  "sonic-passwh:sonic-passwh": {
    "PASSW_HARDENING": {
      "POLICIES": {
        "state": "disabled",
        "expiration": 180,
        "expiration_warning": 15,
        "history_cnt": 10,
        "len_min": 8,
        "reject_user_passw_match": true,
        "lower_class": true,
        "upper_class": true,
        "digits_class": true,
        "special_class": true
      }
    }
  }
}
```

### Update Password Policy

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-passwh:sonic-passwh/PASSW_HARDENING/POLICIES:@./passwh.json
```

passwh.json:
```json
{"sonic-passwh:POLICIES": {"state": "enabled", "expiration": 90, "len_min": 12}}
```

> All numeric fields must be numeric. `state`: `"enabled"` / `"disabled"`.

---

## SONiC SSH Server (full fields)

### Set SSH Policies

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-ssh-server:sonic-ssh-server/SSH_SERVER/POLICIES:@./ssh.json
```

ssh.json:
```json
{"sonic-ssh-server:POLICIES": {"max_sessions": 10, "inactivity_timeout": 300}}
```

> `max_sessions` and `inactivity_timeout` must be numeric.

Available fields: `max_sessions`, `inactivity_timeout`, `ciphers`, `kex_algorithms`, `macs`

### Delete SSH Setting (leaf)

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-ssh-server:sonic-ssh-server/SSH_SERVER/POLICIES/max_sessions
```
