import fitz
import re

def format_with_blocks():
    input_pdf = 'MCC-Award-1930.10.16.pdf'
    output_file = 'mcc_award_1930_text.txt'
    
    doc = fitz.open(input_pdf)
    
    # Define the Header
    final_text = [
        "MIXED CLAIMS COMMISSION\n",
        "UNITED STATES AND GERMANY\n",
        "\n",
        "LEHIGH VALLEY RAILROAD COMPANY, AGENCY OF CANADIAN CAR AND FOUNDRY COMPANY, LIMITED, AND VARIOUS UNDERWRITERS\n",
        "(UNITED STATES)\n",
        "v.\n",
        "GERMANY\n",
        "(Sabotage Cases)\n",
        "\n",
        "DECISION\n",
        "October 16, 1930\n",
        "\n",
        "***\n",
        "\n"
    ]
    
    para_count = 1
    
    # Skip first page (Table of contents/cover seems to be page 0 and 1)
    # Based on the screenshot, Page 3 (index 2) is where "Award" starts.
    # Page 0 is title, Page 1 empty? Let's check.
    # Adjusting start page based on content detection.
    
    start_processing = False
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        # blocks structure: (x0, y0, x1, y1, text, block_no, block_type)
        
        # Sort by vertical position (y0), then horizontal (x0)
        blocks.sort(key=lambda b: (b[1], b[0]))
        
        for b in blocks:
            text = b[4].strip()
            
            # Skip empty or tiny blocks
            if not text:
                continue
                
            # Skip artifacts
            if "View the document on jusmundi.com" in text:
                continue
            if re.match(r'^page \d+ \(original document\)$', text):
                continue
            if text.isdigit(): # Page numbers usually
                continue
            # Skip the initial junk headers if we haven't started yet
            if not start_processing:
                if "These two cases involve" in text:
                    start_processing = True
                else:
                    # Check if it's the "Award" title on page 3
                    if text == "Award" and page_num >= 2:
                        continue # Skip the title itself, we have our own
                    if "COMMISSION US-GERMANY" in text:
                        continue # Skip junk header
                    if "SABO" in text and len(text) < 10:
                        continue
                        
            if start_processing:
                # This block is a paragraph
                # Clean up newlines inside the block (unwrap text) but strictly separate blocks
                clean_para = " ".join(text.splitlines())
                
                # Double check specific junk that might be inside blocks?
                # Usually blocks are clean.
                
                final_text.append(f"[{para_count}] {clean_para}\n\n")
                para_count += 1
                
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(final_text)
        
    print(f"Formatted MCC Award with {para_count-1} paragraphs.")

if __name__ == "__main__":
    format_with_blocks()
