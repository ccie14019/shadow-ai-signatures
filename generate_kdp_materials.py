#!/usr/bin/env python3
"""
Generate KDP materials:
- Book cover prompt
- KDP information including description (3000 chars max)
"""

def generate_book_cover_prompt():
    """Generate a prompt for book cover design"""
    prompt = """Design a professional book cover for "Shadow AI Detection: Network Fingerprinting with JA4 for Enterprise Security Teams" by David Cooper, CCIE #14019.

STYLE & MOOD:
- Professional, technical, cybersecurity-focused
- Dark, modern aesthetic with subtle tech elements
- Conveys enterprise security and network engineering expertise
- Serious, authoritative tone suitable for IT professionals

COLOR SCHEME:
- Primary: Deep navy blue (#0A1929) or charcoal gray (#1A1A1A)
- Accent: Electric blue (#0066FF) or cybersecurity green (#00FF88)
- Text: White or light gray for contrast
- Optional: Subtle network diagram patterns or circuit board textures in background

COMPOSITION:
- 6x9 inch format (KDP trim size)
- Title: "Shadow AI Detection" (large, bold, prominent)
- Subtitle: "Network Fingerprinting with JA4 for Enterprise Security Teams" (smaller, readable)
- Author: "David Cooper, CCIE #14019" (bottom third, professional)
- Visual elements: Abstract network connections, data streams, or fingerprint patterns
- No cliché padlocks or shields - focus on network/technical imagery

TEXT HIERARCHY:
1. Main title: Large, bold, sans-serif (like Montserrat or Roboto)
2. Subtitle: Medium, readable, can be serif (like Garamond)
3. Author: Smaller, professional, serif font

VISUAL ELEMENTS (subtle, not overwhelming):
- Network node connections in background
- Data flow lines or streams
- Fingerprint/identification patterns
- Binary code or hex patterns (very subtle)
- TLS/encryption visual metaphors

TECHNICAL REQUIREMENTS:
- 6x9 inches (KDP standard)
- 300 DPI minimum
- CMYK color mode for print
- Bleed area: 0.125 inches on all sides
- Safe text area: Keep text 0.25 inches from edges

AVOID:
- Stock photos of people
- Generic cybersecurity clichés
- Overly complex designs
- Low contrast text
- Copyrighted imagery

The cover should appeal to:
- Network engineers
- Security architects
- CISOs and security managers
- IT professionals dealing with Shadow IT/AI issues"""
    
    return prompt

