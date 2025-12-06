import streamlit as st
import pandas as pd
import joblib
from database import save_to_db

# ==========================================
# 1. SETUP & UTILS
# ==========================================
st.set_page_config(page_title="Prediksi Churn Telco", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# CSS Styling (Sama seperti sebelumnya)
st.markdown("""
<style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .stButton>button { width: 100%; background-color: #FF4B4B; color: white; height: 3em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# LOAD MODEL
@st.cache_resource
def load_model():
    try:
        model = joblib.load('models/model_churn_rf.pkl')
        cols = joblib.load('models/model_columns.pkl')
        return model, cols
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None

model, model_columns = load_model()

# ==========================================
# 2. KAMUS PENERJEMAH (MAPPING)
# ==========================================
# Kiri: Tampilan di Layar (Indo) | Kanan: Data untuk AI/DB (Inggris)

map_gender = {'Laki-laki': 'Male', 'Perempuan': 'Female'}
map_yes_no = {'Ya': 'Yes', 'Tidak': 'No'}
map_internet = {'DSL': 'DSL', 'Fiber Optic': 'Fiber optic', 'Tidak Langganan': 'No'}
map_contract = {'Bulanan': 'Month-to-month', '1 Tahun': 'One year', '2 Tahun': 'Two year'}
map_payment = {
    'Cek Elektronik': 'Electronic check',
    'Cek Pos': 'Mailed check',
    'Transfer Bank (Otomatis)': 'Bank transfer (automatic)',
    'Kartu Kredit (Otomatis)': 'Credit card (automatic)'
}
map_service = {'Tidak Ada Layanan Internet': 'No internet service', 'Tidak': 'No', 'Ya': 'Yes'}
map_lines = {'Tidak Ada Layanan Telepon': 'No phone service', 'Tidak': 'No', 'Ya': 'Yes'}

# ==========================================
# 3. UI DASHBOARD
# ==========================================
col_logo, col_text = st.columns([1, 4])
with col_logo:
    st.markdown("# 🇮🇩") 
with col_text:
    st.markdown('<p class="big-font">Prediksi Pelanggan Telco (Churn)</p>', unsafe_allow_html=True)
    st.write("Aplikasi prediksi loyalitas pelanggan berbasis AI.")

st.markdown("---")

with st.form("churn_form"):
    
    tab1, tab2, tab3 = st.tabs(["👤 Data Diri", "🌐 Layanan", "💳 Pembayaran"])
    
    # --- TAB 1: DATA DIRI ---
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            # UI menampilkan 'Laki-laki', tapi variabel menyimpan 'Laki-laki'
            gender_ui = st.selectbox('Jenis Kelamin', list(map_gender.keys())) 
            partner_ui = st.selectbox('Punya Pasangan?', list(map_yes_no.keys()))
            dependents_ui = st.selectbox('Punya Tanggungan?', list(map_yes_no.keys()))
        with c2:
            phone_ui = st.selectbox('Layanan Telepon', list(map_yes_no.keys()))
            multiple_lines_ui = st.selectbox('Multiple Lines', list(map_lines.keys()))
            
    # --- TAB 2: LAYANAN ---
    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            internet_ui = st.selectbox('Jenis Internet', list(map_internet.keys()))
            online_sec_ui = st.selectbox('Keamanan Online', list(map_service.keys()))
        with c2:
            backup_ui = st.selectbox('Backup Online', list(map_service.keys()))
            device_prot_ui = st.selectbox('Proteksi Perangkat', list(map_service.keys()))
        with c3:
            tech_supp_ui = st.selectbox('Tech Support', list(map_service.keys()))
            tv_ui = st.selectbox('Streaming TV', list(map_service.keys()))
            movies_ui = st.selectbox('Streaming Movies', list(map_service.keys()))

    # --- TAB 3: PEMBAYARAN ---
    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            contract_ui = st.selectbox('Tipe Kontrak', list(map_contract.keys()))
            paperless_ui = st.selectbox('Tagihan Paperless', list(map_yes_no.keys()))
            payment_ui = st.selectbox('Metode Pembayaran', list(map_payment.keys()))
        with c2:
            tenure = st.slider('Lama Berlangganan (Bulan)', 0, 72, 12)
            monthly_charges = st.number_input('Tagihan Bulanan ($)', min_value=0.0, value=50.0)
            total_charges = st.number_input('Total Tagihan ($)', min_value=0.0, value=500.0)

    st.markdown("###")
    submitted = st.form_submit_button("🔍 ANALISA RISIKO")

# ==========================================
# 4. PROSES TERJEMAHAN & PREDIKSI
# ==========================================
if submitted:
    # --- TAHAP PENTING: Menerjemahkan input Indo -> Inggris ---
    data_english = {
        'tenure': tenure,
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges,
        'Gender': map_gender[gender_ui],          # Mengambil value Inggris dari key Indo
        'Partner': map_yes_no[partner_ui],
        'Dependents': map_yes_no[dependents_ui],
        'PhoneService': map_yes_no[phone_ui],
        'MultipleLines': map_lines[multiple_lines_ui],
        'InternetService': map_internet[internet_ui],
        'OnlineSecurity': map_service[online_sec_ui],
        'OnlineBackup': map_service[backup_ui],
        'DeviceProtection': map_service[device_prot_ui],
        'TechSupport': map_service[tech_supp_ui],
        'StreamingTV': map_service[tv_ui],
        'StreamingMovies': map_service[movies_ui],
        'Contract': map_contract[contract_ui],
        'PaperlessBilling': map_yes_no[paperless_ui],
        'PaymentMethod': map_payment[payment_ui]
    }
    
    # Buat DataFrame dengan data Bahasa Inggris
    input_df = pd.DataFrame(data_english, index=[0])

    # --- PROSES AI (Sama seperti sebelumnya) ---
    if model and model_columns is not None:
        input_encoded = pd.get_dummies(input_df)
        input_final = input_encoded.reindex(columns=model_columns, fill_value=0)
        
        prediction = model.predict(input_final)
        prediction_proba = model.predict_proba(input_final)
        prob_churn = prediction_proba[0][1] * 100
        
        # Output Text untuk User (Bisa Bahasa Indonesia)
        hasil_text = "Berhenti (Churn)" if prediction[0] == 1 else "Setia (No Churn)"
        
        st.markdown("---")
        res_col1, res_col2 = st.columns([1, 2])
        
        with res_col1:
            if prediction[0] == 1:
                st.error("### ⚠️ BERISIKO TINGGI")
            else:
                st.success("### ✅ PELANGGAN AMAN")
            st.metric("Probabilitas Churn", f"{prob_churn:.1f}%")
            
        with res_col2:
            st.write("Interpretasi:")
            st.progress(int(prob_churn))
            if prob_churn > 70:
                st.warning("Sangat mungkin pindah operator. Tawarkan diskon segera!")
            elif prob_churn > 40:
                st.info("Cukup berisiko. Perlu perhatian.")
            else:
                st.write("Pelanggan terlihat nyaman dengan layanan saat ini.")

        # --- SIMPAN KE DATABASE ---
        # Kita simpan data "English" agar database tetap standar dan rapi
        try:
            save_to_db(
                tenure=int(tenure),
                monthly=float(monthly_charges),
                total=float(total_charges),
                gender=data_english['Gender'],      # Simpan 'Male/Female' bukan 'Laki-laki'
                contract=data_english['Contract'],  # Simpan 'Month-to-month'
                pred_result=hasil_text,
                pred_proba=float(prob_churn)
            )
            st.toast("✅ Data tersimpan!", icon="💾")
        except Exception as e:
            st.error(f"Gagal simpan database: {e}")