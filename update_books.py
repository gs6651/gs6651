import os
import re

# File Paths
books_file = r"C:\Users\Gaurav\Documents\GitLocal\gs6651\Library\Books_to_Read.md"
readme_file = r"C:\Users\Gaurav\Documents\GitLocal\gs6651\README.md"

def update_counts():
    with open(books_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count statuses
    done = len(re.findall(r'\|\s*(Read|Completed|Done)\s*\|', content, re.IGNORECASE))
    reading = len(re.findall(r'\|\s*(Reading)\s*\|', content, re.IGNORECASE))
    todo = len(re.findall(r'\|\s*(Yet to Start)\s*\|', content, re.IGNORECASE))
    total = done + reading + todo

    with open(readme_file, 'r', encoding='utf-8') as f:
        readme = f.read()

    # Update the lines
    readme = re.sub(r'(- ✅ \*\*Read:\*\* )\d+', r'\g<1>' + str(done), readme)
    readme = re.sub(r'(- 📖 \*\*Reading:\*\* )\d+', r'\g<1>' + str(reading), readme)
    readme = re.sub(r'(- ⏳ \*\*Yet to Start:\*\* )\d+', r'\g<1>' + str(todo), readme)
    readme = re.sub(r'(- 📚 \*\*Total Books:\*\* )\d+', r'\g<1>' + str(total), readme)

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"✅ README Updated: Total {total} books.")

if __name__ == "__main__":
    update_counts()