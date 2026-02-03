#!/usr/bin/env python3
"""
Improved Site Builder for Black Tom Explosion Case Study
- Better formatting for LCIA Rules, English Arbitration Act
- Full-text search support
- Cross-document hyperlinking
- Proper heading hierarchy and indentation
"""

import os
import re
import json
import fitz  # PyMuPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(BASE_DIR, "site")

# Documents configuration
PDF_DOCUMENTS = {
    "case_study": {
        "file": "The-Black-Tom-Explosion.pdf",
        "title": "The Black Tom Explosion - Case Study",
        "category": "case_study",
        "order": 0
    },
    "protocol_1908": {
        "file": "Protocol-to-the-Treaty-of-Frienship-of-1-January-1908.pdf",
        "title": "Protocol to Treaty of Friendship (1908)",
        "category": "treaties",
        "order": 1
    },
    "treaty_berlin": {
        "file": "Treaty-of-Berlin.pdf",
        "title": "Treaty of Berlin (1921)",
        "category": "treaties",
        "order": 2,
        "text_file": "treaty_berlin_text.txt"
    },
    "supplementary_agreement": {
        "file": "Supplementary-Agreement.pdf",
        "title": "Supplementary Agreement (1922)",
        "category": "treaties",
        "order": 3,
        "text_file": "supplementary_agreement_text.txt"  # Use text file if available
    },
    "soviet_decree": {
        "file": "Soviet-Decree-15-December-1921.pdf",
        "title": "Soviet Decree on Citizenship (1921)",
        "category": "decrees",
        "order": 4
    },
    "rules_procedure": {
        "file": "Rules-of-Procedure.pdf",
        "title": "MCC Rules of Procedure (1922)",
        "category": "procedural",
        "order": 5,
        "text_file": "rules_procedure_text.txt"
    },
    "admin_decision_ii": {
        "file": "Administrative-Decision-II_Extracts.pdf",
        "title": "Administrative Decision II (1923)",
        "category": "mcc_decisions",
        "order": 6
    },
    "mcc_award_1930": {
        "file": "MCC-Award-1930.10.16.pdf",
        "title": "MCC Award (16 Oct 1930)",
        "category": "mcc_decisions",
        "order": 7,
        "text_file": "mcc_award_1930_text.txt"
    },
    "mcc_decision_1931": {
        "file": "MCC-Decision-1931.03.30.pdf",
        "title": "MCC Decision (30 Mar 1931)",
        "category": "mcc_decisions",
        "order": 8,
        "text_file": "mcc_decision_1931_text.txt"
    },
    "mcc_award_1932": {
        "file": "MCC-Award-1932.12.03.pdf",
        "title": "MCC Award (3 Dec 1932)",
        "category": "mcc_decisions",
        "order": 9,
        "text_file": "mcc_award_1932_text.txt"
    },
    "mcc_award_1933": {
        "file": "MCC-Award-1933.12.15.pdf",
        "title": "MCC Award (15 Dec 1933)",
        "category": "mcc_decisions",
        "order": 10
    },
    "resignation_huecking": {
        "file": "Resignation-letter-Huecking-1-March-1939.pdf",
        "title": "Resignation Letter - Huecking (1939)",
        "category": "correspondence",
        "order": 11
    },
    "mcc_award_1939": {
        "file": "MCC-Award-1939.06.15.pdf",
        "title": "MCC Final Award (15 Jun 1939)",
        "category": "mcc_decisions",
        "order": 12
    },
    "letter_thomsen": {
        "file": "Letter-Thomsen-3-October-1939.pdf",
        "title": "Letter from Thomsen (3 Oct 1939)",
        "category": "correspondence",
        "order": 13
    },
    "lcia_rules": {
        "file": "LCIA Rules Effective 1 Oct 2020 With Schedule of Costs 1 Dec 2023.pdf",
        "title": "LCIA Arbitration Rules (2020)",
        "category": "rules",
        "order": 14,
        "text_file": "lcia_rules_text.txt"  # Use our clean text file
    },
    "english_arbitration_act": {
        "file": "English-Arbitration-Act-last-amended-2025.pdf",
        "title": "English Arbitration Act (2025)",
        "category": "legislation",
        "order": 15,
        "text_file": "english_arbitration_act_text.txt"
    },
    "uncitral_transparency": {
        "file": "UNICTRAL-Transparency.pdf",
        "title": "UNCITRAL Transparency Rules",
        "category": "rules",
        "order": 16
    }
}

CATEGORIES = {
    "case_study": {"name": "Case Study", "icon": "📋"},
    "treaties": {"name": "Treaties & Agreements", "icon": "📜"},
    "decrees": {"name": "Decrees", "icon": "⚖️"},
    "procedural": {"name": "Procedural Documents", "icon": "📑"},
    "mcc_decisions": {"name": "MCC Decisions & Awards", "icon": "🏛️"},
    "correspondence": {"name": "Correspondence", "icon": "✉️"},
    "rules": {"name": "Arbitration Rules", "icon": "📖"},
    "legislation": {"name": "Legislation", "icon": "🏛️"}
}


def extract_pdf_text(pdf_path):
    """Extract text from PDF"""
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        for page_num, page in enumerate(doc):
            text = page.get_text("text").strip()
            if text:
                text_parts.append(text)
        doc.close()
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"Error extracting {pdf_path}: {e}")
        return ""


