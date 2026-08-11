# gNMI Dial-out (Subscription)

## Key Points

- DUT's `dialout_client_cli` uses `-insecure` flag = **TLS with skip server cert verification**
- Collector must serve TLS (self-signed cert is fine)
- Config is written to CONFIG_DB; restart dialout service to apply

---

## Architecture

```
┌─────────────────────────────┐          ┌─────────────────────────────┐
│         SONiC DUT           │          │     External Collector      │
│                             │          │                             │
│  ┌───────────────────────┐  │          │  ┌───────────────────────┐  │
│  │   CONFIG_DB           │  │          │  │   collector.py        │  │
│  │  TELEMETRY_CLIENT     │  │          │  │   (gRPC TLS Server)   │  │
│  │  - Global             │  │          │  │                       │  │
│  │  - DestinationGroup   │  │          │  │   Implements:         │  │
│  │  - Subscription       │  │          │  │   gNMIDialOut.Publish │  │
│  └──────────┬────────────┘  │          │  └───────────┬───────────┘  │
│             │               │          │              │              │
│  ┌──────────▼────────────┐  │  gRPC    │              │              │
│  │  dialout_client_cli   │  │  (TLS)   │              │              │
│  │  (gNMI Dial-out       │──┼──────────┼──────────────▶              │
│  │   Client)             │  │  Push     │              │              │
│  │                       │  │  Stream   │  Receives:                 │
│  │  Reads:               │  │          │  SubscribeResponse          │
│  │  - STATE_DB           │  │          │  (Notification + Updates)   │
│  │  - CONFIG_DB          │  │          │                             │
│  │  - COUNTERS_DB        │  │          │                             │
│  │  - APPL_DB            │  │          │                             │
│  └───────────────────────┘  │          └─────────────────────────────┘
│                             │
└─────────────────────────────┘

Direction: DUT pushes data TO collector (unidirectional)
Transport: TLS encrypted (collector provides certificate)
Protocol:  gRPC streaming RPC (gNMIDialOut.Publish)
```

**Roles:**

| Component | Role | Description |
|-----------|------|-------------|
| `dialout_client_cli` (DUT) | gRPC Client | Initiates TLS connection, streams SubscribeResponse |
| `collector.py` (External) | gRPC Server | Listens on TLS port, receives telemetry data |

---

## DUT Configuration

Write directly to CONFIG_DB:

```bash
# Global settings
sudo sonic-db-cli CONFIG_DB HSET "TELEMETRY_CLIENT|Global" \
  encoding JSON_IETF \
  retry_interval 30 \
  src_ip 192.168.3.26 \
  unidirectional true

# Destination Group (collector address)
sudo sonic-db-cli CONFIG_DB HSET "TELEMETRY_CLIENT|DestinationGroup_TEST" \
  dst_addr 192.168.8.193:8081

# Subscription
sudo sonic-db-cli CONFIG_DB HSET "TELEMETRY_CLIENT|Subscription_TEST" \
  dst_group TEST \
  path_target STATE_DB \
  paths TEMPERATURE_INFO,PSU_INFO \
  report_interval 5000 \
  report_type periodic
```

Restart dialout service:

```bash
sudo docker exec gnmi supervisorctl restart dialout
```

---

## Collector Setup

### 1. Generate Self-signed Certificate

```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt \
  -days 365 -nodes -subj "/CN=192.168.8.193"
```

### 2. Install Dependencies

```bash
pip3 install grpcio grpcio-tools protobuf
```

### 3. Compile Proto Files (first time)

Place `gnmi.proto`, `gnmi_ext.proto`, `dial_out.proto` in `proto/` directory, then:

```bash
python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. \
  proto/gnmi.proto proto/gnmi_ext.proto proto/dial_out.proto
```

### 4. collector.py

