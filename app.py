import streamlit as st
import pandas as pd
import json
import os
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
    .section-badge {
        background-color: #eef2f6;
        color: #1e3c72;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 10px;
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
            df_filled = df.fillna("")
            worksheet.update([df_filled.columns.values.tolist()] + df_filled.values.tolist())
            return True
        except Exception as e:
            st.error(f"Gagal menyimpan ke Google Sheets: {e}")
            return False
    return False

# ==========================================
# 3. DATASET SISWA DUMMY (FALLBACK)
# ==========================================
DUMMY_SISWA = {
    "Kelas 7A": [
        "Aditya Naufal Pratama", "Zidan Al Fatir", "Atika Zahara Ratifa", "Ayu Azka Fariha",
        "Dini Khoirunisa", "Enjelita Laia", "Ervan Martio Armana", "Farisman Lase", "Fauzia",
        "Hendriyanto", "M Sahel Habibillah", "Okta Dita Pranata", "Rahmad Ramadhani",
        "Yuda Agustian FitRoh", "Yulia Ramadhani", "Marveltus Hia", "Muhammad Rhaehan A"
    ],
    "Kelas 7B": [
        "Ahmad Albar", "Bagas Saputra", "Citra Kirana", "Dedi Kurniawan", "Eka Putri",
        "Fahri Hamzah", "Gita Gutawa", "Hafiz Ridho", "Indah Permata", "Joko Susilo"
    ],
    "Kelas 8": [
        "Andi Wijaya", "Budi Santoso", "Cici Paramida", "Doni Monardo", "Eva Celia"
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
    list_nama = DUMMY_SISWA.get(kelas_nama, DUMMY_SISWA["Kelas 7A"])
    jk_list = ["L" if i % 2 == 0 else "P" for i in range(len(list_nama))]
    return pd.DataFrame({"No": range(1, len(list_nama) + 1), "Nama": list_nama, "Jenis Kelamin": jk_list})

DATABASE_MATERI = load_materi_json()

# ==========================================
# 4. SIDEBAR PANEL
# ==========================================
with st.sidebar:
    st.markdown("### 👨‍🏫 Identitas Pengajar")
    sekolah = st.text_input("Nama Sekolah", "SMP RSUP PKB Pulau Burung")
    penyusun = st.text_input("Nama Guru / Penyusun", "Ridho Kurniawan, S.Pd.")
    
    st.divider()
    st.markdown("### 🏫 Pengaturan Kelas & Semester")
    kelas_aktif = st.selectbox(
        "Pilih Kelas Aktif",
        ["Kelas 7A", "Kelas 7B", "Kelas 8", "Kelas 9"],
        index=0
    )
    tahun = st.text_input("Tahun Pelajaran", "2026/2027")
    semester = st.selectbox("Semester", ["Ganjil", "Genap"])
    
    st.divider()
    if client:
        st.success("🟢 Otentikasi Google Sheets API Aktif (Auto Sync)!")
    else:
        st.warning("⚠️ Google Sheets API Belum Terkonfigurasi di Secrets.")

DF_SISWA_AKTIF = get_data_siswa(kelas_aktif)
JUMLAH_KOLOM_NILAI = 15
KATEGORI_NILAI_OPSI = [
    "Tugas Individu", "Tugas Kelompok", "Projek / Praktik", "UTS / Mid Semester", "UAS / Akhir Semester"
]

# ==========================================
# 5. SINKRONISASI SESSION STATE & GOOGLE SHEETS
# ==========================================
key_p = f"presensi_{kelas_aktif}"
key_n = f"nilai_{kelas_aktif}"

if key_p not in st.session_state:
    df_cloud_p = load_data_from_sheet(f"Presensi_{kelas_aktif}")
    if df_cloud_p is not None and not df_cloud_p.empty:
        st.session_state[key_p] = df_cloud_p
    else:
        df_p = DF_SISWA_AKTIF.copy()
        for t in range(1, 32):
            df_p[str(t)] = ""
        st.session_state[key_p] = df_p

if key_n not in st.session_state:
    df_cloud_n = load_data_from_sheet(f"Nilai_{kelas_aktif}")
    if df_cloud_n is not None and not df_cloud_n.empty:
        st.session_state[key_n] = df_cloud_n
    else:
        df_n = DF_SISWA_AKTIF.copy()
        for i in range(1, JUMLAH_KOLOM_NILAI + 1):
            df_n[f"Nilai {i}"] = None
        st.session_state[key_n] = df_n

# ==========================================
# 6. HEADER BANNER
# ==========================================
st.markdown(f"""
    <div class="header-box">
        <h1>🎓 Portal Administrasi & Pembelajaran Guru</h1>
        <p>Selamat datang, <b>{penyusun}</b> | {sekolah} | <b>{kelas_aktif}</b> ({tahun} - Semester {semester})</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📑 Generator Modul Ajar", 
    f"📋 Buku Presensi ({kelas_aktif})", 
    f"📊 Buku Nilai & KKTP ({kelas_aktif})"
])

# ------------------------------------------
# TAB 1: GENERATOR MODUL AJAR
# ------------------------------------------
with tab1:
    st.subheader("Konfigurasi Modul Ajar")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            if not DATABASE_MATERI:
                mapel_selected = st.selectbox("Mata Pelajaran", ["IPS", "PPKn"])
                kelas_selected = st.selectbox("Jenjang Kelas Modul", ["Kelas 7", "Kelas 8", "Kelas 9"])
                bab_selected = st.text_input("Bab / Tema Utama", "Bab 1: Kehidupan Sosial")
                subbab_selected = st.text_input("Sub-Materi / Subbab", "Interaksi Sosial")
            else:
                mapel_selected = st.selectbox("Mata Pelajaran", list(DATABASE_MATERI.keys()))
                kelas_selected = st.selectbox("Jenjang Kelas Modul", list(DATABASE_MATERI[mapel_selected].keys()))
                bab_dict = DATABASE_MATERI[mapel_selected][kelas_selected]
                bab_selected = st.selectbox("Bab / Tema Utama", list(bab_dict.keys()))
                subbab_selected = st.selectbox("Sub-Materi / Subbab", bab_dict[bab_selected])

    with col_b:
        with st.container(border=True):
            alokasi = st.text_input("Alokasi Waktu", "2 JP (2 Pertemuan x 1 JP)")

    modul_text = f"""MODUL AJAR KURIKULUM MERDEKA
MATA PELAJARAN: {mapel_selected.upper()}
• Sekolah: {sekolah} | Guru: {penyusun}
• Kelas: {kelas_selected} | Bab: {bab_selected} | Subbab: {subbab_selected}
"""
    def export_word(text):
        doc = Document()
        for p in text.split('\n'):
            doc.add_paragraph(p)
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf

    st.download_button(
        label="📥 Download Modul Ajar (.docx)",
        data=export_word(modul_text),
        file_name=f"Modul_Ajar_{mapel_selected}_{kelas_selected}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )

# ------------------------------------------
# TAB 2: BUKU PRESENSI
# ------------------------------------------
with tab2:
    st.subheader(f"📖 Buku Presensi Harian ({kelas_aktif})")
    bulan_presensi = st.selectbox(
        "Pilih Bulan Presensi",
        ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"],
        index=8,
        key=f"bln_{kelas_aktif}"
    )

    df_p_curr = st.session_state[key_p].copy()
    tgl_cols = [str(t) for t in range(1, 32)]

    col_config_p = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="medium"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    for t in tgl_cols:
        col_config_p[t] = st.column_config.TextColumn(t, width="small")

    df_upper = df_p_curr[tgl_cols].fillna("").apply(lambda x: x.astype(str).str.upper())
    df_p_curr["H"] = (df_upper == "H").sum(axis=1)
    df_p_curr["S"] = (df_upper == "S").sum(axis=1)
    df_p_curr["I"] = (df_upper == "I").sum(axis=1)
    df_p_curr["A"] = (df_upper == "A").sum(axis=1)

    col_config_p["H"] = st.column_config.NumberColumn("H", disabled=True, width="small")
    col_config_p["S"] = st.column_config.NumberColumn("S", disabled=True, width="small")
    col_config_p["I"] = st.column_config.NumberColumn("I", disabled=True, width="small")
    col_config_p["A"] = st.column_config.NumberColumn("A", disabled=True, width="small")

    edited_p = st.data_editor(
        df_p_curr,
        column_config=col_config_p,
        disabled=["No", "Nama", "Jenis Kelamin", "H", "S", "I", "A"],
        hide_index=True,
        use_container_width=True,
        key=f"editor_p_{kelas_aktif}"
    )
    
    st.session_state[key_p] = edited_p[DF_SISWA_AKTIF.columns.tolist() + tgl_cols]

    if st.button(f"💾 Simpan Presensi {kelas_aktif} ke Google Sheets", type="primary"):
        if save_data_to_sheet(f"Presensi_{kelas_aktif}", edited_p):
            st.success("✅ Data Presensi Berhasil Disimpan Permanen ke Google Sheets!")

# ------------------------------------------
# TAB 3: BUKU NILAI & KKTP
# ------------------------------------------
with tab3:
    st.subheader(f"📊 Buku Nilai & Akumulasi Realtime ({kelas_aktif})")
    
    df_nilai_current = st.session_state[key_n].copy()
    column_config_n = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="large"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    kolom_nilai_keys = [f"Nilai {i}" for i in range(1, JUMLAH_KOLOM_NILAI + 1)]
    
    for k in kolom_nilai_keys:
        column_config_n[k] = st.column_config.NumberColumn(
            k, min_value=0.0, max_value=100.0, format="%.1f", width="medium"
        )
    
    df_numeric = df_nilai_current[kolom_nilai_keys].apply(pd.to_numeric, errors='coerce')
    df_nilai_current["Nilai Akhir (Akumulasi)"] = df_numeric.mean(axis=1).round(2)
    column_config_n["Nilai Akhir (Akumulasi)"] = st.column_config.NumberColumn(
        "📊 Nilai Akhir", disabled=True, format="%.2f", width="medium"
    )

    edited_n = st.data_editor(
        df_nilai_current,
        column_config=column_config_n,
        disabled=["No", "Nama", "Jenis Kelamin", "Nilai Akhir (Akumulasi)"],
        hide_index=True,
        use_container_width=True,
        key=f"editor_n_{kelas_aktif}"
    )
    st.session_state[key_n] = edited_n[DF_SISWA_AKTIF.columns.tolist() + kolom_nilai_keys]

    if st.button(f"💾 Simpan Nilai {kelas_aktif} ke Google Sheets", type="primary"):
        if save_data_to_sheet(f"Nilai_{kelas_aktif}", edited_n):
            st.success("✅ Data Nilai Berhasil Disimpan Permanen ke Google Sheets!")
