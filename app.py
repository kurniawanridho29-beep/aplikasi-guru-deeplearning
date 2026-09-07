import streamlit as st
import pandas as pd
import json
from docx import Document
from io import BytesIO
from datetime import date

st.set_page_config(page_title="Sistem Terpadu Pembelajaran & Administrasi Guru", layout="wide")

# --- 1. FUNGSI LOAD DATA ---
@st.cache_data
def load_materi_json():
    try:
        with open("materi.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@st.cache_data
def load_siswa_default():
    try:
        df = pd.read_csv("kelas 7A.csv", sep=None, engine="python")
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception:
        # Fallback jika file tidak ditemukan
        return pd.DataFrame({
            "No": range(1, 18),
            "Nama": [
                "Aditya Naufal Pratama", "Zidan Al Fatir", "Atika Zahara Ratifa",
                "Ayu Azka Fariha", "Dini Khoirunisa", "Enjelita Laia",
                "Ervan Martio Armana", "Farisman Lase", "Fauzia",
                "Hendriyanto", "M Sahel Habibillah", "Okta Dita Pranata",
                "Rahmad Ramadhani", "Yuda Agustian FitRoh", "Yulia Ramadhani",
                "Marveltus Hia", "Muhammad Rhaehan A"
            ],
            "Jenis Kelamin": ["L", "L", "P", "P", "P", "P", "L", "P", "L", "L", "L", "L", "L", "L", "P", "L", "L"]
        })

DATABASE_MATERI = load_materi_json()
DF_SISWA_7A = load_siswa_default()

# --- 2. INISIALISASI SESSION STATE ---
if "presensi_data" not in st.session_state:
    df_p = DF_SISWA_7A.copy()
    df_p["Status"] = "Hadir"
    df_p["Keterangan"] = "-"
    st.session_state.presensi_data = df_p

if "nilai_data" not in st.session_state:
    df_n = DF_SISWA_7A.copy()
    df_n["Formatif (30%)"] = 80.0
    df_n["Sumatif (30%)"] = 80.0
    df_n["STS (20%)"] = 80.0
    df_n["SAS (20%)"] = 80.0
    st.session_state.nilai_data = df_n

# --- 3. SIDEBAR NAVIGASI ---
st.sidebar.title("📌 Menu Utama")
menu = st.sidebar.radio(
    "Pilih Fitur:",
    ["📑 Generator Modul Ajar", "📋 Presensi Siswa (Kelas 7A)", "📊 Buku Nilai & KKTP (Kelas 7A)"]
)

# ==========================================
# MENU 1: GENERATOR MODUL AJAR
# ==========================================
if menu == "📑 Generator Modul Ajar":
    st.header("📑 Generator Modul Ajar Deep Learning")
    
    if not DATABASE_MATERI:
        st.warning("File `materi.json` belum ditemukan di direktori utama. Silakan tambahkan file `materi.json` untuk menampilkan daftar bab & subbab.")
        mapel_selected = st.selectbox("Mata Pelajaran", ["IPS", "PPKn"])
        kelas_selected = st.selectbox("Kelas", ["Kelas 7", "Kelas 8", "Kelas 9"])
        bab_selected = st.text_input("Bab / Tema Utama", "Bab 1: Kehidupan Sosial dan Kondisi Lingkungan Sekitar")
        subbab_selected = st.text_input("Sub-Materi / Subbab", "Kegiatan Ekonomi (Produksi, Distribusi, Konsumsi)")
    else:
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            mapel_selected = st.selectbox("Pilih Mata Pelajaran", list(DATABASE_MATERI.keys()))
            kelas_selected = st.selectbox("Pilih Kelas", list(DATABASE_MATERI[mapel_selected].keys()))
        
        bab_dict = DATABASE_MATERI[mapel_selected][kelas_selected]
        with c_m2:
            bab_selected = st.selectbox("Pilih Bab / Tema Utama", list(bab_dict.keys()))
            subbab_selected = st.selectbox("Pilih Sub-Materi / Subbab", bab_dict[bab_selected])

    st.subheader("⚙️ Identitas & Informasi Pembelajaran")
    col1, col2 = st.columns(2)
    with col1:
        sekolah = st.text_input("Nama Sekolah", "SMP RSUP PKB Pulau Burung")
        penyusun = st.text_input("Nama Penyusun", "Ridho Kurniawan, S.Pd.")
    with col2:
        tahun = st.text_input("Tahun Pelajaran", "2026/2027")
        semester = st.selectbox("Semester", ["Ganjil", "Genap"])
        alokasi = st.text_input("Alokasi Waktu", "2 JP (2 Pertemuan x 1 JP)")

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

    st.subheader("📄 Pratinjau Teks Modul Ajar")
    st.text_area("Hasil Teks Modul", modul_text, height=350)

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
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ==========================================
# MENU 2: PRESENSI SISWA
# ==========================================
elif menu == "📋 Presensi Siswa (Kelas 7A)":
    st.header("📋 Presensi Harian Siswa - Kelas 7A")
    
    tgl_presensi = st.date_input("Tanggal Presensi", date.today())
    st.info(f"Total Siswa Terdaftar: **{len(st.session_state.presensi_data)} Siswa**")

    # Editor Tabel Presensi
    edited_presensi = st.data_editor(
        st.session_state.presensi_data,
        column_config={
            "No": st.column_config.NumberColumn("No", disabled=True),
            "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True),
            "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True),
            "Status": st.column_config.SelectboxColumn(
                "Status Kehadiran",
                options=["Hadir", "Sakit", "Izin", "Alpha"],
                required=True
            ),
            "Keterangan": st.column_config.TextColumn("Keterangan Tambahan")
        },
        disabled=["No", "Nama", "Jenis Kelamin"],
        hide_index=True,
        use_container_width=True
    )
    
    st.session_state.presensi_data = edited_presensi

    # Ringkasan Rekap
    st.subheader("📊 Ringkasan Kehadiran Hari Ini")
    rekap = edited_presensi["Status"].value_counts()
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Hadir", rekap.get("Hadir", 0))
    col_r2.metric("Sakit", rekap.get("Sakit", 0))
    col_r3.metric("Izin", rekap.get("Izin", 0))
    col_r4.metric("Alpha", rekap.get("Alpha", 0))

    # Ekspor CSV
    csv_presensi = edited_presensi.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Rekap Presensi (CSV)",
        data=csv_presensi,
        file_name=f"Presensi_Kelas_7A_{tgl_presensi}.csv",
        mime="text/csv"
    )

