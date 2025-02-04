import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("Elektrikli Araç Şarj Takibi")
    
    # Kullanıcıdan manuel veri girişi
    st.sidebar.header("Şarj Verilerini Girin")
    tarih = st.sidebar.date_input("Tarih")
    tuketim = st.sidebar.number_input("Tüketim (kWh)", min_value=0.0, step=0.1)
    maliyet = st.sidebar.number_input("Maliyet (₺)", min_value=0.0, step=0.1)
    lokasyon = st.sidebar.text_input("Lokasyon")
    ekle = st.sidebar.button("Veriyi Ekle")
    
    if "veriler" not in st.session_state:
        st.session_state.veriler = []
    
    if ekle and tarih and tuketim > 0 and maliyet > 0 and lokasyon:
        st.session_state.veriler.append({"Tarih": tarih, "Tüketim (kWh)": tuketim, "Maliyet (₺)": maliyet, "Lokasyon": lokasyon})
    
    if st.session_state.veriler:
        df = pd.DataFrame(st.session_state.veriler)
        st.write("### Girilen Veriler")
        st.dataframe(df)
        
        # Özet Bilgiler
        toplam_maliyet = df["Maliyet (₺)"].sum()
        ortalama_maliyet = df["Maliyet (₺)"].mean()
        toplam_sarj = df.shape[0]
        
        st.write("### Özet Bilgiler")
        st.write(f"Toplam Maliyet: {toplam_maliyet:.2f} ₺")
        st.write(f"Ortalama Maliyet: {ortalama_maliyet:.2f} ₺")
        st.write(f"Toplam Şarj Döngüsü: {toplam_sarj}")
        
        # Grafik Seçimi
        grafik_tipi = st.selectbox("Grafik Tipi Seçin", ["Çubuk Grafik", "Pasta Grafik"])
        
        # Grafik Çizimi
        fig, ax = plt.subplots()
        if grafik_tipi == "Çubuk Grafik":
            df.plot(x="Tarih", y="Tüketim (kWh)", kind="bar", ax=ax, color="skyblue")
            ax.set_ylabel("Tüketim (kWh)")
        else:
            df_grouped = df.groupby("Lokasyon")["Tüketim (kWh)"].sum().reset_index()
            ax.pie(df_grouped["Tüketim (kWh)"], labels=df_grouped["Lokasyon"], autopct='%1.1f%%', colors=["skyblue", "lightcoral", "lightgreen", "orange"])
        
        st.pyplot(fig)

if __name__ == "__main__":
    main()
