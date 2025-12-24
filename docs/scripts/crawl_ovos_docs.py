#!/usr/bin/env python3
"""
OVOS Technical Manual Web Crawler
Extracts all URLs and documentation content from https://openvoiceos.github.io/ovos-technical-manual/
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from pathlib import Path
from datetime import datetime


class OVOSDocsCrawler:
    def __init__(self, base_url="https://openvoiceos.github.io/ovos-technical-manual/"):
        self.base_url = base_url
        self.visited_urls = set()
        self.all_urls = []
        self.docs_content = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OVOS-EnMS-Skill-Documentation-Crawler/1.0'
        })
    
    def is_valid_url(self, url):
        """Check if URL belongs to OVOS technical manual"""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        
        # Must be same domain and path prefix
        if parsed.netloc != base_parsed.netloc:
            return False
        if not parsed.path.startswith(base_parsed.path.rstrip('/')):
            return False
        
        # Skip certain file types
        skip_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip']
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        return True
    
    def normalize_url(self, url):
        """Remove fragments and normalize URL"""
        parsed = urlparse(url)
        # Keep fragments for anchors but normalize
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.fragment:
            normalized += f"#{parsed.fragment}"
        return normalized
    
    def extract_links(self, soup, current_url):
        """Extract all links from page"""
        links = set()
        
        # Find all anchor tags
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(current_url, href)
            
            # Normalize and validate
            normalized = self.normalize_url(absolute_url)
            if self.is_valid_url(normalized):
                links.add(normalized)
        
        return links
    
    def extract_content(self, soup, url):
        """Extract main content from page"""
        content = {
            'url': url,
            'title': '',
            'headings': [],
            'text': '',
            'code_blocks': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = title_tag.text.strip()
        
        # Extract main content area (adjust selector based on site structure)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            # Extract headings
            for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4']):
                level = heading.name
                text = heading.get_text(strip=True)
                content['headings'].append({
                    'level': level,
                    'text': text,
                    'id': heading.get('id', '')
                })
            
            # Extract text content
            content['text'] = main_content.get_text(separator='\n', strip=True)
            
            # Extract code blocks
            for code_block in main_content.find_all('code'):
                content['code_blocks'].append(code_block.get_text(strip=True))
        
        return content
    
    def crawl(self, url, max_depth=10, delay=0.5):
        """Recursively crawl the documentation site"""
        
        # Check if already visited (without fragment)
        url_no_fragment = url.split('#')[0]
        if url_no_fragment in self.visited_urls:
            return
        
        if max_depth == 0:
            return
        
        try:
            print(f"Crawling: {url}")
            
            # Fetch page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Mark as visited
            self.visited_urls.add(url_no_fragment)
            self.all_urls.append(url)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content
            content = self.extract_content(soup, url)
            self.docs_content[url] = content
            
            # Extract links
            links = self.extract_links(soup, url)
            
            # Crawl found links
            for link in links:
                link_no_fragment = link.split('#')[0]
                if link_no_fragment not in self.visited_urls:
                    time.sleep(delay)  # Be nice to the server
                    self.crawl(link, max_depth - 1, delay)
        
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def save_results(self, output_dir="ovos_docs_crawl"):
        """Save crawl results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save all URLs list
        urls_file = output_path / "urls.txt"
        with open(urls_file, 'w') as f:
            for url in sorted(self.all_urls):
                f.write(f"{url}\n")
        print(f"✅ Saved {len(self.all_urls)} URLs to {urls_file}")
        
        # Save URLs as JSON with metadata
        urls_json = output_path / "urls.json"
        with open(urls_json, 'w') as f:
            json.dump({
                'base_url': self.base_url,
                'crawl_date': datetime.now().isoformat(),
                'total_urls': len(self.all_urls),
                'urls': sorted(self.all_urls)
            }, f, indent=2)
        print(f"✅ Saved URL metadata to {urls_json}")
        
        # Save full content as JSON
        content_json = output_path / "content.json"
        with open(content_json, 'w') as f:
            json.dump(self.docs_content, f, indent=2)
        print(f"✅ Saved full content to {content_json}")
        
        # Create organized markdown summary
        summary_md = output_path / "summary.md"
        with open(summary_md, 'w') as f:
            f.write("# OVOS Technical Manual - Documentation Index\n\n")
            f.write(f"**Crawled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Base URL:** {self.base_url}\n")
            f.write(f"**Total Pages:** {len(self.visited_urls)}\n")
            f.write(f"**Total URLs (with anchors):** {len(self.all_urls)}\n\n")
            
            f.write("## Documentation Structure\n\n")
            
            # Group by page (without fragments)
            pages = {}
            for url in sorted(self.all_urls):
                url_no_fragment = url.split('#')[0]
                fragment = url.split('#')[1] if '#' in url else None
                
                if url_no_fragment not in pages:
                    pages[url_no_fragment] = {
                        'url': url_no_fragment,
                        'title': self.docs_content.get(url, {}).get('title', ''),
                        'anchors': []
                    }
                
                if fragment:
                    pages[url_no_fragment]['anchors'].append(fragment)
            
            # Write organized structure
            for page_url, page_data in pages.items():
                path = urlparse(page_url).path.replace('/ovos-technical-manual/', '')
                title = page_data['title'] or path or 'Home'
                
                f.write(f"### {title}\n")
                f.write(f"- **URL:** {page_url}\n")
                
                if page_data['anchors']:
                    f.write(f"- **Sections ({len(page_data['anchors'])}):**\n")
                    for anchor in sorted(set(page_data['anchors'])):
                        f.write(f"  - `#{anchor}`\n")
                
                # Add headings from content
                content = self.docs_content.get(page_url, {})
                if content.get('headings'):
                    f.write(f"- **Headings:**\n")
                    for heading in content['headings'][:10]:  # Limit to first 10
                        indent = "  " * (int(heading['level'][1]) - 1)
                        f.write(f"{indent}- {heading['text']}\n")
                
                f.write("\n")
        
        print(f"✅ Saved summary to {summary_md}")
        
        # Create simple reference file
        reference_txt = output_path / "reference.txt"
        with open(reference_txt, 'w') as f:
            f.write("OVOS Technical Manual - Quick Reference\n")
            f.write("=" * 60 + "\n\n")
            
            for url in sorted(self.all_urls):
                f.write(f"{url}\n")
        
        print(f"✅ Saved reference to {reference_txt}")
        
        return output_path


def main():
    print("🕷️  OVOS Technical Manual Web Crawler")
    print("=" * 60)
    
    # Initialize crawler
    crawler = OVOSDocsCrawler()
    
    # Start crawling from base URL
    print(f"\n📖 Starting crawl from: {crawler.base_url}\n")
    crawler.crawl(crawler.base_url, max_depth=10, delay=0.5)
    
    # Save results
    print(f"\n💾 Saving results...\n")
    output_dir = crawler.save_results("ovos_docs_crawl")
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ Crawl Complete!")
    print(f"📊 Statistics:")
    print(f"   - Pages crawled: {len(crawler.visited_urls)}")
    print(f"   - Total URLs (with anchors): {len(crawler.all_urls)}")
    print(f"   - Output directory: {output_dir.absolute()}")
    print("\n📁 Files created:")
    print(f"   - urls.txt - Simple list of all URLs")
    print(f"   - urls.json - URLs with metadata")
    print(f"   - content.json - Full page content")
    print(f"   - summary.md - Organized documentation structure")
    print(f"   - reference.txt - Quick reference list")


if __name__ == "__main__":
    main()
