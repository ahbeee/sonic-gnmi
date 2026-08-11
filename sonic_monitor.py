#!/usr/bin/env python3
"""Small read-only gNMI monitor for SONiC counters and transceiver events."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any, Iterable

from pygnmi.client import gNMIclient


DEFAULT_COUNTERS = (
    "SAI_PORT_STAT_IF_IN_OCTETS",
    "SAI_PORT_STAT_IF_OUT_OCTETS",
    "SAI_PORT_STAT_IF_IN_ERRORS",
    "SAI_PORT_STAT_IF_OUT_ERRORS",
    "SAI_PORT_STAT_IF_IN_DISCARDS",
    "SAI_PORT_STAT_IF_OUT_DISCARDS",
)

TRANSCEIVER_HISTORY_TABLES = {
    "change-count": "TRANSCEIVER_STATUS_FLAG_CHANGE_COUNT",
    "set-time": "TRANSCEIVER_STATUS_FLAG_SET_TIME",
    "clear-time": "TRANSCEIVER_STATUS_FLAG_CLEAR_TIME",
}

VDM_AUX_TABLES = (
    "TRANSCEIVER_VDM_HALARM_THRESHOLD",
    "TRANSCEIVER_VDM_HWARN_THRESHOLD",
    "TRANSCEIVER_VDM_LALARM_THRESHOLD",
    "TRANSCEIVER_VDM_LWARN_THRESHOLD",
    "TRANSCEIVER_VDM_HALARM_FLAG",
    "TRANSCEIVER_VDM_HWARN_FLAG",
    "TRANSCEIVER_VDM_LALARM_FLAG",
    "TRANSCEIVER_VDM_LWARN_FLAG",
)


def log(kind: str, message: str, **fields: Any) -> None:
    record = {
        "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "kind": kind,
        "message": message,
        **fields,
    }
    print(json.dumps(record, ensure_ascii=False), flush=True)


def notifications(response: dict[str, Any]) -> Iterable[tuple[str, Any, bool]]:
    """Yield (path, value, deleted) from pygnmi Get/Subscribe responses."""
    notes = list(response.get("notification", []))
    # pygnmi represents SubscribeResponse.update as a single nested dict.
    if isinstance(response.get("update"), dict):
        notes.append(response["update"])
    for note in notes:
        for update in note.get("update", []):
            yield str(update.get("path", "")), update.get("val"), False
        for path in note.get("delete", []):
            yield str(path), None, True


def discover_ports(gc: gNMIclient) -> list[str]:
    response = gc.get(
        path=["/openconfig-interfaces:interfaces/interface"],
        target="OC-YANG",
        encoding="json_ietf",
    )
    ports: set[str] = set()
    for _, value, _ in notifications(response):
        if not isinstance(value, dict):
            continue
        entries = value.get("openconfig-interfaces:interface", [])
        if isinstance(entries, list):
            for entry in entries:
                name = entry.get("name") if isinstance(entry, dict) else None
                if isinstance(name, str) and re.fullmatch(r"Ethernet\d+", name):
                    ports.add(name)
    if not ports:
        raise RuntimeError("OpenConfig did not return any Ethernet interfaces")
    return sorted(ports, key=lambda name: int(name.removeprefix("Ethernet")))


def selected_ports(gc: gNMIclient, value: str) -> list[str]:
    if value.lower() == "all":
        return discover_ports(gc)
    result = [item.strip() for item in value.split(",") if item.strip()]
    if not result:
        raise ValueError("at least one port is required")
    return result


def selected_portchannels(gc: gNMIclient, value: str) -> list[str]:
    if value.lower() != "all":
        result = [item.strip() for item in value.split(",") if item.strip()]
        if not result:
            raise ValueError("at least one PortChannel is required")
        return result
    response = gc.get(path=["PORTCHANNEL"], target="CONFIG_DB", encoding="json_ietf")
    names: set[str] = set()
    for _, table, deleted in notifications(response):
        if deleted or not isinstance(table, dict):
            continue
        names.update(name for name in table if re.fullmatch(r"PortChannel\d+", name))
    if not names:
        raise RuntimeError("CONFIG_DB did not return any PortChannel entries")
    return sorted(names, key=lambda name: int(name.removeprefix("PortChannel")))


def show_counters(gc: gNMIclient, ports: list[str], names: list[str]) -> None:
    paths = [f"COUNTERS/{port}/{name}" for port in ports for name in names]
    response = gc.get(path=paths, target="COUNTERS_DB", encoding="json_ietf")
    for path, value, deleted in notifications(response):
        log("counter", "counter value", path=path, value=None if deleted else value)


def poll_counters(
    gc: gNMIclient,
    ports: list[str],
    names: list[str],
    interval: float,
    count: int,
) -> None:
    log("status", "counter polling started", ports=ports, interval_seconds=interval)
    cycle = 0
    while count == 0 or cycle < count:
        show_counters(gc, ports, names)
        cycle += 1
        if count == 0 or cycle < count:
            time.sleep(interval)


def subscribe_counters(
    gc: gNMIclient, ports: list[str], names: list[str], interval: float, count: int
) -> None:
    request = {
        "mode": "stream",
        "encoding": "json_ietf",
        "subscription": [
            {
                "path": f"COUNTERS/{port}/{name}",
                "mode": "sample",
                "sample_interval": int(interval * 1_000_000_000),
            }
            for port in ports
            for name in names
        ],
    }
    log("status", "gNMI SAMPLE subscription started", ports=ports, interval_seconds=interval)
    updates = 0
    for response in gc.subscribe2(subscribe=request, target="COUNTERS_DB"):
        for path, value, deleted in notifications(response):
            log("counter", "counter value", path=path, value=None if deleted else value)
            updates += 1
            if count and updates >= count:
                return


def interface_oper_status(fields: Any) -> str | None:
    """Return the operational state exposed by this image's PORT_TABLE."""
    if not isinstance(fields, dict):
        return None
    value = fields.get("netdev_oper_status", fields.get("oper_status"))
    return str(value).strip().lower() if value is not None else None


