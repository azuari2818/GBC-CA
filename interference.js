const SC=__SC__;
const st=makeStage(document.getElementById('view'),40,[0,-1,0]);
const RAD={Ca:1.00,Sr:1.18,La:1.03,P:1.07,O:0.66,N:0.71,C:0.76};
const COL={Ca:0x14b8a6,Sr:0x84cc16,La:0xa855f7,P:0xf59e0b,O:0xef4444,N:0x4f46e5,C:0x9ca3af};
const ION=0x14b8a6, ATOM=0xccfbf1;
const mk=(c,o=1)=>new THREE.MeshStandardMaterial({color:c,roughness:0.35,metalness:0.1,transparent:true,opacity:o});
function atom(el,p,g){const m=new THREE.Mesh(new THREE.SphereGeometry(RAD[el],28,20),mk(COL[el]));m.position.set(p[0],p[1],p[2]);g.add(m);return m}
function bond(a,b,g){g.add(cyl(a,b,0.14,mk(0xe5e7eb)))}
const TET=[[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]].map(v=>v.map(k=>k*0.889));
const EL=[[-1.3,0,2.3],[1.3,0,2.3],[-2.3,1.2,-0.6],[-2.3,-1.2,-0.6],[2.3,1.2,-0.6],[2.3,-1.2,-0.6]]; // N,N,O,O,O,O
const B={
  Ca:()=>{const g=new THREE.Group();return {g,main:atom('Ca',[0,0,0],g)}},
  La:()=>{const g=new THREE.Group();atom('La',[0,0,0],g);return {g}},
  Sr:()=>{const g=new THREE.Group();atom('Sr',[0,0,0],g);return {g}},
  PO4:()=>{const g=new THREE.Group();atom('P',[0,0,0],g);TET.forEach(p=>{atom('O',p,g);bond([0,0,0],p,g)});return {g}},
  EDTA:()=>{const g=new THREE.Group();const C1=[-0.76,0,3.55],C2=[0.76,0,3.55];
    atom('N',EL[0],g);atom('N',EL[1],g);atom('C',C1,g);atom('C',C2,g);
    bond(EL[0],C1,g);bond(C1,C2,g);bond(C2,EL[1],g);
    [[0,2],[0,3],[1,4],[1,5]].forEach(k=>{const a=EL[k[0]],b=EL[k[1]];
      const c=a.map((v,i)=>v+0.4*(b[i]-v)), cc=a.map((v,i)=>v+0.75*(b[i]-v));
      atom('C',c,g);atom('C',cc,g);atom('O',b,g);bond(a,c,g);bond(c,cc,g);bond(cc,b,g)});
    return {g}},
  LINES:()=>{const g=new THREE.Group();EL.forEach(p=>g.add(cyl([0,0,0],p,0.07,mk(0x5eead4))));return {g}},
  SHELL:()=>{const g=new THREE.Group();g.add(new THREE.Mesh(new THREE.SphereGeometry(6.2,32,24),mk(0x94a3b8)));return {g}},
  BEAM:()=>{const g=new THREE.Group();g.add(cyl([-16,0.4,0],[16,0.4,0],0.22,new THREE.MeshBasicMaterial({color:0xa78bfa,transparent:true})));return {g}}
};
const s=(p,o=1,c,gl)=>({p:p,o:o,c:c,gl:gl});
const I=p=>s(p,1,ION), A=p=>s(p,1,ATOM,0.5), Z=p=>s(p,0), V=[0,0,0];
const BEAM=['BEAM',[Z(V),Z(V),s(V,1)]];
const CAF=[[[-8,5,3],[-3,3.5,1],[-3,0.4,0.4]],[[7,-4,-5],[2,4,-2],[0.5,-0.3,-0.4]],[[-2,7,-8],[5,3,2],[4,0.4,0.2]]];
const CA3=CAF.map(a=>['Ca',[I(a[0]),I(a[1]),A(a[2])]]);
const clu=[[0,0,1.5],[0,0,-1.5],[0,1.8,-0.2]];
const at=(p,c)=>[p[0]+c[0],p[1]+c[1],p[2]+c[2]];
const same=p=>[s(p),s(p),s(p)];
const SCN={
 none:{t:'Tanpa aditif: gangguan fosfat',eq:'3 Ca²⁺ + 2 PO₄³⁻ → Ca₃(PO₄)₂ (padatan refraktori)',
  items:[['Ca',[I([-8,5,3]),I(clu[0]),I(clu[0])]],['Ca',[I([7,-4,-5]),I(clu[1]),I(clu[1])]],['Ca',[I([-2,7,-8]),I(clu[2]),I(clu[2])]],
   ['PO4',[s([-9,-5,-4]),s([-3,0,0]),s([-3,0,0])]],['PO4',[s([8,5,6]),s([3,0,0]),s([3,0,0])]],
   ['SHELL',[s(V,0),s(V,0),s(V,0.2)]],BEAM],
  cap:[['Larutan sampel','Ion Ca²⁺ dan fosfat (PO₄³⁻) masih tersebar bebas di dalam larutan sampel.'],
       ['Terbentuk senyawa sukar menguap','Saat aerosol memasuki nyala, Ca²⁺ berikatan dengan fosfat membentuk Ca₃(PO₄)₂ / kalsium pirofosfat yang refraktori (titik leleh sangat tinggi).'],
       ['Atomisasi tidak sempurna','Partikel padat sulit teratomisasi, sehingga atom Ca bebas yang menyerap 422,7 nm sedikit. Absorbansi turun (interferensi kimia negatif).']]},
 la:{t:'+ La³⁺ (releasing agent)',eq:'La³⁺ + PO₄³⁻ → LaPO₄  (Ca²⁺ dibebaskan)',
  items:CA3.concat([['PO4',[s([-9,-5,-4]),s([-6,-5,0]),s([-6,-5,0])]],['PO4',[s([8,5,6]),s([6,-5,0]),s([6,-5,0])]],
   ['La',[s([-5,-8,6]),s([-6,-2.1,0]),s([-6,-2.1,0])]],['La',[s([9,-6,-3]),s([6,-2.1,0]),s([6,-2.1,0])]],['La',[s([0,-9,0]),s([0,-8,5]),s([0,-8,5])]],BEAM]),
  cap:[['Aditif ditambahkan','La³⁺ dalam jumlah berlebih ditambahkan ke blanko, standar, dan sampel (umumnya sekitar 0,1–1% b/v). Satu ion La³⁺ ekstra digambarkan sebagai kelebihan.'],
       ['La³⁺ mengikat fosfat','La³⁺ bereaksi lebih dulu dengan fosfat membentuk LaPO₄ yang lebih stabil. Fosfat "terambil", sehingga Ca²⁺ tetap bebas.'],
       ['Ca teratomisasi','Di nyala, Ca bebas menjadi atom Ca⁰ dan menyerap radiasi 422,7 nm dari HCL. Absorbansi kembali normal.']]},
 sr:{t:'+ Sr²⁺ (releasing agent)',eq:'3 Sr²⁺ + 2 PO₄³⁻ → Sr₃(PO₄)₂  (Ca²⁺ dibebaskan)',
  items:CA3.concat([['PO4',[s([-9,-5,-4]),s([-3,-5.5,0]),s([-3,-5.5,0])]],['PO4',[s([8,5,6]),s([3,-5.5,0]),s([3,-5.5,0])]],
   ['Sr',[s([-5,-8,6]),s(at(clu[0],[0,-5.5,0])),s(at(clu[0],[0,-5.5,0]))]],['Sr',[s([9,-6,-3]),s(at(clu[1],[0,-5.5,0])),s(at(clu[1],[0,-5.5,0]))]],
   ['Sr',[s([0,-9,0]),s(at(clu[2],[0,-5.5,0])),s(at(clu[2],[0,-5.5,0]))]],['Sr',[s([6,-9,5]),s([7,-9,5]),s([7,-9,5])]],BEAM]),
  cap:[['Aditif ditambahkan','Sr²⁺ dalam jumlah berlebih ditambahkan ke blanko, standar, dan sampel (umumnya sekitar 0,1–1% b/v). Satu ion Sr²⁺ ekstra digambarkan sebagai kelebihan.'],
       ['Sr²⁺ bersaing mengikat fosfat','Sr²⁺ yang berlebih lebih dahulu mengikat fosfat (membentuk Sr₃(PO₄)₂), sehingga Ca²⁺ tidak terperangkap dan tetap bebas.'],
       ['Ca teratomisasi','Di nyala, Ca bebas menjadi atom Ca⁰ dan menyerap radiasi 422,7 nm dari HCL. Absorbansi kembali normal.']]},
 edta:{t:'+ EDTA (protecting agent)',eq:'Ca²⁺ + Y⁴⁻ → CaY²⁻  (kompleks 1 : 1)',
  items:[['Ca',[I([-8,5,3]),I([-5,2.5,0]),A([-4,0.4,0])]],['Ca',[I([7,-3,-5]),I([5,2.5,0]),A([4,0.4,0])]],
   ['EDTA',[s([-9,-6,-4]),s([-5,2.5,0]),s([-5,2.5,0],0)]],['EDTA',[s([9,-2,5]),s([5,2.5,0]),s([5,2.5,0],0)]],
   ['LINES',[s([-9,-6,-4],0),s([-5,2.5,0]),s([-5,2.5,0],0)]],['LINES',[s([9,-2,5],0),s([5,2.5,0]),s([5,2.5,0],0)]],
   ['PO4',[s([-2,-8,2]),s([-1,-7,2]),s([-1,-7,2])]],['PO4',[s([3,-9,-3]),s([2,-7.5,-3]),s([2,-7.5,-3])]],BEAM],
  cap:[['EDTA ditambahkan','EDTA (Y⁴⁻) ditambahkan ke larutan yang mengandung Ca²⁺ dan fosfat.'],
       ['Terbentuk kompleks Ca–EDTA 1:1','EDTA (ligan heksadentat: 2 atom N dan 4 atom O) membungkus satu Ca²⁺ membentuk CaY²⁻ yang stabil, sehingga Ca²⁺ terlindung dan tidak bereaksi dengan fosfat.'],
       ['Ligan terbakar, Ca teratomisasi','Di nyala, bagian organik EDTA terbakar (menjadi CO₂, H₂O, oksida nitrogen) dan melepas Ca, yang menjadi atom Ca⁰ dan menyerap 422,7 nm.']]}
};
const cfg=SCN[SC]; const objs=[];
cfg.items.forEach((it,k)=>{const b=B[it[0]](); st.scene.add(b.g); objs.push({g:b.g,main:b.main,states:it[1],k:k})});
let stage=0,cur=0,last=0;
st.frame=t=>{
  const dt=Math.min(0.05,t-last); last=t; cur+=(stage-cur)*Math.min(1,dt*3);
  objs.forEach(o=>{
    const n=o.states.length-1, i=Math.min(n,Math.floor(cur+1e-4)), j=Math.min(n,i+1), f=Math.max(0,Math.min(1,cur-i));
    const a=o.states[i], b=o.states[j], L=(x,y)=>x+(y-x)*f;
    o.g.position.set(L(a.p[0],b.p[0])+0.12*Math.sin(t*1.3+o.k), L(a.p[1],b.p[1])+0.12*Math.sin(t*1.1+o.k*2), L(a.p[2],b.p[2]));
    const op=L(a.o,b.o);
    o.g.traverse(ch=>{if(ch.material){ch.material.opacity=op;ch.visible=op>0.02}});
    if(o.main){const c=new THREE.Color(a.c).lerp(new THREE.Color(b.c),f); o.main.material.color.copy(c); o.main.material.emissive.copy(c).multiplyScalar(L(a.gl||0,b.gl||0))}
  });
};
const $=id=>document.getElementById(id);
function ui(){const c=cfg.cap[stage]; $('T').textContent=cfg.t; $('EQ').textContent=cfg.eq; $('ST').textContent='Langkah '+(stage+1)+'/3: '+c[0]; $('TX').textContent=c[1]}
$('pv').onclick=()=>{stage=Math.max(0,stage-1);ui()};
$('nx').onclick=()=>{stage=Math.min(2,stage+1);ui()};
setInterval(()=>{if($('au').checked){stage=(stage+1)%3;ui()}},4000);
[['Ca²⁺ / Ca⁰','#14b8a6'],['La³⁺','#a855f7'],['Sr²⁺','#84cc16'],['P','#f59e0b'],['O','#ef4444'],['N','#4f46e5'],['C','#9ca3af']].forEach(k=>{
  const d=document.createElement('span'); d.className='lg'; d.innerHTML='<span class="dot" style="background:'+k[1]+'"></span>'+k[0]; $('LG').appendChild(d)});
ui();
