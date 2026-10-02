"""
=====================================================================
 WEBSITE PROYEK: SPEKTROFOTOMETER SERAPAN ATOM (AAS) GBC AVANTA
 Satu file lengkap: library -> data -> HTML/CSS/JS -> aplikasi utama
=====================================================================
CARA PAKAI
  1. Simpan seluruh isi file ini sebagai  app.py
  2. Pasang library (satu kali):
         pip install streamlit numpy pandas plotly
     atau buat requirements.txt berisi (untuk Streamlit Community Cloud):
         streamlit
         numpy
         pandas
         plotly
  3. Jalankan:   streamlit run app.py
Catatan: model 3D memakai three.js dari CDN, sehingga browser perlu internet.
 
ISI FILE
  [1] Library & konfigurasi halaman
  [2] Data penjelasan komponen AAS (KOMPONEN)  -> edit sesuai manual/SOP
  [3] CSS bersama
  [4] JavaScript bersama (three.js: scene, orbit, klik, silinder)
  [5] Halaman 3D model AAS   (HTML + JavaScript)
  [6] Halaman 3D gangguan Ca (HTML + JavaScript)
  [7] Fungsi penggabung HTML
  [8] Aplikasi Streamlit (3 tab)
"""
 
# ----------------------------------------------------------------------------
# [1] LIBRARY & KONFIGURASI HALAMAN
# ----------------------------------------------------------------------------
import json                              # data komponen -> JSON untuk JavaScript
 
import streamlit as st                   # kerangka website
 
st.set_page_config(page_title="AAS GBC Avanta 3D", page_icon="🔬", layout="wide")
 
try:
    import numpy as np                   # regresi linear (polyfit, korelasi)
    import pandas as pd                  # tabel data standar & sampel
    import plotly.graph_objects as go    # grafik kurva kalibrasi
except ImportError as e:
    st.error(f"Library belum terpasang: {e.name}. Jalankan: pip install numpy pandas plotly")
    st.stop()

# ----------------------------------------------------------------------------
# [3] CSS BERSAMA
# ----------------------------------------------------------------------------
BASE_CSS = r"""/* Gaya dasar kedua halaman 3D */
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,'Segoe UI',sans-serif;background:#0b1220;color:#e2e8f0}
#wrap{display:flex;height:660px}
#view{flex:1;position:relative;min-width:0;overflow:hidden}
#view canvas{display:block;cursor:grab}
#hint{position:absolute;left:10px;bottom:8px;font-size:12px;color:#94a3b8;background:#0b1220cc;padding:4px 8px;border-radius:6px;pointer-events:none}
#side{width:320px;overflow:auto;padding:14px;background:#111827;border-left:1px solid #1f2a44;font-size:13px;line-height:1.55}
h3{margin:0 0 6px;color:#7dd3fc;font-size:16px}
button{font-family:inherit}
 
/* Komponen halaman interferensi Ca */
.btn{background:#1d4ed8;color:#fff;border:0;border-radius:6px;padding:7px 12px;margin:2px 2px 2px 0;cursor:pointer;font-size:13px}
.btn:hover{background:#2563eb}
.lg{display:inline-flex;align-items:center;margin:2px 10px 2px 0;font-size:12px}
.dot{width:11px;height:11px;border-radius:50%;margin-right:5px;display:inline-block}
.eq{background:#0f172a;border:1px solid #1f2a44;border-radius:6px;padding:8px;margin:8px 0;color:#fde68a}
"""
 
# ----------------------------------------------------------------------------
# [4] JAVASCRIPT BERSAMA (three.js)
# ----------------------------------------------------------------------------
COMMON_JS = r"""// Helper bersama: scene three.js, kontrol orbit, raycast, silinder
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
"""
 
