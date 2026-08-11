# gNMI Path Derivation from YANG Models

This document describes how to derive gNMI xpath from YANG model definitions.
It covers both SONiC YANG and OpenConfig YANG path formats used in SONiC gNMI Telemetry.

---

## Path Construction Rules

### Rule 1: Hierarchical Mapping

The nested structure of a YANG model maps directly to the `/`-separated gNMI xpath:

```
module → container → container → list → leaf
```

Translates to:

```
/<module-name>:<top-container>/<container>/<list>[key=value]/<leaf>
```

### Rule 2: Module Prefix

The first element of the xpath must include the YANG module name as a prefix,
separated by a colon:

```
<module-name>:<top-level-container>
```

Subsequent path elements do not require the module prefix unless they belong
to a different (augmenting) module.

### Rule 3: List Key Notation

YANG `list` nodes use square brackets to specify key values in the xpath:

- Single key: `[key=value]`
- Multiple keys: `[key1=value1][key2=value2]`

### Rule 4: JSON Payload Prefix

The JSON request body must include the module prefix on the top-level key:

- SONiC YANG: `{"sonic-port:mtu": 9100}`
- OpenConfig: `{"openconfig-interfaces:mtu": 9100}`

### Rule 5: xpath_target Parameter

All OpenConfig and SONiC YANG paths require `-xpath_target OC-YANG`.
Non-YANG paths use `STATE_DB` or `OTHERS` as the target.

---

## Example 1: Get/Set Ethernet MTU

### SONiC YANG

**YANG structure (sonic-port.yang):**

```yang
module sonic-port {
  container sonic-port {
    container PORT {
      list PORT_LIST {
        key "ifname";
        leaf ifname { ... }
        leaf mtu { ... }
      }
    }
  }
}
```

**Derived gNMI path:**

```
/sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]/mtu
```

**GET command:**

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]/mtu
```

**SET command:**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update /sonic-port:sonic-port/PORT/PORT_LIST[ifname=Ethernet0]/mtu:@./mtu.json
```

**mtu.json:**

```json
{"sonic-port:mtu": 9100}
```

### OpenConfig YANG

**YANG structure (openconfig-interfaces.yang):**

```yang
module openconfig-interfaces {
  container interfaces {
    list interface {
      key "name";
      leaf name { ... }
      container config {
        uses interface-phys-config;
      }
    }
  }
}

grouping interface-phys-config {
  leaf name { ... }
  leaf mtu { ... }
}
```

**Derived gNMI path:**

```
/openconfig-interfaces:interfaces/interface[name=Ethernet0]/config/mtu
```

> Note: The `grouping` content is expanded inline under the `container`
> that uses it. In the xpath, reference the leaf directly under `config/`.

**GET command:**

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-interfaces:interfaces/interface[name=Ethernet0]/config/mtu
```

**SET command:**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update /openconfig-interfaces:interfaces/interface[name=Ethernet0]/config/mtu:@./mtu.json
```

**mtu.json:**

```json
{"openconfig-interfaces:mtu": 9100}
```

---

## Example 2: Create VLAN

### SONiC YANG

**YANG structure (sonic-vlan.yang):**

```yang
module sonic-vlan {
  container sonic-vlan {
    container VLAN {
      list VLAN_LIST {
        key "name";
        leaf name { ... }
        leaf vlanid { ... }
        leaf admin_status { ... }
      }
    }
  }
}
```

**Derived gNMI path (target the container level for replace):**

```
/sonic-vlan:sonic-vlan/VLAN
```

**SET command:**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-vlan:sonic-vlan/VLAN:@./vlan.json
```

**vlan.json:**

```json
{
  "sonic-vlan:VLAN": {
    "VLAN_LIST": [{"name": "Vlan100", "vlanid": 100, "admin_status": "up"}]
  }
}
```

### OpenConfig YANG

**Derived gNMI path (target the list entry with key):**

```
/openconfig-interfaces:interfaces/interface[name=Vlan100]
```

**SET command:**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /openconfig-interfaces:interfaces/interface[name=Vlan100]:@./vlan.json
```

**vlan.json:**

```json
{
  "openconfig-interfaces:interface": [{"name": "Vlan100", "config": {"name": "Vlan100"}}]
}
```

---

## Example 3: Create PortChannel Member

### SONiC YANG

**YANG structure (sonic-portchannel.yang):**

```yang
module sonic-portchannel {
  container sonic-portchannel {
    container PORTCHANNEL_MEMBER {
      list PORTCHANNEL_MEMBER_LIST {
        key "name ifname";
        leaf name { ... }
        leaf ifname { ... }
      }
    }
  }
}
```

**Derived gNMI path:**

```
/sonic-portchannel:sonic-portchannel/PORTCHANNEL_MEMBER/PORTCHANNEL_MEMBER_LIST
```

