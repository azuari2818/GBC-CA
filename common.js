// Helper bersama: scene three.js, kontrol orbit, raycast, silinder
function makeStage(el, dist, target){
  const W=()=>el.clientWidth, H=()=>el.clientHeight;
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x0b1220);
  const camera=new THREE.PerspectiveCamera(45,W()/H(),0.3,3000);
  const renderer=new THREE.WebGLRenderer({antialias:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.setSize(W(),H()); el.appendChild(renderer.domElement);
  scene.add(new THREE.AmbientLight(0xffffff,0.7));
  const d1=new THREE.DirectionalLight(0xffffff,0.8); d1.position.set(60,120,90); scene.add(d1);
  const d2=new THREE.DirectionalLight(0x88aaff,0.35); d2.position.set(-80,40,-60); scene.add(d2);
  const tgt=new THREE.Vector3(target[0],target[1],target[2]);
  let th=0.55, ph=1.25, rad=dist;
  function upd(){
    camera.position.set(tgt.x+rad*Math.sin(ph)*Math.sin(th), tgt.y+rad*Math.cos(ph), tgt.z+rad*Math.sin(ph)*Math.cos(th));
    camera.lookAt(tgt);
  }
  const api={scene,camera,renderer,frame:null,onClick:null};
  const c=renderer.domElement; let drag=false,moved=0,lx=0,ly=0;
  c.addEventListener('pointerdown',e=>{drag=true;moved=0;lx=e.clientX;ly=e.clientY;c.setPointerCapture(e.pointerId);c.style.cursor='grabbing'});
  c.addEventListener('pointermove',e=>{
    if(!drag)return; const dx=e.clientX-lx, dy=e.clientY-ly; moved+=Math.abs(dx)+Math.abs(dy); lx=e.clientX; ly=e.clientY;
    th-=dx*0.006; ph=Math.min(3.0,Math.max(0.15,ph-dy*0.006)); upd();
  });
  c.addEventListener('pointerup',e=>{drag=false;c.style.cursor='grab'; if(moved<5&&api.onClick)api.onClick(e)});
  c.addEventListener('wheel',e=>{e.preventDefault(); rad=Math.min(700,Math.max(8,rad*(1+Math.sign(e.deltaY)*0.08))); upd()},{passive:false});
  window.addEventListener('resize',()=>{renderer.setSize(W(),H());camera.aspect=W()/H();camera.updateProjectionMatrix()});
  upd();
  (function loop(t){requestAnimationFrame(loop); if(api.frame)api.frame(t/1000); renderer.render(scene,camera)})(0);
  return api;
}
function pick(api,e,objs){
  const r=api.renderer.domElement.getBoundingClientRect();
  const m=new THREE.Vector2(((e.clientX-r.left)/r.width)*2-1, -((e.clientY-r.top)/r.height)*2+1);
  const rc=new THREE.Raycaster(); rc.setFromCamera(m,api.camera);
  const h=rc.intersectObjects(objs,false); return h.length?h[0].object:null;
}
function cyl(a,b,r,mat){
  const A=new THREE.Vector3(a[0],a[1],a[2]), B=new THREE.Vector3(b[0],b[1],b[2]);
  const d=B.clone().sub(A), L=d.length();
  const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,L,16),mat);
  m.position.copy(A.clone().add(B).multiplyScalar(0.5));
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.normalize());
  return m;
}
