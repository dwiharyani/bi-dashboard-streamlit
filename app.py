import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BI Dashboard", layout="wide")
st.markdown("""
    <div style='background-color: #f9f0f4; padding: 20px; border-radius: 10px;'>
        <h1 style='text-align: center; color: #5d3a00;'>📊 Business Intelligence Dashboard</h1>
        <h4 style='text-align: center; color: #b65f7b;'>by Dwi Haryani</h4>
    </div>
    <hr style='border: 1px solid #d3c1b2;'>
""", unsafe_allow_html=True)

# Cek apakah ingin pakai data dummy
use_dummy = st.sidebar.checkbox("Gunakan Data Dummy", value=False)

if use_dummy:
    data = {
        "StoreLocation": ["Jakarta", "Bandung", "Surabaya", "Medan"] * 25,
        "TotalAmount": [25000000, 18000000, 22000000, 15000000] * 25,
        "ProductCategory": ["Elektronik", "Fashion", "Elektronik", "Rumah Tangga"] * 25,
        "ProductID": ["P001", "P002", "P003", "P004"] * 25,
        "Quantity": [120, 80, 95, 70] * 25,
        "DiscountApplied(%)": [10, 5, 0, 15] * 25,
        "PaymentMethod": ["Cash", "Credit Card", "Cash", "E-Wallet"] * 25,
        "TransactionDate": pd.date_range(start="2023-01-01", periods=100, freq="W")
    }
    df = pd.DataFrame(data)
else:
    uploaded_file = st.sidebar.file_uploader("📁 Upload Dataset Transaksi (CSV)", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, quotechar='"', escapechar='\\', encoding='utf-8', on_bad_lines='skip')
        except:
            df = pd.read_csv(
                uploaded_file,
                names=["CustomerID", "ProductID", "Quantity", "Price", "TransactionDate",
                       "PaymentMethod", "StoreLocation", "ProductCategory", "DiscountApplied(%)", "TotalAmount"],
                header=None,
                quotechar='"', escapechar='\\', encoding='utf-8', on_bad_lines='skip')
    else:
        st.warning("❗ Silakan upload file CSV terlebih dahulu atau aktifkan mode data dummy.")
        st.stop()

if 'TransactionDate' in df.columns:
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], errors='coerce')
    df["Year"] = df["TransactionDate"].dt.year
    df["Month"] = df["TransactionDate"].dt.strftime("%b")
    df["Month_Num"] = df["TransactionDate"].dt.month
else:
    df["Year"] = 2023
    df["Month"] = "Jan"
    df["Month_Num"] = 1

if "ProductCategory" in df.columns:
    df["ProductCategory"] = df["ProductCategory"].astype(str).str.strip()
if "StoreLocation" in df.columns:
    df["StoreLocation"] = df["StoreLocation"].astype(str).str.strip()

st.sidebar.markdown("""
<div style='background-color: #f2e6e0; padding: 10px; border-radius: 8px;'>
    <h4 style='color: #7b3f00;'>🔍 Filter Global</h4>
</div>
""", unsafe_allow_html=True)
tahun_options = ["Semua Tahun"] + sorted(df["Year"].dropna().astype(int).unique(), reverse=True)
selected_tahun = st.sidebar.selectbox("Pilih Tahun", tahun_options)

if selected_tahun == "Semua Tahun":
    df_tahun = df.copy()
else:
    df_tahun = df[df["Year"] == int(selected_tahun)]

bulan_options = df_tahun["Month"].unique().tolist()
selected_bulan = st.sidebar.multiselect("Pilih Bulan", bulan_options, default=bulan_options)
df_tahun = df_tahun[df_tahun["Month"].isin(selected_bulan)]

# KPI Ringkasan
st.subheader("📌 Ringkasan Kinerja Utama")
col1, col2, col3 = st.columns(3)
col1.metric("Total Transaksi", f"{df_tahun.shape[0]}")
col2.metric("Total Pendapatan", f"${df_tahun['TotalAmount'].sum():,.2f}")
col3.metric("Rata-Rata Diskon", f"{df_tahun['DiscountApplied(%)'].mean():.2f}%")

# Grafik Penjualan Total Tahun Terpilih
st.subheader("📅 Total Penjualan Tahunan")
total_penjualan_tahunan = df.groupby("Year")["TotalAmount"].sum().reset_index()
fig_year_total = px.bar(total_penjualan_tahunan, x="Year", y="TotalAmount", text_auto='.2f',
                        title="Total Penjualan per Tahun",
                        color_discrete_sequence=["#b65f7b"])
st.plotly_chart(fig_year_total, use_container_width=True)

if df_tahun.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
else:
    st.subheader("🛍️ Top 5 Kategori Produk Terlaris")
    penjualan_kategori = df_tahun.groupby("ProductCategory")["TotalAmount"].sum().sort_values(ascending=False).head(5).reset_index()
    fig_kat = px.bar(penjualan_kategori, x="ProductCategory", y="TotalAmount", color="ProductCategory",
                     text_auto='.2f', title=f"Top 5 Kategori dengan Penjualan Terbanyak",
                     color_discrete_sequence=px.colors.sequential.RdPu)
    st.plotly_chart(fig_kat, use_container_width=True)

    st.subheader("📍 Total Pendapatan per Lokasi")
    lokasi_terpilih = st.multiselect("Pilih Lokasi Toko", options=df_tahun["StoreLocation"].unique().tolist())
    df_lokasi = df_tahun[df_tahun["StoreLocation"].isin(lokasi_terpilih)] if lokasi_terpilih else df_tahun
    lokasi_sum = df_lokasi.groupby("StoreLocation")["TotalAmount"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_loc = px.bar(lokasi_sum, x="TotalAmount", y="StoreLocation", orientation="h",
                     color="StoreLocation", text_auto='.2f',
                     title="Lokasi Toko berdasarkan Pendapatan",
                     color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_loc, use_container_width=True)

    st.subheader("🏆 Top 5 Produk Terlaris")
    produk_terlaris = df_tahun.groupby("ProductID")["Quantity"].sum().sort_values(ascending=False).head(5).reset_index()
    fig_top5 = px.bar(produk_terlaris, x="ProductID", y="Quantity", color="ProductID", text_auto='.2f',
                      title="5 Produk dengan Penjualan Tertinggi",
                      color_discrete_sequence=px.colors.sequential.OrRd)
    st.plotly_chart(fig_top5, use_container_width=True)

    st.subheader("💳 Distribusi Metode Pembayaran")
    metode = df_tahun["PaymentMethod"].value_counts().reset_index()
    metode.columns = ["PaymentMethod", "Count"]
    fig_metode = px.pie(metode, names="PaymentMethod", values="Count", title="Persentase Metode Pembayaran",
                        color_discrete_sequence=px.colors.sequential.Pinkyl)
    fig_metode.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_metode, use_container_width=True)

    st.subheader("📈 Tren Penjualan per Bulan")
    monthly_trend = df_tahun.groupby(["Month_Num", "Month"])["TotalAmount"].sum().reset_index()
    monthly_trend = monthly_trend.sort_values("Month_Num")
    fig_trend = px.line(monthly_trend, x="Month", y="TotalAmount", markers=True, text="TotalAmount",
                        title=f"Tren Total Penjualan Bulanan",
                        color_discrete_sequence=["#5d3a00"])
    fig_trend.update_traces(texttemplate='%{text:.2f}', textposition="top center")
    st.plotly_chart(fig_trend, use_container_width=True)

st.subheader("📄 Preview Dataset")
st.dataframe(df.head(10))
