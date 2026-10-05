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
  example.steps.forEach((s,i)=>{const b=document.createElement('button');b.type='button';b.textContent=String(i+1).padStart(2,'0');b.title=s.title;b.setAttribute('aria-label',`第 ${i+1} 站：${s.title}`);b.setAttribute('aria-current',i===position?'step':'false');b.addEventListener('click',()=>{position=i;render();});byId('app-step-tabs').append(b);});
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
  'valid city':['合法 city → 200','reply','路由匹配、city 校验通过，get_weather 构造对象；HTTP 层返回 JSON。这个实现固定返回 cold。'],
  'missing city':['漏掉 city → 422','validate','输入模型要求 city。FastAPI 在执行 get_weather 之前拒绝请求，并由 HTTP 层返回错误详情。'],
  'wrong city type':['city 写成数字 → 422','validate','这个版本的输入校验不把数字 7 自动当作字符串 city；业务函数尚未执行。以实际 schema 和响应为准。'],
  'GET is not POST':['把 POST 写成 GET → 405','route','路径存在，但没有给它注册 GET。请求停在 HTTP 方法匹配这一步，get_weather 没有执行；HTTP 层返回 405。'],
  'unregistered route':['请求 get_humidity → 404','route','这里没有 /get_humidity 路由。仅在模型 tools 中声明名称，不会自动生成服务端实现。'],
  'verify: weather call':['评分：有工具调用 → reward 1','reply','这份测试输入含 get_weather function_call。评分函数返回 reward=1；这只证明它满足这个评分器的条件。'],
  'verify: text without weather call':['评分：只有文字 → reward 0','reply','HTTP 200 表示接口成功处理了请求；reward=0 表示没有满足评分条件。服务成功和任务得分是两个维度。'],
  'verify: missing response':['评分：缺 response → 422','validate','BaseVerifyRequest 必须含 response。输入校验失败，SimpleWeatherVerifier.verify 尚未执行。']
 };
 const records=evidence.checks.filter(c=>descriptions[c.name]);
 records.forEach((item,i)=>{const o=document.createElement('option');o.value=i;o.textContent=descriptions[item.name][0];byId('app-http-case').append(o);});
 function renderHttp(){const record=records[Number(byId('app-http-case').value)];const [,stop,explanation]=descriptions[record.name];const stopIndex=['route','validate','handler','reply'].indexOf(stop);
  document.querySelectorAll('[data-http-stop]').forEach((node,i)=>{node.classList.toggle('is-passed',i<stopIndex||i===3);node.classList.toggle('is-stopped',i===stopIndex&&record.status>=400);node.classList.toggle('is-pending',i>stopIndex&&i<3);});
  byId('app-http-status-code').textContent=record.status;byId('app-http-status-code').classList.toggle('error',record.status>=400);
  byId('app-http-explain').textContent=explanation;byId('app-http-request-title').textContent=`${record.method} ${record.path}`;
  byId('app-http-request').textContent=record.request===null?'（没有请求正文）':JSON.stringify(record.request,null,2);
  byId('app-http-response').textContent=JSON.stringify(record.response,null,2);
 }
 byId('app-http-case').addEventListener('change',renderHttp);byId('app-http-python').textContent=evidence.python;
 function download(value,type,name){const blob=new Blob([value],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 byId('download-weather-lab').addEventListener('click',()=>download(launcher,'text/x-python;charset=utf-8','weather-lab.py'));
 byId('download-weather-evidence').addEventListener('click',()=>download(JSON.stringify(evidence,null,2)+'\n','application/json','weather-http-evidence.json'));
 render();renderHttp();
 window.tutorialAudit.appReading={examples:examples.length,steps:examples.reduce((n,e)=>n+e.steps.length,0),httpRecords:records.length};
})();