def clean_legislation_text(text):
    """Clean up legislation text by removing navigation elements"""
    # Remove common navigation elements
    patterns_to_remove = [
        r'Status:.*?(?=\n)',
        r'Changes to legislation:.*?(?=\n)',
        r'Extent Information\s*E\d+',
        r'Modifications etc\. \(not altering text\)\s*C\d+',
        r'\(See end of Document for details\)',
        r'View the document on jusmundi\.com',
        r'PAGE \d+',
        r'< BACK TO CONTENTS',
        r'\d+\s*$',  # Lone page numbers
    ]
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def format_lcia_rules(text):
    """Format LCIA Rules with proper structure"""
    html_parts = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Title
        if line == "LCIA ARBITRATION RULES":
            html_parts.append(f'<h1 class="doc-title">{line}</h1>')
            i += 1
            continue
        
        # Subtitle (Effective date)
        if line.startswith("Effective"):
            html_parts.append(f'<p class="doc-subtitle"><em>{line}</em></p>')
            i += 1
            continue
        
        # Major section headers (PREAMBLE, INDEX, ANNEX)
        if line in ["PREAMBLE", "INDEX (in alphabetical order)", "ANNEX TO THE LCIA RULES"]:
            section_id = line.lower().replace(' ', '-').replace('(', '').replace(')', '')
            html_parts.append(f'<h2 class="section-header" id="{section_id}">{line}</h2>')
            i += 1
            continue
        
        # Article headers
        article_match = re.match(r'^ARTICLE\s+(\d+[A-C]?)\s*[-–—]\s*(.+)$', line, re.IGNORECASE)
        if article_match:
            art_num = article_match.group(1)
            art_title = article_match.group(2)
            html_parts.append(f'<h3 class="article-header" id="article-{art_num}"><span class="article-num">Article {art_num}</span> <span class="article-title">{art_title}</span></h3>')
            i += 1
            continue
        
        # Numbered paragraphs (1.1, 9.16, etc.)
        para_match = re.match(r'^(\d+\.\d+)\s+(.*)$', line)
        if para_match:
            para_num = para_match.group(1)
            para_text = para_match.group(2)
            # Collect continuation lines
            j = i + 1
            while j < len(lines) and lines[j].strip() and not re.match(r'^(\d+\.\d+|\(i+\)|\(x+\)|\([a-z]\)|ARTICLE|Paragraph)', lines[j].strip()):
                para_text += ' ' + lines[j].strip()
                j += 1
            html_parts.append(f'<div class="para-block" id="lcia-{para_num.replace(".", "-")}"><span class="para-num">{para_num}</span><p>{para_text}</p></div>')
            i = j
            continue
        
        # Sub-items (i), (ii), (a), (b), etc.
        sub_match = re.match(r'^\((i+|x+|[a-z]|[ivx]+)\)\s+(.*)$', line, re.IGNORECASE)
        if sub_match:
            sub_num = sub_match.group(1)
            sub_text = sub_match.group(2)
            # Collect continuation lines
            j = i + 1
            while j < len(lines) and lines[j].strip() and not re.match(r'^(\d+\.\d+|\(i+\)|\(x+\)|\([a-z]\)|ARTICLE|Paragraph)', lines[j].strip()):
                sub_text += ' ' + lines[j].strip()
                j += 1
            html_parts.append(f'<div class="sub-para"><span class="sub-num">({sub_num})</span><p>{sub_text}</p></div>')
            i = j
            continue
        
        # Paragraph headers in Annex
        para_header_match = re.match(r'^Paragraph\s+(\d+):\s*(.*)$', line)
        if para_header_match:
            para_num = para_header_match.group(1)
            para_text = para_header_match.group(2)
            j = i + 1
            while j < len(lines) and lines[j].strip() and not re.match(r'^Paragraph\s+\d+:', lines[j].strip()):
                para_text += ' ' + lines[j].strip()
                j += 1
            html_parts.append(f'<div class="para-block" id="annex-para-{para_num}"><span class="para-num">Paragraph {para_num}:</span><p>{para_text}</p></div>')
            i = j
            continue
        
        # Index entries
        if ':' in line and 'see Article' in line:
            parts = line.split(':', 1)
            term = parts[0].strip()
            ref = parts[1].strip()
            html_parts.append(f'<div class="index-entry"><strong>{term}:</strong> {ref}</div>')
            i += 1
            continue
        
        # Regular paragraph
        para_text = line
        j = i + 1
        while j < len(lines) and lines[j].strip() and not re.match(r'^(\d+\.\d+|\(i+\)|\(x+\)|\([a-z]\)|ARTICLE|Paragraph|INDEX)', lines[j].strip()):
            para_text += ' ' + lines[j].strip()
            j += 1
        html_parts.append(f'<p>{para_text}</p>')
        i = j
    
    return '\n'.join(html_parts)


