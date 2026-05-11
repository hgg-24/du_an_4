import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import os
import urllib.request
import io

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & STYLE (CSS)
# ==========================================
st.set_page_config(page_title="Statistical Insights Lab", page_icon="📊", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        .stApp { background-color: #F4F7FA; }
        
        /* Metric Styling */
        div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #007AFF; font-weight: bold; }
        
        /* Container Styling */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #EAEAEA !important;
            padding: 1.5rem !important;
            margin-bottom: 1rem;
        }
        
        /* Download Button Styling */
        .stDownloadButton > button {
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Tự động tải font Roboto hỗ trợ Tiếng Việt (Unicode)
@st.cache_resource
def load_fonts():
    reg = "Roboto-Regular.ttf"
    bold = "Roboto-Bold.ttf"
    if not os.path.exists(reg):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", reg)
    if not os.path.exists(bold):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", bold)
    return reg, bold

# ==========================================
# 2. HÀM TÍNH TOÁN & XUẤT FILE
# ==========================================
def calculate_stats(data):
    if len(data) == 0: return None
    s = pd.Series(data)
    q1, q3 = np.percentile(data, [25, 75])
    stats = {
        "Chỉ số": ["Trung bình", "Trung vị", "Độ lệch chuẩn", "Phương sai", "Khoảng biến thiên", "Q1", "Q3", "IQR"],
        "Giá trị": [
            np.mean(data), np.median(data), np.std(data), np.var(data), 
            np.max(data) - np.min(data), q1, q3, q3 - q1
        ]
    }
    return pd.DataFrame(stats), s.mode().tolist()

def create_pdf(title, df_stats, modes):
    reg, bold = load_fonts()
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Roboto", "", reg)
    pdf.add_font("Roboto", "B", bold)
    
    # Header
    pdf.set_font("Roboto", "B", 18)
    pdf.set_text_color(0, 122, 255)
    pdf.cell(0, 15, "ED-ODYSSEY ANALYTICS REPORT", ln=True, align="C")
    
    pdf.set_font("Roboto", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 8, f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    
    # Table Data
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 10, "1. Kết quả thống kê chi tiết:", ln=True)
    pdf.set_font("Roboto", "", 11)
    for i, row in df_stats.iterrows():
        pdf.cell(60, 8, f"• {row['Chỉ số']}:", border=0)
        pdf.cell(40, 8, f"{row['Giá trị']:.2f}", border=0, ln=True)
    
    pdf.cell(60, 8, f"• Yếu vị (Mode):", border=0)
    pdf.cell(40, 8, f"{', '.join(map(str, modes))}", border=0, ln=True)
    
    return bytes(pdf.output())

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
st.title("📊 Statistical Insights Lab")
tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# --- TAB 1: PHÂN TÍCH ĐƠN ---
with tab1:
    col_in, col_out = st.columns([1.2, 2.8])
    with col_in:
        with st.container(border=True):
            st.markdown("### 📥 Nhập dữ liệu")
            raw_input = st.text_area("Dãy số (cách nhau bởi dấu phẩy):", 
                                     value="12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12", height=150)
            plot_choice = st.radio("Loại biểu đồ:", ["Box Plot", "Histogram"])

    with col_out:
        try:
            nums = np.array([float(x.strip()) for x in raw_input.replace("\n", ",").split(",") if x.strip()])
            if len(nums) > 0:
                df_res, modes = calculate_stats(nums)
                
                # Metrics Area
                with st.container(border=True):
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Trung bình", f"{df_res.iloc[0,1]:.2f}")
                    m2.metric("Trung vị", f"{df_res.iloc[1,1]:.2f}")
                    m3.metric("Độ lệch chuẩn", f"{df_res.iloc[2,1]:.2f}")
                    m4.metric("Khoảng IQR", f"{df_res.iloc[7,1]:.2f}")
                
                # Chart Area
                df_p = pd.DataFrame(nums, columns=["Giá trị"])
                fig = px.box(df_p, y="Giá trị", points="all", title="Biểu đồ phân phối") if plot_choice == "Box Plot" else px.histogram(df_p, x="Giá trị", title="Biểu đồ tần suất")
                st.plotly_chart(fig, use_container_width=True)
                
                # DOWNLOAD AREA
                st.markdown("### 💾 Xuất dữ liệu")
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    pdf_data = create_pdf("BÁO CÁO PHÂN TÍCH ĐƠN NHÓM", df_res, modes)
                    st.download_button("📥 Tải Báo Cáo PDF (Có dấu)", data=pdf_data, 
                                       file_name="report_single.pdf", mime="application/pdf", type="primary")
                
                with btn_col2:
                    csv = df_res.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📊 Tải Kết Quả CSV (Excel)", data=csv, 
                                       file_name="data_results.csv", mime="text/csv")
        except: st.error("Dữ liệu không hợp lệ.")

# --- TAB 2: SO SÁNH A/B ---
with tab2:
    col_in2, col_out2 = st.columns([1.2, 2.8])
    with col_in2:
        with st.container(border=True):
            st.markdown("### ⚖️ Nhập liệu")
            raw_a = st.text_area("Nhóm A:", value="10, 12, 14, 11, 13", height=100)
            raw_b = st.text_area("Nhóm B:", value="15, 18, 14, 16, 17", height=100)

    with col_out2:
        try:
            da = np.array([float(x.strip()) for x in raw_a.split(",") if x.strip()])
            db = np.array([float(x.strip()) for x in raw_b.split(",") if x.strip()])
            if len(da) > 0 and len(db) > 0:
                df_a, ma = calculate_stats(da)
                df_b, mb = calculate_stats(db)
                
                # Metrics Compare
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("TB Nhóm A", f"{df_a.iloc[0,1]:.2f}")
                    c2.metric("TB Nhóm B", f"{df_b.iloc[0,1]:.2f}", delta=f"{df_b.iloc[0,1]-df_a.iloc[0,1]:.2f}")
                
                # Boxplot Compare
                df_comp = pd.concat([pd.DataFrame({'Giá trị': da, 'Nhóm': 'A'}), pd.DataFrame({'Giá trị': db, 'Nhóm': 'B'})])
                st.plotly_chart(px.box(df_comp, x='Nhóm', y='Giá trị', color='Nhóm', title="So sánh A vs B"), use_container_width=True)
                
                # Download Button for Tab 2
                pdf_comp = create_pdf("BÁO CÁO SO SÁNH A/B", df_a, ma) # Demo cho nhóm A
                st.download_button("📥 Tải Báo Cáo So Sánh PDF", data=pdf_comp, file_name="comparison_report.pdf", type="primary")
        except: st.error("Dữ liệu lỗi.")

st.markdown("---")
st.caption("Trực quan hóa bởi ED-ODYSSEY Analytics Engine.")
