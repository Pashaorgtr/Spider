"""
Domain Detector Module
Web sayfalarından domain'leri tespit etme ve doğrulama
"""

"""
Spider Domain Crawler - Domain Detector Modülü

Copyright (c) 2025 Hasan Yasin Yaşar
Licensed under PSH 1.1 (Pasha Software License)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import json
import socket
import random
from typing import Set, List, Dict, Optional
import logging
import time

class DomainDetector:
    """Domain tespit etme ve doğrulama sınıfı"""
    
    def __init__(self, delay: float = 1.0, timeout: int = 10, validate_domains: bool = True, 
                 use_random_user_agent: bool = False, use_proxy: bool = False, proxy_list: List[str] = None,
                 blocked_domains: List[str] = None, use_domain_blocking: bool = False):
        """
        DomainDetector başlatıcı
        
        Args:
            delay: İstekler arası bekleme süresi
            timeout: HTTP request timeout
            validate_domains: Domain'lerin gerçek olup olmadığını kontrol et
            use_random_user_agent: Random user agent kullan
            use_proxy: Proxy kullan
            proxy_list: Kullanılacak proxy listesi
            blocked_domains: Engellenen domain listesi
            use_domain_blocking: Domain engelleme kullan
        """
        self.delay = delay
        self.timeout = timeout
        self.validate_domains = validate_domains
        self.use_random_user_agent = use_random_user_agent
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy = None
        self.failed_proxies: Set[str] = set()
        self.use_domain_blocking = use_domain_blocking
        self.blocked_domains = set()
        self.blocked_urls_count = 0
        self.session = requests.Session()
        self.found_domains: Set[str] = set()
        self.valid_domains: Set[str] = set()
        self.invalid_domains: Set[str] = set()
        self.domain_urls: Dict[str, Set[str]] = {}
        
        # Logging ayarla
        self.logger = logging.getLogger(__name__)
        
        # User-Agent ayarla
        self._setup_user_agent()
        
        # Proxy ayarla
        self._setup_proxy()
        
        # Domain engelleme ayarla
        self._setup_domain_blocking(blocked_domains)
    
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
    
    def extract_domain(self, url: str) -> str:
        """URL'den domain çıkarır"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def is_valid_domain_format(self, domain: str) -> bool:
        """Domain formatının geçerli olup olmadığını kontrol eder"""
        if not domain:
            return False
        
        # Basit domain regex kontrolü
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, domain))
    
    def validate_domain_exists(self, domain: str) -> bool:
        """Domain'in gerçekten var olup olmadığını kontrol eder"""
        if not self.validate_domains:
            return True
            
        try:
            # DNS lookup ile domain'in var olup olmadığını kontrol et
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            # DNS çözümlenemedi, domain geçersiz
            return False
        except Exception as e:
            self.logger.warning(f"Domain doğrulama hatası {domain}: {e}")
            return False
    
    def get_page_content(self, url: str) -> BeautifulSoup:
        """Sayfa içeriğini alır"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Random user agent kullanılıyorsa güncelle
                self._update_user_agent_if_needed()
                
                # Proxy rotasyonu
                if attempt > 0:  # İlk denemede rotasyon yapma
                    self._rotate_proxy()
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
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
                self.logger.error(f"Sayfa alınamadı {url} (Deneme {attempt + 1}/{max_retries}): {e}")
                if self.use_proxy and "proxy" in str(e).lower():
                    self._handle_proxy_failure()
                if attempt == max_retries - 1:
                    return None
                continue
        
        return None
    
    def extract_domains_from_page(self, url: str, soup: BeautifulSoup) -> Set[str]:
        """Sayfa içeriğinden domain'leri çıkarır"""
        domains = set()
        
        # <a> etiketlerinden href'leri al
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if href:
                absolute_url = urljoin(url, href)
                domain = self.extract_domain(absolute_url)
                
                if self.is_valid_domain_format(domain):
                    domains.add(domain)
                    
                    if domain not in self.domain_urls:
                        self.domain_urls[domain] = set()
                    self.domain_urls[domain].add(absolute_url)
        
        # <link> etiketlerinden href'leri al
        for link in soup.find_all('link', href=True):
            href = link['href'].strip()
            if href:
                absolute_url = urljoin(url, href)
                domain = self.extract_domain(absolute_url)
                
                if self.is_valid_domain_format(domain):
                    domains.add(domain)
                    
                    if domain not in self.domain_urls:
                        self.domain_urls[domain] = set()
                    self.domain_urls[domain].add(absolute_url)
        
        # <img> etiketlerinden src'leri al
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            if src:
                absolute_url = urljoin(url, src)
                domain = self.extract_domain(absolute_url)
                
                if self.is_valid_domain_format(domain):
                    domains.add(domain)
                    
                    if domain not in self.domain_urls:
                        self.domain_urls[domain] = set()
                    self.domain_urls[domain].add(absolute_url)
        
        # <script> etiketlerinden src'leri al
        for script in soup.find_all('script', src=True):
            src = script['src'].strip()
            if src:
                absolute_url = urljoin(url, src)
                domain = self.extract_domain(absolute_url)
                
                if self.is_valid_domain_format(domain):
                    domains.add(domain)
                    
                    if domain not in self.domain_urls:
                        self.domain_urls[domain] = set()
                    self.domain_urls[domain].add(absolute_url)
        
        return domains
    
    def detect_domains_from_url(self, url: str) -> Set[str]:
        """Tek bir URL'den domain'leri tespit eder"""
        # Domain engelleme kontrolü
        if self._is_domain_blocked(url):
            self._log_blocked_domain(url)
            return set()
        
        self.logger.info(f"Domain tespiti yapılıyor: {url}")
        
        # Sayfa içeriğini al
        soup = self.get_page_content(url)
        if not soup:
            return set()
        
        # Domain'leri çıkar
        domains = self.extract_domains_from_page(url, soup)
        
        # Bulunan domain'leri kaydet (engelleme kontrolü ile)
        for domain in domains:
            # Domain'in kendisini kontrol et (URL formatında)
            test_url = f"https://{domain}"
            if not self._is_domain_blocked(test_url):
                if domain not in self.found_domains:
                    self.found_domains.add(domain)
                    self.logger.info(f"Yeni domain bulundu: {domain}")
            else:
                self.logger.info(f"🚫 Domain engellendi: {domain}")
        
        return domains
    
    def validate_all_domains(self) -> None:
        """Bulunan tüm domain'leri doğrular"""
        if not self.validate_domains:
            self.valid_domains = self.found_domains.copy()
            return
            
        self.logger.info(f"Domain doğrulama başlatılıyor ({len(self.found_domains)} domain)...")
        
        for i, domain in enumerate(self.found_domains, 1):
            self.logger.info(f"Doğrulanıyor ({i}/{len(self.found_domains)}): {domain}")
            
            if self.validate_domain_exists(domain):
                self.valid_domains.add(domain)
                self.logger.info(f"✅ Geçerli domain: {domain}")
            else:
                self.invalid_domains.add(domain)
                self.logger.warning(f"❌ Geçersiz domain: {domain}")
            
            # Rate limiting
            if i < len(self.found_domains):
                time.sleep(0.1)  # DNS sorguları için kısa bekleme
        
        self.logger.info(f"Domain doğrulama tamamlandı. Geçerli: {len(self.valid_domains)}, Geçersiz: {len(self.invalid_domains)}")
    
    def detect_domains_from_urls(self, urls: List[str]) -> Dict:
        """Birden fazla URL'den domain'leri tespit eder"""
        self.logger.info(f"Toplam {len(urls)} URL'den domain tespiti başlatılıyor")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"İşleniyor ({i}/{len(urls)}): {url}")
            
            try:
                self.detect_domains_from_url(url)
                
                # Rate limiting
                if i < len(urls):
                    time.sleep(self.delay)
                    
            except Exception as e:
                self.logger.error(f"URL işlenirken hata {url}: {e}")
                continue
        
        # Domain doğrulama
        self.validate_all_domains()
        
        # Sonuçları hazırla
        results = {
            'total_domains_found': len(self.found_domains),
            'total_valid_domains': len(self.valid_domains),
            'total_invalid_domains': len(self.invalid_domains),
            'total_urls_processed': len(urls),
            'valid_domains': sorted(list(self.valid_domains)),
            'invalid_domains': sorted(list(self.invalid_domains)) if self.validate_domains else [],
            'validation_enabled': self.validate_domains,
            'analysis_time': time.time()
        }
        
        self.logger.info(f"Domain tespiti tamamlandı. Geçerli: {len(self.valid_domains)} domain bulundu.")
        return results
    
    def filter_domains(self, 
                      domains: List[str] = None,
                      exclude_domains: List[str] = None,
                      tld_filter: List[str] = None) -> List[str]:
        """Domain'leri filtreler"""
        
        if domains is None:
            domains = list(self.valid_domains)
        
        exclude_domains = exclude_domains or []
        tld_filter = tld_filter or []
        
        filtered_domains = []
        
        for domain in domains:
            # Hariç tutulacak domain'ler
            if any(excluded in domain for excluded in exclude_domains):
                continue
            
            # TLD filtresi
            if tld_filter:
                domain_tld = domain.split('.')[-1] if '.' in domain else ''
                if domain_tld not in tld_filter:
                    continue
            
            filtered_domains.append(domain)
        
        return filtered_domains
    
    def save_results(self, results: Dict, filename: str = 'domains.json') -> None:
        """Sonuçları JSON dosyasına kaydet - sadece domain'ler"""
        
        # Sadece geçerli domain'leri kaydet
        simple_results = {
            'domains': results['valid_domains'],
            'total_count': results['total_valid_domains'],
            'validation_enabled': results['validation_enabled'],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Eğer doğrulama kapalıysa, geçersiz domain bilgisini de ekle
        if not results['validation_enabled']:
            simple_results['note'] = 'Domain validation disabled - all found domains included'
        else:
            simple_results['invalid_domains_count'] = results['total_invalid_domains']
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(simple_results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Domain'ler {filename} dosyasına kaydedildi.")
    
    def print_summary(self, results: Dict) -> None:
        """Sonuçların özetini yazdırır"""
        print(f"\n=== DOMAIN TESPİT SONUÇLARI ===")
        print(f"Bulunan toplam domain: {results['total_domains_found']}")
        print(f"Geçerli domain'ler: {results['total_valid_domains']}")
        
        if results['validation_enabled']:
            print(f"Geçersiz domain'ler: {results['total_invalid_domains']}")
        else:
            print("Domain doğrulama: Kapalı")
        
        print(f"İşlenen URL sayısı: {results['total_urls_processed']}")
        
        print(f"\n=== GEÇERLİ DOMAIN'LER ===")
        for i, domain in enumerate(results['valid_domains'][:20], 1):
            print(f"{i}. {domain}")
        
        if len(results['valid_domains']) > 20:
            print(f"... ve {len(results['valid_domains']) - 20} domain daha")
        
        if results['validation_enabled'] and results['invalid_domains']:
            print(f"\n=== GEÇERSİZ DOMAIN'LER (İlk 5) ===")
            for i, domain in enumerate(results['invalid_domains'][:5], 1):
                print(f"{i}. {domain}")
            
            if len(results['invalid_domains']) > 5:
                print(f"... ve {len(results['invalid_domains']) - 5} geçersiz domain daha")
