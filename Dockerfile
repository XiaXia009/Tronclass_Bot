# 使用Python 3.12.3作為基礎映像
FROM python:3.12.3

# 安裝必要的系統包，包括tesseract-ocr和libGL
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 將requirements.txt複製到工作目錄
COPY requirements.txt .

# 安裝requirements.txt中的依賴
RUN pip install --no-cache-dir -r requirements.txt

# 將當前目錄中的所有內容複製到工作目錄
COPY . .

# 執行fkustupitbot.py
CMD ["python", "fkustupitbot.py"]
