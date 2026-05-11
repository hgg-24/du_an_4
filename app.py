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
        /* Nút tải PDF */
        .stDownloadButton button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: bold !important;
            width: 100%;
        }
        .stDownloadButton button:hover {
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3) !important;
            transform: translateY(-2px);
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
        single_chart_area = st.empty()
        
        try:
            data_str_list = [x.strip() for x in raw_single.replace("\n", ",").split(",") if x.strip()]
            data_single = np.array([float(x) for x in data_str_list if x])
            
            if len(data_single) > 0:
                stats = calculate_stats(data_single)
                
                # Hiển thị metrics thành 2 hàng
                with single_metrics_area.container(border=True):
                    st.markdown("**Các giá trị cốt lõi:**")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Trung bình", f"{stats['mean']:.2f}")
                    m1.latex(r"\bar{x} = \frac{1}{n} \sum x_i")
                    m2.metric("Trung vị", f"{stats['median']:.2f}")
                    m2.latex(r"Q_2")
                    m3.metric("Yếu vị (Mode)", f"{', '.join(map(lambda x: f'{x:g}', stats['mode']))}")
                    m3.latex(r"M_o")
                    m4.metric("Khoảng GT (Range)", f"{stats['range']:.2f}")
                    m4.latex(r"R = Max - Min")

                    st.divider()
                    
                    m5, m6, m7 = st.columns(3)
                    m5.metric("Phương sai", f"{stats['var']:.2f}")
                    m5.latex(r"\sigma^2 = \frac{\sum (x_i - \bar{x})^2}{n}")
                    m6.metric("Độ lệch chuẩn", f"{stats['std']:.2f}")
                    m6.latex(r"\sigma = \sqrt{\sigma^2}")
                    m7.metric("Khoảng IQR", f"{stats['iqr']:.2f}")
                    m7.latex(r"IQR = Q_3 - Q_1")

                # Vẽ biểu đồ
                with single_chart_area.container():
                    df_single = pd.DataFrame(data_single, columns=["Value"])
                    if plot_type == "Box Plot":
                        fig = px.box(df_single, y="Value", points="all", title="Biểu đồ hộp & Outliers",
                                     color_discrete_sequence=["#007AFF"])
                    else:
                        fig = px.histogram(df_single, x="Value", marginal="box", nbins=15,
                                           title="Phân phối tần suất", color_discrete_sequence=["#007AFF"])
                    
                    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True, key="chart_single")
                
                # Tải PDF
                pdf_bytes = create_pdf_report("Phan tich don nhom", {"Dataset 1": stats})
                st.download_button("📥 Tải Báo Cáo PDF", data=pdf_bytes, file_name="ed_odyssey_single_report.pdf", 
                                   mime="application/pdf", key="dl_single")
        except Exception as e:
            single_chart_area.caption("Dữ liệu không hợp lệ. Vui lòng chỉ nhập các số.")

# ------------------------------------------
# TAB 2: SO SÁNH (A/B ANALYSIS)
# ------------------------------------------
with tab2:
    col1_input, col2_display = st.columns([1.2, 2.8])
    
    with col1_input:
        with st.container(border=True):
            st.markdown("##### Nhóm A")
            upload_a = st.file_uploader("CSV Nhóm A:", type=["csv"], key="file_a")
            val_a = "5, 7, 8, 5, 6, 9, 7, 5"
            if upload_a:
                df_a = pd.read_csv(upload_a)
                val_a = ", ".join(df_a.iloc[:, 0].dropna().astype(str).tolist())
            raw_group_a = st.text_area("Dữ liệu Nhóm A:", value=val_a, height=100, key="input_group_a")

            st.markdown("##### Nhóm B")
            upload_b = st.file_uploader("CSV Nhóm B:", type=["csv"], key="file_b")
            val_b = "3, 4, 12, 14, 5, 6, 8, 9"
            if upload_b:
                df_b = pd.read_csv(upload_b)
                val_b = ", ".join(df_b.iloc[:, 0].dropna().astype(str).tolist())
            raw_group_b = st.text_area("Dữ liệu Nhóm B:", value=val_b, height=100, key="input_group_b")

    with col2_display:
        compare_metrics_area = st.empty()
        compare_chart_area = st.empty()
        
        try:
            list_a = [x.strip() for x in raw_group_a.replace("\n", ",").split(",") if x.strip()]
            list_b = [x.strip() for x in raw_group_b.replace("\n", ",").split(",") if x.strip()]
            
            if len(list_a) > 0 and len(list_b) > 0:
                stats_a = calculate_stats(np.array([float(x) for x in list_a]))
                stats_b = calculate_stats(np.array([float(x) for x in list_b]))
                
                # Hiển thị metrics so sánh
                with compare_metrics_area.container(border=True):
                    st.markdown("**So sánh các giá trị cốt lõi (Nhóm A làm gốc):**")
                    c1, c2, c3, c4 = st.columns(4)
                    
                    c1.metric("Trung bình (A)", f"{stats_a['mean']:.2f}", 
                              delta=f"{(stats_a['mean'] - stats_b['mean']):.2f} so với B", delta_color="inverse")
                    c2.metric("Trung vị (A)", f"{stats_a['median']:.2f}", 
                              delta=f"{(stats_a['median'] - stats_b['median']):.2f} so với B", delta_color="inverse")
                    c3.metric("Phương sai (A)", f"{stats_a['var']:.2f}", 
                              delta=f"{(stats_a['var'] - stats_b['var']):.2f} so với B", delta_color="inverse")
                    c4.metric("Độ lệch chuẩn (A)", f"{stats_a['std']:.2f}", 
                              delta=f"{(stats_a['std'] - stats_b['std']):.2f} so với B", delta_color="inverse")

                # Vẽ biểu đồ
                with compare_chart_area.container():
                    df_a = pd.DataFrame({"Value": [float(x) for x in list_a], "Group": "Nhóm A"})
                    df_b = pd.DataFrame({"Value": [float(x) for x in list_b], "Group": "Nhóm B"})
                    df_compare = pd.concat([df_a, df_b])
                    
                    fig_compare = px.box(df_compare, x="Group", y="Value", color="Group", points="all",
                                         color_discrete_sequence=["#007AFF", "#FF5E5E"],
                                         title="So sánh phân phối & Mức độ phân tán (Box Plot)")
                    fig_compare.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_compare, use_container_width=True, key="chart_compare")
                
                # Tải PDF
                pdf_bytes_compare = create_pdf_report("Phan tich so sanh (A/B Analysis)", 
                                                      {"Nhom A": stats_a, "Nhom B": stats_b})
                st.download_button("📥 Tải Báo Cáo So Sánh (PDF)", data=pdf_bytes_compare, 
                                   file_name="ed_odyssey_compare_report.pdf", mime="application/pdf", key="dl_compare")
        except Exception as e:
            compare_chart_area.caption("Dữ liệu không hợp lệ. Vui lòng kiểm tra lại định dạng dữ liệu đầu vào.")

# ==========================================
# 4. FOOTER
# ==========================================
st.markdown("---")
st.caption("Trực quan hóa và hệ thống hóa bởi ED-ODYSSEY Analytics Engine.")
