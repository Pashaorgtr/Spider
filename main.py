#!/usr/bin/env python3
"""
Spider Domain Crawler - Ana çalıştırma dosyası

Copyright (c) 2025 Hasan Yasin Yaşar
Licensed under PSH 1.1 (Pasha Software License)

Bu yazılım ticari kullanım için yasaktır.
Ticari lisans için: yasin@pasha.org.tr
Detaylar: LICENSE.md
"""

import argparse
import json
import time
import os
from datetime import datetime
from modules.config import DEFAULT_EXCLUDED_EXTENSIONS
from domain_crawler import crawl_and_detect_domains, spider_crawl_domains, enhanced_spider_crawl_domains

def save_results(results, filename=None):
    """Sonuçları JSON dosyasına kaydet"""
    # Data klasörünü oluştur (yoksa)
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"domain_results_{timestamp}.json"
    
    # Dosya yolunu data klasörü ile birleştir
    if not filename.startswith(data_dir):
        filepath = os.path.join(data_dir, filename)
    else:
        filepath = filename
    
    # Sonuçları güzelleştir
    results['timestamp'] = datetime.now().isoformat()
    results['excluded_extensions'] = results.get('excluded_extensions', DEFAULT_EXCLUDED_EXTENSIONS)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sonuçlar kaydedildi: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='Domain Crawler - URL\'lerden domain tespit eder')
    parser.add_argument('urls', nargs='+', help='Crawl edilecek URL\'ler')
    parser.add_argument('--spider', action='store_true', help='Spider crawl modu (zincirleme domain keşfi)')
    parser.add_argument('--enhanced-spider', action='store_true', help='Gelişmiş spider crawl (hem sayfa hem domain zincirleme)')
    parser.add_argument('--spider-depth', type=int, default=3, help='Spider crawl derinliği (varsayılan: 3)')
    parser.add_argument('--spider-domains-per-level', type=int, default=20, help='Seviye başına max domain (varsayılan: 20)')
    parser.add_argument('--spider-max-domains', type=int, default=100, help='Toplam max domain (varsayılan: 100)')
    parser.add_argument('--spider-max-pages-per-domain', type=int, default=50, help='Domain başına max sayfa (gelişmiş spider için, varsayılan: 50)')
    parser.add_argument('--crawler-delay', type=float, default=1.0, help='Crawler gecikme süresi (varsayılan: 1.0)')
    parser.add_argument('--crawler-depth', type=int, default=2, help='Crawler derinliği (varsayılan: 2)')
    parser.add_argument('--crawler-max-urls', type=int, default=50, help='Crawler max URL (varsayılan: 50)')
    parser.add_argument('--detector-delay', type=float, default=0.5, help='Detector gecikme süresi (varsayılan: 0.5)')
    parser.add_argument('--detector-timeout', type=int, default=10, help='Detector timeout (varsayılan: 10)')
    parser.add_argument('--no-validation', action='store_true', help='Domain doğrulamasını devre dışı bırak')
    parser.add_argument('--output', '-o', help='Çıktı dosyası adı (data/ klasörüne kaydedilir)')
    parser.add_argument('--exclude-extensions', nargs='*', help='Hariç tutulacak dosya uzantıları (örn: --exclude-extensions .pdf .jpg)')
    parser.add_argument('--include-all-extensions', action='store_true', help='Tüm dosya uzantılarını dahil et (filtreleme yapma)')
    parser.add_argument('--random-user-agent', action='store_true', help='Random user agent kullan (her istekte farklı)')
    parser.add_argument('--random-user-agent-per-session', action='store_true', help='Oturum başına random user agent kullan')
    parser.add_argument('--proxy', nargs='*', help='Kullanılacak proxy listesi (örn: --proxy http://proxy1:8080 socks5://proxy2:1080)')
    parser.add_argument('--proxy-file', help='Proxy listesini içeren dosya yolu')
    parser.add_argument('--no-proxy-rotation', action='store_true', help='Proxy rotasyonunu devre dışı bırak')
    parser.add_argument('--block-domains', nargs='*', help='Engellenecek domain listesi (örn: --block-domains google.com facebook.com)')
    parser.add_argument('--block-domains-file', help='Engellenecek domain listesini içeren dosya yolu')
    parser.add_argument('--use-default-blocked-domains', action='store_true', help='Varsayılan engellenen domain listesini kullan')
    
    args = parser.parse_args()
    
    # Random user agent ayarları
    use_random_user_agent = args.random_user_agent or args.random_user_agent_per_session
    if use_random_user_agent:
        # Config dosyasındaki ayarları güncelle
        from modules.config import RANDOM_USER_AGENT_PER_REQUEST, RANDOM_USER_AGENT_PER_SESSION
        import modules.config as config
        
        if args.random_user_agent_per_session:
            config.RANDOM_USER_AGENT_PER_SESSION = True
            config.RANDOM_USER_AGENT_PER_REQUEST = False
            print("🎭 Random user agent modu: Oturum başına farklı user agent")
        else:
            config.RANDOM_USER_AGENT_PER_SESSION = False
            config.RANDOM_USER_AGENT_PER_REQUEST = True
            print("🎭 Random user agent modu: Her istekte farklı user agent")
    else:
        print("🎭 Sabit user agent: Tarassut 1.0")
    
    # Proxy ayarları
    proxy_list = []
    use_proxy = False
    
    if args.proxy:
        proxy_list.extend(args.proxy)
        use_proxy = True
        print(f"🌐 Proxy modu: Komut satırından {len(args.proxy)} proxy")
    
    if args.proxy_file:
        try:
            with open(args.proxy_file, 'r', encoding='utf-8') as f:
                file_proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                proxy_list.extend(file_proxies)
                use_proxy = True
                print(f"🌐 Proxy modu: Dosyadan {len(file_proxies)} proxy yüklendi")
        except FileNotFoundError:
            print(f"❌ Proxy dosyası bulunamadı: {args.proxy_file}")
            return 1
        except Exception as e:
            print(f"❌ Proxy dosyası okuma hatası: {e}")
            return 1
    
    if use_proxy:
        # Config dosyasındaki proxy ayarlarını güncelle
        import modules.config as config
        if args.no_proxy_rotation:
            config.PROXY_ROTATION = False
            print("🌐 Proxy rotasyonu: Kapalı")
        else:
            config.PROXY_ROTATION = True
            print("🌐 Proxy rotasyonu: Açık")
        
        print(f"🌐 Toplam proxy sayısı: {len(proxy_list)}")
        for i, proxy in enumerate(proxy_list[:3], 1):  # İlk 3 proxy'yi göster
            print(f"   {i}. {proxy}")
        if len(proxy_list) > 3:
            print(f"   ... ve {len(proxy_list) - 3} proxy daha")
    else:
        print("🌐 Proxy kullanılmıyor")
    
    # Domain engelleme ayarları
    from modules.config import USE_DOMAIN_BLOCKING, DEFAULT_BLOCKED_DOMAINS
    blocked_domains = []
    use_domain_blocking = USE_DOMAIN_BLOCKING  # Config'den varsayılan değeri al
    
    # Eğer varsayılan domain engelleme açıksa, varsayılan domain'leri ekle
    if USE_DOMAIN_BLOCKING:
        blocked_domains.extend(DEFAULT_BLOCKED_DOMAINS)
        print(f"🚫 Domain engelleme: Varsayılan olarak aktif ({len(DEFAULT_BLOCKED_DOMAINS)} domain)")
    
    if args.block_domains:
        blocked_domains.extend(args.block_domains)
        use_domain_blocking = True
        print(f"🚫 Domain engelleme: Komut satırından {len(args.block_domains)} domain eklendi")
    
    if args.block_domains_file:
        try:
            with open(args.block_domains_file, 'r', encoding='utf-8') as f:
                file_domains = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
                blocked_domains.extend(file_domains)
                use_domain_blocking = True
                print(f"🚫 Domain engelleme: Dosyadan {len(file_domains)} domain yüklendi")
        except FileNotFoundError:
            print(f"❌ Domain engelleme dosyası bulunamadı: {args.block_domains_file}")
            return 1
        except Exception as e:
            print(f"❌ Domain engelleme dosyası okuma hatası: {e}")
            return 1
    
    if args.use_default_blocked_domains:
        # Zaten varsayılan olarak eklendiyse, sadece bilgi ver
        if not USE_DOMAIN_BLOCKING:
            blocked_domains.extend(DEFAULT_BLOCKED_DOMAINS)
            use_domain_blocking = True
        print(f"🚫 Domain engelleme: Varsayılan domain'ler manuel olarak eklendi")
    
    if use_domain_blocking:
        # Duplikatları kaldır
        blocked_domains = list(set(blocked_domains))
        print(f"🚫 Toplam engellenen domain sayısı: {len(blocked_domains)}")
        
        # İlk birkaç domain'i göster
        for i, domain in enumerate(blocked_domains[:5], 1):
            print(f"   {i}. {domain}")
        if len(blocked_domains) > 5:
            print(f"   ... ve {len(blocked_domains) - 5} domain daha")
    else:
        print("🚫 Domain engelleme kullanılmıyor")
    
    # Excluded extensions ayarları
    if args.include_all_extensions:
        excluded_extensions = []
        print("📄 Tüm dosya uzantıları dahil edilecek (filtreleme yok)")
    elif args.exclude_extensions is not None:
        excluded_extensions = args.exclude_extensions
        print(f"📄 Özel hariç tutulan uzantılar: {excluded_extensions}")
    else:
        excluded_extensions = DEFAULT_EXCLUDED_EXTENSIONS
        print(f"📄 Varsayılan hariç tutulan uzantılar kullanılıyor: {len(excluded_extensions)} adet")
    
    print(f"🚀 Domain Crawler başlatılıyor...")
    print(f"📋 İşlenecek URL'ler: {len(args.urls)}")
    for i, url in enumerate(args.urls, 1):
        print(f"   {i}. {url}")
    
    start_time = time.time()
    
    try:
        if args.enhanced_spider:
            print(f"\n🕸️  GELİŞMİŞ SPIDER CRAWL MODU (Sayfa + Domain Zincirleme)")
            results = enhanced_spider_crawl_domains(
                args.urls,
                max_depth=args.spider_depth,
                max_domains_per_level=args.spider_domains_per_level,
                max_total_domains=args.spider_max_domains,
                max_pages_per_domain=args.spider_max_pages_per_domain,
                excluded_extensions=excluded_extensions,
                use_random_user_agent=use_random_user_agent,
                use_proxy=use_proxy,
                proxy_list=proxy_list,
                blocked_domains=blocked_domains,
                use_domain_blocking=use_domain_blocking
            )
        elif args.spider:
            print(f"\n🕸️  SPIDER CRAWL MODU (Sadece Domain Zincirleme)")
            results = spider_crawl_domains(
                args.urls,
                max_depth=args.spider_depth,
                max_domains_per_level=args.spider_domains_per_level,
                max_total_domains=args.spider_max_domains,
                excluded_extensions=excluded_extensions,
                use_random_user_agent=use_random_user_agent,
                use_proxy=use_proxy,
                proxy_list=proxy_list,
                blocked_domains=blocked_domains,
                use_domain_blocking=use_domain_blocking
            )
        else:
            print(f"\n🔍 NORMAL CRAWL MODU")
            
            # Crawler ayarları
            crawler_settings = {
                'delay': args.crawler_delay,
                'max_depth': args.crawler_depth,
                'max_urls': args.crawler_max_urls,
                'excluded_extensions': excluded_extensions,
                'use_random_user_agent': use_random_user_agent,
                'use_proxy': use_proxy,
                'proxy_list': proxy_list,
                'blocked_domains': blocked_domains,
                'use_domain_blocking': use_domain_blocking
            }
            
            # Detector ayarları
            detector_settings = {
                'delay': args.detector_delay,
                'timeout': args.detector_timeout,
                'validate_domains': not args.no_validation,
                'use_random_user_agent': use_random_user_agent,
                'use_proxy': use_proxy,
                'proxy_list': proxy_list,
                'blocked_domains': blocked_domains,
                'use_domain_blocking': use_domain_blocking
            }
            
            crawl_results, domain_results, detector = crawl_and_detect_domains(
                args.urls, crawler_settings, detector_settings
            )
            
            # Sonuçları birleştir
            results = {
                **domain_results,
                'crawl_stats': crawl_results,
                'excluded_extensions': excluded_extensions
            }
        
        # Çalışma süresini hesapla
        execution_time = time.time() - start_time
        results['execution_time_seconds'] = round(execution_time, 2)
        
        print(f"\n⏱️  Toplam çalışma süresi: {execution_time:.2f} saniye")
        
        # Sonuçları kaydet
        output_file = save_results(results, args.output)
        
        # Özet bilgileri göster
        print(f"\n📊 ÖZET BİLGİLER:")
        print(f"   Toplam bulunan domain: {results['total_domains_found']}")
        print(f"   Geçerli domain'ler: {results['total_valid_domains']}")
        print(f"   Geçersiz domain'ler: {results['total_invalid_domains']}")
        print(f"   Hariç tutulan uzantı sayısı: {len(excluded_extensions)}")
        
        if args.enhanced_spider:
            print(f"   Toplam bulunan sayfa: {results.get('total_pages_found', 0)}")
            print(f"   Spider derinliği: {results['spider_depth']}")
            print(f"   İşlenen domain sayısı: {results['processed_domains']}")
            print(f"   Domain başına max sayfa: {results.get('max_pages_per_domain', 0)}")
            print(f"   Crawl stratejisi: {results.get('crawl_strategy', 'N/A')}")
        elif args.spider:
            print(f"   Spider derinliği: {results['spider_depth']}")
            print(f"   İşlenen domain sayısı: {results['processed_domains']}")
        
        # İlk 10 domain'i göster
        if results['valid_domains']:
            print(f"\n🎯 İlk 10 geçerli domain:")
            for i, domain in enumerate(results['valid_domains'][:10], 1):
                print(f"   {i:2d}. {domain}")
            
            if len(results['valid_domains']) > 10:
                print(f"   ... ve {len(results['valid_domains']) - 10} domain daha")
        
        # Enhanced spider için sayfa örnekleri göster
        if args.enhanced_spider and results.get('found_pages'):
            print(f"\n📄 İlk 5 bulunan sayfa:")
            for i, page in enumerate(results['found_pages'][:5], 1):
                print(f"   {i:2d}. {page}")
            
            if len(results['found_pages']) > 5:
                print(f"   ... ve {len(results['found_pages']) - 5} sayfa daha")
        
        print(f"\n✅ İşlem başarıyla tamamlandı!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  İşlem kullanıcı tarafından durduruldu")
        return 1
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
