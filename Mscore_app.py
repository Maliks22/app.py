import streamlit as st

# Konfigurasi Halaman
st.set_page_config(page_title="Fraud Detector & Due Diligence", layout="wide", initial_sidebar_state="expanded")

st.title("🔍 Alat Analisis Beneish M-Score & Audit Lapangan")
st.markdown("Masukkan data keuangan untuk menghitung risiko manipulasi laba dan dapatkan daftar pertanyaan verifikasi otomatis.")

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("📝 Entri Data Keuangan")
st.sidebar.markdown("*Masukkan data dalam satuan yang sama (misal: Jutaan).*")

with st.sidebar.form("input_form"):
    st.subheader("Data Tahun Berjalan (t)")
    rev_t = st.number_input("Revenue (t)", value=304367.0)
    rec_t = st.number_input("Account Receivables (t)", value=14292.0)
    cogs_t = st.number_input("COGS (t)", value=191849.0)
    ca_t = st.number_input("Current Assets (t)", value=53554.0)
    ta_t = st.number_input("Total Assets (t)", value=377884.0)
    dep_t = st.number_input("Depreciation (t)", value=31090.0)
    sga_t = st.number_input("Selling Generale Admin Expense (t)", value=69046.0)
    debt_t = st.number_input("Total Debt (t)", value=182348.0)
    ni_t = st.number_input("Net Income (t)", value=294325.0)
    cfo_t = st.number_input("Cash Flow from Ops (t)", value=74526.0)

    st.subheader("Data Tahun Sebelumnya (t-1)")
    rev_t1 = st.number_input("Revenue (t-1)", value=267169.0)
    rec_t1 = st.number_input("Account Receivables (t-1)", value=10944.0)
    cogs_t1 = st.number_input("COGS (t-1)", value=159445.0)
    ca_t1 = st.number_input("Current Assets (t-1)", value=103549.0)
    ta_t1 = st.number_input("Total Assets (t-1)", value=351819.0)
    dep_t1 = st.number_input("Depreciation (t-1)", value=25197.0)
    sga_t1 = st.number_input("Selling Generale Admin Expense (t-1)", value=61591.0)
    debt_t1 = st.number_input("Total Debt (t-1)", value=159334.0)
    
    submitted = st.form_submit_button("Jalankan Analisis")

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
        st.metric(label="Beneish M-Score", value=f"{m_score:.3f}")
        
    with col_status:
        if m_score > -2.22:
            st.error("🚨 **STATUS MERAH:** Kemungkinan Besar Terjadi Manipulasi Laba (Likely Manipulator). Diperlukan investigasi mendalam.")
        else:
            st.success("✅ **STATUS HIJAU:** Tidak Ditemukan Indikasi Kuat Manipulasi Laba (Non-Manipulator).")

    # --- 3. RINCIAN INDEKS ---
    st.subheader("📊 Rincian Komponen Indeks")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DSRI (Piutang)", f"{dsri:.2f}", delta="⚠️ Bahaya" if dsri > 1.03 else "Aman", delta_color="inverse")
    c2.metric("GMI (Margin Kotor)", f"{gmi:.2f}", delta="⚠️ Bahaya" if gmi > 1.01 else "Aman", delta_color="inverse")
    c3.metric("TATA (Akrual)", f"{tata:.2f}", delta="⚠️ Bahaya" if tata > 0.10 else "Aman", delta_color="inverse")
    c4.metric("SGI (Pertumbuhan)", f"{sgi:.2f}", delta="⚠️ Tinggi" if sgi > 1.20 else "Normal", delta_color="inverse")
    
    st.markdown("*(Indeks yang ditandai **Bahaya** merupakan pemicu utama skor M-Score yang memburuk).*")
    
    # --- 4. DYNAMIC DUE DILIGENCE CHECKLIST ---
    st.divider()
    st.header("📋 Daftar Pertanyaan Verifikasi (Due Diligence Lapangan)")
    st.markdown("Berdasarkan hasil analisis di atas, tanyakan hal-hal berikut kepada pihak manajemen:")
    
    questions = []
    
    if dsri > 1.03:
        st.warning("**Sinyal DSRI Tinggi (Pertumbuhan Piutang > Pertumbuhan Penjualan)**")
        st.write("- Minta ditunjukkan **Aging Schedule** (Daftar Umur Piutang) terbaru.")
        st.write("- Mengapa terjadi kelonggaran kredit? Apakah ada perubahan kebijakan penagihan?")
        st.write("- Siapa saja Top 5 klien dengan piutang terbesar? Apakah ada hubungan istimewa (afiliasi) dengan mereka?")
        st.write("- Tunjukkan bukti penerimaan kas (rekening koran) untuk pelunasan piutang bulan lalu.")
        
    if tata > 0.10:
        st.warning("**Sinyal TATA Tinggi (Laba Bersih jauh melampaui Kas Operasional)**")
        st.write("- Minta penjelasan rinci mengenai komponen laba yang bukan berupa kas (akrual).")
        st.write("- Apakah ada pengakuan pendapatan *Percentage of Completion* (jasa belum selesai tapi sudah dicatat)? Tunjukkan BAST (Berita Acara Serah Terima)-nya.")
        st.write("- Bagaimana strategi riil manajemen untuk mengonversi laba bersih tahun ini menjadi kas nyata di bank?")
        
    if gmi > 1.01:
        st.warning("**Sinyal GMI Tinggi (Margin Kotor Memburuk)**")
        st.write("- Tunjukkan rincian Harga Pokok Penjualan (COGS). Biaya bahan/jasa apa yang naiknya paling signifikan?")
        st.write("- Apakah perusahaan memberikan diskon besar-besaran untuk mendongkrak volume penjualan akhir tahun?")
        
    if sgi > 1.20:
        st.warning("**Sinyal SGI Tinggi (Pertumbuhan Penjualan Sangat Cepat)**")
        st.write("- Apakah pertumbuhan omzet ini organik, atau hasil akuisisi?")
        st.write("- Apakah ada tekanan target dari direksi pusat terkait bonus kinerja tahunan yang memicu percepatan pengakuan omzet?")

    if aqi > 1.03:
         st.warning("**Sinyal AQI Tinggi (Kualitas Aset Menurun)**")
         st.write("- Minta rincian Aset Tidak Berwujud dan Biaya Dibayar Dimuka. Apakah ada beban yang sengaja dikapitalisasi menjadi aset?")

    if m_score <= -2.22 and dsri <= 1.03 and tata <= 0.10:
        st.info("Semua parameter terlihat dalam batas normal. Lakukan prosedur *due diligence* standar sesuai SOP perusahaan keuangan Anda.")
        
    st.markdown("---")
    st.caption("Dikembangkan untuk efisiensi Field Audit Financial Analyst. Jangan gunakan alat ini sebagai satu-satunya dasar pengambilan keputusan kredit.")

else:
    st.info("Silakan masukkan data pada panel di sebelah kiri dan klik **Jalankan Analisis**.")
