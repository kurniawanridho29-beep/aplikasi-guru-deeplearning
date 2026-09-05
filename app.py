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

# Helper Function untuk Export Dataframe ke Excel
def to_excel(df, sheet_name="Data_Administrasi"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# ==========================================
# FITUR 1: GENERATOR MODUL AJAR DEEP LEARNING (STANDAR YAYASAN & BSKAP 2025)
# ==========================================
if menu == "1. Generator Modul Ajar (Deep Learning)":
    st.header("⚡ Generator Modul Ajar Otomatis (Deep Learning)")
    st.write("Format disesuaikan 100% dengan Standar Modul Ajar Deep Learning (*Mindful, Meaningful, & Joyful Learning*) BSKAP No. 046/H/KR/2025.")

    col1, col2 = st.columns(2)
    with col1:
        nama_sekolah = st.text_input("Nama Sekolah / Yayasan:", value="SMP YAYASAN")
        nama_guru = st.text_input("Nama Guru / Penyusun:", value="Ridho Kurniawan, S.Pd.")
        mapel = st.selectbox("Mata Pelajaran:", ["Ilmu Pengetahuan Sosial (IPS)", "Pendidikan Pancasila (PPKn)"])
        fase_kelas = st.selectbox("Kelas / Fase / Semester:", [
            "Kelas VII / Fase D / Ganjil",
            "Kelas VII / Fase D / Genap",
            "Kelas VIII / Fase D / Ganjil",
            "Kelas VIII / Fase D / Genap",
            "Kelas IX / Fase D / Ganjil",
            "Kelas IX / Fase D / Genap"
        ])

    with col2:
        bab_materi = st.text_input("Bab / Topik Utama:", value="Bab 1: Keluarga Awal Kehidupan")
        sub_materi = st.text_input("Sub-Materi Pembelajaran:", value="Sejarah Asal Usul Keluarga, Lokasi Absolut & Relatif, serta Peta")
        alokasi_jp = st.number_input("Alokasi Waktu (JP):", min_value=2, max_value=36, value=4, step=2)
        tahun_ajaran = st.text_input("Tahun Pelajaran:", value="2026/2027")

    instruksi_khusus = st.text_area("Instruksi / Catatan Khusus Kepala Sekolah (Konteks Lokal):", value="Integrasikan studi kasus konteks lokal wilayah sekitar, analisis kritis, dan diskusi interaktif.")

    if st.button("🚀 Generate Modul Ajar Deep Learning"):
        st.success(f"Berhasil meng-generate Modul Ajar **{mapel}** berbasis **Deep Learning**!")
        
        # Format Teks Modul Ajar Sesuai Template Drive
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
* **Alokasi Waktu:** {alokasi_jp} JP
* **Tahun Pelajaran:** {tahun_ajaran}

### B. IDENTIFIKASI KESIAPAN PESERTA DIDIK
* **Pengetahuan Awal:** Peserta didik memiliki pemahaman dasar terkait topik {sub_materi} di lingkungan sekitar.
* **Minat:** Tertarik pada media visual/digital, diskusi kelompok, simulasi interaktif, dan analisis isu nyata.
* **Latar Belakang:** Berasal dari latar belakang sosial-ekonomi yang beragam yang memengaruhi pemahaman awal terhadap fenomena sosial/pancasila.
* **Kebutuhan Belajar:**
  - *Visual:* Gambar, peta digital, video pembelajaran, dan infografis.
  - *Auditori:* Diskusi kelompok, tanya jawab, mendengarkan paparan & kisah sejarah/sosial.
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
   Apersepsi berkesadaran di mana peserta didik diajak merefleksikan pengalaman pribadi dan menyadari pentingnya mempelajari {sub_materi}.
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
  - *Eksplorasi Konsep (Mindful Exploration):* Menelaah materi {sub_materi}.
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
            "Sub-Materi": sub_materi,
            "Alokasi JP": alokasi_jp,
            "Isi Lengkap Modul Ajar": modul_text
        }])
        
        excel_data_modul = to_excel(df_modul, sheet_name="Modul_Ajar_DeepLearning")
        st.download_button(
            label="📥 Download Modul Ajar Standar BSKAP (Excel)",
            data=excel_data_modul,
            file_name=f"Modul_Ajar_DeepLearning_{mapel}_{fase_kelas[:8]}.xlsx",
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
    st.info("💡 **Instruksi:** Klik sel pada kolom **P1–P5**, lalu pilih status: **H** (Hadir), **S** (Sakit), **I** (Izin), atau **A** (Alpa). Rekapitulasi `COUNTIF` akan dihitung otomatis.")

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
# FITUR 3: BUKU NILAI & STATUS KKTP
# ==========================================
else:
    st.header("📖 Buku Nilai Terpisah per Kelas & Keketatan KKTP")
    st.write("Buku nilai terpisah untuk **7A, 7B, Kelas 8, dan Kelas 9** agar pengelolaan nilai Formatif, Sumatif, STS, dan SAS akurat.")

    selected_kelas_nilai = st.selectbox("Pilih Kelas Buku Nilai:", daftar_kelas, key="nilai_kelas_key")

    if f"nilai_{selected_kelas_nilai}" not in st.session_state:
        st.session_state[f"nilai_{selected_kelas_nilai}"] = pd.DataFrame({
            "NIS": ["1001", "1002", "1003", "1004", "1005"],
            "Nama Siswa": [f"Ahmad Fauzi ({selected_kelas_nilai})", f"Budi Santoso ({selected_kelas_nilai})", f"Citra Dewi ({selected_kelas_nilai})", f"Dina Maria ({selected_kelas_nilai})", f"Eko Prasetyo ({selected_kelas_nilai})"],
            "Formatif 1 (LKPD)": [85, 80, 90, 70, 60],
            "Formatif 2 (Tugas)": [88, 82, 92, 75, 65],
            "Sumatif Bab 1": [80, 78, 88, 65, 55],
            "Sumatif Bab 2": [85, 80, 90, 70, 60],
            "STS (Tengah Sem)": [78, 75, 85, 68, 62],
            "SAS (Akhir Sem)": [82, 80, 88, 72, 60]
        })

    df_nilai = st.session_state[f"nilai_{selected_kelas_nilai}"]

    st.subheader(f"Input Nilai Siswa - {selected_kelas_nilai}")
    edited_nilai_df = st.data_editor(df_nilai, use_container_width=True)
    st.session_state[f"nilai_{selected_kelas_nilai}"] = edited_nilai_df

    # Kalkulasi Otomatis Nilai Rapor
    edited_nilai_df["Rata Formatif"] = edited_nilai_df[["Formatif 1 (LKPD)", "Formatif 2 (Tugas)"]].mean(axis=1)
    edited_nilai_df["Rata Sumatif Bab"] = edited_nilai_df[["Sumatif Bab 1", "Sumatif Bab 2"]].mean(axis=1)
    
    # Formula Bobot (30% Formatif + 30% Sumatif Bab + 20% STS + 20% SAS)
    edited_nilai_df["Nilai Akhir Rapor"] = (
        (edited_nilai_df["Rata Formatif"] * 0.3) +
        (edited_nilai_df["Rata Sumatif Bab"] * 0.3) +
        (edited_nilai_df["STS (Tengah Sem)"] * 0.2) +
        (edited_nilai_df["SAS (Akhir Sem)"] * 0.2)
    ).round(0)

    # Status Ketuntasan KKTP
    kktp_limit = st.slider("Batas Kriteria Ketercapaian Tujuan Pembelajaran (KKTP):", min_value=60, max_value=85, value=75)
    edited_nilai_df["Status KKTP"] = edited_nilai_df["Nilai Akhir Rapor"].apply(lambda val: "✅ TUNTAS" if val >= kktp_limit else "❌ REMEDIAL")

    st.subheader(f"🎯 Hasil Pengolahan Rapor & Status KKTP - {selected_kelas_nilai}")
    st.dataframe(edited_nilai_df[["NIS", "Nama Siswa", "Rata Formatif", "Rata Sumatif Bab", "STS (Tengah Sem)", "SAS (Akhir Sem)", "Nilai Akhir Rapor", "Status KKTP"]], use_container_width=True)

    # Tombol Download Excel
    excel_nilai = to_excel(edited_nilai_df, sheet_name=f"Nilai_{selected_kelas_nilai}")
    st.download_button(
        label=f"📥 Download Buku Nilai {selected_kelas_nilai} (Excel)",
        data=excel_nilai,
        file_name=f"Buku_Nilai_{selected_kelas_nilai}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )