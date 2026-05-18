import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import streamlit as st

# ==========================================
# CONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="Responsi IF-A - Smart Greenhouse", layout="wide")
st.title("Sistem Kendali Otomatis Smart Greenhouse")
st.write("Implementasi Logika Fuzzy Mamdani - Praktikum SC & PK.")
st.markdown("---")

# ==========================================
# 1. DEFINISI VARIABEL & SEMESTA PEMBICARAAN
# ==========================================
x_suhu = np.arange(0, 41, 1)
x_kelembapan = np.arange(0, 101, 1)
x_cahaya = np.arange(0, 101, 1)

x_pompa = np.arange(0, 61, 1)
x_kipas = np.arange(0, 101, 1)
x_lampu = np.arange(0, 101, 1)

suhu = ctrl.Antecedent(x_suhu, 'suhu')
kelembapan = ctrl.Antecedent(x_kelembapan, 'kelembapan')
cahaya = ctrl.Antecedent(x_cahaya, 'cahaya')

pompa = ctrl.Consequent(x_pompa, 'pompa')
kipas = ctrl.Consequent(x_kipas, 'kipas')
lampu = ctrl.Consequent(x_lampu, 'lampu')

# ==========================================
# 2. FUNGSI KEANGGOTAAN (MEMBERSHIP FUNCTIONS)
# ==========================================
suhu['dingin'] = fuzz.trapmf(x_suhu, [0, 0, 15, 22])
suhu['normal'] = fuzz.trimf(x_suhu, [18, 25, 30])
suhu['panas'] = fuzz.trapmf(x_suhu, [27, 32, 40, 40])

kelembapan['kering'] = fuzz.trapmf(x_kelembapan, [0, 0, 0, 40])
kelembapan['ideal'] = fuzz.trimf(x_kelembapan, [30, 50, 70])
kelembapan['basah'] = fuzz.trapmf(x_kelembapan, [60, 100, 100, 100])

cahaya['gelap'] = fuzz.trapmf(x_cahaya, [0, 0, 20, 40])
cahaya['redup'] = fuzz.trimf(x_cahaya, [30, 50, 70])
cahaya['terang'] = fuzz.trapmf(x_cahaya, [60, 90, 100, 100])

pompa['singkat'] = fuzz.trapmf(x_pompa, [0, 0, 0, 20])
pompa['sedang'] = fuzz.trimf(x_pompa, [15, 30, 45])
pompa['lama'] = fuzz.trapmf(x_pompa, [40, 60, 60, 60])

kipas['lambat'] = fuzz.trapmf(x_kipas, [0, 0, 25, 50])
kipas['sedang'] = fuzz.trimf(x_kipas, [35, 60, 80])
kipas['cepat'] = fuzz.trapmf(x_kipas, [70, 90, 100, 100])

lampu['mati_redup'] = fuzz.trapmf(x_lampu, [0, 0, 0, 40])
lampu['sedang'] = fuzz.trimf(x_lampu, [20, 50, 80])
lampu['terang'] = fuzz.trapmf(x_lampu, [60, 100, 100, 100])

# ==========================================
# 3. ATURAN LOGIKA FUZZY (RULE BASE)
# ==========================================
rule1 = ctrl.Rule(suhu['panas'] | cahaya['terang'], [kipas['cepat'], pompa['singkat'], lampu['mati_redup']])
rule2 = ctrl.Rule(suhu['dingin'] & cahaya['gelap'], [kipas['lambat'], pompa['sedang'], lampu['terang']])
rule3 = ctrl.Rule(kelembapan['kering'] & suhu['panas'], [pompa['lama'], kipas['cepat'], lampu['sedang']])
rule4 = ctrl.Rule(kelembapan['basah'] & suhu['dingin'], [pompa['singkat'], kipas['lambat'], lampu['terang']])
rule5 = ctrl.Rule(suhu['normal'] & kelembapan['ideal'] & cahaya['redup'], [pompa['sedang'], kipas['sedang'], lampu['sedang']])
rule6 = ctrl.Rule(kelembapan['kering'] | cahaya['gelap'], [pompa['lama'], lampu['terang'], kipas['lambat']])

# ==========================================
# 4. SISTEM INFERENSI & KONTROL
# ==========================================
greenhouse_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
simulasi = ctrl.ControlSystemSimulation(greenhouse_ctrl)

# ==========================================
# 5. INPUT PARAMETER DINAMIS (UI SIDEBAR)
# ==========================================
st.sidebar.header("Input Parameter Sensor")
input_suhu = st.sidebar.slider("Suhu Lingkungan (°C)", 0.0, 40.0, 30.0, step=0.5) [cite: 130]
input_kelembapan = st.sidebar.slider("Kelembapan Tanah (%)", 0.0, 100.0, 35.0, step=1.0) [cite: 131]
input_cahaya = st.sidebar.slider("Cahaya Matahari (Lux/100)", 0.0, 100.0, 25.0, step=1.0) [cite: 132]

simulasi.input['suhu'] = input_suhu
simulasi.input['kelembapan'] = input_kelembapan
simulasi.input['cahaya'] = input_cahaya

simulasi.compute()

hasil_pompa = simulasi.output['pompa'] [cite: 133]
hasil_kipas = simulasi.output['kipas'] [cite: 133]
hasil_lampu = simulasi.output['lampu'] [cite: 133]

