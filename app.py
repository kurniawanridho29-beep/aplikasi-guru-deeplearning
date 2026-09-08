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
        st.success("🟢 Otentikasi Google Sheets API Aktif!")
    else:
        st.warning("⚠️ Google Sheets API Belum Terkonfigurasi.")

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
# TAB 1: GENERATOR MODUL AJAR (DEEP LEARNING MODEL FULL TEMPLATE)
# ------------------------------------------
with tab1:
    st.subheader("Konfigurasi Modul Ajar Kurikulum Merdeka (Deep Learning Model)")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            if not DATABASE_MATERI:
                mapel_selected = st.selectbox("Mata Pelajaran", ["Ilmu Pengetahuan Sosial (IPS)", "Pendidikan Pancasila (PPKn)"])
                kelas_selected = st.selectbox("Jenjang Kelas Modul", ["Kelas VII", "Kelas VIII", "Kelas IX"])
                bab_selected = st.text_input("Bab / Tema Utama", "Bab 1: Perubahan Sosial dan Globalisasi")
                subbab_selected = st.text_input("Sub-Materi / Subbab", "Dampak Modernisasi & Globalisasi")
            else:
                mapel_selected = st.selectbox("Mata Pelajaran", list(DATABASE_MATERI.keys()))
                kelas_selected = st.selectbox("Jenjang Kelas Modul", list(DATABASE_MATERI[mapel_selected].keys()))
                bab_dict = DATABASE_MATERI[mapel_selected][kelas_selected]
                bab_selected = st.selectbox("Bab / Tema Utama", list(bab_dict.keys()))
                subbab_selected = st.selectbox("Sub-Materi / Subbab", bab_dict[bab_selected])

    with col_b:
        with st.container(border=True):
            fase_selected = st.selectbox("Fase", ["Fase D", "Fase E"])
            alokasi = st.text_input("Alokasi Waktu", "2 JP (2 Pertemuan x 1 JP)")

    def generate_full_modul_doc(sekolah, penyusun, mapel, kelas, fase, semester, tahun, bab, subbab, alokasi):
        doc = Document()
        
        # Title
        p_title = doc.add_paragraph()
        run_title = p_title.add_run("MODUL AJAR KURIKULUM MERDEKA (DEEP LEARNING MODEL)\n")
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
        p_ka.add_run("• Peserta didik telah memahami konsep dasar kehidupan bermasyarakat dan lingkungan sosial sekitar.\n")
        p_ka.add_run(f"• Peserta didik memiliki kemampuan awal dalam mengidentifikasi fenomena sosial/pancasila terkait {subbab} di lingkungan sehari-hari.")

        doc.add_heading("PROFIL PELAJAR PANCASILA", level=2)
        p_p3 = doc.add_paragraph()
        p_p3.add_run("• Beriman, Bertakwa kepada Tuhan YME, dan Berakhlak Mulia: Menghargai keberagaman dan norma sosial.\n")
        p_p3.add_run("• Bernalar Kritis: Mampu menganalisis fenomena sosial secara objektif dan berbasis data.\n")
        p_p3.add_run("• Gotong Royong: Berkolaborasi secara efektif dalam diskusi kelompok dan penyelesaian tugas bersama.\n")
        p_p3.add_run(f"• Kreatif: Menghasilkan karya/solusi inovatif terkait topik {subbab}.")

        doc.add_heading("SARANA DAN PRASARANA", level=2)
        p_sp = doc.add_paragraph()
        p_sp.add_run("• Media: Laptop, Proyektor, Peta Konseptual/Digital, Slide Presentasi, Artikel Kasus, Lembar Kerja Peserta Didik (LKPD).\n")
        p_sp.add_run(f"• Sumber Belajar: Buku Paket Siswa Kurikulum Merdeka {mapel}, Artikel Berita, Lingkungan Sekitar Sekolah.")

        doc.add_heading("TARGET PESERTA DIDIK", level=2)
        p_tp_d = doc.add_paragraph()
        p_tp_d.add_run("• Target: Peserta didik reguler / tipikal (tidak ada kesulitan dalam memahami materi ajar).\n")
        p_tp_d.add_run("• Model Pembelajaran: Deep Learning Model (Mindful, Meaningful, & Joyful Learning) dengan pendekatan Problem-Based Learning (PBL).")

        doc.add_heading("II. KOMPONEN INTI", level=1)
        
        doc.add_heading("TUJUAN PEMBELAJARAN (TP)", level=2)
        p_tp = doc.add_paragraph()
        p_tp.add_run(f"1. Peserta didik mampu mendeskripsikan dan menganalisis konsep {subbab} dengan tepat.\n")
        p_tp.add_run(f"2. Peserta didik mampu mengidentifikasi serta memecahkan masalah kontekstual yang berkaitan dengan {bab} di kehidupan nyata.\n")
        p_tp.add_run(f"3. Peserta didik mampu menyajikan hasil analisis dan solusi kreatif mengenai {subbab} melalui presentasi atau media visual.")

        doc.add_heading("PEMAHAMAN BERMAKNA (MEANINGFUL LEARNING)", level=2)
        p_mb = doc.add_paragraph()
        p_mb.add_run(f"Pemahaman terhadap {subbab} membantu peserta didik menyadari peran aktifnya sebagai warga negara yang bijak, kritis, dan bertanggung jawab di tengah kehidupan sosial masyarakat.")

        doc.add_heading("PERTANYAAN PEMANTIK", level=2)
        p_pp = doc.add_paragraph()
        p_pp.add_run(f"1. Mengapa topik {subbab} sangat dekat dan penting dalam kehidupan sehari-hari kita?\n")
        p_pp.add_run(f"2. Dampak apa yang akan terjadi jika kita tidak memahami dan menerapkan prinsip {bab} di masyarakat?")

        doc.add_heading("III. KEGIATAN PEMBELAJARAN DETAIL", level=1)
        
        doc.add_heading("PENDAHULUAN (15 MENIT) - Mindful Start", level=2)
        p_pen = doc.add_paragraph()
        p_pen.add_run("• Pembukaan & Orientasi: Guru menyapa siswa hangat, memimpin doa, mengecek kesiapan belajar, dan memeriksa presensi.\n")
        p_pen.add_run(f"• Apersepsi Mindful: Guru mengajak siswa melakukan komparasi singkat antara pengetahuan awal mereka dengan fenomena riil {subbab}.\n")
        p_pen.add_run(f"• Penyampaian Tujuan: Guru memaparkan tujuan pembelajaran hari ini, tahapan kegiatan, serta bentuk penilaian fokus sub-materi {subbab}.\n")
        p_pen.add_run(f"• Pertanyaan Pemantik: Guru melemparkan pertanyaan pemantik untuk memicu minat dan daya kritis siswa terhadap topik {subbab}.")

        doc.add_heading("KEGIATAN INTI (80 MENIT) - Meaningful & Joyful Learning", level=2)
        p_inti = doc.add_paragraph()
        p_inti.add_run(f"1. Eksplorasi Konsep & Orientasi Masalah (~15-20 Menit):\n")
        p_inti.add_run(f"   - Peserta didik mencermati tayangan visual/studi kasus faktual mengenai {subbab}.\n")
        p_inti.add_run(f"   - Guru memfasilitasi penjelajahan konsep dasar terkait sub-materi {subbab} secara dialogis dan interaktif menggunakan metode Studi Kasus / Storytelling.\n\n")
        p_inti.add_run(f"2. Kolaborasi Kelompok & Penyelidikan (~45 Menit):\n")
        p_inti.add_run(f"   - Peserta didik dibagi ke dalam kelompok kecil heterogen (4-5 siswa) menerapkan sintaks Discovery Learning.\n")
        p_inti.add_run(f"   - Masing-masing kelompok mendalami lembar kerja (LKPD) yang memuat problematik nyata terkait {subbab}.\n")
        p_inti.add_run(f"   - Guru melakukan pendampingan terarah (scaffolding) pada kelompok yang membutuhkan penguatan pemahaman.\n\n")
        p_inti.add_run(f"3. Unjuk Karya & Diskusi Pleno (~15-20 Menit):\n")
        p_inti.add_run(f"   - Perwakilan kelompok mempresentasikan analisis dan rekomendasi solusi sub-materi {subbab} di depan kelas.\n")
        p_inti.add_run(f"   - Kelompok lain memberikan tanggapan, sanggahan santun, atau pertanyaan konstruktif (Joyful interaction).")

        doc.add_heading("PENUTUP (15 MENIT) - Deep Reflection", level=2)
        p_penutup = doc.add_paragraph()
        p_penutup.add_run(f"• Sintesis & Rangkuman: Guru bersama siswa merangkum poin kunci dan kesimpulan utama dari pembahasan {subbab}.\n")
        p_penutup.add_run(f"• Refleksi Deep Learning: Peserta didik merefleksikan proses belajar: 'Apa pemahaman baru terbesar yang saya dapatkan dari sub-materi {subbab}?'\n")
        p_penutup.add_run("• Apresiasi & Tindak Lanjut: Guru memberikan apresiasi atas partisipasi aktif kelas, menyampaikan pengantar materi untuk pertemuan berikutnya, dan menutup dengan doa bersama.")

        doc.add_heading("IV. ASESMEN PEMBELAJARAN (PENILAIAN)", level=1)
        p_as = doc.add_paragraph()
        p_as.add_run("• Asesmen Sikap: Observasi Profil Pelajar Pancasila (Bernalar Kritis, Gotong Royong, Mandiri).\n")
        p_as.add_run("• Asesmen Formatif: Penilaian Diskusi Kelompok, Observasi Kesiapan, dan Pengerjaan LKPD.\n")
        p_as.add_run(f"• Asesmen Sumatif: Tes Tertulis Pilihan Ganda / Uraian Analitis mengenai {subbab}.")

        doc.add_heading("V. LAMPIRAN MODUL AJAR", level=1)
        
        doc.add_heading("A. LEMBAR KERJA PESERTA DIDIK (LKPD) DEEP LEARNING", level=2)
        p_lkpd = doc.add_paragraph()
        p_lkpd.add_run(f"Nama Kelompok : ....................................\nKelas : {kelas}\nAnggota Kelompok : 1. ..... 2. ..... 3. ..... 4. .....\n\n")
        p_lkpd.add_run("PETUNJUK DISKUSI:\n")
        p_lkpd.add_run(f"1. Simaklah tayangan video/artikel mengenai fenomena {subbab} yang diputar/dibagikan di depan kelas dengan saksama.\n")
        p_lkpd.add_run("2. Catatlah poin-poin penting selama materi berlangsung.\n")
        p_lkpd.add_run("3. Diskusikan dan jawablah pertanyaan analisis di bawah ini bersama anggota kelompokmu.\n\n")
        
        p_lkpd.add_run("PERTANYAAN ANALISIS KASUS (RUMUS 3-T):\n").bold = True
        p_lkpd.add_run("1. TEKNOLOGI PENDORONG (T-1):\n   Berdasarkan materi, sarana atau teknologi apa saja yang menjadi jalan utama sehingga fenomena ini memengaruhi masyarakat dengan cepat?\n\n")
        p_lkpd.add_run(f"2. TANTANGAN DAN DAMPAK (T-2):\n   Amatilah perubahan perilaku masyarakat akibat {subbab}. Tuliskan 2 dampak positif dan 2 dampak negatifnya!\n   - Dampak Positif: 1. ..... 2. .....\n   - Dampak Negatif: 1. ..... 2. .....\n\n")
        p_lkpd.add_run("3. TINDAKAN DAN SOLUSI (T-3):\n   Sebagai generasi muda yang bijak, tindakan nyata apa yang harus kalian lakukan agar tetap bisa berkembang tanpa kehilangan identitas dan moral bangsa?\n\n")
        p_lkpd.add_run("\"Nilai-nilai luhur bangsa adalah jangkar kita di tengah arus perubahan zaman.\"\n")

        doc.add_heading("B. RUBRIK PENILAIAN DISKUSI & UNJUK KARYA", level=2)
        table = doc.add_table(rows=4, cols=5)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Kriteria Penilaian'
        hdr_cells[1].text = 'Sangat Baik (4)'
        hdr_cells[2].text = 'Baik (3)'
        hdr_cells[3].text = 'Cukup (2)'
        hdr_cells[4].text = 'Perlu Bimbingan (1)'
        
        row1 = table.rows[1].cells
        row1[0].text = 'Penguasaan Materi'
        row1[1].text = f'Menjelaskan {subbab} sangat akurat & analitis'
        row1[2].text = 'Menjelaskan materi dengan akurat'
        row1[3].text = 'Menjelaskan materi cukup akurat'
        row1[4].text = 'Kurang memahami materi'

        row2 = table.rows[2].cells
        row2[0].text = 'Kerjasama Kelompok'
        row2[1].text = 'Semua anggota aktif dan saling mendukung'
        row2[2].text = 'Sebagian besar anggota aktif'
        row2[3].text = 'Hanya sebagian anggota aktif'
        row2[4].text = 'Pasif dalam kelompok'

        row3 = table.rows[3].cells
        row3[0].text = 'Kreativitas Produk'
        row3[1].text = 'Sangat kreatif, rapi, dan komunikatif'
        row3[2].text = 'Kreatif dan rapi'
        row3[3].text = 'Cukup rapi'
        row3[4].text = 'Kurang rapi / Less visual'

        # Tanda Tangan
        doc.add_paragraph("\n\n")
        p_ttd = doc.add_paragraph()
        p_ttd.add_run("Mengetahui,\t\t\t\t\t\tGuru Mata Pelajaran\nKepala Sekolah\n\n\n\n").bold = True
        p_ttd.add_run(f"( .................................................... )\t\t\t\t({penyusun})")

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf

    buf_doc = generate_full_modul_doc(sekolah, penyusun, mapel_selected, kelas_selected, fase_selected, semester, tahun, bab_selected, subbab_selected, alokasi)

    st.download_button(
        label="📥 Download Modul Ajar Deep Learning Lengkap (.docx)",
        data=buf_doc,
        file_name=f"Modul_Ajar_DeepLearning_{mapel_selected}_{kelas_selected}.docx",
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
    
    with st.expander("📌 Pengaturan Kategori/Jenis Penilaian per Kolom", expanded=True):
        st.write("Silakan tentukan jenis penilaian untuk masing-masing kolom di bawah ini:")
        cols_kat = st.columns(5)
        kategori_terpilih = {}
        for i in range(1, JUMLAH_KOLOM_NILAI + 1):
            col_idx = (i - 1) % 5
            with cols_kat[col_idx]:
                kategori_terpilih[f"Nilai {i}"] = st.selectbox(
                    f"Kolom Nilai {i}",
                    options=KATEGORI_NILAI_OPSI,
                    index=0 if i <= 10 else 1,
                    key=f"kat_n_{kelas_aktif}_{i}"
                )

    df_nilai_current = st.session_state[key_n].copy()
    
    column_config_n = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="medium"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    
    kolom_nilai_keys = [f"Nilai {i}" for i in range(1, JUMLAH_KOLOM_NILAI + 1)]
    
    for k in kolom_nilai_keys:
        label_kat = kategori_terpilih[k]
        column_config_n[k] = st.column_config.NumberColumn(
            f"{k} ({label_kat})",
            min_value=0.0,
            max_value=100.0,
            format="%.1f",
            width="medium"
        )
    
    df_numeric = df_nilai_current[kolom_nilai_keys].apply(pd.to_numeric, errors='coerce')
    df_nilai_current["📊 Nilai Akhir"] = df_numeric.mean(axis=1).round(2)
    
    column_config_n["📊 Nilai Akhir"] = st.column_config.NumberColumn(
        "📊 Nilai Akhir", disabled=True, format="%.2f", width="medium"
    )

    edited_n = st.data_editor(
        df_nilai_current,
        column_config=column_config_n,
        disabled=["No", "Nama", "Jenis Kelamin", "📊 Nilai Akhir"],
        hide_index=True,
        use_container_width=True,
        key=f"editor_n_{kelas_aktif}"
    )
    
    st.session_state[key_n] = edited_n[DF_SISWA_AKTIF.columns.tolist() + kolom_nilai_keys]

    st.markdown("---")
    if st.button(f"💾 Simpan Buku Nilai {kelas_aktif} ke Google Sheets", type="primary"):
        if save_data_to_sheet(f"Nilai_{kelas_aktif}", edited_n):
            st.success("✅ Data Buku Nilai Berhasil Disimpan Permanen ke Google Sheets!")
