import fitz
import re

def format_1932_award():
    input_pdf = "MCC-Award-1932.12.03.pdf"
    output_txt = "mcc_award_1932_text.txt"
    
    doc = fitz.open(input_pdf)
    
    content_blocks = []
    
    # Header for the final file
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
        "DECISION OF THE UMPIRE\n",
        "December 3, 1932\n",
        "\n",
        "***\n",
        "\n"
    ]
    
    stop_processing = False
    
    for page in doc:
        if stop_processing: break
        
        blocks = page.get_text("blocks")
        # blocks structure: (x0, y0, x1, y1, "text", block_no, block_type)
        
        for b in blocks:
            text = b[4]
            clean_text = text.strip()
            
            if not clean_text:
                continue
                
            y0 = b[1]
            
            # Stop condition
            if "KATHARINE M. DRIER" in clean_text:
                stop_processing = True
                break

            # Heuristic filters for headers/running text
            if "REPORTS OF INTERNATIONAL" in clean_text: continue
            if "ARBITRAL AWARDS" in clean_text: continue
            if "RECUEIL DES SENTENCES" in clean_text: continue
            
            # Running headers often look like "104 UNITED STATES/GERMANY" or "DECISIONS 105"
            # We filter if it looks like a running header
            if "UNITED STATES" in clean_text and "GERMANY" in clean_text: continue
            if "UNITED STATES" in clean_text and "GERM ANY" in clean_text: continue
            if "DECISIONS" in clean_text and len(clean_text) < 40: continue
            if clean_text.isdigit(): continue
            
            # Specific garbage from PDF metadata/watermarks
            if "NATIONS UNIES" in clean_text: continue
            if "Copyright (c)" in clean_text: continue
            if "Volume" in clean_text and len(clean_text) < 20: continue
            if "VIII pp." in clean_text: continue

            # OCR Fixes/Cleanups
            para = text.replace("\n", " ").strip()
            para = para.replace("Honoiable", "Honorable")
            para = para.replace("Blark Tom", "Black Tom")
            
            # Fix hyphenation (e.g. "re- hear") -> "rehear"
            para = re.sub(r'(\w)-\s+(\w)', r'\1\2', para)
            
            content_blocks.append(para)

    # Post-process content blocks
    
    # Locate the start of relevant content.
    # We look for "Certificate of Disagreement" or preamble.
    start_index = 0
    for i, block in enumerate(content_blocks):
        if "Certificate of Disagreement" in block and "National Commissioners" in block:
            start_index = i
            break
            
    if start_index > 0:
        content_blocks = content_blocks[start_index:]
        
    # Merge blocks that are likely split paragraphs
    merged_paras = []
    headers = ["Kingsland", "Black Tom"]
    
    if content_blocks:
        current_para = content_blocks[0]
        
        for next_block in content_blocks[1:]:
            strip_current = current_para.strip()
            if not strip_current:
                current_para = next_block
                continue
            
            # Check if current is a header (explicit list)
            if strip_current in headers:
                merged_paras.append(current_para)
                current_para = next_block
                continue

            # Heuristic for merging:
            ends_incomplete = strip_current[-1] not in ['.', '!', '?', ':', '"', "”", ')']
            starts_lowercase = next_block.strip() and next_block.strip()[0].islower()
            
            if ends_incomplete or starts_lowercase:
                current_para += " " + next_block
            else:
                merged_paras.append(current_para)
                current_para = next_block
        
        merged_paras.append(current_para)

    # Append to final text using numbered paragraphs
    para_count = 1
    for block in merged_paras:
        clean_block = block.strip()
        if not clean_block: continue
        
        if clean_block in headers:
            final_text.append(f"{clean_block}\n\n")
        else:
            final_text.append(f"[{para_count}] {clean_block}\n\n")
            para_count += 1

    with open(output_txt, "w", encoding="utf-8") as f:
        f.writelines(final_text)
        
    print(f"Formatted text saved to {output_txt}")

if __name__ == "__main__":
    format_1932_award()
