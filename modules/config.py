"""
Spider Domain Crawler - Konfigürasyon Modülü

Copyright (c) 2025 Hasan Yasin Yaşar
Licensed under PSH 1.1 (Pasha Software License)
"""

# Crawler Ayarları
DEFAULT_DELAY = 1.0  # İstekler arası bekleme süresi (saniye)
DEFAULT_MAX_DEPTH = 2  # Maksimum crawl derinliği
DEFAULT_MAX_URLS = 100  # Maksimum toplanacak URL sayısı
DEFAULT_TIMEOUT = 10  # HTTP request timeout (saniye)

# User-Agent Strings
TARASSUT_USER_AGENT = 'Tarassut 1.0'

# Random User Agent Pool - Güncel ve çeşitli user agent'lar
RANDOM_USER_AGENTS = [
    # Chrome - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    
    # Chrome - macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    # Chrome - Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    # Firefox - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
    
    # Firefox - macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    
    # Firefox - Linux
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    
    # Safari - macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    
    # Edge - Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    
    # Mobile - Android Chrome
    'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    
    # Mobile - iPhone Safari
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    
    # Opera
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
]

# Eski user agent listesi (geriye uyumluluk için)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
]

# Random User Agent ayarları
USE_RANDOM_USER_AGENT = False  # Varsayılan olarak kapalı
RANDOM_USER_AGENT_PER_REQUEST = True  # Her istekte farklı user agent kullan
RANDOM_USER_AGENT_PER_SESSION = False  # Oturum başına bir user agent kullan

# Proxy ayarları
USE_PROXY = False  # Varsayılan olarak kapalı
PROXY_ROTATION = True  # Proxy rotasyonu (her istekte farklı proxy)
PROXY_TIMEOUT = 10  # Proxy timeout (saniye)
PROXY_RETRIES = 3  # Proxy başarısız olursa deneme sayısı

# Proxy listesi - HTTP ve SOCKS proxy'leri desteklenir
PROXY_LIST = [
    # HTTP Proxy örnekleri (gerçek proxy'ler değil, örnek format)
    # 'http://proxy1.example.com:8080',
    # 'http://username:password@proxy2.example.com:3128',
    # 'https://proxy3.example.com:8080',
    
    # SOCKS Proxy örnekleri
    # 'socks5://proxy4.example.com:1080',
    # 'socks4://proxy5.example.com:1080',
    
    # Ücretsiz proxy servisleri (test için - güvenilirlik düşük)
    # Not: Bu proxy'ler test amaçlıdır, production'da güvenilir proxy servisleri kullanın
]

# Proxy doğrulama ayarları
PROXY_VALIDATION_URL = 'http://httpbin.org/ip'  # Proxy test URL'i
PROXY_VALIDATION_TIMEOUT = 5  # Proxy doğrulama timeout

# Domain engelleme ayarları
USE_DOMAIN_BLOCKING = False  # Varsayılan olarak kapalı
BLOCKED_DOMAINS_FILE = 'blocked_domains.txt'  # Varsayılan engellenen domain dosyası

# Varsayılan engellenen domain'ler
DEFAULT_BLOCKED_DOMAINS = [
    # Sosyal medya platformları (genellikle crawl için gereksiz)
    'facebook.com',
    'twitter.com', 
    'instagram.com',
    'linkedin.com',
    'tiktok.com',
    'snapchat.com',
    'pinterest.com',
    
    # Reklam ve analitik servisleri
    'google-analytics.com',
    'googletagmanager.com',
    'doubleclick.net',
    'googlesyndication.com',
    'googleadservices.com',
    'facebook.net',
    'fbcdn.net',
    
    # CDN ve statik içerik (opsiyonel)
    # 'cdnjs.cloudflare.com',
    # 'ajax.googleapis.com',
    
    # Diğer yaygın servisler
    'youtube.com',
    'vimeo.com',
    'dailymotion.com'
]

# Domain engelleme seçenekleri
DOMAIN_BLOCKING_MODE = 'exact'  # 'exact', 'subdomain', 'contains'
# exact: Tam eşleşme (google.com sadece google.com'u engeller)
# subdomain: Alt domain dahil (google.com, www.google.com, maps.google.com'u engeller)  
# contains: İçeren (google.com, mygoogle.com, google.com.tr'yi engeller)

# İstenmeyen dosya uzantıları (varsayılan)
DEFAULT_EXCLUDED_EXTENSIONS = [
    # Resim dosyaları
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif',
    
    # Video dosyaları
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp',
    
    # Ses dosyaları
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
    
    # Döküman dosyaları
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
    
    # Arşiv dosyaları
    '.zip', '.rar', '.tar', '.gz', '.7z', '.bz2', '.xz', '.tar.gz', '.tar.bz2',
    
    # Kod ve stil dosyaları
    '.css', '.js', '.json', '.xml', '.scss', '.sass', '.less', '.ts', '.jsx', '.tsx',
    
    # Font dosyaları
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    
    # Executable dosyalar
    '.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.app',
    
    # Diğer
    '.swf', '.fla', '.psd', '.ai', '.eps', '.sketch', '.fig'
]

# Engellenen URL pattern'leri
BLOCKED_PATTERNS = [
    r'mailto:',
    r'tel:',
    r'javascript:',
    r'#$',  # Sadece fragment olan linkler
    r'/admin/',
    r'/wp-admin/',
    r'/login',
    r'/logout',
    r'/api/',
    r'\.rss$',
    r'\.atom$'
]

# İzin verilen content type'lar
ALLOWED_CONTENT_TYPES = [
    'text/html',
    'application/xhtml+xml'
]

# Robots.txt ayarları
RESPECT_ROBOTS_TXT = True
ROBOTS_TXT_CACHE_TIME = 3600  # 1 saat

# Rate limiting ayarları
MIN_DELAY = 0.1  # Minimum bekleme süresi
MAX_DELAY = 10.0  # Maksimum bekleme süresi

# Retry ayarları
MAX_RETRIES = 3
RETRY_DELAY = 2.0

# Logging ayarları
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Output ayarları
DEFAULT_OUTPUT_FILE = 'domains.json'
SAVE_VISITED_URLS = True
SAVE_FAILED_URLS = True
