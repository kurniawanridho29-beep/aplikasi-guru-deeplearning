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
    possible_filenames = [
        f"{kelas_nama.upper()}.csv",
        f"{kelas_nama}.csv",
        f"{kelas_nama.lower()}.csv"
    ]
    
    for filename in possible_filenames:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            try:
                df_csv = pd.read_csv(filepath)
                if not df_csv.empty:
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
# 5. SIDEBAR PANEL (TERMASUK BULAN)
# ==========================================
with st.sidebar:
    st.markdown("### 👨‍🏫 Identitas Pengajar")
    sekolah = st.text_input("Nama Sekolah", "SMP RSUP PKB Pulau Burung")
    penyusun = st.text_input("Nama Guru / Penyusun", "Ridho Kurniawan, S.Pd.")
    
    st.divider()
    st.markdown("### 🏫 Pengaturan Kelas, Mapel & Bulan")
    
    mapel_aktif = st.selectbox("Pilih Mata Pelajaran", ["PPKn", "IPS"])
    kelas_aktif = st.selectbox("Pilih Kelas Aktif", ["Kelas 7A", "Kelas 7B", "Kelas 8", "Kelas 9"], index=1)
    
    bulan_aktif = st.selectbox(
        "Pilih Bulan Presensi",
        DAFTAR_BULAN,
        index=9  # Default Oktober
    )
    tahun = st.text_input("Tahun Pelajaran", "2026/2027")
    semester = st.selectbox("Semester", ["Ganjil", "Genap"])
    
    st.divider()
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
    if df_cloud_p is None or df_cloud_p.empty:
        df_old_p = load_data_from_sheet(f"Presensi_{kelas_aktif}")
        if df_old_p is not None and not df_old_p.empty:
            df_cloud_p = df_old_p.copy()

    if df_cloud_p is not None and not df_cloud_p.empty:
        for t in TANGGAL_JADWAL:
            if t not in df_cloud_p.columns:
                df_cloud_p[t] = ""
        st.session_state[key_p] = df_cloud_p
    else:
        df_p = DF_SISWA_AKTIF.copy()
        for t in TANGGAL_JADWAL:
            df_p[t] = ""
        st.session_state[key_p] = df_p

