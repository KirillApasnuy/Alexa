from dotenv import load_dotenv
import os

load_dotenv("dev.env")

# Конфигурация
VA_NAME = 'Alex'
VA_VER = "1.0"
VA_ALIAS = ('Alex',)
VA_TBR = ('скажи', 'покажи', 'ответь', 'произнеси', 'расскажи', 'сколько', 'слушай')

# ID микрофона
# -1 это стандартное записывающее устройство
MICROPHONE_INDEX = -1

# Путь к браузеру Google Chrome
CHROME_PATH = 'C:\Program Files\Google\Chrome\Application/chrome.exe %s'

# Токен Picovoice
PICOVOICE_TOKEN = os.getenv('PICOVOICE_TOKEN')

# Токен OpenAI
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
