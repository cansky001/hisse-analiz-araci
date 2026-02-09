import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.indicators import calculate_regression_channel, calculate_fibonacci

def load_custom_css():
    """Özel CSS stillerini yükler."""
    st.markdown("""
        <style>
            /* Genel Ayarlar */
            .block-container { padding-top: 1rem; padding-bottom: 2rem; }
            
            /* Başlık ve Fontlar */
            h1, h2, h3 { font-family: 'Segoe UI', sans-serif; font-weight: 600; }
            h1 { color: #00e676; margin-bottom: 0.5rem; }
            
            /* Metrik Kutuları */
            .stMetric { 
                background-color: #111827; 
                border: 1px solid #374151; 
                padding: 15px; 
                border-radius: 10px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .stMetric label { color: #9ca3af !important; }
            .stMetric div[data-testid="stMetricValue"] { color: #f3f4f6 !important; font-weight: 700; }
            
            /* Butonlar */
            .stButton>button { 
                width: 100%; 
                border-radius: 8px; 
                font-weight: 600; 
                background-color: #1f2937; 
                color: white; 
                border: 1px solid #374151; 
                transition: all 0.2s;
            }
            .stButton>button:hover { 
                border-color: #00e676; 
                color: #00e676; 
                background-color: #111827; 
                transform: translateY(-1px);
            }
            
            /* Sidebar ve Expander */
            section[data-testid="stSidebar"] { background-color: #0b0f19; }
            div[data-testid="stExpander"] { 
                background-color: #111827; 
                border: 1px solid #374151; 
                border-radius: 8px; 
            }
            
            /* Rehber Kutusu */
            .guide-box {
                background-color: #1f2937;
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #00e676;
                margin-bottom: 20px;
                font-size: 0.9rem;
                color: #e5e7eb;
            }
            .guide-item { margin-bottom: 8px; display: flex; align-items: center; }
            .guide-icon { width: 25px; display: inline-block; text-align: center; margin-right: 10px; font-weight: bold; }
            
            /* Pivot Kutusu */
            .pivot-grid { display: flex; gap: 10px; justify-content: space-between; margin-bottom: 20px; }
            .pivot-box {
                background-color: #1f2937;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #374151;
                flex: 1;
            }
            .pivot-label { font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; }
            .pivot-value { font-size: 1.1rem; font-weight: bold; color: #fff; margin-top: 5px; }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Yan paneli oluşturur ve kullanıcı seçeneklerini döndürür."""
    st.sidebar.title("🛠️ Kontrol Paneli")
    
    st.sidebar.subheader("Görünüm Ayarları")
    options = {
        "show_linreg": st.sidebar.checkbox("Regresyon Kanalı", value=True),
        "show_fib": st.sidebar.checkbox("Fibonacci Seviyeleri", value=True),
        "show_bb": st.sidebar.checkbox("Bollinger Bantları", value=True),
        "show_ema": st.sidebar.checkbox("EMA (Hareketli Ort.)", value=True),
        "show_swings": st.sidebar.checkbox("Tepe/Dip Noktaları", value=True),
        "show_atr": st.sidebar.checkbox("ATR Stop", value=False),
        "pro_indicator": st.sidebar.selectbox("Trend Göstergesi:", ["Yok", "Parabolic SAR", "SuperTrend"]),
        "oscillator_mode": st.sidebar.selectbox("Momentum:", ["RSI (Klasik)", "Stoch RSI (Hassas)"])
    }
    
    return options

def render_pivot_points(pivot, r1, s1, r2, s2):
    """Pivot noktalarını görsel olarak şık bir şekilde gösterir."""
    st.markdown("##### 🗝️ Pivot Seviyeleri (Destek / Direnç)")
    
    # HTML ile CSS Grid yapısı kuruyoruz, st.columns yerine daha kontrollü
    html = f"""
    <div class="pivot-grid">
        <div class="pivot-box">
            <div class="pivot-label">Destek 2 (S2)</div>
            <div class="pivot-value" style="color:#ef4444">{s2:.2f}</div>
        </div>
        <div class="pivot-box">
            <div class="pivot-label">Destek 1 (S1)</div>
            <div class="pivot-value" style="color:#f87171">{s1:.2f}</div>
        </div>
        <div class="pivot-box" style="border-color:#00e676; background-color: #064e3b;">
            <div class="pivot-label" style="color:#a7f3d0">PİVOT</div>
            <div class="pivot-value" style="color:#fff">{pivot:.2f}</div>
        </div>
        <div class="pivot-box">
            <div class="pivot-label">Direnç 1 (R1)</div>
            <div class="pivot-value" style="color:#4ade80">{r1:.2f}</div>
        </div>
        <div class="pivot-box">
            <div class="pivot-label">Direnç 2 (R2)</div>
            <div class="pivot-value" style="color:#22c55e">{r2:.2f}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_chart(df, options):
    """Ana analiz grafiğini çizer."""
    if df is None or df.empty:
        st.warning("Grafik çizilemiyor, veri yok.")
        return

    oscillator_mode = options["oscillator_mode"]
    
    # Alt grafik düzeni
    rows = [0.55, 0.15, 0.15, 0.15]
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=rows,
        subplot_titles=("Fiyat Analizi", "Hacim", f"Momentum ({oscillator_mode})", "Trend (MACD)")
    )
    
    # --- 1. PANEL: Fiyat ---
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
        name="Fiyat"
    ), row=1, col=1)
    
    # Bollinger
    if options["show_bb"]:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], fill='tonexty', fillcolor='rgba(0,255,100,0.05)', line=dict(width=0), name="Bollinger", hoverinfo='skip'), row=1, col=1)
    
    # EMA
    if options["show_ema"]:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='#fbbf24', width=1), name="EMA 20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='#22d3ee', width=1), name="EMA 50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='#a855f7', width=1.5, dash='dot'), name="EMA 200"), row=1, col=1)
    
    # Regresyon Kanalı
    if options["show_linreg"]:
        reg_line, upper_ch, lower_ch = calculate_regression_channel(df)
        if reg_line is not None:
            fig.add_trace(go.Scatter(x=df.index, y=upper_ch, line=dict(color='yellow', width=0), showlegend=False, hoverinfo='skip'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=lower_ch, fill='tonexty', fillcolor='rgba(255, 255, 0, 0.08)', line=dict(color='yellow', width=0), name="Regresyon Kanalı", hoverinfo='skip'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=reg_line, line=dict(color='yellow', width=1, dash='dash'), name="Regresyon Hattı"), row=1, col=1)

    # Fibonacci
    if options["show_fib"]:
        fib_levels = calculate_fibonacci(df)
        colors = {0.236: 'gray', 0.382: 'gray', 0.5: 'orange', 0.618: '#00e676', 0.786: 'red'} 
        for level, price in fib_levels.items():
            color = colors.get(level, 'white')
            fig.add_hline(y=price, line_dash="dot", annotation_text=f"Fib {level}", annotation_position="top right", line_color=color, line_width=1, row=1, col=1)
            
    # Swings (Tepe/Dip)
    if options["show_swings"]:
        dipler = df[df['min'].notnull()]
        tepeler = df[df['max'].notnull()]
        fig.add_trace(go.Scatter(x=dipler.index, y=dipler['min']*0.99, mode='markers', marker=dict(symbol='triangle-up', color='#00e676', size=8), name="Dip"), row=1, col=1)
        fig.add_trace(go.Scatter(x=tepeler.index, y=tepeler['max']*1.01, mode='markers', marker=dict(symbol='triangle-down', color='#ff1744', size=8), name="Tepe"), row=1, col=1)

    # ATR Stop
    if options["show_atr"]:
        fig.add_trace(go.Scatter(x=df.index, y=df['Trailing_Stop'], mode='markers', marker=dict(color='red', size=4), name="ATR Stop"), row=1, col=1)

    # SuperTrend / PSAR
    if options["pro_indicator"] == "Parabolic SAR":
        psar_cols = [c for c in df.columns if c.startswith('PSAR')]
        for c in psar_cols:
            valid_psar = df[c].dropna()
            if not valid_psar.empty:
                fig.add_trace(go.Scatter(x=valid_psar.index, y=valid_psar, mode='markers', marker=dict(color='#2962FF', size=4), name="Parabolic SAR"), row=1, col=1)
    elif options["pro_indicator"] == "SuperTrend":
        st_cols = [c for c in df.columns if c.startswith('SUPERT')]
        if st_cols:
            fig.add_trace(go.Scatter(x=df.index, y=df[st_cols[0]], line=dict(color='white', width=2), name="SuperTrend"), row=1, col=1)

    # --- 2. PANEL: Hacim ---
    colors = ['#00e676' if o-c < 0 else '#ff1744' for o, c in zip(df['Open'], df['Close'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Hacim"), row=2, col=1)
    if 'Vol_EMA' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['Vol_EMA'], line=dict(color='white', width=1), name="Hacim Ort."), row=2, col=1)

    # --- 3. PANEL: Momentum ---
    if oscillator_mode == "RSI (Klasik)":
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#a855f7', width=2), name="RSI"), row=3, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#ef4444", row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#22c55e", row=3, col=1)
    else: # Stoch RSI
        k_col = next((c for c in df.columns if c.startswith('STOCHRSIk')), None)
        d_col = next((c for c in df.columns if c.startswith('STOCHRSId')), None)
        if k_col and d_col:
            fig.add_trace(go.Scatter(x=df.index, y=df[k_col], line=dict(color='#22d3ee', width=1.5), name="Stoch K"), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df[d_col], line=dict(color='#fbbf24', width=1.5), name="Stoch D"), row=3, col=1)
            fig.add_hline(y=80, line_dash="dot", line_color="#ef4444", row=3, col=1)
            fig.add_hline(y=20, line_dash="dot", line_color="#22c55e", row=3, col=1)

    # --- 4. PANEL: MACD ---
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color='gray', name="Hist"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#3b82f6', width=1.5), name="MACD"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(color='#f97316', width=1.5), name="Signal"), row=4, col=1)

    # Layout Ayarları
    fig.update_layout(
        height=1000, 
        template="plotly_dark", 
        xaxis_rangeslider_visible=False, 
        margin=dict(l=10, r=10, t=30, b=10), 
        hovermode="x unified",
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)', # Transparan arka plan
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_guide():
    """Grafik okuma rehberini gösterir."""
    with st.expander("📖 Grafik Okuma Rehberi (Kılavuz)", expanded=False):
        st.markdown("""
        <div class="guide-box">
            <div class="guide-item"><span class="guide-icon" style="color:#00e676">▲</span> <b>Yeşil Üçgen (Dip):</b> Destek bölgesi / Dönüş sinyali.</div>
            <div class="guide-item"><span class="guide-icon" style="color:#ff1744">▼</span> <b>Kırmızı Üçgen (Tepe):</b> Direnç bölgesi / Satış sinyali.</div>
            <div class="guide-item"><span class="guide-icon" style="color:yellow">===</span> <b>Sarı Kanal (Regresyon):</b> Fiyatın matematiksel ortalaması ve sapma sınırları.</div>
            <div class="guide-item"><span class="guide-icon" style="color:#2962FF">●●●</span> <b>Parabolic SAR:</b> Noktalar fiyatın altındaysa yükseliş, üstündeyse düşüş trendi.</div>
            <div class="guide-item"><span class="guide-icon" style="color:white">▬▬</span> <b>SuperTrend:</b> Trend değişim ve stop noktası.</div>
        </div>
        """, unsafe_allow_html=True)
