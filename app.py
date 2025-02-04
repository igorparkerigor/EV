import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("Elektrikli Araç Şarj Takibi")
    
    # Kullanıcıdan manuel veri girişi
    st.sidebar.header("Şarj Verilerini Girin")
    tarih = st.sidebar.text_input("Tarih (YYYY-AA-GG)")
    tuketim = st.sidebar.number_input("Tüketim (kWh)", min_value=0.0, step=0.1)
    maliyet = st.sidebar.number_input("Maliyet (₺)", min_value=0.0, step=0.1)
    ekle = st.sidebar.button("Veriyi Ekle")
    
    if "veriler" not in st.session_state:
        st.session_state.veriler = []
    
    if ekle and tarih and tuketim > 0 and maliyet > 0:
        st.session_state.veriler.append({"Tarih": tarih, "Tüketim (kWh)": tuketim, "Maliyet (₺)": maliyet})
    
    if st.session_state.veriler:
        df = pd.DataFrame(st.session_state.veriler)
        st.write("### Girilen Veriler")
        st.dataframe(df)
        
        # Grafik Seçimi
        grafik_tipi = st.selectbox("Grafik Tipi Seçin", ["Çubuk Grafik", "Pasta Grafik"])
        
        # Grafik Çizimi
        fig, ax = plt.subplots()
        if grafik_tipi == "Çubuk Grafik":
            df.plot(x="Tarih", y="Tüketim (kWh)", kind="bar", ax=ax, color="skyblue")
            ax.set_ylabel("Tüketim (kWh)")
        else:
            ax.pie(df["Tüketim (kWh)"], labels=df["Tarih"], autopct='%1.1f%%', colors=["skyblue", "lightcoral", "lightgreen"])
        
        st.pyplot(fig)

if __name__ == "__main__":
    main()
