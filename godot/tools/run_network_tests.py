#!/usr/bin/env python3
"""Run real ENet host + seven clients + a rejected ninth participant locally."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
run_dir = Path(tempfile.mkdtemp(prefix='reserka-enet-'))
print('Network test results:', run_dir, flush=True)
processes = []
logs = []
environment = os.environ.copy()
for key, folder in [('XDG_DATA_HOME', 'data'), ('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache')]:
    location = run_dir / folder
    location.mkdir()
    environment[key] = str(location)
port = 24673


def launch(name, role, avatar='knight'):
    log = (run_dir / (name+'.log')).open('w')
    logs.append(log)
    command = ['godot', '--headless', '--log-file', str(run_dir / (name+'-engine.log')),
               '--path', str(ROOT), '--script', 'tests/network_peer.gd', '--',
               '--role='+role, '--out='+str(run_dir / (name+'.json')),
               '--port='+str(port), '--avatar='+avatar]
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=environment)
    processes.append((name, process))


try:
    launch('host', 'host')
    start = time.monotonic()
    while 'PASS: host opens' not in (run_dir/'host.log').read_text() and time.monotonic()-start < 8:
        if processes[0][1].poll() is not None:
            raise RuntimeError('Host failed to start: '+(run_dir/'host.log').read_text()[-2500:])
        time.sleep(.05)
    for i, avatar in enumerate(['adventurer', 'spectral', 'crimson', 'knight', 'adventurer', 'spectral', 'crimson'], 1):
        launch('client'+str(i), 'client', avatar)
    start = time.monotonic()
    while 'PASS: seven different' not in (run_dir/'host.log').read_text() and time.monotonic()-start < 15:
        time.sleep(.05)
    launch('overflow', 'overflow')
    deadline = time.monotonic()+25
    while any(p.poll() is None for _, p in processes) and time.monotonic() < deadline:
        time.sleep(.1)
    failed = []
    count = 0
    for name, process in processes:
        if process.poll() is None:
            process.terminate()
            failed.append(name+' timed out')
            continue
        report = run_dir / (name+'.json')
        if process.returncode or not report.exists():
            failed.append(name+' process failed')
        else:
            data = json.loads(report.read_text())
            count += sum(item['passed'] for item in data['checks'])
            if data['failures']:
                failed.append(name+' checks failed')
        print(name, 'exit', process.returncode, flush=True)
        text = (run_dir / (name+'.log')).read_text()
        if process.returncode or 'ERROR:' in text:
            print(text[-5000:], flush=True)
            if 'ERROR:' in text and name+' runtime error' not in failed:
                failed.append(name+' runtime error')
    print('Network checks passed:', count, flush=True)
    if failed:
        raise RuntimeError('; '.join(failed))
finally:
    for _, process in processes:
        if process.poll() is None:
            process.terminate()
    for _, process in processes:
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    for log in logs:
        log.close()