# --- BUKU NILAI ---
if key_n not in st.session_state:
    df_cloud_n = load_data_from_sheet(sheet_n_name)
    if df_cloud_n is None or df_cloud_n.empty:
        df_old_n = load_data_from_sheet(f"Nilai_{kelas_aktif}")
        if df_old_n is not None and not df_old_n.empty:
            df_cloud_n = df_old_n.copy()

    if df_cloud_n is not None and not df_cloud_n.empty:
        st.session_state[key_n] = df_cloud_n
    else:
        df_n = DF_SISWA_AKTIF.copy()
        for i in range(1, JUMLAH_KOLOM_NILAI + 1):
            df_n[f"Nilai {i}"] = None
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
# TAB 1: GENERATOR MODUL AJAR (DEEP LEARNING)
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
                kelas_selected = st.selectbox("Jenjang Kelas Modul", list(DATABASE_MATERI[mapel_selected].keys()))
                bab_dict = DATABASE_MATERI[mapel_selected][kelas_selected]
                bab_selected = st.selectbox("Bab / Tema Utama", list(bab_dict.keys()))
                subbab_selected = st.selectbox("Sub-Materi / Subbab", bab_dict[bab_selected])
            
            fase_selected = st.selectbox("Fase", ["Fase D", "Fase E"])
            alokasi = st.text_input("Alokasi Waktu", "2 JP (2 Pertemuan x 1 JP)")

    with col_b:
        with st.container(border=True):
            st.markdown("**🎯 Strategi Deep Learning & Bentuk LKPD**")
            
            model_selected = st.selectbox(
                "Model Pembelajaran Deep Learning",
                [
                    "Problem-Based Learning (PBL) - Deep Learning",
                    "Project-Based Learning (PjBL) - Deep Learning",
                    "Inquiry / Contextual Learning - Deep Learning"
                ]
            )
            
            metode_selected = st.selectbox(
                "Metode Pembelajaran Deep Learning",
                [
                    "Studi Kasus & Analisis Berita",
                    "Diskusi Kelompok & Debat Kontekstual",
                    "Simulasi / Bermain Peran",
                    "Tanya Jawab Sokratik"
                ]
            )
            
            tipe_lkpd = st.selectbox(
                "Bentuk dan Karakteristik LKPD Deep Learning",
                [
                    "LKPD Investigasi & Analisis Masalah",
                    "LKPD Berbasis Proyek (Jurnal Kegiatan / Logbook)",
                    "LKPD Reflektif & Argumentatif"
                ]
            )

    def generate_custom_modul_doc(sekolah, penyusun, mapel, kelas, fase, semester, tahun, bab, subbab, alokasi, model, metode, lkpd_choice):
        doc = Document()
        p_title = doc.add_paragraph()
        run_title = p_title.add_run("MODUL AJAR KURIKULUM MERDEKA (DEEP LEARNING)\n")
        run_title.bold = True
        p_title.add_run(f"MATA PELAJARAN: {mapel.upper()}\nSTANDAR KEPUTUSAN BSKAP NOMOR 046/H/KR/2025").bold = True

        doc.add_heading("I. INFORMASI UMUM", level=1)
        doc.add_heading("IDENTITAS MODUL", level=2)
        p_id = doc.add_paragraph()
        p_id.add_run(f"Nama Sekolah: {sekolah}\n")
        p_id.add_run(f"Nama Penyusun: {penyusun}\n")
        p_id.add_run(f"Mata Pelajaran: {mapel}\n")
        p_id.add_run(f"Kelas / Fase / Semester: {kelas} / {fase} / {semester}\n")
        p_id.add_run(f"Bab / Tema Utama: {bab}\n")
        p_id.add_run(f"Sub-Materi Pembelajaran: {subbab}\n")
        p_id.add_run(f"Alokasi Waktu: {alokasi}\n")
        p_id.add_run(f"Tahun Pelajaran: {tahun}")

        doc.add_heading("KOMPETENSI AWAL", level=2)
        p_ka = doc.add_paragraph()
        p_ka.add_run(f"• Peserta didik telah membaca konsep awal mengenai {subbab}.\n")
        p_ka.add_run(f"• Peserta didik dapat mengidentifikasi masalah kontekstual seputar {bab} di lingkungan sekolah dan rumah.")

        doc.add_heading("PROFIL PELAJAR PANCASILA", level=2)
        p_p3 = doc.add_paragraph()
        p_p3.add_run("• Beriman, Bertakwa kepada Tuhan YME, dan Berakhlak Mulia: Menumbuhkan etika & tanggung jawab sosial.\n")
        p_p3.add_run("• Bernalar Kritis: Mampu membedah akar masalah dan memvalidasi kebenaran informasi.\n")
        p_p3.add_run("• Gotong Royong: Berkolaborasi aktif menyelesaikan penugasan kelompok.\n")
        p_p3.add_run(f"• Kreatif: Menghasilkan karya/solusi inovatif terkait {subbab}.")

        doc.add_heading("SARANA DAN PRASARANA", level=2)
        p_sp = doc.add_paragraph()
        p_sp.add_run("• Media Pembelajaran: Artikel Berkas Kasus, Lembar Kerja Peserta Didik (LKPD), Proyektor & Slide.\n")
        p_sp.add_run(f"• Sumber Belajar: Buku Teks Utama {mapel}, Lingkungan Sekitar Siswa, Sumber Berita Terpercaya.")

        doc.add_heading("TARGET PESERTA DIDIK & STRATEGI PEMBELAJARAN DEEP LEARNING", level=2)
        p_tp_d = doc.add_paragraph()
        p_tp_d.add_run("• Target Peserta Didik: Peserta didik reguler / tipikal.\n")
        p_tp_d.add_run(f"• Model Pembelajaran: {model}\n")
        p_tp_d.add_run(f"• Metode Pembelajaran: {metode}\n")
        p_tp_d.add_run(f"• Karakteristik LKPD: {lkpd_choice}")

        doc.add_heading("II. KOMPONEN INTI", level=1)
        doc.add_heading("TUJUAN PEMBELAJARAN (TP)", level=2)
        p_tp = doc.add_paragraph()
        p_tp.add_run(f"1. Peserta didik dapat menganalisis secara mendalam konsep {subbab}.\n")
        p_tp.add_run(f"2. Peserta didik mampu menguraikan solusi logis terhadap permasalahan terkait {bab} dengan pendekatan {metode}.\n")
        p_tp.add_run(f"3. Peserta didik mampu mempresentasikan dan mempertahankan argumen hasil analisis kelompok di depan kelas.")

        doc.add_heading("PEMAHAMAN BERMAKNA (DEEP LEARNING)", level=2)
        p_mb = doc.add_paragraph()
        p_mb.add_run(f"Pemahaman mendalam mengenai {subbab} melatih siswa berpikir logis dan sistematis, sehingga mampu mengambil keputusan yang bertanggung jawab sebagai warga masyarakat.")

        doc.add_heading("PERTANYAAN PEMANTIK (PERTANYAAN SOKRATIK)", level=2)
        p_pp = doc.add_paragraph()
        p_pp.add_run(f"1. Mengapa isu {subbab} ini bisa terjadi di sekitar kita dan apa akar penyebab utamanya?\n")
        p_pp.add_run(f"2. Apa dampak yang paling terasa jika masalah pada {bab} tidak segera diselesaikan secara bijak?")

        doc.add_heading("III. KEGIATAN PEMBELAJARAN DETAIL", level=1)
        doc.add_heading("PENDAHULUAN (15 MENIT) - Mindful Start & Orientasi", level=2)
        p_pen = doc.add_paragraph()
        p_pen.add_run("• Orientasi Kelas: Guru menyapa peserta didik, memimpin doa, dan memeriksa kehadiran.\n")
        p_pen.add_run(f"• Apersepsi Mindful: Guru mengajukan pertanyaan pemantik sokratik untuk memicu pemikiran kritis awal siswa mengenai {subbab}.\n")
        p_pen.add_run(f"• Penyampaian Tujuan: Guru memaparkan tujuan pembelajaran serta alur kegiatan berorientasi {model}.")

        doc.add_heading(f"KEGIATAN INTI (50 MENIT) - Deep Learning Process ({model})", level=2)
        p_inti = doc.add_paragraph()
        
        if "Problem-Based Learning" in model:
            p_inti.add_run(f"1. Orientasi Masalah (~10 Menit):\n   Guru menyajikan studi kasus/berita nyata terkait {subbab} yang memerlukan pemecahan masalah.\n\n")
            p_inti.add_run(f"2. Mengorganisasi Siswa untuk Belajar (~5 Menit):\n   Siswa dibagi menjadi kelompok diskusi dan dibagikan {lkpd_choice}.\n\n")
            p_inti.add_run(f"3. Membimbing Penyelidikan Kelompok ({metode}) (~20 Menit):\n   Siswa mendiskusikan akar masalah, membedah data, dan merumuskan alternatif solusi kontekstual.\n\n")
            p_inti.add_run(f"4. Mengembangkan & Menyajikan Hasil Karya (~15 Menit):\n   Setiap kelompok mempresentasikan solusi mereka dan melakukan tanya jawab dengan kelompok lain.")
        elif "Project-Based Learning" in model:
            p_inti.add_run(f"1. Pertanyaan Mendasar & Perancangan Proyek (~10 Menit):\n   Guru memberikan tantangan proyek terkait {subbab} dan membantu siswa menyusun rencana karya.\n\n")
            p_inti.add_run(f"2. Menyusun Jadwal & Logbook Kegiatan (~5 Menit):\n   Siswa membagi peran dalam kelompok dan mencatat langkah kerja pada {lkpd_choice}.\n\n")
            p_inti.add_run(f"3. Pelaksanaan & Penerapan Metode ({metode}) (~20 Menit):\n   Siswa memproduksi draft/prototype produk kampanye/riset dengan bimbingan terarah dari guru.\n\n")
            p_inti.add_run(f"4. Penilaian & Evaluasi Proyek (~15 Menit):\n   Siswa menampilkan produk proyek mereka dan menerima masukan konstruktif dari teman sejawat.")
        else:
            p_inti.add_run(f"1. Eksplorasi Konteks Lingkungan (~10 Menit):\n   Siswa mengamati fenomena nyata seputar {subbab} yang relevan dengan kehidupan sehari-hari.\n\n")
            p_inti.add_run(f"2. Merumuskan Hipotesis & Pertanyaan (~5 Menit):\n   Siswa mencatat poin penting dan pertanyaan investigatif pada {lkpd_choice}.\n\n")
            p_inti.add_run(f"3. Analisis & Pembuktian ({metode}) (~20 Menit):\n   Siswa mengumpulkan bukti empiris dan memverifikasi keterkaitan teori dengan realita di lapangan.\n\n")
            p_inti.add_run(f"4. Komunikasi & Generalisasi (~15 Menit):\n   Siswa menyimpulkan prinsip dasar materi berdasarkan bukti-bukti yang telah dianalisis.")

        doc.add_heading("PENUTUP (15 MENIT) - Refleksi Metakognisi", level=2)
        p_penutup = doc.add_paragraph()
        p_penutup.add_run(f"• Sintesis Materi: Guru dan peserta didik menyimpulkan gagasan utama dari {subbab}.\n")
        p_penutup.add_run("• Refleksi Metakognitif: Siswa mengisi pertanyaan refleksi di LKPD (menilai apa yang dipahami dan argumen personal).\n")
        p_penutup.add_run("• Apresiasi & Tindak Lanjut: Guru memberikan pujian atas keaktifan siswa dan menutup kelas dengan doa bersama.")

        doc.add_heading("IV. ASESMEN PEMBELAJARAN", level=1)
        p_as = doc.add_paragraph()
        p_as.add_run("• Asesmen Sikap: Observasi Profil Pelajar Pancasila (Bernalar Kritis, Gotong Royong, Kreatif).\n")
        p_as.add_run(f"• Asesmen Formatif: Observasi Proses Keaktifan Diskusi / Penerapan Metode {metode}.\n")
        p_as.add_run(f"• Asesmen Sumatif: Laporan Akhir & Hasil Pengisian {lkpd_choice}.")

        doc.add_heading("V. LAMPIRAN: LEMBAR KERJA PESERTA DIDIK (LKPD DEEP LEARNING)", level=1)
        doc.add_heading(f"LEMBAR KERJA PESERTA DIDIK: {lkpd_choice.upper()}", level=2)
        p_lkpd = doc.add_paragraph()
        p_lkpd.add_run(f"Nama Kelompok : ....................................\nKelas : {kelas}\nAnggota Kelompok : 1. ..... 2. ..... 3. ..... 4. .....\n\n")
        
        if "Investigasi" in lkpd_choice:
            p_lkpd.add_run("BAGIAN 1: TEKS KASUS & ANALISIS MASALAH KONTEKSTUAL\nBacalah kasus mengenai isu sosial/masyarakat di bawah ini, kemudian identifikasi akar masalahnya!\n\n").bold = True
            p_lkpd.add_run("[ RUANG TEKS KASUS ATAU BERITA ]\n\n")
            p_lkpd.add_run("BAGIAN 2: TABEL ANALISIS AKAR MASALAH DAN SOLUSI\n").bold = True
            table_m = doc.add_table(rows=4, cols=4)
            table_m.style = 'Table Grid'
            hdr = table_m.rows[0].cells
            hdr[0].text = 'No'
            hdr[1].text = 'Masalah Utama'
            hdr[2].text = 'Akar Penyebab'
            hdr[3].text = 'Alternatif Solusi'
            for i in range(1, 4):
                table_m.rows[i].cells[0].text = str(i)
            p_lkpd.add_run("\nBAGIAN 3: JUSTIFIKASI ARGUMEN KELOMPOK\nJelaskan alasan logis mengapa solusi yang kelompok kalian pilih adalah yang paling tepat:\nJawaban: ....................................................................................................................................................................................................................................................................................").bold = True
        elif "Proyek" in lkpd_choice:
            p_lkpd.add_run("BAGIAN 1: PERANCANGAN PROYEK (PERENCANAAN)\n").bold = True
            p_lkpd.add_run(f"Judul Proyek / Produk : .....\nTarget Sasaran Proyek : .....\nAlasan Pemilihan Proyek : ....................................................................................\n\n")
            p_lkpd.add_run("BAGIAN 2: LOGBOOK / JURNAL KONTROL KEGIATAN PROYEK\n").bold = True
            table_p = doc.add_table(rows=4, cols=4)
            table_p.style = 'Table Grid'
            hdr = table_p.rows[0].cells
            hdr[0].text = 'Tahapan'
            hdr[1].text = 'Rencana Kegiatan'
            hdr[2].text = 'Penanggung Jawab'
            hdr[3].text = 'Status / Progres'
            table_p.rows[1].cells[0].text = 'Persiapan'
            table_p.rows[2].cells[0].text = 'Pelaksanaan'
            table_p.rows[3].cells[0].text = 'Finishing'
            p_lkpd.add_run("\nBAGIAN 3: EVALUASI HASIL KARYA PROYEK\nTuliskan kendala utama yang dihadapi saat pembuatan proyek dan bagaimana cara mengatasinya:\nJawaban: ....................................................................................................................................................................................................................................................................................").bold = True
        else:
            p_lkpd.add_run("BAGIAN 1: PENALARAN ARGUMENTATIF KONTEKSTUAL\n").bold = True
            p_lkpd.add_run(f"Berdasarkan topik {subbab}, kemukakan pendapat kelompokmu mengenai kondisi di bawah ini dan sertakan alasan logisnya!\n")
            p_lkpd.add_run("Pernyataan Diskusi : ....................................................................................\n")
            p_lkpd.add_run("Pendapat Kelompok  : [ Setuju / Tidak Setuju ]\n")
            p_lkpd.add_run("Alasan Justifikasi : ....................................................................................................................................................................................................................................................................................\n\n")
            p_lkpd.add_run("BAGIAN 2: PERTANYAAN METAKOGNISI (REFLEKSI DIRI)\n").bold = True
            p_lkpd.add_run("1. Satu hal paling penting dan berharga yang saya pelajari hari ini adalah:\n   Jawaban: ....................................................................................................\n")
            p_lkpd.add_run("2. Bagian materi mana yang menurut saya masih menantang dan perlu dipelajari lebih lanjut?\n   Jawaban: ....................................................................................................\n")

        doc.add_heading("RUBRIK PENILAIAN DEEP LEARNING", level=2)
        table_r = doc.add_table(rows=3, cols=5)
        table_r.style = 'Table Grid'
        hdr_cells = table_r.rows[0].cells
        hdr_cells[0].text = 'Kriteria'
        hdr_cells[1].text = 'Sangat Baik (4)'
        hdr_cells[2].text = 'Baik (3)'
        hdr_cells[3].text = 'Cukup (2)'
        hdr_cells[4].text = 'Perlu Bimbingan (1)'
        
        row1 = table_r.rows[1].cells
        row1[0].text = 'Bernalar Kritis'
        row1[1].text = 'Analisis mendalam & solutif'
        row1[2].text = 'Analisis cukup mendalam'
        row1[3].text = 'Jawaban masih umum'
        row1[4].text = 'Belum mampu menganalisis'

        row2 = table_r.rows[2].cells
        row2[0].text = 'Argumen & Refleksi'
        row2[1].text = 'Argumen logis & metakognisi jelas'
        row2[2].text = 'Argumen logis'
        row2[3].text = 'Refleksi kurang lengkap'
        row2[4].text = 'Belum mengisi refleksi'

        doc.add_paragraph("\n\n")
        p_ttd = doc.add_paragraph()
        p_ttd.add_run("Mengetahui,\t\t\t\t\t\tGuru Mata Pelajaran\nKepala Sekolah\n\n\n\n").bold = True
        p_ttd.add_run(f"( .................................................... )\t\t\t\t({penyusun})")

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf

    buf_doc = generate_custom_modul_doc(
        sekolah, penyusun, mapel_selected, kelas_selected, fase_selected, 
        semester, tahun, bab_selected, subbab_selected, alokasi, 
        model_selected, metode_selected, tipe_lkpd
    )

    st.download_button(
        label="📥 Download Modul Ajar Deep Learning (.docx)",
        data=buf_doc,
        file_name=f"Modul_Ajar_DeepLearning_{mapel_selected}_{kelas_selected}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )

# ------------------------------------------
# TAB 2: BUKU PRESENSI DINAMIS & DROPDOWN SELECTBOX
# ------------------------------------------
with tab2:
    st.subheader(f"📖 Buku Presensi Harian ({mapel_aktif} - {kelas_aktif} - Bulan {bulan_aktif})")
    st.caption(f"🗓️ Kolom tanggal otomatis disesuaikan dengan Jadwal KBM {mapel_aktif} di {kelas_aktif} pada bulan {bulan_aktif}.")

    df_p_curr = st.session_state[key_p].copy()
    
    # Menyiapkan kolom tanggal mengajar
    for col in TANGGAL_JADWAL:
        if col not in df_p_curr.columns:
            df_p_curr[col] = ""

    # Konfigurasi kolom presensi dengan Dropdown Selectbox (H, S, I, A)
    col_config_p = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="medium"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    
    # Menghubungkan dropdown H, S, I, A ke setiap sel tanggal
    for t in TANGGAL_JADWAL:
        col_config_p[t] = st.column_config.SelectboxColumn(
            label=t,
            options=["", "H", "S", "I", "A"],
            required=False,
            width="small"
        )

    # Hitung Rekapitulasi Kehadiran Realtime
    df_upper = df_p_curr[TANGGAL_JADWAL].fillna("").apply(lambda x: x.astype(str).str.upper())
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
        key=f"editor_p_{mapel_aktif}_{kelas_aktif}_{bulan_aktif}"
    )
    
    cols_to_keep = [c for c in DF_SISWA_AKTIF.columns if c in edited_p.columns] + TANGGAL_JADWAL
    st.session_state[key_p] = edited_p[cols_to_keep]

    # --- SINKRONISASI OTOMATIS NILAI PRESENSI KE BUKU NILAI (MAX 75 / PAS KKM) ---
    total_pertemuan = len(TANGGAL_JADWAL)
    if total_pertemuan > 0:
        # Bobot: Hadir (H) = 75.0 (Pas KKM), Sakit/Izin (S/I) = 60.0, Alpa/Kosong = 0.0
        skor_h = (df_upper == "H").sum(axis=1) * 75.0
        skor_s = (df_upper == "S").sum(axis=1) * 60.0
        skor_i = (df_upper == "I").sum(axis=1) * 60.0
        
        # Kalkulasi Nilai Kehadiran Penunjang Maksimal 75
        nilai_presensi_calc = ((skor_h + skor_s + skor_i) / total_pertemuan).round(1)
        
        # Masukkan otomatis ke Kolom Nilai 1 (Nilai Kehadiran Penunjang) pada Buku Nilai Mapel & Kelas Aktif
        st.session_state[key_n]["Nilai 1"] = nilai_presensi_calc

    if st.button(f"💾 Simpan Presensi {mapel_aktif} {kelas_aktif} ({bulan_aktif}) ke Google Sheets", type="primary"):
        if save_data_to_sheet(sheet_p_name, edited_p):
            save_data_to_sheet(sheet_n_name, st.session_state[key_n])
            st.success(f"✅ Presensi & Nilai Kehadiran Otomatis Bulan {bulan_aktif} Berhasil Disimpan!")

