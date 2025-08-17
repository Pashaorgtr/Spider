#!/usr/bin/env python3
"""
Spider Domain Crawler - Spider Chain Domain Tespit Aracı
Web sayfalarından domain'leri tespit eder ve zincirleme crawl yapar

Copyright (c) 2025 Hasan Yasin Yaşar
Licensed under PSH 1.1 (Pasha Software License)

Bu yazılım ticari kullanım için yasaktır.
Ticari lisans için: yasin@pasha.org.tr
Detaylar: LICENSE.md
"""

from modules.url_crawler import URLCrawler
from modules.domain_detector import DomainDetector
import argparse
import sys
import logging
import time

def setup_logging(level='INFO'):
    """Logging ayarlarını yapar"""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def crawl_and_detect_domains(start_urls, crawler_settings, detector_settings):
    """URL'leri crawl eder ve domain'leri tespit eder"""
    
    # URL Crawler ile URL'leri topla
    print("🕷️  URL Crawling başlatılıyor...")
    crawler = URLCrawler(**crawler_settings)
    crawl_results = crawler.crawl(start_urls)
    
    print(f"✅ Crawling tamamlandı: {crawl_results['total_found']} URL bulundu")
    
    # Tüm URL'leri birleştir (başlangıç + bulunan)
    all_urls = list(set(start_urls + crawl_results['found_urls']))
    
    # Domain Detector ile domain'leri tespit et
    print(f"🔍 Domain tespiti başlatılıyor ({len(all_urls)} URL)...")
    detector = DomainDetector(**detector_settings)
    domain_results = detector.detect_domains_from_urls(all_urls)
    
    return crawl_results, domain_results, detector