```python
#!/usr/bin/env python3
"""Minimal gNMI Dial-out Collector (TLS). Prints all updates."""
import json, time, grpc, gnmi_pb2, dial_out_pb2, dial_out_pb2_grpc
from concurrent import futures

class Collector(dial_out_pb2_grpc.gNMIDialOutServicer):
    def Publish(self, request_iterator, context):
        for r in request_iterator:
            if not r.HasField('update'):
                continue
            n = r.update
            target = n.prefix.target
            for u in n.update:
                path = '/'.join(e.name for e in u.path.elem)
                val = (u.val.json_ietf_val or u.val.json_val or b'').decode()
                try:
                    val = json.dumps(json.loads(val), indent=2, ensure_ascii=False)
                except:
                    pass
                print(f"\n[{time.strftime('%H:%M:%S')}] {target} | {path}\n{val}", flush=True)
        return iter([])

srv = grpc.server(futures.ThreadPoolExecutor(4))
dial_out_pb2_grpc.add_gNMIDialOutServicer_to_server(Collector(), srv)
with open('server.key', 'rb') as f: key = f.read()
with open('server.crt', 'rb') as f: crt = f.read()
srv.add_secure_port('0.0.0.0:8081', grpc.ssl_server_credentials([(key, crt)]))
srv.start()
print("gNMI Dialout Collector (TLS) on :8081 - Ctrl+C to stop", flush=True)
try:
    srv.wait_for_termination()
except KeyboardInterrupt:
    print("\nStopped.")
```

### 5. Run

```bash
python3 collector.py
```

---

## Verification

Sample collector output:

```
gNMI Dialout Collector (TLS) on :8081 - Ctrl+C to stop

[04:01:49] STATE_DB | TEMPERATURE_INFO
{
  "CB_temp(0x4B)": {
    "high_threshold": "80.0",
    "temperature": "40.5",
    "warning_status": "False"
  },
  "CPU_Package_temp": {
    "temperature": "49.0"
  }
}

[04:01:49] STATE_DB | PSU_INFO
{
  "PSU 1": {
    "current": "6.875",
    "power": "71.0",
    "voltage": "11.89",
    "model": "YM-1401A-BR"
  }
}
```

### Verify Real-time Updates

```bash
# Manually modify temperature on DUT
sudo sonic-db-cli STATE_DB HSET "TEMPERATURE_INFO|CB_temp(0x4B)" temperature 99.9
```

Collector shows the change in the next 5s cycle:

```
[03:57:49] STATE_DB | TEMPERATURE_INFO
  "CB_temp(0x4B)": {"temperature": "40.5"}    ← before
[03:57:54] STATE_DB | TEMPERATURE_INFO
  "CB_temp(0x4B)": {"temperature": "99.9"}    ← after (next cycle)
```

---

## Configuration Reference

| Parameter | Value | Description |
|-----------|-------|-------------|
| `encoding` | JSON_IETF | Data encoding format |
| `retry_interval` | 30 | Retry interval on connection failure (seconds) |
| `src_ip` | 192.168.3.26 | DUT source IP |
| `unidirectional` | true | One-way push, no PublishResponse expected |
| `dst_addr` | 192.168.8.193:8081 | Collector address (comma-separated for multiple) |
| `path_target` | STATE_DB | Source database |
| `paths` | TEMPERATURE_INFO | Subscribed paths (comma-separated for multiple) |
| `report_interval` | 5000 | Push interval (milliseconds) |
| `report_type` | periodic | periodic / stream / once |

### Tested DB Targets

| DB | Result | Example Path |
|----|--------|-------------|
| STATE_DB | ✅ | PSU_INFO, FAN_INFO, TEMPERATURE_INFO |
| CONFIG_DB | ✅ | PORT |
| APPL_DB | ✅ | PORT_TABLE |
| COUNTERS_DB | ✅ | COUNTERS/Ethernet0, COUNTERS_PORT_NAME_MAP |

---

## DUT Troubleshooting

```bash
# Check dialout status
sudo docker exec gnmi supervisorctl status dialout

# Run dialout manually with debug logs
sudo docker exec gnmi supervisorctl stop dialout
sudo docker exec gnmi /usr/sbin/dialout_client_cli -insecure -logtostderr -v 2
```

---

## TLS Notes

The DUT `dialout_client_cli -insecure` means:

- Uses TLS encryption (not plaintext)
- Skips server certificate verification
- Does NOT present a client certificate

Therefore:

- Collector **must** provide a TLS certificate (self-signed is OK)
- A plaintext gRPC server will cause 30s connection timeout (TLS handshake fails)

