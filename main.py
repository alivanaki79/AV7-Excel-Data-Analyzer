import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ابزار تحلیل فایل اکسل", layout="centered")

# انتخاب زبان
lang = st.sidebar.selectbox("Language / زبان", ["English", "فارسی"])

# متون دو زبانه
texts = {
    "فارسی": {
        "title": "📊 ابزار تحلیل داده‌ها (فارسی + English)",
        "upload": "فایل اکسل یا سی‌اِس‌وی خود را آپلود کنید:",
        "select_file": "انتخاب فایل",
        "success": "✅ فایل با موفقیت بارگذاری شد!",
        "preview": "پیش‌نمایش داده‌ها:",
        "rows": "تعداد ردیف‌ها:",
        "columns": "تعداد ستون‌ها:",
        "describe": "📈 خلاصه آماری ستون‌های عددی:",
        "missing": "🧹 تعداد مقادیر خالی در هر ستون:",
        "unique": "🔢 تعداد مقادیر یکتا در هر ستون:",
        "suggested": "🤖 نمودارهای پیشنهادی خودکار",
        "custom": "🎯 ساخت نمودار دلخواه شما",
        "chart_type": "نوع نمودار",
        "x_axis": "ستون محور X",
        "y_axis": "ستون محور Y (عددی)",
        "pie_warning": "📛 برای رسم نمودار دایره‌ای، ستون X باید حداکثر ۱۵ مقدار یکتا داشته باشد.",
        "filters": "🎚 فیلتر کردن داده‌ها",
        "no_filters": "بدون فیلتر"
    },
    "English": {
        "title": "📊 Data Analysis Tool (English + فارسی)",
        "upload": "Upload your Excel or CSV file:",
        "select_file": "Select File",
        "success": "✅ File uploaded successfully!",
        "preview": "Data Preview:",
        "rows": "Number of Rows:",
        "columns": "Number of Columns:",
        "describe": "📈 Statistical Summary of Numeric Columns:",
        "missing": "🧹 Missing Values in Each Column:",
        "unique": "🔢 Unique Values per Column:",
        "suggested": "🤖 Suggested Charts",
        "custom": "🎯 Create Your Own Chart",
        "chart_type": "Chart Type",
        "x_axis": "X Axis Column",
        "y_axis": "Y Axis Column (numeric)",
        "pie_warning": "📛 To draw a pie chart, the X column must have at most 15 unique values.",
        "filters": "🎚 Filter Your Data",
        "no_filters": "No Filter"
    }
}

T = texts[lang]

st.title(T["title"])
st.markdown(T["upload"])

uploaded_file = st.file_uploader(T["select_file"], type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(T["success"])
        st.write(T["preview"])
        st.dataframe(df.head(10))

        st.markdown(f"**{T['rows']}** {df.shape[0]}")
        st.markdown(f"**{T['columns']}** {df.shape[1]}")

        st.subheader(T["describe"])
        stats = df.describe()
        st.dataframe(stats)

        st.subheader(T["missing"])
        st.dataframe(df.isnull().sum())

        st.subheader(T["unique"])
        st.dataframe(df.nunique())

        numeric_columns = df.select_dtypes(include='number').columns.tolist()
        non_numeric_columns = df.select_dtypes(exclude='number').columns.tolist()

        # بخش فیلتر
        st.subheader(T["filters"])
        filtered_df = df.copy()
        cols_to_filter = st.multiselect("(Column) ستون‌هایی برای فیلتر", df.columns)
        for col in cols_to_filter:
            unique_vals = df[col].dropna().unique().tolist()
            selected_vals = st.multiselect(f" (Desired value for the column) مقدار مورد نظر برای ستون {col}", unique_vals)
            if selected_vals:
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

        # نمودارهای پیشنهادی
        if numeric_columns and non_numeric_columns:
            st.subheader(T["suggested"])
            suggestions_found = False
            for x in non_numeric_columns:
                if df[x].nunique() > 30:
                    continue
                for y in numeric_columns:
                    st.plotly_chart(px.bar(filtered_df, x=x, y=y, title=f"Bar: {y} vs {x}"), use_container_width=True, key=f"bar_{x}_{y}")
                    st.plotly_chart(px.line(filtered_df, x=x, y=y, title=f"Line: {y} vs {x}"), use_container_width=True, key=f"line_{x}_{y}")
                    st.plotly_chart(px.scatter(filtered_df, x=x, y=y, title=f"Scatter: {y} vs {x}"), use_container_width=True, key=f"scatter_{x}_{y}")
                    if df[x].nunique() <= 15:
                        st.plotly_chart(px.pie(filtered_df, names=x, values=y, title=f"Pie: {y} vs {x}"), use_container_width=True, key=f"pie_{x}_{y}")
                    suggestions_found = True
                    break
                if suggestions_found:
                    break
            if not suggestions_found and numeric_columns and non_numeric_columns:
                # نمایش ۴ نمودار پایه با اولین ستون‌ها
                x = non_numeric_columns[0]
                y = numeric_columns[0]
                st.plotly_chart(px.bar(filtered_df, x=x, y=y, title=f"Bar: {y} vs {x}"), use_container_width=True, key="fallback_bar")
                st.plotly_chart(px.line(filtered_df, x=x, y=y, title=f"Line: {y} vs {x}"), use_container_width=True, key="fallback_line")
                st.plotly_chart(px.scatter(filtered_df, x=x, y=y, title=f"Scatter: {y} vs {x}"), use_container_width=True, key="fallback_scatter")
                st.plotly_chart(px.pie(filtered_df, names=x, values=y, title=f"Pie: {y} vs {x}"), use_container_width=True, key="fallback_pie")

        # ساخت نمودار دلخواه
        st.subheader(T["custom"])
        chart_type = st.selectbox(T["chart_type"], ["Bar", "Line", "Pie", "Scatter"])
        x_axis = st.selectbox(T["x_axis"], df.columns)
        y_axis = st.selectbox(T["y_axis"], numeric_columns)

        if chart_type == "Bar":
            fig = px.bar(filtered_df, x=x_axis, y=y_axis, title=f"{y_axis} بر اساس {x_axis}")
            st.plotly_chart(fig, use_container_width=True, key="custom_bar")
        elif chart_type == "Line":
            fig = px.line(filtered_df, x=x_axis, y=y_axis, title=f"{y_axis} بر اساس {x_axis}")
            st.plotly_chart(fig, use_container_width=True, key="custom_line")
        elif chart_type == "Scatter":
            fig = px.scatter(filtered_df, x=x_axis, y=y_axis, title=f"{y_axis} بر اساس {x_axis}")
            st.plotly_chart(fig, use_container_width=True, key="custom_scatter")
        elif chart_type == "Pie":
            if df[x_axis].nunique() <= 15:
                fig = px.pie(filtered_df, names=x_axis, values=y_axis, title=f"{y_axis} بر اساس {x_axis}")
                st.plotly_chart(fig, use_container_width=True, key="custom_pie")
            else:
                st.warning(T["pie_warning"])

    except Exception as e:
        st.error(f"❌ خطا در پردازش فایل: {e}")