# ----------------------------------------------------------------------------
# [6] HALAMAN 3D GANGGUAN Ca (1 unit = 1 Angstrom)
# ----------------------------------------------------------------------------
INT_HTML = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>__CSS__</style></head><body>
<div id="wrap"><div id="view"><div id="hint">Seret: putar · Scroll: zoom · 1 unit = 1 Å (jari-jari ion/kovalen sesuai skala)</div></div>
<div id="side"><h3 id="T"></h3><div class="eq" id="EQ"></div>
<div style="font-weight:600;color:#7dd3fc" id="ST"></div><p id="TX" style="margin:6px 0 10px"></p>
<button class="btn" id="pv">◀ Sebelumnya</button><button class="btn" id="nx">Berikutnya ▶</button>
<label style="display:block;margin:6px 0;color:#94a3b8"><input type="checkbox" id="au"> Putar otomatis</label>
<hr style="border-color:#1f2a44;margin:12px 0"><div id="LG"></div>
<p style="color:#94a3b8;font-size:12px;margin-top:10px">Model skematik: posisi atom diperkirakan untuk ilustrasi. Jari-jari: Ca²⁺ 1,00; Sr²⁺ 1,18; La³⁺ 1,03 Å (ion); P 1,07; O 0,66; N 0,71; C 0,76 Å (kovalen).</p></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>__COMMON__</script>
<script>__SCRIPT__</script>
</body></html>
"""
 
INT_JS = r"""const SC=__SC__;
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
"""
 
# ----------------------------------------------------------------------------
# [7] PENGGABUNG HTML (iframe Streamlit tidak bisa memuat file lokal)
# ----------------------------------------------------------------------------
def render_html(template: str, script: str, **kw) -> str:
    for k, v in kw.items():
        script = script.replace(f"__{k}__", v)
    return (template.replace("__CSS__", BASE_CSS)
            .replace("__COMMON__", COMMON_JS)
            .replace("__SCRIPT__", script))
 
 
def tampilkan_html(html: str, tinggi: int) -> None:
    """Tampilkan HTML penuh. Streamlit baru memakai st.iframe; versi lama memakai components.html."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=tinggi)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=tinggi, scrolling=False)
 
 
# ----------------------------------------------------------------------------
# [8] APLIKASI STREAMLIT
# ----------------------------------------------------------------------------
st.title("🔬 Spektrofotometer Serapan Atom (AAS) GBC Avanta")
st.caption("Media pembelajaran interaktif: model 3D instrumen, kurva kalibrasi, dan mekanisme penghilangan gangguan pada analisis Ca.")
 
tab1, tab2, tab3 = st.tabs(["🧊 Model 3D AAS", "📈 Kurva Kalibrasi", "🧪 Gangguan Ca (Sr²⁺, La³⁺, EDTA)"])
 
