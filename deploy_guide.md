# 🚀 RUNTIMEZERO: $0 MALİYETLE 2 DAKİKADA CANLIYA ALMA REHBERİ
### *Sıfır Masrafla 24/7 Bulutta Yaşayan Otonom Dijital Şirket*

Bu rehber, **SysCalculus** sistemini yerel bilgisayarından çıkarıp dünya çapında en hızlı sunucularda (**Cloudflare Pages**) **$0 maliyetle** yayına almanı ve **GitHub Actions** ile 24/7 otonom çalıştırmanı sağlar.

---

## 📋 GEREKENLER (TAMAMI %100 ÜCRETSİZ)
1. Ücretsiz bir **GitHub** hesabı ([github.com](https://github.com))
2. Ücretsiz bir **Cloudflare** hesabı ([cloudflare.com](https://cloudflare.com))

---

## ⚡ 1. ADIM: PROJEYİ GITHUB'A YÜKLEME (1 DAKİKA)

Terminali veya Komut Satırını (`cmd`) aç ve proje klasöründe şu 4 komutu sırayla çalıştır:

```bash
# 1. Git deposunu başlat
git init

# 2. Tüm dosyaları ekle ve ilk paketi hazırla
git add .
git commit -m "feat: initial launch of syscalculus autonomous dac"

# 3. GitHub'da "syscalculus" adında yeni bir Public repository (depo) aç ve adresini bağla:
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/syscalculus.git

# 4. Kodları buluta fırlat
git push -u origin main
```

---

## ☁️ 2. ADIM: CLOUDFLARE PAGES'E BAĞLAMA (60 SANİYE)

1. [Cloudflare Dashboard](https://dash.cloudflare.com)'a giriş yap.
2. Sol menüden **Workers & Pages** > **Create application** > **Pages** sekmesine tıkla.
3. **Connect to Git** seçeneğini seç ve GitHub hesabını bağla.
4. Az önce açtığın `syscalculus` deposunu seç ve **Begin setup** de.
5. Ayarları aynen şu şekilde doldur:
   * **Project name:** `syscalculus`
   * **Production branch:** `main`
   * **Framework preset:** `None`
   * **Build command:** `python build.py`
   * **Build output directory:** `dist`
6. **Save and Deploy** butonuna bas!

🎉 **TEBRİKLER!** 30 saniye içinde siten tüm dünyada yayına girecek:  
👉 `https://syscalculus.pages.dev` (veya belirlediğin isim)

---

## 🤖 3. ADIM: 24/7 BULUT CRON OTONOMİSİ (BİLGİSAYARIN KAPALIYKEN)

Depona eklediğimiz `.github/workflows/autonomous_cron.yml` dosyası sayesinde:
* GitHub her gece saat 03:00'te sanal sunucu ayağa kaldırır.
* `python main.py --cron` çalıştırır.
* Yeni içerikleri ve araçları derler, SEO site haritasını yeniler.
* Değişiklikleri otomatik commit edip Cloudflare'a basar.

### (Opsiyonel) Sosyal Medya ve Gemini API Anahtarlarını Ekleme:
GitHub reponda **Settings > Secrets and variables > Actions** sekmesine gidip şu ücretsiz anahtarları tanımlayabilirsin:
* `DEVTO_API_KEY`: [dev.to/settings/extensions](https://dev.to/settings/extensions) adresinden alacağın ücretsiz API key (Makalelerin Dev.to'da otomatik yayınlanmasını sağlar).
* `DISCORD_WEBHOOK_URL`: Kendi Discord sunucundaki bir kanalın Webhook linki (Yazılar hazır olunca Discord'a bildirim atar).
* `GEMINI_API_KEY`: [aistudio.google.com](https://aistudio.google.com) adresinden alacağın ücretsiz Gemini API key (Sıfırdan sınırsız yeni araç yazması için).

*(Bu anahtarları eklemesen bile sistem kendi içindeki uzman kütüphanesiyle tıkır tıkır çalışmaya devam eder).*

---

## 🔍 4. ADIM: GOOGLE SEARCH CONSOLE'A SİTE HARİTASINI VERME

Google'ın siteni 24 saat içinde indekslemesi için:
1. [Google Search Console](https://search.google.com/search-console)'a git.
2. Sitenin adresini gir (`https://syscalculus.pages.dev`).
3. Sol menüden **Sitemaps (Site Haritaları)** bölümüne tıkla.
4. `sitemap.xml` yazıp **Gönder (Submit)** butonuna bas.

Google botları hemen devreye girecek; 7 adet interaktif simülatörü, 7 adet 1.500+ kelimelik teknik analizi ve zengin `SoftwareApplication` şemalarını tarayıp aramada en üstlere yerleştirecektir.

---

## 💰 5. ADIM: GOOGLE ADSENSE GELİRİNİ AKTİF ETME

1. Google Search Console'da indeksler açıldıktan ve ilk 100-200 mühendis trafiği geldikten sonra AdSense'e başvur.
2. Onay çıktığında Google'ın sana vereceği `ca-pub-XXXXXXXXXXXXXXXX` kodunu:
   * Projedeki `.env` dosyasına veya Cloudflare Environment Variables'a `ADSENSE_PUB_ID=ca-pub-SENIN_KODUN` olarak gir.
   * `build.py` çalıştırıldığı an tüm sitedeki reklamlar gerçek dolara dönüşür!