def format_treaty(text):
    """Format treaty/agreement documents with proper structure"""
    html_parts = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Main title
        if line == "SUPPLEMENTARY AGREEMENT":
            html_parts.append(f'<h1 class="doc-title" style="text-align: center;">{line}</h1>')
            i += 1
            continue
        
        # Subtitle (parties)
        if line.startswith("Germany and United States"):
            html_parts.append(f'<p class="doc-subtitle" style="text-align: center;"><em>{line}</em></p>')
            i += 1
            continue
        
        # Agreement description
        if line.startswith("Agreement supplementary"):
            html_parts.append(f'<p class="doc-subtitle" style="text-align: center;">{line}</p>')
            i += 1
            continue
        
        # Document number
        if line.startswith("No. "):
            html_parts.append(f'<p class="doc-number" style="text-align: center; font-weight: bold;">{line}</p>')
            i += 1
            continue
        
        # Long title (AGREEMENT BETWEEN...)
        if line.startswith("AGREEMENT BETWEEN"):
            # Collect continuation
            full_title = line
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("German and English"):
                full_title += ' ' + lines[j].strip()
                j += 1
            html_parts.append(f'<h2 class="section-header" style="text-align: center; font-size: 14pt;">{full_title}</h2>')
            i = j
            continue
        
        # Registration note
        if line.startswith("German and English"):
            html_parts.append(f'<p class="doc-note" style="text-align: center; font-style: italic; margin-bottom: 20px;">{line}</p>')
            i += 1
            # Get the registration line too
            if i < len(lines) and "registration" in lines[i].lower():
                html_parts.append(f'<p class="doc-note" style="text-align: center; font-style: italic;">{lines[i].strip()}</p>')
                i += 1
            continue
        
        # Section headers
        if line in ["PREAMBLE", "SIGNATURES", "FOOTNOTES"]:
            html_parts.append(f'<h2 class="section-header">{line}</h2>')
            i += 1
            continue
        
        # Article headers (ARTICLE 1 - TITLE)
        article_match = re.match(r'^ARTICLE\s+(\d+)\s*[-–—]\s*(.+)$', line, re.IGNORECASE)
        if article_match:
            art_num = article_match.group(1)
            art_title = article_match.group(2)
            html_parts.append(f'<h3 class="article-header" id="article-{art_num}"><span class="article-num">Article {art_num}</span> <span class="article-title">{art_title}</span></h3>')
            i += 1
            continue
        
        # President/Plenipotentiary lines
        if line.startswith("The PRESIDENT"):
            html_parts.append(f'<p class="official-title" style="margin-top: 16px;"><strong>{line}</strong></p>')
            i += 1
            continue
        
        # Officials (Dr. WIRTH, Alanson B. HOUGHTON)
        if line.startswith("Dr. ") or line.startswith("Alanson"):
            html_parts.append(f'<p class="official-name" style="margin-left: 24px; font-style: italic;">{line}</p>')
            i += 1
            continue
        
        # Signature blocks
        if line == "Dr. WIRTH" or line == "ALANSON B. HOUGHTON":
            html_parts.append(f'<p class="signature" style="margin-top: 16px; font-weight: bold;">{line}</p>')
            i += 1
            continue
        
        # Sub-items (1), (2), (3)
        sub_match = re.match(r'^\((\d+)\)\s+(.*)$', line)
        if sub_match:
            sub_num = sub_match.group(1)
            sub_text = sub_match.group(2)
            # Collect continuation
            j = i + 1
            while j < len(lines) and lines[j].strip() and not re.match(r'^\(\d+\)|^ARTICLE|^[A-Z]{4,}', lines[j].strip()):
                sub_text += ' ' + lines[j].strip()
                j += 1
            html_parts.append(f'<div class="sub-para"><span class="sub-num">({sub_num})</span><p>{sub_text}</p></div>')
            i = j
            continue
        
        # Footnotes (numbered)
        footnote_match = re.match(r'^(\d+)\.\s+(.*)$', line)
        if footnote_match and "footnote" in text.lower()[:text.lower().find(line)] or "FOOTNOTES" in text[:text.find(line)]:
            fn_num = footnote_match.group(1)
            fn_text = footnote_match.group(2)
            html_parts.append(f'<div class="footnote" style="font-size: 10pt; margin: 8px 0;"><sup>{fn_num}</sup> {fn_text}</div>')
            i += 1
            continue
        
        # Regular paragraph
        para_text = line
        j = i + 1
        while j < len(lines) and lines[j].strip() and not re.match(r'^\(\d+\)|^ARTICLE|^The PRESIDENT|^PREAMBLE|^SIGNATURES|^FOOTNOTES|^[A-Z]{4,}', lines[j].strip()):
            para_text += ' ' + lines[j].strip()
            j += 1
        html_parts.append(f'<p>{para_text}</p>')
        i = j
    
    return '\n'.join(html_parts)


def format_case_study(text):
    """Special formatting for the case study document"""
    lines = text.split('\n')
    html_parts = []
    
    re_header = re.compile(r'^(Introduction|The Facts|The Dispute|The Black Tom Explosion)$')
    re_para_start = re.compile(r'^(\d+)\.\s+(.*)')
    re_copyright = re.compile(r'^©.*')
    
    current_para_lines = []
    current_para_num = None
    
    def flush_para():
        nonlocal current_para_lines, current_para_num
        if current_para_lines:
            text = ' '.join(current_para_lines)
            if current_para_num:
                html_parts.append(f'<div class="para-block" id="para-{current_para_num}"><span class="para-num">{current_para_num}.</span><p>{text}</p></div>')
            else:
                html_parts.append(f'<p>{text}</p>')
            current_para_lines = []
            current_para_num = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if re_copyright.match(line):
            continue
        
        if re_header.match(line):
            flush_para()
            section_id = line.lower().replace(' ', '-')
            html_parts.append(f'<h2 id="section-{section_id}" class="section-header">{line}</h2>')
            continue
        
        m = re_para_start.match(line)
        if m:
            flush_para()
            current_para_num = m.group(1)
            current_para_lines = [m.group(2)]
        else:
            current_para_lines.append(line)
    
    flush_para()
    return '\n'.join(html_parts)


def format_generic_document(text, doc_id):
    """Generic document formatter with improved structure"""
    # Escape HTML
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    lines = text.split('\n')
    html_parts = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Detect main title (all caps, short)
        if line.isupper() and 3 < len(line) < 80:
            if any(kw in line for kw in ['ARTICLE', 'CHAPTER', 'PART', 'SECTION', 'TITLE', 'DECISION', 'AWARD', 'TREATY', 'AGREEMENT', 'RULE', 'DECREE']):
                html_parts.append(f'<h2 class="doc-h2">{line}</h2>')
            else:
                html_parts.append(f'<h3 class="doc-h3">{line}</h3>')
            i += 1
            continue
        
        # Article/Section headers
        article_match = re.match(r'^(Article|Section|Rule|Chapter|Part)\s+(\d+|[IVXLC]+)\.?\s*(.*)', line, re.IGNORECASE)
        if article_match:
            num_part = f"{article_match.group(1)} {article_match.group(2)}"
            title_part = article_match.group(3)
            if title_part:
                html_parts.append(f'<h3 class="doc-article"><span class="article-num">{num_part}.</span> <span class="article-title">{title_part}</span></h3>')
            else:
                html_parts.append(f'<h3 class="doc-article"><span class="article-num">{num_part}</span></h3>')
            i += 1
            continue
        
        # Numbered paragraphs
        numbered_match = re.match(r'^(\d+)\.\s+(.*)$', line)
        if numbered_match:
            num = numbered_match.group(1)
            content = numbered_match.group(2)
            j = i + 1
            while j < len(lines) and lines[j].strip() and not re.match(r'^\d+\.\s+', lines[j].strip()) and not lines[j].strip().isupper():
                content += ' ' + lines[j].strip()
                j += 1
            html_parts.append(f'<div class="para-block" id="para-{doc_id}-{num}"><span class="para-num">{num}.</span><p>{content}</p></div>')
            i = j
            continue
        
        # Sub-items
        paren_match = re.match(r'^\(([a-z0-9ivx]+)\)\s+(.*)$', line, re.IGNORECASE)
        if paren_match:
            num = paren_match.group(1)
            content = paren_match.group(2)
            html_parts.append(f'<div class="sub-para"><span class="sub-num">({num})</span><p>{content}</p></div>')
            i += 1
            continue
        
        # Regular paragraph
        content = line
        j = i + 1
        while j < len(lines) and lines[j].strip() and not re.match(r'^\d+\.\s+', lines[j].strip()) and not lines[j].strip().isupper():
            content += ' ' + lines[j].strip()
            j += 1
        html_parts.append(f'<p>{content}</p>')
        i = j
    
    return '\n'.join(html_parts)


