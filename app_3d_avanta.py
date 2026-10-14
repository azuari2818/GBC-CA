"""
=====================================================================
 MODEL 3D SPEKTROFOTOMETER SERAPAN ATOM (AAS) GBC AVANTA
 Satu file: library -> data komponen -> HTML/CSS/JS 3D -> aplikasi
=====================================================================
Jalankan lokal :  pip install streamlit
                  streamlit run app.py
GitHub / Streamlit Community Cloud: unggah file ini (beri nama app.py)
dan requirements.txt yang berisi satu baris:  streamlit
Model 3D memakai three.js dari CDN -> browser perlu internet.
Skala model: 1 unit = 1 cm (grid 10 cm).
"""
import json

import streamlit as st

st.set_page_config(page_title="3D AAS GBC Avanta", page_icon="🔬", layout="wide")

# ----------------------------------------------------------------------------
# DATA KOMPONEN  (edit sesuai manual / SOP laboratorium Anda)
# ----------------------------------------------------------------------------
KOMPONEN = [
    {"id": "hcl", "label": "HCL", "nama": "Lampu Katoda Berongga (HCL)",
     "fungsi": "Sumber radiasi garis. Katoda berbentuk rongga terbuat dari (atau dilapisi) logam analit, di dalam tabung gas mulia (Ne/Ar) bertekanan rendah. Ion gas menembak katoda (sputtering), atom logam tereksitasi lalu memancarkan garis resonansi yang tajam, sama dengan garis serapan atom analit (Ca: 422,7 nm).",
     "catatan": "Hangatkan lampu sekitar 10–15 menit agar sinyal stabil; jangan melebihi arus maksimum yang tertera pada lampu."},
    {"id": "turret", "label": "Turret", "nama": "Turret Lampu",
     "fungsi": "Dudukan putar yang memuat beberapa HCL. Lampu yang dipilih diputar ke posisi sumbu optik, sehingga ganti unsur tidak perlu memasang ulang lampu.",
     "catatan": "Jumlah lampu pada turret tergantung varian instrumen, cek manual unit Anda."},
    {"id": "d2", "label": "Lampu D₂", "nama": "Lampu Deuterium (Koreksi Latar)",
     "fungsi": "Memancarkan spektrum kontinu UV. Serapan latar (hamburan partikel dan serapan molekul matriks) diukur dengan D₂ lalu dikurangkan dari sinyal total HCL, sehingga yang tersisa adalah serapan atom saja.",
     "catatan": "D₂ efektif di daerah UV (sekitar 190–350 nm). Garis Ca 422,7 nm berada di luar rentang efektif tersebut."},
    {"id": "nebu", "label": "Nebulizer", "nama": "Nebulizer",
     "fungsi": "Menghisap larutan sampel lewat kapiler (efek Venturi oleh aliran oksidan yang cepat) dan memecahnya menjadi aerosol halus. Laju hisap tipikal sekitar 4–6 mL/menit.",
     "catatan": "Kapiler tersumbat membuat sinyal turun dan noise naik; bilas dengan air atau asam encer."},
    {"id": "spray", "label": "Spray chamber", "nama": "Spray Chamber (Ruang Pengabut)",
     "fungsi": "Mencampur aerosol dengan bahan bakar (asetilen) dan oksidan (udara atau N₂O), serta membuang tetesan besar (lewat impact bead / flow spoiler) ke drain. Hanya sebagian kecil sampel (kira-kira 5–10%) sampai ke nyala.",
     "catatan": "Liquid trap pada selang drain harus selalu terisi cairan untuk mencegah gas bocor dan flashback."},
    {"id": "burner", "label": "Burner", "nama": "Burner Head (Kepala Pembakar)",
     "fungsi": "Kepala pembakar bercelah panjang agar jalur optik panjang dan nyala laminar: sekitar 10 cm untuk udara–asetilen, sekitar 5 cm untuk N₂O–asetilen. Celah dijajarkan dengan sumbu optik.",
     "catatan": "Atur tinggi dan rotasi burner agar berkas melewati zona nyala dengan atom bebas terbanyak; bersihkan kerak garam secara rutin."},
    {"id": "flame", "label": "Nyala", "nama": "Nyala (Zona Atomisasi)",
     "fungsi": "Tempat atomisasi: pelarut menguap (desolvasi), partikel padat menguap, lalu molekul terdisosiasi menjadi atom bebas keadaan dasar yang menyerap radiasi HCL. Udara–C₂H₂ sekitar 2300 °C; N₂O–C₂H₂ sekitar 2900 °C. Untuk Ca, nyala N₂O–C₂H₂ mengurangi gangguan fosfat tetapi ionisasi Ca naik, sehingga perlu penekan ionisasi (mis. K atau Cs).",
     "catatan": "Ikuti urutan nyala/padam menurut SOP; aspirasikan air sebelum dan sesudah pengukuran."},
    {"id": "hood", "label": "Cerobong", "nama": "Cerobong Pembuangan (Exhaust)",
     "fungsi": "Menyedot gas buang (CO₂, NOx, uap logam dan pelarut) ke luar ruangan agar panas dan uap tidak terakumulasi di laboratorium.",
     "catatan": "Pastikan exhaust sudah menyala sebelum nyala dinyalakan."},
    {"id": "sample", "label": "Sampel", "nama": "Wadah Sampel & Kapiler",
     "fungsi": "Wadah larutan standar/sampel. Kapiler (selang kecil) menghubungkan larutan ke nebulizer.",
     "catatan": "Gunakan matriks asam yang sama pada standar dan sampel, dan jangan biarkan ujung kapiler menyentuh dasar wadah."},
    {"id": "drain", "label": "Drain", "nama": "Wadah Drain (Pembuangan)",
     "fungsi": "Menampung limbah cair dari spray chamber melalui selang drain berbentuk U (liquid seal) yang harus selalu terisi cairan agar gas tidak bocor dan flashback tercegah.",
     "catatan": "Kosongkan secara rutin dan pastikan selang drain tidak tertekuk."},
    {"id": "gas", "label": "Panel gas", "nama": "Panel Kontrol Gas",
     "fungsi": "Mengatur aliran bahan bakar (asetilen) dan oksidan (udara / N₂O), dilengkapi interlock keselamatan (mis. tekanan gas, deteksi nyala, level liquid trap).",
     "catatan": "Tekanan asetilen dari regulator dijaga tidak lebih dari sekitar 15 psi (≈ 100 kPa)."},
    {"id": "slit", "label": "Slit", "nama": "Celah Monokromator (Slit Masuk & Keluar)",
     "fungsi": "Celah masuk membatasi berkas yang memasuki monokromator; celah keluar hanya meneruskan pita sempit panjang gelombang (spectral bandwidth, mis. 0,5 nm) ke detektor, sehingga garis analit terpisah dari garis lain.",
     "catatan": "Celah sempit: resolusi lebih baik tetapi energi turun dan noise naik."},
    {"id": "grating", "label": "Kisi difraksi", "nama": "Kisi Difraksi (Grating) – Monokromator",
     "fungsi": "Memantulkan dan mendispersikan cahaya. Dengan memutar kisi, hanya garis resonansi analit yang diarahkan ke celah keluar, sehingga garis analit terpisah dari emisi nyala dan garis lain dari lampu.",
     "catatan": "Konfigurasi optik (mis. Czerny–Turner) dapat berbeda antarmodel, cek manual. Jangan menyentuh permukaan kisi."},
    {"id": "pmt", "label": "PMT", "nama": "Detektor Photomultiplier (PMT)",
     "fungsi": "Mengubah foton menjadi arus listrik lalu menggandakannya (efek fotolistrik dan emisi sekunder pada dinode). Sinyal diolah menjadi absorbansi: A = log(I₀/I).",
     "catatan": "Tegangan PMT terlalu tinggi menaikkan noise; jangan membuka rumah detektor saat instrumen bertegangan."},
]

