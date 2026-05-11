import streamlit as st

# Konfigurasi Halaman
st.set_page_config(page_title="Fraud Detector & Due Diligence", layout="wide", initial_sidebar_state="collapsed")

st.title("🔍 Alat Analisis Beneish M-Score & Audit Lapangan")
st.markdown("Masukkan data keuangan untuk menghitung risiko manipulasi laba dan dapatkan daftar pertanyaan verifikasi otomatis.")

# --- MAIN CONTENT: INPUT DATA (SIDE-BY-SIDE) ---
with st.form("input_form"):
    st.subheader("📝 Entri Data Keuangan")
    st.markdown("*Masukkan data dalam satuan yang sama (misal: Jutaan).*")
    
    col_t, col_t1 = st.columns(2)
    
    with col_t:
        st.markdown("### 📅 Tahun Berjalan (t)")
        rev_t = st.number_input("Revenue (t)", value=304367.0, step=1000.0)
        rec_t = st.number_input("Account Receivables (t)", value=14292.0, step=1000.0)
        cogs_t = st.number_input("COGS (t)", value=191849.0, step=1000.0)
        ca_t = st.number_input("Current Assets (t)", value=53554.0, step=1000.0)
        ta_t = st.number_input("Total Assets (t)", value=377884.0, step=1000.0)
        dep_t = st.number_input("Depreciation (t)", value=31090.0, step=1000.0)
        sga_t = st.number_input("Selling Generale Admin Expense (t)", value=69046.0, step=1000.0)
        debt_t = st.number_input("Total Debt (t)", value=182348.0, step=1000.0)
        ni_t = st.number_input("Net Income (t)", value=294325.0, step=1000.0)
        cfo_t = st.number_input("Cash Flow from Ops (t)", value=74526.0, step=1000.0)

    with col_t1:
        st.markdown("### ⏪ Tahun Sebelumnya (t-1)")
        rev_t1 = st.number_input("Revenue (t-1)", value=267169.0, step=1000.0)
        rec_t1 = st.number_input("Account Receivables (t-1)", value=10944.0, step=1000.0)
        cogs_t1 = st.number_input("COGS (t-1)", value=159445.0, step=1000.0)
        ca_t1 = st.number_input("Current Assets (t-1)", value=103549.0, step=1000.0)
        ta_t1 = st.number_input("Total Assets (t-1)", value=351819.0, step=1000.0)
        dep_t1 = st.number_input("Depreciation (t-1)", value=25197.0, step=1000.0)
        sga_t1 = st.number_input("Selling Generale Admin Expense (t-1)", value=61591.0, step=1000.0)
        debt_t1 = st.number_input("Total Debt (t-1)", value=159334.0, step=1000.0)
        st.markdown("<br><br><br>", unsafe_allow_html=True) # Spacer agar tombol sejajar
        
    submitted = st.form_submit_button("Jalankan Analisis", use_container_width=True)

