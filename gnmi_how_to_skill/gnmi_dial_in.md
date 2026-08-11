# gNMI Dial-in (gRPC Subscribe)

## Key Points

- Dial-in = external client connects TO the SONiC Device gNMI server
- DUT runs gNMI server (telemetry service) on port 8080
- Supports standard gNMI Subscribe RPC (once / poll / stream)
- Stream mode (on-change / sample) works with all DB targets (DB path format)
- OC-YANG target only supports `once` and `poll` modes

---

## Architecture

```
┌─────────────────────────────┐           ┌─────────────────────────────┐
│     External Client         │           │         SONiC DUT           │
│                             │           │                             │
│  ┌───────────────────────┐  │           │  ┌───────────────────────┐  │
│  │   gnmi_get / gnmi_cli │  │           │  │   telemetry service   │  │
│  │   gnmic               │  │  gRPC     │  │   (gNMI Server)       │  │
│  │   pygnmi              │  │  (noTLS)  │  │   port 8080           │  │
│  │                       │──┼───────────┼──▶                       │  │
│  │  Sends:               │  │           │  │  Serves:              │  │
│  │  - GetRequest         │  │           │  │  - COUNTERS_DB        │  │
│  │  - SubscribeRequest   │◀─┼───────────┼──│  - STATE_DB           │  │
│  │                       │  │  Stream   │  │  - CONFIG_DB          │  │
│  │  Receives:            │  │  Response │  │  - APPL_DB            │  │
│  │  - GetResponse        │  │           │  │  - OC-YANG            │  │
│  │  - SubscribeResponse  │  │           │  │  - OTHERS             │  │
│  └───────────────────────┘  │           │  └───────────────────────┘  │
│                             │           │                             │
└─────────────────────────────┘           └─────────────────────────────┘

Direction: Client initiates connection TO DUT
Transport: Plaintext (noTLS) or TLS
Protocol:  gRPC unary (Get) or streaming (Subscribe)
```

**Roles:**

| Component | Role | Description |
|-----------|------|-------------|
| `gnmi_get` / `gnmic` (External) | gRPC Client | Initiates connection, sends requests |
| `telemetry` (DUT) | gRPC Server | Listens on port 8080, serves data |

---

## Subscribe Mode Support Matrix

| Mode | COUNTERS_DB | CONFIG_DB | STATE_DB | APPL_DB | OTHERS | OC-YANG |
|------|-------------|-----------|----------|---------|--------|---------|
| once | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| poll | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| stream (sample) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| stream (on-change) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| stream (target-defined) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

> Note: Stream mode works with all DB targets using DB path format.
> OC-YANG target only supports `once` and `poll`.

### Stream Mode Explanation

| Stream Mode | Behavior | Who Decides |
|---|---|---|
| `on-change` | Push only when value changes | Client specifies |
| `sample` | Push at fixed interval (regardless of change) | Client specifies interval |
| `target-defined` | Server decides whether to use on-change or sample | Server decides |

> SONiC does **NOT** support `target-defined`. Client must explicitly
> specify `on-change` or `sample`.

---

## Using gnmi_get (inside DUT gnmi container)

### Get Single Counter

```bash
docker exec gnmi gnmi_get -notls -target_addr localhost:8080 \
  -xpath_target COUNTERS_DB \
  -xpath COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS
```

Response:
```
val: <
  string_val: "670"
>
```

### Get All Counters on a Port

```bash
docker exec gnmi gnmi_get -notls -target_addr localhost:8080 \
  -xpath_target COUNTERS_DB \
  -xpath COUNTERS/Ethernet48
```

### Get Counters on All Ports (wildcard)

```bash
docker exec gnmi gnmi_get -notls -target_addr localhost:8080 \
  -xpath_target COUNTERS_DB \
  -xpath "COUNTERS/Ethernet*"
```

### Get Queue Counters

```bash
docker exec gnmi gnmi_get -notls -target_addr localhost:8080 \
  -xpath_target COUNTERS_DB \
  -xpath COUNTERS/Ethernet48/Queues
```

---

## Using gnmi_cli (Subscribe inside DUT)

### Stream On-Change

```bash
docker exec gnmi gnmi_cli -insecure \
  -logtostderr \
  -address localhost:8080 \
  -query_type s \
  -streaming_type ON_CHANGE \
  -q "COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS" \
  -target COUNTERS_DB
```

### Stream Sample (every 2 seconds)

```bash
docker exec gnmi gnmi_cli -insecure \
  -logtostderr \
  -address localhost:8080 \
  -query_type s \
  -streaming_type SAMPLE \
  -q "COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS" \
  -target COUNTERS_DB \
  -sample_interval 2s
```