# ----------------------------------------------------------------------------
# HALAMAN 3D (HTML + CSS + JavaScript/three.js)
# ----------------------------------------------------------------------------
HTML_3D = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,'Segoe UI',sans-serif;background:#0b1220;color:#e2e8f0}
#wrap{display:flex;height:680px}
#view{flex:1;position:relative;min-width:0;overflow:hidden}
#view canvas{display:block;cursor:grab}
.bar{position:absolute;top:8px;left:8px;right:8px;display:flex;gap:6px;flex-wrap:wrap;z-index:5}
.tb{background:#0b1220dd;color:#cbd5e1;border:1px solid #334155;border-radius:6px;padding:4px 9px;font-size:12px;cursor:pointer;font-family:inherit;display:inline-flex;align-items:center;gap:6px}
.tb.on{background:#1d4ed8;color:#fff;border-color:#1d4ed8}
.tb input{width:90px}
#labels{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:4}
.lab{position:absolute;transform:translate(-50%,-110%);font-size:11px;background:#0b1220dd;color:#e2e8f0;border:1px solid #334155;padding:1px 7px;border-radius:10px;cursor:pointer;white-space:nowrap;pointer-events:auto}
.lab.on{background:#1d4ed8;border-color:#1d4ed8}
#hint{position:absolute;left:10px;bottom:8px;font-size:12px;color:#94a3b8;background:#0b1220cc;padding:4px 8px;border-radius:6px;pointer-events:none}
#side{width:320px;overflow:auto;padding:14px;background:#111827;border-left:1px solid #1f2a44;font-size:13px;line-height:1.55}
h3{margin:0 0 6px;color:#7dd3fc;font-size:16px}
.item{display:block;width:100%;text-align:left;margin:3px 0;padding:6px 8px;border-radius:6px;border:1px solid #1f2a44;background:#0f172a;color:#cbd5e1;cursor:pointer;font-size:12px;font-family:inherit}
.item.on,.item:hover{background:#1d4ed8;color:#fff}
</style></head><body>
<div id="wrap"><div id="view">
  <div class="bar">
    <button class="tb" id="bReset">⟲ Reset</button><button class="tb" id="bFront">Depan</button><button class="tb" id="bTop">Atas</button><button class="tb" id="bSide">Samping</button>
    <button class="tb on" id="tHouse">Selubung</button><button class="tb on" id="tLab">Label</button><button class="tb on" id="tBeam">Jalur cahaya</button>
    <label class="tb">Terpisah <input type="range" id="ex" min="0" max="100" value="0"></label>
  </div>
  <div id="labels"></div>
  <div id="hint">Seret: putar · Scroll: zoom · Klik komponen / label untuk penjelasan · Skala 1:1 (1 unit = 1 cm, grid 10 cm)</div>
</div>
<div id="side"><h3 id="T"></h3><div id="D"></div><hr style="border-color:#1f2a44;margin:12px 0"><div style="color:#94a3b8;margin-bottom:4px">Daftar komponen:</div><div id="list"></div></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const DATA=__DATA__, SCALE=__SCALE__, AX=34;   // AX = tinggi sumbu optik (cm)
const $=id=>document.getElementById(id);
const view=$('view');
let renderer;
try{renderer=new THREE.WebGLRenderer({antialias:true});}
catch(err){view.innerHTML='<p style="padding:24px">WebGL tidak tersedia di browser ini. Gunakan daftar komponen di bawah halaman.</p>';throw err;}

// ---------- scene, kamera, kontrol orbit ----------
const scene=new THREE.Scene(); scene.background=new THREE.Color(0x0b1220);
const camera=new THREE.PerspectiveCamera(45,view.clientWidth/view.clientHeight,0.3,3000);
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
renderer.setSize(view.clientWidth,view.clientHeight); view.appendChild(renderer.domElement);
scene.add(new THREE.AmbientLight(0xffffff,0.7));
const l1=new THREE.DirectionalLight(0xffffff,0.8); l1.position.set(60,120,90); scene.add(l1);
const l2=new THREE.DirectionalLight(0x88aaff,0.35); l2.position.set(-80,40,-60); scene.add(l2);
const tgt=new THREE.Vector3(0,32,0); let th=0.55, ph=1.25, rad=175;
function upd(){
  camera.position.set(tgt.x+rad*Math.sin(ph)*Math.sin(th), tgt.y+rad*Math.cos(ph), tgt.z+rad*Math.sin(ph)*Math.cos(th));
  camera.lookAt(tgt);
}
function setView(t,p,r){th=t;ph=p;rad=r;upd()}
const cv=renderer.domElement; let drag=false,moved=0,lx=0,ly=0;
cv.addEventListener('pointerdown',e=>{drag=true;moved=0;lx=e.clientX;ly=e.clientY;cv.setPointerCapture(e.pointerId);cv.style.cursor='grabbing'});
cv.addEventListener('pointermove',e=>{
  if(drag){const dx=e.clientX-lx, dy=e.clientY-ly; moved+=Math.abs(dx)+Math.abs(dy); lx=e.clientX; ly=e.clientY;
    th-=dx*0.006; ph=Math.min(3.0,Math.max(0.15,ph-dy*0.006)); upd();}
  else cv.style.cursor=pick(e)?'pointer':'grab';
});
cv.addEventListener('pointerup',e=>{drag=false;cv.style.cursor='grab'; if(moved<5){const o=pick(e); if(o)select(o.userData.id)}});
cv.addEventListener('wheel',e=>{e.preventDefault(); rad=Math.min(700,Math.max(8,rad*(1+Math.sign(e.deltaY)*0.08))); upd()},{passive:false});
window.addEventListener('resize',()=>{renderer.setSize(view.clientWidth,view.clientHeight);camera.aspect=view.clientWidth/view.clientHeight;camera.updateProjectionMatrix()});
upd();

// ---------- helper ----------
const G=new THREE.Group(); G.scale.setScalar(SCALE); scene.add(G);
const grid=new THREE.GridHelper(300,30,0x334155,0x1e293b); grid.position.y=-0.05; scene.add(grid);
const mat=(c,o=1,m=0.3,r=0.5)=>new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:m,transparent:o<1,opacity:o});
const all=[], picks=[], housings=[], beams=[];
function reg(m,id,pk=true){m.userData.id=id;m.userData.home=m.position.clone();m.userData.em=m.material.emissive.getHex();G.add(m);all.push(m);if(pk)picks.push(m);return m}
function N(m){G.add(m);return m}
const bx=(w,h,d,x,y,z,m)=>{const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);return o};
const cy=(r,h,x,y,z,m,ax)=>{const o=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,28),m);o.position.set(x,y,z);if(ax==='x')o.rotation.z=Math.PI/2;if(ax==='z')o.rotation.x=Math.PI/2;return o};
function cyl(a,b,r,m){
  const A=new THREE.Vector3(a[0],a[1],a[2]), B=new THREE.Vector3(b[0],b[1],b[2]);
  const d=B.clone().sub(A), L=d.length();
  const o=new THREE.Mesh(new THREE.CylinderGeometry(r,r,L,16),m);
  o.position.copy(A.clone().add(B).multiplyScalar(0.5));
  o.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.normalize());
  return o;
}
function house(w,h,d,x,y,z,c,o){
  const m=bx(w,h,d,x,y,z,mat(c,o,0,1)); m.material.depthWrite=false; N(m); housings.push(m);
  const e=new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),new THREE.LineBasicMaterial({color:0x64748b})); e.position.copy(m.position); N(e); housings.push(e);
}

