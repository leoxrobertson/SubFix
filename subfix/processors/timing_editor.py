import re
from datetime import datetime, timedelta

def process_subtitles(input_file, output_file, 
                      min_duration, max_duration, 
                      min_gap, chars_per_sec, 
                      chars_per_line, max_lines):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    subtitle_blocks = re.split(r'\n\s*\n', content.strip())
    processed_blocks = []
    
    for i, block in enumerate(subtitle_blocks):
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 2:
            continue
            
        sub_num = lines[0]
        timecode_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
        if not timecode_match:
            continue
            
        start_time_str, end_time_str = timecode_match.groups()
        start_time = datetime.strptime(start_time_str, '%H:%M:%S,%f')
        end_time = datetime.strptime(end_time_str, '%H:%M:%S,%f')
        text = '\n'.join(lines[2:])
        processed_text = process_text_content(text, chars_per_line, max_lines)
        
        duration = (end_time - start_time).total_seconds()
        char_per_sec = len(processed_text.replace('\n', '')) / max(duration, 0.001)
        required_duration = max(min_duration, len(processed_text.replace('\n', '')) / chars_per_sec)
        
        if duration < required_duration:
            new_end_time = start_time + timedelta(seconds=required_duration)
            end_time = new_end_time
        
        processed_blocks.append({
            'num': sub_num,
            'start': start_time,
            'end': end_time,
            'text': processed_text
        })
    
    for i in range(len(processed_blocks) - 1):
        current = processed_blocks[i]
        next_block = processed_blocks[i + 1]
        min_gap_td = timedelta(seconds=min_gap)
        required_end = next_block['start'] - min_gap_td
        
        if current['end'] > required_end:
            current['end'] = required_end
            duration = (current['end'] - current['start']).total_seconds()
            if duration < min_duration:
                needed_end = current['start'] + timedelta(seconds=min_duration)
                if needed_end > next_block['start']:
                    time_diff = needed_end - next_block['start']
                    for j in range(i + 1, len(processed_blocks)):
                        processed_blocks[j]['start'] += time_diff
                        processed_blocks[j]['end'] += time_diff
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for block in processed_blocks:
            start_str = block['start'].strftime('%H:%M:%S,%f')[:-3]
            end_str = block['end'].strftime('%H:%M:%S,%f')[:-3]
            f.write(f"{block['num']}\n{start_str} --> {end_str}\n{block['text']}\n\n")

def adjust_timings(input_path, output_path, 
                  min_duration=0.6, max_duration=8.0, 
                  min_gap=0.066, chars_per_sec=25,
                  chars_per_line=43, max_lines=2):
    """Adjust subtitle timings based on specified parameters."""
    process_subtitles(
        input_file=input_path,
        output_file=output_path,
        min_duration=min_duration,
        max_duration=max_duration,
        min_gap=min_gap,
        chars_per_sec=chars_per_sec,
        chars_per_line=chars_per_line,
        max_lines=max_lines
    )

def process_text_content(text, chars_per_line, max_lines):
    """Process text to fit chars_per_line and max_lines, with punctuation breaks."""
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        if len(line) <= chars_per_line:
            processed_lines.append(line)
        else:
            # Try splitting at punctuation first
            split_line = split_at_punctuation(line, chars_per_line)
            if split_line:
                processed_lines.extend(split_line)
            else:
                # Fallback to word-based splitting
                words = line.split()
                line1, line2 = [], []
                current_line, current_len = line1, 0
                
                for word in words:
                    if current_len + len(word) + len(current_line) > chars_per_line and current_line is line1:
                        current_line, current_len = line2, 0
                    current_line.append(word)
                    current_len += len(word)
                
                line1_str = ' '.join(line1)
                line2_str = ' '.join(line2) if line2 else ''
                if line2_str:
                    processed_lines.append(line1_str)
                    processed_lines.append(line2_str)
                else:
                    processed_lines.append(line1_str)
    
    if len(processed_lines) > max_lines:
        processed_lines = [processed_lines[0], ' '.join(processed_lines[1:])]
        if len(processed_lines[1]) > chars_per_line:
            processed_lines[1] = processed_lines[1][:chars_per_line - 3] + "..."
    
    return '\n'.join(processed_lines)

def split_at_punctuation(line, chars_per_line):
    """Split a line at the last punctuation mark before chars_per_line."""
    if len(line) <= chars_per_line:
        return [line]
    
    # Prefer splitting at these punctuation marks
    punctuation_marks = [',', '.', '-', ';', '!', '?', '…']
    split_pos = -1
    
    for mark in punctuation_marks:
        # Find the last occurrence of punctuation before chars_per_line
        pos = line.rfind(mark, 0, chars_per_line)
        if pos > split_pos:
            split_pos = pos
    
    if split_pos != -1:
        # Split at punctuation + space if possible
        part1 = line[:split_pos + 1].strip()
        part2 = line[split_pos + 1:].strip()
        return [part1, part2] if part2 else [part1]
    
    return None

if __name__ == "__main__":
    input_file = "input.srt"
    output_file = "output.srt"
    adjust_timings(input_file, output_file)
    print(f"Processed subtitles saved to {output_file}")