---

## Appendix: Proto Files

### proto/dial_out.proto

```protobuf
syntax = "proto3";

import "gnmi.proto";

package gnmi.sonic;

service gNMIDialOut {
  rpc Publish(stream SubscribeResponse) returns (stream PublishResponse);
}

message PublishResponse {
  int64 timestamp = 1;
  Path prefix = 2;
  string alias = 3;
  repeated Path path = 4;
}
```

### proto/gnmi.proto

Source: [openconfig/gnmi](https://github.com/openconfig/gnmi/blob/master/proto/gnmi/gnmi.proto)

Modify the import path before compiling:

```diff
- import "github.com/openconfig/gnmi/proto/gnmi_ext/gnmi_ext.proto";
+ import "gnmi_ext.proto";
```

Or download and patch:

```bash
curl -o proto/gnmi.proto \
  https://raw.githubusercontent.com/openconfig/gnmi/master/proto/gnmi/gnmi.proto
sed -i 's|github.com/openconfig/gnmi/proto/gnmi_ext/||' proto/gnmi.proto
```

### proto/gnmi_ext.proto

Source: [openconfig/gnmi](https://github.com/openconfig/gnmi/blob/master/proto/gnmi_ext/gnmi_ext.proto)

```protobuf
syntax = "proto3";

package gnmi_ext;

option go_package = "github.com/openconfig/gnmi/proto/gnmi_ext";

message Extension {
  oneof ext {
    RegisteredExtension registered_ext = 1;
    MasterArbitration master_arbitration = 2;
  }
}

message RegisteredExtension {
  ExtensionID id = 1;
  bytes msg = 2;
}

enum ExtensionID {
  EID_UNSET = 0;
  EID_EXPERIMENTAL = 999;
}

message MasterArbitration {
  Role role = 1;
  Uint128 election_id = 2;
}

message Uint128 {
  uint64 high = 1;
  uint64 low = 2;
}

message Role {
  string id = 1;
}
```

---

## Generating Python from Proto Files

```bash
python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. \
  proto/gnmi.proto proto/gnmi_ext.proto proto/dial_out.proto
```

| Flag | Purpose |
|------|---------|
| `-I proto` | Proto import search path |
| `--python_out=.` | Generate `*_pb2.py` (message classes) |
| `--grpc_python_out=.` | Generate `*_pb2_grpc.py` (service stubs) |

Generated files:

| File | Source | Content |
|------|--------|---------|
| `gnmi_pb2.py` | gnmi.proto | Message classes (Path, TypedValue, etc.) |
| `gnmi_pb2_grpc.py` | gnmi.proto | gNMI dial-in stubs (not used here) |
| `gnmi_ext_pb2.py` | gnmi_ext.proto | Extension messages (dependency) |
| `gnmi_ext_pb2_grpc.py` | gnmi_ext.proto | Empty (no service) |
| `dial_out_pb2.py` | dial_out.proto | PublishResponse message |
| `dial_out_pb2_grpc.py` | dial_out.proto | `gNMIDialOutServicer` base class |

The collector uses:
- `dial_out_pb2_grpc` — to register the `Publish()` RPC handler
- `gnmi_pb2` — to access `r.update.prefix.target`, `u.path.elem`, `u.val.json_ietf_val`

Re-generation is only needed if proto definitions change.

---

## File Structure

```
dialout-collector/
├── proto/
│   ├── dial_out.proto       # SONiC dial-out service definition
│   ├── gnmi.proto           # OpenConfig gNMI messages
│   └── gnmi_ext.proto       # gNMI extensions (dependency)
├── server.crt               # Self-signed TLS certificate
├── server.key               # TLS private key
├── collector.py             # Dial-out collector script
├── gnmi_pb2.py              # Generated: message classes
├── gnmi_pb2_grpc.py         # Generated: gNMI service stubs
├── gnmi_ext_pb2.py          # Generated: extension messages
├── gnmi_ext_pb2_grpc.py     # Generated: (empty)
├── dial_out_pb2.py          # Generated: PublishResponse
└── dial_out_pb2_grpc.py     # Generated: gNMIDialOutServicer
```
