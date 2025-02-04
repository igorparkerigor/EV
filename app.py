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
    sarj_yuzdesi = st.sidebar.number_input("Şarj Yüzdesi (%)", min_value=1, max_value=100, step=1)
    ekle = st.sidebar.button("Veriyi Ekle")
    
    if "veriler" not in st.session_state:
        st.session_state.veriler = []
    
    if ekle and tarih and tuketim > 0 and maliyet > 0 and lokasyon and sarj_yuzdesi:
        st.session_state.veriler.append({
            "Tarih": tarih, 
            "Tüketim (kWh)": tuketim, 
            "Maliyet (₺)": maliyet, 
            "Lokasyon": lokasyon,
            "Şarj Yüzdesi (%)": sarj_yuzdesi
        })
        st.rerun()
    
    if st.session_state.veriler:
        df = pd.DataFrame(st.session_state.veriler)
        
        # Verileri gizleme/gösterme butonu
        if "show_data" not in st.session_state:
            st.session_state.show_data = True
        
        if st.button("Girilen Verileri Göster/Gizle"):
            st.session_state.show_data = not st.session_state.show_data
        
        if st.session_state.show_data:
            st.write("### Girilen Veriler")
            st.dataframe(df)
        
        # Özet Bilgiler (Aylık Bazda)
        df["Ay"] = df["Tarih"].apply(lambda x: x.strftime('%Y-%m'))
        aylik_ozet = df.groupby("Ay").agg({
            "Maliyet (₺)": "sum",
            "Tüketim (kWh)": "sum",
            "Şarj Yüzdesi (%)": lambda x: x.sum() / 100
        }).reset_index()
        
        # Ortalama maliyet/kWh hesaplama (aylık toplam maliyet / toplam tüketim)
        aylik_ozet["Ortalama Maliyet/kWh (₺)"] = aylik_ozet["Maliyet (₺)"] / aylik_ozet["Tüketim (kWh)"]
        
        # Genel toplam hesaplama
        toplam_maliyet = aylik_ozet["Maliyet (₺)"].sum()
        toplam_tuketim = aylik_ozet["Tüketim (kWh)"].sum()
        toplam_sarj_dongusu = aylik_ozet["Şarj Yüzdesi (%)"].sum()
        
        # Tüm ayların toplam maliyetini toplam tüketime bölerek ortalama maliyet/kWh hesaplama
        ortalama_maliyet_kwh = toplam_maliyet / toplam_tuketim if toplam_tuketim > 0 else 0
        
        # Toplam satırını ekleme
        toplam_satir = pd.DataFrame({
            "Ay": ["Toplam"],
            "Maliyet (₺)": [toplam_maliyet],
            "Tüketim (kWh)": [toplam_tuketim],
            "Şarj Yüzdesi (%)": [toplam_sarj_dongusu],
            "Ortalama Maliyet/kWh (₺)": [ortalama_maliyet_kwh]
        })
        
        aylik_ozet = pd.concat([aylik_ozet, toplam_satir], ignore_index=True)
        
        st.write("### Aylık Özet Bilgiler")
        st.dataframe(aylik_ozet.rename(columns={
            "Maliyet (₺)": "Toplam Maliyet (₺)",
            "Tüketim (kWh)": "Toplam Tüketim (kWh)",
            "Şarj Yüzdesi (%)": "Toplam Şarj Döngüsü"
        }))
        
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
        
        # Veri Düzenleme ve Silme
        st.write("### Veri Düzenleme/Silme")
        index_to_edit = st.number_input("Düzenlemek veya silmek istediğiniz verinin indeksini girin", min_value=0, max_value=len(df)-1, step=1)
        
        if st.button("Veriyi Sil"):
            del st.session_state.veriler[index_to_edit]
            st.rerun()
        
        with st.expander("Veriyi Düzenle"):
            veri = st.session_state.veriler[index_to_edit]
            tarih_yeni = st.date_input("Yeni Tarih", value=veri["Tarih"])
            tuketim_yeni = st.number_input("Yeni Tüketim (kWh)", value=veri["Tüketim (kWh)"], min_value=0.0, step=0.1)
            maliyet_yeni = st.number_input("Yeni Maliyet (₺)", value=veri["Maliyet (₺)"], min_value=0.0, step=0.1)
            lokasyon_yeni = st.text_input("Yeni Lokasyon", value=veri["Lokasyon"])
            sarj_yuzdesi_yeni = st.number_input("Yeni Şarj Yüzdesi (%)", value=veri["Şarj Yüzdesi (%)"], min_value=1, max_value=100, step=1)
            
            if st.button("Kaydet"):
                st.session_state.veriler[index_to_edit] = {
                    "Tarih": tarih_yeni,
                    "Tüketim (kWh)": tuketim_yeni,
                    "Maliyet (₺)": maliyet_yeni,
                    "Lokasyon": lokasyon_yeni,
                    "Şarj Yüzdesi (%)": sarj_yuzdesi_yeni
                }
                st.rerun()

if __name__ == "__main__":
    main()
