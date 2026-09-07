import streamlit as st
import pandas as pd
import json
import os
from docx import Document
from io import BytesIO

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM STYLING (CSS)
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = f"{kelas_nama.lower()}.csv"
    file_path = os.path.join(base_dir, file_name)
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, sep=None, engine="python")
            df.columns = [c.strip() for c in df.columns]
            return df
        except Exception:
            pass

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

DF_SISWA_AKTIF = get_data_siswa(kelas_aktif)

# ==========================================
# 5. INISIALISASI SESSION STATE (KOSONG AWAL)
# ==========================================
key_p = f"presensi_blank_{kelas_aktif}"
key_n = f"nilai_blank_{kelas_aktif}"
key_kat = f"kategori_cols_{kelas_aktif}"

# Presensi Blank
if key_p not in st.session_state:
    df_p = DF_SISWA_AKTIF.copy()
    for t in range(1, 32):
        df_p[str(t)] = ""  # Dikosongkan
    st.session_state[key_p] = df_p

# Nilai Blank (Sediakan 10 Kolom Nilai)
JUMLAH_KOLOM_NILAI = 10
if key_n not in st.session_state:
    df_n = DF_SISWA_AKTIF.copy()
    for i in range(1, JUMLAH_KOLOM_NILAI + 1):
        df_n[f"N{i}"] = None  # Kosong (None)
    st.session_state[key_n] = df_n

# Kategori per Kolom Nilai
if key_kat not in st.session_state:
    st.session_state[key_kat] = {f"N{i}": "Tugas Individu" for i in range(1, JUMLAH_KOLOM_NILAI + 1)}

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
    f"📋 Buku Presensi ({kelas_aktif})", 
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
# TAB 2: BUKU PRESENSI (KOSONG / KOSONGKAN)
# ------------------------------------------
with tab2:
    st.subheader(f"📖 Buku Presensi Harian ({kelas_aktif})")
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        bulan_presensi = st.selectbox(
            "Pilih Bulan Presensi",
            ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"],
            index=8,
            key=f"bln_{kelas_aktif}"
        )
    with col_p2:
        st.info("💡 **Petunjuk:** Tabel presensi disajikan kosong. Silakan isi kode: **H** (Hadir), **S** (Sakit), **I** (Izin), atau **A** (Alpha).")

    df_p_edit = st.session_state[key_p].copy()

    col_config_p = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="medium"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    for t in range(1, 32):
        col_config_p[str(t)] = st.column_config.TextColumn(str(t), width="small")

    with st.container(border=True):
        st.caption(f"🗓️ **Presensi Bulan {bulan_presensi} - {kelas_aktif}**")
        edited_p_matrix = st.data_editor(
            df_p_edit,
            column_config=col_config_p,
            disabled=["No", "Nama", "Jenis Kelamin"],
            hide_index=True,
            use_container_width=True,
            key=f"editor_p_blank_{kelas_aktif}"
        )
        st.session_state[key_p] = edited_p_matrix

    # HITUNG REKAP PRESENSI (OTOMATIS DARI ISI MANUAL)
    tgl_cols = [str(t) for t in range(1, 32)]
    df_rekap_p = edited_p_matrix[["No", "Nama", "Jenis Kelamin"]].copy()
    df_rekap_p["Hadir (H)"] = edited_p_matrix[tgl_cols].apply(lambda row: (row.astype(str).str.upper() == "H").sum(), axis=1)
    df_rekap_p["Sakit (S)"] = edited_p_matrix[tgl_cols].apply(lambda row: (row.astype(str).str.upper() == "S").sum(), axis=1)
    df_rekap_p["Izin (I)"] = edited_p_matrix[tgl_cols].apply(lambda row: (row.astype(str).str.upper() == "I").sum(), axis=1)
    df_rekap_p["Alpha (A)"] = edited_p_matrix[tgl_cols].apply(lambda row: (row.astype(str).str.upper() == "A").sum(), axis=1)

    st.markdown(f"#### 📊 Rekapitulasi Presensi Bulan {bulan_presensi}")
    st.dataframe(df_rekap_p, use_container_width=True, hide_index=True)

    st.divider()
    csv_presensi = edited_p_matrix.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Unduh Buku Presensi Bulan {bulan_presensi} ({kelas_aktif})",
        data=csv_presensi,
        file_name=f"Buku_Presensi_{kelas_aktif}_{bulan_presensi}.csv",
        mime="text/csv",
        type="primary"
    )