def show_interface_status(gc: gNMIclient, ports: list[str]) -> None:
    for port in ports:
        path = f"PORT_TABLE/{port}"
        response = gc.get(path=[path], target="STATE_DB", encoding="json_ietf")
        status = None
        for _, value, deleted in notifications(response):
            if not deleted:
                status = interface_oper_status(value)
        log("interface_status", "interface operational status", port=port, oper_status=status)


def poll_interface_status(
    gc: gNMIclient, ports: list[str], interval: float, count: int
) -> None:
    log("status", "interface status polling started", ports=ports, interval_seconds=interval)
    cycle = 0
    while count == 0 or cycle < count:
        show_interface_status(gc, ports)
        cycle += 1
        if count == 0 or cycle < count:
            time.sleep(interval)


def subscribe_interface_status(gc: gNMIclient, ports: list[str], count: int) -> None:
    request = {
        "mode": "stream",
        "encoding": "json_ietf",
        "updates_only": False,
        "subscription": [{"path": "PORT_TABLE", "mode": "on_change"}],
    }
    previous: dict[str, str] = {}
    synchronized = False
    changes = 0
    log("status", "gNMI ON_CHANGE interface status subscription started", ports=ports)
    for response in gc.subscribe2(subscribe=request, target="STATE_DB"):
        for path, value, deleted in notifications(response):
            if deleted or path.strip("/") != "PORT_TABLE" or not isinstance(value, dict):
                continue
            for port, fields in value.items():
                if port not in ports:
                    continue
                new_status = interface_oper_status(fields)
                if new_status is None:
                    continue
                old_status = previous.get(port)
                previous[port] = new_status
                if synchronized and old_status is not None and old_status != new_status:
                    log(
                        "interface_status",
                        "interface operational status changed",
                        severity="info" if new_status == "up" else "warning",
                        port=port,
                        old_status=old_status,
                        new_status=new_status,
                    )
                    changes += 1
        if response.get("sync_response") and not synchronized:
            synchronized = True
            log("status", "initial interface status synchronized", oper_status=previous)
        if count and changes >= count:
            return


