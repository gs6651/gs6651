import os
import re
from collections import Counter

# File Paths
books_file = r"C:\Users\Gaurav\Documents\GitLocal\gs6651\Library\Books_to_Read.md"
readme_file = r"C:\Users\Gaurav\Documents\GitLocal\gs6651\README.md"

def update_counts():
    with open(books_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    book_names = []
    content = "".join(lines)

    # 1. Find all book names from the table
    for line in lines:
        if line.startswith('|') and 'Book Name' not in line and '---' not in line:
            # Extract name between the first two pipes
            parts = line.split('|')
            if len(parts) > 1:
                name = parts[1].strip()
                if name:
                    book_names.append(name)

    # 2. Check for duplicates
    counts = Counter(book_names)
    duplicates = [name for name, count in counts.items() if count > 1]
    
    if duplicates:
        print(f"⚠️ WARNING: Found duplicates: {', '.join(duplicates)}")
    else:
        print("✅ No duplicate books found.")

    # 3. Count statuses
    done = len(re.findall(r'\|\s*(Read|Completed|Done)\s*\|', content, re.IGNORECASE))
    reading = len(re.findall(r'\|\s*(Reading)\s*\|', content, re.IGNORECASE))
    todo = len(re.findall(r'\|\s*(Yet to Start)\s*\|', content, re.IGNORECASE))
    total = len(book_names)

    # 4. Update README
    with open(readme_file, 'r', encoding='utf-8') as f:
        readme = f.read()

    readme = re.sub(r'(- ✅ \*\*Read:\*\* )\d+', r'\g<1>' + str(done), readme)
    readme = re.sub(r'(- 📖 \*\*Reading:\*\* )\d+', r'\g<1>' + str(reading), readme)
    readme = re.sub(r'(- ⏳ \*\*Yet to Start:\*\* )\d+', r'\g<1>' + str(todo), readme)
    readme = re.sub(r'(- 📚 \*\*Total Books:\*\* )\d+', r'\g<1>' + str(total), readme)

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"✅ README Updated: Total {total} books.")

if __name__ == "__main__":
    update_counts()