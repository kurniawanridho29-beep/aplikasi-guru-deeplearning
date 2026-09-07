import streamlit as st
import pandas as pd
import io
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# -----------------------------------------------------------------------------
# KONFIGURASI HALAMAN UTAMA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Aplikasi Administrasi Guru Digital - IPS & PPKn",
    page_icon="📚",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #1E293B;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">PORTAL ADMINISTRASI GURU DIGITAL (IPS & PPKn SMP)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generator Modul Ajar Deep Learning Lengkap (BSKAP 046/2025), Presensi Dropdown & Buku Nilai KKTP</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA REFERENSI JAM SEKOLAH (JADWAL REAL)
# -----------------------------------------------------------------------------
DATA_JAM_SEKOLAH = {
    "Jam 1": {"waktu": "08:10 - 08:50", "durasi": 40},
    "Jam 2": {"waktu": "08:50 - 09:30", "durasi": 40},
    # 09:30 - 09:45 Istirahat 1
    "Jam 3": {"waktu": "09:45 - 10:25", "durasi": 40},
    "Jam 4": {"waktu": "10:25 - 11:05", "durasi": 40},
    # 11:05 - 11:20 Istirahat 2
    "Jam 5": {"waktu": "11:20 - 12:10", "durasi": 50},  # Durasi sebelum Zuhur
    # 12:10 - 12:30 Shalat Zuhur
    "Jam 6": {"waktu": "12:30 - 13:10", "durasi": 40},
    "Jam 7": {"waktu": "13:10 - 13:30", "durasi": 20},  # Jam terakhir Senin
    "Jam 8": {"waktu": "13:10 - 13:30", "durasi": 20},  # Jam terakhir Selasa
}

# -----------------------------------------------------------------------------
# NAVIGASI SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navigasi Fitur")
menu = st.sidebar.radio(
    "Pilih Modul Aplikasi:",
    ["1. Generator Modul Ajar (Deep Learning)", "2. Info Jadwal Jam Sekolah", "3. Presensi Dropdown Lintas Kelas", "4. Buku Nilai & Status KKTP (Satu Tabel)"]
)

daftar_kelas = ["Kelas 7A", "Kelas 7B", "Kelas 8", "Kelas 9"]