def build_site():
    """Build the complete website"""
    print("Starting improved site build...")
    os.makedirs(SITE_DIR, exist_ok=True)
    
    # Extract and format all documents
    extracted_docs = {}
    
    for doc_id, doc_info in PDF_DOCUMENTS.items():
        print(f"Processing: {doc_info['title']}...")
        
        # Check for text file override
        text_file = doc_info.get('text_file')
        if text_file:
            text_path = os.path.join(BASE_DIR, text_file)
            if os.path.exists(text_path):
                print(f"  Using text file: {text_file}")
                with open(text_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Format based on document type
                if doc_id == 'lcia_rules':
                    html_content = format_lcia_rules(text)
                elif doc_id in ['supplementary_agreement', 'treaty_berlin']:
                    html_content = format_treaty(text)
                else:
                    html_content = format_generic_document(text, doc_id)
                
                extracted_docs[doc_id] = {
                    **doc_info,
                    "content": html_content,
                    "text": text  # Store for search index
                }
                continue
        
        # Extract from PDF
        pdf_path = os.path.join(BASE_DIR, doc_info["file"])
        if os.path.exists(pdf_path):
            text = extract_pdf_text(pdf_path)
            
            if not text.strip():
                # PDF has no extractable text (scanned)
                html_content = '<p class="notice"><em>This document is a scanned image. Please provide the text content for proper display.</em></p>'
                extracted_docs[doc_id] = {
                    **doc_info,
                    "content": html_content,
                    "text": ""
                }
                continue
            
            # Clean up legislation text
            if doc_id == 'english_arbitration_act':
                text = clean_legislation_text(text)
            
            # Format based on document type
            if doc_id == 'case_study':
                # Use .txt file if available
                txt_path = os.path.join(BASE_DIR, "The-Black-Tom-Explosion.txt")
                if os.path.exists(txt_path):
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                html_content = format_case_study(text)
            else:
                html_content = format_generic_document(text, doc_id)
            
            extracted_docs[doc_id] = {
                **doc_info,
                "content": html_content,
                "text": text
            }
        else:
            print(f"  Warning: File not found - {pdf_path}")
    
    # Build search index
    search_index = []
    for doc_id, doc in extracted_docs.items():
        if doc.get("text"):
            search_index.append({
                "id": doc_id,
                "title": doc["title"],
                "content": doc.get("text", "")[:50000]  # Limit for performance
            })
    
    # Generate HTML, CSS, JS
    html = generate_html(extracted_docs)
    css = generate_css()
    js = generate_js(search_index)
    
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    
    with open(os.path.join(SITE_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(css)
    
    with open(os.path.join(SITE_DIR, "app.js"), "w", encoding="utf-8") as f:
        f.write(js)
    
    print(f"\nSite built successfully!")
    print(f"Open: {os.path.join(SITE_DIR, 'index.html')}")
    return os.path.join(SITE_DIR, "index.html")


def generate_html(docs):
    """Generate the complete HTML page"""
    
    # Group documents by category
    categories_html = {cat_id: [] for cat_id in CATEGORIES}
    
    for doc_id, doc in sorted(docs.items(), key=lambda x: x[1].get('order', 99)):
        cat = doc.get('category', 'other')
        if cat in categories_html:
            categories_html[cat].append((doc_id, doc))
    
    # Build navigation
    nav_items = []
    for cat_id, cat_info in CATEGORIES.items():
        if categories_html.get(cat_id):
            nav_items.append(f'''
                <div class="nav-category">
                    <h4>{cat_info["icon"]} {cat_info["name"]}</h4>
                    <ul>
            ''')
            for doc_id, doc in categories_html[cat_id]:
                nav_items.append(f'''
                        <li><a href="#" onclick="showDocument('{doc_id}'); return false;" data-doc="{doc_id}">{doc["title"]}</a></li>
                ''')
            nav_items.append('</ul></div>')
    
    # Build document content sections
    doc_sections = []
    for doc_id, doc in docs.items():
        is_case = doc_id == "case_study"
        doc_sections.append(f'''
            <section class="document-section {'active' if is_case else ''}" id="doc-{doc_id}" data-title="{doc["title"]}">
                <div class="document-header">
                    <h1>{doc["title"]}</h1>
                    <div class="doc-meta">
                        <span class="category-badge">{CATEGORIES.get(doc["category"], {}).get("name", "Document")}</span>
                        <button class="btn-download" onclick="downloadPDF('{doc.get('file', '')}')">📥 Download PDF</button>
                    </div>
                </div>
                <div class="document-content">
                    {doc["content"]}
                </div>
            </section>
        ''')
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Black Tom Explosion - Case Materials</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <button class="sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()" title="Toggle Sidebar">☰</button>
    
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h2>BTE Case</h2>
            <p class="subtitle">Frankfurt Moot 2026</p>
            <button class="collapse-btn" onclick="toggleSidebar()" title="Collapse Sidebar">◀</button>
        </div>
        
        <div class="search-box">
            <input type="text" id="search-input" placeholder="Search all documents..." oninput="handleSearch(this.value)">
            <div id="search-results" class="search-results"></div>
        </div>
        
        <div class="nav-content">
            {''.join(nav_items)}
        </div>
        
        <div class="sidebar-footer">
            <div class="tools-section">
                <h4>Tools</h4>
                <div class="tool-buttons">
                    <button onclick="setTool('pointer')" id="tool-pointer" class="tool-btn active" title="Pointer">👆</button>
                    <button onclick="setTool('highlight')" id="tool-highlight" class="tool-btn" title="Highlight">🖍️</button>
                    <button onclick="setTool('underline')" id="tool-underline" class="tool-btn" title="Underline">U̲</button>
                </div>
                <div class="color-picker">
                    <span class="swatch yellow active" onclick="setColor('yellow')"></span>
                    <span class="swatch green" onclick="setColor('green')"></span>
                    <span class="swatch pink" onclick="setColor('pink')"></span>
                    <span class="swatch blue" onclick="setColor('blue')"></span>
                </div>
                <button class="clear-btn" onclick="clearAnnotations()">Clear All</button>
            </div>
        </div>
    </nav>
    
    <div class="overlay" id="overlay" onclick="closeAllPanels()"></div>
    
    <main class="main-content" id="main-content">
        <div class="content-wrapper">
            {''.join(doc_sections)}
        </div>
    </main>
    
    <aside class="timeline-panel" id="timeline-panel">
        <div class="panel-header">
            <h3>📅 Timeline</h3>
            <button class="close-panel" onclick="closeTimeline()">×</button>
        </div>
        <div class="timeline-content" id="timeline-content"></div>
    </aside>
    
    <button class="fab" onclick="toggleTimeline()" title="Timeline">📅</button>
    
    <script src="app.js"></script>
</body>
</html>'''


def generate_css():
    """Generate CSS with improved styling"""
    return '''/* ===== CSS Variables ===== */
:root {
    --bg-primary: #f8f9fa;
    --bg-secondary: #ffffff;
    --bg-sidebar: #1a202c;
    --bg-sidebar-hover: #2d3748;
    --text-primary: #1a202c;
    --text-secondary: #4a5568;
    --text-sidebar: #e2e8f0;
    --text-muted: #a0aec0;
    --accent: #2563eb;
    --accent-light: #3b82f6;
    --border: #e2e8f0;
    --shadow: 0 2px 8px rgba(0,0,0,0.08);
    
    --highlight-yellow: rgba(254, 240, 138, 0.7);
    --highlight-green: rgba(187, 247, 208, 0.7);
    --highlight-pink: rgba(251, 207, 232, 0.7);
    --highlight-blue: rgba(191, 219, 254, 0.7);
    
    --sidebar-width: 260px;
}

/* ===== Reset ===== */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html { scroll-behavior: smooth; }

body {
    font-family: "Times New Roman", Georgia, serif;
    font-size: 12pt;
    background: var(--bg-primary);
    color: var(--text-primary);
    display: flex;
    min-height: 100vh;
    overflow: hidden;
    line-height: 1.6;
}

/* ===== Sidebar ===== */
.sidebar-toggle {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 200;
    width: 40px;
    height: 40px;
    border: none;
    background: var(--bg-sidebar);
    color: white;
    border-radius: 8px;
    cursor: pointer;
    font-size: 18px;
    display: none;
    box-shadow: var(--shadow);
}

body.sidebar-collapsed .sidebar-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
}

.sidebar {
    width: var(--sidebar-width);
    background: var(--bg-sidebar);
    color: var(--text-sidebar);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    height: 100vh;
    overflow: hidden;
    transition: width 0.25s, transform 0.25s;
}

body.sidebar-collapsed .sidebar {
    width: 0;
    transform: translateX(-100%);
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.sidebar-header h2 {
    font-size: 16px;
    font-weight: 700;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    flex: 1;
}

.sidebar-header .subtitle {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    width: 100%;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.collapse-btn {
    width: 28px;
    height: 28px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 6px;
    font-size: 12px;
}

.collapse-btn:hover {
    background: var(--bg-sidebar-hover);
    color: white;
}

.search-box {
    padding: 12px;
    position: relative;
}

.search-box input {
    width: 100%;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.08);
    color: var(--text-sidebar);
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.search-box input:focus {
    outline: none;
    border-color: var(--accent);
    background: rgba(255,255,255,0.12);
}

.search-box input::placeholder {
    color: var(--text-muted);
}

.search-results {
    position: absolute;
    top: 100%;
    left: 12px;
    right: 12px;
    background: var(--bg-secondary);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    max-height: 400px;
    overflow-y: auto;
    z-index: 100;
    display: none;
}

.search-results.active {
    display: block;
}

.search-result-item {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    color: var(--text-primary);
}

.search-result-item:hover {
    background: var(--bg-primary);
}

.search-result-item .doc-title {
    font-weight: 600;
    font-size: 13px;
    color: var(--accent);
    margin-bottom: 4px;
}

.search-result-item .match-text {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.4;
}

.search-result-item .match-text mark {
    background: var(--highlight-yellow);
    padding: 0 2px;
    border-radius: 2px;
}

.search-highlight {
    background: var(--highlight-yellow);
    color: inherit;
    border-radius: 2px;
    padding: 0 1px;
    animation: highlight-pulse 2s 3;
}

@keyframes highlight-pulse {
    0% { background-color: var(--highlight-yellow); }
    50% { background-color: rgba(253, 224, 71, 0.9); }
    100% { background-color: var(--highlight-yellow); }
}

.nav-content {
    flex: 1;
    overflow-y: auto;
    padding: 8px 0;
}

.nav-category {
    padding: 0 12px;
    margin-bottom: 12px;
}

.nav-category h4 {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    padding: 8px 0 6px;
    font-weight: 600;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.nav-category ul {
    list-style: none;
}

.nav-category li a {
    display: block;
    padding: 8px 10px;
    color: var(--text-sidebar);
    text-decoration: none;
    font-size: 12px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    border-radius: 6px;
    transition: all 0.15s;
    border-left: 3px solid transparent;
}

.nav-category li a:hover {
    background: var(--bg-sidebar-hover);
    border-left-color: var(--accent);
}

.nav-category li a.active {
    background: rgba(37, 99, 235, 0.2);
    border-left-color: var(--accent);
    color: var(--accent-light);
}

.sidebar-footer {
    border-top: 1px solid rgba(255,255,255,0.1);
    padding: 12px;
}

.tools-section h4 {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 8px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.tool-buttons {
    display: flex;
    gap: 6px;
    margin-bottom: 10px;
}

.tool-btn {
    flex: 1;
    padding: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: transparent;
    color: var(--text-sidebar);
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.15s;
}

.tool-btn:hover {
    background: var(--bg-sidebar-hover);
}

.tool-btn.active {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
}

.color-picker {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-bottom: 10px;
}

.swatch {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    cursor: pointer;
    border: 2px solid transparent;
    transition: transform 0.15s;
}

.swatch:hover { transform: scale(1.15); }
.swatch.active { border-color: white; transform: scale(1.2); }
.swatch.yellow { background: #fef08a; }
.swatch.green { background: #bbf7d0; }
.swatch.pink { background: #fbcfe8; }
.swatch.blue { background: #bfdbfe; }

.clear-btn {
    width: 100%;
    padding: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: transparent;
    color: var(--text-muted);
    border-radius: 6px;
    cursor: pointer;
    font-size: 11px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    transition: all 0.15s;
}

.clear-btn:hover {
    background: #dc2626;
    border-color: #dc2626;
    color: white;
}

/* ===== Main Content ===== */
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.4);
    z-index: 90;
    display: none;
}

.overlay.active {
    display: block;
}

.main-content {
    flex: 1;
    overflow-y: auto;
    height: 100vh;
    background: var(--bg-primary);
}

.content-wrapper {
    max-width: 850px;
    margin: 0 auto;
    padding: 32px 40px;
}

.document-section {
    display: none;
}

.document-section.active {
    display: block;
}

.document-header {
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 3px solid var(--accent);
}

.document-header h1 {
    font-family: "Times New Roman", Georgia, serif;
    font-size: 22pt;
    font-weight: bold;
    color: var(--text-primary);
    margin-bottom: 12px;
    line-height: 1.3;
}

.doc-meta {
    display: flex;
    gap: 12px;
    align-items: center;
}

.category-badge {
    display: inline-block;
    padding: 4px 14px;
    background: var(--accent);
    color: white;
    border-radius: 16px;
    font-size: 11px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 500;
}

.btn-download {
    padding: 6px 14px;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 12px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    transition: all 0.15s;
}

.btn-download:hover {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
}

/* ===== Document Content ===== */
.document-content {
    font-family: "Times New Roman", Georgia, serif;
    font-size: 12pt;
    line-height: 1.7;
    color: var(--text-primary);
    text-align: justify;
}

.document-content p {
    margin-bottom: 14px;
    text-align: justify;
}

.document-content .doc-title {
    font-size: 20pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 8px;
    color: var(--text-primary);
}

.document-content .doc-subtitle {
    text-align: center;
    margin-bottom: 24px;
    color: var(--text-secondary);
}

.document-content h2,
.document-content .doc-h2,
.document-content .section-header {
    font-family: "Times New Roman", Georgia, serif;
    font-size: 16pt;
    font-weight: bold;
    color: var(--text-primary);
    margin: 28px 0 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--accent);
    text-align: left;
}

.document-content h3,
.document-content .doc-h3,
.document-content .article-header {
    font-family: "Times New Roman", Georgia, serif;
    font-size: 13pt;
    font-weight: bold;
    color: var(--text-primary);
    margin: 20px 0 12px;
    text-align: left;
}

.document-content .article-header {
    padding: 10px 14px;
    background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
    border-left: 4px solid var(--accent);
    border-radius: 0 8px 8px 0;
}

.document-content .article-header .article-num {
    color: var(--accent);
    font-weight: bold;
}

.document-content .article-header .article-title {
    color: var(--text-secondary);
    font-weight: normal;
    font-style: italic;
}

.document-content .doc-article {
    font-size: 12pt;
    font-weight: bold;
    margin: 20px 0 10px;
    text-align: left;
}

.document-content .article-num {
    color: var(--accent);
    font-weight: bold;
}

.document-content .article-title {
    font-style: italic;
    color: var(--text-secondary);
}

.para-block {
    position: relative;
    padding-left: 45px;
    margin-bottom: 16px;
}

.para-num {
    position: absolute;
    left: 0;
    top: 0;
    font-family: "Times New Roman", Georgia, serif;
    font-size: 12pt;
    font-weight: bold;
    color: var(--accent);
    width: 40px;
    text-align: right;
}

.para-block p {
    margin-bottom: 0;
}

.sub-para {
    padding-left: 30px;
    margin: 10px 0;
    position: relative;
}

.sub-num {
    position: absolute;
    left: 0;
    font-weight: bold;
    color: var(--text-secondary);
}

.sub-para p {
    margin-bottom: 0;
}

.doc-list {
    margin: 12px 0 16px 30px;
    list-style-type: disc;
}

.doc-list li {
    margin-bottom: 6px;
    text-align: justify;
}

.index-entry {
    padding: 6px 0;
    border-bottom: 1px dotted var(--border);
    font-size: 11pt;
}

.notice {
    padding: 20px;
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    text-align: center;
}

/* ===== Annotations ===== */
.highlight-yellow { background: var(--highlight-yellow); }
.highlight-green { background: var(--highlight-green); }
.highlight-pink { background: var(--highlight-pink); }
.highlight-blue { background: var(--highlight-blue); }

.underline-yellow { text-decoration: underline; text-decoration-color: #eab308; text-underline-offset: 3px; text-decoration-thickness: 2px; }
.underline-green { text-decoration: underline; text-decoration-color: #22c55e; text-underline-offset: 3px; text-decoration-thickness: 2px; }
.underline-pink { text-decoration: underline; text-decoration-color: #ec4899; text-underline-offset: 3px; text-decoration-thickness: 2px; }
.underline-blue { text-decoration: underline; text-decoration-color: #3b82f6; text-underline-offset: 3px; text-decoration-thickness: 2px; }

/* ===== Timeline Panel ===== */
.timeline-panel {
    width: 300px;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border);
    height: 100vh;
    display: flex;
    flex-direction: column;
    position: fixed;
    right: 0;
    top: 0;
    z-index: 100;
    transform: translateX(100%);
    transition: transform 0.25s ease;
    box-shadow: -4px 0 20px rgba(0,0,0,0.1);
}

.timeline-panel.open {
    transform: translateX(0);
}

.panel-header {
    padding: 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.panel-header h3 {
    font-size: 14px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 600;
}

.close-panel {
    width: 28px;
    height: 28px;
    border: none;
    background: transparent;
    font-size: 20px;
    cursor: pointer;
    border-radius: 6px;
    color: var(--text-secondary);
}

.close-panel:hover {
    background: var(--bg-primary);
}

.timeline-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.timeline-item {
    position: relative;
    padding-left: 20px;
    padding-bottom: 16px;
    border-left: 2px solid var(--border);
    margin-left: 8px;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 2px;
    width: 10px;
    height: 10px;
    background: var(--accent);
    border-radius: 50%;
    border: 2px solid var(--bg-secondary);
}

.timeline-date {
    font-weight: 600;
    font-size: 12px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--accent);
    cursor: pointer;
}

.timeline-date:hover {
    text-decoration: underline;
}

.timeline-summary {
    font-size: 11px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--text-secondary);
    margin-top: 4px;
    line-height: 1.4;
}

/* ===== FAB ===== */
.fab {
    position: fixed;
    right: 20px;
    bottom: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--accent);
    color: white;
    border: none;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    z-index: 50;
    transition: transform 0.2s, box-shadow 0.2s;
}

.fab:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* ===== Print ===== */
@media print {
    .sidebar, .timeline-panel, .fab, .sidebar-toggle, .overlay { display: none !important; }
    .main-content { width: 100%; }
    .content-wrapper { max-width: 100%; padding: 0; }
    .document-content { font-size: 12pt; }
}
'''


def generate_js(search_index):
    """Generate JavaScript with full-text search"""
    search_index_json = json.dumps(search_index, ensure_ascii=False)
    
    return f'''// ===== Search Index =====
const searchIndex = {search_index_json};

// ===== App State =====
let currentDoc = 'case_study';
let currentTool = 'pointer';
let currentColor = 'yellow';

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {{
    initNavigation();
    initAnnotations();
    initKeyboardShortcuts();
    initTimeline();
    restoreSidebarState();
}});

// ===== Full-Text Search =====
function handleSearch(query) {{
    const resultsContainer = document.getElementById('search-results');
    
    if (!query || query.length < 2) {{
        resultsContainer.classList.remove('active');
        resultsContainer.innerHTML = '';
        return;
    }}
    
    const results = searchDocuments(query);
    
    if (results.length === 0) {{
        resultsContainer.innerHTML = '<div class="search-result-item"><em>No results found</em></div>';
        resultsContainer.classList.add('active');
        return;
    }}
    
    resultsContainer.innerHTML = results.map(result => `
        <div class="search-result-item" data-doc-id="${{result.docId}}" data-query="${{escapeHtml(query)}}" onclick="handleResultClick(this)">
            <div class="doc-title">${{result.title}}</div>
            <div class="match-text">${{result.snippet}}</div>
        </div>
    `).join('');
    resultsContainer.classList.add('active');
}}

function handleResultClick(element) {{
    const docId = element.dataset.docId;
    const query = element.dataset.query;
    goToSearchResult(docId, query);
}}

function searchDocuments(query) {{
    const results = [];
    const queryLower = query.toLowerCase();
    
    for (const doc of searchIndex) {{
        const content = doc.content.toLowerCase();
        const idx = content.indexOf(queryLower);
        
        if (idx !== -1) {{
            // Extract snippet
            const start = Math.max(0, idx - 50);
            const end = Math.min(content.length, idx + query.length + 100);
            let snippet = doc.content.substring(start, end);
            
            // Highlight match
            const matchStart = snippet.toLowerCase().indexOf(queryLower);
            if (matchStart !== -1) {{
                snippet = snippet.substring(0, matchStart) + 
                         '<mark>' + snippet.substring(matchStart, matchStart + query.length) + '</mark>' +
                         snippet.substring(matchStart + query.length);
            }}
            
            if (start > 0) snippet = '...' + snippet;
            if (end < content.length) snippet = snippet + '...';
            
            results.push({{
                docId: doc.id,
                title: doc.title,
                snippet: snippet
            }});
        }}
    }}
    
    return results.slice(0, 10);
}}

function goToSearchResult(docId, query) {{
    showDocument(docId);
    document.getElementById('search-results').classList.remove('active');
    document.getElementById('search-input').value = '';
    
    // Highlight search terms in document
    setTimeout(() => {{
        highlightSearchTerms(query);
    }}, 50);
}}

function highlightSearchTerms(query) {{
    const content = document.querySelector('#doc-' + currentDoc + ' .document-content');
    if (!content || !query) return;
    
    // Remove existing highlights
    content.querySelectorAll('.search-highlight').forEach(mark => {{
        const parent = mark.parentNode;
        while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
        parent.removeChild(mark);
        parent.normalize();
    }});

    if (!query.trim()) return;

    const escapedQuery = query.replace(/[.*+?^${{}}()|[\]\\\\]/g, '\\\\$&');
    const regex = new RegExp(escapedQuery, 'gi');

    const treeWalker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT, {{
        acceptNode: function(node) {{
            if (node.parentElement.tagName === 'SCRIPT' || 
                node.parentElement.tagName === 'STYLE' || 
                node.parentElement.classList.contains('search-highlight')) {{
                return NodeFilter.FILTER_REJECT;
            }}
            return NodeFilter.FILTER_ACCEPT;
        }}
    }});

    const nodeList = [];
    while(treeWalker.nextNode()) nodeList.push(treeWalker.currentNode);

    let firstMatch = null;

    nodeList.forEach(node => {{
        const text = node.textContent;
        if (!regex.test(text)) return;
        
        regex.lastIndex = 0;
        
        const fragment = document.createDocumentFragment();
        let lastIndex = 0;
        let match;
        let found = false;
        
        while ((match = regex.exec(text)) !== null) {{
            found = true;
            fragment.appendChild(document.createTextNode(text.substring(lastIndex, match.index)));
            
            const mark = document.createElement('mark');
            mark.className = 'search-highlight';
            mark.textContent = match[0];
            fragment.appendChild(mark);
            
            if (!firstMatch) firstMatch = mark;
            
            lastIndex = regex.lastIndex;
        }}
        
        if (found) {{
            fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
            node.parentNode.replaceChild(fragment, node);
        }}
    }});

    if (firstMatch) {{
        firstMatch.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}
}}

function escapeHtml(text) {{
    return text.replace(/[&<>"']/g, m => ({{
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }}[m]));
}}

// ===== Keyboard Shortcuts =====
function initKeyboardShortcuts() {{
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') {{
            closeTimeline();
            document.getElementById('search-results').classList.remove('active');
        }}
        if ((e.ctrlKey || e.metaKey) && e.key === 'z') {{
            e.preventDefault();
            undoAnnotation();
        }}
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {{
            e.preventDefault();
            document.getElementById('search-input').focus();
        }}
    }});
}}

