// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
(function(){
 document.querySelectorAll('[data-interaction]').forEach(figure=>{
  const canvas=figure.querySelector('.interaction-canvas'),svg=canvas.querySelector('svg');
  const width=svg.viewBox.baseVal.width;
  figure.querySelectorAll('[data-diagram-size]').forEach(button=>button.addEventListener('click',()=>{
   const fit=button.dataset.diagramSize==='fit';
   canvas.style.width=fit?'100%':`${Math.max(width,1100)}px`;
   canvas.style.minWidth=fit?'0':'720px';
   figure.querySelectorAll('[data-diagram-size]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  }));
 });
})();
