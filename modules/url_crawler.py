"""
Spider Domain Crawler - URL Crawler Modülü

Copyright (c) 2025 Hasan Yasin Yaşar
Licensed under PSH 1.1 (Pasha Software License)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import validators
import time
import json
import random
import socket
from typing import Set, List, Dict, Optional
import logging

class URLCrawler:
    """
    URL Crawler sınıfı - Web sayfalarından URL'leri toplar
    """
    
    def __init__(self, delay: float = 1.0, max_depth: int = 2, max_urls: int = 100, 
                 excluded_extensions: List[str] = None, use_random_user_agent: bool = False,
                 use_proxy: bool = False, proxy_list: List[str] = None, 
                 blocked_domains: List[str] = None, use_domain_blocking: bool = False):
        """
        URLCrawler başlatıcı
        
        Args:
            delay: İstekler arası bekleme süresi (saniye)
            max_depth: Maksimum crawl derinliği
            max_urls: Maksimum toplanacak URL sayısı
            excluded_extensions: Hariç tutulacak dosya uzantıları
            use_random_user_agent: Random user agent kullan
            use_proxy: Proxy kullan
            proxy_list: Kullanılacak proxy listesi
            blocked_domains: Engellenen domain listesi
            use_domain_blocking: Domain engelleme kullan
        """
        self.delay = delay
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.visited_urls: Set[str] = set()
        self.found_urls: Set[str] = set()
        self.session = requests.Session()
        self.use_random_user_agent = use_random_user_agent
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy = None
        self.failed_proxies: Set[str] = set()
        self.use_domain_blocking = use_domain_blocking
        self.blocked_domains = set()
        self.blocked_urls_count = 0
        
        # Excluded extensions ayarla
        if excluded_extensions is None:
            from .config import DEFAULT_EXCLUDED_EXTENSIONS
            self.excluded_extensions = set(ext.lower() for ext in DEFAULT_EXCLUDED_EXTENSIONS)
        else:
            self.excluded_extensions = set(ext.lower() for ext in excluded_extensions)
        
        # Logging ayarla
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # User-Agent ayarla
        self._setup_user_agent()
        
        # Proxy ayarla
        self._setup_proxy()
        
        # Domain engelleme ayarla
        self._setup_domain_blocking(blocked_domains)
        
        # Logging ayarla
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def _setup_user_agent(self):
        """User agent ayarlarını yapar"""
        if self.use_random_user_agent:
            from .config import RANDOM_USER_AGENTS, RANDOM_USER_AGENT_PER_SESSION
            if RANDOM_USER_AGENT_PER_SESSION:
                # Oturum başına bir user agent seç
                self.session_user_agent = random.choice(RANDOM_USER_AGENTS)
                self.session.headers.update({'User-Agent': self.session_user_agent})
                self.logger.info(f"Random user agent seçildi (oturum): {self.session_user_agent}")
            else:
                # Her istekte farklı user agent kullanılacak
                self.logger.info("Random user agent modu: Her istekte farklı user agent")
        else:
            from .config import TARASSUT_USER_AGENT
            self.session.headers.update({'User-Agent': TARASSUT_USER_AGENT})
            self.logger.info(f"Sabit user agent: {TARASSUT_USER_AGENT}")
    
    def _get_random_user_agent(self) -> str:
        """Random user agent döndürür"""
        from .config import RANDOM_USER_AGENTS
        return random.choice(RANDOM_USER_AGENTS)
    
    def _update_user_agent_if_needed(self):
        """Gerekirse user agent'ı günceller"""
        if self.use_random_user_agent:
            from .config import RANDOM_USER_AGENT_PER_REQUEST
            if RANDOM_USER_AGENT_PER_REQUEST:
                new_user_agent = self._get_random_user_agent()
                self.session.headers.update({'User-Agent': new_user_agent})
                self.logger.debug(f"User agent güncellendi: {new_user_agent}")
    
    def _setup_proxy(self):
        """Proxy ayarlarını yapar"""
        if self.use_proxy and self.proxy_list:
            self.logger.info(f"Proxy modu etkin: {len(self.proxy_list)} proxy mevcut")
            self._select_proxy()
        elif self.use_proxy and not self.proxy_list:
            self.logger.warning("Proxy modu etkin ama proxy listesi boş!")
            self.use_proxy = False
        else:
            self.logger.info("Proxy kullanılmıyor")
    
    def _select_proxy(self) -> Optional[str]:
        """Kullanılabilir bir proxy seçer"""
        if not self.proxy_list:
            return None
        
        # Başarısız proxy'leri hariç tut
        available_proxies = [p for p in self.proxy_list if p not in self.failed_proxies]
        
        if not available_proxies:
            self.logger.warning("Tüm proxy'ler başarısız! Proxy'siz devam ediliyor.")
            self.use_proxy = False
            return None
        
        # Random proxy seç
        proxy = random.choice(available_proxies)
        self.current_proxy = proxy
        
        # Session'a proxy ayarla
        proxy_dict = self._parse_proxy(proxy)
        if proxy_dict:
            self.session.proxies.update(proxy_dict)
            self.logger.info(f"Proxy seçildi: {proxy}")
            return proxy
        else:
            self.failed_proxies.add(proxy)
            return self._select_proxy()  # Başka proxy dene
    
    def _parse_proxy(self, proxy_url: str) -> Optional[Dict[str, str]]:
        """Proxy URL'ini parse eder"""
        try:
            if proxy_url.startswith('http://') or proxy_url.startswith('https://'):
                return {
                    'http': proxy_url,
                    'https': proxy_url
                }
            elif proxy_url.startswith('socks4://') or proxy_url.startswith('socks5://'):
                return {
                    'http': proxy_url,
                    'https': proxy_url
                }
            else:
                # Format belirtilmemişse HTTP olarak varsay
                formatted_proxy = f"http://{proxy_url}"
                return {
                    'http': formatted_proxy,
                    'https': formatted_proxy
                }
        except Exception as e:
            self.logger.error(f"Proxy parse hatası {proxy_url}: {e}")
            return None
    
    def _validate_proxy(self, proxy_url: str) -> bool:
        """Proxy'nin çalışıp çalışmadığını test eder"""
        try:
            from .config import PROXY_VALIDATION_URL, PROXY_VALIDATION_TIMEOUT
            
            proxy_dict = self._parse_proxy(proxy_url)
            if not proxy_dict:
                return False
            
            test_session = requests.Session()
            test_session.proxies.update(proxy_dict)
            
            response = test_session.get(
                PROXY_VALIDATION_URL, 
                timeout=PROXY_VALIDATION_TIMEOUT
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Proxy doğrulandı: {proxy_url}")
                return True
            else:
                self.logger.debug(f"Proxy doğrulama başarısız: {proxy_url} (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.logger.debug(f"Proxy doğrulama hatası {proxy_url}: {e}")
            return False
    
    def _rotate_proxy(self):
        """Proxy rotasyonu yapar"""
        if self.use_proxy and self.proxy_list:
            from .config import PROXY_ROTATION
            if PROXY_ROTATION:
                old_proxy = self.current_proxy
                new_proxy = self._select_proxy()
                if new_proxy and new_proxy != old_proxy:
                    self.logger.debug(f"Proxy değiştirildi: {old_proxy} -> {new_proxy}")
    
    def _handle_proxy_failure(self):
        """Proxy başarısızlığını işler"""
        if self.current_proxy:
            self.failed_proxies.add(self.current_proxy)
            self.logger.warning(f"Proxy başarısız olarak işaretlendi: {self.current_proxy}")
            
            # Yeni proxy dene
            new_proxy = self._select_proxy()
            if not new_proxy:
                self.logger.warning("Kullanılabilir proxy kalmadı, proxy'siz devam ediliyor")
                self.use_proxy = False
                self.session.proxies.clear()
    
    def _setup_domain_blocking(self, blocked_domains: List[str] = None):
        """Domain engelleme ayarlarını yapar"""
        if not self.use_domain_blocking:
            self.logger.info("Domain engelleme kullanılmıyor")
            return
        
        # Engellenen domain'leri ayarla
        if blocked_domains:
            self.blocked_domains.update(domain.lower().strip() for domain in blocked_domains)
            self.logger.info(f"Domain engelleme: {len(blocked_domains)} domain komut satırından eklendi")
        else:
            from .config import DEFAULT_BLOCKED_DOMAINS
            self.blocked_domains.update(domain.lower().strip() for domain in DEFAULT_BLOCKED_DOMAINS)
            self.logger.info(f"Domain engelleme: {len(DEFAULT_BLOCKED_DOMAINS)} varsayılan domain eklendi")
        
        self.logger.info(f"Toplam engellenen domain sayısı: {len(self.blocked_domains)}")
        
        # İlk birkaç engellenen domain'i göster
        if self.blocked_domains:
            sample_domains = list(self.blocked_domains)[:5]
            for i, domain in enumerate(sample_domains, 1):
                self.logger.info(f"   {i}. {domain}")
            if len(self.blocked_domains) > 5:
                self.logger.info(f"   ... ve {len(self.blocked_domains) - 5} domain daha")
    
    def _load_blocked_domains_from_file(self, file_path: str) -> List[str]:
        """Dosyadan engellenen domain'leri yükler"""
        blocked_domains = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        blocked_domains.append(line.lower())
            self.logger.info(f"Domain engelleme dosyasından {len(blocked_domains)} domain yüklendi: {file_path}")
        except FileNotFoundError:
            self.logger.warning(f"Domain engelleme dosyası bulunamadı: {file_path}")
        except Exception as e:
            self.logger.error(f"Domain engelleme dosyası okuma hatası: {e}")
        
        return blocked_domains
    
    def _is_domain_blocked(self, url: str) -> bool:
        """URL'nin domain'inin engellenip engellenmediğini kontrol eder"""
        if not self.use_domain_blocking or not self.blocked_domains:
            return False
        
        try:
            from .config import DOMAIN_BLOCKING_MODE
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Port numarasını kaldır
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # www. prefix'ini kaldır
            if domain.startswith('www.'):
                domain = domain[4:]
            
            for blocked_domain in self.blocked_domains:
                if DOMAIN_BLOCKING_MODE == 'exact':
                    # Tam eşleşme
                    if domain == blocked_domain:
                        return True
                elif DOMAIN_BLOCKING_MODE == 'subdomain':
                    # Alt domain dahil
                    if domain == blocked_domain or domain.endswith('.' + blocked_domain):
                        return True
                elif DOMAIN_BLOCKING_MODE == 'contains':
                    # İçeren
                    if blocked_domain in domain:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Domain engelleme kontrolü hatası {url}: {e}")
            return False
    
    def _log_blocked_domain(self, url: str):
        """Engellenen domain'i loglar"""
        self.blocked_urls_count += 1
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        self.logger.info(f"🚫 Domain engellendi: {domain} (URL: {url})")
        self.logger.debug(f"Toplam engellenen URL sayısı: {self.blocked_urls_count}")
    
    def is_excluded_url(self, url: str) -> bool:
        """URL'nin hariç tutulacak dosya uzantısına sahip olup olmadığını kontrol eder"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Dosya uzantısını kontrol et
            for ext in self.excluded_extensions:
                if path.endswith(ext):
                    self.logger.debug(f"URL hariç tutuldu (uzantı {ext}): {url}")
                    return True
            
            return False
            
        except Exception:
            return False
    
    def is_valid_url(self, url: str) -> bool:
        """URL'nin geçerli olup olmadığını kontrol eder"""
        if not validators.url(url):
            return False
        
        # Sadece HTTP ve HTTPS protokollerini kabul et
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Hariç tutulacak uzantıları kontrol et
        if self.is_excluded_url(url):
            return False
        
        return True
    
    def normalize_url(self, url: str) -> str:
        """URL'yi normalize eder (fragment'ları kaldırır)"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    def get_page_content(self, url: str) -> BeautifulSoup:
        """
        Verilen URL'den sayfa içeriğini alır
        
        Args:
            url: Crawl edilecek URL
            
        Returns:
            BeautifulSoup objesi veya None
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Random user agent kullanılıyorsa güncelle
                self._update_user_agent_if_needed()
                
                # Proxy rotasyonu
                if attempt > 0:  # İlk denemede rotasyon yapma
                    self._rotate_proxy()
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                # Content-Type kontrolü
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    return None
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.exceptions.ProxyError as e:
                self.logger.warning(f"Proxy hatası {url} (Deneme {attempt + 1}/{max_retries}): {e}")
                self._handle_proxy_failure()
                if attempt == max_retries - 1:
                    self.logger.error(f"Tüm proxy denemeleri başarısız: {url}")
                    return None
                continue
                
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"Timeout {url} (Deneme {attempt + 1}/{max_retries}): {e}")
                if self.use_proxy:
                    self._rotate_proxy()
                if attempt == max_retries - 1:
                    return None
                continue
                
            except requests.RequestException as e:
                self.logger.error(f"URL alınamadı {url} (Deneme {attempt + 1}/{max_retries}): {e}")
                if self.use_proxy and "proxy" in str(e).lower():
                    self._handle_proxy_failure()
                if attempt == max_retries - 1:
                    return None
                continue
        
        return None
    
    def extract_urls_from_page(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Sayfa içeriğinden URL'leri çıkarır
        
        Args:
            soup: BeautifulSoup objesi
            base_url: Temel URL (relative URL'ler için)
            
        Returns:
            Bulunan URL'lerin listesi
        """
        urls = []
        
        # <a> etiketlerinden href'leri al
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if href:
                # Relative URL'leri absolute'a çevir
                absolute_url = urljoin(base_url, href)
                normalized_url = self.normalize_url(absolute_url)
                
                if self.is_valid_url(normalized_url):
                    urls.append(normalized_url)
        
        # <link> etiketlerinden href'leri al (CSS, canonical vb.)
        for link in soup.find_all('link', href=True):
            href = link['href'].strip()
            if href:
                absolute_url = urljoin(base_url, href)
                normalized_url = self.normalize_url(absolute_url)
                
                if self.is_valid_url(normalized_url):
                    urls.append(normalized_url)
        
        return list(set(urls))  # Duplikatları kaldır
    
    def crawl_url(self, url: str, current_depth: int = 0) -> None:
        """
        Tek bir URL'yi crawl eder
        
        Args:
            url: Crawl edilecek URL
            current_depth: Mevcut derinlik seviyesi
        """
        if (len(self.found_urls) >= self.max_urls or 
            current_depth > self.max_depth or 
            url in self.visited_urls):
            return
        
        # Domain engelleme kontrolü
        if self._is_domain_blocked(url):
            self._log_blocked_domain(url)
            return
        
        self.visited_urls.add(url)
        self.logger.info(f"Crawling: {url} (Derinlik: {current_depth})")
        
        # Sayfa içeriğini al
        soup = self.get_page_content(url)
        if not soup:
            return
        
        # URL'leri çıkar
        urls = self.extract_urls_from_page(soup, url)
        
        for found_url in urls:
            if found_url not in self.found_urls and len(self.found_urls) < self.max_urls:
                # Domain engelleme kontrolü (bulunan URL'ler için)
                if not self._is_domain_blocked(found_url):
                    self.found_urls.add(found_url)
                    self.logger.info(f"Yeni URL bulundu: {found_url}")
                else:
                    self._log_blocked_domain(found_url)
        
        # Recursive crawling (eğer derinlik limiti aşılmamışsa)
        if current_depth < self.max_depth:
            for found_url in urls:
                if len(self.found_urls) >= self.max_urls:
                    break
                
                # Domain engelleme kontrolü
                if self._is_domain_blocked(found_url):
                    continue
                
                # Aynı domain'den URL'leri crawl et (opsiyonel)
                base_domain = urlparse(url).netloc
                found_domain = urlparse(found_url).netloc
                
                if base_domain == found_domain:  # Sadece aynı domain
                    time.sleep(self.delay)  # Rate limiting
                    self.crawl_url(found_url, current_depth + 1)
    
    def crawl(self, start_urls: List[str]) -> Dict:
        """
        Ana crawling fonksiyonu
        
        Args:
            start_urls: Başlangıç URL'lerinin listesi
            
        Returns:
            Crawling sonuçları
        """
        self.logger.info(f"Crawling başlatılıyor. Başlangıç URL'leri: {start_urls}")
        
        for url in start_urls:
            if len(self.found_urls) >= self.max_urls:
                break
            
            if self.is_valid_url(url):
                # Domain engelleme kontrolü
                if self._is_domain_blocked(url):
                    self._log_blocked_domain(url)
                    continue
                
                self.crawl_url(url)
            else:
                self.logger.warning(f"Geçersiz URL: {url}")
        
        results = {
            'start_urls': start_urls,
            'total_found': len(self.found_urls),
            'total_visited': len(self.visited_urls),
            'found_urls': list(self.found_urls),
            'visited_urls': list(self.visited_urls),
            'blocked_urls_count': self.blocked_urls_count if self.use_domain_blocking else 0,
            'blocked_domains_count': len(self.blocked_domains) if self.use_domain_blocking else 0
        }
        
        if self.use_domain_blocking:
            self.logger.info(f"Crawling tamamlandı. {len(self.found_urls)} URL bulundu, {self.blocked_urls_count} URL engellendi.")
        else:
            self.logger.info(f"Crawling tamamlandı. {len(self.found_urls)} URL bulundu.")
        
        return results
    
    def save_results(self, results: Dict, filename: str = 'crawl_results.json') -> None:
        """
        Sonuçları JSON dosyasına kaydet
        
        Args:
            results: Crawling sonuçları
            filename: Kayıt dosyası adı
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Sonuçlar {filename} dosyasına kaydedildi.")
