#!/usr/bin/env python3
"""Minimal gNMI Dial-out Collector (TLS). Prints all updates."""
import json,time,grpc,gnmi_pb2,dial_out_pb2,dial_out_pb2_grpc
from concurrent import futures

class Collector(dial_out_pb2_grpc.gNMIDialOutServicer):
    def Publish(self, request_iterator, context):
        for r in request_iterator:
            if not r.HasField('update'): continue
            n = r.update
            target = n.prefix.target
            for u in n.update:
                path = '/'.join(e.name for e in u.path.elem)
                val = (u.val.json_ietf_val or u.val.json_val or b'').decode()
                try: val = json.dumps(json.loads(val), indent=2, ensure_ascii=False)
                except: pass
                print(f"\n[{time.strftime('%H:%M:%S')}] {target} | {path}\n{val}", flush=True)
        return iter([])

srv = grpc.server(futures.ThreadPoolExecutor(4))
dial_out_pb2_grpc.add_gNMIDialOutServicer_to_server(Collector(), srv)
with open('server.key','rb') as f: key=f.read()
with open('server.crt','rb') as f: crt=f.read()
srv.add_secure_port('0.0.0.0:8081', grpc.ssl_server_credentials([(key, crt)]))
srv.start()
print("gNMI Dialout Collector (TLS) on :8081 - Ctrl+C to stop", flush=True)
try: srv.wait_for_termination()
except KeyboardInterrupt: print("\nStopped.")