// ===== Sidebar =====
function toggleSidebar() {{
    document.body.classList.toggle('sidebar-collapsed');
    localStorage.setItem('sidebarCollapsed', document.body.classList.contains('sidebar-collapsed'));
}}

function restoreSidebarState() {{
    if (localStorage.getItem('sidebarCollapsed') === 'true') {{
        document.body.classList.add('sidebar-collapsed');
    }}
}}

// ===== Navigation =====
function initNavigation() {{
    const firstLink = document.querySelector('.nav-category a');
    if (firstLink) firstLink.classList.add('active');
}}

function showDocument(docId) {{
    document.querySelectorAll('.document-section').forEach(sec => sec.classList.remove('active'));
    
    const section = document.getElementById('doc-' + docId);
    if (section) {{
        section.classList.add('active');
        currentDoc = docId;
        document.querySelector('.main-content').scrollTop = 0;
    }}
    
    document.querySelectorAll('.nav-category a').forEach(link => {{
        link.classList.toggle('active', link.dataset.doc === docId);
    }});
    
    if (docId === 'case_study') initTimeline();
}}

// ===== Tools =====
function setTool(tool) {{
    currentTool = tool;
    document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
    const btn = document.getElementById('tool-' + tool);
    if (btn) btn.classList.add('active');
    
    const content = document.querySelector('.main-content');
    content.style.cursor = tool === 'pointer' ? 'default' : 'text';
}}

