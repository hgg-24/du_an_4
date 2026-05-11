import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import os
import urllib.request

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (CSS)
# ==========================================
st.set_page_config(page_title="Statistical Insights Lab", page_icon="📊", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        /* Tổng thể nền trang */
        .stApp { background-color: #F4F7FA; }
        
        /* Tùy chỉnh các khối Metrics */
        div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #007AFF; }
        div[data-testid="stMetricDelta"] { font-size: 1rem; }
        
        /* Bo góc các container dữ liệu */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #EAEAEA !important;
            padding: 1.5rem !important;
        }
        
        /* Tùy chỉnh nút tải PDF chuyên nghiệp */
        .stDownloadButton > button {
            border-radius: 8px !important;
            background-color: #007AFF !important;
            color: white !important;
            font-weight: bold !important;
            padding: 0.6rem 2.5rem !important;
            border: none !important;
            transition: all 0.3s ease;
            width: auto !important;
        }
        .stDownloadButton > button:hover {
            background-color: #0056b3 !important;
            box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3) !important;
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Tự động tải Font Roboto hỗ trợ Tiếng Việt Unicode
@st.cache_resource
def get_fonts():
    reg_path = "Roboto-Regular.ttf"
    bold_path = "Roboto-Bold.ttf"
    if not os.path.exists(reg_path):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", reg_path)
    if not os.path.exists(bold_path):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", bold_path)
    return reg_path, bold_path

# ==========================================
# 2. LOGIC TOÁN HỌC & XỬ LÝ DỮ LIỆU
# ==========================================
def calculate_stats(data_array):
    if len(data_array) == 0: return None
    series = pd.Series(data_array)
    q1, q3 = np.percentile(data_array, [25, 75])
    iqr = q3 - q1
    return {
        "mean": np.mean(data_array),
        "median": np.median(data_array),
        "std": np.std(data_array),
        "var": np.var(data_array),
        "range": np.max(data_array) - np.min(data_array),
        "q1": q1, "q3": q3, "iqr": iqr,
        "mode": series.mode().tolist()
    }

# Hàm tạo PDF Unicode hỗ trợ Tiếng Việt chuẩn
def create_pdf_report(title, datasets_dict):
    reg, bold = get_fonts()
    pdf = FPDF()
    pdf.add_page()
    
    # Đăng ký font Roboto hỗ trợ Unicode
    pdf.add_font("Roboto", "", reg)
    pdf.add_font("Roboto", "B", bold)
    
    # Header Branding
    pdf.set_font("Roboto", "B", 18)
    pdf.set_text_color(0, 122, 255)
    pdf.cell(0, 15, "ED-ODYSSEY ANALYTICS REPORT", ln=True, align="C")
    
    pdf.set_font("Roboto", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, title, ln=True, align="C")
    
    pdf.set_font("Roboto", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Ngày xuất báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    pdf.line(10, 52, 200, 52)

    # Nội dung chi tiết từng nhóm
    pdf.set_text_color(0, 0, 0)
    for group_name, stats in datasets_dict.items():
        pdf.set_font("Roboto", "B", 13)
        pdf.cell(0, 10, f"--- Nhóm dữ liệu: {group_name} ---", ln=True)
        
        pdf.set_font("Roboto", "", 11)
        mode_str = ", ".join(map(lambda x: f"{x:g}", stats['mode']))
        
        col_width = 90
        pdf.cell(col_width, 8, f"+ Trung bình (Mean): {stats['mean']:.2f}")
        pdf.cell(col_width, 8, f"+ Trung vị (Median): {stats['median']:.2f}", ln=True)
        pdf.cell(col_width, 8, f"+ Độ lệch chuẩn (Std): {stats['std']:.2f}")
        pdf.cell(col_width, 8, f"+ Phương sai (Var): {stats['var']:.2f}", ln=True)
        pdf.cell(col_width, 8, f"+ Khoảng IQR: {stats['iqr']:.2f}")
        pdf.cell(col_width, 8, f"+ Yếu vị (Mode): {mode_str}", ln=True)
        pdf.ln(5)
        
    return bytes(pdf.output())

# ==========================================
# 3. GIAO DIỆN TỔNG THỂ (TABS)
# ==========================================
st.title("📊 Statistical Insights Lab")
st.markdown("Hệ thống trực quan hóa và phân tích thống kê dữ liệu đa chiều.")

tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# --- TAB 1: PHÂN TÍCH ĐƠN NHÓM ---
with tab1:
    col1_in, col1_out = st.columns([1.3, 2.7])
    
    with col1_in:
        with st.container(border=True):
            st.markdown("#### Cấu hình dữ liệu")
            up_file = st.file_uploader("Tải lên CSV (tùy chọn):", type=["csv"], key="single_up")
            
            default_text = "12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12"
            if up_file:
                try:
                    df_up = pd.read_csv(up_file)
                    default_text = ", ".join(df_up.iloc[:, 0].dropna().astype(str).tolist())
                except: st.error("Lỗi đọc file CSV.")
                
            input_data = st.text_area("Nhập dãy số (cách nhau bởi dấu phẩy):", value=default_text, height=180)
            plot_type = st.radio("Loại biểu đồ hiển thị:", ["Box Plot", "Histogram"])

    with col1_out:
        try:
            # Xử lý mảng số
            nums = np.array([float(x.strip()) for x in input_data.replace("\n", ",").split(",") if x.strip()])
            
            if len(nums) > 0:
                stats = calculate_stats(nums)
                
                # Hiển thị Metrics chính
                with st.container(border=True):
                    st.markdown("**Các chỉ số cốt lõi:**")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Trung bình", f"{stats['mean']:.2f}")
                    m2.metric("Trung vị", f"{stats['median']:.2f}")
                    m3.metric("Độ lệch chuẩn", f"{stats['std']:.2f}")
                    m4.metric("Khoảng IQR", f"{stats['iqr']:.2f}")
                
                # Biểu đồ Plotly
                df_plot = pd.DataFrame(nums, columns=["Value"])
                if plot_type == "Box Plot":
                    fig = px.box(df_plot, y="Value", points="all", title="Biểu đồ hộp & Điểm dị biệt", color_discrete_sequence=["#007AFF"])
                else:
                    fig = px.histogram(df_plot, x="Value", marginal="box", title="Phân phối tần suất dữ liệu", color_discrete_sequence=["#007AFF"])
                
                fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Nút tải file PDF (Có dấu)
                pdf_bytes = create_pdf_report("PHÂN TÍCH ĐƠN NHÓM", {"Dữ liệu nhóm": stats})
                st.download_button(
                    label="📥 Tải Báo Cáo PDF (Tiếng Việt)",
                    data=pdf_bytes,
                    file_name="ed_odyssey_report.pdf",
                    mime="application/pdf"
                )
        except:
            st.warning("Vui lòng kiểm tra lại định dạng dữ liệu (chỉ nhập số và dấu phẩy).")

# --- TAB 2: SO SÁNH A/B ---
with tab2:
    col2_in, col2_out = st.columns([1.3, 2.7])
    
    with col2_in:
        with st.container(border=True):
            st.markdown("#### Nhập liệu Nhóm A")
            raw_a = st.text_area("Dữ liệu nhóm A:", value="10, 12, 14, 15, 13, 11", height=100)
            st.markdown("#### Nhập liệu Nhóm B")
            raw_b = st.text_area("Dữ liệu nhóm B:", value="15, 18, 14, 16, 17, 22", height=100)

    with col2_out:
        try:
            da = np.array([float(x.strip()) for x in raw_a.split(",") if x.strip()])
            db = np.array([float(x.strip()) for x in raw_b.split(",") if x.strip()])
            
            if len(da) > 0 and len(db) > 0:
                sa = calculate_stats(da)
                sb = calculate_stats(db)
                
                # Metrics so sánh nhanh
                with st.container(border=True):
                    st.markdown("**So sánh Trung bình:**")
                    c1, c2 = st.columns(2)
                    c1.metric("Nhóm A", f"{sa['mean']:.2f}")
                    c2.metric("Nhóm B", f"{sb['mean']:.2f}", delta=f"{sb['mean']-sa['mean']:.2f} so với A")
                
                # Biểu đồ so sánh
                df_a = pd.DataFrame({'Giá trị': da, 'Nhóm': 'Nhóm A'})
                df_b = pd.DataFrame({'Giá trị': db, 'Nhóm': 'Nhóm B'})
                df_comp = pd.concat([df_a, df_b])
                
                fig_comp = px.box(df_comp, x='Nhóm', y='Giá trị', color='Nhóm', 
                                  title="So sánh phân phối giữa Nhóm A và Nhóm B",
                                  color_discrete_sequence=["#007AFF", "#FF5E5E"])
                st.plotly_chart(fig_comp, use_container_width=True)
                
                # Tải PDF so sánh (Có dấu)
                pdf_comp = create_pdf_report("SO SÁNH DỮ LIỆU A/B", {"Nhóm A": sa, "Nhóm B": sb})
                st.download_button(
                    label="📥 Tải Báo Cáo So Sánh (PDF)",
                    data=pdf_comp,
                    file_name="ed_odyssey_comparison.pdf",
                    mime="application/pdf"
                )
        except:
            st.warning("Vui lòng kiểm tra lại dữ liệu ở cả hai nhóm.")

st.markdown("---")
st.caption("Trực quan hóa và hệ thống hóa bởi ED-ODYSSEY Analytics Engine.")
