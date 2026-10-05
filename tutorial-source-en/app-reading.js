// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
(function(){
 const examples=JSON.parse(document.getElementById('app-reading-data').textContent);
 const evidence=JSON.parse(document.getElementById('weather-http-evidence').textContent);
 const launcher=JSON.parse(document.getElementById('weather-launcher-data').textContent);
 const byId=id=>document.getElementById(id);
 let kind='resources',position=0;
 function render(){
  const example=examples.find(e=>e.id===kind),item=example.steps[position];
  document.querySelectorAll('[data-app-kind]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.appKind===kind)));
  byId('app-kind-description').textContent=example.description;
  byId('app-step-tabs').replaceChildren();
  example.steps.forEach((s,i)=>{const b=document.createElement('button');b.type='button';b.textContent=String(i+1).padStart(2,'0');b.title=s.title;b.setAttribute('aria-label',`Step ${i+1}: ${s.title}`);b.setAttribute('aria-current',i===position?'step':'false');b.addEventListener('click',()=>{position=i;render();});byId('app-step-tabs').append(b);});
  byId('app-source').href=`https://github.com/NVIDIA-NeMo/Gym/blob/${evidence.source_sha}/${item.file}#L${item.start}`;
  byId('app-file-name').textContent=`${item.file} · L${item.start}–${item.end}`;
  const code=byId('app-code').querySelector('code');code.replaceChildren();
  item.lines.forEach((value,index)=>{const number=item.start+index;const line=document.createElement('span');line.className='app-code-line'+(item.focus.includes(number)?' is-highlight':'');line.dataset.line=number;const no=document.createElement('span');no.className='app-line-no';no.setAttribute('aria-hidden','true');no.textContent=number;const text=document.createElement('span');text.className='app-line-text';text.textContent=value||' ';line.append(no,text);code.append(line);});
  byId('app-code').scrollTop=0;
  byId('app-step-label').textContent=`READ ALONG / ${position+1} OF ${example.steps.length}`;
  byId('app-step-title').textContent=item.title;
  byId('app-explain').replaceChildren(...item.explain.map(t=>{const p=document.createElement('p');p.textContent=t;return p;}));
  byId('app-mental-text').textContent=item.mental;
  byId('app-question-title').textContent=item.question;
  byId('app-answer').textContent=item.answer;byId('app-question').open=false;
  byId('app-read-prev').disabled=position===0;byId('app-read-next').disabled=position===example.steps.length-1;
  byId('app-read-counter').textContent=`${position+1} / ${example.steps.length}`;
 }
 document.querySelectorAll('[data-app-kind]').forEach(b=>b.addEventListener('click',()=>{kind=b.dataset.appKind;position=0;render();}));
 byId('app-read-prev').addEventListener('click',()=>{if(position>0){position--;render();}});
 byId('app-read-next').addEventListener('click',()=>{if(position<examples.find(e=>e.id===kind).steps.length-1){position++;render();}});
 const descriptions={
  'valid city':['Valid city → 200','reply','The route matches and city passes validation. get_weather builds an object, and the HTTP layer returns JSON. This implementation always returns cold.'],
  'missing city':['Missing city → 422','validate','The input model requires city. FastAPI rejects the request before get_weather runs. The HTTP layer returns error details.'],
  'wrong city type':['Numeric city → 422','validate','In this version, input validation does not convert the number 7 to a city string. The handler has not run. Check the actual schema and response.'],
  'GET is not POST':['Use GET instead of POST → 405','route','The path exists, but no GET method is registered. Method matching fails before get_weather runs. The HTTP layer returns 405.'],
  'unregistered route':['Request get_humidity → 404','route','There is no /get_humidity route. Declaring a name in the model tools does not create a server implementation.'],
  'verify: weather call':['Scoring: tool call → reward 1','reply','This test input contains a get_weather function_call. The verifier returns reward=1. This only proves that the output meets this verifier’s condition.'],
  'verify: text without weather call':['Scoring: text only → reward 0','reply','HTTP 200 means the endpoint handled the request successfully. reward=0 means the scoring condition was not met. Service success and task score are separate outcomes.'],
  'verify: missing response':['Scoring: missing response → 422','validate','BaseVerifyRequest requires response. Input validation fails before SimpleWeatherVerifier.verify runs.']
 };
 const records=evidence.checks.filter(c=>descriptions[c.name]);
 records.forEach((item,i)=>{const o=document.createElement('option');o.value=i;o.textContent=descriptions[item.name][0];byId('app-http-case').append(o);});
 function renderHttp(){const record=records[Number(byId('app-http-case').value)];const [,stop,explanation]=descriptions[record.name];const stopIndex=['route','validate','handler','reply'].indexOf(stop);
  document.querySelectorAll('[data-http-stop]').forEach((node,i)=>{node.classList.toggle('is-passed',i<stopIndex||i===3);node.classList.toggle('is-stopped',i===stopIndex&&record.status>=400);node.classList.toggle('is-pending',i>stopIndex&&i<3);});
  byId('app-http-status-code').textContent=record.status;byId('app-http-status-code').classList.toggle('error',record.status>=400);
  byId('app-http-explain').textContent=explanation;byId('app-http-request-title').textContent=`${record.method} ${record.path}`;
  byId('app-http-request').textContent=record.request===null?'(no request body)':JSON.stringify(record.request,null,2);
  byId('app-http-response').textContent=JSON.stringify(record.response,null,2);
 }
 byId('app-http-case').addEventListener('change',renderHttp);byId('app-http-python').textContent=evidence.python;
 function download(value,type,name){const blob=new Blob([value],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 byId('download-weather-lab').addEventListener('click',()=>download(launcher,'text/x-python;charset=utf-8','weather-lab.py'));
 byId('download-weather-evidence').addEventListener('click',()=>download(JSON.stringify(evidence,null,2)+'\n','application/json','weather-http-evidence.json'));
 render();renderHttp();
 window.tutorialAudit.appReading={examples:examples.length,steps:examples.reduce((n,e)=>n+e.steps.length,0),httpRecords:records.length};
})();