# -----------------------------------------------------------------------------
# DATABASE BAB & SUB-MATERI LENGKAP IPS & PPKN
# -----------------------------------------------------------------------------
DATABASE_MATERI = {
    "Ilmu Pengetahuan Sosial (IPS)": {
        "Kelas VII / Fase D": {
            "Bab 1: Keluarga Awal Kehidupan": [
                "Sejarah Asal Usul Keluarga & Silsilah Keluarga",
                "Konsep Lokasi Absolut dan Lokasi Relatif",
                "Letak, Luas, Cuaca, Iklim & Geologis Indonesia",
                "Komponen Peta dan Fungsi Peta",
                "Sejarah Lisan dan Sumber Sejarah Lisan",
                "Manusia sebagai Makhluk Sosial dan Ekonomi Bermoral",
                "Hakikat dan Agen-Agen Sosialisasi",
                "Nilai dan Norma dalam Kehidupan Masyarakat",
                "Interaksi Antar Wilayah",
                "Kebutuhan Manusia dan Alat Pemuas Kebutuhan"
            ],
            "Bab 2: Keberagaman Lingkungan Sekitar": [
                "Pencemaran Lingkungan & Pelestarian Sumber Daya",
                "Pembentukan Muka Bumi & Pembentukan Batuan",
                "Kehidupan Masyarakat Masa Praaksara",
                "Pembangunan Berkelanjutan (SDGs)"
            ],
            "Bab 3: Potensi Ekonomi Lingkungan": [
                "Kegiatan Ekonomi (Produksi, Distribusi, Konsumsi)",
                "Pelaku Ekonomi di Masyarakat",
                "Peran Masyarakat dalam Rantai Ekonomi",
                "Pasar dan Pembentukan Harga Pasar"
            ],
            "Bab 4: Pemberdayaan Masyarakat": [
                "Keragaman Sosial Budaya Indonesia",
                "Pemberdayaan Finansial & Literasi Keuangan",
                "Peranan Komunitas Lokal dalam Perekonomian"
            ]
        },
        "Kelas VIII / Fase D": {
            "Bab 1: Kondisi Geografis dan Pelestarian Sumber Daya Alam": [
                "Keragaman Alam Indonesia & Letak Astronomis",
                "Pemanfaatan dan Pelestarian Sumber Daya Alam",
                "Kualitas Sumber Daya Manusia (SDM)",
                "Lembaga Sosial dalam Pengelolaan SDA"
            ],
            "Bab 2: Kemajemukan Masyarakat Indonesia": [
                "Keragaman Etnis, Agama, dan Budaya",
                "Mobilitas Sosial (Vertikal & Horizontal)",
                "Interaksi Budaya Hindia-Buddha dan Islam",
                "Konflik dan Integrasi Sosial"
            ],
            "Bab 3: Nasionalisme dan Pengembangan Ekonomi": [
                "Penjelajahan Samudra & Kolonialisme di Indonesia",
                "Tumbuhnya Pergerakan Nasional & Sumpah Pemuda",
                "Perdagangan Antarpulau dan Antarnegara",
                "Penguatan Ekonomi Maritim dan Agrikultur"
            ],
            "Bab 4: Pembangunan Perekonomian Indonesia": [
                "Kondisi Ekonomi Pasca Kemerdekaan",
                "Orde Baru dan Perubahan Perekonomian",
                "Ekonomi Digital & Peran Generasi Muda",
                "Tantangan Pembangunan Ekonomi Nasional"
            ]
        },
        "Kelas IX / Fase D": {
            "Bab 1: Perubahan Sosial dan Globalisasi": [
                "Bentuk-Bentuk Perubahan Sosial Masyarakat",
                "Dampak Modernisasi & Globalisasi",
                "Kearifan Lokal dalam Menghadapi Globalisasi",
                "Digitalisasi Sosial dan Budaya Masa Kini"
            ],
            "Bab 2: Keragaman Bangsa-Bangsa di Dunia": [
                "Karakteristik Benua-Benua di Dunia",
                "Potensi Sumber Daya Negara-Negara Dunia",
                "Interaksi Antarruang dan Kerjasama Internasional",
                "Pengaruh Kerjasama Internasional bagi Indonesia"
            ],
            "Bab 3: Literasi Keuangan dan Kesejahteraan Masyarakat": [
                "Lembaga Keuangan Bank dan Non-Bank",
                "Sistem Pembayaran dan Uang Digital",
                "Pengelolaan Keuangan Pribadi & Investasi",
                "Kewirausahaan dan Ekonomi Kreatif"
            ],
            "Bab 4: Indonesia dalam Kehidupan Dunia": [
                "Peran Aktif Indonesia dalam Perdamaian Dunia",
                "Kerjasama ASEAN, Asia-Afrika, dan PBB",
                "Isu Lingkungan Global & Krisis Iklim"
            ]
        }
    },
    "Pendidikan Pancasila (PPKn)": {
        "Kelas VII / Fase D": {
            "Bab 1: Sejarah Kelahiran Pancasila": [
                "Latar Belakang & Sejarah Nilai-Nilai Pancasila",
                "Kelahiran Pancasila, Janji Kemerdekaan & BPUPK",
                "Perumusan Pancasila oleh Panitia Sembilan",
                "Penetapan Pancasila sebagai Dasar Negara oleh PPKI",
                "Penerapan Nilai-Nilai Pancasila dalam Kehidupan Sehari-hari"
            ],
            "Bab 2: Norma dan UUD NRI Tahun 1945": [
                "Pengertian dan Jenis-jenis Norma",
                "Arti Penting Norma dalam Kehidupan Bermasyarakat",
                "Sejarah Perumusan UUD NRI Tahun 1945",
                "Amandemen dan Penerapan UUD NRI 1945"
            ],
            "Bab 3: Kesatuan Indonesia dan Karakteristik Daerah": [
                "Wilayah Negara Kesatuan Republik Indonesia (NKRI)",
                "Indonesia sebagai Negara Kesatuan",
                "Karakteristik Daerah dalam Frame NKRI",
                "Mempertahankan Persatuan dan Kesatuan Bangsa"
            ],
            "Bab 4: Kebinekaan Indonesia": [
                "Keragaman Suku, Agama, Ras, dan Antargolongan",
                "Menghargai Keberagaman Budaya Lokal",
                "Menjaga Toleransi dan Harmoni Sosial"
            ]
        },
        "Kelas VIII / Fase D": {
            "Bab 1: Kedudukan dan Fungsi Pancasila": [
                "Pancasila sebagai Dasar Negara",
                "Pancasila sebagai Pandangan Hidup Bangsa",
                "Pancasila sebagai Ideologi Negara",
                "Meneladani Nilai Pancasila dalam Masyarakat"
            ],
            "Bab 2: Bentuk dan Kedaulatan Negara": [
                "Indonesia sebagai Negara Hukum",
                "Bentuk Negara Kesatuan dan Republik",
                "Kedaulatan Rakyat dan Sistem Demokrasi",
                "Peran Lembaga-Lembaga Negara"
            ],
            "Bab 3: Tata Urutan Peraturan Perundang-undangan": [
                "Hierarki Peraturan Perundang-undangan Indonesia",
                "Proses Pembuatan Undang-Undang",
                "Kepatuhan terhadap Hukum dan Peraturan"
            ],
            "Bab 4: Kebangkitan Nasional dan Sumpah Pemuda": [
                "Sejarah Perjuangan Kebangkitan Nasional 1908",
                "Makna dan Nilai-Nilai Sumpah Pemuda 1928",
                "Semangat Sumpah Pemuda untuk Generasi Muda"
            ]
        },
        "Kelas IX / Fase D": {
            "Bab 1: Penerapan Pancasila dari Masa ke Masa": [
                "Pancasila Masa Orde Lama & Dinamikanya",
                "Pancasila Masa Orde Baru & Reformasi",
                "Tantangan Ideologi Pancasila di Era Digital"
            ],
            "Bab 2: Hak dan Kewajiban Warga Negara": [
                "Substansi Hak dan Kewajiban dalam UUD 1945",
                "Keseimbangan Hak dan Kewajiban",
                "Kasus Pelanggaran Hak & Pengingkaran Kewajiban"
            ],
            "Bab 3: Kemerdekaan Berpendapat Warga Negara": [
                "Jaminan Kemerdekaan Berpendapat di Indonesia",
                "Bentuk-Bentuk Penyampaian Pendapat",
                "Etika Berpendapat dan Bermedia Sosial"
            ],
            "Bab 4: Harmoni dalam Keberagaman Masyarakat": [
                "Permasalahan dan Dampak Keberagaman",
                "Upaya Pencegahan Konflik SARA",
                "Bela Negara dalam Konteks Indonesia Modern"
            ]
        }
    }
}

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def to_excel(df, sheet_name="Data_Administrasi"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def to_word(text_content):
    doc = Document()
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    lines = text_content.split('\n')
    in_table = False
    table_data = []

    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('|') and stripped.endswith('|'):
            in_table = True
            if "---" in stripped:
                continue
            cols = [col.strip() for col in stripped.split('|')[1:-1]]
            table_data.append(cols)
            continue
        elif in_table and not (stripped.startswith('|') and stripped.endswith('|')):
            if table_data:
                num_rows = len(table_data)
                num_cols = max(len(row) for row in table_data)
                table = doc.add_table(rows=num_rows, cols=num_cols)
                table.style = 'Table Grid'
                
                for r_idx, row in enumerate(table_data):
                    for c_idx, val in enumerate(row):
                        if c_idx < num_cols:
                            cell = table.cell(r_idx, c_idx)
                            cell.text = val
                            if r_idx == 0:
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.font.bold = True
                doc.add_paragraph()
                table_data = []
                in_table = False

        if not stripped:
            continue

        if stripped.startswith('# '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[2:])
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 51, 102)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif stripped.startswith('## '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[3:])
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 51, 102)
        elif stripped.startswith('### '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[4:])
            run.font.size = Pt(11)
            run.font.bold = True
        elif stripped.startswith('#### '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[5:])
            run.font.size = Pt(10.5)
            run.font.bold = True
        elif stripped.startswith('* ') or stripped.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            parts = stripped[2:].split('**')
            for idx, part in enumerate(parts):
                run = p.add_run(part)
                if idx % 2 == 1:
                    run.font.bold = True
        elif stripped.startswith('---'):
            p = doc.add_paragraph()
            p.add_run('_________________________________________________________________________________').font.color.rgb = RGBColor(200, 200, 200)
        else:
            p = doc.add_paragraph()
            parts = stripped.split('**')
            for idx, part in enumerate(parts):
                run = p.add_run(part)
                if idx % 2 == 1:
                    run.font.bold = True

    if in_table and table_data:
        num_rows = len(table_data)
        num_cols = max(len(row) for row in table_data)
        table = doc.add_table(rows=num_rows, cols=num_cols)
        table.style = 'Table Grid'
        for r_idx, row in enumerate(table_data):
            for c_idx, val in enumerate(row):
                if c_idx < num_cols:
                    cell = table.cell(r_idx, c_idx)
                    cell.text = val
                    if r_idx == 0:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.bold = True

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