def spider_crawl_domains(initial_urls, max_depth=3, max_domains_per_level=20, max_total_domains=100, 
                        excluded_extensions=None, use_random_user_agent=False, use_proxy=False, proxy_list=None,
                        blocked_domains=None, use_domain_blocking=False):
    """Spider crawl - bulunan domain'leri zincirleme crawl eder (Orijinal versiyon)"""
    
    all_domains = set()
    processed_domains = set()
    current_urls = initial_urls.copy()
    
    print(f"🕸️  SPIDER CRAWL BAŞLATIYOR")
    print(f"   Maksimum derinlik: {max_depth}")
    print(f"   Seviye başına max domain: {max_domains_per_level}")
    print(f"   Toplam max domain: {max_total_domains}")
    print(f"   Başlangıç URL'leri: {len(initial_urls)}")
    
    # Excluded extensions bilgisini göster
    if excluded_extensions is None:
        from modules.config import DEFAULT_EXCLUDED_EXTENSIONS
        excluded_extensions = DEFAULT_EXCLUDED_EXTENSIONS
        print(f"   Hariç tutulan uzantılar: {len(excluded_extensions)} adet (varsayılan)")
    else:
        print(f"   Hariç tutulan uzantılar: {excluded_extensions}")
    
    for depth in range(max_depth):
        if len(all_domains) >= max_total_domains:
            print(f"⚠️  Maksimum domain sayısına ulaşıldı ({max_total_domains})")
            break
            
        if not current_urls:
            print(f"⚠️  İşlenecek URL kalmadı")
            break
        
        print(f"\n🔄 SEVİYE {depth + 1} - {len(current_urls)} URL işlenecek")
        
        # Bu seviyedeki tüm URL'leri işle
        level_domains = set()
        
        for i, url in enumerate(current_urls, 1):
            if len(all_domains) >= max_total_domains:
                print(f"⚠️  Maksimum domain sayısına ulaşıldı, seviye durduruluyor")
                break
                
            print(f"  🔍 ({i}/{len(current_urls)}) İşleniyor: {url}")
            
            # Her URL için ayrı crawling yap
            crawler_settings = {
                'delay': 1.0,
                'max_depth': 2,  # Her domain için daha derin crawl
                'max_urls': 30,   # Her domain için daha fazla URL
                'excluded_extensions': excluded_extensions,  # Dosya uzantısı filtresi
                'use_random_user_agent': use_random_user_agent,
                'use_proxy': use_proxy,
                'proxy_list': proxy_list,
                'blocked_domains': blocked_domains,
                'use_domain_blocking': use_domain_blocking
            }
            
            detector_settings = {
                'delay': 0.5,    # Daha hızlı domain tespiti
                'timeout': 10,
                'validate_domains': True,
                'use_random_user_agent': use_random_user_agent,
                'use_proxy': use_proxy,
                'proxy_list': proxy_list,
                'blocked_domains': blocked_domains,
                'use_domain_blocking': use_domain_blocking
            }
            
            try:
                # Bu URL'yi crawl et ve domain'leri tespit et
                crawl_results, domain_results, detector = crawl_and_detect_domains(
                    [url], crawler_settings, detector_settings
                )
                
                # Yeni domain'leri ekle
                new_domains = set(domain_results['valid_domains']) - all_domains
                level_domains.update(new_domains)
                all_domains.update(new_domains)
                
                print(f"    ✅ {len(new_domains)} yeni domain bulundu")
                print(f"    📄 {crawl_results['total_found']} URL crawl edildi (filtrelenmiş)")
                
                # İlk birkaç yeni domain'i göster
                if new_domains:
                    for j, domain in enumerate(list(new_domains)[:3], 1):
                        print(f"      {j}. {domain}")
                    if len(new_domains) > 3:
                        print(f"      ... ve {len(new_domains) - 3} domain daha")
                
                # Rate limiting
                if i < len(current_urls):
                    time.sleep(1)
                    
            except Exception as e:
                print(f"    ❌ Hata: {e}")
                continue
        
        print(f"📊 Seviye {depth + 1} sonuçları:")
        print(f"   Bu seviyede yeni domain'ler: {len(level_domains)}")
        print(f"   Toplam domain'ler: {len(all_domains)}")
        
        # Bu seviyede bulunan domain'lerin özetini göster
        if level_domains:
            print(f"   Seviye {depth + 1} domain'leri:")
            for i, domain in enumerate(list(level_domains)[:5], 1):
                print(f"     {i}. {domain}")
            if len(level_domains) > 5:
                print(f"     ... ve {len(level_domains) - 5} domain daha")
        
        # İşlenmiş domain'leri kaydet
        processed_domains.update([detector.extract_domain(url) for url in current_urls])
        
        # Bir sonraki seviye için URL'leri hazırla
        # Bu seviyede bulunan yeni domain'lerden henüz işlenmemiş olanları seç
        next_domains = []
        for domain in level_domains:
            if (domain not in processed_domains and 
                len(next_domains) < max_domains_per_level and
                len(all_domains) < max_total_domains):
                next_domains.append(domain)
        
        # Domain'leri URL'lere çevir
        current_urls = [f"https://{domain}" for domain in next_domains]
        
        print(f"   Bir sonraki seviye için: {len(current_urls)} URL hazırlandı")
        
        # Bir sonraki seviye için hazırlanan URL'leri göster
        if current_urls:
            print(f"   Bir sonraki seviye URL'leri:")
            for i, url in enumerate(current_urls[:3], 1):
                print(f"     {i}. {url}")
            if len(current_urls) > 3:
                print(f"     ... ve {len(current_urls) - 3} URL daha")
        
        # Rate limiting
        if depth < max_depth - 1 and current_urls:
            print(f"⏳ Bir sonraki seviye için 3 saniye bekleniyor...")
            time.sleep(3)
    
    print(f"\n🎯 SPIDER CRAWL TAMAMLANDI")
    print(f"   Toplam bulunan domain: {len(all_domains)}")
    print(f"   İşlenen seviye: {depth + 1}")
    print(f"   İşlenen toplam domain: {len(processed_domains)}")
    print(f"   Filtrelenen uzantı sayısı: {len(excluded_extensions) if excluded_extensions else 0}")
    
    # Final sonuçları hazırla
    final_results = {
        'total_domains_found': len(all_domains),
        'total_valid_domains': len(all_domains),
        'total_invalid_domains': 0,
        'total_urls_processed': len(initial_urls),
        'valid_domains': sorted(list(all_domains)),
        'invalid_domains': [],
        'validation_enabled': True,
        'spider_depth': depth + 1,
        'processed_domains': len(processed_domains),
        'excluded_extensions': excluded_extensions,
        'analysis_time': time.time()
    }
    
    return final_results