# ==========================================
# MENU 3: BUKU NILAI & KKTP
# ==========================================
elif menu == "📊 Buku Nilai & KKTP (Kelas 7A)":
    st.header("📊 Buku Nilai & Kriteria Ketercapaian Tujuan Pembelajaran (KKTP)")
    st.caption("Pembobotan Nilai Akhir: Formatif (30%), Sumatif (30%), STS (20%), SAS (20%). Batas KKTP: 75")

    kktp_limit = st.number_input("Batas Minimal KKTP", min_value=50.0, max_value=100.0, value=75.0, step=1.0)

    edited_nilai = st.data_editor(
        st.session_state.nilai_data,
        column_config={
            "No": st.column_config.NumberColumn("No", disabled=True),
            "Nama": st.column_config.TextColumn("Nama Siswa", disabled=True),
            "Jenis Kelamin": st.column_config.TextColumn("JK", disabled=True),
            "Formatif (30%)": st.column_config.NumberColumn("Nilai Formatif", min_value=0, max_value=100),
            "Sumatif (30%)": st.column_config.NumberColumn("Nilai Sumatif", min_value=0, max_value=100),
            "STS (20%)": st.column_config.NumberColumn("Nilai STS", min_value=0, max_value=100),
            "SAS (20%)": st.column_config.NumberColumn("Nilai SAS", min_value=0, max_value=100)
        },
        disabled=["No", "Nama", "Jenis Kelamin"],
        hide_index=True,
        use_container_width=True
    )
    
    st.session_state.nilai_data = edited_nilai

    # Hitung Nilai Akhir
    df_hasil = edited_nilai.copy()
    df_hasil["Nilai Akhir"] = (
        df_hasil["Formatif (30%)"] * 0.3 +
        df_hasil["Sumatif (30%)"] * 0.3 +
        df_hasil["STS (20%)"] * 0.2 +
        df_hasil["SAS (20%)"] * 0.2
    ).round(2)

    df_hasil["Status KKTP"] = df_hasil["Nilai Akhir"].apply(
        lambda x: "Tercapai" if x >= kktp_limit else "Perlu Bimbingan"
    )

    st.subheader("📋 Hasil Perhitungan Nilai Rapor Kelas 7A")
    st.dataframe(df_hasil[["No", "Nama", "Jenis Kelamin", "Nilai Akhir", "Status KKTP"]], use_container_width=True, hide_index=True)

    # Ekspor Laporan Nilai
    csv_nilai = df_hasil.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Leger Nilai (CSV)",
        data=csv_nilai,
        file_name="Leger_Nilai_Kelas_7A.csv",
        mime="text/csv"
    )
