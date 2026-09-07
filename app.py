import streamlit as st
import pandas as pd
import json
import os
from docx import Document
from io import BytesIO
from datetime import date

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM STYLING (CSS)
# ==========================================
st.set_page_config(
    page_title="Sistem Terpadu Pembelajaran & Administrasi Guru",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS untuk Tampilan Modern
st.markdown("""
    <style>
    /* Styling Container & Card */
    div[data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {
        border-radius: 12px;
    }
    
    /* Header Banner Custom */
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

    /* Subheader Badges */
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
# 2. DATASET SISWA DUMMY (FALLBACK)
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
        "Fahri Hamzah", "Gita Gutawa", "Hafiz Ridho", "Indah Permata", "Joko Susilo",
        "Kurnia Dewi", "Lutfi Hakim", "M. Rizky Pratama", "Nabila Syakieb", "Oki Setiana"
    ],
    "Kelas 8": [
        "Andi Wijaya", "Budi Santoso", "Cici Paramida", "Doni Monardo", "Eva Celia",
        "Fajar Sadboy", "Grace Natalie", "Hendra Setiawan", "Irfan Bachdim", "Joni Suprianto",
        "Kiki Amalia", "Lesti Andryani", "M. Ahsan", "Nia Ramadhani", "Olivia Jensen"
    ],
    "Kelas 9": [
        "Ahmad Dhani", "Baim Wong", "Cinta Laura", "Deddy Corbuzier", "El Rumi",
        "Fadil Jaidi", "Gading Marten", "Habib Jafar", "Isyana Sarasvati", "Jerome Polin",
        "Kaesang Pangarep", "Livie Renata", "M. Atta Halilintar", "Najwa Shihab", "Onadio Leonardo"
    ]
}

# ==========================================
# 3. FUNGSI LOAD DATA
# ==========================================
@st.cache_data
def load_materi_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "materi.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_data_siswa(kelas_nama):
    """Mencoba membaca file CSV (misal: kelas 7a.csv atau kelas 8.csv). Jika tidak ditemukan, gunakan dummy."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = f"{kelas_nama.lower()}.csv"  # contoh: kelas 7a.csv atau kelas 8.csv
    file_path = os.path.join(base_dir, file_name)
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, sep=None, engine="python")
            df.columns = [c.strip() for c in df.columns]
            return df
        except Exception:
            pass

    # Jika file CSV tidak ada, gunakan dataset dummy bawaan
    list_nama = DUMMY_SISWA.get(kelas_nama, DUMMY_SISWA["Kelas 7A"])
    jk_list = ["L" if i % 2 == 0 else "P" for i in range(len(list_nama))]
    
    return pd.DataFrame({
        "No": range(1, len(list_nama) + 1),
        "Nama": list_nama,
        "Jenis Kelamin": jk_list
    })

DATABASE_MATERI = load_materi_json()

# ==========================================
# 4. SIDEBAR PANEL (PROFIL GURU & KELAS)
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
    st.caption("✨ **Aplikasi Administrasi Guru**\nKurikulum Merdeka BSKAP 2025")

# Load Data Siswa Sesuai Kelas Yang Dipilih
DF_SISWA_AKTIF = get_data_siswa(kelas_aktif)

# ==========================================
# 5. INISIALISASI SESSION STATE PER KELAS
# ==========================================
key_p = f"presensi_{kelas_aktif}"
key_n = f"nilai_{kelas_aktif}"

if key_p not in st.session_state:
    df_p = DF_SISWA_AKTIF.copy()
    df_p["Status"] = "Hadir"
    df_p["Keterangan"] = "-"
    st.session_state[key_p] = df_p

if key_n not in st.session_state:
    df_n = DF_SISWA_AKTIF.copy()
    df_n["Formatif (30%)"] = 80.0
    df_n["Sumatif (30%)"] = 80.0
    df_n["STS (20%)"] = 80.0
    df_n["SAS (20%)"] = 80.0
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

# ==========================================
# 7. TAB NAVIGASI UTAMA
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📑 Generator Modul Ajar", 
    f"📋 Presensi ({kelas_aktif})", 
    f"📊 Buku Nilai & KKTP ({kelas_aktif})"
])

