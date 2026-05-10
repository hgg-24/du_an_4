import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import io

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (UI/UX)
# ==========================================
st.set_page_config(page_title="ED-ODYSSEY | Stats Lab", layout="wide")

def inject_custom_css():
    st.markdown(r"""
    <style>
        :root {
            --primary-color: #007AFF;
        }
        .stApp {
            background-color: #F4F7FA;
        }
        /* Neumorphism cho các container */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 16px !important;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #E5E5EA !important;
            padding: 1.2rem;
        }
        /* Nút tải PDF */
        .stDownloadButton>button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: bold !important;
            width: 100%;
        }
        .stDownloadButton>button:hover {
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3) !important;
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. ENGINE TOÁN HỌC & XUẤT PDF
# ==========================================
def calculate_stats(data_array):
    """Tính toán tất cả các chỉ số thống kê cơ bản."""
    q1 = np.percentile(data_array, 25)
    q3 = np.percentile(data_array, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = data_array[(data_array < lower_bound) | (data_array > upper_bound)]
    
    return {
        "mean": np.mean(data_array),
        "median": np.median(data_array),
        "var": np.var(data_array),
        "std": np.std(data_array),
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "outliers": outliers.tolist()
    }

def create_pdf_report(title, datasets_info):
    """
    Tạo PDF. Lưu ý: Sử dụng tiếng Việt không dấu để đảm bảo
    thư viện FPDF không bị lỗi Encoding trên Streamlit Cloud.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Tiêu đề
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="THONG KE CHI TIET - ED-ODYSSEY", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    
    # Nội dung từng nhóm dữ liệu
    pdf.set_font("Arial", size=12)
    for data_name, stats in datasets_info.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=f"--- Nhom du lieu: {data_name} ---", ln=True)
        pdf.set_font("Arial", size=12)
        
        pdf.cell(0, 8, txt=f"Trung binh (Mean): {stats['mean']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Trung vi (Median): {stats['median']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Phuong sai (Variance): {stats['var']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Do lech chuan (Std Dev): {stats['std']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Tu phan vi Q1: {stats['q1']:.2f} | Q3: {stats['q3']:.2f}", ln=True)
        pdf.cell(0, 8, txt=f"Khoang bien thien (IQR): {stats['iqr']:.2f}", ln=True)
        
        if len(stats['outliers']) > 0:
            pdf.cell(0, 8, txt=f"Diem di biet (Outliers): {stats['outliers']}", ln=True)
        else:
            pdf.cell(0, 8, txt="Khong co diem di biet (Outliers).", ln=True)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
st.title("📊 Statistical Insights Lab")
st.markdown("Hệ thống trực quan hóa và phân tích dữ liệu đa chiều.")

# Phân tách 2 tính năng bằng Tabs để UI luôn Minimalist
tab1, tab2 = st.tabs(["🔬 Phân tích Đơn nhóm", "⚖️ So sánh (A/B Analysis)"])

