import streamlit as st
import pandas as pd
import io

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Aplikasi Administrasi Guru Digital - Deep Learning IPS & PPKn",
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
st.markdown('<div class="sub-header">Generator Modul Ajar Deep Learning (BSKAP 2025), Presensi Dropdown Lintas Kelas & Buku Nilai KKTP</div>', unsafe_allow_html=True)

# Sidebar Navigasi
st.sidebar.title("📌 Navigasi Fitur")
menu = st.sidebar.radio(
    "Pilih Modul Aplikasi:",
    ["1. Generator Modul Ajar (Deep Learning)", "2. Presensi Dropdown Lintas Kelas", "3. Buku Nilai & Status KKTP"]
)

daftar_kelas = ["Kelas 7A", "Kelas 7B", "Kelas 8", "Kelas 9"]

# Database Bab & Sub-Materi Lengkap IPS & PPKn (Disesuaikan dari Google Drive & BSKAP 046/2025)
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

# Helper Function untuk Export Dataframe ke Excel
def to_excel(df, sheet_name="Data_Administrasi"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# ==========================================
# FITUR 1: GENERATOR MODUL AJAR DEEP LEARNING
# ==========================================
if menu == "1. Generator Modul Ajar (Deep Learning)":
    st.header("⚡ Generator Modul Ajar Otomatis (Deep Learning)")
    st.write("Format disesuaikan 100% dengan Standar Modul Ajar Deep Learning (*Mindful, Meaningful, & Joyful Learning*) BSKAP No. 046/H/KR/2025.")

    col1, col2 = st.columns(2)
    with col1:
        nama_sekolah = st.text_input("Nama Sekolah / Yayasan:", value="SMP YAYASAN")
        nama_guru = st.text_input("Nama Guru / Penyusun:", value="Ridho Kurniawan, S.Pd.")
        mapel = st.selectbox("Mata Pelajaran:", ["Ilmu Pengetahuan Sosial (IPS)", "Pendidikan Pancasila (PPKn)"])
        
        tingkat_kelas = st.selectbox("Pilih Tingkatan Kelas:", ["Kelas VII / Fase D", "Kelas VIII / Fase D", "Kelas IX / Fase D"])
        semester = st.selectbox("Semester:", ["Ganjil", "Genap"])
        fase_kelas = f"{tingkat_kelas} / {semester}"

    with col2:
        # Otomatisasi Dropdown Bab sesuai Mapel & Tingkatan Kelas
        draf_bab = DATABASE_MATERI.get(mapel, {}).get(tingkat_kelas, {})
        pilihan_bab = list(draf_bab.keys()) if draf_bab else ["Tidak ada data Bab"]
        
        bab_materi = st.selectbox("Pilih Bab / Topik Utama:", pilihan_bab)
        
        # Otomatisasi Multi-Select Sub-Materi (Bisa pilih lebih dari 1)
        pilihan_sub_materi = draf_bab.get(bab_materi, [])
        sub_materi_terpilih = st.multiselect(
            "Pilih Sub-Materi Pembelajaran (Bisa pilih lebih dari 1):",
            options=pilihan_sub_materi,
            default=pilihan_sub_materi[:2] if pilihan_sub_materi else []
        )
        
        # Gabungkan Sub-materi terpilih menjadi bentuk teks
        str_sub_materi = ", ".join(sub_materi_terpilih) if sub_materi_terpilih else "Belum memilih sub-materi"

        alokasi_jp = st.number_input("Alokasi Waktu (JP):", min_value=2, max_value=36, value=4, step=2)
        tahun_ajaran = st.text_input("Tahun Pelajaran:", value="2026/2027")

    instruksi_khusus = st.text_area("Instruksi / Catatan Khusus Kepala Sekolah (Konteks Lokal):", value="Integrasikan studi kasus konteks lokal wilayah sekitar, analisis kritis, dan diskusi interaktif.")

    if st.button("🚀 Generate Modul Ajar Deep Learning"):
        st.success(f"Berhasil meng-generate Modul Ajar **{mapel}** berbasis **Deep Learning**!")
        
        # Format Teks Modul Ajar Sesuai Template BSKAP 2025 & Deep Learning
        modul_text = f"""
# MODUL AJAR KURIKULUM MERDEKA (DEEP LEARNING)
**MATA PELAJARAN:** {mapel.upper()}  
**STANDAR KEPUTUSAN BSKAP NOMOR 046/H/KR/2025**

---

### A. IDENTITAS MODUL
* **Nama Sekolah:** {nama_sekolah}
* **Nama Penyusun:** {nama_guru}
* **Mata Pelajaran:** {mapel}
* **Kelas / Fase / Semester:** {fase_kelas}
* **Bab / Topik Utama:** {bab_materi}
* **Sub-Materi Pembelajaran:** {str_sub_materi}
* **Alokasi Waktu:** {alokasi_jp} JP
* **Tahun Pelajaran:** {tahun_ajaran}

### B. IDENTIFIKASI KESIAPAN PESERTA DIDIK
* **Pengetahuan Awal:** Peserta didik memiliki pemahaman dasar terkait topik {str_sub_materi} di lingkungan sekitar.
* **Minat:** Tertarik pada media visual/digital, diskusi kelompok, simulasi interaktif, dan analisis isu nyata.
* **Latar Belakang:** Berasal dari latar belakang sosial-ekonomi yang beragam yang memengaruhi pemahaman awal terhadap fenomena sosial/pancasila.
* **Kebutuhan Belajar:**
  - *Visual:* Gambar, peta digital, video pembelajaran, dan infografis.
  - *Auditori:* Diskusi kelompok, tanya jawab, penjelasan guru yang interaktif, dan mendengarkan paparan & kisah sejarah/sosial.
  - *Kinestetik:* Praktik pemetaan, bermain peran (role-play), unjuk karya, dan penyusunan produk kreatif.

### C. KARAKTERISTIK MATERI PELAJARAN
* **Jenis Pengetahuan:** Konseptual (memahami teori & prinsip) dan Prosedural (keterampilan pemecahan masalah & karya).
* **Relevansi Kehidupan Nyata:** Sangat relevan karena dimulai dari lingkungan terdekat peserta didik (keluarga, sekolah, masyarakat).
* **Tingkat Kesulitan:** Sedang & Berjenjang (dari konsep konkret menuju konsep analisis abstrak).
* **Integrasi Nilai & Karakter:** Keimanan, Penalaran Kritis, Kreativitas, Kolaborasi, Kemandirian, dan Kepedulian Sosial.

### D. DIMENSI PROFIL LULUSAN
Bernalar Kritis, Gotong Royong (Kolaborasi), Mandiri, Berkebinekaan Global, dan Komunikasi Efektif.

### E. DESAIN DEEP LEARNING (3 ELEMEN UTAMA)
1. **Mindful Learning (Kesadaran Utuh):**
   Apersepsi berkesadaran di mana peserta didik diajak merefleksikan pengalaman pribadi dan menyadari pentingnya mempelajari {str_sub_materi}.
2. **Meaningful Learning (Pembelajaran Bermakna):**
   Materi dihubungkan langsung dengan konteks kehidupan sehari-hari dan pemecahan masalah nyata di masyarakat.
3. **Joyful Learning (Pembelajaran Menyenangkan):**
   Penggunaan media interaktif, permainan edukatif, diskusi kelompok kolaboratif, dan presentasi hasil karya yang menggembirakan.

### F. STRATEGI PEMBELAJARAN BERDIFERENSIASI
* **Diferensiasi Konten:** Menyediakan variasi bahan bacaan, gambar, dan video sesuai tingkat kesiapan peserta didik.
* **Diferensiasi Proses:** Bimbingan kelompok terstruktur (scaffolding) sesuai tingkat pemahaman.
* **Diferensiasi Produk:** Kebebasan memilih bentuk sajian karya (laporan, poster, infografis, atau presentasi lisan).

### G. SKENARIO KEGIATAN PEMBELAJARAN
* **Pendahuluan (15 Menit):** 
  - Orientasi Mindful Start & Refleksi Kesadaran Awal.
  - Penyampaian Tujuan Pembelajaran & Pertanyaan Pemantik Kontekstual.
* **Kegiatan Inti ({alokasi_jp * 40 - 30} Menit):**
  - *Eksplorasi Konsep (Mindful Exploration):* Menelaah materi {str_sub_materi}.
  - *Koneksi Bermakna (Meaningful Task):* Diskusi pemecahan masalah/studi kasus kontekstual secara berkolaborasi.
  - *Unjuk Karya & Refleksi (Joyful Share):* Presentasi kreatif antar kelompok dan pemberian umpan balik positif (peer review).
* **Penutup (15 Menit):** Kesimpulan bersama, evaluasi mandiri, refleksi pembelajaran, dan tindak lanjut.

### H. ASESMEN PEMBELAJARAN
* **Asesmen Formatif:** Lembar Kerja Peserta Didik (LKPD) Deep Learning, Observasi Diskusi, & Unjuk Kerja.
* **Asesmen Sumatif:** Tes Tertulis Konseptual & Analisis Studi Kasus.
        """
        
        st.markdown(modul_text)
        
        # Export ke Excel
        df_modul = pd.DataFrame([{
            "Nama Sekolah": nama_sekolah,
            "Penyusun": nama_guru,
            "Mata Pelajaran": mapel,
            "Kelas/Fase": fase_kelas,
            "Bab / Topik": bab_materi,
            "Sub-Materi": str_sub_materi,
            "Alokasi JP": alokasi_jp,
            "Isi Lengkap Modul Ajar": modul_text
        }])
        
        excel_data_modul = to_excel(df_modul, sheet_name="Modul_Ajar_DeepLearning")
        st.download_button(
            label="📥 Download Modul Ajar Standar BSKAP (Excel)",
            data=excel_data_modul,
            file_name=f"Modul_Ajar_DeepLearning_{mapel}_{tingkat_kelas[:8]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==========================================
# FITUR 2: PRESENSI DROPDOWN LINTAS KELAS
# ==========================================
elif menu == "2. Presensi Dropdown Lintas Kelas":
    st.header("📋 Presensi Siswa Dropdown Lintas Kelas (7A, 7B, 8, 9)")
    st.write("Pilih kelas di bawah. Data presensi **terpisah rapi per kelas** agar tidak bercampur.")

    selected_kelas = st.selectbox("Pilih Kelas yang Ingin Diisi / Dilihat:", daftar_kelas)

    # State Presensi per Kelas
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

    st.subheader(f"Input Presensi Manual (Dropdown) - {selected_kelas}")
    st.info("💡 **Tips:** Klik sel pada kolom **P1–P5**, lalu pilih status: **H** (Hadir), **S** (Sakit), **I** (Izin), atau **A** (Alpa). Kamu juga bisa menambah/mengubah nama siswa langsung pada tabel.")

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

    # Hitung Rumus COUNTIF Otomatis
    cols_p = [c for c in edited_df.columns if c.startswith("P")]
    edited_df["Hadir (H)"] = edited_df[cols_p].apply(lambda x: (x == "H").sum(), axis=1)
    edited_df["Sakit (S)"] = edited_df[cols_p].apply(lambda x: (x == "S").sum(), axis=1)
    edited_df["Izin (I)"] = edited_df[cols_p].apply(lambda x: (x == "I").sum(), axis=1)
    edited_df["Alpa (A)"] = edited_df[cols_p].apply(lambda x: (x == "A").sum(), axis=1)

    st.subheader(f"📊 Hasil Rekapitulasi Otomatis (COUNTIF) - {selected_kelas}")
    st.dataframe(edited_df[["NIS", "Nama Siswa", "Hadir (H)", "Sakit (S)", "Izin (I)", "Alpa (A)"]], use_container_width=True)

    # Tombol Download Excel
    excel_presensi = to_excel(edited_df, sheet_name=f"Presensi_{selected_kelas}")
    st.download_button(
        label=f"📥 Download Rekap Presensi {selected_kelas} (Excel)",
        data=excel_presensi,
        file_name=f"Presensi_Siswa_{selected_kelas}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==========================================
# FITUR 3: BUKU NILAI & STATUS KKTP (REAL-TIME UPDATE)
# ==========================================
else:
    st.header("📖 Buku Nilai Terpisah per Kelas & Keketatan KKTP")
    st.write("Buku nilai terpisah untuk **7A, 7B, Kelas 8, dan Kelas 9** agar pengelolaan nilai Formatif, Sumatif, STS, dan SAS akurat.")

    selected_kelas_nilai = st.selectbox("Pilih Kelas Buku Nilai:", daftar_kelas, key="nilai_kelas_key")

    # Inisialisasi State jika belum ada
    if f"nilai_{selected_kelas_nilai}" not in st.session_state:
        st.session_state[f"nilai_{selected_kelas_nilai}"] = pd.DataFrame({
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
            "STS (Tengah Sem)": [78.0, 75.0, 85.0, 68.0, 62.0],
            "SAS (Akhir Sem)": [82.0, 80.0, 88.0, 72.0, 60.0]
        })

    df_nilai = st.session_state[f"nilai_{selected_kelas_nilai}"]

    # Slider Batas KKTP
    kktp_limit = st.slider("Batas Kriteria Ketercapaian Tujuan Pembelajaran (KKTP):", min_value=60, max_value=85, value=75)

    st.subheader(f"Input Nilai Siswa - {selected_kelas_nilai}")
    st.info("💡 **Petunjuk:** Ubah atau ketik nilai di kolom Formatif, Sumatif, STS, atau SAS. Hasil kalkulasi dan status KKTP di bawah akan langsung terupdate secara otomatis!")

    # Input nilai melalui Data Editor
    edited_nilai_df = st.data_editor(
        df_nilai, 
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_{selected_kelas_nilai}"
    )

    # Pastikan tipe data numerik untuk kolom penilaian
    kolom_nilai = ["Formatif 1 (LKPD)", "Formatif 2 (Tugas)", "Sumatif Bab 1", "Sumatif Bab 2", "STS (Tengah Sem)", "SAS (Akhir Sem)"]
    for col in kolom_nilai:
        edited_nilai_df[col] = pd.to_numeric(edited_nilai_df[col], errors='coerce').fillna(0)

    # 1. Kalkulasi Otomatis Rata-rata
    edited_nilai_df["Rata Formatif"] = edited_nilai_df[["Formatif 1 (LKPD)", "Formatif 2 (Tugas)"]].mean(axis=1).round(1)
    edited_nilai_df["Rata Sumatif Bab"] = edited_nilai_df[["Sumatif Bab 1", "Sumatif Bab 2"]].mean(axis=1).round(1)
    
    # 2. Formula Bobot Nilai Akhir Rapor (30% Formatif + 30% Sumatif Bab + 20% STS + 20% SAS)
    edited_nilai_df["Nilai Akhir Rapor"] = (
        (edited_nilai_df["Rata Formatif"] * 0.3) +
        (edited_nilai_df["Rata Sumatif Bab"] * 0.3) +
        (edited_nilai_df["STS (Tengah Sem)"] * 0.2) +
        (edited_nilai_df["SAS (Akhir Sem)"] * 0.2)
    ).round(0)

    # 3. Status Ketuntasan KKTP
    edited_nilai_df["Status KKTP"] = edited_nilai_df["Nilai Akhir Rapor"].apply(
        lambda val: "✅ TUNTAS" if val >= kktp_limit else "❌ REMEDIAL"
    )

    # Simpan kembali hasil kalkulasi terbaru ke session_state
    st.session_state[f"nilai_{selected_kelas_nilai}"] = edited_nilai_df

    st.subheader(f"🎯 Hasil Pengolahan Rapor & Status KKTP - {selected_kelas_nilai}")
    
    # Tampilkan tabel rekapitulasi hasil kalkulasi
    st.dataframe(
        edited_nilai_df[["NIS", "Nama Siswa", "Rata Formatif", "Rata Sumatif Bab", "STS (Tengah Sem)", "SAS (Akhir Sem)", "Nilai Akhir Rapor", "Status KKTP"]], 
        use_container_width=True
    )

    # Tombol Download Excel dengan data rekapitulasi lengkap
    excel_nilai = to_excel(edited_nilai_df, sheet_name=f"Nilai_{selected_kelas_nilai}")
    st.download_button(
        label=f"📥 Download Buku Nilai {selected_kelas_nilai} (Excel)",
        data=excel_nilai,
        file_name=f"Buku_Nilai_{selected_kelas_nilai}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