def show_portchannel_status(gc: gNMIclient, names: list[str]) -> None:
    for name in names:
        response = gc.get(
            path=[f"LAG_TABLE/{name}"], target="STATE_DB", encoding="json_ietf"
        )
        fields: dict[str, Any] = {}
        for _, value, deleted in notifications(response):
            if not deleted and isinstance(value, dict):
                fields.update(value)
        log(
            "portchannel_status",
            "PortChannel status",
            portchannel=name,
            admin_status=fields.get("admin_status"),
            oper_status=fields.get("oper_status"),
            state=fields.get("state"),
        )


def poll_portchannel_status(
    gc: gNMIclient, names: list[str], interval: float, count: int
) -> None:
    log("status", "PortChannel status polling started", portchannels=names, interval_seconds=interval)
    cycle = 0
    while count == 0 or cycle < count:
        show_portchannel_status(gc, names)
        cycle += 1
        if count == 0 or cycle < count:
            time.sleep(interval)


def subscribe_portchannel_status(gc: gNMIclient, names: list[str], count: int) -> None:
    request = {
        "mode": "stream",
        "encoding": "json_ietf",
        "updates_only": False,
        "subscription": [{"path": "LAG_TABLE", "mode": "on_change"}],
    }
    previous: dict[str, str] = {}
    synchronized = False
    changes = 0
    log("status", "gNMI ON_CHANGE PortChannel subscription started", portchannels=names)
    for response in gc.subscribe2(subscribe=request, target="STATE_DB"):
        for path, value, deleted in notifications(response):
            if deleted or path.strip("/") != "LAG_TABLE" or not isinstance(value, dict):
                continue
            for name, fields in value.items():
                if name not in names or not isinstance(fields, dict):
                    continue
                raw_status = fields.get("oper_status")
                if raw_status is None:
                    continue
                new_status = str(raw_status).strip().lower()
                old_status = previous.get(name)
                previous[name] = new_status
                if synchronized and old_status is not None and old_status != new_status:
                    log(
                        "portchannel_status",
                        "PortChannel operational status changed",
                        severity="info" if new_status == "up" else "warning",
                        portchannel=name,
                        old_status=old_status,
                        new_status=new_status,
                    )
                    changes += 1
        if response.get("sync_response") and not synchronized:
            synchronized = True
            log("status", "initial PortChannel status synchronized", oper_status=previous)
        if count and changes >= count:
            return


def module_inventory(gc: gNMIclient) -> dict[str, dict[str, Any]]:
    """Read all interfaces once and return ports that expose transceiver state."""
    response = gc.get(
        path=["/openconfig-interfaces:interfaces/interface"],
        target="OC-YANG",
        encoding="json_ietf",
    )
    result: dict[str, dict[str, Any]] = {}
    for _, value, _ in notifications(response):
        entries = value.get("openconfig-interfaces:interface", []) if isinstance(value, dict) else []
        for entry in entries if isinstance(entries, list) else []:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name")
            ethernet = entry.get("openconfig-if-ethernet:ethernet", {})
            state = ethernet.get("state", {}) if isinstance(ethernet, dict) else {}
            transceiver = state.get("transceiver") if isinstance(state, dict) else None
            if isinstance(name, str) and isinstance(transceiver, dict):
                result[name] = transceiver
    return result


def transceiver_details(gc: gNMIclient, port: str) -> dict[str, Any]:
    response = gc.get(
        path=[f"TRANSCEIVER_INFO/{port}"], target="STATE_DB", encoding="json_ietf"
    )
    for _, value, _ in notifications(response):
        if isinstance(value, dict):
            return value
    return {}