# ---------------------------- TAB 2 ----------------------------
with tab2:
    st.subheader("Kurva Kalibrasi Standar & Penentuan Konsentrasi Sampel")
    kiri, kanan = st.columns([1, 1.5])
 
    with kiri:
        satuan = st.text_input("Satuan konsentrasi", "mg/L")
        st.markdown("**1. Data deret standar** (tambah/hapus baris dengan tombol tabel)")
        std = st.data_editor(
            pd.DataFrame({"Konsentrasi": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                          "Absorbansi": [0.002, 0.051, 0.103, 0.148, 0.205, 0.249]}),
            num_rows="dynamic", key="std",
            column_config={"Konsentrasi": st.column_config.NumberColumn(format="%.4f"),
                           "Absorbansi": st.column_config.NumberColumn(format="%.4f")})
        st.markdown("**2. Absorbansi sampel**")
        smp = st.data_editor(
            pd.DataFrame({"Nama Sampel": ["Sampel 1", "Sampel 2"], "Absorbansi": [0.120, 0.180]}),
            num_rows="dynamic", key="smp",
            column_config={"Absorbansi": st.column_config.NumberColumn(format="%.4f")})
        fp = st.number_input("Faktor pengenceran sampel", min_value=1.0, value=1.0, step=1.0)
 
    d = std[["Konsentrasi", "Absorbansi"]].apply(pd.to_numeric, errors="coerce").dropna()
 
    with kanan:
        if len(d) < 3 or d["Konsentrasi"].nunique() < 2:
            st.info("Masukkan minimal 3 titik standar dengan konsentrasi yang berbeda.")
        else:
            x = d["Konsentrasi"].to_numpy(float)
            y = d["Absorbansi"].to_numpy(float)
            m, b = np.polyfit(x, y, 1)
            yhat = m * x + b
            ss_res = float(np.sum((y - yhat) ** 2))
            ss_tot = float(np.sum((y - y.mean()) ** 2))
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
            r = float(np.corrcoef(x, y)[0, 1])
            tanda = "+" if b >= 0 else "−"
            st.success(f"**Persamaan regresi:**  A = {m:.4f} · C {tanda} {abs(b):.4f}")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Slope (m)", f"{m:.4f}")
            m2.metric("Intersep (b)", f"{b:.4f}")
            m3.metric("Koef. korelasi (r)", f"{r:.5f}")
            m4.metric("R²", f"{r2:.5f}")
            if r < 0.995:
                st.warning("r < 0,995. Banyak SOP AAS mensyaratkan r ≥ 0,995 (cek SOP Anda); periksa titik standar yang menyimpang.")
            if len(d) > 2 and abs(m) > 1e-12:
                syx = (ss_res / (len(d) - 2)) ** 0.5
                st.caption(f"Perkiraan LOD = 3·Sy/x ÷ m = {3*syx/abs(m):.4f} {satuan}; LOQ = 10·Sy/x ÷ m = {10*syx/abs(m):.4f} {satuan} (dari simpangan residual regresi).")
 
            fig = go.Figure()
            xx = np.linspace(0, x.max() * 1.1, 50)
            fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="Standar", marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=xx, y=m * xx + b, mode="lines", name="Regresi linear"))
 
            if abs(m) < 1e-12:
                st.error("Slope bernilai 0, sampel tidak dapat dihitung. Periksa data standar.")
            else:
                s = smp.copy()
                s["Nama Sampel"] = s["Nama Sampel"].fillna("-")
                s["Absorbansi"] = pd.to_numeric(s["Absorbansi"], errors="coerce")
                s = s.dropna(subset=["Absorbansi"]).reset_index(drop=True)
                if len(s):
                    ck = f"C terbaca ({satuan})"
                    cf = f"C sampel × FP ({satuan})"
                    s[ck] = (s["Absorbansi"] - b) / m
                    s[cf] = s[ck] * fp
                    s["Status"] = np.where((s["Absorbansi"] >= y.min()) & (s["Absorbansi"] <= y.max()),
                                           "✔ dalam rentang kalibrasi", "⚠ di luar rentang (ekstrapolasi)")
                    fig.add_trace(go.Scatter(x=s[ck], y=s["Absorbansi"], mode="markers", name="Sampel",
                                             marker=dict(size=12, symbol="diamond"), text=s["Nama Sampel"]))
                    st.markdown("**Hasil konsentrasi sampel**  (C = (A − b) / m)")
                    st.dataframe(s.style.format({"Absorbansi": "{:.4f}", ck: "{:.4f}", cf: "{:.4f}"}), hide_index=True)
 
            fig.update_layout(xaxis_title=f"Konsentrasi ({satuan})", yaxis_title="Absorbansi",
                              height=400, margin=dict(l=10, r=10, t=30, b=10),
                              title=f"Kurva kalibrasi: A = {m:.4f}·C {tanda} {abs(b):.4f}  (R² = {r2:.4f})")
            st.plotly_chart(fig)
 
# ---------------------------- TAB 3 ----------------------------
with tab3:
    st.subheader("Bagaimana Sr²⁺, La³⁺, dan EDTA mengatasi gangguan pada analisis Ca?")
    st.markdown(
        "Pada AAS nyala, **fosfat, sulfat, dan Al** membentuk senyawa sukar menguap dengan Ca (gangguan kimia). "
        "Atom Ca bebas berkurang sehingga absorbansi turun. Gangguan ini diatasi dengan **releasing agent** (La³⁺, Sr²⁺) "
        "atau **protecting agent** (EDTA). Pilih skenario lalu geser langkahnya pada model 3D.")
    pilihan = st.radio(
        "Skenario", ["Tanpa aditif (ada gangguan fosfat)", "+ La³⁺ (releasing agent)",
                     "+ Sr²⁺ (releasing agent)", "+ EDTA (protecting agent)"], horizontal=True)
    kunci = {"Tanpa aditif (ada gangguan fosfat)": "none", "+ La³⁺ (releasing agent)": "la",
             "+ Sr²⁺ (releasing agent)": "sr", "+ EDTA (protecting agent)": "edta"}[pilihan]
    tampilkan_html(render_html(INT_HTML, INT_JS, SC=json.dumps(kunci)), 665)
    st.caption("Skala model: 1 unit = 1 Å. Ukuran bola mengikuti jari-jari ion/kovalen sehingga perbandingan ukuran antarspesi proporsional. "
               "Rasio kompleks Ca : EDTA = 1 : 1. Posisi atom bersifat skematik untuk tujuan ilustrasi.")