def enhanced_spider_crawl_domains(initial_urls, max_depth=3, max_domains_per_level=20, max_total_domains=100, 
                                max_pages_per_domain=50, excluded_extensions=None, use_random_user_agent=False,
                                use_proxy=False, proxy_list=None, blocked_domains=None, use_domain_blocking=False):
    """
    Gelişmiş Spider Crawl - Hem sayfa hem domain seviyesinde zincirleme crawl
    
    Args:
        initial_urls: Başlangıç URL'leri
        max_depth: Maksimum crawl derinliği
        max_domains_per_level: Her seviyede işlenecek maksimum domain sayısı
        max_total_domains: Toplam maksimum domain sayısı
        max_pages_per_domain: Her domain için maksimum sayfa sayısı
        excluded_extensions: Hariç tutulacak dosya uzantıları
    """
    
    all_domains = set()
    all_pages = set()
    processed_domains = set()
    current_urls = initial_urls.copy()
    
    print(f"🕸️  GELİŞMİŞ SPIDER CRAWL BAŞLATIYOR")
    print(f"   Maksimum derinlik: {max_depth}")
    print(f"   Seviye başına max domain: {max_domains_per_level}")
    print(f"   Toplam max domain: {max_total_domains}")
    print(f"   Domain başına max sayfa: {max_pages_per_domain}")
    print(f"   Başlangıç URL'leri: {len(initial_urls)}")
    
    # Excluded extensions bilgisini göster
    if excluded_extensions is None:
        from modules.config import DEFAULT_EXCLUDED_EXTENSIONS
        excluded_extensions = DEFAULT_EXCLUDED_EXTENSIONS
        print(f"   Hariç tutulan uzantılar: {len(excluded_extensions)} adet (varsayılan)")
    else:
        print(f"   Hariç tutulan uzantılar: {excluded_extensions}")
    
    for depth in range(max_depth):
        if len(all_domains) >= max_total_domains:
            print(f"⚠️  Maksimum domain sayısına ulaşıldı ({max_total_domains})")
            break
            
        if not current_urls:
            print(f"⚠️  İşlenecek URL kalmadı")
            break
        
        print(f"\n🔄 SEVİYE {depth + 1} - {len(current_urls)} URL işlenecek")
        
        # Bu seviyedeki tüm URL'leri işle
        level_domains = set()
        level_pages = set()
        
        for i, url in enumerate(current_urls, 1):
            if len(all_domains) >= max_total_domains:
                print(f"⚠️  Maksimum domain sayısına ulaşıldı, seviye durduruluyor")
                break
                
            print(f"  🔍 ({i}/{len(current_urls)}) İşleniyor: {url}")
            
            # Her URL için derin sayfa crawling yap
            crawler_settings = {
                'delay': 1.0,
                'max_depth': 3,  # Daha derin sayfa crawling
                'max_urls': max_pages_per_domain,  # Domain başına daha fazla sayfa
                'excluded_extensions': excluded_extensions,
                'use_random_user_agent': use_random_user_agent,
                'use_proxy': use_proxy,
                'proxy_list': proxy_list,
                'blocked_domains': blocked_domains,
                'use_domain_blocking': use_domain_blocking
            }
            
            detector_settings = {
                'delay': 0.5,
                'timeout': 10,
                'validate_domains': True,
                'use_random_user_agent': use_random_user_agent,
                'use_proxy': use_proxy,
                'proxy_list': proxy_list,
                'blocked_domains': blocked_domains,
                'use_domain_blocking': use_domain_blocking
            }
            
            try:
                # Bu URL'yi derin crawl et
                crawl_results, domain_results, detector = crawl_and_detect_domains(
                    [url], crawler_settings, detector_settings
                )
                
                # Bulunan sayfaları kaydet
                found_pages = set(crawl_results['found_urls'])
                new_pages = found_pages - all_pages
                level_pages.update(new_pages)
                all_pages.update(new_pages)
                
                # Yeni domain'leri kaydet
                new_domains = set(domain_results['valid_domains']) - all_domains
                level_domains.update(new_domains)
                all_domains.update(new_domains)
                
                print(f"    ✅ {len(new_domains)} yeni domain, {len(new_pages)} yeni sayfa bulundu")
                print(f"    📄 {crawl_results['total_found']} URL crawl edildi (filtrelenmiş)")
                
                # İlk birkaç yeni domain ve sayfayı göster
                if new_domains:
                    print(f"    🌐 Yeni domain'ler:")
                    for j, domain in enumerate(list(new_domains)[:3], 1):
                        print(f"      {j}. {domain}")
                    if len(new_domains) > 3:
                        print(f"      ... ve {len(new_domains) - 3} domain daha")
                
                if new_pages:
                    print(f"    📄 Yeni sayfalar:")
                    for j, page in enumerate(list(new_pages)[:3], 1):
                        print(f"      {j}. {page}")
                    if len(new_pages) > 3:
                        print(f"      ... ve {len(new_pages) - 3} sayfa daha")
                
                # Rate limiting
                if i < len(current_urls):
                    time.sleep(1)
                    
            except Exception as e:
                print(f"    ❌ Hata: {e}")
                continue
        
        print(f"📊 Seviye {depth + 1} sonuçları:")
        print(f"   Bu seviyede yeni domain'ler: {len(level_domains)}")
        print(f"   Bu seviyede yeni sayfalar: {len(level_pages)}")
        print(f"   Toplam domain'ler: {len(all_domains)}")
        print(f"   Toplam sayfalar: {len(all_pages)}")
        
        # Bu seviyede bulunan domain'lerin özetini göster
        if level_domains:
            print(f"   Seviye {depth + 1} domain'leri:")
            for i, domain in enumerate(list(level_domains)[:5], 1):
                print(f"     {i}. {domain}")
            if len(level_domains) > 5:
                print(f"     ... ve {len(level_domains) - 5} domain daha")
        
        # İşlenmiş domain'leri kaydet
        processed_domains.update([detector.extract_domain(url) for url in current_urls])
        
        # Bir sonraki seviye için URL'leri hazırla
        # Strategi 1: Yeni domain'lerden URL'ler seç
        next_urls_from_domains = []
        for domain in level_domains:
            if (domain not in processed_domains and 
                len(next_urls_from_domains) < max_domains_per_level // 2 and
                len(all_domains) < max_total_domains):
                next_urls_from_domains.append(f"https://{domain}")
        
        # Strateji 2: Yeni sayfalardan URL'ler seç
        next_urls_from_pages = []
        for page in level_pages:
            page_domain = detector.extract_domain(page)
            if (page_domain not in processed_domains and 
                len(next_urls_from_pages) < max_domains_per_level // 2 and
                len(all_domains) < max_total_domains):
                next_urls_from_pages.append(page)
        
        # İki stratejiyi birleştir
        current_urls = next_urls_from_domains + next_urls_from_pages
        
        print(f"   Bir sonraki seviye için: {len(current_urls)} URL hazırlandı")
        print(f"     - Domain'lerden: {len(next_urls_from_domains)} URL")
        print(f"     - Sayfalardan: {len(next_urls_from_pages)} URL")
        
        # Bir sonraki seviye için hazırlanan URL'leri göster
        if current_urls:
            print(f"   Bir sonraki seviye URL'leri:")
            for i, url in enumerate(current_urls[:5], 1):
                print(f"     {i}. {url}")
            if len(current_urls) > 5:
                print(f"     ... ve {len(current_urls) - 5} URL daha")
        
        # Rate limiting
        if depth < max_depth - 1 and current_urls:
            print(f"⏳ Bir sonraki seviye için 3 saniye bekleniyor...")
            time.sleep(3)
    
    print(f"\n🎯 GELİŞMİŞ SPIDER CRAWL TAMAMLANDI")
    print(f"   Toplam bulunan domain: {len(all_domains)}")
    print(f"   Toplam bulunan sayfa: {len(all_pages)}")
    print(f"   İşlenen seviye: {depth + 1}")
    print(f"   İşlenen toplam domain: {len(processed_domains)}")
    print(f"   Filtrelenen uzantı sayısı: {len(excluded_extensions) if excluded_extensions else 0}")
    
    # Final sonuçları hazırla
    final_results = {
        'total_domains_found': len(all_domains),
        'total_pages_found': len(all_pages),
        'total_valid_domains': len(all_domains),
        'total_invalid_domains': 0,
        'total_urls_processed': len(initial_urls),
        'valid_domains': sorted(list(all_domains)),
        'found_pages': sorted(list(all_pages)),
        'invalid_domains': [],
        'validation_enabled': True,
        'spider_depth': depth + 1,
        'processed_domains': len(processed_domains),
        'max_pages_per_domain': max_pages_per_domain,
        'excluded_extensions': excluded_extensions,
        'analysis_time': time.time(),
        'crawl_strategy': 'enhanced_spider_both_page_and_domain'
    }
    
    return final_results
    

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Spider Domain Crawler - Zincirleme domain tespit eder')
    
    # URL parametreleri
    parser.add_argument('urls', nargs='+', help='Crawl edilecek başlangıç URL\'leri')
    
    # Spider ayarları
    parser.add_argument('--spider-depth', type=int, default=3, help='Spider crawl derinliği (varsayılan: 3)')
    parser.add_argument('--domains-per-level', type=int, default=20, help='Seviye başına max domain (varsayılan: 20)')
    parser.add_argument('--max-total-domains', type=int, default=100, help='Toplam max domain (varsayılan: 100)')
    
    # Filtreleme ayarları
    parser.add_argument('--exclude-extensions', nargs='*', help='Hariç tutulacak dosya uzantıları (örn: .css .js .pdf)')
    
    # Çıktı ayarları
    parser.add_argument('--output', type=str, default='spider_domains.json', help='Çıktı dosyası adı')
    parser.add_argument('--verbose', action='store_true', help='Detaylı log göster')
    
    args = parser.parse_args()
    
    # Logging ayarla
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level)
    
    try:
        # Spider crawling başlat
        domain_results = spider_crawl_domains(
            args.urls,
            max_depth=args.spider_depth,
            max_domains_per_level=args.domains_per_level,
            max_total_domains=args.max_total_domains
        )
        
        # Sonuçları kaydet
        detector = DomainDetector()
        detector.save_results(domain_results, args.output)
        
        # Özet göster
        detector.print_summary(domain_results)
        
        print(f"\n📁 Sonuçlar {args.output} dosyasına kaydedildi")
        
    except KeyboardInterrupt:
        print("\n⏹️  İşlem kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def quick_spider_demo():
    """Hızlı spider demo"""
    print("=== SPIDER CRAWL DEMO ===\n")
    
    # Test URL'leri
    test_urls = ['https://pasha.org.tr']
    
    print(f"Demo URL'leri: {test_urls}")
    
    try:
        domain_results = spider_crawl_domains(
            test_urls,
            max_depth=2,
            max_domains_per_level=3,
            max_total_domains=15
        )
        
        detector = DomainDetector()
        detector.print_summary(domain_results)
        
        return domain_results
        
    except Exception as e:
        print(f"Demo hatası: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Argüman verilmemişse demo çalıştır
        quick_spider_demo()
    else:
        main()
