"""Exercise eight native WebSocket clients through the HTTP room proxy."""
import concurrent.futures
import json
import os
import subprocess
import urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
base = os.environ.get('TEST_SERVER_URL', 'http://127.0.0.1:8080')
request = urllib.request.Request(base+'/api/rooms', data=b'{"capacity":8}', headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request) as response:
    room = json.load(response)
url = base.replace('http://','ws://').replace('https://','wss://')+room['socket']
def run(index):
    result = subprocess.run(['godot','--headless','--audio-driver','Dummy','--path',str(ROOT),'--script','tests/websocket_peer.gd','--',url,str(index)],capture_output=True,text=True,timeout=25)
    if result.returncode or 'ERROR:' in result.stdout+result.stderr:
        raise RuntimeError(result.stdout+result.stderr)
    print(index,result.stdout.strip().splitlines()[-1],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(run,range(8)))
print('Eight WebSocket clients passed')