# ------------------------------------------
# TAB 3: BUKU NILAI (TABEL TUNGGAL + KATEGORI HEADER DROPDOWN)
# ------------------------------------------
with tab3:
    st.subheader(f"📊 Buku Nilai Siswa ({kelas_aktif})")
    st.caption("💡 Atur jenis penilaian pada setiap kolom di bawah ini, lalu isikan nilainya. Akumulasi nilai akhir akan terhitung otomatis.")

    OPSI_KATEGORI = [
        "Tugas Individu",
        "Tugas Kelompok",
        "Projek / Praktik",
        "UTS / Mid Semester",
        "UAS / Akhir Semester"
    ]

    # PENGATURAN DROPDOWN KATEGORI HEADER UNTUK KOLOM NILAI
    with st.expander("⚙️ **Atur Jenis Penilaian untuk Setiap Kolom (Nilai 1 s.d Nilai 10)**", expanded=True):
        cols_kat = st.columns(5)
        for idx in range(1, JUMLAH_KOLOM_NILAI + 1):
            col_target = cols_kat[(idx - 1) % 5]
            with col_target:
                st.session_state[key_kat][f"N{idx}"] = st.selectbox(
                    f"Jenis Nilai #{idx}",
                    OPSI_KATEGORI,
                    index=0 if idx <= 5 else 1,
                    key=f"sel_kat_N{idx}_{kelas_aktif}"
                )

    # PERSIAPAN TABEL TUNGGAL BUKU NILAI
    df_n_current = st.session_state[key_n].copy()
    
    # Hitung Akumulasi Realtime (Rata-Rata Nilai yang Diisi)
    col_nilai_list = [f"N{i}" for i in range(1, JUMLAH_KOLOM_NILAI + 1)]
    df_n_current["Nilai Akhir (Akumulasi)"] = df_n_current[col_nilai_list].mean(axis=1, skipna=True).round(2)

    # Buat Config Header Dinamis (Nama Kolom + Jenis Penilaiannya)
    column_config_n = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="large"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }

    for idx in range(1, JUMLAH_KOLOM_NILAI + 1):
        kat_label = st.session_state[key_kat][f"N{idx}"]
        column_config_n[f"N{idx}"] = st.column_config.NumberColumn(
            f"N{idx} ({kat_label})",
            min_value=0.0,
            max_value=100.0,
            format="%.1f",
            width="medium"
        )

    column_config_n["Nilai Akhir (Akumulasi)"] = st.column_config.NumberColumn(
        "Nilai Akhir (Realtime)",
        disabled=True,
        format="%.2f",
        width="medium"
    )

    with st.container(border=True):
        st.markdown(f"##### 📖 Buku Nilai Tunggal - **{kelas_aktif}**")
        
        edited_buku_nilai = st.data_editor(
            df_n_current,
            column_config=column_config_n,
            disabled=["No", "Nama", "Jenis Kelamin", "Nilai Akhir (Akumulasi)"],
            hide_index=True,
            use_container_width=True,
            key=f"editor_buku_nilai_tunggal_{kelas_aktif}"
        )
        
        # Simpan Kembali Inputan Guru ke Session State
        for col in col_nilai_list:
            st.session_state[key_n][col] = edited_buku_nilai[col]

    st.divider()
    csv_buku_nilai = edited_buku_nilai.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Unduh Buku Nilai Lengkap {kelas_aktif} (CSV)",
        data=csv_buku_nilai,
        file_name=f"Buku_Nilai_{kelas_aktif}.csv",
        mime="text/csv",
        type="primary"
    )
