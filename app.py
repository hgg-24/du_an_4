import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import os
import urllib.request

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (CSS TÙY CHỈNH)
# ==========================================
st.set_page_config(page_title="Statistical Insights Lab", page_icon="📊", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        /* Nền trang và font chữ */
        .stApp { background-color: #F4F7FA; }
        
        /* Tùy chỉnh các khối Metrics (con số chính) */
        div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #007AFF; font-weight: bold; }
        div[data-testid="stMetricDelta"] { font-size: 0.9rem; }
        
        /* Bo góc và đổ bóng cho các khung trắng (Container) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #EAEAEA !important;
            padding: 1.5rem !important;
            margin-bottom: 1rem;
        }
        
        /* Nút tải PDF chuyên nghiệp (Xanh dương, bo góc) */
        .stDownloadButton > button {
            background-color: #007AFF !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            font-weight: bold !important;
            border: none !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 122, 255, 0.2);
        }
        .stDownloadButton > button:hover {
            background-color: #0056b3 !important;
            box-shadow: 0 6px 15px rgba(0, 122, 255, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* Chỉnh tab cho hiện đại */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Tự động tải font Roboto hỗ trợ Tiếng Việt (Unicode)
@st.cache_resource
def load_vietnamese_fonts():
    reg_path = "Roboto-Regular.ttf"
    bold_path = "Roboto-Bold.ttf"
    if not os.path.exists(reg_path):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", reg_path)
    if not os.path.exists(bold_path):
        urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", bold_path)
    return reg_path, bold_path

# ==========================================
# 2. LOGIC TÍNH TOÁN & XUẤT BÁO CÁO PDF
# ==========================================
def calculate_stats(data):
    if len(data) == 0: return None
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

def create_unicode_pdf(report_title, datasets_dict):
    reg, bold = load_vietnamese_fonts()
    pdf = FPDF()
    pdf.add_page()
    
    # Đăng ký font Roboto Unicode
    pdf.add_font("Roboto", "", reg)
    pdf.add_font("Roboto", "B", bold)
    
    # Header dự án
    pdf.set_font("Roboto", "B", 18)
    pdf.set_text_color(0, 122, 255)
    pdf.cell(0, 15, "ED-ODYSSEY ANALYTICS ENGINE", ln=True, align="C")
    
    pdf.set_font("Roboto", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, report_title, ln=True, align="C")
    
    pdf.set_font("Roboto", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Thời gian xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    pdf.line(10, 52, 200, 52)

    # Chi tiết số liệu
    pdf.set_text_color(0, 0, 0)
    for name, stats in datasets_dict.items():
        pdf.set_font("Roboto", "B", 13)
        pdf.cell(0, 10, f"--- Nhóm: {name} ---", ln=True)
        pdf.set_font("Roboto", "", 11)
        mode_val = ", ".join(map(lambda x: f"{x:g}", stats['mode']))
        
        pdf.cell(90, 8, f"• Trung bình (Mean): {stats['mean']:.2f}")
        pdf.cell(90, 8, f"• Trung vị (Median): {stats['median']:.2f}", ln=True)
        pdf.cell(90, 8, f"• Độ lệch chuẩn (Std): {stats['std']:.2f}")
        pdf.cell(90, 8, f"• Phương sai (Var): {stats['var']:.2f}", ln=True)
        pdf.cell(90, 8, f"• Khoảng biến thiên (IQR): {stats['iqr']:.2f}")
        pdf.cell(90, 8, f"• Yếu vị (Mode): {mode_val}", ln=True)
        pdf.ln(5)
        
    return bytes(pdf.output())

# ==========================================
# 3. GIAO DIỆN CHÍNH (TABS & COLUMNS)
# ==========================================
st.title("📊 Statistical Insights Lab")
st.markdown("Hệ thống trực quan hóa và phân tích dữ liệu đa chiều.")

tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# --- TAB 1: PHÂN TÍCH ĐƠN NHÓM ---
with tab1:
    col_in, col_out = st.columns([1.2, 2.8])
    
    with col_in:
        with st.container(border=True):
            st.markdown("### Cấu hình dữ liệu")
            up_file = st.file_uploader("Tải lên CSV (tùy chọn):", type=["csv"], key="up_single")
            
            # Xử lý input mặc định hoặc từ file
            txt_val = "12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12"
            if up_file:
                df_up = pd.read_csv(up_file)
                txt_val = ", ".join(df_up.iloc[:,0].dropna().astype(str).tolist())
            
            raw_input = st.text_area("Nhập dãy số (phân tách bởi dấu phẩy):", value=txt_val, height=180)
            plot_choice = st.radio("Loại biểu đồ hiển thị:", ["Box Plot", "Histogram"], key="p_choice")

    with col_out:
        try:
            # Chuyển đổi text sang array
            nums = np.array([float(x.strip()) for x in raw_input.replace("\n", ",").split(",") if x.strip()])
            
            if len(nums) > 0:
                res = calculate_stats(nums)
                
                # Metrics cốt lõi (Dòng trên cùng bên phải)
                with st.container(border=True):
                    st.markdown("**Kết quả thống kê:**")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Trung bình", f"{res['mean']:.2f}")
                    m2.metric("Trung vị", f"{res['median']:.2f}")
                    m3.metric("Độ lệch chuẩn", f"{res['std']:.2f}")
                    m4.metric("Khoảng IQR", f"{res['iqr']:.2f}")
                
                # Biểu đồ Plotly
                df_p = pd.DataFrame(nums, columns=["Giá trị"])
                if plot_choice == "Box Plot":
                    fig = px.box(df_p, y="Giá trị", points="all", title="Biểu đồ hộp & Outliers", color_discrete_sequence=["#007AFF"])
                else:
                    fig = px.histogram(df_p, x="Giá trị", marginal="box", title="Phân phối tần suất", color_discrete_sequence=["#007AFF"])
                
                fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Nút tải PDF (Unicode có dấu)
                pdf_bytes = create_unicode_pdf("BÁO CÁO PHÂN TÍCH ĐƠN NHÓM", {"Dữ liệu": res})
                st.download_button("📥 Tải Báo Cáo PDF (Tiếng Việt)", data=pdf_bytes, file_name="bao_cao_don_nhom.pdf", mime="application/pdf")
        except:
            st.error("Dữ liệu nhập vào chưa đúng định dạng. Vui lòng chỉ dùng số và dấu phẩy.")

# --- TAB 2: SO SÁNH A/B ---
with tab2:
    col_in2, col_out2 = st.columns([1.2, 2.8])
    
    with col_in2:
        with st.container(border=True):
            st.markdown("### Dữ liệu so sánh")
            raw_a = st.text_area("Nhóm A:", value="10, 12, 14, 11, 13, 12", height=120)
            raw_b = st.text_area("Nhóm B:", value="15, 18, 14, 16, 17, 20", height=120)

    with col_out2:
        try:
            da = np.array([float(x.strip()) for x in raw_a.split(",") if x.strip()])
            db = np.array([float(x.strip()) for x in raw_b.split(",") if x.strip()])
            
            if len(da) > 0 and len(db) > 0:
                sa, sb = calculate_stats(da), calculate_stats(db)
                
                # Metrics so sánh chênh lệch
                with st.container(border=True):
                    st.markdown("**So sánh Trung bình:**")
                    c1, c2 = st.columns(2)
                    c1.metric("Nhóm A", f"{sa['mean']:.2f}")
                    c2.metric("Nhóm B", f"{sb['mean']:.2f}", delta=f"{sb['mean']-sa['mean']:.2f} (vs A)")
                
                # Biểu đồ so sánh
                df_a = pd.DataFrame({'Giá trị': da, 'Nhóm': 'Nhóm A'})
                df_b = pd.DataFrame({'Giá trị': db, 'Nhóm': 'Nhóm B'})
                df_comp = pd.concat([df_a, df_b])
                
                fig_c = px.box(df_comp, x='Nhóm', y='Giá trị', color='Nhóm', title="So sánh phân phối A vs B", color_discrete_sequence=["#007AFF", "#FF5E5E"])
                st.plotly_chart(fig_c, use_container_width=True)
                
                # Tải PDF so sánh (Unicode có dấu)
                pdf_c = create_unicode_pdf("BÁO CÁO SO SÁNH A/B", {"Nhóm A": sa, "Nhóm B": sb})
                st.download_button("📥 Tải Báo Cáo So Sánh (PDF)", data=pdf_c, file_name="bao_cao_so_sanh.pdf", mime="application/pdf")
        except:
            st.error("Dữ liệu ở các nhóm chưa hợp lệ.")

st.markdown("---")
st.caption("Trực quan hóa và hệ thống hóa bởi ED-ODYSSEY Analytics Engine.")
