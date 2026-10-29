import streamlit as st
import pandas as pd
import json
import os
import calendar
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from docx import Document
from io import BytesIO

# ==========================================
# 1. KONFIGURASI HALAMAN & STYLING
# ==========================================
st.set_page_config(
    page_title="Sistem Terpadu Pembelajaran & Administrasi Guru",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {
        border-radius: 12px;
    }
    .header-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-box h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 1.8rem;
    }
    .header-box p {
        color: #e0e6ed !important;
        margin: 5px 0 0 0;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SINKRONISASI GOOGLE SHEETS API
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        return gspread.authorize(creds)
    return None

SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID", "1o-xa_G7Vt8l4wrSrPl6AVAmhr7MXJ-AVyZf35mrW1Bc")
client = get_gspread_client()

def load_data_from_sheet(sheet_name):
    if client:
        try:
            sh = client.open_by_key(SPREADSHEET_ID)
            worksheet = sh.worksheet(sheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception:
            return None
    return None

def save_data_to_sheet(sheet_name, df):
    if client:
        try:
            sh = client.open_by_key(SPREADSHEET_ID)
            try:
                worksheet = sh.worksheet(sheet_name)
            except Exception:
                worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols="40")
            
            worksheet.clear()
            df_to_save = df.astype(object).fillna("")
            worksheet.update([df_to_save.columns.values.tolist()] + df_to_save.values.tolist())
            return True
        except Exception as e:
            st.error(f"Gagal menyimpan ke Google Sheets: {e}")
            return False
    return False

# ==========================================
# 3. DATASET SISWA & HELPER CSV
# ==========================================
DUMMY_SISWA = {
    "Kelas 7A": [
        "Aditya Naufal Pratama", "Zidan Al Fatir", "Atika Zahara Ratifa", "Ayu Azka Fariha",
        "Dini Khoirunisa", "Enjelita Laia", "Ervan Martio Armana", "Farisman Lase", "Fauzia",
        "Hendriyanto", "M Sahel Habibillah", "Okta Dita Pranata", "Rahmad Ramadhani",
        "Yuda Agustian FitRoh", "Yulia Ramadhani", "Marveltus Hia", "Muhammad Rhaehan A"
    ],
    "Kelas 7B": [
        "Aal- Bar", "Ahmad Rehan Zainudin", "Bela Anggraini Nurmalasari", "Durrotul Zahiya",
        "Marhan", "Muhammmad Ardiansyah", "Muhammad Iqbal", "Muhammad Irfan Zaki",
        "Muhammad Restu Adillah", "Nadiya Maulida Husna"
    ],
    "Kelas 8": [
        "Adiba Khazahra", "Ahmad Ovianto", "Ahmad Rifandi Praditya", "Alif Al Hambia",
        "Andi Saputra Hia", "Anisa Rahmawati", "Aprilia Armanda", "Bagas Prakoso",
        "Desi Rahmadani", "Desta Angga Syahputra", "Edward Alexis Saragi", "Faris Ramadani",
        "Irwansyah Alexsander", "Juandra Zebua", "Juwita", "Lenta Mentari", "Lisa Sri Utami",
        "M Zibran Fatturaman", "Maulana Malik Ibrahim", "Muhammad Pahri", "Muhammad Afrizal",
        "Muhammad Amin", "Naomi Sepriyani", "Nzawa Khaira Wilda", "Nurmayanti",
        "Q Vela Br Situmorang", "Ratna Sari Dewi", "Riski Muhammad Nur Fahmi", "Safitri Nurfadilah",
        "Selvi", "Adistya Mahardika", "Mareti Wakha", "Andini puji lestari"
    ],
    "Kelas 9": [
        "Abelia", "Alfinus", "Arifki", "Felicita", "Hendra", "Heri", "Hezekiel", "Lesi", 
        "Marhadi", "Melfin", "Meriati", "M. Ali", "M. Huda", "M. Alif", "M. Fauzan", 
        "Naufal", "Putra", "Putri", "Rafa", "Reno", "Rizky", "Robi", "Saputra", 
        "Selly", "Selvi", "Suci", "Yestina"
    ]
}

def load_materi_json():
    file_path = os.path.join(BASE_DIR, "materi.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_data_siswa(kelas_nama):
    possible_filenames = [
        f"{kelas_nama.upper()}.csv",
        f"{kelas_nama}.csv",
        f"{kelas_nama.lower()}.csv",
        f"KELAS {kelas_nama.replace('Kelas ', '')}.csv"
    ]
    
    for filename in possible_filenames:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            try:
                df_csv = pd.read_csv(filepath)
                if not df_csv.empty and "Nama" in df_csv.columns:
                    return df_csv
            except Exception:
                pass

    list_nama = DUMMY_SISWA.get(kelas_nama, DUMMY_SISWA["Kelas 7A"])
    jk_list = ["L" if i % 2 == 0 else "P" for i in range(len(list_nama))]
    return pd.DataFrame({"No": range(1, len(list_nama) + 1), "Nama": list_nama, "Jenis Kelamin": jk_list})

DATABASE_MATERI = load_materi_json()

# ==========================================
# 4. JADWAL MENGAJAR & KALENDER DINAMIS
# ==========================================
JADWAL_GURU = {
    ("PPKn", "Kelas 7A"): [0], # Senin
    ("IPS", "Kelas 7A"): [3],  # Kamis
    ("PPKn", "Kelas 7B"): [1], # Selasa
    ("IPS", "Kelas 7B"): [2],  # Rabu
    ("PPKn", "Kelas 8"): [3],  # Kamis
    ("IPS", "Kelas 8"): [1],   # Selasa
    ("PPKn", "Kelas 9"): [4],  # Jumat
    ("IPS", "Kelas 9"): [0],   # Senin
}

DAFTAR_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

BULAN_MAP = {b: i+1 for i, b in enumerate(DAFTAR_BULAN)}
HARI_SINGKAT = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Ming"]

def get_jadwal_tanggal(mapel, kelas, bulan_nama, tahun_str):
    try:
        tahun_val = int(tahun_str.split("/")[0])
    except Exception:
        tahun_val = 2026
        
    bulan_num = BULAN_MAP.get(bulan_nama, 10)
    hari_target = JADWAL_GURU.get((mapel, kelas), [0, 1, 2, 3, 4])
    
    cal = calendar.Calendar()
    list_tgl = []
    
    for day_obj in cal.itermonthdates(tahun_val, bulan_num):
        if day_obj.month == bulan_num and day_obj.weekday() in hari_target:
            nama_hari = HARI_SINGKAT[day_obj.weekday()]
            tgl_formatted = f"{nama_hari}, {day_obj.day:02d}"
            list_tgl.append(tgl_formatted)
            
    return list_tgl if list_tgl else ["Sesi 1", "Sesi 2", "Sesi 3", "Sesi 4"]

# ==========================================
# 5. SIDEBAR PANEL
# ==========================================
with st.sidebar:
    st.markdown("### 👨‍🏫 Identitas Pengajar")
    sekolah = st.text_input("Nama Sekolah", "SMP RSUP PKB Pulau Burung")
    penyusun = st.text_input("Nama Guru / Penyusun", "Ridho Kurniawan, S.Pd.")
    
    st.divider()
    st.markdown("### 🏫 Pengaturan Kelas, Mapel & Bulan")
    
    mapel_aktif = st.selectbox("Pilih Mata Pelajaran", ["PPKn", "IPS"])
    kelas_aktif = st.selectbox("Pilih Kelas Aktif", ["Kelas 7A", "Kelas 7B", "Kelas 8", "Kelas 9"], index=2)
    
    bulan_aktif = st.selectbox(
        "Pilih Bulan Presensi",
        DAFTAR_BULAN,
        index=9  # Default Oktober
    )
    tahun = st.text_input("Tahun Pelajaran", "2026/2027")
    semester = st.selectbox("Semester", ["Ganjil", "Genap"])
    
    st.divider()
    
    # CARA AMAN REFRESH SISWA TANPA ERROR
    if st.button("🔄 Sync Siswa Baru dari CSV", type="secondary"):
        st.cache_data.clear()
        st.session_state.clear()
        st.success("✅ Data berhasil diperbarui!")
        st.rerun()

    if client:
        st.success("🟢 Otentikasi Google Sheets API Aktif!")
    else:
        st.warning("⚠️ Google Sheets API Belum Terkonfigurasi.")

DF_SISWA_AKTIF = get_data_siswa(kelas_aktif)
JUMLAH_KOLOM_NILAI = 15
KATEGORI_NILAI_OPSI = [
    "Nilai Kehadiran (Otomatis)", "Tugas Individu", "Tugas Kelompok", "Projek / Praktik", "UTS / Mid Semester", "UAS / Akhir Semester"
]

# ==========================================
# 6. SINKRONISASI DATA SESSION STATE & GOOGLE SHEETS
# ==========================================
tahun_clean = tahun.replace("/", "_")
key_p = f"presensi_{mapel_aktif}_{kelas_aktif}_{bulan_aktif}_{tahun_clean}"
key_n = f"nilai_{mapel_aktif}_{kelas_aktif}"

sheet_p_name = f"Presensi_{mapel_aktif}_{kelas_aktif}_{bulan_aktif}"
sheet_n_name = f"Nilai_{mapel_aktif}_{kelas_aktif}"

TANGGAL_JADWAL = get_jadwal_tanggal(mapel_aktif, kelas_aktif, bulan_aktif, tahun)

# --- PRESENSI DINAMIS ---
if key_p not in st.session_state:
    df_cloud_p = load_data_from_sheet(sheet_p_name)
    df_base = DF_SISWA_AKTIF[["No", "Nama", "Jenis Kelamin"]].copy()
    
    if df_cloud_p is not None and not df_cloud_p.empty and "Nama" in df_cloud_p.columns:
        df_p = pd.merge(df_base, df_cloud_p, on="Nama", how="left")
        if "No_x" in df_p.columns:
            df_p["No"] = df_p["No_x"]
            df_p.drop(columns=["No_x", "No_y"], inplace=True, errors='ignore')
        if "Jenis Kelamin_x" in df_p.columns:
            df_p["Jenis Kelamin"] = df_p["Jenis Kelamin_x"].fillna(df_p["Jenis Kelamin_y"])
            df_p.drop(columns=["Jenis Kelamin_x", "Jenis Kelamin_y"], inplace=True, errors='ignore')
    else:
        df_p = df_base.copy()

    for t in TANGGAL_JADWAL:
        if t not in df_p.columns:
            df_p[t] = ""
            
    st.session_state[key_p] = df_p

# --- BUKU NILAI ---
if key_n not in st.session_state:
    df_cloud_n = load_data_from_sheet(sheet_n_name)
    df_base_n = DF_SISWA_AKTIF[["No", "Nama", "Jenis Kelamin"]].copy()
    
    if df_cloud_n is not None and not df_cloud_n.empty and "Nama" in df_cloud_n.columns:
        df_n = pd.merge(df_base_n, df_cloud_n, on="Nama", how="left")
        if "No_x" in df_n.columns:
            df_n["No"] = df_n["No_x"]
            df_n.drop(columns=["No_x", "No_y"], inplace=True, errors='ignore')
        if "Jenis Kelamin_x" in df_n.columns:
            df_n["Jenis Kelamin"] = df_n["Jenis Kelamin_x"].fillna(df_n["Jenis Kelamin_y"])
            df_n.drop(columns=["Jenis Kelamin_x", "Jenis Kelamin_y"], inplace=True, errors='ignore')
    else:
        df_n = df_base_n.copy()

    for i in range(1, JUMLAH_KOLOM_NILAI + 1):
        col_name = f"Nilai {i}"
        if col_name not in df_n.columns:
            df_n[col_name] = None
            
    st.session_state[key_n] = df_n

# ==========================================
# 7. HEADER BANNER
# ==========================================
st.markdown(f"""
    <div class="header-box">
        <h1>🎓 Portal Administrasi & Pembelajaran Guru</h1>
        <p>Selamat datang, <b>{penyusun}</b> | {sekolah} | Mapel: <b>{mapel_aktif}</b> | <b>{kelas_aktif}</b> ({bulan_aktif} {tahun} - Semester {semester})</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📑 Generator Modul Ajar", 
    f"📋 Presensi ({mapel_aktif} - {kelas_aktif} - {bulan_aktif})", 
    f"📊 Buku Nilai & KKTP ({mapel_aktif} - {kelas_aktif})"
])

# ------------------------------------------
# TAB 1: GENERATOR MODUL AJAR
# ------------------------------------------
with tab1:
    st.subheader("⚙️ Konfigurasi Modul Ajar Kurikulum Merdeka (Deep Learning)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**📖 Materi & Kurikulum**")
            if not DATABASE_MATERI:
                mapel_selected = st.selectbox("Mata Pelajaran Modul", ["Pendidikan Pancasila (PPKn)", "Ilmu Pengetahuan Sosial (IPS)"], index=0 if mapel_aktif=="PPKn" else 1)
                kelas_selected = st.selectbox("Jenjang Kelas Modul", ["Kelas VII", "Kelas VIII", "Kelas IX"])
                bab_selected = st.text_input("Bab / Tema Utama", "Bab 1: Kondisi Geografis dan Pelestarian SDA")
                subbab_selected = st.text_input("Sub-Materi / Subbab", "Peran Lembaga Sosial dalam Pemanfaatan SDA dan SDM")
            else:
                default_mapel_idx = 0 if mapel_aktif == "PPKn" else 1
                mapel_selected = st.selectbox("Mata Pelajaran Modul", list(DATABASE_MATERI.keys()), index=min(default_mapel_idx, len(DATABASE_MATERI)-1))
                kelas_selected = st
