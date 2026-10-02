const DATA=__DATA__, SCALE=__SCALE__, AX=34;   // AX = tinggi sumbu optik (cm)
const st=makeStage(document.getElementById('view'),175,[0,32,0]);
const G=new THREE.Group(); G.scale.setScalar(SCALE); st.scene.add(G);
const grid=new THREE.GridHelper(300,30,0x334155,0x1e293b); grid.position.y=-0.05; st.scene.add(grid);
const mat=(c,o=1,m=0.3,r=0.5)=>new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:m,transparent:o<1,opacity:o});
const picks=[];
function P(mesh,id){mesh.userData.id=id;mesh.userData.em=mesh.material.emissive.getHex();G.add(mesh);picks.push(mesh);return mesh}
function N(mesh){G.add(mesh);return mesh}
const bx=(w,h,d,x,y,z,m)=>{const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);return o};
const cy=(r,h,x,y,z,m,ax)=>{const o=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,28),m);o.position.set(x,y,z);if(ax==='x')o.rotation.z=Math.PI/2;if(ax==='z')o.rotation.x=Math.PI/2;return o};
function house(w,h,d,x,y,z,c,o){
  const m=bx(w,h,d,x,y,z,mat(c,o,0,1)); m.material.depthWrite=false; N(m);
  const e=new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),new THREE.LineBasicMaterial({color:0x64748b})); e.position.copy(m.position); N(e);
}
// --- rangka instrumen (84 x 48 x 50 cm, perkiraan) ---
N(bx(84,20,48,0,10,0,mat(0xcbd5e1,1,0.2,0.6)));
house(30,30,48,-27,35,0,0x60a5fa,0.10);   // rumah lampu
house(24,30,48,0,35,0,0x93c5fd,0.06);     // kompartemen sampel / nyala
house(30,30,48,27,35,0,0x60a5fa,0.10);    // rumah monokromator + detektor
house(22,18,24,25,AX,0,0x1e40af,0.25);    // monokromator
// --- jalur cahaya ---
const beamM=new THREE.MeshBasicMaterial({color:0xfde047,transparent:true,opacity:0.8});
[[[-10.5,AX,0],[14,AX,0]],[[14,AX,0],[25,AX,-8.6]],[[25,AX,-8.6],[36,AX,0]]].forEach(b=>N(cyl(b[0],b[1],0.3,beamM)));
// --- turret + HCL ---
P(cy(4.5,6,-26,AX,0,mat(0x475569),'y'),'turret');
[0,90,180,270].forEach(a=>{
  const r=a*Math.PI/180, dx=Math.cos(r), dz=Math.sin(r);
  P(cyl([-26+dx*3.5,AX,dz*3.5],[-26+dx*15.5,AX,dz*15.5],1.9,mat(a===0?0xfbbf24:0xe5e7eb,1,0.6,0.3)),'hcl');
});
P(cy(2.2,9,-26,AX,-19.5,mat(0x38bdf8,1,0.4,0.3),'x'),'d2');
// --- spray chamber, nebulizer, burner, nyala ---
P(cy(4.5,20,0,25.5,0,mat(0x9ca3af,1,0.5,0.4),'z'),'spray');
P(cy(1.6,6,0,25.5,13,mat(0xf59e0b),'z'),'nebu');
P(cy(2,3,0,29,0,mat(0x6b7280),'y'),'burner');
P(bx(10,2,1.2,0,31.5,0,mat(0x374151,1,0.6,0.4)),'burner');
const flM=mat(0xfb923c,0.75); flM.emissive.setHex(0xfb923c);
const fl=new THREE.Mesh(new THREE.SphereGeometry(1,24,16),flM); fl.position.set(0,36,0); fl.scale.set(5.5,4,1.4); P(fl,'flame');
const coreM=mat(0x60a5fa,0.8); coreM.emissive.setHex(0x3b82f6);
const core=new THREE.Mesh(new THREE.SphereGeometry(1,20,12),coreM); core.position.set(0,33.4,0); core.scale.set(4.5,1.6,0.9); N(core);
// --- cerobong ---
const hoodM=mat(0x94a3b8,1,0.5,0.5); hoodM.side=THREE.DoubleSide;
P(new THREE.Mesh(new THREE.CylinderGeometry(5,9,8,28,1,true),hoodM),'hood').position.set(0,46,0);
P(new THREE.Mesh(new THREE.CylinderGeometry(4,4,20,28,1,true),hoodM),'hood').position.set(0,60,0);
// --- wadah sampel + kapiler ---
P(cy(3.5,8,0,4,32,mat(0xe0f2fe,0.3,0.1,0.1)),'sample');
P(cy(3.2,5,0,3,32,mat(0x38bdf8,0.85,0.1,0.2)),'sample');
P(cyl([0,25.5,16],[0,25.5,32],0.35,mat(0xf1f5f9)),'sample');
P(cyl([0,25.5,32],[0,4,32],0.35,mat(0xf1f5f9)),'sample');
// --- drain ---
P(cy(4,12,0,6,-34,mat(0xf87171,0.5,0.1,0.3)),'drain');
P(cyl([0,22,-10],[0,22,-34],0.5,mat(0xfca5a5)),'drain');
P(cyl([0,22,-34],[0,10,-34],0.5,mat(0xfca5a5)),'drain');
// --- panel gas ---
P(bx(22,10,1.5,-28,10,24.75,mat(0x1f2937,1,0.4,0.5)),'gas');
[[-34,0xef4444],[-28,0x9ca3af],[-22,0x3b82f6]].forEach(k=>P(cy(1.6,2,k[0],10,26,mat(k[1]),'z'),'gas'));
// --- monokromator + detektor ---
[14,36].forEach(x=>[-1,1].forEach(sg=>P(bx(0.6,4,1,x,AX,sg*1,mat(0xfacc15)),'slit')));
P(bx(6,6,0.8,25,AX,-9,mat(0xa78bfa,1,0.8,0.2)),'grating');
P(cy(3,6,39,AX,0,mat(0xd97706,1,0.5,0.4),'x'),'pmt');

// --- interaksi UI ---
const T=document.getElementById('T'), D=document.getElementById('D'), LIST=document.getElementById('list');
function select(id){
  picks.forEach(m=>m.material.emissive.setHex(m.userData.id===id?0x1d4ed8:m.userData.em));
  const d=DATA.find(x=>x.id===id);
  T.textContent=d.nama; D.innerHTML='<p style="margin:6px 0">'+d.fungsi+'</p><p style="margin:6px 0;color:#fcd34d"><b>Catatan:</b> '+d.catatan+'</p>';
  document.querySelectorAll('.item').forEach(e=>e.classList.toggle('on',e.dataset.id===id));
}
DATA.forEach(d=>{const b=document.createElement('button');b.className='item';b.dataset.id=d.id;b.textContent=d.nama;b.onclick=()=>select(d.id);LIST.appendChild(b)});
const cv=st.renderer.domElement;
cv.addEventListener('pointermove',e=>{if(e.buttons)return; cv.style.cursor=pick(st,e,picks)?'pointer':'grab'});
st.onClick=e=>{const o=pick(st,e,picks); if(o)select(o.userData.id)};
st.frame=t=>{
  fl.scale.set(5.5,4*(1+0.07*Math.sin(t*18)),1.4);
  core.scale.set(4.5,1.6*(1+0.05*Math.sin(t*22)),0.9);
  beamM.opacity=0.65+0.2*Math.sin(t*5);
};
select('hcl');
