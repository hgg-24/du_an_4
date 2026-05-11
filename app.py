import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# ==========================================
# 1. THIẾT LẬP TRANG & GIAO DIỆN CƠ BẢN (CSS)
# ==========================================
st.set_page_config(page_title="Statistical Insights Lab", page_icon="📊", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        /* CSS tuỳ chỉnh cho giao diện */
        .stApp {
            background-color: #F4F7FA;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        div[data-testid="stMetricDelta"] {
            font-size: 1rem;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #EAEAEA !important;
            padding: 0.5rem;
        }
        /* Nút tải PDF nhỏ gọn và mượt mà hơn */
        .stDownloadButton > button {
            border-radius: 6px !important;
            transition: all 0.3s ease;
        }
        .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. HÀM TOÁN HỌC & XUẤT PDF
# ==========================================
def calculate_stats(data_array):
    """Tính toán tất cả các chỉ số thống kê cơ bản."""
    q1 = np.percentile(data_array, 25)
    q3 = np.percentile(data_array, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = data_array[(data_array < lower_bound) | (data_array > upper_bound)]
    
    # Các chỉ số mới
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

def create_pdf_report(title, datasets_info):
    """Tạo file PDF báo cáo. Trả về định dạng bytes."""
    pdf = FPDF()
    pdf.add_page()
    
    # Tiêu đề
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt="THONG KE CHI TIET - ED-ODYSSEY", ln=True, align="C")
    pdf.set_font("Arial", "I", 12)
    pdf.cell(0, 10, txt=title, ln=True, align="C")
    pdf.ln(10)
    
    # Nội dung
    pdf.set_font("Arial", "", 12)
    for data_name, stats in datasets_info.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, txt=f"--- Nhom du lieu: {data_name} ---", ln=True)
        pdf.set_font("Arial", "", 12)
        
        mode_str = ", ".join(map(lambda x: f"{x:g}", stats['mode']))
        
        pdf.cell(0, 8, txt=f"Trung binh (Mean): {stats['mean']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Trung vi (Median): {stats['median']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Yeu vi (Mode): {mode_str}", ln=True)
        pdf.cell(0, 8, txt=f"Phuong sai (Variance): {stats['var']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Do lech chuan (Std Dev): {stats['std']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Khoang gia tri (Range): {stats['range']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Tu phan vi Q1: {stats['q1']:.2f} | Q3: {stats['q3']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Khoang bien thien (IQR): {stats['iqr']:.2f}", ln=True)
        
        outliers_str = str(stats['outliers']) if stats['outliers'] else "Khong co"
        pdf.cell(0, 8, txt=f"Diem di biet (Outliers): {outliers_str}", ln=True)
        pdf.ln(5)
        
    return bytes(pdf.output(dest='S').encode('latin-1'))

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
st.title("📊 Statistical Insights Lab")
st.markdown("Hệ thống trực quan hóa và phân tích dữ liệu đa chiều.")

tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# ------------------------------------------
# TAB 1: PHÂN TÍCH ĐƠN NHÓM
# ------------------------------------------
with tab1:
    col1_input, col2_display = st.columns([1.2, 2.8])
    
    with col1_input:
        with st.container(border=True):
            # Tính năng Upload file
            uploaded_file = st.file_uploader("Tải lên file CSV (1 cột dữ liệu):", type=["csv"], key="file_single")
            
            default_val = "12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12"
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    first_column = df_upload.iloc[:, 0].dropna().astype(str).tolist()
                    default_val = ", ".join(first_column)
                    st.success(f"Đã tải thành công {len(first_column)} dòng!")
                except Exception as e:
                    st.error("Lỗi file CSV. Hãy đảm bảo định dạng đúng.")

            raw_single = st.text_area("Nhập dãy số (phân tách bởi dấu phẩy):", 
                                      value=default_val, 
                                      height=150, 
                                      key="input_single_data")
            
        plot_type = st.radio("Loại biểu đồ:", ["Box Plot", "Histogram"], key="radio_plot_type")

    with col2_display:
        single_metrics_area = st.empty()
        single_chart_area = st.empty
