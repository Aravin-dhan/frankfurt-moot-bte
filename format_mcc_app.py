import re

def format_mcc_award():
    input_file = 'mcc_award_1930_raw.txt' # Use raw to start fresh or text if raw is gone. Raw should be there.
    # Check if raw exists, if not use text
    import os
    if not os.path.exists(input_file):
        input_file = 'mcc_award_1930_text.txt'

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Define the new Clean Header
    header = [
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

    # Content processing
    # Skip the first ~20 lines of junk (SABO ABOTAGE etc)
    # Finding the start of real text. It starts with "These two cases involve..."
    
    start_index = 0
    for i, line in enumerate(lines):
        if "These two cases involve" in line:
            start_index = i
            break
    
    body_lines = lines[start_index:]
    
    # Process body for paragraphing
    processed_lines = []
    
    # We want to join broken lines but keep paragraph breaks
    # And unwanted lines: "--- Page X ---" (User wants to keep them? User said "number separated paragraphs" and "remove lines". 
    # Usually page markers are good, but if they break paragraphs mid-sentence, we should handle them.
    # User said "see main docs... lmk if you do not have access". 
    # I will keep page markers but ensure they don't look like text.
    
    buffer = ""
    paragraph_count = 1
    
    for line in body_lines:
        sline = line.strip()
        
        # Skip junk
        if "View the document on jusmundi" in sline:
            continue
        if "page" in sline and "(original document)" in sline:
            continue
        if sline.isdigit(): # likely a page number artifact "1", "2"
            continue
        
        # Page markers
        if "--- Page" in sline:
            # If we have a buffer, dump it as a paragraph first
            if buffer:
                processed_lines.append(f"[{paragraph_count}] {buffer}\n\n")
                paragraph_count += 1
                buffer = ""
            processed_lines.append(f"\n{sline}\n\n") # Keep page marker separate
            continue
            
        if not sline:
            # Empty line -> Paragraph break
            if buffer:
                processed_lines.append(f"[{paragraph_count}] {buffer}\n\n")
                paragraph_count += 1
                buffer = ""
            continue
            
        # Text line
        if buffer:
            if buffer.endswith("-"):
                buffer = buffer[:-1] + sline # Hyphenation fix
            else:
                buffer += " " + sline
        else:
            buffer = sline

    if buffer:
        processed_lines.append(f"[{paragraph_count}] {buffer}\n\n")

    # Combine
    final_content = "".join(header + processed_lines)
    
    with open('mcc_award_1930_text.txt', 'w', encoding='utf-8') as f:
        f.write(final_content)

    print("Formatted MCC Award 1930 successfully.")

if __name__ == "__main__":
    format_mcc_award()
