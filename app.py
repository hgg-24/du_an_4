import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

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
# 2. HÀM TOÁN HỌC & XUẤT PDF AN TOÀN
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

def remove_accents(input_str):
    """Hàm tẩy dấu Tiếng Việt tuyệt đối để chống lỗi FPDF"""
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuUuYyYyYyYy'
    s = ''
    for c in str(input_str):
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s

def create_pdf_report(title, datasets_info):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", style="B", size=16)
    pdf.set_text_color(0, 122, 255) 
    pdf.cell(0, 10, txt=remove_accents("ED-ODYSSEY ANALYTICS ENGINE"), ln=True, align="C")
    
    pdf.set_font("Arial", style="B", size=14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=remove_accents(title), ln=True, align="C")
    
    pdf.set_font("Arial", style="I", size=10)
    pdf.set_text_color(128, 128, 128)
    current_time = datetime.now().strftime("%d/%m/%Y - %H:%M")
    pdf.cell(0, 8, txt=remove_accents(f"Ngày xuất báo cáo: {current_time}"), ln=True, align="C")
    
    pdf.line(10, 42, 200, 42)
    pdf.ln(10)
    
    pdf.set_text_color(0, 0, 0)
    for data_name, stats in datasets_info.items():
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 8, txt=remove_accents(f"--- Nhóm dữ liệu: {data_name} ---"), ln=True)
        pdf.set_font("Arial", style="", size=11)
        
        mode_str = ", ".join(map(lambda x: f"{x:g}", stats['mode']))
        outliers_str = str(stats['outliers']) if stats['outliers'] else "Không có"
        
        pdf.cell(0, 7, txt=remove_accents(f"Trung bình (Mean): {stats['mean']:.2f}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Trung vị (Median): {stats['median']:.2f}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Yếu vị (Mode): {mode_str}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Phương sai (Variance): {stats['var']:.2f}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Độ lệch chuẩn (Std Dev): {stats['std']:.2f}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Khoảng giá trị (Range): {stats['range']:.2f}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Tứ phân vị Q1: {stats['q1']:.2f} | Q3: {stats['q3']:.2f}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Khoảng biến thiên (IQR): {stats['iqr']:.2f}"), ln=True)
        pdf.cell(0, 7, txt=remove_accents(f"Điểm dị biệt (Outliers): {outliers_str}"), ln=True)
        pdf.ln(5)

    # Đảm bảo mã hóa an toàn 100% cho FPDF
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
            uploaded_file = st.file_uploader("Tải lên file CSV (1 cột dữ liệu):", type=["csv"], key="file_single")
            default_val = "12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12"
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    default_val = ", ".join(df_upload.iloc[:, 0].dropna().astype(str).tolist())
                except:
                    st.error("Lỗi file CSV.")
            raw_single = st.text_area("Nhập dãy số:", value=default_val, height=150, key="in_single")
        plot_type = st.radio("Loại biểu đồ:", ["Box Plot", "Histogram"], key="rad_plot")

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
                    st.divider()
                    m5, m6, m7 = st.columns(3)
                    m5.metric("Phương sai", f"{stats['var']:.2f}")
                    m6.metric("Độ lệch chuẩn", f"{stats['std']:.2f}")
                    m7.metric("Khoảng IQR", f"{stats['iqr']:.2f}")

                df_single = pd.DataFrame(data_single, columns=["Value"])
                if plot_type == "Box Plot":
                    fig = px.box(df_single, y="Value", points="all", title="Biểu đồ hộp & Outliers", color_discrete_sequence=["#007AFF"])
                else:
                    fig = px.histogram(df_single, x="Value", marginal="box", nbins=15, title="Phân phối tần suất", color_discrete_sequence=["#007AFF"])
                fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                try:
                    pdf_bytes = create_pdf_report("BÁO CÁO PHÂN TÍCH ĐƠN NHÓM", {"Dataset 1": stats})
                    st.download_button("📥 Tải Báo Cáo PDF", data=pdf_bytes, file_name="ed_odyssey_single.pdf", mime="application/pdf", type="primary")
                except Exception as e:
                    st.error(f"Lỗi tạo PDF: {e}")
        except Exception:
            st.warning("Dữ liệu không hợp lệ.")

# ------------------------------------------
# TAB 2: SO SÁNH (A/B ANALYSIS)
# ------------------------------------------
with tab2:
    col1_input, col2_display = st.columns([1.2, 2.8])
    with col1_input:
        with st.container(border=True):
            st.markdown("##### Nhóm A")
            raw_group_a = st.text_area("Dữ liệu Nhóm A:", value="5, 7, 8, 5, 6, 9, 7, 5", height=100, key="in_a")
            st.markdown("##### Nhóm B")
            raw_group_b = st.text_area("Dữ liệu Nhóm B:", value="3, 4, 12, 14, 5, 6, 8, 9", height=100, key="in_b")

    with col2_display:
        try:
            list_a = [x.strip() for x in raw_group_a.replace("\n", ",").split(",") if x.strip()]
            list_b = [x.strip() for x in raw_group_b.replace("\n", ",").split(",") if x.strip()]
            
            if len(list_a) > 0 and len(list_b) > 0:
                stats_a = calculate_stats(np.array([float(x) for x in list_a]))
                stats_b = calculate_stats(np.array([float(x) for x in list_b]))
                
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Trung bình (A)", f"{stats_a['mean']:.2f}", delta=f"{(stats_a['mean'] - stats_b['mean']):.2f} so với B", delta_color="inverse")
                    c2.metric("Trung vị (A)", f"{stats_a['median']:.2f}", delta=f"{(stats_a['median'] - stats_b['median']):.2f} so với B", delta_color="inverse")
                    c3.metric("Phương sai (A)", f"{stats_a['var']:.2f}", delta=f"{(stats_a['var'] - stats_b['var']):.2f} so với B", delta_color="inverse")
                    c4.metric("Độ lệch chuẩn (A)", f"{stats_a['std']:.2f}", delta=f"{(stats_a['std'] - stats_b['std']):.2f} so với B", delta_color="inverse")

                df_a = pd.DataFrame({"Value": [float(x) for x in list_a], "Group": "Nhóm A"})
                df_b = pd.DataFrame({"Value": [float(x) for x in list_b], "Group": "Nhóm B"})
                df_compare = pd.concat([df_a, df_b])
                
                fig_compare = px.box(df_compare, x="Group", y="Value", color="Group", points="all",
                                     color_discrete_sequence=["#007AFF", "#FF5E5E"], title="So sánh phân phối & Mức độ phân tán (Box Plot)")
                fig_compare.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_compare, use_container_width=True)
                
                try:
                    pdf_bytes_compare = create_pdf_report("BÁO CÁO SO SÁNH (A/B ANALYSIS)", {"Nhóm A": stats_a, "Nhóm B": stats_b})
                    st.download_button("📥 Tải Báo Cáo So Sánh", data=pdf_bytes_compare, file_name="ed_odyssey_compare.pdf", mime="application/pdf", type="primary")
                except Exception as e:
                    st.error(f"Lỗi tạo PDF: {e}")
        except Exception:
            st.warning("Dữ liệu không hợp lệ.")

st.markdown("---")
st.caption("Trực quan hóa và hệ thống hóa bởi ED-ODYSSEY Analytics Engine.")
