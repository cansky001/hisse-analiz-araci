# 📈 ProTrade Hisse Analiz Terminali

Bu proje, Python ve Streamlit kullanılarak geliştirilmiş modern bir hisse senedi analiz aracıdır. BIST ve dünya borsalarındaki hisseleri teknik ve temel olarak analiz etmenizi sağlar.

## 🚀 Özellikler

- **Gelişmiş Grafikler:** Mum grafikleri, Bollinger bantları, EMA, Regresyon kanalı.
- **Teknik İndikatörler:** RSI, Stoch RSI, MACD, ATR Stop, SuperTrend, Parabolic SAR.
- **Pivot Noktaları:** Destek ve direnç seviyelerinin otomatik hesaplanması.
- **Temel Analiz:** Basitleştirilmiş bilanço analizi ve Graham Adil Değer hesaplaması.
- **Responsive Tasarım:** Telefonda ve bilgisayarda şık görünüm.

## 💻 Kurulum ve Çalıştırma (Kendi Bilgisayarınızda)

1. **Gereksinimleri Yükleyin:**
   Terminali açın ve proje klasöründe şu komutu çalıştırın:
   ```bash
   pip install -r requirements.txt
   ```

2. **Uygulamayı Başlatın:**
   ```bash
   streamlit run main.py
   ```
   Tarayıcınızda otomatik olarak açılacaktır (Genellikle http://localhost:8501).

## 🌐 İnternette Yayınlama (Herkesin Erişimi İçin)

Bu uygulamayı "gerçek bir web sitesi" gibi herkesin kullanabilmesi için **Streamlit Cloud** kullanabilirsiniz (Ücretsizdir).

1. Bu proje klasörünü bir **GitHub** deposuna (repository) yükleyin.
2. [share.streamlit.io](https://share.streamlit.io) adresine gidin ve GitHub hesabınızla giriş yapın.
3. "New App" butonuna tıklayın.
4. GitHub deposunu, dalı (branch - genelde main) ve ana dosya yolunu (`main.py`) seçin.
5. "Deploy" butonuna basın.

Yaklaşık 2-3 dakika içinde uygulamanız `https://protrade-analiz.streamlit.app` gibi bir adreste yayına girecektir. Bu linki arkadaşlarınızla paylaşabilirsiniz.

## 📁 Proje Yapısı

- `main.py`: Ana uygulama dosyası.
- `utils/`: Yardımcı modüller.
  - `data.py`: Veri çekme işlemleri.
  - `ui.py`: Görsel tasarım ve grafikler.
  - `indicators.py`: Matematiksel hesaplamalar.
- `requirements.txt`: Gerekli kütüphaneler listesi.
