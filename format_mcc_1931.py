import fitz

def format_1931_decision():
    # Manual text reconstruction based on user's specific request for exactly 10 paragraphs
    # and specific content starts.
    
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
        "DECISION ON PETITIONS FOR REHEARING\n",
        "March 30, 1931\n",
        "\n",
        "***\n",
        "\n"
    ]
    
    # We will grab the text content but force the specific paragraph breaks user requested.
    # Text source:
    doc = fitz.open("MCC-Decision-1931.03.30.pdf")
    full_text = " ".join([page.get_text() for page in doc])
    
    # Clean up newlines and junk
    full_text = full_text.replace("\n", " ")
    full_text = " ".join(full_text.split()) # Normalize spaces
    
    # The starting phrases provided by user:
    starts = [
        "Petitions for a rehearing have been filed",
        "The briefs previously filed in behalf",
        "The terms of the Treaty of Berlin determine",
        "We think it futile to criticize",
        "This question is raised by the American", # Wait, user said "fifth with this question is raised"
        # Wait, looking at my extraction:
        # "We think it futile... One of his criticisms... This question is raised..." 
        # The user wants "This question..." as a new para.
        "These petitions for rehearing are dismissed", # 6th
        "A new jurisdictional question is raised", # 7th
        "Accordingly, the requests in these petitions", # 8th
        "In these petitions the American Agent states", # Wait, user said "ninth with each of the two governments"
        # Checking user request:
        # "eighth with accoridnly, the requests in these peittions"
        # "ninth with each of the two governments"
        # "10 with done at washington"
        
        # But my extraction shows a paragraph between "Accordingly..." and "Each of..."
        # "In these petitions the American Agent states...". The user might have skipped this or it's part of 8th?
        # User said "ninth with each of two governments". 
        # I will check if "In these petitions..." is in the text.
        # Yes: "In these petitions the American Agent states that he is collecting new evidence..."
        # User didn't mention it. I should probably include it.
        # Maybe user wants it merged into 8th? Or missed it?
        # "do accordingly" with the User's list "10 paras".
        # If I strictly follow 10 paras as described:
        # 1. Petitions...
        # 2. Briefs...
        # 3. Terms...
        # 4. We think...
        # 5. This question...
        # 6. These petitions...
        # 7. A new jurisdictional...
        # 8. Accordingly...
        # 9. Each of the two...
        # 10. Done at...
        
        # What about "In these petitions the American Agent states..."?
        # If I leave it out, text is missing.
        # I will append it to "Accordingly..." paragraph or "Each of..."?
        # Likely it belongs to the previous section (Accordingly).
        
        # Actually, looking at the user's list:
        # "sixth with these petitions for rehearing are dismissed"
        # "seventh with a new jusridictional question"
        # "eighth with accoridnly, the requests in these peittions"
        # "ninth with each of the two governments"
        
        # Where is "In these petitions..."?
        # It comes AFTER "Accordingly...". 
        # If I skip it, I lose text. I will assume it's part of the 8th or 9th?
        # Or maybe the user missed one and I should include it as an 11th specific para or merge.
        # I'll merge it with the 8th because 9th is clearly "Each of the two governments... wind up its labors".
        
    ]
    
    # Let's find indices
    extracted_paras = []
    
    # Manual extraction logic is safer to get clean text
    # I'll copy the text from the previous turn's output to be precise, or search in full_text
    
    # 1. Petitions...
    p1_start = full_text.find("Petitions for a rehearing have been filed")
    p1_end = full_text.find("The briefs previously filed")
    extracted_paras.append(full_text[p1_start:p1_end].strip())
    
    # 2. Briefs...
    p2_start = p1_end
    p2_end = full_text.find("The terms of the Treaty of Berlin")
    extracted_paras.append(full_text[p2_start:p2_end].strip())
    
    # 3. Terms...
    p3_start = p2_end
    p3_end = full_text.find("We think it futile")
    extracted_paras.append(full_text[p3_start:p3_end].strip())
    
    # 4. We think...
    p4_start = p3_end
    p4_end = full_text.find("This question is raised")
    extracted_paras.append(full_text[p4_start:p4_end].strip())
    
    # 5. This question...
    p5_start = p4_end
    p5_end = full_text.find("These petitions for rehearing are dismissed")
    # Wait, my extraction in previous turn: 
    # "The Umpire participated... accepted by all concerned. These petitions..."
    # So "This question..." goes until "These petitions..."
    extracted_paras.append(full_text[p5_start:p5_end].strip())
    
    # 6. These petitions...
    p6_start = p5_end
    p6_end = full_text.find("A new jurisdictional question")
    extracted_paras.append(full_text[p6_start:p6_end].strip())
    
    # 7. A new jurisdictional...
    p7_start = p6_end
    p7_end = full_text.find("Accordingly, the requests")
    extracted_paras.append(full_text[p7_start:p7_end].strip())
    
    # 8. Accordingly... (and the missing paragraph?)
    p8_start = p7_end
    p9_start = full_text.find("Each of the two Governments")
    # Using case insensitive search for "Governments" just in case
    if p9_start == -1:
         p9_start = full_text.find("Each of the two governments")
    
    # Check "In these petitions..."
    missing_start = full_text.find("In these petitions the American Agent states")
    
    # If missing text exists, determine where it goes.
    # Logic: 8th para is "Accordingly... denied."
    # Then "In these petitions... decided."
    # Then 9th para "Each of...".
    # User didn't request "In these petitions" as a start.
    # I will merge it into 8th so it's not lost, or should I drop it? 
    # Better to keep it attached to 8th.
    
    extracted_paras.append(full_text[p8_start:p9_start].strip())
    
    # 9. Each of...
    p9_end = full_text.find("Done at Washington")
    extracted_paras.append(full_text[p9_start:p9_end].strip())
    
    # 10. Done at...
    p10_end = full_text.find("ROLAND W. BOYDEN") # Signature start
    extracted_paras.append(full_text[p9_end:p10_end].strip())
    
    # Signatures
    signatures = [
        "ROLAND W. BOYDEN",
        "Umpire",
        "",
        "Chandler P. ANDERSON",
        "American Commissioner",
        "",
        "W. KIESSELBACH",
        "German Commissioner"
    ]
    
    # Build content
    final_output = list(header)
    for i, para in enumerate(extracted_paras):
        final_output.append(f"[{i+1}] {para}\n\n")
        
    final_output.append("Signatures:\n\n")
    final_output.extend([s + "\n" for s in signatures])
    
    with open('mcc_decision_1931_text.txt', 'w', encoding='utf-8') as f:
        f.writelines(final_output)

    print("Formatted MCC Decision 1931.")

if __name__ == "__main__":
    format_1931_decision()
