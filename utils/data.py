import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from scipy.signal import argrelextrema
from datetime import timedelta
import streamlit as st

@st.cache_data(ttl=3600)  # Verileri 1 saat önbelleğe al
def fetch_stock_data(ticker, period="max"):
    """
    Belirtilen hisse senedi için geçmiş verileri ve temel finansal bilgileri çeker.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None, None, None, None
            
        # MultiIndex sütun yapısını düzelt (yfinance bazen böyle döner)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df, stock.financials, stock.balance_sheet, stock.info
    except Exception as e:
        print(f"Hata: {e}")
        return None, None, None, None

def process_indicators(df):
    """
    DataFrame'e teknik analiz indikatörlerini ekler.
    """
    if df is None or df.empty:
        return df
        
    try:
        # 1. Hareketli Ortalamalar
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['EMA50'] = ta.ema(df['Close'], length=50)
        df['EMA200'] = ta.ema(df['Close'], length=200)
        
        # 2. Momentum (RSI & Stoch RSI)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        stoch = ta.stochrsi(df['Close'], length=14, rsi_length=14, k=3, d=3)
        if stoch is not None:
            df = pd.concat([df, stoch], axis=1)
        
        # 3. MACD
        k = df['Close'].ewm(span=12, adjust=False, min_periods=12).mean()
        d = df['Close'].ewm(span=26, adjust=False, min_periods=26).mean()
        df['MACD'] = k - d
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False, min_periods=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # 4. Bollinger Bantları
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
            # Sütun isimlerini standartlaştır
            cols_map = {c: c.replace('BBL_20_2.0', 'BB_Lower').replace('BBU_20_2.0', 'BB_Upper').replace('BBM_20_2.0', 'BB_Mid') for c in df.columns if 'BB' in c}
            # Basit rename işlemi, kütüphane versiyonuna göre isimler değişebilir, bu yüzden garantiye alalım
            df.rename(columns=lambda x: x.replace('BBL_20_2.0', 'BB_Lower').replace('BBU_20_2.0', 'BB_Upper'), inplace=True)

        # 5. ATR ve Trailing Stop
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['Trailing_Stop'] = df['Close'] - (df['ATR'] * 2)
        
        # 6. Parabolic SAR
        psar = ta.psar(df['High'], df['Low'], df['Close'])
        if psar is not None:
             df = pd.concat([df, psar], axis=1)

        # 7. SuperTrend
        supertrend = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3.0)
        if supertrend is not None:
            df = pd.concat([df, supertrend], axis=1)
            
        # 8. Hacim EMA
        df['Vol_EMA'] = ta.ema(df['Volume'], length=20)
        
        # 9. Swing Points (Tepe/Dip)
        n = 8
        df['min'] = df.iloc[argrelextrema(df.Close.values, np.less_equal, order=n)[0]]['Close']
        df['max'] = df.iloc[argrelextrema(df.Close.values, np.greater_equal, order=n)[0]]['Close']
        
        return df
    except Exception as e:
        st.error(f"İndikatör hesaplama hatası: {e}")
        return df

def process_symbol(input_symbol):
    """
    Girilen sembolü BIST formatına veya global formata uygun hale getirir.
    """
    if not input_symbol: return "THYAO.IS"
    s = input_symbol.upper().strip()
    if s.endswith(".IS") or "-" in s:
        return s
    # BIST hisseleri genelde 5 karakterden kısa ve rakam içermez (istisnalar olabilir ama genel kural)
    if len(s) <= 5 and not any(char.isdigit() for char in s):
         return f"{s}.IS"
    return s

def slice_data_by_period(df, period_str):
    """
    Veriyi seçilen periyoda göre filtreler.
    """
    days_map = {"3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825}
    if period_str not in days_map: return df
    if df.empty: return df
    start_date = df.index[-1] - timedelta(days=days_map[period_str])
    return df[df.index >= start_date]

def get_market_status(current_price, previous_close):
    change = current_price - previous_close
    pct_change = (change / previous_close) * 100
    return change, pct_change
