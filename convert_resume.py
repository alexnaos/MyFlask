import re
import subprocess
from pathlib import Path

# --- НАСТРОЙКИ ---
DOCX_FILE = r"C:\YandexDisk\Я_док\РезюмеЗолотовГАП.docx"
PROJECT_STATIC = Path(r"C:\Projects\MyFlask\api\static")
OUTPUT_MD = PROJECT_STATIC / "resume.md"
IMAGES_DIR = PROJECT_STATIC / "images" 

# ВОТ НАШ «ВРАГ» - абсолютный путь, который пишет Pandoc
BAD_PATH = str(PROJECT_STATIC) + "\\images\\media\\"
BAD_PATH_SLASH = str(PROJECT_STATIC).replace("\\", "/") + "/images/media/"
# -----------------

def convert():
    print("1. Конвертация...")
    cmd = [
        "pandoc", DOCX_FILE, "-t", "markdown_strict", "--wrap=none",
        "--extract-media", str(IMAGES_DIR), "-o", str(OUTPUT_MD)
    ]
    subprocess.run(cmd, check=True)

    print("2. Жесткая замена путей...")
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()

    # Удаляем абсолютный путь с бэкслэшами (C:\Projects...)
    content = content.replace(BAD_PATH, "/static/images/media/")
    # Удаляем абсолютный путь с обычными слэшами (C:/Projects...)
    content = content.replace(BAD_PATH_SLASH, "/static/images/media/")
    
    # Если Pandoc оставил просто images/media/, добавляем /static/
    content = content.replace('src="images/media/', 'src="/static/images/media/')
    content = content.replace('](images/media/', '](/static/images/media/')

    # Убираем оставшиеся параметры ширины и высоты (они ломают вёрстку)
    content = re.sub(r'\{width="[^"]*"\s*height="[^"]*"\}', '', content)
    content = re.sub(r'\{width="[^"]*"\}', '', content)
    content = re.sub(r'\{height="[^"]*"\}', '', content)
    
    # Чиним возможные двойные слэши
    content = content.replace('//static/', '/static/')

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(content)
    print("   Готово!")

if __name__ == "__main__":
    convert()