// ---------- model instrumen (1 unit = 1 cm, perkiraan: 84 x 48 x ~70 cm) ----------
N(bx(84,20,48,0,10,0,mat(0xcbd5e1,1,0.2,0.6)));                 // rangka bawah
house(30,30,48,-27,35,0,0x60a5fa,0.10);                          // rumah lampu
house(24,30,48,0,35,0,0x93c5fd,0.06);                            // kompartemen sampel/nyala
house(30,30,48,27,35,0,0x60a5fa,0.10);                           // rumah monokromator + detektor
house(22,18,24,25,AX,0,0x1e40af,0.25);                           // monokromator
// jalur cahaya
const beamM=new THREE.MeshBasicMaterial({color:0xfde047,transparent:true,opacity:0.8});
[[[-10.5,AX,0],[14,AX,0]],[[14,AX,0],[25,AX,-8.6]],[[25,AX,-8.6],[36,AX,0]]].forEach(b=>beams.push(N(cyl(b[0],b[1],0.3,beamM))));
// turret + HCL + D2
reg(cy(4.5,6,-26,AX,0,mat(0x475569),'y'),'turret');
[0,90,180,270].forEach(a=>{
  const r=a*Math.PI/180, dx=Math.cos(r), dz=Math.sin(r);
  reg(cyl([-26+dx*3.5,AX,dz*3.5],[-26+dx*15.5,AX,dz*15.5],1.9,mat(a===0?0xfbbf24:0xe5e7eb,1,0.6,0.3)),'hcl');
});
reg(cy(2.2,9,-26,AX,-19.5,mat(0x38bdf8,1,0.4,0.3),'x'),'d2');
// spray chamber, nebulizer, burner, nyala
reg(cy(4.5,20,0,25.5,0,mat(0x9ca3af,1,0.5,0.4),'z'),'spray');
reg(cy(1.6,6,0,25.5,13,mat(0xf59e0b),'z'),'nebu');
reg(cy(2,3,0,29,0,mat(0x6b7280),'y'),'burner');
reg(bx(10,2,1.2,0,31.5,0,mat(0x374151,1,0.6,0.4)),'burner');
const flM=mat(0xfb923c,0.75); flM.emissive.setHex(0xfb923c);
const fl=new THREE.Mesh(new THREE.SphereGeometry(1,24,16),flM); fl.position.set(0,36,0); fl.scale.set(5.5,4,1.4); reg(fl,'flame');
const coreM=mat(0x60a5fa,0.8); coreM.emissive.setHex(0x3b82f6);
const core=new THREE.Mesh(new THREE.SphereGeometry(1,20,12),coreM); core.position.set(0,33.4,0); core.scale.set(4.5,1.6,0.9); reg(core,'flame',false);
// cerobong
const hoodM=mat(0x94a3b8,1,0.5,0.5); hoodM.side=THREE.DoubleSide;
const h1=new THREE.Mesh(new THREE.CylinderGeometry(5,9,8,28,1,true),hoodM); h1.position.set(0,46,0); reg(h1,'hood');
const h2=new THREE.Mesh(new THREE.CylinderGeometry(4,4,20,28,1,true),hoodM); h2.position.set(0,60,0); reg(h2,'hood');
// wadah sampel + kapiler
reg(cy(3.5,8,0,4,32,mat(0xe0f2fe,0.3,0.1,0.1)),'sample');
reg(cy(3.2,5,0,3,32,mat(0x38bdf8,0.85,0.1,0.2)),'sample');
reg(cyl([0,25.5,16],[0,25.5,32],0.35,mat(0xf1f5f9)),'sample');
reg(cyl([0,25.5,32],[0,4,32],0.35,mat(0xf1f5f9)),'sample');
// drain
reg(cy(4,12,0,6,-34,mat(0xf87171,0.5,0.1,0.3)),'drain');
reg(cyl([0,22,-10],[0,22,-34],0.5,mat(0xfca5a5)),'drain');
reg(cyl([0,22,-34],[0,10,-34],0.5,mat(0xfca5a5)),'drain');
// panel gas
reg(bx(22,10,1.5,-28,10,24.75,mat(0x1f2937,1,0.4,0.5)),'gas');
[[-34,0xef4444],[-28,0x9ca3af],[-22,0x3b82f6]].forEach(k=>reg(cy(1.6,2,k[0],10,26,mat(k[1]),'z'),'gas'));
// monokromator + detektor
[14,36].forEach(x=>[-1,1].forEach(sg=>reg(bx(0.6,4,1,x,AX,sg*1,mat(0xfacc15)),'slit')));
reg(bx(6,6,0.8,25,AX,-9,mat(0xa78bfa,1,0.8,0.2)),'grating');
reg(cy(3,6,39,AX,0,mat(0xd97706,1,0.5,0.4),'x'),'pmt');

