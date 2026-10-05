// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
// Connectors follow the rendered HTML nodes, keeping text readable at every width.
(function(){
 const ns='http://www.w3.org/2000/svg';
 const maps=[...document.querySelectorAll('.diagram-map[data-edges]')];
 function svgEl(tag,attrs){const el=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));return el;}
 function draw(map,index){
  let svg=map.querySelector(':scope > .diagram-links');
  if(!svg){svg=svgEl('svg',{class:'diagram-links','aria-hidden':'true',focusable:'false'});map.prepend(svg);}
  const bounds=map.getBoundingClientRect();if(!bounds.width||!bounds.height)return;
  svg.setAttribute('viewBox',`0 0 ${bounds.width} ${bounds.height}`);svg.replaceChildren();
  const defs=svgEl('defs',{}),marker=svgEl('marker',{id:`map-arrow-${index}`,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:5,markerHeight:5,orient:'auto-start-reverse'});
  marker.append(svgEl('path',{d:'M 1 1 L 9 5 L 1 9 z'}));defs.append(marker);svg.append(defs);
  const dashed=new Set((map.dataset.dashed||'').split(','));
  const edgeSet=new Set(map.dataset.edges.split(','));
  for(const edge of map.dataset.edges.split(',')){
   const [from,to]=edge.split(':');const a=map.querySelector(`[data-node="${from}"]`),b=map.querySelector(`[data-node="${to}"]`);if(!a||!b)continue;
   const ar=a.getBoundingClientRect(),br=b.getBoundingClientRect();
   const ac={x:ar.left-bounds.left+ar.width/2,y:ar.top-bounds.top+ar.height/2};
   const bc={x:br.left-bounds.left+br.width/2,y:br.top-bounds.top+br.height/2};
   const dx=bc.x-ac.x,dy=bc.y-ac.y;
   let sx,sy,tx,ty,c1x,c1y,c2x,c2y;
   if(Math.abs(dy)<Math.min(ar.height,br.height)*.45){
    const sign=Math.sign(dx)||1;sx=ac.x+sign*(ar.width/2+2);sy=ac.y;tx=bc.x-sign*(br.width/2+5);ty=bc.y;
    c1x=(sx+tx)/2;c1y=sy;c2x=c1x;c2y=ty;
   }else{
    const sign=Math.sign(dy)||1;sx=ac.x;sy=ac.y+sign*(ar.height/2+2);tx=bc.x;ty=bc.y-sign*(br.height/2+5);
    c1x=sx;c1y=(sy+ty)/2;c2x=tx;c2y=c1y;
   }
   if(edgeSet.has(`${to}:${from}`)){
    const offset=6;
    if(Math.abs(dy)<Math.min(ar.height,br.height)*.45){const shift=(Math.sign(dx)||1)*offset;sy+=shift;ty+=shift;c1y+=shift;c2y+=shift;}
    else{const shift=(Math.sign(dy)||1)*offset;sx+=shift;tx+=shift;c1x+=shift;c2x+=shift;}
   }
   let curve=`M${sx},${sy} C${c1x},${c1y} ${c2x},${c2y} ${tx},${ty}`;
   // On mobile, route the long agent-to-model edge beside the intervening node.
   if(map.classList.contains('journey-map')&&edge==='agent:model'&&Math.abs(dy)>ar.height*1.6){
    const right=bounds.width+12;curve=`M${ar.right-bounds.left+2},${ac.y} C${right},${ac.y} ${right},${bc.y} ${br.right-bounds.left+5},${bc.y}`;
   }
   const p=svgEl('path',{d:curve,'marker-end':`url(#map-arrow-${index})`,'data-edge':edge});
   if(dashed.has(edge))p.setAttribute('stroke-dasharray','5 5');
   if(a.classList.contains('is-focus')||b.classList.contains('is-focus'))p.classList.add('current-edge');
   svg.append(p);
  }
 }
 let queued=false;function redraw(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;maps.forEach(draw);});}
 const observer=new ResizeObserver(redraw);maps.forEach(m=>observer.observe(m));
 window.updateJourneyDiagram=function(mode,step,title){
  const map=document.querySelector('.journey-map');
  const roles=mode==='native'?['client','env','resources','agent','agent','model','agent','resources','verifier','client']:['client','resources','agent','model','agent','verifier','resources'];
  map.querySelectorAll('[data-node]').forEach(n=>n.classList.toggle('is-focus',n.dataset.node===roles[step]));
  document.getElementById('journey-focus-caption').textContent=`Step ${step+1} · ${title}. The highlight marks the focus of this step. Arrows show component relationships, not measured concurrency.`;
  const length=mode==='native'?nativeSteps.length:observedSteps.length;
  document.querySelector('[data-journey-prev]').disabled=step===0;
  document.querySelector('[data-journey-next]').disabled=step===length-1;
  document.getElementById('journey-step-count').textContent=`${step+1} / ${length}`;
  redraw();
 };
 document.querySelector('[data-journey-prev]').addEventListener('click',()=>document.getElementById('flow-prev').click());
 document.querySelector('[data-journey-next]').addEventListener('click',()=>document.getElementById('flow-next').click());
 updateJourneyDiagram(flowMode,step,(flowMode==='native'?nativeSteps:observedSteps)[step].title);
 if(document.fonts)document.fonts.ready.then(redraw);redraw();
 window.tutorialAudit.diagramCount=document.querySelectorAll('figure.diagram').length;
 window.tutorialAudit.connectorMaps=maps.length;
})();
