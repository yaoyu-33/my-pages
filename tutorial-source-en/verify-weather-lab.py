# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Exercise real loopback HTTP routes without any model, sandbox or cluster."""
import argparse,datetime,hashlib,json,os,platform,socket,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--gym-root',type=Path,required=True);a=p.parse_args()
root=a.gym_root.resolve();here=Path(__file__).resolve().parent
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
base=f'http://127.0.0.1:{port}'
log=(here/'weather-lab.log').open('w')
proc=subprocess.Popen([sys.executable,str(here/'weather-lab.py'),'--gym-root',str(root),'--port',str(port)],stdout=log,stderr=subprocess.STDOUT)
checks=[]
def call(name,route,body=None,method=None):
 data=None if body is None else json.dumps(body).encode()
 request=urllib.request.Request(base+route,data=data,headers={'Content-Type':'application/json'},method=method)
 try:
  with urllib.request.urlopen(request,timeout=5) as r:status=r.status;payload=json.load(r)
 except urllib.error.HTTPError as e:status=e.code;payload=json.load(e)
 result={'name':name,'method':method or ('POST' if data is not None else 'GET'),'path':route,'request':body,'status':status,'response':payload};checks.append(result);return result
try:
 deadline=time.monotonic()+60
 while True:
  if proc.poll() is not None:raise RuntimeError('server exited before ready; see weather-lab.log')
  try:
   with urllib.request.urlopen(base+'/health',timeout=.5) as r:assert r.status==200
   break
  except (urllib.error.URLError,TimeoutError):
   if time.monotonic()>deadline:raise RuntimeError('server readiness timeout')
   time.sleep(.2)
 healthy=call('health','/health');assert healthy['response']=={'status':'ok'}
 valid=call('valid city','/get_weather',{'city':'San Francisco'});assert valid['status']==200;assert valid['response']=={'city':'San Francisco','weather_description':'The weather in San Francisco is cold.'}
 missing=call('missing city','/get_weather',{});assert missing['status']==422;assert any(e['loc']==['body','city'] for e in missing['response']['detail'])
 wrong=call('wrong city type','/get_weather',{'city':7});assert wrong['status']==422
 method=call('GET is not POST','/get_weather');assert method['status']==405
 unknown=call('unregistered route','/get_humidity',{'city':'San Francisco'});assert unknown['status']==404
 fixtures=[json.loads(line) for line in (root/'resources_servers/example_single_tool_call/tests/verifier_cases.jsonl').read_text().splitlines()]
 for f in fixtures:
  result=call('verify: '+f['name'],'/verify',f['request'])
  if 'expected_reward' in f:assert result['status']==200 and result['response']['reward']==f['expected_reward']
  else:assert result['status']==422
 with urllib.request.urlopen(base+'/openapi.json') as r:schema=json.load(r)
 assert '/get_weather' in schema['paths'] and '/verify' in schema['paths']
 (here/'weather-openapi.json').write_text(json.dumps(schema,indent=2)+'\n')
finally:
 proc.terminate()
 try:proc.wait(timeout=10)
 except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
 log.close()
with socket.socket() as sock:closed=sock.connect_ex(('127.0.0.1',port))!=0
assert closed
report={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha':'3ef478df1ee163134d32a3f291f0a9e5981d0e52','app_sha256':hashlib.sha256((root/'resources_servers/example_single_tool_call/app.py').read_bytes()).hexdigest(),'python':platform.python_version(),'os':platform.platform(),'actual_http':True,'startup':'SimpleWeatherResourcesServer.run_webserver() with explicit child config; no Gym parent/Head/model process','checks':checks,'cleanup':{'process_exited':proc.poll() is not None,'port_closed':closed},'scope':'HTTP wiring and fixture verification only; no agent/model rollout','result':'PASS'}
(here/'weather-http-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'result':'PASS','cleanup':report['cleanup']}))
