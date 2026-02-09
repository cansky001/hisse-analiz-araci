import numpy as np

def calculate_fibonacci(df):
    """Fibonacci düzeltme seviyelerini hesaplar."""
    if df.empty: return {}
    max_price = df['High'].max()
    min_price = df['Low'].min()
    diff = max_price - min_price
    
    levels = {
        0.236: max_price - diff * 0.236,
        0.382: max_price - diff * 0.382,
        0.5: max_price - diff * 0.5,
        0.618: max_price - diff * 0.618,
        0.786: max_price - diff * 0.786
    }
    return levels

def calculate_regression_channel(df):
    """Doğrusal Regresyon Kanalı (Linear Regression Channel) hesaplar."""
    if df.empty: return None, None, None
    x = np.arange(len(df))
    y = df['Close'].values
    
    # Trend Çizgisi (Slope & Intercept)
    slope, intercept = np.polyfit(x, y, 1)
    regression_line = slope * x + intercept
    
    # Standart Sapma Kanalı
    residuals = y - regression_line
    std_dev = np.std(residuals)
    
    upper_channel = regression_line + (2 * std_dev)
    lower_channel = regression_line - (2 * std_dev)
    
    return regression_line, upper_channel, lower_channel

def calculate_pivot_points(high, low, close):
    """
    Klasik Pivot Noktaları (P, R1, S1, R2, S2) hesaplar.
    Son günün (veya periyodun) Yüksek, Düşük ve Kapanış değerlerini alır.
    """
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    return pivot, r1, s1, r2, s2

def calculate_fair_value(info):
    """
    Graham Formülü ile basit Adil Değer hesaplaması (Sadece Fikir Verir).
    Formül: Sqrt(22.5 * EPS * BookValue)
    """
    try:
        if not info: return None
        eps = info.get('trailingEps')
        book_value = info.get('bookValue')
        
        if (isinstance(eps, (int, float)) and isinstance(book_value, (int, float)) and 
            eps > 0 and book_value > 0):
            fair_value = (22.5 * eps * book_value) ** 0.5
            return fair_value
        else:
            return None
    except:
        return None
