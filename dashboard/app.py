import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from branca.element import Template, MacroElement
import os

# ==============================
# 0. KONFIGURASI HALAMAN & BAHASA
# ==============================
st.set_page_config(page_title="Dashboard Qwords Intelligence", layout="wide")

st.sidebar.title("Settings")
lang = st.sidebar.selectbox("🌐 Select Language / Pilih Bahasa", ["ID", "EN"])

# Kamus Terjemahan - Menambahkan bagian "The Why" agar support EN
texts = {
    "ID": {
        "sidebar_header": "Pusat Filter Wilayah",
        "filter_1": "1. Pilih Wilayah Administrasi",
        "filter_2": "2. Pilih Kecamatan/Area",
        "filter_3": "3. Pilih Kategori Usaha",
        "title": "🛰️ Geospatial Intelligence: Pemetaan Strategis Potensi Pasar Internet Wilayah Bandung Raya",
        "subtitle": "Analisis Potensi Penjualan Layanan Internet PT Qwords (Kota Bandung, Kab. Bandung, & Cimahi)",
        "kpi_1": "Total Calon Pelanggan",
        "kpi_2": "Total Titik Lokasi",
        "kpi_3": "Volume Prospek Berpotensi Tinggi",
        "chart_donut": "Proporsi Pangsa Pasar (%)",
        "chart_bar": "Distribusi Potensi Wilayah",
        "chart_top10": "Top 10 Kategori Bisnis",
        "strategy_header": "Rekomendasi Strategi Pemasaran",
        "map_header": "Peta Rekomendasi Potensi Wilayah",
        "table_header": "Eksplorasi Detail Entitas Bisnis",
        "high": "Potensi Tinggi",
        "med": "Potensi Sedang",
        "low": "Potensi Rendah",
        "tips": "💡 **Tips:** Klik pada batang grafik atau potongan donat untuk melihat strategi spesifik wilayah tersebut.",
        "col_usaha": "Nama Usaha",
        "col_kat": "Kategori",
        "col_lok": "Lokasi",
        "col_seg": "Segmentasi Wilayah",
        # Penjelasan Detail Potensi (The Why) ID
        "exp_title": "🔍 Analisis Karakteristik Wilayah (Mengapa Berpotensi?)",
        "exp_why_high": "**Mengapa Berpotensi?** Wilayah ini memiliki konsentrasi entitas bisnis (kantor, klinik, kafe) yang sangat rapat, terutama di pusat ekonomi Kota Bandung dan Cimahi.",
        "exp_act_high": "**Aksi:** Prioritas utama pembangunan infrastruktur **Fiber Optic (FO)**. Fokus pada layanan internet Dedicated dengan reliabilitas tinggi.",
        "exp_why_med": "**Mengapa Berpotensi?** Wilayah transisi atau area berkembang di Kabupaten Bandung dan pinggiran kota dengan jumlah ruko/UMKM yang mulai tumbuh.",
        "exp_act_med": "**Aksi:** Fokus pada penetrasi pasar menggunakan paket internet bisnis broadband yang kompetitif dan fleksibel.",
        "exp_why_low": "**Mengapa Kurang Berpotensi?** Wilayah didominasi area residensial, lahan terbuka, atau aktivitas komersial yang letaknya berjauhan (tersebar).",
        "exp_act_low": "**Aksi:** Pemantauan berkala. Penambahan infrastruktur jaringan dilakukan hanya berdasarkan permintaan khusus dari komunitas atau korporat."
    },
    "EN": {
        "sidebar_header": "Regional Filter Center",
        "filter_1": "1. Select Administrative Area",
        "filter_2": "2. Select District/Area",
        "filter_3": "3. Select Business Category",
        "title": "🛰️ Geospatial Intelligence: Strategic Mapping of Bandung Metropolitan Internet Market Potential",
        "subtitle": "Internet Service Sales Potential Analysis for PT Qwords (Bandung City, Bandung Regency, & Cimahi)",
        "kpi_1": "Total Potential Leads",
        "kpi_2": "Total Location Points",
        "kpi_3": "High-Potential Leads Volume",
        "chart_donut": "Market Share Proportion (%)",
        "chart_bar": "Regional Potential Distribution",
        "chart_top10": "Top 10 Business Categories",
        "strategy_header": "Strategic Marketing Recommendations",
        "map_header": "Regional Potential Recommendation Map",
        "table_header": "Detailed Business Entity Exploration",
        "high": "High Potential",
        "med": "Medium Potential",
        "low": "Low Potential",
        "tips": "💡 **Tips:** Click on a chart bar or donut slice to see region-specific strategies.",
        "col_usaha": "Business Name",
        "col_kat": "Category",
        "col_lok": "Location",
        "col_seg": "Regional Segmentation",
        # Penjelasan Detail Potensi (The Why) EN
        "exp_title": "🔍 Regional Characteristics Analysis (Why is it Potential?)",
        "exp_why_high": "**Why Potential?** This area has a very high concentration of business entities (offices, clinics, cafes), especially in the economic centers of Bandung City and Cimahi.",
        "exp_act_high": "**Action:** Top priority for **Fiber Optic (FO)** infrastructure development. Focus on Dedicated internet services with high reliability.",
        "exp_why_med": "**Why Potential?** Transition zones or developing areas in Bandung Regency and city outskirts with a growing number of shops/MSMEs.",
        "exp_act_med": "**Action:** Focus on market penetration using competitive and flexible broadband business internet packages.",
        "exp_why_low": "**Why Less Potential?** The area is dominated by residential zones, open land, or commercial activities that are far apart (scattered).",
        "exp_act_low": "**Action:** Regular monitoring. Network infrastructure expansion is carried out only based on specific requests from communities or corporates."
    }
}

