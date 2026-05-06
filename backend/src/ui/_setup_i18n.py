# !/usr/bin/env python3
"""
Script to setup i18n structure for SOAR B2B
Creates TR and EN versions of HTML files with proper SEO tags and JSON loading
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
SOURCE_FILE = BASE_DIR / "soarb2b_home.html"
TR_DIR = BASE_DIR / "tr"
EN_DIR = BASE_DIR / "en"

def setup_i18n():
    # Create directories
    TR_DIR.mkdir(exist_ok=True)
    EN_DIR.mkdir(exist_ok=True)
    
    # Read source file
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create TR version
    tr_content = content.replace('<html lang="en">', '<html lang="tr">')
    tr_content = tr_content.replace(
        '<title>SOAR B2B — Turn Companies Into Booked Meetings</title>',
        '<title>SOAR B2B — Doğru Şirketleri Randevuya Dönüştürün</title>\n    <meta name="description" content="Doğrulanmış işletmelere ulaşın, gerçek karar vericilerle iletişime geçin, temasları randevuya çevirin. Üretici ve toptancılar için B2B randevu motoru.">'
    )
    
    # Add hreflang tags to TR version (after meta description)
    hreflang_tags = """    <!-- SEO hreflang tags -->
    <link rel="alternate" hreflang="tr" href="https://soarb2b.com/ui/tr/soarb2b_home.html" />
    <link rel="alternate" hreflang="en" href="https://soarb2b.com/ui/en/soarb2b_home.html" />
    <link rel="alternate" hreflang="x-default" href="https://soarb2b.com/ui/tr/soarb2b_home.html" />"""
    
    tr_content = tr_content.replace(
        '<meta name="description" content="Doğrulanmış',
        f'<meta name="description" content="Doğrulanmış'
    )
    
    # Insert hreflang after charset meta
    if '<meta name="description"' in tr_content:
        tr_content = tr_content.replace(
            '<meta name="description"',
            hreflang_tags + '\n    <meta name="description"'
        )
    else:
        tr_content = tr_content.replace(
            '<link rel="preconnect"',
            hreflang_tags + '\n    <link rel="preconnect"'
        )
    
    # Create EN version
    en_content = content
    if '<meta name="description"' not in en_content:
        en_content = en_content.replace(
            '<title>SOAR B2B — Turn Companies Into Booked Meetings</title>',
            '<title>SOAR B2B — Turn Companies Into Booked Meetings</title>\n    <meta name="description" content="Reach verified businesses, engage real decision-makers, and convert outreach into meetings. B2B appointment engine for manufacturers and wholesalers.">'
        )
    
    # Add hreflang to EN version
    if '<meta name="description"' in en_content:
        en_content = en_content.replace(
            '<meta name="description"',
            hreflang_tags + '\n    <meta name="description"'
        )
    else:
        en_content = en_content.replace(
            '<link rel="preconnect"',
            hreflang_tags + '\n    <link rel="preconnect"'
        )
    
    # Write files
    tr_file = TR_DIR / "soarb2b_home.html"
    en_file = EN_DIR / "soarb2b_home.html"
    
    with open(tr_file, 'w', encoding='utf-8') as f:
        f.write(tr_content)
    
    with open(en_file, 'w', encoding='utf-8') as f:
        f.write(en_content)
    
    print(f"✓ Created {tr_file}")
    print(f"✓ Created {en_file}")

if __name__ == "__main__":
    setup_i18n()
