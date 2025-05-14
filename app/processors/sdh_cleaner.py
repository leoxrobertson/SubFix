import re

def remove_hi_tags(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove common HI tags (case-insensitive)
    cleaned_content = re.sub(
        r'\[(music|applause|laughter|sighs?|coughs?|noise|speaker|door|phone|ringing)\]',
        '', 
        content, 
        flags=re.IGNORECASE
    )
    
    # Remove empty subtitle blocks (optional)
    cleaned_content = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n\s*\n', '', cleaned_content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

if __name__ == "__main__":
    remove_hi_tags("input.srt", "cleaned.srt")
    print("Hearing-impaired tags removed. Saved to cleaned.srt")