# ------------------------------------------
# TAB 1: GENERATOR MODUL AJAR
# ------------------------------------------
with tab1:
    st.markdown("<span class=\"section-badge\">LANGKAH 1 DARI 2</span>", unsafe_allow_html=True)
    st.subheader("Konfigurasi Modul Ajar")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.container(border=True):
            st.markdown("#### 📚 Pemilihan Kurikulum & Materi")
            if not DATABASE_MATERI:
                st.warning("⚠️ File `materi.json` belum terdeteksi. Menggunakan mode manual.")
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
            st.markdown("#### ⚙️ Setting Pembelajaran")
            alokasi = st.text_input("Alokasi Waktu", "2 JP (2 Pertemuan x 1 JP)")
            st.info("💡 Modul ini dibuat menggunakan format **Deep Learning Model** (Mindful, Meaningful, & Joyful Learning).")

    st.markdown("<span class=\"section-badge\">LANGKAH 2 DARI 2</span>", unsafe_allow_html=True)
    st.subheader("Pratinjau & Unduh Modul")

    modul_text = f"""MODUL AJAR KURIKULUM MERDEKA (DEEP LEARNING MODEL)
MATA PELAJARAN: {mapel_selected.upper()}
STANDAR KEPUTUSAN BSKAP NOMOR 046/H/KR/2025

I. INFORMASI UMUM
IDENTITAS MODUL
• Nama Sekolah: {sekolah}
• Nama Penyusun: {penyusun}
• Mata Pelajaran: {mapel_selected}
• Kelas / Fase / Semester: {kelas_selected} / Fase D / {semester}
• Bab / Tema Utama: {bab_selected}
• Sub-Materi Pembelajaran: {subbab_selected}
• Alokasi Waktu: {alokasi}
• Tahun Pelajaran: {tahun}

KOMPETENSI AWAL
1. Peserta didik telah memahami konsep dasar kehidupan bermasyarakat dan lingkungan sosial sekitar.
2. Peserta didik memiliki kemampuan awal dalam mengidentifikasi fenomena sosial/pancasila di lingkungan sehari-hari.

PROFIL PELAJAR PANCASILA
• Beriman, Bertakwa kepada Tuhan YME, dan Berakhlak Mulia
• Bernalar Kritis
• Gotong Royong
• Kreatif

SARANA DAN PRASARANA
• Media: Laptop, Proyektor, Slide Presentasi, Lembar Kerja Peserta Didik (LKPD).
• Sumber Belajar: Buku Paket Siswa Kurikulum Merdeka {mapel_selected}, Lingkungan Sekitar Sekolah.

TARGET PESERTA DIDIK
• Target: Peserta didik reguler / tipikal.
• Model Pembelajaran: Deep Learning Model (Mindful, Meaningful, & Joyful Learning) dengan pendekatan Problem-Based Learning (PBL).

II. KOMPONEN INTI
TUJUAN PEMBELAJARAN (TP)
1. Peserta didik mampu mendeskripsikan dan menganalisis konsep {subbab_selected} dengan tepat.
2. Peserta didik mampu mengidentifikasi serta memecahkan masalah kontekstual yang berkaitan dengan {bab_selected}.
3. Peserta didik mampu menyajikan hasil analisis mengenai {subbab_selected} melalui presentasi atau media visual.

PEMAHAMAN BERMAKNA (MEANINGFUL LEARNING)
Pemahaman terhadap {subbab_selected} membantu peserta didik menyadari peran aktifnya sebagai warga negara yang bijak, kritis, dan bertanggung jawab.

PERTANYAAN PEMANTIK
1. Mengapa topik {subbab_selected} sangat dekat dan penting dalam kehidupan sehari-hari kita?
2. Dampak apa yang akan terjadi jika kita tidak memahami prinsip {bab_selected} di masyarakat?

III. KEGIATAN PEMBELAJARAN DETAIL
PENDAHULUAN (15 MENIT) - Mindful Start
• Pembukaan, doa, presensi, dan penyampaian tujuan pembelajaran {subbab_selected}.

KEGIATAN INTI (80 MENIT) - Meaningful & Joyful Learning
• Eksplorasi konsep studi kasus {subbab_selected}.
• Diskusi kelompok berbasis LKPD (Discovery Learning).
• Presentasi dan umpan balik antar kelompok.

PENUTUP (15 MENIT) - Deep Reflection
• Menyimpulkan poin kunci dan melakukan refleksi pembelajaran.

IV. ASESMEN PEMBELAJARAN
• Asesmen Sikap, Formatif (LKPD & Diskusi), dan Sumatif (Tes Tertulis).

V. LAMPIRAN (LKPD DEEP LEARNING & RUBRIK)
 Mengetahui,
 Kepala Sekolah {sekolah}               Guru Mata Pelajaran

 ( .................................... )                  ({penyusun})
"""

    with st.expander("📄 Klik untuk Pratinjau Teks Dokumen", expanded=False):
        st.text_area("Isi Teks", modul_text, height=250)

    def export_word(text):
        doc = Document()
        for p in text.split('\n'):
            if p.startswith("I. ") or p.startswith("II. ") or p.startswith("III. ") or p.startswith("IV. ") or p.startswith("V. "):
                doc.add_heading(p, level=1)
            elif p.isupper() and len(p) < 50:
                doc.add_heading(p, level=2)
            else:
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
# TAB 2: PRESENSI SISWA (INCLUDE TANGGAL)
# ------------------------------------------
with tab2:
    col_p_title, col_p_date = st.columns([2, 1])
    with col_p_title:
        st.subheader(f"📋 Lembar Presensi Harian Siswa ({kelas_aktif})")
    with col_p_date:
        tgl_presensi = st.date_input("Tanggal Pengajaran / Presensi", date.today(), key=f"date_{kelas_aktif}")

    tgl_str = tgl_presensi.strftime("%Y-%m-%d")

    # Ambil data presensi dari session state
    df_presensi_current = st.session_state[key_p].copy()
    df_presensi_current["Tanggal"] = tgl_str

    cols_order = ["Tanggal", "No", "Nama", "Jenis Kelamin", "Status", "Keterangan"]
    df_presensi_current = df_presensi_current[cols_order]

    with st.container(border=True):
        st.caption(f"🗓️ Menampilkan presensi **{kelas_aktif}** untuk tanggal: **{tgl_presensi.strftime('%d %B %Y')}**")
        
        edited_presensi = st.data_editor(
            df_presensi_current,
            column_config={
                "Tanggal": st.column_config.TextColumn("Tanggal", disabled=True, width="medium"),
                "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
                "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="large"),
                "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
                "Status": st.column_config.SelectboxColumn(
                    "Status Kehadiran",
                    options=["Hadir", "Sakit", "Izin", "Alpha"],
                    required=True,
                    width="medium"
                ),
                "Keterangan": st.column_config.TextColumn("Keterangan", width="large")
            },
            disabled=["Tanggal", "No", "Nama", "Jenis Kelamin"],
            hide_index=True,
            use_container_width=True,
            key=f"editor_p_{kelas_aktif}"
        )
        
        st.session_state[key_p] = edited_presensi[["No", "Nama", "Jenis Kelamin", "Status", "Keterangan"]]

    # STATISTIK KARTU METRIK
    st.markdown("#### 📊 Statistik Kehadiran Hari Ini")
    rekap = edited_presensi["Status"].value_counts()
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Hadir", f"{rekap.get('Hadir', 0)} Siswa", delta="🟢 Sempurna" if rekap.get('Hadir', 0) == len(edited_presensi) else None)
    r2.metric("Sakit", f"{rekap.get('Sakit', 0)} Siswa")
    r3.metric("Izin", f"{rekap.get('Izin', 0)} Siswa")
    r4.metric("Alpha", f"{rekap.get('Alpha', 0)} Siswa", delta_color="inverse")

    st.divider()
    csv_presensi = edited_presensi.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Unduh Rekap Presensi {kelas_aktif} ({tgl_str})",
        data=csv_presensi,
        file_name=f"Presensi_{kelas_aktif}_{tgl_str}.csv",
        mime="text/csv",
        type="primary"
    )