# ------------------------------------------
# TAB 3: BUKU NILAI & KKTP
# ------------------------------------------
with tab3:
    st.subheader(f"📊 Buku Nilai & Akumulasi Realtime ({mapel_aktif} - {kelas_aktif})")
    
    with st.expander("📌 Pengaturan Kategori/Jenis Penilaian per Kolom", expanded=True):
        st.write("Silakan tentukan jenis penilaian untuk masing-masing kolom di bawah ini:")
        cols_kat = st.columns(5)
        kategori_terpilih = {}
        
        # Kolom Nilai 1 dikunci khusus untuk Nilai Kehadiran Otomatis
        kategori_terpilih["Nilai 1"] = "Nilai Kehadiran (Otomatis)"
        with cols_kat[0]:
            st.text_input("Kolom Nilai 1", "Nilai Kehadiran (Otomatis)", disabled=True, key=f"kat_n_1_dis_{mapel_aktif}_{kelas_aktif}")
            
        for i in range(2, JUMLAH_KOLOM_NILAI + 1):
            col_idx = (i - 1) % 5
            with cols_kat[col_idx]:
                kategori_terpilih[f"Nilai {i}"] = st.selectbox(
                    f"Kolom Nilai {i}",
                    options=KATEGORI_NILAI_OPSI[1:],
                    index=0 if i <= 10 else 1,
                    key=f"kat_n_{mapel_aktif}_{kelas_aktif}_{i}"
                )

    df_nilai_current = st.session_state[key_n].copy()
    
    column_config_n = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="medium"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    
    kolom_nilai_keys = [f"Nilai {i}" for i in range(1, JUMLAH_KOLOM_NILAI + 1)]
    for k in kolom_nilai_keys:
        if k not in df_nilai_current.columns:
            df_nilai_current[k] = None
        label_kat = kategori_terpilih[k]
        
        is_disabled = True if k == "Nilai 1" else False
        column_config_n[k] = st.column_config.NumberColumn(
            f"{k} ({label_kat})",
            min_value=0.0,
            max_value=100.0,
            format="%.1f",
            width="medium",
            disabled=is_disabled
        )
    
    df_numeric = df_nilai_current[kolom_nilai_keys].apply(pd.to_numeric, errors='coerce')
    df_nilai_current["📊 Nilai Akhir"] = df_numeric.mean(axis=1).round(2)
    
    column_config_n["📊 Nilai Akhir"] = st.column_config.NumberColumn(
        "📊 Nilai Akhir", disabled=True, format="%.2f", width="medium"
    )

    edited_n = st.data_editor(
        df_nilai_current,
        column_config=column_config_n,
        disabled=["No", "Nama", "Jenis Kelamin", "Nilai 1", "📊 Nilai Akhir"],
        hide_index=True,
        use_container_width=True,
        key=f"editor_n_{mapel_aktif}_{kelas_aktif}"
    )
    
    cols_n_keep = [c for c in DF_SISWA_AKTIF.columns if c in edited_n.columns] + kolom_nilai_keys
    st.session_state[key_n] = edited_n[cols_n_keep]

    st.markdown("---")
    if st.button(f"💾 Simpan Buku Nilai {mapel_aktif} {kelas_aktif} ke Google Sheets", type="primary"):
        if save_data_to_sheet(sheet_n_name, edited_n):
            st.success(f"✅ Data Buku Nilai Mapel {mapel_aktif} Berhasil Disimpan Permanen ke Sheet {sheet_n_name}!")
