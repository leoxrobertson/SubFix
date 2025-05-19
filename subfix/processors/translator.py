import re
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator, LibreTranslator, MicrosoftTranslator
from langdetect import detect

# ======= CONFIGURATION =======
TARGET_LANG = 'es'  # Example: 'fr', 'de', 'zh'
WORKERS = 3  # Conservative to avoid bans
MAX_CHARS_PER_REQUEST = 4500  # Stay under provider limits
REQUEST_DELAY = 1.0  # Seconds between requests
PROXY_LIST = [  # Rotating proxies (http/s)
    None,  # First try without proxy
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080'
]
BATCH_SAVE_EVERY = 20  # Save progress every N subtitles
# =============================

class SubtitleTranslator:
    def __init__(self):
        self.translated_count = 0
        self.failed_count = 0
        self.current_proxy = None
        self.proxy_rotation_index = 0
        self.provider_order = [
            self._try_google,
            self._try_microsoft,
            self._try_libre
        ]

    def _rotate_proxy(self):
        """Rotate through available proxies"""
        self.proxy_rotation_index = (self.proxy_rotation_index + 1) % len(PROXY_LIST)
        self.current_proxy = PROXY_LIST[self.proxy_rotation_index]
        return self.current_proxy

    def _try_google(self, text, source_lang, target_lang):
        try:
            return GoogleTranslator(
                source=source_lang,
                target=target_lang
            ).translate(text[:MAX_CHARS_PER_REQUEST])
        except Exception as e:
            print(f"Google failed: {str(e)}")
            print(f"   Text: {text[:50]}...")
            print(f"   Target language: {target_lang}, Source language: {source_lang}")
            return None

    def _try_microsoft(self, text, source_lang, target_lang):
        try:
            # Requires API key - set env var MICROSOFT_TRANSLATOR_KEY
            return MicrosoftTranslator(
                source=source_lang,
                target=target_lang,
                proxies={'https': self.current_proxy}
            ).translate(text[:MAX_CHARS_PER_REQUEST])
        except Exception as e:
            print(f"Microsoft failed: {str(e)[:100]}")
            return None

    def _try_libre(self, text, source_lang, target_lang):
        try:
            return LibreTranslator(
                source=source_lang,
                target=target_lang,
                base_url='https://libretranslate.de'
            ).translate(text[:MAX_CHARS_PER_REQUEST])
        except Exception as e:
            print(f"Libre failed: {str(e)[:100]}")
            return None

    def detect_language(self, text_sample):
        """Auto-detect source language from sample text"""
        try:
            return detect(text_sample)
        except:
            return 'auto'

    def translate_text(self, text, target_lang, source_lang='auto'):
        """Robust translation with all fallbacks"""
        if not text.strip():
            print("⚠️ Skipping empty or invalid text.")
            return text

        # Chunk large texts
        if len(text) > MAX_CHARS_PER_REQUEST:
            chunks = [text[i:i+MAX_CHARS_PER_REQUEST] for i in range(0, len(text), MAX_CHARS_PER_REQUEST)]
            return ' '.join([self.translate_text(chunk, target_lang, source_lang) for chunk in chunks])

        # Try all providers with proxy rotation
        for attempt in range(3):  # Max 3 attempts
            self._rotate_proxy()
            for provider in self.provider_order:
                result = provider(text, source_lang, target_lang)
                if result:
                    time.sleep(REQUEST_DELAY)
                    return result
            print(f"⚠️ All providers failed on attempt {attempt + 1}. Retrying...")
            time.sleep(5)  # Backoff on complete failure

        self.failed_count += 1
        print(f"⚠️ Failed to translate: {text[:50]}...")
        print(f"   Target language: {target_lang}, Source language: {source_lang}")
        print(f"   Last proxy used: {self.current_proxy}")
        return text  # Return original as fallback

    def process_subtitle(self, sub, target_lang, source_lang):
        """Process single subtitle with progress tracking"""
        try:
            result = {
                'num': sub['num'],
                'timecode': sub['timecode'],
                'original_text': sub['text'],
                'translated_text': self.translate_text(sub['text'], target_lang, source_lang)
            }
            self.translated_count += 1
            return result
        except Exception as e:
            print(f"⚠️ Failed to process subtitle {sub['num']}: {str(e)}")
            self.failed_count += 1
            return {
                'num': sub['num'],
                'timecode': sub['timecode'],
                'original_text': sub['text'],
                'translated_text': sub['text']  # Return original text as fallback
            }

def parse_srt(file_path):
    """Parse SRT file into structured blocks"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []

    for block in blocks:
        if not block.strip():
            continue

        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 3:
            continue

        subtitles.append({
            'num': lines[0],
            'timecode': lines[1],
            'text': '\n'.join(lines[2:])  
        })

    return subtitles

def save_progress(subtitles, output_path, batch_file=None):
    """Save translated subtitles (full or partial)"""
    if batch_file:
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(subtitles, f)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for sub in subtitles:
            f.write(f"{sub['num']}\n{sub['timecode']}\n{sub['translated_text']}\n\n")

def load_progress(batch_file):
    """Resume from saved batch file"""
    with open(batch_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def translate_srt(input_path, output_path, target_lang):
    """Main translation workflow"""
    # Setup
    translator = SubtitleTranslator()
    input_path = Path(input_path)
    output_path = Path(output_path)
    batch_file = input_path.with_suffix('.batch')
    
    # Initialize source_lang
    source_lang = 'auto'  # Default to 'auto' if not detected

    # Resume or start new
    if batch_file.exists():
        print("⏩ Resuming previous translation...")
        subtitles = load_progress(batch_file)
        remaining = [s for s in subtitles if 'translated_text' not in s]
        # Attempt to detect language from existing subtitles if possible
        if subtitles:
            sample_text = ' '.join([s['text'] for s in subtitles[:3]])
            source_lang = translator.detect_language(sample_text)
            print(f"🌍 Detected source language: {source_lang}")
    else:
        print("🔍 Parsing SRT file...")
        subtitles = parse_srt(input_path)
        remaining = subtitles.copy()
        
        # Auto-detect language from first 3 subtitles
        if subtitles:
            sample_text = ' '.join([s['text'] for s in subtitles[:3]])
            source_lang = translator.detect_language(sample_text)
            print(f"🌍 Detected source language: {source_lang}")

    # Process in batches
    print(f"🔧 Translating {len(remaining)} subtitles to {target_lang}...")
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        for i in range(0, len(remaining), BATCH_SAVE_EVERY):
            batch = remaining[i:i+BATCH_SAVE_EVERY]
            
            try:
                results = list(executor.map(
                    lambda s: translator.process_subtitle(s, target_lang, source_lang),
                    batch
                ))
            except Exception as e:
                print(f"⚠️ Failed to process batch {i//BATCH_SAVE_EVERY + 1}: {str(e)}")
                continue
            
            # Update main list
            for result in results:
                idx = next(i for i, s in enumerate(subtitles) if s['num'] == result['num'])
                subtitles[idx] = result
            
            # Save progress
            save_progress(subtitles, output_path, batch_file)
            print(f"✅ Saved batch {i//BATCH_SAVE_EVERY + 1} ({translator.translated_count} total)")
    
    # Final save
    save_progress(subtitles, output_path)
    batch_file.unlink(missing_ok=True)
    
    print(f"\n🎉 Translation complete!")
    print(f"   Total: {len(subtitles)}")
    print(f"   Failed: {translator.failed_count}")
    print(f"   Saved to: {output_path}")
    
if __name__ == "__main__":
    translate_srt("input.srt", "translated.srt")


