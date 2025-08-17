"""
URL Yardımcı Fonksiyonları
URL filtreleme, analiz ve işleme araçları
"""

from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Set
import re
from collections import Counter

class URLAnalyzer:
    """URL analiz ve filtreleme sınıfı"""
    
    def __init__(self):
        self.common_file_extensions = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
            'media': ['.mp4', '.avi', '.mov', '.mp3', '.wav', '.flv'],
            'archives': ['.zip', '.rar', '.tar', '.gz', '.7z'],
            'code': ['.js', '.css', '.xml', '.json']
        }
    
    def categorize_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        URL'leri kategorilere ayırır
        
        Args:
            urls: URL listesi
            
        Returns:
            Kategorilere ayrılmış URL'ler
        """
        categories = {
            'pages': [],
            'images': [],
            'documents': [],
            'media': [],
            'archives': [],
            'code': [],
            'external': [],
            'other': []
        }
        
        for url in urls:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Dosya uzantısını kontrol et
            categorized = False
            for category, extensions in self.common_file_extensions.items():
                if any(path.endswith(ext) for ext in extensions):
                    categories[category].append(url)
                    categorized = True
                    break
            
            if not categorized:
                # Uzantısı yoksa veya HTML ise sayfa olarak kategorize et
                if not path or path.endswith('/') or path.endswith('.html') or path.endswith('.htm'):
                    categories['pages'].append(url)
                else:
                    categories['other'].append(url)
        
        return categories
    
    def filter_by_domain(self, urls: List[str], allowed_domains: List[str] = None, 
                        blocked_domains: List[str] = None) -> List[str]:
        """
        Domain'e göre URL'leri filtreler
        
        Args:
            urls: URL listesi
            allowed_domains: İzin verilen domain'ler
            blocked_domains: Engellenen domain'ler
            
        Returns:
            Filtrelenmiş URL listesi
        """
        filtered_urls = []
        
        for url in urls:
            domain = urlparse(url).netloc.lower()
            
            # Blocked domains kontrolü
            if blocked_domains and any(blocked in domain for blocked in blocked_domains):
                continue
            
            # Allowed domains kontrolü
            if allowed_domains and not any(allowed in domain for allowed in allowed_domains):
                continue
            
            filtered_urls.append(url)
        
        return filtered_urls
    
    def filter_by_pattern(self, urls: List[str], include_patterns: List[str] = None,
                         exclude_patterns: List[str] = None) -> List[str]:
        """
        Regex pattern'lere göre URL'leri filtreler
        
        Args:
            urls: URL listesi
            include_patterns: Dahil edilecek pattern'ler
            exclude_patterns: Hariç tutulacak pattern'ler
            
        Returns:
            Filtrelenmiş URL listesi
        """
        filtered_urls = []
        
        for url in urls:
            # Exclude patterns kontrolü
            if exclude_patterns:
                if any(re.search(pattern, url, re.IGNORECASE) for pattern in exclude_patterns):
                    continue
            
            # Include patterns kontrolü
            if include_patterns:
                if not any(re.search(pattern, url, re.IGNORECASE) for pattern in include_patterns):
                    continue
            
            filtered_urls.append(url)
        
        return filtered_urls
    
    def get_domain_statistics(self, urls: List[str]) -> Dict[str, int]:
        """
        Domain istatistiklerini döndürür
        
        Args:
            urls: URL listesi
            
        Returns:
            Domain sayıları
        """
        domains = [urlparse(url).netloc for url in urls]
        return dict(Counter(domains))
    
    def get_url_parameters(self, urls: List[str]) -> Dict[str, Set[str]]:
        """
        URL parametrelerini analiz eder
        
        Args:
            urls: URL listesi
            
        Returns:
            Parametre adları ve değerleri
        """
        all_params = {}
        
        for url in urls:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            for param_name, param_values in params.items():
                if param_name not in all_params:
                    all_params[param_name] = set()
                all_params[param_name].update(param_values)
        
        return all_params
    
    def find_similar_urls(self, urls: List[str], similarity_threshold: float = 0.8) -> List[List[str]]:
        """
        Benzer URL'leri gruplar
        
        Args:
            urls: URL listesi
            similarity_threshold: Benzerlik eşiği
            
        Returns:
            Benzer URL grupları
        """
        from difflib import SequenceMatcher
        
        groups = []
        processed = set()
        
        for i, url1 in enumerate(urls):
            if url1 in processed:
                continue
            
            similar_group = [url1]
            processed.add(url1)
            
            for j, url2 in enumerate(urls[i+1:], i+1):
                if url2 in processed:
                    continue
                
                similarity = SequenceMatcher(None, url1, url2).ratio()
                if similarity >= similarity_threshold:
                    similar_group.append(url2)
                    processed.add(url2)
            
            if len(similar_group) > 1:
                groups.append(similar_group)
        
        return groups
    
    def clean_urls(self, urls: List[str]) -> List[str]:
        """
        URL'leri temizler (fragment'ları kaldırır, normalize eder)
        
        Args:
            urls: URL listesi
            
        Returns:
            Temizlenmiş URL listesi
        """
        cleaned_urls = []
        
        for url in urls:
            parsed = urlparse(url)
            # Fragment'ı kaldır, query'yi koru
            cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                cleaned_url += f"?{parsed.query}"
            
            cleaned_urls.append(cleaned_url)
        
        return list(set(cleaned_urls))  # Duplikatları kaldır
