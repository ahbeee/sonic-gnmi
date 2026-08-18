# SONiC gNMI Monitor

一個唯讀的 SONiC gNMI 範例程式，用來查詢或訂閱：

- Interface performance counters
- Interface operational status
- PortChannel operational status
- MCLAG session、peer-link 與 member status
- BGP neighbor status
- OSPF neighbor status（SSH polling fallback）
- 光模組插入／移除事件
- Transceiver PM、VDM、LOS、CDR loss-of-lock 與 fault
- Transceiver 告警變化次數及最後 set／clear 時間

程式只執行 gNMI `Get` 或 `Subscribe`，不會修改設備設定。輸出格式為一行一筆 JSON，方便寫入 log 或串接告警系統。

## 環境需求

- Python 3.10 或以上版本
- 電腦能連線到 SONiC gNMI port
- SONiC 使用者帳號及密碼

安裝 Python 套件：

```powershell
python -m pip install -r requirements.txt
```

建議用環境變數提供連線資訊，避免把密碼寫進程式或 Git：

```powershell
$env:SONIC_HOST = "202.39.116.32"
$env:SONIC_GNMI_PORT = "8080"
$env:SONIC_USERNAME = "admin"
$env:SONIC_PASSWORD = Read-Host "SONiC password"
```

如果沒有設定 `SONIC_PASSWORD`，程式執行時會提示輸入密碼，輸入內容不會顯示在畫面上。

> 全域參數必須放在子指令前面，例如 `--host ... counters`，不能寫成 `counters --host ...`。

## 基本語法

```powershell
python .\sonic_monitor.py [連線參數] <command> [command 參數]
```

常用連線參數：

| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `--host` | `202.39.116.31` | SONiC 管理 IP |
| `--port` | `8080` | gNMI TCP port |
| `--username` | `admin` | 登入帳號 |
| `--password` | 環境變數或互動輸入 | 登入密碼 |
| `--tls` | 關閉 | 使用 TLS |
| `--skip-verify` | 關閉 | 測試時略過 TLS 憑證驗證 |

查看全部指令：

```powershell
python .\sonic_monitor.py --help
python .\sonic_monitor.py transceiver-pm --help
```

## 支援功能

| Command | 單次 Get | Polling | gNMI Subscribe |
| --- | ---: | ---: | --- |
| `counters` | ✓ | ✓ | `SAMPLE` |
| `interface-status` | ✓ | ✓ | `ON_CHANGE` |
| `portchannel-status` | ✓ | ✓ | `ON_CHANGE` |
| `mclag-status` | ✓ | ✓ | `ON_CHANGE` |
| `bgp-status` | ✓ | ✓ | `ON_CHANGE` |
| `ospf-status` | ✓ | ✓ | 不支援；使用 SSH polling |
| `modules` | — | ✓ | `ON_CHANGE` |
| `transceiver-pm` | ✓ | — | `SAMPLE` |
| `transceiver-vdm` | ✓ | — | `SAMPLE` |
| `transceiver-status` | ✓ | — | `ON_CHANGE` |
| `transceiver-history` | ✓ | — | — |

`SAMPLE` 會按照 interval 定期送出資料；`ON_CHANGE` 只在設備狀態改變時送出 update。

## Performance counters

查詢一次預設流量、錯誤及丟棄 counters：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  counters --ports Ethernet240
```

每五秒 polling 所有 ports：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  counters --ports all --stream --interval 5
```

使用 gNMI `STREAM + SAMPLE`：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  counters --ports all --subscribe --interval 5
```

指定 counters（可以重複使用 `--counter`）：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  counters --ports Ethernet0,Ethernet240 `
  --counter SAI_PORT_STAT_IF_IN_OCTETS `
  --counter SAI_PORT_STAT_IF_OUT_OCTETS
```

## Interface status

每五秒 polling operation up/down：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  interface-status --ports all --stream --interval 5
```

訂閱 operation status 變化：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  interface-status --ports all --subscribe
```

資料來源：`STATE_DB/PORT_TABLE/<port>/netdev_oper_status`。

## PortChannel status

查詢一次：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  portchannel-status --portchannels all
```

每五秒 polling：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  portchannel-status --portchannels all --stream --interval 5
```

訂閱 operation status 變化：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  portchannel-status --portchannels all --subscribe
```

資料來源：`STATE_DB/LAG_TABLE/<PortChannel>` 的 `admin_status`、`oper_status` 與 `state`。

## MCLAG status

查詢所有 domains 的 session、peer-link 及 member local/remote 狀態：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  mclag-status --domains all
```

每五秒 polling：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  mclag-status --domains all --stream --interval 5
```

使用 gNMI `ON_CHANGE` 訂閱：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  mclag-status --domains all --subscribe
```

診斷原始 notification：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  mclag-status --domains all --subscribe --raw-events
```

輸出的 `scope` 代表：

- `session`：MCLAG domain session
- `peer_link`：peer-link PortChannel
- `member_local`：本機 MCLAG member PortChannel
- `member_remote`：對端回報的 MCLAG member PortChannel

資料來源為 `STATE_DB/MCLAG_TABLE`、`MCLAG_REMOTE_INTF_TABLE` 與
`LAG_TABLE/<PortChannel>`。收到任一 ON_CHANGE update 後，程式會重新比對完整
MCLAG snapshot，因此一次有多個狀態變化時會分別輸出告警。

## BGP neighbor status

查詢所有 BGP neighbors：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  bgp-status --peers all
```