def show_transceiver_data(
    gc: gNMIclient, ports: list[str], primary_table: str, table_only: bool = False
) -> None:
    """Print PM/VDM values plus the threshold and crossing-flag tables."""
    tables = (primary_table,) if table_only else (primary_table, *VDM_AUX_TABLES)
    kind = "transceiver_pm" if primary_table == "TRANSCEIVER_PM" else "transceiver_vdm"
    for port in ports:
        found = False
        for table in tables:
            path = f"{table}/{port}"
            try:
                response = gc.get(path=[path], target="STATE_DB", encoding="json_ietf")
            except Exception as exc:
                # VDM is module-dependent. Missing optional threshold/flag tables
                # should not prevent the primary PM/VDM values from being shown.
                if table == primary_table:
                    log("error", f"{table} is unavailable", port=port, exception=str(exc))
                continue
            for returned_path, value, deleted in notifications(response):
                if not deleted and isinstance(value, dict) and value:
                    found = True
                    log(kind, "transceiver data", port=port, table=table, path=returned_path, value=value)
        if not found:
            log("warning", "no PM/VDM data returned", port=port, primary_table=primary_table)


def subscribe_transceiver_data(
    gc: gNMIclient,
    ports: list[str],
    primary_table: str,
    interval: float,
    count: int,
) -> None:
    """Sample dynamic PM/VDM values without repeatedly sending static thresholds."""
    request = {
        "mode": "stream",
        "encoding": "json_ietf",
        "updates_only": False,
        "subscription": [
            {
                "path": f"{primary_table}/{port}",
                "mode": "sample",
                "sample_interval": int(interval * 1_000_000_000),
            }
            for port in ports
        ],
    }
    kind = "transceiver_pm" if primary_table == "TRANSCEIVER_PM" else "transceiver_vdm"
    log(
        "status",
        "gNMI SAMPLE transceiver subscription started",
        table=primary_table,
        ports=ports,
        interval_seconds=interval,
    )
    updates = 0
    for response in gc.subscribe2(subscribe=request, target="STATE_DB"):
        for path, value, deleted in notifications(response):
            log(
                kind,
                "transceiver data",
                path=path,
                value=None if deleted else value,
            )
            updates += 1
            if count and updates >= count:
                return


def show_transceiver_status(gc: gNMIclient, ports: list[str], signals_only: bool) -> None:
    for port in ports:
        path = f"TRANSCEIVER_STATUS_FLAG/{port}"
        try:
            response = gc.get(path=[path], target="STATE_DB", encoding="json_ietf")
        except Exception as exc:
            log("error", "transceiver status is unavailable", port=port, exception=str(exc))
            continue
        for returned_path, value, deleted in notifications(response):
            if deleted or not isinstance(value, dict):
                continue
            if signals_only:
                value = {
                    key: item
                    for key, item in value.items()
                    if any(token in key.lower() for token in ("los", "lol", "fault"))
                }
            log(
                "transceiver_status",
                "transceiver status flags",
                port=port,
                path=returned_path,
                value=value,
            )


def show_transceiver_history(
    gc: gNMIclient, ports: list[str], selected_table: str, signals_only: bool
) -> None:
    tables = (
        TRANSCEIVER_HISTORY_TABLES.values()
        if selected_table == "all"
        else (TRANSCEIVER_HISTORY_TABLES[selected_table],)
    )
    for port in ports:
        for table in tables:
            path = f"{table}/{port}"
            try:
                response = gc.get(path=[path], target="STATE_DB", encoding="json_ietf")
            except Exception as exc:
                log("error", "transceiver history is unavailable", port=port, table=table, exception=str(exc))
                continue
            for returned_path, value, deleted in notifications(response):
                if deleted or not isinstance(value, dict):
                    continue
                value = signal_fields(value, signals_only)
                log(
                    "transceiver_history",
                    "transceiver status history",
                    port=port,
                    table=table,
                    path=returned_path,
                    value=value,
                )


def signal_fields(value: dict[str, Any], signals_only: bool) -> dict[str, Any]:
    if not signals_only:
        return value
    return {
        key: item
        for key, item in value.items()
        if any(token in key.lower() for token in ("los", "lol", "fault"))
    }


