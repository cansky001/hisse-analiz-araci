import streamlit as st
import utils.data as data
import utils.indicators as indicators
import utils.ui as ui
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="ProTrade Analiz Terminali", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="📈"
)

# --- CSS YÜKLE ---
ui.load_custom_css()

# --- YAN PANEL ---
options = ui.render_sidebar()

# --- ANA KONTROLLER (HEADER) ---
st.title("ProTrade Analiz Terminali")
st.markdown("---")

col_head1, col_head2, col_head3 = st.columns([2, 1, 1])

with col_head1:
    raw_symbol = st.text_input("Hisse Sembolü", "THYAO", help="BIST hisseleri için sonuna .IS eklemenize gerek yoktur.")
    symbol = data.process_symbol(raw_symbol)
    
with col_head2:
    period = st.selectbox("Periyot", ["3mo", "6mo", "1y", "2y", "5y", "max"], index=1)
    
with col_head3:
    st.write("")
    st.write("")
    if st.button("Analiz Et"): 
        st.cache_data.clear()

if symbol != raw_symbol.upper():
    st.caption(f"İşlenen Sembol: **{symbol}**")

# --- VERİ ÇEKME & İŞLEME ---
with st.spinner(f"{symbol} verileri çekiliyor..."):
    df_full, financials, balance, info = data.fetch_stock_data(symbol, period="max")

if df_full is not None:
    # İndikatörleri Hesapla
    df_full = data.process_indicators(df_full)
    
    # Seçilen Periyoda Göre Dilimle
    df_view = data.slice_data_by_period(df_full, period)
    
    # Son Veriler
    last_close = df_view['Close'].iloc[-1]
    prev_close = df_view['Close'].iloc[-2]
    last_high = df_view['High'].iloc[-1]
    last_low = df_view['Low'].iloc[-1]
    
    # Değişim Hesabı
    change, pct_change = data.get_market_status(last_close, prev_close)
    
    # Pivot Hesabı
    pivot, r1, s1, r2, s2 = indicators.calculate_pivot_points(last_high, last_low, last_close)
    
    # Adil Değer
    fair_value = indicators.calculate_fair_value(info)

    # --- METRİKLER ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Son Fiyat", f"{last_close:.2f}", f"{pct_change:.2f}%")
    
    last_rsi = df_view['RSI'].iloc[-1]
    m2.metric("RSI (14)", f"{last_rsi:.2f}")
    
    trend_status = "YÜKSELİŞ 🚀" if last_close > df_view['EMA200'].iloc[-1] else "DÜŞÜŞ 🔻"
    m3.metric("Trend (EMA200)", trend_status)
    
    if fair_value:
        upside = ((fair_value - last_close) / last_close) * 100
        m4.metric("Adil Değer (Graham)", f"{fair_value:.2f}", f"{upside:.1f}% Potansiyel")
    else:
        m4.metric("Adil Değer", "Hesaplanamadı")

    # --- PİVOTLAR ---
    ui.render_pivot_points(pivot, r1, s1, r2, s2)
    
    # --- GRAFİK ve REHBER ---
    ui.render_guide()
    ui.render_chart(df_view, options)
    
    # --- TEMEL ANALİZ ÖZETİ ---
    st.markdown("---")
    st.subheader(f"📊 {symbol} Analiz Özeti")
    
    col_fund1, col_fund2 = st.columns(2)
    
    with col_fund1:
        st.markdown("#### 🏢 Bilanço ve Temel Durum")
        if balance is not None and not balance.empty:
            try:
                # Bilanço verileri bazen Karmaşık döner, güvenli erişim deniyoruz
                # yfinance yapısı zaman zaman değişebilir, bu yüzden esnek olmalıyız
                equity_row = balance.loc['Stockholders Equity'] if 'Stockholders Equity' in balance.index else None
                debt_row = balance.loc['Total Debt'] if 'Total Debt' in balance.index else None
                
                equity = equity_row.iloc[0] if equity_row is not None else 1
                debt = debt_row.iloc[0] if debt_row is not None else 0
                
                if equity and equity != 0:
                    debt_equity = debt / equity
                    st.metric("Borç / Özsermaye Oranı", f"{debt_equity:.2f}")
                    st.progress(min(debt_equity/3, 1.0))
                    
                    if debt_equity < 0.5: st.caption("✅ Şirketin borç yükü düşük, mali yapısı güçlü.")
                    elif debt_equity < 1.5: st.caption("⚠️ Şirketin borç yükü makul seviyede.")
                    else: st.caption("❌ Şirket yüksek borçla finanse ediliyor, riskli olabilir.")
                else:
                    st.info("Borç/Özsermaye oranı hesaplanamadı.")
            except Exception as e:
                st.warning(f"Bilanço verisi detaylandırılamadı: {e}")
        else:
            st.warning("Temel analiz verilerine ulaşılamadı.")

    with col_fund2:
        st.markdown("#### 🤖 Teknik Sinyaller")
        signals = []
        if last_rsi < 30: signals.append("🟢 RSI: Aşırı satım bölgesinde, tepki yükselişi gelebilir.")
        elif last_rsi > 70: signals.append("🔴 RSI: Aşırı alım bölgesinde, kar satışı gelebilir.")
        
        if last_close > df_view['EMA200'].iloc[-1]: signals.append("🟢 Trend: Uzun vadeli ortalamanın üzerinde (Pozitif).")
        else: signals.append("🔴 Trend: Uzun vadeli ortalamanın altında (Negatif).")
        
        macd = df_view['MACD'].iloc[-1]
        signal = df_view['MACD_Signal'].iloc[-1]
        if macd > signal: signals.append("🟢 MACD: Alıcılı seyir (Pozitif Kesişim).")
        else: signals.append("🔴 MACD: Satıcılı seyir (Negatif Kesişim).")
        
        if fair_value and last_close < fair_value:
             signals.append(f"💎 Değerleme: Hisse adil değerinin altında (%{upside:.1f} potansiyel).")

        if not signals:
            st.write("Belirgin bir teknik sinyal bulunmuyor, piyasa nötr.")
        else:
            for s in signals:
                st.write(f"- {s}")

else:
    st.info("Analiz yapmak için lütfen geçerli bir hisse senedi kodu girin.")