# ------------------------------------------
# TAB 1: PHÂN TÍCH ĐƠN NHÓM
# ------------------------------------------
with tab1:
    col1_input, col1_display = st.columns([1.2, 2.8])
    
    with col1_input:
        with st.container(border=True):
            raw_single = st.text_area(
                "Nhập dãy số (phân tách bởi dấu phẩy):",
                value="12, 15, 14, 16, 18, 21, 23, 50, 11, 14, 15, 12",
                height=150,
                key="input_single_data"
            )
            plot_type = st.radio("Loại biểu đồ:", ["Box Plot", "Histogram"], key="radio_plot_type")
            
    with col1_display:
        # Giữ chỗ cố định cho Đồ thị và Chỉ số để tránh lỗi removeChild
        single_metrics_area = st.empty()
        single_chart_area = st.empty()
        
        try:
            # Tiền xử lý dữ liệu
            data_str_list = [x.strip() for x in raw_single.replace('\n', ',').split(',')]
            data_single = np.array([float(x) for x in data_str_list if x])
            
            if len(data_single) > 0:
                stats = calculate_stats(data_single)
                
                # Hiển thị Metrics với Raw Strings cho LaTeX
                with single_metrics_area.container(border=True):
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Trung bình", f"{stats['mean']:.2f}")
                    m1.latex(r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i")
                    
                    m2.metric("Trung vị", f"{stats['median']:.2f}")
                    m2.latex(r"Q_2")
                    
                    m3.metric("Phương sai", f"{stats['var']:.2f}")
                    m3.latex(r"\sigma^2 = \frac{\sum (x_i - \bar{x})^2}{n}")
                    
                    m4.metric("Khoảng IQR", f"{stats['iqr']:.2f}")
                    m4.latex(r"IQR = Q_3 - Q_1")

                # Vẽ biểu đồ
                with single_chart_area.container():
                    df_single = pd.DataFrame(data_single, columns=["Value"])
                    if plot_type == "Box Plot":
                        fig = px.box(df_single, y="Value", points="all", title="Biểu đồ hộp & Outliers",
                                     color_discrete_sequence=['#007AFF'])
                    else:
                        fig = px.histogram(df_single, x="Value", marginal="box", nbins=15, 
                                           title="Phân phối tần suất", color_discrete_sequence=['#007AFF'])
                    
                    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                    # Đảm bảo key duy nhất cho plotly_chart
                    st.plotly_chart(fig, use_container_width=True, key="chart_single")
                
                # Tải PDF
                pdf_bytes = create_pdf_report("Phan tich don nhom", {"Dataset 1": stats})
                st.download_button("📥 Tải Báo Cáo PDF", data=pdf_bytes, file_name="ed_odyssey_single_report.pdf", mime="application/pdf", key="dl_single")
            else:
                single_chart_area.caption("Đang chờ dữ liệu hợp lệ...")
        except Exception:
            single_chart_area.caption("Lỗi cú pháp. Vui lòng chỉ nhập các chữ số và dấu phẩy.")

# ------------------------------------------
# TAB 2: PHÂN TÍCH SO SÁNH (A/B ANALYSIS)
# ------------------------------------------
with tab2:
    col2_input, col2_display = st.columns([1.2, 2.8])
    
    with col2_input:
        with st.container(border=True):
            raw_group_a = st.text_area("Nhóm A (VD: Lớp 1, Cổ phiếu A):", value="5, 7, 8, 5, 6, 9, 7, 5", height=100, key="input_group_a")
            raw_group_b = st.text_area("Nhóm B (VD: Lớp 2, Cổ phiếu B):", value="3, 4, 12, 14, 5, 6, 8, 9", height=100, key="input_group_b")
            
    with col2_display:
        compare_metrics_area = st.empty()
        compare_chart_area = st.empty()
        
        try:
            list_a = [float(x.strip()) for x in raw_group_a.replace('\n', ',').split(',') if x.strip()]
            list_b = [float(x.strip()) for x in raw_group_b.replace('\n', ',').split(',') if x.strip()]
            
            if len(list_a) > 0 and len(list_b) > 0:
                stats_a = calculate_stats(np.array(list_a))
                stats_b = calculate_stats(np.array(list_b))
                
                # Hiển thị chỉ số so sánh nhanh
                with compare_metrics_area.container(border=True):
                    st.markdown("**So sánh các giá trị cốt lõi:**")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Trung bình (A vs B)", f"{stats_a['mean']:.2f}", delta=f"{stats_a['mean'] - stats_b['mean']:.2f} so với B")
                    c2.metric("Phương sai (A vs B)", f"{stats_a['var']:.2f}", delta=f"{stats_a['var'] - stats_b['var']:.2f} so với B", delta_color="inverse")
                    c3.metric("IQR (A vs B)", f"{stats_a['iqr']:.2f}", delta=f"{stats_a['iqr'] - stats_b['iqr']:.2f} so với B", delta_color="inverse")
                
                # Biểu đồ so sánh
                with compare_chart_area.container():
                    # Gộp data để vẽ
                    df_a = pd.DataFrame({"Value": list_a, "Group": "Nhóm A"})
                    df_b = pd.DataFrame({"Value": list_b, "Group": "Nhóm B"})
                    df_compare = pd.concat([df_a, df_b])
                    
                    fig_compare = px.box(df_compare, x="Group", y="Value", color="Group", points="all",
                                         color_discrete_sequence=['#007AFF', '#FF3B30'],
                                         title="So sánh phân phối & Mức độ phân tán (Box Plot)")
                    fig_compare.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_compare, use_container_width=True, key="chart_compare")
                
                # Tải PDF
                pdf_bytes_compare = create_pdf_report("Phan tich so sanh (A/B Analysis)", {"Nhom A": stats_a, "Nhom B": stats_b})
                st.download_button("📥 Tải Báo Cáo So Sánh (PDF)", data=pdf_bytes_compare, file_name="ed_odyssey_compare_report.pdf", mime="application/pdf", key="dl_compare")
            else:
                compare_chart_area.caption("Đang chờ dữ liệu hợp lệ từ cả 2 nhóm...")
        except Exception:
            compare_chart_area.caption("Lỗi cú pháp. Vui lòng kiểm tra lại định dạng dữ liệu đầu vào.")

# ==========================================
# 4. FOOTER
# ==========================================
st.markdown("---")
st.caption("Trực quan hóa và hệ thống hóa bởi ED-ODYSSEY Analytics Engine.")