def generate_kdp_information():
    """Generate complete KDP information"""
    
    description = """Shadow AI—unauthorized artificial intelligence tools installed by employees—represents one of the most critical and invisible security threats facing enterprises today. IBM's 2025 research reveals that Shadow AI incidents account for 20% of all data breaches, with 86% of enterprises completely blind to their AI data flows. Traditional security tools fail because the traffic is encrypted, runs locally, and appears identical to normal HTTPS connections.

This comprehensive guide, written by CCIE #14019 David Cooper with 25 years of network security experience, provides the first practical solution: network-layer fingerprinting using JA4 signatures. Unlike policy frameworks or awareness training, this book delivers working code, real signatures, and battle-tested deployment strategies that security teams can implement this quarter.

WHAT YOU'LL LEARN:

• Why Your Security Stack is Blind: Understand why DLP, endpoint detection, SIEM, and cloud monitoring fail to detect Shadow AI. Learn the technical limitations that make AI agents invisible to traditional tools.

• JA4 Fingerprinting Fundamentals: Master the TLS Client Hello analysis technique that identifies applications before encryption begins. Every AI framework—LangChain, AutoGPT, Ollama, and 30+ others—has a unique, unforgeable signature.

• Complete Signature Database: Access tested JA4 signatures for major AI frameworks including OpenAI, Anthropic, LangChain, AutoGPT, CrewAI, Ollama, and more. Each signature comes from actual packet captures, not theoretical analysis.

• Production Deployment Guides: Step-by-step instructions for implementing JA4 detection on Zeek, Suricata, and eBPF platforms. Deploy working detection in under 8 hours with provided scripts and configurations.

• Integration Patterns: Learn how to integrate JA4 detection into existing SIEM platforms, security orchestration tools, and incident response workflows. Includes Splunk, ELK, QRadar, and custom integration examples.

• Compliance Mapping: Understand how Shadow AI detection maps to GDPR, HIPAA, PCI DSS, and other regulatory frameworks. Includes audit-ready documentation templates.

• Incident Response Playbooks: Detailed procedures for investigating Shadow AI detections, including data exposure assessment, user communication templates, and remediation strategies.

• Real-World Case Studies: Analyze actual Shadow AI incidents including the $670,000 AutoGPT breach, healthcare HIPAA violations, and financial services data exposure scenarios.

WHAT MAKES THIS DIFFERENT:

This isn't a vendor whitepaper or academic research. Every technique has been tested in lab environments. Every script has been debugged. Every playbook has been refined through tabletop exercises. The signature database comes from actual packet captures of real AI frameworks running in production-like conditions.

Written by a practitioner for practitioners, this book acknowledges reality: you don't have unlimited budget, unlimited time, or unlimited staff. You need solutions that work with your existing infrastructure, integrate with your current tools, and can be deployed this quarter.

WHO THIS BOOK IS FOR:

• Security Architects designing comprehensive detection solutions
• Network Engineers implementing network-layer monitoring
• SOC Managers building detection and response capabilities
• CISOs needing to address Shadow AI before the next audit
• Compliance Officers mapping technical controls to regulatory requirements

REQUIREMENTS:

• Working knowledge of network protocols (TCP/IP, TLS)
• Experience with packet capture and analysis
• Familiarity with at least one SIEM platform
• Access to network infrastructure for sensor deployment

You don't need to be a developer, though basic scripting knowledge helps. You don't need to understand AI/ML internals—we're fingerprinting the network behavior, not the algorithms.

ABOUT THE AUTHOR:

David Cooper holds CCIE #14019, earned in 2004, representing 25 years of hands-on experience in cybersecurity and network engineering. As founder of CyberShield Austin, a security consultancy serving enterprise clients, David has spent the past decade analyzing the intersection of network security, blockchain infrastructure, and emerging AI threats. His career spans Air Force service, Fortune 500 network architecture, and independent security research.

David has published over 20 technical guides on Kindle covering topics from blockchain node security to distributed cloud architecture. His TokenAudit YouTube channel featured 102 detailed analyses of cryptocurrency projects, applying network engineering principles to decentralized systems.

This unique background—combining deep networking expertise with security analysis and emerging technology assessment—positions him to address the Shadow AI detection challenge from both theoretical and practical perspectives.

KEY FEATURES:

✓ Working Python scripts for JA4 extraction and analysis
✓ Complete Zeek configuration files ready for deployment
✓ Suricata rules for JA4-based detection
✓ eBPF implementation examples
✓ Signature database in CSV format for easy import
✓ SIEM integration templates (Splunk, ELK, QRadar)
✓ Incident response playbooks and templates
✓ Compliance mapping documentation
✓ Lab environment setup guide
✓ Troubleshooting and optimization guides

Stop being blind to Shadow AI. Deploy network-layer detection that works on encrypted traffic, requires no endpoint agents, and scales to enterprise networks. This book provides everything you need to detect unauthorized AI agents before your next audit—or your next breach."""
    
    # Ensure description is under 3000 characters
    if len(description) > 3000:
        description = description[:2997] + "..."
    
    kdp_info = {
        "title": "Shadow AI Detection: Network Fingerprinting with JA4 for Enterprise Security Teams",
        "subtitle": "A CCIE's Guide to Identifying Unauthorized AI Agents Using TLS Client Signatures",
        "author": "David Cooper",
        "author_bio": "David Cooper holds CCIE #14019, earned in 2004, representing 25 years of hands-on experience in cybersecurity and network engineering. As founder of CyberShield Austin, a security consultancy serving enterprise clients, David has spent the past decade analyzing the intersection of network security, blockchain infrastructure, and emerging AI threats.",
        "description": description,
        "description_length": len(description),
        "keywords": [
            "Shadow AI",
            "Network Security",
            "JA4 Fingerprinting",
            "TLS Analysis",
            "Enterprise Security",
            "Cybersecurity",
            "Network Engineering",
            "AI Detection",
            "Encrypted Traffic Analysis",
            "Security Operations",
            "SIEM Integration",
            "Incident Response",
            "Compliance",
            "HIPAA",
            "GDPR",
            "PCI DSS"
        ],
        "categories": [
            "Computers / Security / General",
            "Computers / Networking / Network Protocols",
            "Computers / Security / Cryptography",
            "Business & Economics / Information Management"
        ],
        "bisac_codes": [
            "COM043000",  # Computers / Security / General
            "COM043020",  # Computers / Security / Cryptography
            "COM043040",  # Computers / Security / Network Security
            "COM043060"   # Computers / Security / Viruses & Malware
        ],
        "language": "English",
        "publication_date": "2025",
        "trim_size": "6 x 9 inches",
        "page_count": "Approximately 400-500 pages (to be confirmed after conversion)",
        "paperback_price_suggestions": {
            "US": "$29.99 - $34.99",
            "UK": "£24.99 - £29.99",
            "EU": "€27.99 - €32.99"
        },
        "ebook_price_suggestions": {
            "US": "$9.99 - $14.99",
            "UK": "£7.99 - £12.99",
            "EU": "€8.99 - €13.99"
        },
        "age_range": "Adult",
        "rights_territory": "Worldwide",
        "isbn_notes": "KDP will assign ISBN automatically, or you can provide your own"
    }
    
    return kdp_info