# ------------------------------------------
# TAB 3: BUKU NILAI & KKTP
# ------------------------------------------
with tab3:
    st.subheader(f"📊 Buku Nilai Rapor & KKTP ({kelas_aktif})")
    
    col_kktp, col_info = st.columns([1, 2])
    with col_kktp:
        kktp_limit = st.number_input("Batas Minimal KKTP", min_value=50.0, max_value=100.0, value=75.0, step=1.0, key=f"kktp_{kelas_aktif}")
    with col_info:
        st.info("ℹ️ **Formulasi Bobot Nilai:** Formatif (30%) + Sumatif (30%) + STS (20%) + SAS (20%)")

    with st.container(border=True):
        edited_nilai = st.data_editor(
            st.session_state[key_n],
            column_config={
                "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
                "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="large"),
                "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
                "Formatif (30%)": st.column_config.NumberColumn("Formatif", min_value=0, max_value=100),
                "Sumatif (30%)": st.column_config.NumberColumn("Sumatif", min_value=0, max_value=100),
                "STS (20%)": st.column_config.NumberColumn("STS", min_value=0, max_value=100),
                "SAS (20%)": st.column_config.NumberColumn("SAS", min_value=0, max_value=100)
            },
            disabled=["No", "Nama", "Jenis Kelamin"],
            hide_index=True,
            use_container_width=True,
            key=f"editor_n_{kelas_aktif}"
        )
        st.session_state[key_n] = edited_nilai

    # LEGER RINGKASAN NILAI
    df_hasil = edited_nilai.copy()
    df_hasil["Nilai Akhir"] = (
        df_hasil["Formatif (30%)"] * 0.3 +
        df_hasil["Sumatif (30%)"] * 0.3 +
        df_hasil["STS (20%)"] * 0.2 +
        df_hasil["SAS (20%)"] * 0.2
    ).round(2)

    df_hasil["Status KKTP"] = df_hasil["Nilai Akhir"].apply(
        lambda x: "✅ Tercapai" if x >= kktp_limit else "⚠️ Perlu Bimbingan"
    )

    st.markdown("#### 📋 Leger Ringkasan Nilai Akhir Rapor")
    st.dataframe(
        df_hasil[["No", "Nama", "Jenis Kelamin", "Nilai Akhir", "Status KKTP"]],
        column_config={
            "Nilai Akhir": st.column_config.NumberColumn("Nilai Akhir Rapor", format="%.2f"),
            "Status KKTP": st.column_config.TextColumn("Status Ketercapaian KKTP")
        },
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    csv_nilai = df_hasil.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Unduh Leger Nilai {kelas_aktif} (CSV)",
        data=csv_nilai,
        file_name=f"Leger_Nilai_{kelas_aktif}.csv",
        mime="text/csv"
    )
