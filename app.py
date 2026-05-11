import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import os
import urllib.request

# ==========================================
# 1. THIẾT LẬP GIAO DIỆN & CSS (FULL)
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
        /* Style nút tải PDF chuyên nghiệp */
        .stDownloadButton > button {
            border-radius: 6px !important;
            background-color: #007AFF !important;
            color: white !important;
            font-weight: bold !important;
            padding: 0.5rem 2rem !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Tự động tải Font hỗ trợ Tiếng Việt (Roboto)
@st.cache_resource
def load_fonts():
    f_reg = "Roboto-Regular.ttf"
    f_bold = "Roboto-Bold.ttf"
    if not os.path.exists(f_reg):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", f_reg)
    if not os.path.exists(f_bold):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", f_bold)
    return f_reg, f_bold

# ==========================================
# 2. LOGIC TOÁN HỌC & TẠO PDF (HỖ TRỢ CÓ DẤU)
# ==========================================
def calculate_stats(data):
    s = pd.Series(data)
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    return {
        "mean": np.mean(data),
        "median": np.median(data),
        "std": np.std(data),
        "var": np.var(data),
        "range": np.max(data) - np.min(data),
        "q1": q1, "q3": q3, "iqr": iqr,
        "mode": s.mode().tolist()
    }

def create_pdf_report(title, datasets_info):
    f_reg, f_bold = load_fonts()
    pdf = FPDF()
    pdf.add_page()
    
    # Đăng ký font hỗ trợ Unicode
    pdf.add_font("Roboto", "", f_reg)
    pdf.add_font("Roboto", "B", f_bold)
    
    # Header
    pdf.set_font("Roboto", "B", 16)
    pdf.set_text_color(0, 122, 255)
    pdf.cell(0, 10, "ED-ODYSSEY ANALYTICS ENGINE", ln=True, align="C")
    
    pdf.set_font("Roboto", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, title, ln=True, align="C")
    
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 8, f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    for name, stats in datasets_info.items():
        pdf.set_font("Roboto", "B", 12)
        pdf.cell(0, 8, f"--- Nhóm: {name} ---", ln=True)
        pdf.set_font("Roboto", "", 11)
        pdf.cell(0, 7, f"Trung bình (Mean): {stats['mean']:.2f}", ln=True)
        pdf.cell(0, 7, f"Trung vị (Median): {stats['median']:.2f}", ln=True)
        pdf.cell(0, 7, f"Độ lệch chuẩn: {stats['std']:.2f}", ln=True)
        pdf.cell(0, 7, f"Phương sai: {stats['var']:.2f}", ln=True)
        pdf.cell(0, 7, f"Khoảng biến thiên (IQR): {stats['iqr']:.2f}", ln=True)
        pdf.cell(0, 7, f"Điểm dị biệt (Outliers): {stats['range']:.2f}", ln=True)
        pdf.ln(5)
        
    return bytes(pdf.output())

# ==========================================
# 3. GIAO DIỆN CHÍNH (TABS & COLUMNS)
# ==========================================
st.title("📊 Statistical Insights Lab")
st.markdown("Hệ thống trực quan hóa và phân tích dữ liệu chuyên sâu.")

tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# --- TAB 1: PHÂN TÍCH ĐƠN ---
with tab1:
    col_input, col_display = st.columns([1.2, 2.8])
    
    with col_input:
        with st.container(border=True):
            uploaded_file = st.file_uploader("Tải lên file CSV:", type=["csv"], key="single_up")
            default_val = "12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12"
            raw_data = st.text_area("Nhập dãy số (cách nhau bởi dấu phẩy):", value=default_val, height=150)
            plot_choice = st.radio("Loại biểu đồ:", ["Box Plot", "Histogram"])

    with col_display:
        try:
            # Xử lý dữ liệu
            data_list = [float(x.strip()) for x in raw_data.replace("\n", ",").split(",") if x.strip()]
            if len(data_list) > 0:
                stats = calculate_stats(data_list)
                
                # Hiển thị Metrics
                with st.container(border=True):
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Trung bình", f"{stats['mean']:.2f}")
                    m2.metric("Trung vị", f"{stats['median']:.2f}")
                    m3.metric("Độ lệch chuẩn", f"{stats['std']:.2f}")
                    m4.metric("Khoảng IQR", f"{stats['iqr']:.2f}")
                
                # Biểu đồ
                df = pd.DataFrame(data_list, columns=["Value"])
                if plot_choice == "Box Plot":
                    fig = px.box(df, y="Value", points="all", title="Biểu đồ hộp & Outliers", color_discrete_sequence=["#007AFF"])
                else:
                    fig = px.histogram(df, x="Value", marginal="box", title="Phân phối tần suất", color_discrete_sequence=["#007AFF"])
                st.plotly_chart(fig, use_container_width=True)
                
                # Nút tải PDF (Có dấu)
                pdf_data = create_pdf_report("BÁO CÁO PHÂN TÍCH ĐƠN NHÓM", {"Dữ liệu nhóm": stats})
                st.download_button("📥 Tải Báo Cáo PDF (Tiếng Việt)", data=pdf_data, file_name="single_report.pdf", mime="application/pdf")
        except:
            st.error("Dữ liệu không hợp lệ. Vui lòng kiểm tra lại dấu phẩy.")

# --- TAB 2: SO SÁNH A/B ---
with tab2:
    col_in2, col_dis2 = st.columns([1.2, 2.8])
    
    with col_in2:
        with st.container(border=True):
            st.subheader("Nhóm A")
            raw_a = st.text_area("Dữ liệu A:", value="10, 12, 14, 11, 13", height=100, key="in_a")
            st.subheader("Nhóm B")
            raw_b = st.text_area("Dữ liệu B:", value="15, 18, 14, 16, 17", height=100, key="in_b")

    with col_dis2:
        try:
            da = np.array([float(x.strip()) for x in raw_a.split(",") if x.strip()])
            db = np.array([float(x.strip()) for x in raw_b.split(",") if x.strip()])
            sa, sb = calculate_stats(da), calculate_stats(db)
            
            with st.container(border=True):
                c1, c2 = st.columns(2)
                c1.metric("TB Nhóm A", f"{sa['mean']:.2f}")
                c2.metric("TB Nhóm B", f"{sb['mean']:.2f}", delta=f"{sb['mean']-sa['mean']:.2f}")
            
            df_a = pd.DataFrame({'Val': da, 'Group': 'A'})
            df_b = pd.DataFrame({'Val': db, 'Group': 'B'})
            fig_comp = px.box(pd.concat([df_a, df_b]), x='Group', y='Val', color='Group', title="So sánh phân phối A vs B")
            st.plotly_chart(fig_comp, use_container_width=True)
            
            pdf_comp = create_pdf_report("BÁO CÁO SO SÁNH A/B", {"Nhóm A": sa, "Nhóm B": sb})
            st.download_button("📥 Tải Báo Cáo So Sánh (PDF)", data=pdf_comp, file_name="compare_report.pdf", mime="application/pdf")
        except:
            st.error("Dữ liệu so sánh không hợp lệ.")

st.markdown("---")
st.caption("Trực quan hóa và hệ thống hóa bởi ED-ODYSSEY Analytics Engine.")
