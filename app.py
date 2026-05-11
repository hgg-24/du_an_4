import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import os
import urllib.request

# ==========================================
# 1. CẤU HÌNH & GIAO DIỆN (CSS)
# ==========================================
st.set_page_config(page_title="Statistical Insights Lab", page_icon="📊", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        .stApp { background-color: #F4F7FA; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem; }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #EAEAEA !important;
            padding: 1rem;
        }
        .stDownloadButton > button {
            border-radius: 6px !important;
            width: auto !important;
            padding: 0.5rem 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Tự động tải Font Roboto để hỗ trợ Tiếng Việt
@st.cache_resource
def load_fonts():
    f_reg = "Roboto-Regular.ttf"
    f_bold = "Roboto-Bold.ttf"
    if not os.path.exists(f_reg):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", f_reg)
    if not os.path.exists(f_bold):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", f_bold)
    return f_reg, f_bold

f_reg, f_bold = load_fonts()

# ==========================================
# 2. LOGIC TOÁN HỌC & PDF
# ==========================================
def calculate_stats(data):
    s = pd.Series(data)
    q1, q3 = np.percentile(data, [25, 75])
    return {
        "mean": np.mean(data),
        "median": np.median(data),
        "std": np.std(data),
        "var": np.var(data),
        "range": np.max(data) - np.min(data),
        "q1": q1, "q3": q3, "iqr": q3 - q1,
        "mode": s.mode().tolist()
    }

def create_pdf(title, datasets):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Roboto", "", f_reg)
    pdf.add_font("Roboto", "B", f_bold)
    
    pdf.set_font("Roboto", "B", 16)
    pdf.set_text_color(0, 122, 255)
    pdf.cell(0, 10, "ED-ODYSSEY ANALYTICS ENGINE", ln=True, align="C")
    
    pdf.set_font("Roboto", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, title, ln=True, align="C")
    
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 8, f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    for name, stats in datasets.items():
        pdf.set_font("Roboto", "B", 12)
        pdf.cell(0, 8, f"--- Nhóm: {name} ---", ln=True)
        pdf.set_font("Roboto", "", 11)
        pdf.cell(0, 7, f"Trung bình: {stats['mean']:.2f}", ln=True)
        pdf.cell(0, 7, f"Trung vị: {stats['median']:.2f}", ln=True)
        pdf.cell(0, 7, f"Độ lệch chuẩn: {stats['std']:.2f}", ln=True)
        pdf.cell(0, 7, f"IQR: {stats['iqr']:.2f}", ln=True)
        pdf.ln(5)
    return pdf.output()

# ==========================================
# 3. GIAO DIỆN TABS (FULL)
# ==========================================
st.title("📊 Statistical Insights Lab")
tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# --- TAB 1 ---
with tab1:
    c1, c2 = st.columns([1.2, 2.8])
    with c1:
        with st.container(border=True):
            up_1 = st.file_uploader("Tải CSV:", type=["csv"], key="up1")
            raw_1 = st.text_area("Dãy số (cách bởi dấu phẩy):", value="12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12", height=150)
            p_type = st.radio("Loại biểu đồ:", ["Box Plot", "Histogram"])

    with c2:
        try:
            data1 = np.array([float(x.strip()) for x in raw_1.split(",") if x.strip()])
            if len(data1) > 0:
                s1 = calculate_stats(data1)
                with st.container(border=True):
                    st.markdown("**Kết quả thống kê:**")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Trung bình", f"{s1['mean']:.2f}")
                    m2.metric("Trung vị", f"{s1['median']:.2f}")
                    m3.metric("IQR", f"{s1['iqr']:.2f}")
                
                fig1 = px.box(y=data1, title="Biểu đồ phân phối") if p_type=="Box Plot" else px.histogram(x=data1)
                st.plotly_chart(fig1, use_container_width=True)
                
                pdf1 = create_pdf("BÁO CÁO ĐƠN NHÓM", {"Dữ liệu": s1})
                st.download_button("📥 Tải Báo Cáo PDF", data=bytes(pdf1), file_name="single_report.pdf", mime="application/pdf", type="primary")
        except: st.error("Lỗi định dạng dữ liệu.")

# --- TAB 2 ---
with tab2:
    c21, c22 = st.columns([1.2, 2.8])
    with c21:
        with st.container(border=True):
            raw_a = st.text_area("Dữ liệu Nhóm A:", value="10, 12, 14, 15", height=100)
            raw_b = st.text_area("Dữ liệu Nhóm B:", value="11, 13, 16, 18", height=100)

    with c22:
        try:
            da = np.array([float(x.strip()) for x in raw_a.split(",") if x.strip()])
            db = np.array([float(x.strip()) for x in raw_b.split(",") if x.strip()])
            sa, sb = calculate_stats(da), calculate_stats(db)
            
            with st.container(border=True):
                m_a, m_b = st.columns(2)
                m_a.metric("TB Nhóm A", f"{sa['mean']:.2f}")
                m_b.metric("TB Nhóm B", f"{sb['mean']:.2f}", delta=f"{sb['mean']-sa['mean']:.2f}")
            
            df_comp = pd.concat([pd.DataFrame({'Val': da, 'Gr': 'A'}), pd.DataFrame({'Val': db, 'Gr': 'B'})])
            st.plotly_chart(px.box(df_comp, x='Gr', y='Val', color='Gr', title="So sánh nhóm"), use_container_width=True)
            
            pdf2 = create_pdf("BÁO CÁO SO SÁNH", {"Nhóm A": sa, "Nhóm B": sb})
            st.download_button("📥 Tải Báo Cáo So Sánh (PDF)", data=bytes(pdf2), file_name="compare_report.pdf", mime="application/pdf", type="primary")
        except: st.error("Dữ liệu nhóm không hợp lệ.")

st.markdown("---")
st.caption("ED-ODYSSEY Analytics Engine - Hệ thống phân tích chuyên sâu.")