**SET command:**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-portchannel:sonic-portchannel/\
PORTCHANNEL_MEMBER/PORTCHANNEL_MEMBER_LIST:@./member.json
```

**member.json:**

```json
{
  "sonic-portchannel:PORTCHANNEL_MEMBER_LIST": [
    {"name": "PortChannel100", "ifname": "Ethernet0"}
  ]
}
```

**DELETE command (specify keys):**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -delete /sonic-portchannel:sonic-portchannel/\
PORTCHANNEL_MEMBER/PORTCHANNEL_MEMBER_LIST[name=PortChannel100][ifname=Ethernet0]
```

### OpenConfig YANG

The OpenConfig path for adding a port to a PortChannel is:

```
/openconfig-interfaces:interfaces/interface[name=Ethernet0]/
  openconfig-if-ethernet:ethernet/config/openconfig-if-aggregate:aggregate-id
```

**SET command:**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update "/openconfig-interfaces:interfaces/interface[name=Ethernet0]/\
openconfig-if-ethernet:ethernet/config/\
openconfig-if-aggregate:aggregate-id:@./agg.json"
```

**agg.json:**

```json
{"openconfig-if-aggregate:aggregate-id": "1"}
```

> **Important:** The value is the PortChannel numeric ID only (`"1"` for
> PortChannel1), not the full name. The PortChannel must exist before
> assigning a member port.

---

## Example 4: Create Loopback Interface

### SONiC YANG

**YANG structure (sonic-loopback-interface.yang):**

```yang
module sonic-loopback-interface {
  container sonic-loopback-interface {
    container LOOPBACK_INTERFACE {
      list LOOPBACK_INTERFACE_LIST {
        key "loIfName";
        leaf loIfName { ... }
      }
    }
  }
}
```

**Derived gNMI path:**

```
/sonic-loopback-interface:sonic-loopback-interface/LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_LIST
```

**SET command:**

```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -replace /sonic-loopback-interface:sonic-loopback-interface/\
LOOPBACK_INTERFACE/LOOPBACK_INTERFACE_LIST:@./lo.json
```

**lo.json:**

```json
{"sonic-loopback-interface:LOOPBACK_INTERFACE_LIST": [{"loIfName": "Loopback1"}]}
```

---

## Quick Reference

### Path Construction Summary

| Rule | Description | Example |
|------|-------------|---------|
| Module prefix | First element uses `module:container` | `sonic-port:sonic-port` |
| Path separator | YANG hierarchy separated by `/` | `.../PORT/PORT_LIST` |
| List key | Specified with `[key=value]` | `PORT_LIST[ifname=Ethernet0]` |
| Multiple keys | Each key in separate brackets | `[name=X][ifname=Y]` |
| JSON prefix | Top-level JSON key includes module name | `"sonic-port:mtu": 9100` |
| GET leaf | xpath can point directly to a leaf | `.../mtu` |
| SET container | REPLACE targets container/list level | `.../VLAN:@./file.json` |
| grouping/uses | Expanded inline under parent container | `config/mtu` (from grouping) |

### gNMI Operation Types

| Operation | Purpose | xpath Target Level |
|-----------|---------|-------------------|
| `gnmi_get -xpath` | Read value | Leaf, container, or list |
| `gnmi_set -update` | Update existing value | Leaf or container |
| `gnmi_set -replace` | Create or fully replace | Container or list |
| `gnmi_set -delete` | Remove entry | List entry with key(s) |

### Common Pitfalls

- **`aggregate-id` value is the numeric ID, not the full PortChannel name:**

  The OpenConfig `aggregate-id` field expects only the numeric portion of
  the PortChannel name. The server internally prepends `"PortChannel"` to
  construct the full interface name.

  | Correct | Wrong |
  |---------|-------|
  | `{"openconfig-if-aggregate:aggregate-id": "1"}` | `{"openconfig-if-aggregate:aggregate-id": "PortChannel1"}` |

  The wrong value causes `"Interface does not exist in DB"` because the
  server looks up `"PortChannelPortChannel1"` which does not exist.

- **Multi-colon xpath is supported:**

  Paths with multiple `:` characters (cross-module augmentation) work
  correctly. The CLI uses `SplitN(":", 2)` to split only at the last
  path/value boundary.

  ```bash
  # This works — 3 colons in the xpath, no problem:
  gnmi_set ... -update "/openconfig-interfaces:interfaces/\
  interface[name=Ethernet0]/openconfig-if-ethernet:ethernet/\
  config/openconfig-if-aggregate:aggregate-id:@./agg.json"
  ```

- **xpath_target required:** All YANG-based paths must specify
  `-xpath_target OC-YANG`. Omitting this parameter will result in lookup failure.

- **Data type sensitivity:** The gNMI server strictly validates JSON field types.
  Refer to the API Checklist "Data Type Notes" section for correct types
  (numeric vs. string vs. boolean vs. array).