def save_kdp_materials():
    """Save all KDP materials to files"""
    cover_prompt = generate_book_cover_prompt()
    kdp_info = generate_kdp_information()
    
    # Save cover prompt
    with open('Book/kdp_book_cover_prompt.txt', 'w', encoding='utf-8') as f:
        f.write(cover_prompt)
    
    # Save KDP information
    with open('Book/kdp_information.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("KDP PUBLICATION INFORMATION\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"TITLE: {kdp_info['title']}\n")
        f.write(f"SUBTITLE: {kdp_info['subtitle']}\n")
        f.write(f"AUTHOR: {kdp_info['author']}\n\n")
        
        f.write("AUTHOR BIO:\n")
        f.write(f"{kdp_info['author_bio']}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("BOOK DESCRIPTION\n")
        f.write(f"(Length: {kdp_info['description_length']} characters)\n")
        f.write("=" * 80 + "\n\n")
        f.write(kdp_info['description'])
        f.write("\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("KEYWORDS\n")
        f.write("=" * 80 + "\n")
        for keyword in kdp_info['keywords']:
            f.write(f"- {keyword}\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("CATEGORIES\n")
        f.write("=" * 80 + "\n")
        for category in kdp_info['categories']:
            f.write(f"- {category}\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("BISAC CODES\n")
        f.write("=" * 80 + "\n")
        for code in kdp_info['bisac_codes']:
            f.write(f"- {code}\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("PUBLICATION DETAILS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Language: {kdp_info['language']}\n")
        f.write(f"Publication Date: {kdp_info['publication_date']}\n")
        f.write(f"Trim Size: {kdp_info['trim_size']}\n")
        f.write(f"Page Count: {kdp_info['page_count']}\n")
        f.write(f"Age Range: {kdp_info['age_range']}\n")
        f.write(f"Rights Territory: {kdp_info['rights_territory']}\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("PRICING SUGGESTIONS\n")
        f.write("=" * 80 + "\n")
        f.write("PAPERBACK:\n")
        for region, price in kdp_info['paperback_price_suggestions'].items():
            f.write(f"  {region}: {price}\n")
        f.write("\nEBOOK:\n")
        for region, price in kdp_info['ebook_price_suggestions'].items():
            f.write(f"  {region}: {price}\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("ISBN NOTES\n")
        f.write("=" * 80 + "\n")
        f.write(f"{kdp_info['isbn_notes']}\n")
    
    print("KDP materials generated successfully!")
    print(f"  - Cover prompt: Book/kdp_book_cover_prompt.txt")
    print(f"  - KDP information: Book/kdp_information.txt")
    print(f"  - Description length: {kdp_info['description_length']} characters")

if __name__ == '__main__':
    save_kdp_materials()