### Poll (every 10 seconds)

```bash
docker exec gnmi gnmi_cli -insecure \
  -logtostderr \
  -address localhost:8080 \
  -query_type p \
  -pi 10s \
  -q "COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS" \
  -target COUNTERS_DB
```

---

## Using gnmic (External Client)

> Install: https://gnmic.openconfig.net/install/

### Subscribe Once

```bash
gnmic subscribe \
  --address 192.168.8.230:8080 \
  --insecure \
  --mode once \
  --path "COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS" \
  --target COUNTERS_DB \
  --encoding json_ietf \
  --format flat
```

Output:
```
/COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS: 670
```

### Subscribe Stream On-Change

```bash
gnmic subscribe \
  --address 192.168.8.230:8080 \
  --insecure \
  --mode stream \
  --stream-mode on-change \
  --path "COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS" \
  --target COUNTERS_DB \
  --encoding json_ietf \
  --format flat
```

Output (updates only when value changes):
```
/COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS: 670
/COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS: 1340
```

### Subscribe Stream Sample (every 3 seconds)

```bash
gnmic subscribe \
  --address 192.168.8.230:8080 \
  --insecure \
  --mode stream \
  --stream-mode sample \
  --sample-interval 3s \
  --path "COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS" \
  --target COUNTERS_DB \
  --encoding json_ietf \
  --format flat
```

Output (periodic push every 3s):
```
/COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS: 670
/COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS: 670
/COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS: 670
```

### Subscribe All Counters on a Port (Sample)

```bash
gnmic subscribe \
  --address 192.168.8.230:8080 \
  --insecure \
  --mode stream \
  --stream-mode sample \
  --sample-interval 5s \
  --path "COUNTERS/Ethernet48" \
  --target COUNTERS_DB \
  --encoding json_ietf
```

Output (JSON with all SAI_PORT_STAT_* fields):
```json
{
  "source": "192.168.8.230:8080",
  "timestamp": 1779166318804313851,
  "target": "COUNTERS_DB",
  "updates": [{
    "Path": "COUNTERS/Ethernet48",
    "values": {
      "COUNTERS/Ethernet48": {
        "SAI_PORT_STAT_IF_IN_OCTETS": "4883",
        "SAI_PORT_STAT_IF_IN_MULTICAST_PKTS": "21",
        "SAI_PORT_STAT_IF_OUT_OCTETS": "670",
        "SAI_PORT_STAT_IF_OUT_BROADCAST_PKTS": "5",
        "SAI_PORT_STAT_ETHER_IN_PKTS_128_TO_255_OCTETS": "4",
        "SAI_PORT_STAT_ETHER_OUT_PKTS_128_TO_255_OCTETS": "5",
        "..."
      }
    }
  }]
}
```

### Subscribe Poll (OC-YANG)

```bash
gnmic subscribe \
  --address 192.168.8.230:8080 \
  --insecure \
  --mode once \
  --path "/openconfig-interfaces:interfaces/interface[name=Ethernet48]/state/counters" \
  --target OC-YANG \
  --encoding json_ietf
```

> Note: For OC-YANG paths, only `once` and `poll` modes are supported.

---

## Virtual Paths (Wildcard)

SONiC supports virtual paths for COUNTERS_DB:

| Path | Description |
|------|-------------|
| `COUNTERS/Ethernet*` | All counters on all Ethernet ports |
| `COUNTERS/Ethernet*/SAI_PORT_STAT_IF_OUT_OCTETS` | One counter on all ports |
| `COUNTERS/Ethernet48/SAI_PORT_STAT_IF_OUT_OCTETS` | One counter on one port |
| `COUNTERS/Ethernet48/Queues` | Queue stats on one port |
| `COUNTERS/Ethernet*/Queues` | Queue stats on all ports |

All virtual paths support Get, Subscribe (poll and stream).

---

## Comparison: Dial-in vs Dial-out

| | Dial-in (this doc) | Dial-out |
|--|--|--|
| Connection initiator | External client → DUT | DUT → External collector |
| DUT role | gRPC Server | gRPC Client |
| Protocol | Standard gNMI Subscribe | Custom `gnmi.sonic.gNMIDialOut` |
| Client tools | gnmic, gnmi_cli, pygnmi | Custom collector (Python/Go) |
| Stream support | All DB targets (DB path) | All DB targets |
| Configuration | None (always available) | CONFIG_DB `TELEMETRY_CLIENT` |
| TLS | Optional (noTLS mode available) | Required (collector must serve TLS) |
| Use case | On-demand query, debugging | Continuous telemetry export |