function setColor(color) {{
    currentColor = color;
    document.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
    document.querySelector('.swatch.' + color)?.classList.add('active');
}}

// ===== Annotations =====
function initAnnotations() {{
    document.querySelector('.main-content').addEventListener('mouseup', () => {{
        if (currentTool === 'pointer') return;
        
        const selection = window.getSelection();
        if (selection.toString().trim().length > 0) {{
            applyAnnotation(selection);
        }}
    }});
}}

function applyAnnotation(selection) {{
    const range = selection.getRangeAt(0);
    const selectedText = selection.toString();
    
    let node = range.commonAncestorContainer;
    while (node && node.nodeType !== 1) node = node.parentNode;
    if (!node || !node.closest('.document-content')) return;
    
    const span = document.createElement('span');
    const className = currentTool === 'highlight' 
        ? 'highlight-' + currentColor 
        : 'underline-' + currentColor;
    span.className = className;
    span.dataset.annotationId = 'ann-' + Date.now();
    
    try {{
        range.surroundContents(span);
    }} catch (e) {{
        // Handle cross-element selections
        const fragment = range.extractContents();
        span.appendChild(fragment);
        range.insertNode(span);
    }}
    
    saveAnnotation({{
        id: span.dataset.annotationId,
        docId: currentDoc,
        text: selectedText,
        type: currentTool,
        color: currentColor,
        timestamp: Date.now()
    }});
    
    selection.removeAllRanges();
}}

