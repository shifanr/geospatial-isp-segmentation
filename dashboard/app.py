import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from branca.element import Template, MacroElement

# ==============================
# 0. KONFIGURASI BAHASA (Language Switcher)
# ==============================
st.set_page_config(page_title="Dashboard Qwords", layout="wide")

# Tambahkan pilihan bahasa di sidebar paling atas
st.sidebar.title("Settings")
lang = st.sidebar.selectbox("🌐 Select Language / Pilih Bahasa", ["ID", "EN"])

# Kamus Terjemahan
texts = {
    "ID": {
        "sidebar_header": "Pusat Filter Sidebar",
        "filter_1": "1. Pilih Kota/Kabupaten",
        "filter_2": "2. Pilih Wilayah/Kecamatan",
        "filter_3": "3. Pilih Kategori Usaha",
        "title": "📊 Dashboard Segmentasi Calon Pelanggan Internet",
        "subtitle": "Analisis Potensi Penjualan Layanan Internet PT Qwords Bandung",
        "kpi_1": "Total Calon Pelanggan",
        "kpi_2": "Titik Lokasi Tersebar",
        "kpi_3": "Segmen Potensi Tinggi",
        "chart_donut": "Proporsi Potensi (%)",
        "chart_bar": "Distribusi Potensi",
        "chart_top10": "Top 10 Kategori Usaha",
        "strategy_header": "💡 Rekomendasi Strategi Penjualan Internet",
        "map_header": "Peta Persebaran Lokasi Terfilter",
        "table_header": "Detail Data Calon Pelanggan",
        "high": "Potensi Tinggi",
        "med": "Potensi Sedang",
        "low": "Potensi Rendah",
        "tips": "💡 **Tips:** Klik pada salah satu batang grafik di atas untuk melihat rekomendasi strategi penjualan internet yang lebih spesifik.",
        "col_usaha": "Nama Usaha",
        "col_kat": "Kategori",
        "col_lok": "Lokasi",
        "col_seg": "Segmentasi Wilayah"
    },
    "EN": {
        "sidebar_header": "Sidebar Filter Center",
        "filter_1": "1. Select City/Regency",
        "filter_2": "2. Select District/Area",
        "filter_3": "3. Select Business Category",
        "title": "📊 Internet Prospective Customer Segmentation Dashboard",
        "subtitle": "Internet Service Sales Potential Analysis for PT Qwords Bandung",
        "kpi_1": "Total Prospective Customers",
        "kpi_2": "Scattered Location Points",
        "kpi_3": "High Potential Segment",
        "chart_donut": "Potential Proportion (%)",
        "chart_bar": "Potential Distribution",
        "chart_top10": "Top 10 Business Categories",
        "strategy_header": "💡 Internet Sales Strategy Recommendation",
        "map_header": "Filtered Location Distribution Map",
        "table_header": "Prospective Customer Data Detail",
        "high": "High Potential",
        "med": "Medium Potential",
        "low": "Low Potential",
        "tips": "💡 **Tips:** Click on a chart bar above to see specific internet sales strategy recommendations.",
        "col_usaha": "Business Name",
        "col_kat": "Category",
        "col_lok": "Location",
        "col_seg": "Regional Segmentation"
    }
}

t = texts[lang]

# ==============================
# 1. LOAD DATASET
# ==============================


@st.cache_data
def load_data():
    path = r"D:\SHIFA\KULIAH\SMT ONE TO EIGHT\Skripsi\codingan\dahsborad\data\dataset_dashboard.csv"
    try:
        df = pd.read_csv(path)
        # Rename original columns to internal English key for consistency
        df = df.rename(columns={
            "Updated_Category": "Kategori",
            "Place Name": "Nama Usaha",
            "Location": "Lokasi",
            "Segmentasi_Wilayah": "Segmentasi Wilayah"
        })
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()


df = load_data()

