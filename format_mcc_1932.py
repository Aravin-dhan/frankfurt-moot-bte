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
    if content_blocks:
        current_para = content_blocks[0]
        
        for next_block in content_blocks[1:]:
            # Heuristic for merging:
            # If current_para ends with a word char, comma, or hyphen (not . ! ? :)
            # OR if next_block starts with lowercase
            # We assume it should be merged.
            
            strip_current = current_para.strip()
            if not strip_current:
                current_para = next_block
                continue
                
            ends_incomplete = strip_current[-1] not in ['.', '!', '?', ':', '"', "”", ')']
            # Special case: "Mr." or "No." ends with dot but is not end of sentence.
            # But usually PDF blocks break at end of page/column which might cut mid-sentence.
            
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
        
        # Don't number the "Signatures" or headers if they look like headers
        # Heuristic: headers usually distinct. But user wants "paragraph numbers".
        # I'll number everything that looks like a paragraph.
        # Maybe skip "Certificate of Disagreement..." title?
        
        # Check if it is a Title (short, all caps or Title Case without period?)
        # But user said "use paragaph numbers". Usually applies to body text.
        # I'll number everything to be safe, or start numbering after the initial header?
        
        final_text.append(f"[{para_count}] {clean_block}\n\n")
        para_count += 1

    with open(output_txt, "w", encoding="utf-8") as f:
        f.writelines(final_text)
        
    print(f"Formatted text saved to {output_txt}")

if __name__ == "__main__":
    format_1932_award()
