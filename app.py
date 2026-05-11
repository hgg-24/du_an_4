import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import os
import urllib.request

# ==========================================
# 1. THIẾT LẬP TRANG & GIAO DIỆN CƠ BẢN (CSS)
# ==========================================
st.set_page_config(page_title="Statistical Insights Lab", page_icon="📊", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        .stApp { background-color: #F4F7FA; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem; }
        div[data-testid="stMetricDelta"] { font-size: 1rem; }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #EAEAEA !important;
            padding: 0.5rem;
        }
        /* Nút tải PDF nhỏ gọn */
        .stDownloadButton > button {
            border-radius: 6px !important;
            transition: all 0.3s ease;
            width: auto !important;
            padding: 0.5rem 1.5rem !important;
        }
        .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. HÀM TOÁN HỌC & XUẤT PDF UNICODE
# ==========================================
def calculate_stats(data_array):
    q1 = np.percentile(data_array, 25)
    q3 = np.percentile(data_array, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = data_array[(data_array < lower_bound) | (data_array > upper_bound)]
    
    data_range = np.max(data_array) - np.min(data_array)
    std_dev = np.std(data_array)
    s = pd.Series(data_array)
    mode_val = s.mode().tolist()
    
    return {
        "mean": np.mean(data_array),
        "median": np.median(data_array),
        "var": np.var(data_array),
        "std": std_dev,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "range": data_range,
        "mode": mode_val,
        "outliers": outliers.tolist()
    }

def download_font_if_not_exists(font_name, url):
    if not os.path.exists(font_name):
        try:
            urllib.request.urlretrieve(url, font_name)
        except:
            return False
    return True

def create_pdf_report(title, datasets_info):
    pdf = FPDF()
    pdf.add_page()
    
    # --- TỰ ĐỘNG TẢI FONT TIẾNG VIỆT (ROBOTO) ---
    font_regular_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
    font_bold_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
    font_italic_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Italic.ttf"
    
    font_regular = "Roboto-Regular.ttf"
    font_bold = "Roboto-Bold.ttf"
    font_italic = "Roboto-Italic.ttf"
    
    # Nhúng font vào PDF
    if download_font_if_not_exists(font_regular, font_regular_url):
        pdf.add_font("Roboto", "", font_regular)
    if download_font_if_not_exists(font_bold, font_bold_url):
        pdf.add_font("Roboto", "B", font_bold)
    if download_font_if_not_exists(font_italic, font_italic_url):
        pdf.add_font("Roboto", "I", font_italic)
    
    # Sử dụng font đã nhúng (nếu không tải được sẽ lùi về Arial mặc định)
    active_font = "Roboto" if os.path.exists(font_regular) else "Arial"

    # --- HEADER BRANDING ---
    pdf.set_font(active_font, "B", 16)
    pdf.set_text_color(0, 122, 255) # Màu xanh thương hiệu
    pdf.cell(0, 10, txt="ED-ODYSSEY ANALYTICS ENGINE", ln=True, align="C")
    
    pdf.set_font(active_font, "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=title, ln=True, align="C")
    
    pdf.set_font(active_font, "I", 10)
    pdf.set_text_color(128, 128, 128)
    current_time = datetime.now().strftime("%d/%m/%Y - %H:%M")
    pdf.cell(0, 8, txt=f"Ngày xuất báo cáo: {current_time}", ln=True, align="C")
    
    pdf.line(10, 42, 200, 42) 
    pdf.ln(10)
    
    # --- NỘI DUNG THỐNG KÊ (HỖ TRỢ CÓ DẤU) ---
    pdf.set_text_color(0, 0, 0)
    for data_name, stats in datasets_info.items():
        pdf.set_font(active_font, "B", 12)
        pdf.cell(0, 8, txt=f"--- Nhóm dữ liệu: {data_name} ---", ln=True)
        pdf.set_font(active_font, "", 11)
        
        mode_str = ", ".join(map(lambda x: f"{x:g}", stats['mode']))
        outliers_str = str(stats['outliers']) if stats['outliers'] else "Không có"
        
        pdf.cell(0, 7, txt=f"Trung bình (Mean): {stats['mean']:.2f}", ln=True)
        pdf.cell(0, 7, txt=f"Trung vị (Median): {stats['median']:.2f}", ln=True)
        pdf.cell(0, 7, txt=f"Yếu vị (Mode): {mode_str}", ln=True)
        pdf.cell(0, 7, txt=f"Phương sai (Variance): {stats['var']:.2f}", ln=True)
        pdf.cell(0, 7, txt=f"Độ lệch chuẩn (Std Dev): {stats['std']:.2f}", ln=True)
        pdf.cell(0, 7, txt=f"Khoảng giá trị (Range): {stats['range']:.2f}", ln=True)
        pdf.cell(0, 7, txt=f"Tứ phân vị Q1: {stats['q1']:.2f} | Q3: {stats['q3']:.2f}", ln=True)
        pdf.cell(0, 7, txt=f"Khoảng biến thiên (IQR): {stats['iqr']:.2f}", ln=True)
        pdf.cell(0, 7, txt=f"Điểm dị biệt (Outliers): {outliers_str}", ln=True)
        pdf.ln(5)

    return bytes(pdf.output())

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
st.title("📊 Statistical Insights Lab")
st.markdown("Hệ thống trực quan hóa và phân tích dữ liệu đa chiều.")

tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# --- TAB 1 ---
with tab1:
    col1_input, col2_display = st.columns([1.2, 2.8])
    with col1_input:
        with st.container(border=True):
            uploaded_file = st.file_uploader("Tải lên CSV:", type=["csv"], key="file_1")
            raw_single = st.text_area("Nhập dãy số:", value="12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12", height=150)
            plot_type = st.radio("Loại biểu đồ:", ["Box Plot", "Histogram"], key="p1")

    with col2_display:
        try:
            data_str_list = [x.strip() for x in raw_single.replace("\n", ",").split(",") if x.strip()]
            data_single = np.array([float(x) for x in data_str_list if x])
            if len(data_single) > 0:
                stats = calculate_stats(data_single)
                with st.container(border=True):
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Trung bình", f"{stats['mean']:.2f}")
                    m2.metric("Trung vị", f"{stats['median']:.2f}")
                    m3.metric("Yếu vị (Mode)", f"{', '.join(map(lambda x: f'{x:g}', stats['mode']))}")
                    m4.metric("Khoảng GT (Range)", f"{stats['range']:.2f}")
                
                df_single = pd.DataFrame(data_single, columns=["Value"])
                fig = px.box(df_single, y="Value", points="all", title="Biểu đồ hộp", color_discrete_sequence=["#007AFF"]) if plot_type == "Box Plot" else px.histogram(df_single, x="Value", marginal="box", title="Phân phối", color_discrete_sequence=["#007AFF"])
                st.plotly_chart(fig, use_container_width=True)
                
                pdf_bytes = create_pdf_report("BÁO CÁO PHÂN TÍCH ĐƠN NHÓM", {"Dữ liệu 1": stats})
                st.download_button("📥 Tải Báo Cáo PDF", data=pdf_bytes, file_name="ed_odyssey_single.pdf", mime="application/pdf", type="primary")
        except: st.warning("Dữ liệu lỗi.")

# --- TAB 2 ---
with tab2:
    col1_input, col2_display = st.columns([1.2, 2.8])
    with col1_input:
        with st.container(border=True):
            raw_a = st.text_area("Nhóm A:", value="5, 7, 8, 5, 6, 9, 7, 5", height=100)
            raw_b = st.text_area("Nhóm B:", value="3, 4, 12, 14, 5, 6, 8, 9", height=100)

    with col2_display:
        try:
            list_a = [float(x.strip()) for x in raw_a.replace("\n", ",").split(",") if x.strip()]
            list_b = [float(x.strip()) for x in raw_b.replace("\n", ",").split(",") if x.strip()]
            
            stats_a = calculate_stats(np.array(list_a))
            stats_b = calculate_stats(np.array(list_b))
            
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("TB (A)", f"{stats_a['mean']:.2f}", delta=f"{(stats_a['mean'] - stats_b['mean']):.2f}")
                c2.metric("Trung vị (A)", f"{stats_a['median']:.2f}", delta=f"{(stats_a['median'] - stats_b['median']):.2f}")
                c3.metric("IQR (A)", f"{stats_a['iqr']:.2f}", delta=f"{(stats_a['iqr'] - stats_b['iqr']):.2f}")
                c4.metric("Độ lệch (A)", f"{stats_a['std']:.2f}", delta=f"{(stats_a['std'] - stats_b['std']):.2f}")

            df_a = pd.DataFrame({"Value": list_a, "Group": "Nhóm A"})
            df_b = pd.DataFrame({"Value": list_b, "Group": "Nhóm B"})
            fig_compare = px.box(pd.concat([df_a, df_b]), x="Group", y="Value", color="Group", title="So sánh nhóm", color_discrete_sequence=["#007AFF", "#FF5E5E"])
            st.plotly_chart(fig_compare, use_container_width=True)
            
            pdf_bytes_comp = create_pdf_report("BÁO CÁO SO SÁNH (A/B ANALYSIS)", {"Nhóm A": stats_a, "Nhóm B": stats_b})
            st.download_button("📥 Tải Báo Cáo So Sánh", data=pdf_bytes_comp, file_name="ed_odyssey_compare.pdf", mime="application/pdf", type="primary")
        except: st.warning("Dữ liệu lỗi.")

st.markdown("---")
st.caption("ED-ODYSSEY Analytics Engine - Chuyên sâu Thống kê & Trực quan hóa.")