if not df.empty:
    # Mapping label potensi sesuai bahasa
    mapping_label = {
        "Potensi Tinggi": t["high"],
        "Potensi Sedang": t["med"],
        "Potensi Rendah": t["low"]
    }
    df["Display_Segmen"] = df["Segmentasi Wilayah"].map(mapping_label)

    # ==============================
    # 2. SIDEBAR FILTER
    # ==============================
    st.sidebar.header(t["sidebar_header"])
    st.sidebar.markdown("---")

    kota_options = sorted(df["Kota/Kab"].dropna().unique())
    selected_kota = st.sidebar.multiselect(t["filter_1"], options=kota_options)

    df_filtered = df.copy()
    if selected_kota:
        df_filtered = df_filtered[df_filtered["Kota/Kab"].isin(selected_kota)]

    wilayah_options = sorted(df_filtered["Lokasi"].unique())
    selected_wilayah = st.sidebar.multiselect(
        t["filter_2"], options=wilayah_options)
    if selected_wilayah:
        df_filtered = df_filtered[df_filtered["Lokasi"].isin(selected_wilayah)]

    kategori_sidebar_options = sorted(df_filtered["Kategori"].unique())
    selected_kategori_sidebar = st.sidebar.multiselect(
        t["filter_3"], options=kategori_sidebar_options)
    if selected_kategori_sidebar:
        df_filtered = df_filtered[df_filtered["Kategori"].isin(
            selected_kategori_sidebar)]

    # ==============================
    # 3. JUDUL & KPI
    # ==============================
    st.title(t["title"])
    st.markdown(t["subtitle"])

    total_usaha = len(df_filtered)
    jumlah_titik = df_filtered[["Latitude",
                                "Longitude"]].drop_duplicates().shape[0]
    potensi_tinggi = df_filtered[df_filtered["Segmentasi Wilayah"]
                                 == "Potensi Tinggi"].shape[0]

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric(t["kpi_1"], f"{total_usaha:,}")
    col_kpi2.metric(t["kpi_2"], f"{jumlah_titik:,}")
    col_kpi3.metric(t["kpi_3"], f"{potensi_tinggi:,}")

    st.divider()

    # ==============================
    # 4. VISUALISASI
    # ==============================
    col_donut, col_segmen, col_kategori = st.columns([1, 1.1, 1.2])

    count_segmen = df_filtered["Display_Segmen"].value_counts().reset_index()
    count_segmen.columns = ["Segmen", "Jumlah"]

    warna_diskrit = {
        t["high"]: '#FF8C00',  # Oranye untuk Potensi Tinggi
        t["med"]: '#FFD700',  # Kuning untuk Potensi Sedang
        t["low"]: '#808080'  # Abu-abu untuk Potensi Rendah
    }

    with col_donut:
        st.subheader(t["chart_donut"])
        fig_donut = px.pie(count_segmen, names="Segmen", values="Jumlah", hole=0.5,
                           color="Segmen", color_discrete_map=warna_diskrit, height=350)
        fig_donut.update_traces(textposition='inside', textinfo='percent')
        fig_donut.update_layout(showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_segmen:
        st.subheader(t["chart_bar"])
        fig_segmen = px.bar(count_segmen, x="Segmen", y="Jumlah", color="Segmen",
                            color_discrete_map=warna_diskrit, text_auto=True, height=350)
        st.plotly_chart(fig_segmen, use_container_width=True)

    with col_kategori:
        st.subheader(t["chart_top10"])
        top_10 = df_filtered["Kategori"].value_counts().head(10).reset_index()
        top_10.columns = ["Kategori", "Total"]
        fig_kat = px.bar(top_10, x="Kategori", y="Total", text_auto=True,
                         height=350, color_discrete_sequence=['#3366CC'])
        st.plotly_chart(fig_kat, use_container_width=True)

    # ==============================
    # 5. STRATEGI
    # ==============================
    st.subheader(t["strategy_header"])

    # Logika strategi tetap menggunakan nilai internal ID untuk konsistensi
    current_segmen = df_filtered["Segmentasi Wilayah"].unique()
    top_kat = df_filtered["Kategori"].value_counts(
    ).idxmax() if not df_filtered.empty else "-"

    if len(current_segmen) == 1:
        seg_nama = current_segmen[0]
        if seg_nama == "Potensi Tinggi":
            st.success(
                f"### 🎯 {'Focus Penetration' if lang == 'EN' else 'Fokus Penetrasi'}: {t['high']}")
            if lang == "ID":
                st.markdown(
                    f"* **Analisis:** Peluang konversi tinggi untuk kategori **{top_kat}**.\n* **Produk:** Dedicated Internet Business.\n* **Sales:** Canvassing massal.")
            else:
                st.markdown(
                    f"* **Analysis:** High conversion opportunity for **{top_kat}**.\n* **Product:** Dedicated Internet Business.\n* **Sales:** Mass Canvassing.")
        elif seg_nama == "Potensi Sedang":
            st.warning(
                f"### ⚡ {'Growth Focus' if lang == 'EN' else 'Fokus Pertumbuhan'}: {t['med']}")
            if lang == "ID":
                st.markdown(
                    f"* **Analisis:** Area berkembang didominasi **{top_kat}**.\n* **Produk:** Broadband Business.\n* **Sales:** Telemarketing.")
            else:
                st.markdown(
                    f"* **Analysis:** Emerging area dominated by **{top_kat}**.\n* **Product:** Broadband Business.\n* **Sales:** Telemarketing.")
        else:
            st.info(
                f"### 🌐 {'Awareness Focus' if lang == 'EN' else 'Fokus Awareness'}: {t['low']}")
            if lang == "ID":
                st.markdown(
                    f"* **Analisis:** Sebaran usaha renggang.\n* **Produk:** SOHO / Wireless.\n* **Sales:** Targeted Social Media Ads.")
            else:
                st.markdown(
                    f"* **Analysis:** Sparse business distribution.\n* **Product:** SOHO / Wireless.\n* **Sales:** Targeted Social Media Ads.")
    else:
        st.info(t["tips"])

    st.divider()

    # ==============================
    # 6. PETA
    # ==============================
    st.subheader(t["map_header"])
    if not df_filtered.empty:
        df_map = df_filtered.groupby(["Latitude", "Longitude"]).agg({
            "Display_Segmen": "first", "Nama Usaha": "count", "Lokasi": "first"
        }).reset_index().rename(columns={"Nama Usaha": "Total"})

        m = folium.Map(location=[df_map["Latitude"].mean(
        ), df_map["Longitude"].mean()], zoom_start=11)

        legend_html = f'''
        {{% macro html(this, kwargs) %}}
        <div style="position: fixed; bottom: 30px; left: 30px; width: 170px; height: 95px; 
            background-color: white; border:2px solid grey; z-index:9999; font-size:12px;
            padding: 10px; border-radius: 5px;">
            <b>{'Legend:' if lang == 'EN' else 'Legenda Potensi:'}</b><br>
            <i class="fa fa-circle" style="color:#FF8C00"></i> {t['high']}<br>
            <i class="fa fa-circle" style="color:#FFD700"></i> {t['med']}<br>
            <i class="fa fa-circle" style="color:#808080"></i> {t['low']}
        </div>
        {{% endmacro %}}
        '''
        legend = MacroElement()
        legend._template = Template(legend_html)
        m.get_root().add_child(legend)

        warna_map = {t["high"]: "#FF8C00", t["med"]: "#FFD700", t["low"]: "#808080"}
        for _, row in df_map.iterrows():
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=7, color=warna_map.get(row["Display_Segmen"], "blue"),
                fill=True, fill_opacity=0.6,
                popup=f"<b>{row['Lokasi']}</b><br>Seg: {row['Display_Segmen']}<br>Total: {row['Total']}"
            ).add_to(m)
        st_folium(m, width=1400, height=500)

    st.divider()

    # ==============================
    # 7. TABEL DETAIL & DOWNLOAD
    # ==============================
    st.subheader(t["table_header"])

    # Download Button
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(f"📥 Download CSV", data=csv,
                       file_name='data_internet_qwords.csv', mime='text/csv')

    # --- LOGIKA BARU: MEMBUAT TABEL BERSIH ---
    # 1. Ambil kolom mentah yang dibutuhkan saja
    raw_cols = ["Nama Usaha", "Kategori",
                "Lokasi", "Kota/Kab", "Display_Segmen"]
    df_temp = df_filtered[raw_cols].copy()

    # 2. Berikan nama baru sesuai bahasa yang dipilih
    df_temp.columns = [
        t["col_usaha"],
        t["col_kat"],
        t["col_lok"],
        "Kota/Kab",
        t["col_seg"]
    ]

    # 3. Tampilkan (Sekarang dijamin tidak ada kolom ganda karena kita definisikan ulang strukturnya)
    st.dataframe(df_temp, use_container_width=True, height=400)

else:
    st.error("Dataset not found / Dataset tidak ditemukan.")
