from spellchecker import SpellChecker
import re
from pathlib import Path

def spellcheck_srt(input_file, output_file):
    spell = SpellChecker()
    
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    content = input_path.read_text(encoding='utf-8')
    
    # Split into subtitle blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    processed_blocks = []
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.split('\n')
        if len(lines) < 3:  # Skip malformed blocks
            processed_blocks.append(block)
            continue
        
        # Process text lines (lines[2] and beyond)
        text_lines = lines[2:]
        corrected_lines = []
        
        for line in text_lines:
            words = re.findall(r'\b\w+\b', line)  # Extract words
            misspelled = spell.unknown(words)  # Get all misspelled words at once
            for word in misspelled:
                correction = spell.correction(word)
                if correction:
                    line = line.replace(word, correction, 1)  # Replace first occurrence
            corrected_lines.append(line)
        
        # Rebuild block
        processed_block = '\n'.join([lines[0], lines[1]] + corrected_lines)
        processed_blocks.append(processed_block)
    
    # Write corrected subtitles
    output_path.write_text('\n\n'.join(processed_blocks), encoding='utf-8')

if __name__ == "__main__":
    spellcheck_srt("input.srt", "spellchecked.srt")
    print("Spell-checked subtitles saved to spellchecked.srt")