def flag_is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def subscribe_transceiver_status(
    gc: gNMIclient, ports: list[str], signals_only: bool
) -> None:
    request = {
        "mode": "stream",
        "encoding": "json_ietf",
        "updates_only": False,
        "subscription": [{"path": "TRANSCEIVER_STATUS_FLAG", "mode": "on_change"}],
    }
    previous: dict[str, dict[str, Any]] = {}
    synchronized = False
    log("status", "gNMI ON_CHANGE transceiver-status subscription started", ports=ports)
    for response in gc.subscribe2(subscribe=request, target="STATE_DB"):
        for path, value, deleted in notifications(response):
            if deleted or path.strip("/") != "TRANSCEIVER_STATUS_FLAG":
                continue
            if not isinstance(value, dict):
                continue
            for port, raw_fields in value.items():
                if port not in ports or not isinstance(raw_fields, dict) or not raw_fields:
                    continue
                fields = signal_fields(raw_fields, signals_only)
                old_fields = previous.get(port, {})
                if synchronized:
                    for field, new_value in fields.items():
                        old_value = old_fields.get(field)
                        if old_value is None or str(old_value) == str(new_value):
                            continue
                        raised = flag_is_true(new_value)
                        log(
                            "alarm" if raised else "clear",
                            "transceiver status raised" if raised else "transceiver status cleared",
                            severity="warning" if raised else "info",
                            port=port,
                            field=field,
                            old_value=old_value,
                            new_value=new_value,
                        )
                previous[port] = {**old_fields, **fields}
        if response.get("sync_response") and not synchronized:
            synchronized = True
            log("status", "initial transceiver status synchronized", ports=sorted(previous))


def monitor_modules(gc: gNMIclient, ports: list[str], interval: float, count: int) -> None:
    known_present = set(module_inventory(gc)).intersection(ports)
    log("status", "initial module inventory synchronized", present=sorted(known_present))
    cycle = 0
    while count == 0 or cycle < count:
        if cycle:
            time.sleep(interval)
        current = set(module_inventory(gc)).intersection(ports)
        for port in sorted(known_present - current):
            log("alarm", "transceiver removed", severity="warning", port=port)
        for port in sorted(current - known_present):
            details = transceiver_details(gc, port)
            log(
                "alarm",
                "transceiver inserted",
                severity="info",
                port=port,
                manufacturer=str(details.get("manufacturer", "")).strip(),
                model=str(details.get("model", "")).strip(),
                serial=str(details.get("serial", "")).strip(),
            )
        known_present = current
        cycle += 1


