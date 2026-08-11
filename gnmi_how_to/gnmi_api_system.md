# gNMI API - System Management


## OpenConfig YANG (`xpath_target: OC-YANG`)

---

### Get/Set System Hostname

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-system:system/config
```

Response:
```json
{"openconfig-system:config": {"hostname": "as4630-54npe-2"}}
```

Set hostname:
```bash
gnmi_set -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -update /openconfig-system:system/config:@./hostname.json
```

hostname.json:
```json
{"openconfig-system:config": {"hostname": "my-switch"}}
```

---

### sFlow (OpenConfig)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /openconfig-sampling-sflow:sampling/sflow
```

---

## SONiC YANG (`xpath_target: OC-YANG`)

---

### NTP Server

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-system-ntp:sonic-system-ntp
```

---

### Logging Server

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-system-logging:sonic-system-logging
```

---

### Device Metadata

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OC-YANG \
  -xpath /sonic-device-metadata:sonic-device-metadata
```

---

### Other System Modules

```bash
gnmi_get ... -xpath /sonic-image-management:sonic-image-management
gnmi_get ... -xpath /sonic-mirror:sonic-mirror
gnmi_get ... -xpath /sonic-sflow:sonic-sflow
gnmi_get ... -xpath /sonic-flex-counter:sonic-flex-counter
gnmi_get ... -xpath /sonic-mgmt-interface:sonic-mgmt-interface
gnmi_get ... -xpath /sonic-drop-counter:sonic-drop-counter
gnmi_get ... -xpath /sonic-kdump:sonic-kdump
gnmi_get ... -xpath /sonic-banner:sonic-banner
gnmi_get ... -xpath /sonic-serial-console:sonic-serial-console
```

---

## Non-YANG Paths

---

### PSU Information (`xpath_target: STATE_DB`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target STATE_DB \
  -xpath /PSU_INFO
```

Response (per PSU):
```json
{
  "PSU 1": {
    "current": "1.265",
    "led_status": "green",
    "max_power": "1200.0",
    "model": "YPEB1200AM",
    "power": "68.0",
    "presence": "true",
    "serial": "SB020X181951000070",
    "status": "true",
    "temp": "30.0",
    "voltage": "54.062"
  }
}
```

---

### FAN Information (`xpath_target: STATE_DB`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target STATE_DB \
  -xpath /FAN_INFO
```

Response (per FAN):
```json
{
  "FAN-1": {
    "direction": "exhaust",
    "drawer_name": "FanTray1",
    "led_status": "green",
    "presence": "True",
    "speed": "77",
    "speed_target": "75",
    "status": "True"
  }
}
```

---

### Temperature Information (`xpath_target: STATE_DB`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target STATE_DB \
  -xpath /TEMPERATURE_INFO
```

Response (per sensor):
```json
{
  "CB_temp(0x4B)": {
    "high_threshold": "80.0",
    "temperature": "35.0",
    "warning_status": "False"
  }
}
```

---

### CPU Utilization (`xpath_target: OTHERS`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OTHERS \
  -xpath /platform/cpu
```

Response:
```json
{
  "cpu_all": {"id": "cpu", "100ms": 19, "1s": 23, "5s": 18, "1min": 20, "5min": 20},
  "cpus": [
    {"id": "cpu0", "100ms": 40, "1s": 18, "5s": 15, "1min": 23, "5min": 22}
  ]
}
```

---

### Memory Information (`xpath_target: OTHERS`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OTHERS \
  -xpath /proc/meminfo
```

Response (key fields, unit: KB):
```json
{"mem_total": 15888528, "mem_free": 11131324, "mem_available": 12698084}
```

---

### System Load Average (`xpath_target: OTHERS`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OTHERS \
  -xpath /proc/loadavg
```

Response:
```json
{"last1min": 4.31, "last5min": 4.01, "last15min": 3.39, "process_running": 3, "process_total": 804}
```

---

### OS Version (`xpath_target: OTHERS`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OTHERS \
  -xpath /osversion/build
```

Response:
```json
{"build_version": "sonic.Edgecore-SONiC_202311.6_ec202311_807", "error": ""}
```

---

### System Uptime (`xpath_target: OTHERS`)

```bash
gnmi_get -notls -target_addr localhost:8080 -xpath_target OTHERS \
  -xpath /proc/uptime
```

Response (unit: seconds):
```json
{"total": 2360.33, "idle": 7062.46}
```

---

## Not Supported

| Module |
|--------|
| `/openconfig-procmon:processes` |
| `/sonic-system-service:sonic-system-service` |
| `/sonic-config-mgmt:sonic-config-mgmt` |
