# SONiC gNMI Usage SKILL

## Overview

gNMI (gRPC Network Management Interface) on SONiC provides programmatic access to
switch configuration and telemetry data. This skill covers the essential knowledge
for using gNMI on Edgecore SONiC devices.

---

## Quick Start

```bash
# GET interface config
docker exec gnmi gnmi_get -notls -target_addr localhost:8080 \
  -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet0]/config

# SET interface MTU
docker exec gnmi gnmi_set -notls -target_addr localhost:8080 \
  -xpath_target OC-YANG \
  -update /sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]/mtu:@./mtu.json
# mtu.json: {"sonic-port:mtu": 9100}

# DELETE a VLAN
docker exec gnmi gnmi_set -notls -target_addr localhost:8080 \
  -xpath_target OC-YANG \
  -delete /openconfig-interfaces:interfaces/interface[name=Vlan100]
```

---

## Core Concepts

### xpath_target

| Target | Usage | Path Format |
|--------|-------|-------------|
| `OC-YANG` | OpenConfig + SONiC YANG models | `/module:container/...` |
| `COUNTERS_DB` | Port/Queue/PG counters | `COUNTERS/Ethernet0` |
| `STATE_DB` | PSU/FAN/TEMP info | `/PSU_INFO` |
| `CONFIG_DB` | Switch configuration | `/PORT/Ethernet0` |
| `APPL_DB` | Application state | `/PORT_TABLE/Ethernet0` |
| `OTHERS` | System metrics | `/platform/cpu`, `/proc/loadavg` |

### gNMI Operations

| Operation | Usage | Example |
|-----------|-------|---------|
| `gnmi_get -xpath` | Read | Any path, any target |
| `gnmi_set -update` | Update existing | Leaf or container |
| `gnmi_set -replace` | Create or overwrite | Container or list |
| `gnmi_set -delete` | Remove | List entry with key(s) |

### Path Format Rules

1. First element: `<module-name>:<top-container>`
2. List keys: `[key=value]`, multiple: `[k1=v1][k2=v2]`
3. JSON payload prefix: `{"module-name:field": value}`

---

## Connection Modes

| Mode | Flag | When |
|------|------|------|
| noTLS | `-notls` | `--noTLS` in telemetry startup |
| Insecure (TLS skip verify) | `-insecure` | TLS enabled, skip cert check |
| TLS with auth | `-cert`, `-key`, `-username`, `-password` | Production |

---

## Subscription (Dial-in)

```bash
# Stream on-change (any DB target)
gnmic subscribe --address <DUT>:8080 --insecure \
  --mode stream --stream-mode on-change \
  --path "COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS" \
  --target COUNTERS_DB --encoding json_ietf

# Stream sample (periodic)
gnmic subscribe --address <DUT>:8080 --insecure \
  --mode stream --stream-mode sample --sample-interval 5s \
  --path "/TEMPERATURE_INFO" --target STATE_DB --encoding json_ietf

# Once (snapshot)
gnmic subscribe --address <DUT>:8080 --insecure \
  --mode once \
  --path "/openconfig-system:system/config" \
  --target OC-YANG --encoding json_ietf
```

### Stream Mode Support

| Mode | DB targets | OC-YANG | OTHERS |
|------|-----------|---------|--------|
| once | ✅ | ✅ | ✅ |
| poll | ✅ | ✅ | ✅ |
| stream (on-change) | ✅ | ❌ | ❌ |
| stream (sample) | ✅ | ❌ | ✅ |

---

## Dial-out (Telemetry Push)

DUT pushes data to external collector. Uses custom `gnmi.sonic.gNMIDialOut` service
(not standard gNMI — gnmic cannot be used as collector).

```bash
# Configure on DUT
sudo sonic-db-cli CONFIG_DB HSET "TELEMETRY_CLIENT|Global" \
  encoding JSON_IETF retry_interval 30 src_ip <DUT_IP> unidirectional true
sudo sonic-db-cli CONFIG_DB HSET "TELEMETRY_CLIENT|DestinationGroup_X" \
  dst_addr <COLLECTOR_IP>:8081
sudo sonic-db-cli CONFIG_DB HSET "TELEMETRY_CLIENT|Subscription_X" \
  dst_group X path_target STATE_DB paths TEMPERATURE_INFO \
  report_interval 5000 report_type periodic
sudo docker exec gnmi supervisorctl restart dialout
```

Collector must serve TLS (self-signed OK). See `gnmi_dial_out-subscription.md`.

---

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| `aggregate-id` value | Use numeric ID only (`"1"` not `"PortChannel1"`) |
| `mtu` type | Numeric `9100` (not string) |
| `distance` (static route) | String `"0"` (not numeric) |
| `kbps` (storm-control) | String `"1000"` (not numeric) |
| `ethernet/state` leaf GET fails | Use parent path `/ethernet` instead |
| OC-YANG stream subscribe | Not supported; use DB target paths |
| gnmic as dial-out collector | Not compatible; use custom `collector.py` |

---

## Document Index

## Document Reference

### In this SKILL (always available)

| Document | When to Use |
|----------|-------------|
| `SKILL.md` (this file) | Quick lookup: commands, targets, pitfalls |
| `api_checklist.md` | Need to know: which API exists, key fields, data types, supported operations |
| `gnmi_path_yang_model_how_to_mapping.md` | Need to construct a new gNMI path from YANG model |
| `gnmi_dial_in.md` | Setting up Subscribe (stream/poll/once) with gnmic or gnmi_cli |
| `gnmi_dial_out-subscription.md` | Setting up dial-out telemetry push to external collector |

### External documents (read file when triggered)

When the information in this SKILL is insufficient, follow this priority order:

**Priority 1 → `api_docs/gnmi_api_{category}.md`** (complete examples)

| Trigger | File |
|---------|------|
| Need full JSON payload with all required fields | `api_docs/gnmi_api_interface.md` |
| Need exact request/response for VLAN, STP, Storm Control | `api_docs/gnmi_api_layer2.md` |
| Need exact request/response for IP, Route, VRF, BGP | `api_docs/gnmi_api_layer3.md` |
| Need exact request/response for ACL, QoS, AAA, Policer | `api_docs/gnmi_api_security.md` |
| Need exact request/response for Hostname, NTP, PSU, FAN | `api_docs/gnmi_api_system.md` |

**Priority 2 → `yang-models/sonic-{module}.yang`** (YANG structure)

| Trigger | File |
|---------|------|
| Need to know ALL available fields/leaves for any module | Read `yang-models/sonic-{module}.yang` |
| Need to confirm valid enum values or pattern constraints | Read `yang-models/sonic-{module}.yang` |
| api_docs has no example for this specific API | Read YANG to find key, leaf names, types |
| YANG file not in `yang-models/` | Check DUT: `docker exec gnmi cat /usr/models/yang/{module}.yang` |

> ⚠️ Key names in `yang-models/` may differ from gNMI actual keys due to
> build-time renaming. Always cross-check with `api_checklist.md` Key Field Reference.

**Priority 3 → `dialout-collector/`** (source code)

| Trigger | File |
|---------|------|
| Need collector implementation or proto definition | `dialout-collector/` |

---

## Key References

- SONiC gNMI server: https://github.com/sonic-net/sonic-gnmi
- OpenConfig gNMI spec: https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md
- gnmic client: https://gnmic.openconfig.net
- OpenConfig YANG models: https://github.com/openconfig/public/tree/master/release/models
- SONiC YANG models: https://github.com/sonic-net/sonic-buildimage/tree/master/src/sonic-yang-models/yang-models
