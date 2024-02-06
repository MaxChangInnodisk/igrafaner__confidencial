import logging
from logging.handlers import RotatingFileHandler
import datetime
import os

# 建立 Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 建立 Stream Handler，將所有訊息顯示在螢幕上
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 建立 Rotating File Handler，僅記錄錯誤訊息，以日期為檔名
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.mkdir(log_folder)
log_filename = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
log_path = os.path.join(log_folder, log_filename)

file_handler = RotatingFileHandler(log_path, maxBytes=1024*10, backupCount=10, mode='a+')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)