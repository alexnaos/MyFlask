import os
import re
from datetime import datetime

VAULT_PATH = r"C:\YandexDisk\Obsidian Vault"
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), "notes_table.html")

def extract_title(filepath):
    """Extract a nice title from the filename."""
    basename = os.path.basename(filepath)
    name, _ = os.path.splitext(basename)
    # If filename looks like "2026-04-13.md", return just the date part formatted
    # Otherwise return the name as-is
    return name

def extract_date(filepath):
    """Get the modification date of the file."""
    mtime = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(mtime)
    return dt.strftime("%d.%m.%Y %H:%M")

def is_note_file(filename):
    """Check if file is a markdown note (exclude system files, .obsidian, etc.)"""
    # Only .md files at the top level (not in subdirectories)
    if not filename.endswith('.md'):
        return False
    # Exclude files in known non-note directories
    # We'll handle this by checking the path depth
    return True

def main():
    notes = []
    
    # Walk the vault directory, but only top-level .md files
    for entry in os.listdir(VAULT_PATH):
        full_path = os.path.join(VAULT_PATH, entry)
        if os.path.isfile(full_path) and entry.endswith('.md'):
            title = extract_title(full_path)
            date = extract_date(full_path)
            notes.append({
                'title': title,
                'date': date,
                'path': full_path
            })
    
    # Sort notes by date descending (newest first)
    notes.sort(key=lambda x: x['date'], reverse=True)
    
    # Generate HTML table
    html = ['<html><head><meta charset="UTF-8">']
    html.append('<style>')
    html.append('body { font-family: Arial, sans-serif; margin: 20px; }')
    html.append('table { border-collapse: collapse; width: 100%; margin-top: 20px; }')
    html.append('th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }')
    html.append('th { background-color: #f2f2f2; }')
    html.append('.open-btn { padding: 5px 10px; background: #0066cc; color: white; border: none; cursor: pointer; }')
    html.append('.open-btn:hover { background: #0055aa; }')
    html.append('</style>')
    html.append('</head><body>')
    html.append('<h1>Заметки Obsidian Vault</h1>')
    html.append('<table>')
    html.append('<tr><th>Название</th><th>Дата</th><th>Открыть</th></tr>')
    
    for note in notes:
        # Create a clickable link that opens the file
        # Using JavaScript to show a preview or just link to file
        html.append(f'<tr>')
        html.append(f'<td>{note["title"]}</td>')
        html.append(f'<td>{note["date"]}</td>')
        html.append(f'<td><button class="open-btn" onclick="window.open(\'file://{note["path"]}\', \'_blank\')">Открыть</button></td>')
        html.append(f'</tr>')
    
    html.append('</table>')
    html.append('</body></html>')
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f"Generated {OUTPUT_HTML} with {len(notes)} notes")

if __name__ == "__main__":
    main()