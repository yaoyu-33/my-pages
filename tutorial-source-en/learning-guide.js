// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
(()=>{
 const items=JSON.parse(document.getElementById('learning-data').textContent);
 for(const item of items){
  const box=document.getElementById('question-'+item.id),out=box.querySelector('.learn-feedback');
  for(const button of box.querySelectorAll('[data-choice]'))button.addEventListener('click',()=>{
   for(const peer of box.querySelectorAll('[data-choice]'))peer.setAttribute('aria-pressed',String(peer===button));
   const correct=Number(button.dataset.choice)===item.answer;
   out.replaceChildren();out.hidden=false;out.dataset.correct=String(correct);
   const title=document.createElement('strong');title.textContent=correct?'Correct! Here is why 🌱':'Take another look at this distinction';
   const text=document.createElement('span');text.textContent=item.feedback;
   const link=document.createElement('a');link.href='#'+item.anchor;link.textContent='Back to the example →';
   link.addEventListener('click',()=>{const target=document.getElementById(item.anchor);for(let p=target;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;});
   out.append(title,text,document.createElement('br'),link);
  });
 }
 document.getElementById('download-async-mini-lab').addEventListener('click',()=>{
  const source=document.getElementById('async-mini-source').textContent;
  const url=URL.createObjectURL(new Blob([source],{type:'text/x-python;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download='async-mini-lab.py';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 });
})();