每五秒 polling 指定 peers：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  bgp-status --peers 10.29.32.29,10.31.32.31 `
  --stream --interval 5
```

使用 gNMI `ON_CHANGE` 訂閱 neighbor up/down：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  bgp-status --peers all --subscribe
```

資料來源：`STATE_DB/BGP_NEIGHBOR/<peer>` 的 `status` 與 `update_time`。
SONiC 可能用 `status=down`、空 `{}` 或 Redis key deletion 表示 neighbor down；
程式會將這些格式統一轉成每個 peer 各自一筆告警，並在 `source_event`
標示原始事件類型。
若要診斷設備實際送出的 notification，可加入 `--raw-events`；BGP 訂閱會同時
監聽 table-level path 與啟動時已知的每個 neighbor exact path：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  bgp-status --peers all --subscribe --raw-events
```

## OSPF neighbor status

查詢一次：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  ospf-status
```

每五秒讀取 FRR 狀態並只輸出 neighbor added、removed 或 state change：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  ospf-status --stream --interval 5
```

這個 SONiC 202311.N 映像的 `STATE_DB` 沒有 OSPF table，OpenConfig
`network-instance/protocols` 也沒有回傳 OSPF operational state，因此此 command
透過唯讀 SSH 執行 `vtysh -c 'show ip ospf neighbor json'`，不是 gNMI Subscribe。
如 SSH 不是 TCP 22，可在 command 前指定 `--ssh-port`：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 --ssh-port 2222 `
  ospf-status --stream --interval 5
```

## 光模組插入／移除

每五秒 polling：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  modules --ports all --interval 5
```

使用 gNMI `ON_CHANGE` 訂閱：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  modules --ports all --subscribe
```

資料來源為 `STATE_DB/TRANSCEIVER_INFO`。`transceiver inserted`、`transceiver removed` 與 `severity` 是程式比較狀態後產生的告警文字，不是 SONiC 原始訊息。

## Transceiver PM 與 VDM

查詢 PM，以及可用的 VDM thresholds／flags：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-pm --ports Ethernet248
```

只查 `TRANSCEIVER_PM` table：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-pm --ports Ethernet248 --table-only
```

每五秒以 gNMI `SAMPLE` 訂閱動態 PM 資料：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-pm --ports Ethernet248 --subscribe --interval 5
```

查詢 VDM real values、thresholds 與 flags：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-vdm --ports Ethernet248
```

訂閱 VDM real values：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-vdm --ports Ethernet248 --subscribe --interval 5
```

## LOS、CDR loss-of-lock 與 fault

查詢目前狀態：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-status --ports Ethernet240 --signals-only
```

訂閱狀態變化：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-status --ports Ethernet240 --signals-only --subscribe
```

查詢告警變化次數、最後 set 時間及最後 clear 時間：

```powershell
python .\sonic_monitor.py --host 202.39.116.32 `
  transceiver-history --ports Ethernet240 --table all --signals-only
```

也可以分別指定：

```powershell
--table change-count
--table set-time
--table clear-time
```

相關 STATE_DB tables：

```text
TRANSCEIVER_STATUS_FLAG
TRANSCEIVER_STATUS_FLAG_CHANGE_COUNT
TRANSCEIVER_STATUS_FLAG_SET_TIME
TRANSCEIVER_STATUS_FLAG_CLEAR_TIME
```

## 輸出與告警

所有輸出都是 newline-delimited JSON。例如 interface 從 up 變成 down：

```json
{"kind":"interface_status","message":"interface operational status changed","severity":"warning","port":"Ethernet240","old_status":"up","new_status":"down"}
```

SONiC 經由 gNMI 提供原始 DB update；`message`、`kind`、`severity`、`old_status` 與 `new_status` 是本程式比較前後狀態後加入的欄位。

停止持續監控請按 `Ctrl+C`。

## 已驗證的設備條件

- 測試設備：`202.39.116.31`、`202.39.116.32`
- gNMI endpoint：TCP 8080，plaintext gRPC，username/password metadata
- gNMI version：0.7.0
- Encoding：JSON、JSON-IETF、protobuf
- Counters：`COUNTERS_DB/COUNTERS/<port>/<SAI counter>`
- Interface state：`STATE_DB/PORT_TABLE/<port>`
- PortChannel state：`STATE_DB/LAG_TABLE/<PortChannel>`
- MCLAG：`STATE_DB/MCLAG_TABLE`、`MCLAG_REMOTE_INTF_TABLE`、`LAG_TABLE`
- BGP state：`STATE_DB/BGP_NEIGHBOR/<peer>`
- OSPF state：此映像未提供 gNMI path，使用 FRR SSH polling fallback
- Transceiver：`STATE_DB/TRANSCEIVER_*`
- 此映像不支援 wildcard Get，因此程式會先探索 interface／PortChannel，再查詢 exact paths
- 目前兩台測試設備使用 plaintext port 8080；只有設備確實啟用 TLS 時才應加上 `--tls`

不同 SONiC 版本或硬體平台可能沒有相同的 transceiver tables／fields，部署前應先在目標設備驗證。
