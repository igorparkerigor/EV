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
        df["Maliyet/kWh"] = df["Maliyet (₺)"] / df["Tüketim (kWh)"]
        
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
            "Maliyet/kWh": "mean",
            "Şarj Yüzdesi (%)": lambda x: x.sum() / 100
        }).reset_index()
        
        # Toplam ve ortalama ekleme
        toplam_maliyet = aylik_ozet["Maliyet (₺)"].sum()
        toplam_sarj_dongusu = aylik_ozet["Şarj Yüzdesi (%)"].sum()
        ortalama_maliyet_kwh = aylik_ozet["Maliyet/kWh"].mean()
        
        aylik_ozet = aylik_ozet.append({
            "Ay": "Toplam",
            "Maliyet (₺)": toplam_maliyet,
            "Maliyet/kWh": ortalama_maliyet_kwh,
            "Şarj Yüzdesi (%)": toplam_sarj_dongusu
        }, ignore_index=True)
        
        st.write("### Aylık Özet Bilgiler")
        st.dataframe(aylik_ozet.rename(columns={
            "Maliyet (₺)": "Toplam Maliyet (₺)",
            "Maliyet/kWh": "Ortalama Maliyet/kWh (₺)",
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
            tarih_yeni = st.date_input("Yeni Tarih", value=st.session_state.veriler[index_to_edit]["Tarih"])
            tuketim_yeni = st.number_input("Yeni Tüketim (kWh)", value=st.session_state.veriler[index_to_edit]["Tüketim (kWh)"], min_value=0.0, step=0.1)
            maliyet_yeni = st.number_input("Yeni Maliyet (₺)", value=st.session_state.veriler[index_to_edit]["Maliyet (₺)"], min_value=0.0, step=0.1)
            lokasyon_yeni = st.text_input("Yeni Lokasyon", value=st.session_state.veriler[index_to_edit]["Lokasyon"])
            sarj_yuzdesi_yeni = st.number_input("Yeni Şarj Yüzdesi (%)", value=st.session_state.veriler[index_to_edit]["Şarj Yüzdesi (%)"], min_value=1, max_value=100, step=1)
            
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
