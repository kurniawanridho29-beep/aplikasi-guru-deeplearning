import streamlit as st
import pandas as pd
import io

# Konfigurasi Halaman Utama
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

# Sidebar Navigasi
st.sidebar.title("📌 Navigasi Fitur")
menu = st.sidebar.radio(
    "Pilih Modul Aplikasi:",
    ["1. Generator Modul Ajar (Deep Learning)", "2. Presensi Dropdown Lintas Kelas", "3. Buku Nilai & Status KKTP (Satu Tabel)"]
)

daftar_kelas = ["Kelas 7A", "Kelas 7B", "Kelas 8", "Kelas 9"]

# Database Bab & Sub-Materi Lengkap IPS & PPKn (Berdasarkan Struktur Drive & BSKAP 2025)
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

# Helper Function Export Excel
def to_excel(df, sheet_name="Data_Administrasi"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# Helper Kalkulasi Nilai
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

# ==========================================
# FITUR 1: GENERATOR MODUL AJAR LENGKAP (DEEP LEARNING)
# ==========================================
if menu == "1. Generator Modul Ajar (Deep Learning)":
    st.header("⚡ Generator Modul Ajar Lengkap & Komprehensif (Deep Learning)")
    st.write("Format disesuaikan dengan Standar Modul Ajar Deep Learning (*Mindful, Meaningful, & Joyful Learning*) BSKAP No. 046/H/KR/2025 & Template Lengkap Drive.")

    col1, col2 = st.columns(2)
    with col1:
        nama_sekolah = st.text_input("Nama Sekolah / Yayasan:", value="SMP YAYASAN INTERNASIONAL")
        nama_guru = st.text_input("Nama Guru / Penyusun:", value="Ridho Kurniawan, S.Pd.")
        mapel = st.selectbox("Mata Pelajaran:", ["Ilmu Pengetahuan Sosial (IPS)", "Pendidikan Pancasila (PPKn)"])
        tingkat_kelas = st.selectbox("Pilih Tingkatan Kelas:", ["Kelas VII / Fase D", "Kelas VIII / Fase D", "Kelas IX / Fase D"])
        semester = st.selectbox("Semester:", ["Ganjil", "Genap"])
        fase_kelas = f"{tingkat_kelas} / {semester}"

    with col2:
        draf_bab = DATABASE_MATERI.get(mapel, {}).get(tingkat_kelas, {})
        pilihan_bab = list(draf_bab.keys()) if draf_bab else ["Tidak ada data Bab"]
        bab_materi = st.selectbox("Pilih Bab / Topik Utama:", pilihan_bab)
        
        pilihan_sub_materi = draf_bab.get(bab_materi, [])
        sub_materi_terpilih = st.multiselect(
            "Pilih Sub-Materi Pembelajaran (Bisa pilih lebih dari 1):",
            options=pilihan_sub_materi,
            default=pilihan_sub_materi[:2] if pilihan_sub_materi else []
        )
        str_sub_materi = ", ".join(sub_materi_terpilih) if sub_materi_terpilih else "Materi Pokok Bab"

        alokasi_jp = st.number_input("Alokasi Waktu Total (JP):", min_value=2, max_value=36, value=8, step=2)
        tahun_ajaran = st.text_input("Tahun Pelajaran:", value="2026/2027")

    instruksi_khusus = st.text_area("Pendekatan / Catatan Khusus Guru (Konteks Sekolah):", value="Gunakan studi kasus nyata di lingkungan sekitar sekolah, diskusi kelompok berkolaborasi, dan presentasi produk visual/digital.")

    if st.button("🚀 Generate Modul Ajar Deep Learning Lengkap"):
        st.success(f"Berhasil meng-generate Modul Ajar Lengkap **{mapel}** berbasis **Deep Learning**!")
        
        # FORMAT KOMPREHENSIF LENGKAP SESUAI DRIVE DAN BSKAP 2025
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
* **Kelas / Fase / Semester:** {fase_kelas}
* **Bab / Tema Utama:** {bab_materi}
* **Sub-Materi Pembelajaran:** {str_sub_materi}
* **Alokasi Waktu:** {alokasi_jp} JP (2 Pertemuan x {alokasi_jp//2} JP)
* **Tahun Pelajaran:** {tahun_ajaran}

### B. KOMPETENSI AWAL
1. Peserta didik telah memahami konsep dasar kehidupan bermasyarakat dan lingkungan sosial sekitar.
2. Peserta didik memiliki kemampuan awal dalam mengidentifikasi fenomena sosial/pancasila di lingkungan sehari-hari.

### C. PROFIL PELAJAR PANCASILA
* **Beriman, Bertakwa kepada Tuhan YME, dan Berakhlak Mulia:** Menghargai keberagaman dan norma sosial.
* **Bernalar Kritis:** Mampu menganalisis fenomena sosial/pancasila secara objektif dan berbasis data.
* **Gotong Royong:** Berkolaborasi secara efektif dalam diskusi kelompok dan penyelesaian tugas bersama.
* **Kreatif:** Menghasilkan karya/solusi inovatif terkait topik {str_sub_materi}.

### D. SARANA DAN PRASARANA
* **Media:** Laptop, Proyektor, Peta Konseptual/Digital, Slide Presentasi, Artikel Kasus, Lembar Kerja Peserta Didik (LKPD).
* **Sumber Belajar:** Buku Paket Siswa Kurikulum Merdeka {mapel}, Artikel Berita, Lingkungan Sekitar Sekolah.

### E. TARGET PESERTA DIDIK
* **Target:** Peserta didik reguler / tipikal (tidak ada kesulitan dalam memahami materi ajar).
* **Model Pembelajaran:** *Deep Learning Model* (Mindful, Meaningful, & Joyful Learning) dengan pendekatan *Problem-Based Learning* (PBL).

---

## II. KOMPONEN INTI

### A. TUJUAN PEMBELAJARAN (TP)
1. Peserta didik mampu mendeskripsikan dan menganalisis konsep {str_sub_materi} dengan tepat.
2. Peserta didik mampu mengidentifikasi serta memecahkan masalah kontekstual yang berkaitan dengan {bab_materi} di kehidupan nyata.
3. Peserta didik mampu menyajikan hasil analisis dan solusi kreatif mengenai {str_sub_materi} melalui presentasi atau media visual.

### B. PEMAHAMAN BERMAKNA (MEANINGFUL LEARNING)
* Pemahaman terhadap {str_sub_materi} membantu peserta didik menyadari peran aktifnya sebagai warga negara yang bijak, kritis, dan bertanggung jawab di tengah kehidupan sosial masyarakat.

### C. PERTANYAAN PEMANTIK
1. *Mengapa topik {str_sub_materi} sangat dekat dan penting dalam kehidupan sehari-hari kita?*
2. *Dampak apa yang akan terjadi jika kita tidak memahami dan menerapkan prinsip {bab_materi} di masyarakat?*

---

## III. KEGIATAN PEMBELAJARAN DETAIL (DEEP LEARNING SYNTAX)

### 🔴 PERTEMUAN 1 ({alokasi_jp//2} JP) - EKSPLORASI KONSEP & MINDFUL LEARNING

#### 1. Pendahuluan (15 Menit) - *Mindful Start*
* **Salam & Doa:** Guru membuka pembelajaran dengan salam dan berdoa bersama untuk membangun suasana religius.
* **Apersepsi Kesadaran Utuh (Mindful Awareness):** Guru mengajak peserta didik melakukan refleksi singkat (mengamati gambar/video terkait {str_sub_materi}) dan menanyakan perasaan peserta didik sebelum belajar.
* **Motivasi & Tujuan:** Guru menyampaikan tujuan pembelajaran, alokasi waktu, dan manfaat mempelajari {str_sub_materi}.

#### 2. Kegiatan Inti ({alokasi_jp * 20 - 30} Menit) - *Meaningful & Joyful Exploration*
* **Orientasi Masalah (Meaningful Learning):** Guru menyajikan studi kasus / fenomena nyata yang relevan dengan {str_sub_materi}.
* **Pengorganisasian Kelompok:** Peserta didik dibagi menjadi beberapa kelompok heterogen (4-5 orang).
* **Penyelidikan Terbimbing (Mindful Thinking):** Peserta didik mengumpulkan data dan membaca bahan ajar terkait {str_sub_materi}. Guru melakukan *scaffolding* (bimbingan) sesuai tingkat kebutuhan kelompok.
* **Diskusi Interaktif (Joyful Collaboration):** Kelompok mendiskusikan pertanyaan pada LKPD 1 yang berfokus pada analisis akar masalah dan dampaknya.

#### 3. Penutup (15 Menit)
* Guru dan peserta didik membuat kesimpulan sementara.
* Refleksi singkat mengenai pengalaman belajar hari ini (*Joyful Feedback*).
* Doa penutup dan salam.

---

### 🔴 PERTEMUAN 2 ({alokasi_jp//2} JP) - APLIKASI, UNJUK KARYA & REFLEKSI

#### 1. Pendahuluan (15 Menit)
* Guru mereview kembali pemahaman dari Pertemuan 1 terkait {str_sub_materi}.
* Guru menyampaikan alur kegiatan utama: Penyusunan Solusi dan Presentasi Karya.

#### 2. Kegiatan Inti ({alokasi_jp * 20 - 30} Menit) - *Joyful Share & Action*
* **Penyusunan Produk Kreatif:** Setiap kelompok merumuskan solusi atas masalah {str_sub_materi} dan menyajikannya dalam bentuk poster / infografis / ringkasan visual.
* **Unjuk Kerja & Presentasi (*Joyful Share*):**
  - Masing-masing kelompok mempresentasikan hasil karyanya di depan kelas.
  - Kelompok lain memberikan masukan, pertanyaan, atau tanggapan apresiatif (*Peer Review*).
* **Penguatan Konsep (Meaningful Assessment):** Guru memberikan konfirmasi, penguatan materi, dan meluruskan miskonsepsi.

#### 3. Penutup (15 Menit) - *Deep Reflection*
* **Refleksi Deep Learning:** Peserta didik mengisi lembar refleksi diri tentang apa yang telah dipelajari, perasaan saat berdiskusi, dan komitmen tindakan nyata.
* **Evaluasi / Asesmen Sumatif Singkat:** Pengerjaan soal tes formatif/sumatif secara mandiri.
* **Doa & Penutup.**

---

## IV. ASESMEN PEMBELAJARAN (PENILAIAN)

1. **Asesmen Sikap:** Observasi Profil Pelajar Pancasila (Bernalar Kritis, Gotong Royong, Mandiri).
2. **Asesmen Formatif:** Penilaian Diskusi Kelompok, Observasi Kesiapan, dan Pengerjaan LKPD.
3. **Asesmen Sumatif:** Tes Tertulis Pilihan Ganda / Uraian Analitis mengenai {str_sub_materi}.

---

## V. LAMPIRAN MODUL AJAR

### A. LEMBAR KERJA PESERTA DIDIK (LKPD) DEEP LEARNING
* **Nama Kelompok:** ...........................................
* **Kelas:** {fase_kelas}
* **Materi:** {str_sub_materi}
* **Tugas Diskusi:**
  1. Amatilah fenomena/masalah yang disajikan oleh guru mengenai {str_sub_materi}!
  2. Analisislah penyebab utama timbulnya fenomena tersebut!
  3. Rumuskan 3 solusi kreatif dan rasional yang dapat dilakukan oleh generasi muda untuk mengatasinya!
  4. Sajikan hasil diskusimu dalam bentuk pameran karya visual / poster ringkas!

### B. RUBRIK PENILAIAN DISKUSI & UNJUK KARYA
| Kriteria Penilaian | Sangat Baik (4) | Baik (3) | Cukup (2) | Perlu Bimbingan (1) |
| :--- | :--- | :--- | :--- | :--- |
| **Penguasaan Materi** | Menjelaskan {str_sub_materi} sangat akurat & analitis | Menjelaskan materi dengan akurat | Menjelaskan materi cukup akurat | Kurang memahami materi |
| **Kerjasama Kelompok** | Semua anggota aktif dan saling mendukung | Sebagian besar anggota aktif | Hanya sebagian anggota aktif | Pasif dalam kelompok |
| **Kreativitas Produk** | Sangat kreatif, rapi, dan komunikatif | Kreatif dan rapi | Cukup rapi | Less visual / tidak rapi |

---
**Mengetahui,**  
Kepala Sekolah SMP  

**( .................................................... )**  
NIP.  

**Guru Mata Pelajaran**  

**({nama_guru})**  
NIP.
        """
        
        st.markdown(modul_text)
        
        # Download Excel
        df_modul = pd.DataFrame([{
            "Nama Sekolah": nama_sekolah,
            "Penyusun": nama_guru,
            "Mata Pelajaran": mapel,
            "Kelas/Fase": fase_kelas,
            "Bab / Topik": bab_materi,
            "Sub-Materi": str_sub_materi,
            "Alokasi JP": alokasi_jp,
            "Isi Lengkap Modul Ajar Deep Learning": modul_text
        }])
        
        st.download_button(
            label="📥 Download Modul Ajar Lengkap (Excel)",
            data=to_excel(df_modul, "Modul_Ajar_Lengkap"),
            file_name=f"Modul_Ajar_Lengkap_{mapel}_{tingkat_kelas[:8]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==========================================
# FITUR 2: PRESENSI DROPDOWN LINTAS KELAS
# ==========================================
elif menu == "2. Presensi Dropdown Lintas Kelas":
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

# ==========================================
# FITUR 3: BUKU NILAI & KKTP (SATU TABEL TANPA DELAY)
# ==========================================
else:
    st.header("📖 Buku Nilai & Pengolahan Rapor Terpadu (Satu Tabel)")
    st.write("Ketik atau ubah nilai secara langsung pada tabel. Hasil kalkulasi **Rata-Rata, Nilai Akhir, dan Status KKTP** akan langsung berada di tabel yang sama tanpa delay.")

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
