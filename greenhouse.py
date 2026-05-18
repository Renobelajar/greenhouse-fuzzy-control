import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import streamlit as st

# ==========================================
# CONFIGURASI HALAMAN STREAMLIT (BONUS)
# ==========================================
st.set_page_config(page_title="Responsi IF-A - Smart Greenhouse", layout="wide")
st.title("Sistem Kendali Otomatis Smart Greenhouse")
st.write("Implementasi Logika Fuzzy Mamdani - Praktikum SC & PK.")
st.markdown("---")

# ==========================================
# 1. DEFINISI VARIABEL & SEMESTA PEMBICARAAN
# ==========================================
# Variabel Input (Sesuai Ketentuan Soal)
suhu = ctrl.Antecedent(np.arange(0, 41, 1), 'suhu')            # Rentang Semesta: 0-40
kelembapan = ctrl.Antecedent(np.arange(0, 101, 1), 'kelembapan') # Rentang Semesta: 0-100
cahaya = ctrl.Antecedent(np.arange(0, 101, 1), 'cahaya')        # Rentang Semesta: 0-100

# Variabel Output (Sesuai Ketentuan Soal)
pompa = ctrl.Consequent(np.arange(0, 61, 1), 'pompa')          # Rentang Semesta: 0-60
kipas = ctrl.Consequent(np.arange(0, 101, 1), 'kipas')        # Rentang Semesta: 0-100
lampu = ctrl.Consequent(np.arange(0, 101, 1), 'lampu')        # Rentang Semesta: 0-100


# ==========================================
# 2. FUNGSI KEANGGOTAAN (MEMBERSHIP FUNCTIONS)
# ==========================================
# a. Suhu Lingkungan
suhu['dingin'] = fuzz.trapmf(suhu.universe, [0, 0, 15, 22])
suhu['normal'] = fuzz.trimf(suhu.universe, [18, 25, 30])
suhu['panas'] = fuzz.trapmf(suhu.universe, [27, 32, 40, 40])

# b. Kelembapan Tanah
kelembapan['kering'] = fuzz.trapmf(kelembapan.universe, [0, 0, 0, 40])
kelembapan['ideal'] = fuzz.trimf(kelembapan.universe, [30, 50, 70])
kelembapan['basah'] = fuzz.trapmf(kelembapan.universe, [60, 100, 100, 100])

# c. Cahaya Matahari
cahaya['gelap'] = fuzz.trapmf(cahaya.universe, [0, 0, 20, 40])
cahaya['redup'] = fuzz.trimf(cahaya.universe, [30, 50, 70])
cahaya['terang'] = fuzz.trapmf(cahaya.universe, [60, 90, 100, 100])

# d. Output: Durasi Pompa Air
pompa['singkat'] = fuzz.trapmf(pompa.universe, [0, 0, 0, 20])
pompa['sedang'] = fuzz.trimf(pompa.universe, [15, 30, 45])
pompa['lama'] = fuzz.trapmf(pompa.universe, [40, 60, 60, 60])

# e. Output: Kipas Exhaust
kipas['lambat'] = fuzz.trapmf(kipas.universe, [0, 0, 25, 50])
kipas['sedang'] = fuzz.trimf(kipas.universe, [35, 60, 80])
kipas['cepat'] = fuzz.trapmf(kipas.universe, [70, 90, 100, 100])

# f. Output: Lampu UV
lampu['mati_redup'] = fuzz.trapmf(lampu.universe, [0, 0, 0, 40])
lampu['sedang'] = fuzz.trimf(lampu.universe, [20, 50, 80])
lampu['terang'] = fuzz.trapmf(lampu.universe, [60, 100, 100, 100])


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

# Nilai default otomatis diset berdasarkan instruksi soal simulasi:
# Suhu: 30, Kelembapan: 35, Cahaya: 25
input_suhu = st.sidebar.slider("Suhu Lingkungan (°C)", 0.0, 40.0, 30.0, step=0.5)
input_kelembapan = st.sidebar.slider("Kelembapan Tanah (%)", 0.0, 100.0, 35.0, step=1.0)
input_cahaya = st.sidebar.slider("Cahaya Matahari (Lux/100)", 0.0, 100.0, 25.0, step=1.0)

# Masukkan nilai input ke dalam simulasi
simulasi.input['suhu'] = input_suhu
simulasi.input['kelembapan'] = input_kelembapan
simulasi.input['cahaya'] = input_cahaya

# Jalankan Proses Defuzzifikasi
simulasi.compute()

# Ambil nilai murni hasil output
hasil_pompa = simulasi.output['pompa']
hasil_kipas = simulasi.output['kipas']
hasil_lampu = simulasi.output['lampu']


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
# 7. MENAMPILKAN GRAFIK ARSIR OUTPUT
# ==========================================
st.subheader("Grafik Arsir Hasil Defuzzifikasi Pada Kurva Output")

# Membuat subplot berukuran 3 baris untuk menampung masing-masing grafik output
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(10, 14))

# Kurva Output Pompa Air dengan Arsir Hasil
pompa.view(sim=simulasi, ax=ax0)
ax0.set_title("Hasil Defuzzifikasi - Durasi Pompa Air", fontsize=12, fontweight='bold')
ax0.grid(True, linestyle='--', alpha=0.6)

# Kurva Output Kipas dengan Arsir Hasil
kipas.view(sim=simulasi, ax=ax1)
ax1.set_title("Hasil Defuzzifikasi - Kipas Exhaust", fontsize=12, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)

# Kurva Output Lampu dengan Arsir Hasil
lampu.view(sim=simulasi, ax=ax2)
ax2.set_title("Hasil Defuzzifikasi - Daya Lampu UV", fontsize=12, fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.6)

# Render gambar ke dalam dashboard Streamlit
plt.tight_layout()
st.pyplot(fig)