import streamlit as st
import pandas as pd
import json
import os
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
# 2. KONFIGURASI SPREADSHEET DARI SECRETS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if "SPREADSHEET_ID" in st.secrets:
    SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
else:
    SPREADSHEET_ID = "1o-xa_G7Vt8l4wrSrPl6AVAmhr7MXJ-AVyZf35mrW1Bc"

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

# ==========================================
# 4. FUNGSI READ/WRITE DATA
# ==========================================
def load_materi_json():
    file_path = os.path.join(BASE_DIR, "materi.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_data_siswa(kelas_nama):
    nama_clean = kelas_nama.lower().replace(" ", "")
    possible_files = [
        f"{nama_clean}.csv",
        f"{kelas_nama.lower()}.csv",
        f"{kelas_nama.upper()}.csv",
        f"{kelas_nama}.csv",
        f"{kelas_nama.replace(' ', '_')}.csv"
    ]
    
    file_path = None
    for fname in possible_files:
        p = os.path.join(BASE_DIR, fname)
        if os.path.exists(p):
            file_path = p
            break

    if file_path:
        try:
            df = pd.read_csv(file_path, sep=None, engine="python")
            df.columns = [str(c).strip() for c in df.columns]
            
            col_map = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'nama' in col_lower:
                    col_map[col] = 'Nama'
                elif col_lower in ['no', 'no.']:
                    col_map[col] = 'No'
                elif 'jenis' in col_lower or 'jk' in col_lower or 'kelamin' in col_lower:
                    col_map[col] = 'Jenis Kelamin'
            
            df = df.rename(columns=col_map)
            if "Nama" in df.columns:
                if "No" not in df.columns:
                    df.insert(0, "No", range(1, len(df) + 1))
                if "Jenis Kelamin" not in df.columns:
                    df["Jenis Kelamin"] = "-"
                return df[["No", "Nama", "Jenis Kelamin"]]
        except Exception:
            pass

    list_nama = DUMMY_SISWA.get(kelas_nama, DUMMY_SISWA["Kelas 7A"])
    jk_list = ["L" if i % 2 == 0 else "P" for i in range(len(list_nama))]
    return pd.DataFrame({"No": range(1, len(list_nama) + 1), "Nama": list_nama, "Jenis Kelamin": jk_list})

DATABASE_MATERI = load_materi_json()

# ==========================================
# 5. SIDEBAR PANEL
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
    st.success(f"🟢 Spreadsheet ID Terhubung:\n`{SPREADSHEET_ID[:10]}...`")
    st.caption("✨ **Aplikasi Administrasi Guru**\nKurikulum Merdeka BSKAP 2025")

DF_SISWA_AKTIF = get_data_siswa(kelas_aktif)
JUMLAH_KOLOM_NILAI = 15
KATEGORI_NILAI_OPSI = [
    "Tugas Individu", 
    "Tugas Kelompok", 
    "Projek / Praktik", 
    "UTS / Mid Semester", 
    "UAS / Akhir Semester"
]

# ==========================================
# 6. SINKRONISASI DATAFRAME
# ==========================================
key_p = f"presensi_{kelas_aktif}"
key_n = f"nilai_{kelas_aktif}"

if key_p not in st.session_state:
    df_p = DF_SISWA_AKTIF.copy()
    for t in range(1, 32):
        df_p[str(t)] = ""
    st.session_state[key_p] = df_p

if key_n not in st.session_state:
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
        <p>Selamat datang, <b>{penyusun}</b> | {sekolah} | <b>{kelas_aktif}</b> ({tahun} - Semester {semester})</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 8. TAB NAVIGASI UTAMA
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

II. KOMPONEN INTI
TUJUAN PEMBELAJARAN (TP)
1. Peserta didik mampu mendeskripsikan dan menganalisis konsep {subbab_selected} dengan tepat.
2. Peserta didik mampu mengidentifikasi serta memecahkan masalah kontekstual yang berkaitan dengan {bab_selected}.

III. KEGIATAN PEMBELAJARAN DETAIL
PENDAHULUAN (15 MENIT) - Mindful Start
• Pembukaan, doa, presensi, dan penyampaian tujuan pembelajaran {subbab_selected}.

KEGIATAN INTI (80 MENIT) - Meaningful & Joyful Learning
• Eksplorasi konsep studi kasus {subbab_selected}.
• Diskusi kelompok berbasis LKPD (Discovery Learning).

PENUTUP (15 MENIT) - Deep Reflection
• Menyimpulkan poin kunci dan melakukan refleksi pembelajaran.

 Mengetahui,
 Kepala Sekolah {sekolah}                Guru Mata Pelajaran

 ( .................................... )                ({penyusun})
"""

    def export_word(text):
        doc = Document()
        for p in text.split('\n'):
            if p.startswith(("I. ", "II. ", "III. ", "IV. ", "V. ")):
                doc.add_heading(p, level=1)
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

    col_config_p = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="medium"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    for t in range(1, 32):
        col_config_p[str(t)] = st.column_config.TextColumn(str(t), width="small")

    edited_p = st.data_editor(
        st.session_state[key_p],
        column_config=col_config_p,
        disabled=["No", "Nama", "Jenis Kelamin"],
        hide_index=True,
        use_container_width=True,
        key=f"editor_p_{kelas_aktif}"
    )
    st.session_state[key_p] = edited_p

    st.divider()
    csv_presensi = edited_p.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Unduh CSV Presensi ({kelas_aktif})",
        data=csv_presensi,
        file_name=f"Presensi_{kelas_aktif}_{bulan_presensi}.csv",
        mime="text/csv",
        type="primary"
    )

# ------------------------------------------
# TAB 3: BUKU NILAI & KKTP
# ------------------------------------------
with tab3:
    st.subheader(f"📊 Buku Nilai & Akumulasi Realtime ({kelas_aktif})")
    
    st.markdown("#### ⚙️ Pengaturan Kategori Tugas & Penilaian")
    st.caption("Pilih kategori penilaian untuk setiap kolom nilai di bawah ini:")
    
    # Pengaturan Opsi Jenis Nilai untuk setiap Kolom (Dalam Ekspander)
    with st.expander("📌 Kustomisasi Kategori Jenis Nilai tiap Kolom", expanded=False):
        kategori_cols = st.columns(5)
        kategori_terpilih = {}
        for idx in range(1, JUMLAH_KOLOM_NILAI + 1):
            col_idx = (idx - 1) % 5
            with kategori_cols[col_idx]:
                kategori_terpilih[f"Nilai {idx}"] = st.selectbox(
                    f"Kolom Nilai {idx}",
                    options=KATEGORI_NILAI_OPSI,
                    index=0 if idx <= 5 else (1 if idx <= 10 else 2),
                    key=f"kat_{kelas_aktif}_{idx}"
                )

    # Menyiapkan DataFrame untuk Pengeditan
    df_nilai_current = st.session_state[key_n].copy()
    
    # Konfigurasi Tampilan Tabel
    column_config_n = {
        "No": st.column_config.NumberColumn("No", disabled=True, width="small"),
        "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True, width="large"),
        "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True, width="small"),
    }
    
    kolom_nilai_keys = [f"Nilai {i}" for i in range(1, JUMLAH_KOLOM_NILAI + 1)]
    
    for k in kolom_nilai_keys:
        kat_label = kategori_terpilih.get(k, "Tugas")
        column_config_n[k] = st.column_config.NumberColumn(
            f"{k} ({kat_label})",
            min_value=0.0,
            max_value=100.0,
            format="%.1f",
            width="medium"
        )
    
    # Menghitung Nilai Akhir Secara Realtime (Rata-Rata)
    df_numeric = df_nilai_current[kolom_nilai_keys].apply(pd.to_numeric, errors='coerce')
    df_nilai_current["Nilai Akhir (Akumulasi)"] = df_numeric.mean(axis=1).round(2)
    
    column_config_n["Nilai Akhir (Akumulasi)"] = st.column_config.NumberColumn(
        "📊 Nilai Akhir (Rata-Rata)",
        disabled=True,
        format="%.2f",
        width="medium"
    )

    edited_n = st.data_editor(
        df_nilai_current,
        column_config=column_config_n,
        disabled=["No", "Nama", "Jenis Kelamin", "Nilai Akhir (Akumulasi)"],
        hide_index=True,
        use_container_width=True,
        key=f"editor_n_{kelas_aktif}"
    )
    
    # Simpan kembali ke Session State
    st.session_state[key_n] = edited_n[DF_SISWA_AKTIF.columns.tolist() + kolom_nilai_keys]

    st.divider()
    csv_nilai = edited_n.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Unduh CSV Nilai & Akumulasi ({kelas_aktif})",
        data=csv_nilai,
        file_name=f"Nilai_{kelas_aktif}.csv",
        mime="text/csv",
        type="primary"
    )