def hitung_kktp_dataframe(df, kktp_val):
    kolom_nilai = ["Formatif 1 (LKPD)", "Formatif 2 (Tugas)", "Sumatif Bab 1", "Sumatif Bab 2", "STS", "SAS"]
    for col in kolom_nilai:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df["Rata Formatif"] = df[["Formatif 1 (LKPD)", "Formatif 2 (Tugas)"]].mean(axis=1).round(1)
    df["Rata Sumatif"] = df[["Sumatif Bab 1", "Sumatif Bab 2"]].mean(axis=1).round(1)
    
    df["Nilai Akhir Rapor"] = (
        (df["Rata Formatif"] * 0.3) +
        (df["Rata Sumatif"] * 0.3) +
        (df["STS"] * 0.2) +
        (df["SAS"] * 0.2)
    ).round(0)

    df["Status KKTP"] = df["Nilai Akhir Rapor"].apply(
        lambda val: "✅ TUNTAS" if val >= kktp_val else "❌ REMEDIAL"
    )
    return df

# =============================================================================
# FITUR 1: GENERATOR MODUL AJAR (1 PERTEMUAN UTUH - DEEP LEARNING)
# =============================================================================
if menu == "1. Generator Modul Ajar (Deep Learning)":
    st.header("⚡ Generator Modul Ajar Lengkap (1 Pertemuan Utuh)")
    st.caption("Pendekatan Deep Learning (Mindful, Meaningful, & Joyful Learning) - BSKAP No. 046/H/KR/2025")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Informasi Sekolah & Pengajar")
        nama_sekolah = st.text_input("Nama Sekolah / Yayasan:", value="SMP YAYASAN INTERNASIONAL")
        nama_guru = st.text_input("Nama Guru / Penyusun:", value="Ridho Kurniawan, S.Pd.")
        mapel = st.selectbox("Mata Pelajaran:", ["Ilmu Pengetahuan Sosial (IPS)", "Pendidikan Pancasila (PPKn)"])
        tingkat_kelas = st.selectbox("Pilih Tingkatan Kelas:", ["Kelas VII / Fase D", "Kelas VIII / Fase D", "Kelas IX / Fase D"])
        semester = st.selectbox("Semester:", ["Ganjil", "Genap"])
        hari = st.selectbox("Hari Mengajar:", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"])
        tahun_ajaran = st.text_input("Tahun Pelajaran:", value="2026/2027")

    with col2:
        st.subheader("📖 Materi & Pengaturan Jam Pelajaran")
        draf_bab = DATABASE_MATERI.get(mapel, {}).get(tingkat_kelas, {})
        pilihan_bab = list(draf_bab.keys()) if draf_bab else ["Tidak ada data Bab"]
        bab_materi = st.selectbox("Pilih Bab / Topik Utama:", pilihan_bab)
        
        pilihan_sub_materi = draf_bab.get(bab_materi, [])
        sub_materi_terpilih = st.multiselect(
            "Pilih Sub-Materi Pembelajaran Hari Ini:",
            options=pilihan_sub_materi,
            default=pilihan_sub_materi[:1] if pilihan_sub_materi else []
        )
        str_sub_materi = ", ".join(sub_materi_terpilih) if sub_materi_terpilih else "Materi Pokok"

        jam_terpilih = st.multiselect(
            "Pilih Jam Pelajaran untuk Pertemuan Ini:",
            options=list(DATA_JAM_SEKOLAH.keys()),
            default=["Jam 5", "Jam 6", "Jam 7"]
        )

    st.markdown("---")
    if st.button("🚀 Generate Modul Ajar (1 Pertemuan Utuh)", type="primary", use_container_width=True):
        if not jam_terpilih:
            st.error("❌ Silakan pilih minimal 1 jam pelajaran!")
        else:
            total_jp = len(jam_terpilih)
            waktu_mulai = DATA_JAM_SEKOLAH[jam_terpilih[0]]["waktu"].split(" - ")[0]
            waktu_selesai = DATA_JAM_SEKOLAH[jam_terpilih[-1]]["waktu"].split(" - ")[1]
            total_menit = sum([DATA_JAM_SEKOLAH[j]["durasi"] for j in jam_terpilih])
            rincian_jam_str = ", ".join(jam_terpilih)
            
            menit_awal = 10 if total_jp <= 2 else 15
            menit_akhir = 10 if total_jp <= 2 else 15
            menit_inti = total_menit - menit_awal - menit_akhir

            ada_zuhur = "Jam 5" in jam_terpilih and any(j in jam_terpilih for j in ["Jam 6", "Jam 7", "Jam 8"])
            catatan_zuhur = "\n> **Catatan Jeda:** *Pertemuan ini terpotong jeda Shalat Zuhur (12:10 - 12:30 WIB) pada transisi Jam 5 ke Jam 6.*\n" if ada_zuhur else ""

            st.success(f"✅ Modul Ajar 1 Pertemuan Berhasil Dibuat! Total: {total_jp} JP ({total_menit} Menit) | {waktu_mulai} - {waktu_selesai} WIB")

            modul_text = f"""
# MODUL AJAR KURIKULUM MERDEKA (DEEP LEARNING MODEL)
**MATA PELAJARAN:** {mapel.upper()}  
**STANDAR KEPUTUSAN BSKAP NOMOR 046/H/KR/2025**

---

## I. INFORMASI UMUM

### A. IDENTITAS MODUL
* **Nama Sekolah:** {nama_sekolah}
* **Nama Penyusun:** {nama_guru}
* **Mata Pelajaran:** {mapel}
* **Kelas / Fase / Semester:** {tingkat_kelas} / {semester}
* **Pelaksanaan:** **1 Pertemuan Utuh** (Hari {hari}, {rincian_jam_str})
* **Waktu Pelaksanaan:** Pukul {waktu_mulai} - {waktu_selesai} WIB
* **Alokasi Waktu:** {total_jp} JP (Total Durasi Efektif: {total_menit} Menit)
* **Bab / Tema Utama:** {bab_materi}
* **Sub-Materi Pembelajaran:** {str_sub_materi}
* **Tahun Pelajaran:** {tahun_ajaran}

### B. KOMPETENSI AWAL
1. Peserta didik telah memiliki pemahaman dasar terkait kehidupan sosial dan lingkungan sekitar.
2. Peserta didik memiliki kemampuan awal dalam mengidentifikasi fenomena sosial/pancasila di kehidupan sehari-hari.

### C. PROFIL PELAJAR PANCASILA
* **Beriman, Bertakwa kepada Tuhan YME, dan Berakhlak Mulia:** Menghargai norma dan nilai kemanusiaan.
* **Bernalar Kritis:** Mampu menganalisis fenomena dan masalah kontekstual secara logis.
* **Gotong Royong:** Berkolaborasi aktif dalam diskusi kelompok dan pemecahan masalah.

### D. SARANA DAN PRASARANA
* **Media:** Laptop, Proyektor, Slide Presentasi, Artikel Studi Kasus, Lembar Kerja Peserta Didik (LKPD).
* **Sumber Belajar:** Buku Paket Siswa Kurikulum Merdeka {mapel}, Artikel Lingkungan Sekitar.

### E. TARGET PESERTA DIDIK & MODEL
* **Target:** Peserta didik reguler / tipikal.
* **Model Pembelajaran:** *Deep Learning Model* (Mindful, Meaningful, & Joyful Learning) dengan pendekatan *Problem-Based Learning*.

---

## II. KOMPONEN INTI

### A. TUJUAN PEMBELAJARAN (TP)
1. Peserta didik mampu mendeskripsikan dan menganalisis konsep {str_sub_materi} secara kritis.
2. Peserta didik mampu mengidentifikasi serta memecahkan masalah kontekstual yang berkaitan dengan {bab_materi}.
3. Peserta didik mampu menyajikan hasil analisis kelompok melalui presentasi interaktif secara komunikatif.

### B. PEMAHAMAN BERMAKNA (MEANINGFUL LEARNING)
* Memahami {str_sub_materi} membantu peserta didik menyadari peran aktifnya sebagai warga negara yang kritis, bijak, dan bertanggung jawab.

### C. PERTANYAAN PEMANTIK
1. *Mengapa fenomena {str_sub_materi} sangat dekat dengan kehidupan sehari-hari kita?*
2. *Sikap apa yang harus kita tunjukkan saat menghadapi isu {bab_materi} di masyarakat?*

---

## III. KEGIATAN PEMBELAJARAN (PERTEMUAN TUNGGAL - {total_jp} JP)
{catatan_zuhur}
### A. PENDAHULUAN ({menit_awal} MENIT) - *Mindful Start*
1. **Pembukaan & Orientasi:** Guru menyapa peserta didik, memimpin doa bersama, dan mengecek kehadiran.
2. **Apersepsi & Motivasi:** Guru mengaitkan materi **{str_sub_materi}** dengan pengalaman atau pengamatan sehari-hari peserta didik.
3. **Penyampaian Tujuan:** Guru menjelaskan tujuan pembelajaran, alokasi waktu, serta skenario kegiatan pertemuan hari ini.
4. **Pertanyaan Pemantik:** Guru menyampaikan pertanyaan pemantik untuk memicu keterlibatan aktif siswa.

### B. KEGIATAN INTI ({menit_inti} MENIT) - *Meaningful & Joyful Learning*
1. **Eksplorasi Konsep (~15-20 Menit):** 
   * Peserta didik mengamati tayangan/studi kasus nyata mengenai **{str_sub_materi}**.
   * Guru memberikan penguatan awal konsep dasar terkait **{bab_materi}**.
2. **Kolaborasi Kelompok (~{max(menit_inti - 35, 10)} Menit):** 
   * Peserta didik dibagi ke dalam kelompok heterogen (4-5 siswa).
   * Kelompok berdiskusi menyelesaikan analisis kasus pada LKPD terkait **{str_sub_materi}**.
   * Guru mengobservasi dan memberikan bimbingan (*scaffolding*) sesuai kebutuhan kelompok.
   *(Jika kegiatan melewati pukul 12:10 WIB, diskusi diistirahatkan sejenak untuk Shalat Zuhur).*
3. **Unjuk Karya & Pleno (~15-20 Menit):** 
   * Perwakilan kelompok mempresentasikan hasil solusi/diskusi di depan kelas.
   * Kelompok lain memberikan masukan dan tanggapan secara kritis dan santun.

### C. PENUTUP ({menit_akhir} MENIT) - *Deep Reflection*
1. **Rangkuman & Kesimpulan:** Guru bersama peserta didik menyimpulkan poin utama materi **{str_sub_materi}**.
2. **Refleksi Pembelajaran:** Peserta didik mengisi lembar refleksi singkat tentang proses belajar hari ini.
3. **Apresiasi & Penutup:** Guru memberikan apresiasi, menyampaikan rencana materi minggu depan, dan mengakhiri dengan doa bersama.

---

## IV. ASESMEN & EVALUASI
1. **Asesmen Sikap:** Observasi Profil Pelajar Pancasila (Bernalar Kritis, Gotong Royong).
2. **Asesmen Formatif:** Penilaian kinerja diskusi kelompok dan pengerjaan LKPD.
3. **Asesmen Performa:** Rubrik penilaian presentasi kelompok.

---

## V. LAMPIRAN (LKPD DEEP LEARNING)

### LEMBAR KERJA PESERTA DIDIK (LKPD)
* **Kelompok:** ...........................................
* **Kelas / Hari:** {tingkat_kelas} / {hari}
* **Materi:** {str_sub_materi}
* **Instruksi Tugas:**
  1. Amatilah studi kasus yang diberikan mengenai {str_sub_materi}!
  2. Identifikasi masalah utama dan dampak yang ditimbulkannya!
  3. Diskusikan 2-3 solusi nyata yang dapat diterapkan oleh pelajar!
  4. Presentasikan hasil diskusimu di depan kelas!

---
**Mengetahui,**  
Kepala Sekolah  

**( .................................................... )**  

**Guru Mata Pelajaran**  

**({nama_guru})**
        """

        st.markdown(modul_text)
        
        word_data = to_word(modul_text)
        nama_file_clean = mapel.replace(" ", "_").replace("(", "").replace(")", "")
        
        st.download_button(
            label="📄 Download Modul Ajar Lengkap (Word / .docx)",
            data=word_data,
            file_name=f"Modul_Ajar_{nama_file_clean}_{tingkat_kelas[:8].replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# =============================================================================
# FITUR 2: INFO JADWAL JAM SEKOLAH
# =============================================================================
elif menu == "2. Info Jadwal Jam Sekolah":
    st.header("🕒 Rincian Jam Pelajaran Sekolah")
    st.write("Tabel acuan waktu dan durasi untuk tiap jam pelajaran:")
    
    jadwal_data = []
    for k, v in DATA_JAM_SEKOLAH.items():
        jadwal_data.append({
            "Jam Pelajaran": k,
            "Rentang Waktu": v["waktu"],
            "Durasi (Menit)": f"{v['durasi']} Menit"
        })
    
    st.table(jadwal_data)
    
    st.info("""
    **Catatan Jadwal Istirahat & Shalat:**
    * **Istirahat 1:** 09:30 - 09:45 WIB
    * **Istirahat 2:** 11:05 - 11:20 WIB
    * **Shalat Zuhur:** 12:10 - 12:30 WIB (Berada di antara Jam 5 dan Jam 6)
    """)

# =============================================================================
# FITUR 3: PRESENSI DROPDOWN LINTAS KELAS
# =============================================================================
elif menu == "3. Presensi Dropdown Lintas Kelas":
    st.header("📋 Presensi Siswa Dropdown Lintas Kelas")
    selected_kelas = st.selectbox("Pilih Kelas:", daftar_kelas)

    if f"presensi_{selected_kelas}" not in st.session_state:
        st.session_state[f"presensi_{selected_kelas}"] = pd.DataFrame({
            "NIS": ["1001", "1002", "1003", "1004", "1005"],
            "Nama Siswa": [f"Ahmad Fauzi ({selected_kelas})", f"Budi Santoso ({selected_kelas})", f"Citra Dewi ({selected_kelas})", f"Dina Maria ({selected_kelas})", f"Eko Prasetyo ({selected_kelas})"],
            "L/P": ["L", "L", "P", "P", "L"],
            "P1": ["H", "H", "H", "S", "H"],
            "P2": ["H", "H", "I", "S", "H"],
            "P3": ["H", "A", "H", "H", "H"],
            "P4": ["H", "H", "H", "H", "H"],
            "P5": ["H", "H", "H", "H", "H"]
        })

    df_presensi = st.session_state[f"presensi_{selected_kelas}"]

    edited_df = st.data_editor(
        df_presensi,
        column_config={
            "P1": st.column_config.SelectboxColumn("P1", options=["H", "S", "I", "A"], required=True),
            "P2": st.column_config.SelectboxColumn("P2", options=["H", "S", "I", "A"], required=True),
            "P3": st.column_config.SelectboxColumn("P3", options=["H", "S", "I", "A"], required=True),
            "P4": st.column_config.SelectboxColumn("P4", options=["H", "S", "I", "A"], required=True),
            "P5": st.column_config.SelectboxColumn("P5", options=["H", "S", "I", "A"], required=True),
        },
        num_rows="dynamic",
        use_container_width=True
    )

    st.session_state[f"presensi_{selected_kelas}"] = edited_df

    cols_p = [c for c in edited_df.columns if c.startswith("P")]
    edited_df["Hadir (H)"] = edited_df[cols_p].apply(lambda x: (x == "H").sum(), axis=1)
    edited_df["Sakit (S)"] = edited_df[cols_p].apply(lambda x: (x == "S").sum(), axis=1)
    edited_df["Izin (I)"] = edited_df[cols_p].apply(lambda x: (x == "I").sum(), axis=1)
    edited_df["Alpa (A)"] = edited_df[cols_p].apply(lambda x: (x == "A").sum(), axis=1)

    st.subheader(f"📊 Rekapitulasi Presensi - {selected_kelas}")
    st.dataframe(edited_df[["NIS", "Nama Siswa", "Hadir (H)", "Sakit (S)", "Izin (I)", "Alpa (A)"]], use_container_width=True)

    st.download_button(
        label=f"📥 Download Presensi {selected_kelas} (Excel)",
        data=to_excel(edited_df, f"Presensi_{selected_kelas}"),
        file_name=f"Presensi_{selected_kelas}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =============================================================================
# FITUR 4: BUKU NILAI & KKTP (SATU TABEL)
# =============================================================================
else:
    st.header("📖 Buku Nilai & Pengolahan Rapor Terpadu (Satu Tabel)")
    st.write("Ketik atau ubah nilai secara langsung pada tabel. Hasil kalkulasi **Rata-Rata, Nilai Akhir, dan Status KKTP** langsung diperbarui otomatis.")

    col_k1, col_k2 = st.columns([2, 3])
    with col_k1:
        selected_kelas_nilai = st.selectbox("Pilih Kelas Buku Nilai:", daftar_kelas, key="nilai_kelas_key")
    with col_k2:
        kktp_limit = st.slider("Batas Kriteria Ketercapaian Tujuan Pembelajaran (KKTP):", min_value=60, max_value=85, value=75)

    if f"nilai_{selected_kelas_nilai}" not in st.session_state:
        raw_data = pd.DataFrame({
            "NIS": ["1001", "1002", "1003", "1004", "1005"],
            "Nama Siswa": [
                f"Ahmad Fauzi ({selected_kelas_nilai})", 
                f"Budi Santoso ({selected_kelas_nilai})", 
                f"Citra Dewi ({selected_kelas_nilai})", 
                f"Dina Maria ({selected_kelas_nilai})", 
                f"Eko Prasetyo ({selected_kelas_nilai})"
            ],
            "Formatif 1 (LKPD)": [85.0, 80.0, 90.0, 70.0, 60.0],
            "Formatif 2 (Tugas)": [88.0, 82.0, 92.0, 75.0, 65.0],
            "Sumatif Bab 1": [80.0, 78.0, 88.0, 65.0, 55.0],
            "Sumatif Bab 2": [85.0, 80.0, 90.0, 70.0, 60.0],
            "STS": [78.0, 75.0, 85.0, 68.0, 62.0],
            "SAS": [82.0, 80.0, 88.0, 72.0, 60.0]
        })
        st.session_state[f"nilai_{selected_kelas_nilai}"] = hitung_kktp_dataframe(raw_data, kktp_limit)

    df_current = st.session_state[f"nilai_{selected_kelas_nilai}"]
    df_current = hitung_kktp_dataframe(df_current, kktp_limit)

    st.subheader(f"📊 Tabel Penilaian Rapor Lengkap - {selected_kelas_nilai}")
    
    edited_unified_df = st.data_editor(
        df_current,
        column_config={
            "NIS": st.column_config.TextColumn("NIS", disabled=False),
            "Nama Siswa": st.column_config.TextColumn("Nama Siswa", disabled=False),
            "Formatif 1 (LKPD)": st.column_config.NumberColumn("Formatif 1", min_value=0, max_value=100, step=1),
            "Formatif 2 (Tugas)": st.column_config.NumberColumn("Formatif 2", min_value=0, max_value=100, step=1),
            "Sumatif Bab 1": st.column_config.NumberColumn("Sumatif 1", min_value=0, max_value=100, step=1),
            "Sumatif Bab 2": st.column_config.NumberColumn("Sumatif 2", min_value=0, max_value=100, step=1),
            "STS": st.column_config.NumberColumn("STS", min_value=0, max_value=100, step=1),
            "SAS": st.column_config.NumberColumn("SAS", min_value=0, max_value=100, step=1),
            "Rata Formatif": st.column_config.NumberColumn("Rata Formatif", disabled=True, format="%.1f"),
            "Rata Sumatif": st.column_config.NumberColumn("Rata Sumatif", disabled=True, format="%.1f"),
            "Nilai Akhir Rapor": st.column_config.NumberColumn("Nilai Akhir", disabled=True, format="%d"),
            "Status KKTP": st.column_config.TextColumn("Status KKTP", disabled=True),
        },
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_unified_{selected_kelas_nilai}"
    )

    updated_df = hitung_kktp_dataframe(edited_unified_df, kktp_limit)
    st.session_state[f"nilai_{selected_kelas_nilai}"] = updated_df

    st.download_button(
        label=f"📥 Download Rekap Buku Nilai Lengkap {selected_kelas_nilai} (Excel)",
        data=to_excel(updated_df, sheet_name=f"Nilai_{selected_kelas_nilai}"),
        file_name=f"Buku_Nilai_Lengkap_{selected_kelas_nilai}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
