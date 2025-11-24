import re

# Read the file
with open('phi4_plus_adaptive_validation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all emoji and special Unicode characters
# Replace with plain text equivalents
replacements = {
    '🔴': 'RED',
    '🟠': 'ORANGE',
    '🟡': 'YELLOW',
    '🟢': 'GREEN',
    '⚪': 'WHITE',
    '🌡️': 'TEMP',
    '⏸️': 'PAUSE',
    '🔄': 'CYCLE',
    '📄': 'FILE',
    '📁': 'FOLDER',
    '✅': '[PASS]',
    '❌': '[FAIL]',
    '⚠️': '[WARN]',
    '✓': 'OK',
    '✗': 'FAIL',
}

for emoji, text in replacements.items():
    content = content.replace(emoji, text)

# Remove any remaining emoji using regex (Unicode ranges)
# This removes all emoji characters
content = re.sub(r'[\U0001F300-\U0001F9FF]', '', content)  # Misc symbols and pictographs
content = re.sub(r'[\U0001F600-\U0001F64F]', '', content)  # Emoticons
content = re.sub(r'[\U0001F680-\U0001F6FF]', '', content)  # Transport and map
content = re.sub(r'[\U0001F700-\U0001F77F]', '', content)  # Alchemical
content = re.sub(r'[\U0001F780-\U0001F7FF]', '', content)  # Geometric shapes
content = re.sub(r'[\U0001F800-\U0001F8FF]', '', content)  # Supplemental arrows
content = re.sub(r'[\U0001F900-\U0001F9FF]', '', content)  # Supplemental symbols
content = re.sub(r'[\U0001FA00-\U0001FA6F]', '', content)  # Chess symbols
content = re.sub(r'[\U0001FA70-\U0001FAFF]', '', content)  # Symbols and pictographs
content = re.sub(r'[\U00002600-\U000026FF]', '', content)  # Misc symbols
content = re.sub(r'[\U00002700-\U000027BF]', '', content)  # Dingbats
content = re.sub(r'[\uFE0F]', '', content)  # Variation selector

# Write back
with open('phi4_plus_adaptive_validation.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Unicode cleanup complete!")
