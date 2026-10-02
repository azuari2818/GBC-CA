"""
Website Proyek: Spektrofotometer Serapan Atom (AAS) GBC Avanta
Jalankan:  streamlit run app.py

Struktur proyek:
  app.py                  -> Python (Streamlit): UI, regresi, pemanggil halaman 3D
  requirements.txt        -> daftar pustaka Python
  assets/style.css        -> CSS (tampilan halaman 3D)
  assets/common.js        -> JavaScript bersama (three.js: scene, orbit, raycast)
  assets/instrument.html  -> HTML halaman model 3D AAS
  assets/instrument.js    -> JavaScript model 3D AAS (klik komponen)
  assets/interference.html-> HTML halaman animasi gangguan Ca
  assets/interference.js  -> JavaScript animasi Sr2+, La3+, EDTA
  assets/komponen.json    -> teks penjelasan tiap komponen (mudah diedit)
Model 3D memakai three.js dari CDN -> perlu koneksi internet di browser.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AAS GBC Avanta 3D", page_icon="🔬", layout="wide")

ASSETS = Path(__file__).parent / "assets"


def baca(nama: str) -> str:
    return (ASSETS / nama).read_text(encoding="utf-8")


KOMPONEN = json.loads(baca("komponen.json"))


def render_html(halaman: str, **kw) -> str:
    """Gabungkan HTML + CSS + JS menjadi satu dokumen (iframe Streamlit tidak bisa memuat file lokal)."""
    js = baca(f"{halaman}.js")
    for k, v in kw.items():
        js = js.replace(f"__{k}__", v)
    return (baca(f"{halaman}.html")
            .replace("__CSS__", baca("style.css"))
            .replace("__COMMON__", baca("common.js"))
            .replace("__SCRIPT__", js))


# ----------------------------------------------------------------------------
# # APLIKASI STREAMLIT
# ----------------------------------------------------------------------------
st.title("🔬 Spektrofotometer Serapan Atom (AAS) GBC Avanta")
st.caption("Media pembelajaran interaktif: model 3D instrumen, kurva kalibrasi, dan mekanisme penghilangan gangguan pada analisis Ca.")

tab1, tab2, tab3 = st.tabs(["🧊 Model 3D AAS", "📈 Kurva Kalibrasi", "🧪 Gangguan Ca (Sr²⁺, La³⁺, EDTA)"])

# ---------------------------- TAB 1 ----------------------------
with tab1:
    c_a, c_b = st.columns([3, 1])
    with c_a:
        st.markdown("Klik bagian instrumen (lampu, nebulizer, burner, nyala, monokromator, detektor, dst.) atau pilih dari daftar di panel kanan untuk melihat penjelasannya.")
    with c_b:
        skala = st.number_input("Faktor kalibrasi skala", 0.5, 2.0, 1.0, 0.01,
                                help="Model dibuat dengan 1 unit = 1 cm (lebar ±84 cm, kedalaman ±48 cm, tinggi ±70 cm dengan cerobong). "
                                     "Jika dimensi asli di manual berbeda, ubah faktor ini (mis. 0,95 atau 1,05).")
    components.html(
        render_html("instrument", DATA=json.dumps(KOMPONEN, ensure_ascii=False), SCALE=str(skala)),
        height=665, scrolling=False)
    st.caption("Catatan: model 3D adalah representasi sederhana. Dimensi dan tata letak komponen sebaiknya diverifikasi dengan manual GBC Avanta unit di laboratorium Anda.")

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
    components.html(render_html("interference", SC=json.dumps(kunci)), height=665, scrolling=False)
    st.caption("Skala model: 1 unit = 1 Å. Ukuran bola mengikuti jari-jari ion/kovalen sehingga perbandingan ukuran antarspesi proporsional. "
               "Rasio kompleks Ca : EDTA = 1 : 1. Posisi atom bersifat skematik untuk tujuan ilustrasi.")
