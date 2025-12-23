import streamlit as st
import pandas as pd
import os
from datetime import date

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Báo cáo học tập", layout="wide")

DATA_FILE = "data.csv"

# ================== LOAD / INIT DATA ==================
if "data" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.data = pd.read_csv(DATA_FILE)

        # Vá cột thiếu nếu file cũ
        for col in ["Bé đã làm tốt các phần:", "Tuy nhiên, cần cải thiện thêm:"]:
            if col not in st.session_state.data.columns:
                st.session_state.data[col] = ""
    else:
        st.session_state.data = pd.DataFrame(
            columns=["Ngày", "Nội dung học", "Bé đã làm tốt các phần:", "Tuy nhiên, cần cải thiện thêm:", "Đánh giá"]
        )

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ================== TIÊU ĐỀ ==================
st.title("📘 BÁO CÁO KẾT QUẢ HỌC TẬP")

# ================== THÔNG TIN CHUNG ==================
with st.expander("ℹ️ Thông tin học sinh", expanded=True):
    student_name = st.text_input("Tên học sinh", "Quốc Anh")

# ================== FORM THÊM / SỬA ==================
st.divider()
st.subheader("➕ Thêm / ✏️ Sửa buổi học")

with st.form("lesson_form", clear_on_submit=True):
    lesson_date = st.date_input(
        "📅 Ngày học",
        value=date.today() if st.session_state.edit_index is None
        else pd.to_datetime(
            st.session_state.data.loc[st.session_state.edit_index, "Ngày"],
            dayfirst=True
        )
    )

    content = st.text_area("📚 Nội dung học", height=120)

    col1, col2 = st.columns(2)
    with col1:
        pros = st.text_area("✅ Bé đã làm tốt các phần:", height=100)
    with col2:
        cons = st.text_area("⚠️ Tuy nhiên, cần cải thiện thêm:", height=100)

    rating = st.selectbox(
        "📊 Đánh giá",
        ["Xuất sắc", "Tốt", "Khá", "Cần cố gắng"]
    )

    save_btn = st.form_submit_button("💾 LƯU BUỔI HỌC")

    if save_btn:
        new_row = {
            "Ngày": lesson_date.strftime("%d/%m/%Y"),
            "Nội dung học": content,
            "Bé đã làm tốt các phần:": pros,
            "Tuy nhiên, cần cải thiện thêm:": cons,
            "Đánh giá": rating
        }

        if st.session_state.edit_index is None:
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([new_row])],
                ignore_index=True
            )
        else:
            st.session_state.data.loc[st.session_state.edit_index] = new_row
            st.session_state.edit_index = None

        # 💾 LƯU FILE
        st.session_state.data.to_csv(DATA_FILE, index=False)

        st.success("✅ Đã lưu buổi học")
        st.rerun()

# ================== TÌM KIẾM & LỌC ==================
st.divider()
st.subheader("🔍 Tìm kiếm & lọc")

search_text = st.text_input("🔎 Tìm trong nội dung học")
filter_rating = st.multiselect(
    "📊 Lọc theo đánh giá",
    ["Xuất sắc", "Tốt", "Khá", "Cần cố gắng"],
    default=["Xuất sắc", "Tốt", "Khá", "Cần cố gắng"]
)

df = st.session_state.data.copy()

if search_text:
    df = df[df["Nội dung học"].str.contains(search_text, case=False, na=False)]

df = df[df["Đánh giá"].isin(filter_rating)]

# ================== DANH SÁCH BUỔI HỌC (RÚT GỌN) ==================
st.divider()
st.subheader("📋 Danh sách buổi học (5 buổi gần nhất)")

if df.empty:
    st.info("Chưa có dữ liệu phù hợp.")
else:
    # Sort nhưng GIỮ index gốc
    df_sorted = df.copy()
    df_sorted["Ngày_sort"] = pd.to_datetime(df_sorted["Ngày"], dayfirst=True)
    df_sorted = df_sorted.sort_values("Ngày_sort", ascending=False)

    visible_df = df_sorted.head(5)

    for idx, row in visible_df.iterrows():
        with st.expander(f"📅 {row['Ngày']} — {row['Đánh giá']}"):
            st.markdown(f"**📚 Nội dung học:**\n\n{row['Nội dung học']}")
            st.markdown(f"**✅ Bé đã làm tốt các phần:**\n\n{row['Bé đã làm tốt các phần:']}")
            st.markdown(f"**⚠️ Tuy nhiên, cần cải thiện thêm:**\n\n{row['Tuy nhiên, cần cải thiện thêm:']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Sửa", key=f"edit_{idx}"):
                    st.session_state.edit_index = idx
                    st.rerun()

            with col2:
                if st.button("❌ Xóa", key=f"delete_{idx}"):
                    st.session_state.data = (
                        st.session_state.data.drop(idx).reset_index(drop=True)
                    )
                    st.session_state.data.to_csv(DATA_FILE, index=False)
                    st.rerun()


# ================== THỐNG KÊ ==================
st.divider()
st.subheader("📊 Thống kê tiến độ")

if not st.session_state.data.empty:
    rating_map = {
        "Cần cố gắng": 1,
        "Khá": 2,
        "Tốt": 3,
        "Xuất sắc": 4
    }

    chart_df = st.session_state.data.copy()
    chart_df["Score"] = chart_df["Đánh giá"].map(rating_map)
    chart_df["Ngày"] = pd.to_datetime(chart_df["Ngày"], dayfirst=True)
    chart_df = chart_df.sort_values("Ngày")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Số buổi theo đánh giá")
        st.bar_chart(chart_df["Đánh giá"].value_counts())

    with col2:
        st.markdown("### 📈 Xu hướng tiến bộ")
        st.line_chart(chart_df.set_index("Ngày")["Score"])

    percent = chart_df["Đánh giá"].value_counts(normalize=True) * 100
    st.markdown("### 🧮 Tỷ lệ % đánh giá")
    st.dataframe(percent.round(1).astype(str) + " %")

else:
    st.info("Chưa có dữ liệu để thống kê.")

st.caption("📌 Dữ liệu được lưu tự động – phụ huynh có thể xem bất cứ lúc nào")