// ---------- posisi label & arah "exploded view" (cm) ----------
const ANCH={hcl:[-26,AX,16.5],turret:[-26,AX+7,0],d2:[-26,AX,-22],nebu:[0,25.5,17],spray:[6,22,-8],burner:[-7,31.5,0],
  flame:[0,41,0],hood:[0,71,0],sample:[5,9,32],drain:[0,13,-34],gas:[-28,16,25],slit:[14,AX+3,2],grating:[25,AX+4,-9],pmt:[39,AX+4,0]};
const EXP={hcl:[-14,0,0],turret:[-14,0,0],d2:[-14,0,-10],nebu:[0,0,16],burner:[0,12,0],flame:[0,20,0],hood:[0,18,0],
  sample:[0,0,22],drain:[0,0,-18],gas:[-10,0,14],slit:[10,0,0],grating:[8,0,-12],pmt:[18,0,0]};

// ---------- UI ----------
const T=$('T'), D=$('D'), LIST=$('list'), LAB=$('labels');
const labs=[];
DATA.forEach(d=>{
  const b=document.createElement('button'); b.className='item'; b.dataset.id=d.id; b.textContent=d.nama; b.onclick=()=>select(d.id); LIST.appendChild(b);
  const l=document.createElement('div'); l.className='lab'; l.textContent=d.label; l.onclick=()=>select(d.id); LAB.appendChild(l); labs.push({id:d.id,el:l});
});
function select(id){
  picks.forEach(m=>m.material.emissive.setHex(m.userData.id===id?0x1d4ed8:m.userData.em));
  const d=DATA.find(x=>x.id===id);
  T.textContent=d.nama; D.innerHTML='<p style="margin:6px 0">'+d.fungsi+'</p><p style="margin:6px 0;color:#fcd34d"><b>Catatan:</b> '+d.catatan+'</p>';
  document.querySelectorAll('.item').forEach(e=>e.classList.toggle('on',e.dataset.id===id));
  labs.forEach(l=>l.el.classList.toggle('on',l.id===id));
}
let showLab=true, showHouse=true, showBeam=true, expK=0;
function toggle(btn,fn){btn.onclick=()=>{btn.classList.toggle('on');fn(btn.classList.contains('on'))}}
toggle($('tHouse'),v=>showHouse=v); toggle($('tLab'),v=>showLab=v); toggle($('tBeam'),v=>showBeam=v);
$('bReset').onclick=()=>setView(0.55,1.25,175);
$('bFront').onclick=()=>setView(0,1.45,175);
$('bTop').onclick=()=>setView(0,0.2,175);
$('bSide').onclick=()=>setView(1.5708,1.45,175);
$('ex').oninput=e=>{expK=e.target.value/100};