function saveAnnotation(annotation) {{
    const annotations = JSON.parse(localStorage.getItem('bte_annotations') || '[]');
    annotations.push(annotation);
    localStorage.setItem('bte_annotations', JSON.stringify(annotations));
}}

function undoAnnotation() {{
    const annotations = JSON.parse(localStorage.getItem('bte_annotations') || '[]');
    if (!annotations.length) return;
    
    const last = annotations.pop();
    const span = document.querySelector(`[data-annotation-id="${{last.id}}"]`);
    if (span) {{
        const parent = span.parentNode;
        while (span.firstChild) {{
            parent.insertBefore(span.firstChild, span);
        }}
        parent.removeChild(span);
        parent.normalize();
    }}
    localStorage.setItem('bte_annotations', JSON.stringify(annotations));
}}

function clearAnnotations() {{
    if (!confirm('Clear all highlights and underlines?')) return;
    
    document.querySelectorAll('[data-annotation-id]').forEach(el => {{
        const parent = el.parentNode;
        while (el.firstChild) {{
            parent.insertBefore(el.firstChild, el);
        }}
        parent.removeChild(el);
        parent.normalize();
    }});
    localStorage.removeItem('bte_annotations');
}}

// ===== Timeline =====
function initTimeline() {{
    const container = document.getElementById('timeline-content');
    if (!container) return;
    
    const caseStudy = document.querySelector('#doc-case_study .document-content');
    if (!caseStudy) return;
    
    const text = caseStudy.textContent;
    const datePattern = /(\\d{{1,2}}\\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{{4}})/g;
    
    const dates = [];
    let match;
    while ((match = datePattern.exec(text)) !== null) {{
        const start = Math.max(0, match.index - 30);
        const end = Math.min(text.length, match.index + match[0].length + 80);
        let context = text.substring(start, end).replace(/^[^.]*\\.\\s*/, '').split('.')[0];
        
        if (!dates.some(d => d.date === match[1])) {{
            dates.push({{
                date: match[1],
                context: context.trim().substring(0, 60) + '...'
            }});
        }}
    }}
    
    dates.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    container.innerHTML = dates.slice(0, 25).map(item => `
        <div class="timeline-item">
            <div class="timeline-date">${{item.date}}</div>
            <div class="timeline-summary">${{item.context}}</div>
        </div>
    `).join('');
}}

function toggleTimeline() {{
    const panel = document.getElementById('timeline-panel');
    const overlay = document.getElementById('overlay');
    panel.classList.toggle('open');
    overlay.classList.toggle('active', panel.classList.contains('open'));
}}

function closeTimeline() {{
    document.getElementById('timeline-panel').classList.remove('open');
    document.getElementById('overlay').classList.remove('active');
}}

function closeAllPanels() {{
    closeTimeline();
}}

// ===== Download =====
function downloadPDF(filename) {{
    if (filename) window.open('../' + filename, '_blank');
}}
'''


if __name__ == "__main__":
    build_site()