# ==========================================
# 6. MENAMPILKAN ANGKA HASIL DEFUZZIFIKASI
# ==========================================
st.subheader("Hasil Nilai Defuzzifikasi (Aksi Aktuator)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Durasi Pompa Air", value=f"{hasil_pompa:.2f} Menit")
with col2:
    st.metric(label="Kecepatan Kipas Exhaust", value=f"{hasil_kipas:.2f} RPM/10")
with col3:
    st.metric(label="Daya Lampu UV", value=f"{hasil_lampu:.2f} Watt")

st.markdown("---")

# ==========================================
# 7. VISUALISASI MANUAL (GARANSI MUNCUL)
# ==========================================
st.subheader("Grafik Arsir Hasil Defuzzifikasi Pada Kurva Output") [cite: 133]

# --- PLOT 1: POMPA AIR ---
fig1, ax1 = plt.subplots(figsize=(8, 3.5))
# Gambar kurva referensi dasar
ax1.plot(x_pompa, pompa['singkat'].mf, 'b', linewidth=1.5, label='Singkat')
ax1.plot(x_pompa, pompa['sedang'].mf, 'g', linewidth=1.5, label='Sedang')
ax1.plot(x_pompa, pompa['lama'].mf, 'r', linewidth=1.5, label='Lama')
# Hitung tingkat kecocokan untuk arsir hasil
m_singkat = fuzz.interp_membership(x_pompa, pompa['singkat'].mf, hasil_pompa)
m_sedang  = fuzz.interp_membership(x_pompa, pompa['sedang'].mf, hasil_pompa)
m_lama    = fuzz.interp_membership(x_pompa, pompa['lama'].mf, hasil_pompa)
# Lakukan pengarsiran area hasil komputasi
pompa_activation = np.fmax(np.fmin(m_singkat, pompa['singkat'].mf),
                           np.fmax(np.fmin(m_sedang, pompa['sedang'].mf),
                                   np.fmin(m_lama, pompa['lama'].mf)))
ax1.fill_between(x_pompa, 0, pompa_activation, facecolor='Orange', alpha=0.4)
ax1.axvline(x=hasil_pompa, color='Purple', linestyle='--', linewidth=2, label=f'Hasil: {hasil_pompa:.2f}')
ax1.set_title("Hasil Defuzzifikasi - Durasi Pompa Air")
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)
st.pyplot(fig1)

st.markdown("---")

# --- PLOT 2: KIPAS EXHAUST ---
fig2, ax2 = plt.subplots(figsize=(8, 3.5))
ax2.plot(x_kipas, kipas['lambat'].mf, 'b', linewidth=1.5, label='Lambat')
ax2.plot(x_kipas, kipas['sedang'].mf, 'g', linewidth=1.5, label='Sedang')
ax2.plot(x_kipas, kipas['cepat'].mf, 'r', linewidth=1.5, label='Cepat')
m_lambat = fuzz.interp_membership(x_kipas, kipas['lambat'].mf, hasil_kipas)
m_ksedang = fuzz.interp_membership(x_kipas, kipas['sedang'].mf, hasil_kipas)
m_cepat   = fuzz.interp_membership(x_kipas, kipas['cepat'].mf, hasil_kipas)
kipas_activation = np.fmax(np.fmin(m_lambat, kipas['lambat'].mf),
                           np.fmax(np.fmin(m_ksedang, kipas['sedang'].mf),
                                   np.fmin(m_cepat, kipas['cepat'].mf)))
ax2.fill_between(x_kipas, 0, kipas_activation, facecolor='Cyan', alpha=0.4)
ax2.axvline(x=hasil_kipas, color='Purple', linestyle='--', linewidth=2, label=f'Hasil: {hasil_kipas:.2f}')
ax2.set_title("Hasil Defuzzifikasi - Kipas Exhaust")
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)
st.pyplot(fig2)

st.markdown("---")

# --- PLOT 3: LAMPU UV ---
fig3, ax3 = plt.subplots(figsize=(8, 3.5))
ax3.plot(x_lampu, lampu['mati_redup'].mf, 'b', linewidth=1.5, label='Mati/Redup')
ax3.plot(x_lampu, lampu['sedang'].mf, 'g', linewidth=1.5, label='Sedang')
ax3.plot(x_lampu, lampu['terang'].mf, 'r', linewidth=1.5, label='Terang')
m_mredup = fuzz.interp_membership(x_lampu, lampu['mati_redup'].mf, hasil_lampu)
m_lsedang = fuzz.interp_membership(x_lampu, lampu['sedang'].mf, hasil_lampu)
m_terang  = fuzz.interp_membership(x_lampu, lampu['terang'].mf, hasil_lampu)
lampu_activation = np.fmax(np.fmin(m_mredup, lampu['mati_redup'].mf),
                           np.fmax(np.fmin(m_lsedang, lampu['sedang'].mf),
                                   np.fmin(m_terang, lampu['terang'].mf)))
ax3.fill_between(x_lampu, 0, lampu_activation, facecolor='Magenta', alpha=0.4)
ax3.axvline(x=hasil_lampu, color='Purple', linestyle='--', linewidth=2, label=f'Hasil: {hasil_lampu:.2f}')
ax3.set_title("Hasil Defuzzifikasi - Daya Lampu UV")
ax3.legend(loc='upper right')
ax3.grid(True, alpha=0.3)
st.pyplot(fig3)