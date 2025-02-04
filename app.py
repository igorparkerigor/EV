import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def google_sheets_connect():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("EV_Sarj_Verileri").sheet1
    return sheet

def load_data():
    sheet = google_sheets_connect()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_data(df):
    sheet = google_sheets_connect()
    sheet.clear()
    sheet.append_row(df.columns.tolist())
    for row in df.values.tolist():
        sheet.append_row(row)

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
    
    df = load_data()
    
    if ekle and tarih and tuketim > 0 and maliyet > 0 and lokasyon and sarj_yuzdesi:
        new_data = {"Tarih": tarih, "Tüketim (kWh)": tuketim, "Maliyet (₺)": maliyet, "Lokasyon": lokasyon, "Şarj Yüzdesi (%)": sarj_yuzdesi}
        df = df.append(new_data, ignore_index=True)
        save_data(df)
        st.rerun()
    
    if not df.empty:
        df["Maliyet/kWh"] = df["Maliyet (₺)"] / df["Tüketim (kWh)"]
        
        if "show_data" not in st.session_state:
            st.session_state.show_data = True
        
        if st.button("Girilen Verileri Göster/Gizle"):
            st.session_state.show_data = not st.session_state.show_data
        
        if st.session_state.show_data:
            st.write("### Girilen Veriler")
            st.dataframe(df)
        
        df["Ay"] = pd.to_datetime(df["Tarih"]).dt.strftime('%Y-%m')
        aylik_ozet = df.groupby("Ay").agg({
            "Maliyet (₺)": "sum",
            "Tüketim (kWh)": "sum",
            "Şarj Yüzdesi (%)": lambda x: x.sum() / 100
        }).reset_index()
        
        aylik_ozet["Maliyet/kWh"] = aylik_ozet["Maliyet (₺)"] / aylik_ozet["Tüketim (kWh)"]
        
        toplam_maliyet = aylik_ozet["Maliyet (₺)"].sum()
        toplam_tuketim = aylik_ozet["Tüketim (kWh)"].sum()
        toplam_sarj_dongusu = aylik_ozet["Şarj Yüzdesi (%)"].sum()
        toplam_ortalama_maliyet_kwh = toplam_maliyet / toplam_tuketim if toplam_tuketim > 0 else 0
        
        toplam_satir = pd.DataFrame({
            "Ay": ["Toplam"],
            "Maliyet (₺)": [toplam_maliyet],
            "Tüketim (kWh)": [toplam_tuketim],
            "Maliyet/kWh": [toplam_ortalama_maliyet_kwh],
            "Şarj Yüzdesi (%)": [toplam_sarj_dongusu]
        })
        
        aylik_ozet = pd.concat([aylik_ozet, toplam_satir], ignore_index=True)
        
        st.write("### Aylık Özet Bilgiler")
        st.dataframe(aylik_ozet.rename(columns={
            "Maliyet (₺)": "Toplam Maliyet (₺)",
            "Tüketim (kWh)": "Toplam Tüketim (kWh)",
            "Maliyet/kWh": "Ortalama Maliyet/kWh (₺)",
            "Şarj Yüzdesi (%)": "Toplam Şarj Döngüsü"
        }))
        
        # Grafik Seçimi
        grafik_tipi = st.selectbox("Grafik Tipi Seçin", ["Çubuk Grafik", "Pasta Grafik"])
        
        fig, ax = plt.subplots()
        if grafik_tipi == "Çubuk Grafik":
            df.plot(x="Tarih", y="Tüketim (kWh)", kind="bar", ax=ax, color="skyblue")
            ax.set_ylabel("Tüketim (kWh)")
        else:
            df_grouped = df.groupby("Lokasyon")["Tüketim (kWh)"].sum().reset_index()
            ax.pie(df_grouped["Tüketim (kWh)"], labels=df_grouped["Lokasyon"], autopct='%1.1f%%', colors=["skyblue", "lightcoral", "lightgreen", "orange"])
        
        st.pyplot(fig)
        
        # Veri Silme
        index_to_delete = st.number_input("Silmek istediğiniz verinin indeksini girin", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Veriyi Sil"):
            df.drop(index_to_delete, inplace=True)
            save_data(df)
            st.rerun()

if __name__ == "__main__":
    main()
