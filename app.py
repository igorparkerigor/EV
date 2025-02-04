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
                charge_percentage INTEGER,
                kwh REAL,
                cost REAL,
                location TEXT)''')
conn.commit()

# Başlık
st.title("Elektrikli Araç Şarj Takip Sistemi")

# Veri Girişi
st.header("Yeni Şarj Verisi Ekle")
date = st.date_input("Tarih")
charge_percentage = st.number_input("Şarj Yüzdesi (%)", min_value=1, max_value=100, step=1)
kwh = st.number_input("Enerji Miktarı (kWh)", min_value=0.0, format="%.2f")
cost = st.number_input("Ödenen Tutar (₺)", min_value=0.0, format="%.2f")
location = st.text_input("Şarj Lokasyonu")

if st.button("Veriyi Kaydet"):
    c.execute("INSERT INTO charging_data (date, charge_percentage, kwh, cost, location) VALUES (?, ?, ?, ?, ?)",
              (date, charge_percentage, kwh, cost, location))
    conn.commit()
    st.success("Veri başarıyla kaydedildi!")

# Veri Güncelleme ve Silme
st.header("Şarj Verilerini Yönet")
df = pd.read_sql("SELECT * FROM charging_data", conn)

if not df.empty:
    selected_id = st.selectbox("Silmek veya düzenlemek istediğiniz kaydı seçin", df["id"].tolist())
    if st.button("Veriyi Sil"):
        c.execute("DELETE FROM charging_data WHERE id = ?", (selected_id,))
        conn.commit()
        st.success("Veri silindi!")
        st.experimental_rerun()
    
    # Güncelleme işlemi
    edit_date = st.date_input("Yeni Tarih", df[df["id"] == selected_id]["date"].values[0])
    edit_charge = st.number_input("Yeni Şarj Yüzdesi (%)", min_value=1, max_value=100, step=1,
                                  value=df[df["id"] == selected_id]["charge_percentage"].values[0])
    edit_kwh = st.number_input("Yeni Enerji Miktarı (kWh)", min_value=0.0, format="%.2f",
                               value=df[df["id"] == selected_id]["kwh"].values[0])
    edit_cost = st.number_input("Yeni Ödenen Tutar (₺)", min_value=0.0, format="%.2f",
                                value=df[df["id"] == selected_id]["cost"].values[0])
    edit_location = st.text_input("Yeni Şarj Lokasyonu", df[df["id"] == selected_id]["location"].values[0])

    if st.button("Veriyi Güncelle"):
        c.execute("UPDATE charging_data SET date = ?, charge_percentage = ?, kwh = ?, cost = ?, location = ? WHERE id = ?",
                  (edit_date, edit_charge, edit_kwh, edit_cost, edit_location, selected_id))
        conn.commit()
        st.success("Veri güncellendi!")
        st.experimental_rerun()

# Aylık İstatistikler
st.header("Aylık Şarj İstatistikleri")
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.strftime("%Y-%m")
monthly_stats = df.groupby("month").agg({
    "cost": "sum",
    "kwh": "sum",
    "charge_percentage": "sum"
}).reset_index()
monthly_stats["average_cost"] = monthly_stats["cost"] / monthly_stats["kwh"]
monthly_stats["charge_cycles"] = monthly_stats["charge_percentage"] / 100

st.dataframe(monthly_stats[["month", "cost", "average_cost", "charge_cycles"]].rename(
    columns={"month": "Ay", "cost": "Toplam Maliyet (₺)", "average_cost": "Ortalama Maliyet (₺/kWh)", "charge_cycles": "Şarj Döngüsü"}))

# Toplam Veriler
st.subheader("Genel Toplam")
total_cost = monthly_stats["cost"].sum()
total_kwh = monthly_stats["kwh"].sum()
total_cycles = monthly_stats["charge_cycles"].sum()
total_avg_cost = total_cost / total_kwh if total_kwh != 0 else 0

st.write(f"**Toplam Harcama:** {total_cost:.2f} ₺")
st.write(f"**Genel Ortalama Maliyet:** {total_avg_cost:.2f} ₺/kWh")
st.write(f"**Toplam Şarj Döngüsü:** {total_cycles:.2f}")

# Bağlantıyı kapat
conn.close()
