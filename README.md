# Spider Domain Crawler

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-PSH%201.1-red.svg)](LICENSE.md)
[![GitHub Issues](https://img.shields.io/github/issues/yourusername/spider-domain-crawler.svg)](https://github.com/Pashaorgtr/Spider/issues)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/spider-domain-crawler.svg)](https://github.com/Pashaorgtr/Spider/stargazers)

Web sayfalarından **zincirleme domain tespiti** yapan Python crawler yazılımı.

## 🚀 Hızlı Başlangıç

```bash
# Projeyi klonla
git clone https://github.com/Pashaorgtr/Spider.git
cd Spider

# Virtual environment oluştur
python3 -m venv spider-venv
source spider-venv/bin/activate  # Linux/Mac
# spider-venv\Scripts\activate   # Windows

# Kütüphaneleri yükle
pip install -r requirements.txt

# Hızlı test
python main.py https://pasha.org.tr
```

## 📋 İçindekiler

- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Parametreler](#parametreler)
- [Örnekler](#örnekler)
- [Katkıda Bulunma](#katkıda-bulunma)
- [Lisans](#lisans)

## Proje Yapısı

```
spider/
├── modules/                 # Ana modüller
│   ├── __init__.py         
│   ├── url_crawler.py      # URL crawler
│   ├── url_utils.py        # URL analiz araçları
│   ├── domain_detector.py  # Domain tespit modülü
│   └── config.py           # Konfigürasyon ve dosya uzantıları
├── data/                   # Çıktı dosyaları (JSON sonuçları)
├── main.py                 # Ana çalıştırma dosyası
├── domain_crawler.py       # Spider Domain Crawler fonksiyonları
├── requirements.txt        
├── README.md              
└── KULLANIM_KILAVUZU.md   
```

## Özellikler

### 🕸️ Spider Crawl (Ana Özellik)
- **Zincirleme Crawling**: Bulunan domain'leri tekrar crawl eder
- **Çok Seviyeli**: Belirlenen derinlikte spider crawl yapar
- **Otomatik Genişleme**: Her seviyede yeni domain'ler bulur
- **Akıllı Filtreleme**: Daha önce işlenmiş domain'leri atlar

### 📄 Dosya Uzantısı Filtreleme
- **Varsayılan Filtreleme**: 74 farklı dosya uzantısı otomatik hariç tutuluyor
- **Özel Filtreleme**: İstediğiniz uzantıları belirtebilirsiniz
- **Filtresiz Mod**: Tüm dosya türlerini dahil edebilirsiniz
- **Performans**: Gereksiz dosyalar crawl edilmez

### 🔍 Domain Tespiti
- **DNS Doğrulama**: Sadece gerçek domain'ler kaydedilir
- **Otomatik Tespit**: HTML içeriğinden domain çıkarır
- **Temiz Çıktı**: Sadece domain listesi
- **Özel User-Agent**: "Tarassut 1.0" kimliği ile istekler
- **Random User-Agent**: İsteğe bağlı random user agent desteği
- **Proxy Desteği**: HTTP/HTTPS/SOCKS proxy desteği ve rotasyon
- **Domain Engelleme**: İstenmeyen domain'lerin otomatik atlanması

### 💾 Düzenli Çıktı
- **Data Klasörü**: Tüm sonuçlar `data/` klasörüne kaydedilir
- **JSON Format**: Yapılandırılmış çıktı formatı
- **Zaman Damgası**: Otomatik dosya adlandırma

## Kurulum

```bash
# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Kütüphaneleri yükle
pip install -r requirements.txt
```

## Kullanım

### 🕸️ Spider Crawl Modları

#### 1. Normal Spider Crawl (Sadece Domain Zincirleme)
```bash
# Basit spider crawl - sadece domain seviyesinde zincirleme
python main.py https://pasha.org.tr --spider

# Derin spider crawl
python main.py https://pasha.org.tr --spider --spider-depth 5
```

#### 2. Enhanced Spider Crawl (Sayfa + Domain Zincirleme)
```bash
# Gelişmiş spider crawl - hem sayfa hem domain seviyesinde zincirleme
python main.py https://pasha.org.tr --enhanced-spider

# Derin ve geniş enhanced spider crawl
python main.py https://pasha.org.tr --enhanced-spider \
    --spider-depth 4 \
    --spider-domains-per-level 15 \
    --spider-max-domains 200 \
    --spider-max-pages-per-domain 30
```

#### Spider Crawl Karşılaştırması

| Özellik | Normal Spider | Enhanced Spider |
|---------|---------------|-----------------|
| Domain Zincirleme | ✅ | ✅ |
| Sayfa Zincirleme | ❌ | ✅ |
| Bulunan Domain Sayısı | Orta | Çok Yüksek |
| Bulunan Sayfa Sayısı | Az | Çok Yüksek |
| Çalışma Süresi | Hızlı | Daha Uzun |
| Kaynak Kullanımı | Az | Orta |

### 🎭 Random User Agent

```bash
# Her istekte farklı user agent kullan
python main.py https://pasha.org.tr --random-user-agent

# Oturum başına bir random user agent kullan
python main.py https://pasha.org.tr --random-user-agent-per-session

# Spider crawl ile random user agent
python main.py https://pasha.org.tr --spider --random-user-agent

# Enhanced spider crawl ile random user agent
python main.py https://pasha.org.tr --enhanced-spider --random-user-agent
```

### 🌐 Proxy Desteği

```bash
# Tek proxy kullanımı
python main.py https://pasha.org.tr --proxy http://proxy.pasha.org.tr:8080

# Birden fazla proxy kullanımı
python main.py https://pasha.org.tr --proxy http://proxy1:8080 socks5://proxy2:1080

# Proxy dosyasından yükleme
python main.py https://pasha.org.tr --proxy-file proxies.txt

# Proxy rotasyonunu kapatma
python main.py https://pasha.org.tr --proxy http://proxy:8080 --no-proxy-rotation

# Spider crawl ile proxy
python main.py https://pasha.org.tr --spider --proxy http://proxy:8080

# Enhanced spider crawl ile proxy ve random user agent
python main.py https://pasha.org.tr --enhanced-spider --proxy-file proxies.txt --random-user-agent
```

### 🚫 Domain Engelleme

```bash
# Belirli domain'leri engelle
python main.py https://pasha.org.tr --block-domains google.com facebook.com

# Domain engelleme dosyasından yükle
python main.py https://pasha.org.tr --block-domains-file blocked_domains.txt

# Varsayılan engellenen domain'leri kullan
python main.py https://pasha.org.tr --use-default-blocked-domains

# Kombinasyon: Dosya + komut satırı + varsayılan
python main.py https://pasha.org.tr --block-domains-file blocked_domains.txt --block-domains twitter.com --use-default-blocked-domains

# Spider crawl ile domain engelleme
python main.py https://pasha.org.tr --spider --block-domains google.com youtube.com

# Enhanced spider crawl ile domain engelleme
python main.py https://pasha.org.tr --enhanced-spider --block-domains-file blocked_domains.txt
```

### 📄 Dosya Uzantısı Filtreleme

```bash
# Varsayılan filtreleme (74 uzantı hariç tutuluyor)
python main.py https://pasha.org.tr

# Özel uzantıları hariç tut
python main.py https://pasha.org.tr --exclude-extensions .pdf .jpg .png

# Tüm dosya türlerini dahil et
python main.py https://pasha.org.tr --include-all-extensions

# Spider crawl ile özel filtreleme
python main.py https://pasha.org.tr --spider --exclude-extensions .css .js
```

### 🔍 Normal Domain Crawl

```bash
# Basit crawl
python main.py https://pasha.org.tr

# Detaylı crawl
python main.py https://pasha.org.tr \
    --crawler-depth 3 \
    --crawler-max-urls 100 \
    --detector-timeout 15
```

### 🐍 Python Kodunda

```python
from domain_crawler import spider_crawl_domains

# Spider crawl başlat
results = spider_crawl_domains(
    initial_urls=['https://pasha.org.tr'],
    max_depth=3,
    max_domains_per_level=20,
    max_total_domains=100,
    excluded_extensions=['.pdf', '.jpg', '.png']  # Özel filtreleme
)

print(f"Bulunan domain sayısı: {results['total_domains_found']}")
for domain in results['valid_domains'][:10]:
    print(f"- {domain}")
```

## Spider Crawl Nasıl Çalışır?

### Normal Spider Crawl (Sadece Domain)
```
Seviye 1: https://pasha.org.tr
    ↓ (crawl eder, .css/.js dosyalarını atlar)
    → github.com, cdn.pasha.org.tr, api.pasha.org.tr

Seviye 2: https://github.com, https://cdn.pasha.org.tr, https://api.pasha.org.tr
    ↓ (her birini crawl eder, filtreleme uygular)
    → microsoft.com, jquery.com, cloudflare.com, ...

Seviye 3: https://microsoft.com, https://jquery.com, ...
    ↓ (devam eder)
    → Daha fazla domain...
```

### Enhanced Spider Crawl (Sayfa + Domain)
```
Seviye 1: https://pasha.org.tr
    ↓ (derin sayfa crawl + domain tespit)
    → Domains: github.com, cdn.pasha.org.tr, api.pasha.org.tr
    → Pages: /about, /contact, /blog, /products, ...

Seviye 2: Domain'ler + Sayfalar
    ↓ (hem yeni domain'leri hem yeni sayfaları crawl eder)
    → https://github.com + https://pasha.org.tr/about + ...
    → Çok daha fazla domain ve sayfa...

Seviye 3: Exponential Growth!
    ↓ (her seviyede katlanarak büyür)
    → Yüzlerce domain ve binlerce sayfa...
```

## Parametreler

### Ana Parametreler

- `urls`: Crawl edilecek başlangıç URL'leri (zorunlu)
- `--spider`: Spider crawl modunu etkinleştir
- `--output, -o`: Çıktı dosyası adı (data/ klasörüne kaydedilir)

### Spider Crawl Parametreleri

- `--spider`: Normal spider crawl modu (sadece domain zincirleme)
- `--enhanced-spider`: Gelişmiş spider crawl modu (sayfa + domain zincirleme)
- `--spider-depth`: Spider crawl derinliği (varsayılan: 3)
- `--spider-domains-per-level`: Seviye başına max domain (varsayılan: 20)
- `--spider-max-domains`: Toplam max domain (varsayılan: 100)
- `--spider-max-pages-per-domain`: Domain başına max sayfa (enhanced spider için, varsayılan: 50)

### Dosya Filtreleme Parametreleri

- `--exclude-extensions`: Hariç tutulacak uzantılar (örn: --exclude-extensions .pdf .jpg)
- `--include-all-extensions`: Tüm dosya uzantılarını dahil et

### Random User Agent Parametreleri

- `--random-user-agent`: Her istekte farklı random user agent kullan
- `--random-user-agent-per-session`: Oturum başına bir random user agent kullan

### Proxy Parametreleri

- `--proxy`: Kullanılacak proxy listesi (örn: --proxy http://proxy1:8080 socks5://proxy2:1080)
- `--proxy-file`: Proxy listesini içeren dosya yolu
- `--no-proxy-rotation`: Proxy rotasyonunu devre dışı bırak

### Domain Engelleme Parametreleri

- `--block-domains`: Engellenecek domain listesi (örn: --block-domains google.com facebook.com)
- `--block-domains-file`: Engellenecek domain listesini içeren dosya yolu
- `--use-default-blocked-domains`: Varsayılan engellenen domain listesini kullan

### Crawler Parametreleri

- `--crawler-delay`: Crawler gecikme süresi (varsayılan: 1.0)
- `--crawler-depth`: Crawler derinliği (varsayılan: 2)
- `--crawler-max-urls`: Crawler max URL (varsayılan: 50)

### Detector Parametreleri

- `--detector-delay`: Detector gecikme süresi (varsayılan: 0.5)
- `--detector-timeout`: Detector timeout (varsayılan: 10)
- `--no-validation`: Domain doğrulamasını devre dışı bırak

## Çıktı Formatı

**Sonuçlar `data/` klasörüne JSON formatında kaydedilir:**

```json
{
  "total_domains_found": 87,
  "total_valid_domains": 85,
  "total_invalid_domains": 2,
  "valid_domains": [
    "github.com",
    "microsoft.com",
    "jquery.com",
    "cloudflare.com"
  ],
  "excluded_extensions": [".css", ".js", ".pdf", ".jpg"],
  "spider_depth": 3,
  "execution_time_seconds": 45.67,
  "timestamp": "2025-08-15T18:05:21.272Z"
}
```

## Hızlı Test

```bash
# Demo çalıştır (varsayılan filtreleme ile)
python main.py https://pasha.org.tr

# Spider crawl test
python main.py https://pasha.org.tr --spider --spider-depth 2

# Özel filtreleme test
python main.py https://pasha.org.tr --exclude-extensions .css .js --crawler-max-urls 20
```

## Varsayılan Hariç Tutulan Dosya Uzantıları

Sistem varsayılan olarak 74 farklı dosya uzantısını hariç tutar:

- **Resim**: .jpg, .jpeg, .png, .gif, .svg, .webp, .ico, .bmp, .tiff
- **Video**: .mp4, .avi, .mov, .wmv, .flv, .webm, .mkv
- **Ses**: .mp3, .wav, .flac, .aac, .ogg, .wma
- **Doküman**: .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx
- **Arşiv**: .zip, .rar, .tar, .gz, .7z, .bz2
- **Web**: .css, .js, .json, .xml, .scss, .sass
- **Font**: .ttf, .otf, .woff, .woff2, .eot
- **Yazılım**: .exe, .msi, .dmg, .pkg, .deb, .rpm

## Spider Crawl Avantajları

### Normal Spider Crawl
1. **Geniş Domain Kapsama**: Tek URL'den yüzlerce domain bulabilir
2. **Akıllı Filtreleme**: Gereksiz dosyalar crawl edilmez
3. **Kontrollü**: Derinlik ve domain sayısı limitleri
4. **Hızlı**: Dosya uzantısı filtreleme ile performans artışı
5. **Güvenilir**: DNS doğrulama ile sadece gerçek domain'ler

### Enhanced Spider Crawl
1. **Çift Zincirleme**: Hem domain hem sayfa seviyesinde zincirleme
2. **Exponential Growth**: Her seviyede katlanarak büyüyen keşif
3. **Derin Sayfa Analizi**: Her domain'den maksimum sayfa çıkarımı
4. **Hibrit Strateji**: Domain'ler + sayfalar birlikte işlenir
5. **Maksimum Kapsama**: Tek URL'den binlerce sayfa ve yüzlerce domain
6. **Akıllı Kaynak Yönetimi**: Sayfa başına limit ile kontrollü büyüme

### Geliştirme Ortamı

```bash
# Projeyi klonla
git clone https://github.com/Pashaorgtr/Spider.git
cd spider-domain-crawler

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Development dependencies yükle
pip install -r requirements.txt

# Testleri çalıştır
python main.py https://pasha.org.tr --crawler-max-urls 5
```

## 📝 Changelog

### v1.0.0 (2025-08-17)
- ✨ Spider crawl özelliği
- ✨ Enhanced spider crawl (sayfa + domain zincirleme)
- ✨ Random user agent desteği
- ✨ Proxy desteği (HTTP/HTTPS/SOCKS)
- ✨ Domain engelleme sistemi
- ✨ 74 dosya uzantısı filtreleme
- ✨ JSON çıktı formatı
- ✨ DNS domain doğrulama

## 🐛 Bilinen Sorunlar

- Bazı JavaScript-heavy siteler tam olarak crawl edilemeyebilir
- Çok büyük siteler için memory kullanımı artabilir
- Rate limiting nedeniyle bazı siteler erişimi kısıtlayabilir

## 📞 Destek

- 🐛 **Bug Report**: [Issues](https://github.com/Pashaorgtr/Spider/issues) sayfasından bildirebilirsiniz
- 💡 **Feature Request**: Yeni özellik önerileri için Issues kullanın
- 📧 **İletişim**: [yasin@pasha.org.tr](mailto:yasin@pasha.org.tr)

## ⭐ Yıldız Verin

Bu proje işinize yaradıysa, lütfen ⭐ vererek destekleyin!

## 📄 Lisans

Bu proje PSH 1.1 (Pasha Software License) lisansı altında lisanslanmıştır. 

**Önemli:** Bu yazılım **ticari kullanım için kesinlikle yasaktır**. Ticari kullanım için hiçbir koşulda lisans verilmeyecektir.

- **Gayri-ticari kullanım:** Tamamen ücretsiz (kişisel, akademik, topluluk projeleri)
- **Ticari kullanım:** Kesinlikle yasak - İhlal durumunda %20 tazminat + 100.000 TL minimum ceza
- **Amaç:** Telif hakkı koruması ve ticari sömürünün engellenmesi

Detaylar için [LICENSE.md](LICENSE.md) dosyasına bakın.

---

**Spider Domain Crawler** - Web'den domain keşfetmenin en akıllı yolu 🕷️