# --- MAIN CONTENT: KALKULASI & HASIL ---
if submitted:
    # --- 1. PERHITUNGAN INDEKS ---
    try:
        dsri = (rec_t / rev_t) / (rec_t1 / rev_t1)
    except ZeroDivisionError: dsri = 1.0
    
    try:
        gmi = ((rev_t1 - cogs_t1) / rev_t1) / ((rev_t - cogs_t) / rev_t)
    except ZeroDivisionError: gmi = 1.0
    
    try:
        aqi = (1 - ca_t / ta_t) / (1 - ca_t1 / ta_t1)
    except ZeroDivisionError: aqi = 1.0
    
    try:
        sgi = rev_t / rev_t1
    except ZeroDivisionError: sgi = 1.0
    
    try:
        depi = (dep_t1 / (dep_t1 + ta_t1)) / (dep_t / (dep_t + ta_t))
    except ZeroDivisionError: depi = 1.0
    
    try:
        sgai = (sga_t / rev_t) / (sga_t1 / rev_t1)
    except ZeroDivisionError: sgai = 1.0
    
    try:
        lvgi = (debt_t / ta_t) / (debt_t1 / ta_t1)
    except ZeroDivisionError: lvgi = 1.0
    
    try:
        tata = (ni_t - cfo_t) / ta_t
    except ZeroDivisionError: tata = 0.0

    # Perhitungan M-Score 8 Variabel
    m_score = -4.84 + (0.92 * dsri) + (0.528 * gmi) + (0.404 * aqi) + (0.892 * sgi) + (0.115 * depi) - (0.172 * sgai) + (4.679 * tata) - (0.327 * lvgi)

    # --- 2. TAMPILAN HASIL UTAMA ---
    st.divider()
    col_score, col_status = st.columns([1, 2])
    
    with col_score:
        st.metric(label="Beneish M-Score Final", value=f"{m_score:.3f}")
        
    with col_status:
        if m_score > -2.22:
            st.error("🚨 **STATUS MERAH:** Kemungkinan Besar Terjadi Manipulasi Laba (Likely Manipulator). Diperlukan investigasi mendalam.")
        else:
            st.success("✅ **STATUS HIJAU:** Tidak Ditemukan Indikasi Kuat Manipulasi Laba (Non-Manipulator).")

    # --- 3. RINCIAN 8 KOMPONEN INDEKS ---
    st.subheader("📊 Rincian 8 Komponen Indeks")
    st.markdown("*(Indeks dengan tanda **⚠️ Bahaya/Tinggi** merupakan penyumbang utama risiko manipulasi).*")
    
    # Baris Pertama (4 Indeks)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DSRI (Piutang)", f"{dsri:.2f}", delta="⚠️ Bahaya" if dsri > 1.03 else "Aman", delta_color="inverse")
    c2.metric("GMI (Margin Kotor)", f"{gmi:.2f}", delta="⚠️ Bahaya" if gmi > 1.01 else "Aman", delta_color="inverse")
    c3.metric("AQI (Kualitas Aset)", f"{aqi:.2f}", delta="⚠️ Bahaya" if aqi > 1.03 else "Aman", delta_color="inverse")
    c4.metric("SGI (Pertumbuhan)", f"{sgi:.2f}", delta="⚠️ Tinggi" if sgi > 1.20 else "Normal", delta_color="inverse")
    
    # Baris Kedua (4 Indeks)
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("DEPI (Depresiasi)", f"{depi:.2f}", delta="⚠️ Bahaya" if depi > 1.05 else "Aman", delta_color="inverse")
    c6.metric("SGAI (Biaya Admin)", f"{sgai:.2f}", delta="⚠️ Bahaya" if sgai > 1.10 else "Aman", delta_color="inverse")
    c7.metric("LVGI (Leverage/Utang)", f"{lvgi:.2f}", delta="⚠️ Bahaya" if lvgi > 1.05 else "Aman", delta_color="inverse")
    c8.metric("TATA (Akrual)", f"{tata:.3f}", delta="⚠️ Bahaya" if tata > 0.10 else "Aman", delta_color="inverse")
    
    # --- 4. DYNAMIC DUE DILIGENCE CHECKLIST ---
    st.divider()
    st.header("📋 Daftar Pertanyaan Verifikasi (Due Diligence Lapangan)")
    st.markdown("Berdasarkan hasil analisis 8 indeks di atas, fokuskan pertanyaan pada area berikut:")
    
    if dsri > 1.03:
        st.warning("**Sinyal DSRI Tinggi (Pertumbuhan Piutang > Pertumbuhan Penjualan)**")
        st.write("- Minta ditunjukkan **Aging Schedule** (Daftar Umur Piutang) terbaru.")
        st.write("- Mengapa terjadi kelonggaran kredit? Apakah ada perubahan kebijakan penagihan?")
        st.write("- Tunjukkan bukti penerimaan kas (rekening koran) untuk pelunasan piutang bulan lalu.")
        
    if tata > 0.10:
        st.warning("**Sinyal TATA Tinggi (Laba Bersih jauh melampaui Kas Operasional)**")
        st.write("- Minta penjelasan rinci mengenai komponen laba yang bukan berupa kas (akrual).")
        st.write("- Apakah ada pengakuan pendapatan yang layanannya belum selesai (Percentage of Completion)? Tunjukkan BAST.")
        
    if gmi > 1.01:
        st.warning("**Sinyal GMI Tinggi (Margin Kotor Memburuk)**")
        st.write("- Tunjukkan rincian Harga Pokok Penjualan (COGS). Mengapa margin keuntungan menipis?")
        
    if sgi > 1.20:
        st.warning("**Sinyal SGI Tinggi (Pertumbuhan Penjualan Sangat Cepat)**")
        st.write("- Apakah pertumbuhan omzet ini riil dari operasional, atau dari transaksi afiliasi?")

    if aqi > 1.03:
         st.warning("**Sinyal AQI Tinggi (Kualitas Aset Menurun)**")
         st.write("- Minta rincian Aset Tidak Berwujud. Apakah ada beban operasi yang sengaja diubah (dikapitalisasi) menjadi aset agar laba tidak turun?")

    if depi > 1.05:
         st.warning("**Sinyal DEPI Tinggi (Laju Depresiasi Melambat)**")
         st.write("- Apakah perusahaan baru saja merubah estimasi umur manfaat aset tetap menjadi lebih lama? (Ini taktik umum untuk mengecilkan beban penyusutan dan membesarkan laba).")

    if sgai > 1.10:
         st.warning("**Sinyal SGAI Tinggi (Biaya Operasional Melonjak)**")
         st.write("- Mengapa biaya Penjualan, Umum, dan Admin (SGA) tumbuh lebih cepat dibandingkan penjualan itu sendiri? Adakah pengeluaran tidak wajar?")

    if lvgi > 1.05:
         st.warning("**Sinyal LVGI Tinggi (Rasio Utang Meningkat)**")
         st.write("- Perusahaan mengambil lebih banyak utang. Apakah ini karena perusahaan kesulitan menghasilkan arus kas organik untuk membiayai operasinya?")

    if m_score <= -2.22 and max([dsri, gmi, aqi, depi, sgai, lvgi]) <= 1.05 and tata <= 0.10:
        st.info("Semua 8 parameter terlihat dalam batas wajar. Lakukan prosedur *due diligence* standar sesuai SOP perusahaan keuangan Anda.")
        
    st.markdown("---")
    st.caption("Dikembangkan untuk efisiensi Field Audit Financial Analyst. Jangan gunakan alat ini sebagai satu-satunya dasar pengambilan keputusan kredit.")