// ---------- animasi ----------
const v3=new THREE.Vector3();
(function loop(ms){
  requestAnimationFrame(loop); const t=ms/1000;
  fl.scale.set(5.5,4*(1+0.07*Math.sin(t*18)),1.4);
  core.scale.set(4.5,1.6*(1+0.05*Math.sin(t*22)),0.9);
  beamM.opacity=0.65+0.2*Math.sin(t*5);
  all.forEach(m=>{const e=EXP[m.userData.id]; if(e){const h=m.userData.home; m.position.set(h.x+e[0]*expK,h.y+e[1]*expK,h.z+e[2]*expK)}});
  housings.forEach(h=>h.visible=showHouse);
  beams.forEach(b=>b.visible=showBeam&&expK<0.02);
  G.updateMatrixWorld(true);
  const w=view.clientWidth, h=view.clientHeight;
  labs.forEach(l=>{
    const a=ANCH[l.id], e=EXP[l.id]||[0,0,0];
    v3.set(a[0]+e[0]*expK,a[1]+e[1]*expK,a[2]+e[2]*expK).applyMatrix4(G.matrixWorld).project(camera);
    l.el.style.display=(showLab&&v3.z<1)?'block':'none';
    l.el.style.left=((v3.x*0.5+0.5)*w)+'px'; l.el.style.top=((-v3.y*0.5+0.5)*h)+'px';
  });
  renderer.render(scene,camera);
})(0);

function pick(e){
  const r=cv.getBoundingClientRect();
  const m=new THREE.Vector2(((e.clientX-r.left)/r.width)*2-1, -((e.clientY-r.top)/r.height)*2+1);
  const rc=new THREE.Raycaster(); rc.setFromCamera(m,camera);
  const h=rc.intersectObjects(picks,false); return h.length?h[0].object:null;
}
select('hcl');
</script></body></html>
"""


def tampilkan_html(html: str, tinggi: int) -> None:
    """Streamlit baru memakai st.iframe; versi lama memakai components.html."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=tinggi)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=tinggi, scrolling=False)


# ----------------------------------------------------------------------------
# APLIKASI STREAMLIT
# ----------------------------------------------------------------------------
st.title("🔬 Model 3D Spektrofotometer AAS GBC Avanta")
st.caption("Klik komponen (atau labelnya) untuk melihat fungsi dan catatan penggunaannya. Seret untuk memutar, scroll untuk zoom.")

with st.expander("⚙️ Pengaturan skala model"):
    skala = st.number_input(
        "Faktor kalibrasi skala", 0.5, 2.0, 1.0, 0.01,
        help="Model memakai 1 unit = 1 cm (lebar ±84 cm, kedalaman ±48 cm, tinggi ±70 cm dengan cerobong). "
             "Jika dimensi asli di manual berbeda, ubah faktor ini (mis. 0,95 atau 1,05).")

tampilkan_html(HTML_3D.replace("__DATA__", json.dumps(KOMPONEN, ensure_ascii=False))
               .replace("__SCALE__", str(skala)), 685)

st.caption("Model 3D adalah representasi sederhana. Dimensi dan tata letak komponen sebaiknya diverifikasi dengan manual GBC Avanta unit di laboratorium Anda.")

with st.expander("📋 Daftar komponen & fungsi (teks)"):
    for k in KOMPONEN:
        st.markdown(f"**{k['nama']}**  \n{k['fungsi']}  \n*Catatan:* {k['catatan']}")
