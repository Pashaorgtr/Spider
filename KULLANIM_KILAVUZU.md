# Domain Crawler Kullanım Kılavuzu

## Hızlı Başlangıç

### 1. Kurulum

```bash
cd url-crawler
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Temel Kullanım

```bash
# Domain tespiti
python main.py https://example.com

# Ayarlarla
python main.py https://example.com --max-urls 50 --verbose
```

## Komut Satırı Parametreleri

### Temel Parametreler
- `urls`: Başlangıç URL'leri (zorunlu)
- `--output`: Çıktı dosyası (varsayılan: domain_results.json)
- `--verbose`: Detaylı log

### Crawler Ayarları
- `--crawl-delay`: URL crawling bekleme süresi (varsayılan: 1.0)
- `--max-depth`: Maksimum derinlik (varsayılan: 2)
- `--max-urls`: Maksimum URL sayısı (varsayılan: 50)

### Domain Tespiti Ayarları
- `--detect-delay`: Domain tespiti bekleme süresi (varsayılan: 1.0)
- `--timeout`: HTTP timeout (varsayılan: 10)

### Filtreleme Ayarları
- `--no-subdomains`: Subdomain'leri hariç tut
- `--exclude-domains`: Hariç tutulacak domain'ler
- `--min-url-count`: Minimum URL sayısı
- `--tld-filter`: İzin verilen TLD'ler

## Kullanım Örnekleri

### 1. Basit Domain Tespiti
```bash
python main.py https://github.com
```

### 2. Hızlı Tarama
```bash
python main.py https://example.com \
    --crawl-delay 0.5 \
    --detect-delay 0.5 \
    --max-urls 20
```

### 3. Filtrelemeli Tarama
```bash
python main.py https://example.com \
    --no-subdomains \
    --exclude-domains cdn ads \
    --min-url-count 2 \
    --tld-filter com org
```

### 4. Detaylı Analiz
```bash
python main.py https://example.com \
    --max-depth 3 \
    --max-urls 100 \
    --verbose \
    --output detailed_domains.json
```

## Python Kodunda Kullanım

### Basit Kullanım
```python
from modules.domain_detector import DomainDetector

detector = DomainDetector()
results = detector.detect_domains_from_urls(['https://example.com'])
detector.print_summary(results)
```

### Crawling + Domain Tespiti
```python
from modules.url_crawler import URLCrawler
from modules.domain_detector import DomainDetector

# URL crawling
crawler = URLCrawler(max_urls=50)
crawl_results = crawler.crawl(['https://example.com'])

# Domain tespiti
detector = DomainDetector()
all_urls = crawl_results['found_urls'] + ['https://example.com']
domain_results = detector.detect_domains_from_urls(all_urls)

print(f"Bulunan domain: {domain_results['total_domains']}")
```

### Filtreleme
```python
# Domain filtreleme
filtered = detector.filter_domains(
    include_subdomains=False,
    exclude_domains=['spam.com'],
    min_url_count=2,
    tld_filter=['com', 'org']
)
```

## Çıktı Analizi

### Domain İstatistikleri
- `total_domains`: Toplam domain sayısı
- `root_domains`: Ana domain sayısı
- `subdomains`: Subdomain sayısı
- `tld_distribution`: TLD dağılımı
- `top_domains_by_urls`: En çok URL'e sahip domain'ler

### Domain Detayları
Her domain için:
- URL sayısı
- TLD bilgisi
- Subdomain durumu
- Bulunan URL'ler

## İpuçları

1. **Rate Limiting**: Sunucuları yormamak için delay kullanın
2. **Filtreleme**: Gereksiz domain'leri filtreleyin
3. **Limit**: Büyük siteler için URL limitini ayarlayın
4. **Log**: Sorun giderme için --verbose kullanın

## Sorun Giderme

### Yaygın Hatalar
1. **Connection Error**: İnternet bağlantısı kontrol edin
2. **Timeout**: --timeout değerini artırın
3. **Too Many Requests**: --detect-delay değerini artırın

### Debug
```bash
python main.py https://example.com --verbose
```
