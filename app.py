import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Başlık
st.title("Elektrikli Araç Şarj Takibi")

# Veri saklama (geçici olarak session state içinde tutuluyor)
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=["Tarih", "Şarj Yüzdesi", "Enerji Miktarı (kWh)", "Ücret (₺)", "Konum"])

# Veri girişi
st.subheader("Şarj Verisi Girişi")
with st.form("data_entry"):
    tarih = st.date_input("Tarih")
    sarj_yuzdesi = st.number_input("Şarj Yüzdesi (%)", min_value=1, max_value=100, step=1)
    enerji_miktari = st.number_input("Enerji Miktarı (kWh)", min_value=0.1, step=0.1)
    ucret = st.number_input("Ücret (₺)", min_value=0.0, step=0.1)
    konum = st.text_input("Konum")
    ekle = st.form_submit_button("Ekle")
    
    if ekle:
        yeni_veri = pd.DataFrame([[tarih, sarj_yuzdesi, enerji_miktari, ucret, konum]], 
                                 columns=["Tarih", "Şarj Yüzdesi", "Enerji Miktarı (kWh)", "Ücret (₺)", "Konum"])
        st.session_state["data"] = pd.concat([st.session_state["data"], yeni_veri], ignore_index=True)
        st.success("Veri eklendi!")

# Kayıtlı verileri göster
st.subheader("Şarj Verileri")
data = st.session_state["data"]
st.dataframe(data)

# Veri silme
if not data.empty:
    silinecek_index = st.number_input("Silmek istediğiniz satır numarası", min_value=0, max_value=len(data)-1, step=1)
    if st.button("Seçili Veriyi Sil"):
        st.session_state["data"] = data.drop(index=silinecek_index).reset_index(drop=True)
        st.success("Veri silindi!")

# İstatistiksel analiz
st.subheader("Aylık İstatistikler")
if not data.empty:
    data["Tarih"] = pd.to_datetime(data["Tarih"])
    data["Ay"] = data["Tarih"].dt.strftime("%Y-%m")
    aylik_veri = data.groupby("Ay").agg({
        "Enerji Miktarı (kWh)": "sum",
        "Ücret (₺)": "sum",
        "Şarj Yüzdesi": "sum"
    }).reset_index()
    aylik_veri["Ortalama Maliyet (₺/kWh)"] = aylik_veri["Ücret (₺)"] / aylik_veri["Enerji Miktarı (kWh)"]
    aylik_veri["Şarj Döngüsü"] = aylik_veri["Şarj Yüzdesi"] / 100
    st.dataframe(aylik_veri)

    # Pasta grafiği - Ay bazında toplam maliyet dağılımı
    fig_pie = px.pie(aylik_veri, values="Ücret (₺)", names="Ay", title="Aylık Maliyet Dağılımı")
    st.plotly_chart(fig_pie)
    
    # Çubuk grafiği - Ay bazında enerji tüketimi, maliyet ve şarj döngüsü
    fig_bar = px.bar(aylik_veri, x="Ay", y=["Ücret (₺)", "Ortalama Maliyet (₺/kWh)", "Şarj Döngüsü"], 
                     title="Aylık Karşılaştırmalar", barmode="group")
    st.plotly_chart(fig_bar)
    
    # Genel toplamlar
    toplam_maliyet = aylik_veri["Ücret (₺)"].sum()
    toplam_ortalama_maliyet = aylik_veri["Ortalama Maliyet (₺/kWh)"].mean()
    toplam_sarj_dongusu = aylik_veri["Şarj Döngüsü"].sum()
    st.metric("Tüm Zamanların Toplam Maliyeti", f"{toplam_maliyet:.2f} ₺")
    st.metric("Tüm Zamanların Ortalama Maliyeti", f"{toplam_ortalama_maliyet:.2f} ₺/kWh")
    st.metric("Toplam Şarj Döngüsü", f"{toplam_sarj_dongusu:.2f}")
