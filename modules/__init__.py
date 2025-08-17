"""
URL Crawler Modules Package
"""

from .url_crawler import URLCrawler
from .url_utils import URLAnalyzer
from .domain_detector import DomainDetector
from . import config

__version__ = "1.0.0"
__author__ = "Hasan Yasin Yaşar"

__all__ = ['URLCrawler', 'URLAnalyzer', 'DomainDetector', 'config']