t = texts[lang]

# ==============================
# 1. LOAD DATASET
# ==============================


@st.cache_data
def load_data():
    # CARA ANTI GAGAL: Mencari file di folder 'data' relatif terhadap file kodingan ini
    base_path = os.path.dirname(
        __file__) if "__file__" in locals() else os.getcwd()
    file_path = os.path.join(base_path, "data", "dataset_dashboard.csv")
    # path = r"data\dataset_dashboard.csv"
    try:
        df = pd.read_csv(file_path)
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

    kategori_options = sorted(df_filtered["Kategori"].unique())
    selected_kategori = st.sidebar.multiselect(
        t["filter_3"], options=kategori_options)
    if selected_kategori:
        df_filtered = df_filtered[df_filtered["Kategori"].isin(
            selected_kategori)]

    # --- UPDATE DI BAGIAN FOOTER SIDEBAR ---
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: #9e9e9e; font-size: 0.8rem;'>
            Made with ❤️ by <b>Saujenhi</b><br>
            Information Systems '22<br>
            © 2026
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==============================
    # 3. JUDUL & KPI + DATA SUMMARY
    # ==============================
    st.title(t["title"])
    st.markdown(f"**{t['subtitle']}**")

    if lang == "ID":
        st.info(f"""
        **📊 Ringkasan Intelijen Data:** Sistem telah memproses **220.669 data mentah** lokasi bisnis dari Google Places API. 
        Melalui penyaringan (*cleaning*) yang ketat, telah diekstrak **140.175 titik bisnis valid** yang tersebar di wilayah **Kota Bandung, Kabupaten Bandung, dan Cimahi**. 
        Dashboard ini berfungsi sebagai panduan strategis untuk menentukan prioritas perluasan jaringan infrastruktur Fiber Optic secara tepat sasaran.
        """)
    else:
        st.info(f"""
        **📊 Data Intelligence Summary:** The system has processed **220,669 raw data points** from Google Places API. 
        Through rigorous cleaning, **140,175 valid business entities** have been extracted across **Bandung City, Bandung Regency, and Cimahi**. 
        This dashboard serves as a strategic guide to prioritize Fiber Optic infrastructure expansion accurately.
        """)

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
    # 4. VISUALISASI INTERAKTIF
    # ==============================
    col_donut, col_segmen, col_kategori = st.columns([1, 1.1, 1.2])

    count_segmen = df_filtered["Display_Segmen"].value_counts().reset_index()
    count_segmen.columns = ["Segmen", "Jumlah"]

    warna_diskrit = {t["high"]: '#FF8C00',
                     t["med"]: '#FFD700', t["low"]: '#808080'}

    with col_donut:
        st.subheader(t["chart_donut"])
        fig_donut = px.pie(count_segmen, names="Segmen", values="Jumlah", hole=0.5,
                           color="Segmen", color_discrete_map=warna_diskrit, height=350)
        fig_donut.update_traces(textposition='inside', textinfo='percent')
        fig_donut.update_layout(showlegend=False)
        click_donut = st.plotly_chart(
            fig_donut, on_select="rerun", selection_mode="points", use_container_width=True)

        if click_donut and "selection" in click_donut:
            pts_donut = click_donut["selection"]["points"]
            if pts_donut:
                try:
                    val_donut = pts_donut[0].get(
                        "label") or count_segmen.iloc[pts_donut[0].get("point_indices")[0]]["Segmen"]
                    df_filtered = df_filtered[df_filtered["Display_Segmen"] == val_donut]
                except:
                    pass

    with col_segmen:
        st.subheader(t["chart_bar"])
        fig_segmen = px.bar(count_segmen, x="Segmen", y="Jumlah", color="Segmen",
                            color_discrete_map=warna_diskrit, text_auto=True, height=350)
        click_seg = st.plotly_chart(
            fig_segmen, on_select="rerun", selection_mode="points", use_container_width=True)
        if click_seg and "selection" in click_seg:
            pts = click_seg["selection"]["points"]
            if pts:
                df_filtered = df_filtered[df_filtered["Display_Segmen"]
                                          == pts[0]["x"]]

    with col_kategori:
        st.subheader(t["chart_top10"])
        top_10 = df_filtered["Kategori"].value_counts().head(10).reset_index()
        top_10.columns = ["Kategori", "Total"]
        fig_kat = px.bar(top_10, x="Kategori", y="Total", text_auto=True,
                         height=350, color_discrete_sequence=['#3366CC'])
        click_kat = st.plotly_chart(
            fig_kat, on_select="rerun", selection_mode="points", use_container_width=True)
        if click_kat and "selection" in click_kat:
            pts_kat = click_kat["selection"]["points"]
            if pts_kat:
                df_filtered = df_filtered[df_filtered["Kategori"]
                                          == pts_kat[0]["x"]]

    # ==============================
    # 5. STRATEGI & INSIGHT WILAYAH (THE WHY - UPDATED TO SUPPORT EN)
    # ==============================
    st.subheader(t["strategy_header"])

    with st.expander(t["exp_title"]):
        ins_col1, ins_col2, ins_col3 = st.columns(3)
        with ins_col1:
            st.markdown(f"### 🟠 {t['high']}")
            st.write(t["exp_why_high"])
            st.write(t["exp_act_high"])
        with ins_col2:
            st.markdown(f"### 🟡 {t['med']}")
            st.write(t["exp_why_med"])
            st.write(t["exp_act_med"])
        with ins_col3:
            st.markdown(f"### ⚪ {t['low']}")
            st.write(t["exp_why_low"])
            st.write(t["exp_act_low"])

    # Logika Tampilan Strategi Berdasarkan Filter
    current_segmen = df_filtered["Segmentasi Wilayah"].unique()
    top_kat = df_filtered["Kategori"].value_counts(
    ).idxmax() if not df_filtered.empty else "-"

    if len(current_segmen) == 1:
        seg_nama = current_segmen[0]
        if seg_nama == "Potensi Tinggi":
            st.success(
                f"### {'Market Penetration Strategy' if lang == 'EN' else 'Strategi Penetrasi Pasar'}: {t['high']}")
            if lang == "ID":
                st.markdown(
                    f"* **Analisis:** Dominasi sektor **{top_kat}** menunjukkan kebutuhan infrastruktur internet kapasitas tinggi dan reliabilitas maksimal.\n* **Rekomendasi Produk:** Dedicated Internet Business (SLA 99.9%).\n* **Strategi Sales:** Prioritas Utama - Direct Sales & Mass Canvassing.")
            else:
                st.markdown(
                    f"* **Analysis:** Dominance of the **{top_kat}** sector indicates a need for high-capacity internet infrastructure with maximum reliability.\n* **Product Recommendation:** Dedicated Internet Business (99.9% SLA).\n* **Sales Strategy:** Top Priority - Direct Sales & Mass Canvassing.")
        elif seg_nama == "Potensi Sedang":
            st.warning(
                f"### {'Market Development Focus' if lang == 'EN' else 'Fokus Pengembangan Pasar'}: {t['med']}")
            if lang == "ID":
                st.markdown(
                    f"* **Analisis:** Kepadatan moderat pada sektor **{top_kat}** memerlukan pendekatan layanan yang fleksibel dan kompetitif.\n* **Rekomendasi Produk:** Broadband Business / Fiber to the Home (FTTH).\n* **Strategi Sales:** Telemarketing & Re-targeted Email Marketing.")
            else:
                st.markdown(
                    f"* **Analysis:** Moderate density in the **{top_kat}** sector requires a flexible and competitive service approach.\n* **Product Recommendation:** Broadband Business / Fiber to the Home (FTTH).\n* **Sales Strategy:** Telemarketing & Re-targeted Email Marketing.")
        else:
            st.info(
                f"### {'Brand Awareness Priority' if lang == 'EN' else 'Prioritas Kesadaran Merek'}: {t['low']}")
            if lang == "ID":
                st.markdown(f"* **Analisis:** Sebaran usaha yang rendah mengindikasikan pasar yang baru tumbuh (*nascent market*).\n* **Rekomendasi Produk:** Paket SOHO / Solusi Nirkabel Hemat Biaya.\n* **Strategi Penjualan:** Iklan Media Sosial Tertarget & Sosialisasi Komunitas Lokal.")
            else:
                st.markdown(f"* **Analysis:** Sparse business distribution indicates a nascent or emerging market.\n* **Product Recommendation:** SOHO Pack / Cost-Effective Wireless Solutions.\n* **Sales Strategy:** Targeted Social Media Ads & Local Community Awareness.")
    else:
        st.info(t["tips"])

    st.divider()

    # ==============================
    # 6. PETA & TABEL
    # ==============================
    st.subheader(t["map_header"])
    if not df_filtered.empty:
        df_map = df_filtered.groupby(["Latitude", "Longitude"]).agg({
            "Display_Segmen": "first", "Nama Usaha": "count", "Lokasi": "first"
        }).reset_index().rename(columns={"Nama Usaha": "Total"})
        m = folium.Map(location=[df_map["Latitude"].mean(
        ), df_map["Longitude"].mean()], zoom_start=11)
        legend_html = f'''{{% macro html(this, kwargs) %}}<div style="position: fixed; bottom: 30px; left: 30px; width: 170px; height: 95px; background-color: white; border:2px solid grey; z-index:9999; font-size:12px; padding: 10px; border-radius: 5px;"><b>Legenda Potensi:</b><br><i class="fa fa-circle" style="color:#FF8C00"></i> {t['high']}<br><i class="fa fa-circle" style="color:#FFD700"></i> {t['med']}<br><i class="fa fa-circle" style="color:#808080"></i> {t['low']}</div>{{% endmacro %}}'''
        legend = MacroElement()
        legend._template = Template(legend_html)
        m.get_root().add_child(legend)
        warna_map = {t["high"]: "#FF8C00", t["med"]                     : "#FFD700", t["low"]: "#808080"}
        for _, row in df_map.iterrows():
            folium.CircleMarker(location=[row["Latitude"], row["Longitude"]], radius=7, color=warna_map.get(row["Display_Segmen"], "blue"), fill=True, fill_opacity=0.6,
                                popup=f"<b>{row['Lokasi']}</b><br>Segmen: {row['Display_Segmen']}<br>Total Titik: {row['Total']}").add_to(m)
        st_folium(m, width=1400, height=500)

    st.divider()
    st.subheader(t["table_header"])
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(f"📥 Download (CSV)", data=csv,
                       file_name='data_potensi_qwords_bandung.csv', mime='text/csv')
    df_temp = df_filtered[["Nama Usaha", "Kategori",
                           "Lokasi", "Kota/Kab", "Display_Segmen"]].copy()
    df_temp.columns = [t["col_usaha"], t["col_kat"],
                       t["col_lok"], "Kota/Kab", t["col_seg"]]
    st.dataframe(df_temp, use_container_width=True, height=400)

    # # --- ATAU JIKA INGIN DI TENAH BAWAH(Hapus salah satu) - --
    # st.markdown("---")
    # st.markdown("<p style='text-align: center; color: grey;'>Made with ❤️ by Saujenhi | Information Systems '22 | © 2026</p>", unsafe_allow_html=True)

else:
    st.error(
        "Dataset tidak ditemukan. Pastikan file CSV tersedia di path yang ditentukan.")
