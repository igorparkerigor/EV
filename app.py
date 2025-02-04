import streamlit as st
import pandas as pd
import plotly.express as px

# Başlık
st.title("Elektrikli Araç Şarj İstatistikleri")

# Kullanıcının veri yükleyebilmesi için bir dosya yükleme alanı
dosya = st.file_uploader("Şarj verilerini içeren CSV dosyanızı yükleyin", type=["csv"])

if dosya is not None:
    # CSV dosyasını pandas ile oku
    data = pd.read_csv(dosya)
    
    # "Tarih" sütununun formatını düzelt
    if "Tarih" in data.columns:
        data["Tarih"] = pd.to_datetime(data["Tarih"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    # Sayısal sütunları uygun veri türlerine çevir
    sayisal_sutunlar = ["Ücret (₺)", "Ortalama Maliyet (₺/kWh)", "Şarj Döngüsü"]
    for sutun in sayisal_sutunlar:
        if sutun in data.columns:
            data[sutun] = pd.to_numeric(data[sutun], errors="coerce")
    
    # Kullanıcıya veriyi göster
    st.subheader("Yüklenen Veriler")
    st.dataframe(data)
    
    # Aylık toplam maliyet, ortalama maliyet ve şarj döngüsü hesaplama
    data["Tarih"] = pd.to_datetime(data["Tarih"], errors="coerce")
    data["Yıl-Ay"] = data["Tarih"].dt.to_period("M")
    
    aylik_veri = data.groupby("Yıl-Ay").agg({
        "Ücret (₺)": "sum", 
        "Ortalama Maliyet (₺/kWh)": "mean", 
        "Şarj Döngüsü": "count"
    }).reset_index()
    
    aylik_veri["Yıl-Ay"] = aylik_veri["Yıl-Ay"].astype(str)
    
    # Kullanıcıya aylık istatistikleri göster
    st.subheader("Aylık Şarj İstatistikleri")
    st.dataframe(aylik_veri)
    
    # Kullanıcıya grafik türü seçtirme
    grafik_turu = st.selectbox("Grafik Türü Seçin", ["Çubuk Grafik", "Pasta Grafiği"])
    
    if grafik_turu == "Çubuk Grafik":
        fig = px.bar(
            aylik_veri, x="Yıl-Ay", y="Ücret (₺)", 
            title="Aylık Toplam Şarj Maliyetleri", 
            labels={"Yıl-Ay": "Ay", "Ücret (₺)": "Toplam Maliyet (₺)"},
            text_auto=True, color_discrete_sequence=["#636EFA"]
        )
    else:
        fig = px.pie(
            aylik_veri, values="Ücret (₺)", names="Yıl-Ay", 
            title="Aylık Maliyet Dağılımı", 
            color_discrete_sequence=px.colors.sequential.Blues
        )
    
    st.plotly_chart(fig)