def subscribe_modules(gc: gNMIclient, ports: list[str], count: int) -> None:
    request = {
        "mode": "stream",
        "encoding": "json_ietf",
        "updates_only": False,
        # Subscribe at table level. On this SONiC image, HSET updates are sent
        # to exact key paths, but deletion of a complete Redis key is emitted
        # only on the parent table path as {port: {}}.
        "subscription": [{"path": "TRANSCEIVER_INFO", "mode": "on_change"}],
    }
    present: set[str] = set()
    synchronized = False
    alarms = 0
    log("status", "gNMI ON_CHANGE module subscription started", ports=ports)
    for response in gc.subscribe2(subscribe=request, target="STATE_DB"):
        for path, value, deleted in notifications(response):
            if deleted or path.strip("/") != "TRANSCEIVER_INFO" or not isinstance(value, dict):
                continue
            for port, raw_details in value.items():
                if port not in ports:
                    continue
                details = raw_details if isinstance(raw_details, dict) else {}
                is_present = any(
                    details.get(key) for key in ("manufacturer", "model", "serial", "type")
                )
                if not is_present:
                    was_present = port in present
                    present.discard(port)
                    if synchronized or was_present:
                        log("alarm", "transceiver removed", severity="warning", port=port)
                        alarms += 1
                else:
                    was_present = port in present
                    present.add(port)
                    if synchronized and not was_present:
                        log(
                            "alarm",
                            "transceiver inserted",
                            severity="info",
                            port=port,
                            manufacturer=str(details.get("manufacturer", "")).strip(),
                            model=str(details.get("model", "")).strip(),
                            serial=str(details.get("serial", "")).strip(),
                        )
                        alarms += 1
        if response.get("sync_response") and not synchronized:
            synchronized = True
            log("status", "initial module inventory synchronized", present=sorted(present))
        if count and alarms >= count:
            return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("SONIC_HOST", "202.39.116.31"))
    parser.add_argument("--port", type=int, default=int(os.getenv("SONIC_GNMI_PORT", "8080")))
    parser.add_argument("--username", default=os.getenv("SONIC_USERNAME", "admin"))
    parser.add_argument("--password", default=os.getenv("SONIC_PASSWORD"))
    parser.add_argument(
        "--tls", action="store_true", help="use TLS (default is plaintext/insecure gRPC)"
    )
    parser.add_argument(
        "--skip-verify", action="store_true", help="skip TLS certificate verification (test only)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    counters = subparsers.add_parser("counters", help="read or stream performance counters")
    counters.add_argument("--ports", default="Ethernet240", help="comma list, or 'all'")
    counters.add_argument("--counter", action="append", dest="counter_names")
    counters.add_argument("--stream", action="store_true")
    counters.add_argument("--subscribe", action="store_true", help="use gNMI SAMPLE Subscribe")
    counters.add_argument("--interval", type=float, default=5.0)
    counters.add_argument("--count", type=int, default=0, help="poll cycles; 0 means forever")

    interface_status = subparsers.add_parser(
        "interface-status", help="read or monitor interface operational up/down state"
    )
    interface_status.add_argument("--ports", default="all", help="comma list, or 'all'")
    interface_status.add_argument("--stream", action="store_true", help="poll repeatedly")
    interface_status.add_argument(
        "--subscribe", action="store_true", help="use gNMI ON_CHANGE Subscribe"
    )
    interface_status.add_argument("--interval", type=float, default=5.0)
    interface_status.add_argument(
        "--count", type=int, default=0, help="poll cycles or subscribed changes; 0 means forever"
    )

    portchannel_status = subparsers.add_parser(
        "portchannel-status", help="read or monitor PortChannel operational state"
    )
    portchannel_status.add_argument(
        "--portchannels", default="all", help="comma list, or 'all'"
    )
    portchannel_status.add_argument("--stream", action="store_true", help="poll repeatedly")
    portchannel_status.add_argument(
        "--subscribe", action="store_true", help="use gNMI ON_CHANGE Subscribe"
    )
    portchannel_status.add_argument("--interval", type=float, default=5.0)
    portchannel_status.add_argument(
        "--count", type=int, default=0, help="poll cycles or subscribed changes; 0 means forever"
    )

    modules = subparsers.add_parser("modules", help="alarm on transceiver insert/remove")
    modules.add_argument("--ports", default="all", help="comma list, or 'all'")
    modules.add_argument("--interval", type=float, default=5.0)
    modules.add_argument("--count", type=int, default=0, help="poll cycles; 0 means forever")
    modules.add_argument("--subscribe", action="store_true", help="use gNMI ON_CHANGE Subscribe")

    transceiver_pm = subparsers.add_parser(
        "transceiver-pm", help="read transceiver performance-monitoring values"
    )
    transceiver_pm.add_argument("--ports", default="Ethernet240", help="comma list, or 'all'")
    transceiver_pm.add_argument(
        "--table-only", action="store_true", help="show only the TRANSCEIVER_PM table"
    )
    transceiver_pm.add_argument(
        "--subscribe", action="store_true", help="use gNMI SAMPLE Subscribe"
    )
    transceiver_pm.add_argument("--interval", type=float, default=5.0)
    transceiver_pm.add_argument(
        "--count", type=int, default=0, help="received updates; 0 means forever"
    )

    transceiver_vdm = subparsers.add_parser(
        "transceiver-vdm", help="read transceiver VDM values, thresholds and flags"
    )
    transceiver_vdm.add_argument("--ports", default="Ethernet240", help="comma list, or 'all'")
    transceiver_vdm.add_argument(
        "--table-only", action="store_true", help="show only TRANSCEIVER_VDM_REAL_VALUE"
    )
    transceiver_vdm.add_argument(
        "--subscribe", action="store_true", help="use gNMI SAMPLE Subscribe"
    )
    transceiver_vdm.add_argument("--interval", type=float, default=5.0)
    transceiver_vdm.add_argument(
        "--count", type=int, default=0, help="received updates; 0 means forever"
    )

    transceiver_status = subparsers.add_parser(
        "transceiver-status", help="read transceiver LOS/CDRLOL/fault status flags"
    )
    transceiver_status.add_argument("--ports", default="Ethernet240", help="comma list, or 'all'")
    transceiver_status.add_argument(
        "--signals-only", action="store_true", help="show only LOS, loss-of-lock and fault fields"
    )
    transceiver_status.add_argument(
        "--subscribe", action="store_true", help="use gNMI ON_CHANGE Subscribe"
    )

    transceiver_history = subparsers.add_parser(
        "transceiver-history", help="read transceiver flag count/set/clear history"
    )
    transceiver_history.add_argument("--ports", default="Ethernet240", help="comma list, or 'all'")
    transceiver_history.add_argument(
        "--table",
        choices=("all", *TRANSCEIVER_HISTORY_TABLES),
        default="all",
        help="history table to read",
    )
    transceiver_history.add_argument(
        "--signals-only", action="store_true", help="show only LOS, loss-of-lock and fault fields"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    password = args.password or getpass.getpass(f"Password for {args.username}@{args.host}: ")
    try:
        with gNMIclient(
            target=(args.host, args.port),
            username=args.username,
            password=password,
            insecure=not args.tls,
            skip_verify=args.skip_verify,
            timeout=15,
        ) as gc:
            if args.command == "portchannel-status":
                names = selected_portchannels(gc, args.portchannels)
                if args.subscribe:
                    subscribe_portchannel_status(gc, names, args.count)
                elif args.stream:
                    poll_portchannel_status(gc, names, args.interval, args.count)
                else:
                    show_portchannel_status(gc, names)
                return 0
            ports = selected_ports(gc, args.ports)
            if args.command == "counters":
                names = args.counter_names or list(DEFAULT_COUNTERS)
                if args.subscribe:
                    subscribe_counters(gc, ports, names, args.interval, args.count)
                elif args.stream:
                    poll_counters(gc, ports, names, args.interval, args.count)
                else:
                    show_counters(gc, ports, names)
            elif args.command == "interface-status":
                if args.subscribe:
                    subscribe_interface_status(gc, ports, args.count)
                elif args.stream:
                    poll_interface_status(gc, ports, args.interval, args.count)
                else:
                    show_interface_status(gc, ports)
            elif args.command == "modules":
                if args.subscribe:
                    subscribe_modules(gc, ports, args.count)
                else:
                    monitor_modules(gc, ports, args.interval, args.count)
            elif args.command == "transceiver-pm":
                if args.subscribe:
                    subscribe_transceiver_data(
                        gc, ports, "TRANSCEIVER_PM", args.interval, args.count
                    )
                else:
                    show_transceiver_data(gc, ports, "TRANSCEIVER_PM", args.table_only)
            elif args.command == "transceiver-vdm":
                if args.subscribe:
                    subscribe_transceiver_data(
                        gc, ports, "TRANSCEIVER_VDM_REAL_VALUE", args.interval, args.count
                    )
                else:
                    show_transceiver_data(
                        gc, ports, "TRANSCEIVER_VDM_REAL_VALUE", args.table_only
                    )
            elif args.command == "transceiver-status":
                if args.subscribe:
                    subscribe_transceiver_status(gc, ports, args.signals_only)
                else:
                    show_transceiver_status(gc, ports, args.signals_only)
            else:
                show_transceiver_history(gc, ports, args.table, args.signals_only)
        return 0
    except KeyboardInterrupt:
        log("status", "stopped by user")
        return 130
    except Exception as exc:
        log("error", str(exc), exception=type(exc).__name__)
        return 1


if __name__ == "__main__":
    sys.exit(main())
