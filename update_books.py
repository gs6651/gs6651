import os
import re

# File Paths
books_file = r"C:\Users\Gaurav\Documents\GitLocal\gs6651\Library\Books_to_Read.md"
readme_file = r"C:\Users\Gaurav\Documents\GitLocal\gs6651\README.md"

def update_counts():
    # 1. Read the Books file
    with open(books_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. Count statuses (Case-insensitive)
    done_count = len(re.findall(r'\|\s*(Read|Completed|Done)\s*\|', content, re.IGNORECASE))
    reading_count = len(re.findall(r'\|\s*(Reading)\s*\|', content, re.IGNORECASE))
    todo_count = len(re.findall(r'\|\s*(Yet to Start)\s*\|', content, re.IGNORECASE))

    # 3. Read the README file
    with open(readme_file, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # 4. Replace the specific lines in README
    readme_content = re.sub(r'(- ✅ \*\*Read:\*\* )\d+', r'\g<1>' + str(done_count), readme_content)
    readme_content = re.sub(r'(- 📖 \*\*Currently Reading:\*\* )\d+', r'\g<1>' + str(reading_count), readme_content)
    readme_content = re.sub(r'(- ⏳ \*\*Yet to Start:\*\* )\d+', r'\g<1>' + str(todo_count), readme_content)

    # 5. Save the updated README
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Update Successful! Read: {done_count}, Reading: {reading_count}, To-Do: {todo_count}")

if __name__ == "__main__":
    update_counts()
