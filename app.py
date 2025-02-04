import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Veritabanı bağlantısı
conn = sqlite3.connect("energy_data.db", check_same_thread=False)
c = conn.cursor()

# Tabloyu oluştur
c.execute('''CREATE TABLE IF NOT EXISTS charging_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                kwh REAL,
                cost REAL,
                location TEXT)''')
conn.commit()

# Başlık
st.title("Elektrikli Araç Şarj Takip Sistemi")

# Veri Girişi
st.header("Yeni Şarj Verisi Ekle")
date = st.date_input("Tarih")
kwh = st.number_input("Şarj edilen kWh", min_value=0.0, format="%.2f")
cost = st.number_input("Ödenen Tutar (₺)", min_value=0.0, format="%.2f")
location = st.text_input("Şarj Lokasyonu")

if st.button("Veriyi Kaydet"):
    c.execute("INSERT INTO charging_data (date, kwh, cost, location) VALUES (?, ?, ?, ?)",
              (date, kwh, cost, location))
    conn.commit()
    st.success("Veri başarıyla kaydedildi!")

# Veri Görüntüleme
st.header("Şarj Verileri")
df = pd.read_sql("SELECT * FROM charging_data", conn)
st.dataframe(df)

# Grafik Gösterimi
st.header("Şarj Tüketimi Grafikleri")
if not df.empty:
    fig_kwh = px.line(df, x='date', y='kwh', title='Zaman İçinde Şarj Edilen kWh')
    st.plotly_chart(fig_kwh)
    
    fig_cost = px.line(df, x='date', y='cost', title='Zaman İçinde Harcanan Tutar')
    st.plotly_chart(fig_cost)
else:
    st.warning("Grafikler için yeterli veri yok.")

# Bağlantıyı kapat
conn.close()
