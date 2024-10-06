from bs4 import BeautifulSoup
import cv2
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

URL = "https://ecare.nfu.edu.tw/"
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=chrome_options)

async def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    adaptive_threshold = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 7.5)
    return adaptive_threshold

async def ecare_login(account, password):
    while True:
        try:
            driver.get(URL)
            
            # 抓取驗證碼圖片元素
            captcha_img = driver.find_element(By.ID, "authimg")
            
            # 獲取驗證碼圖片的位置和大小
            location = captcha_img.location
            size = captcha_img.size
            left = location['x']
            top = location['y']
            right = left + size['width']
            bottom = top + size['height']
            
            # 截取瀏覽器中驗證碼圖片的區域
            screenshot = driver.get_screenshot_as_png()
            screenshot = Image.open(BytesIO(screenshot))
            captcha_image = screenshot.crop((left, top, right, bottom))
            
            # 將圖片轉換為numpy數組
            img_np = np.array(captcha_image)
            
            # 預處理圖片並顯示每一步結果
            preprocessed_image = await preprocess_image(img_np)
            
            # 使用OCR庫識別驗證碼
            chksum = pytesseract.image_to_string(preprocessed_image, config=custom_config).strip()
            print(f"識別出的驗證碼: {chksum}")

            # 模擬登錄
            driver.find_element(By.ID, "login_acc").send_keys(account)
            driver.find_element(By.ID, "login_pwd").send_keys(password)
            driver.find_element(By.ID, "login_chksum").send_keys(chksum)
            driver.find_element(By.ID, "bt_login").click()

            # 檢查是否需要重新登入
            if "回上一頁，重新登入" in driver.page_source:
                print("重新登入...")
                continue

            # 如果沒有重新登入的提示，結束循環
            break

        except Exception as e:
            print(f"發生錯誤: {e}")
            break
        
    driver.get("https://ecare.nfu.edu.tw/aaiqry/studscore")

    # 獲取頁面源代碼並解析
    page_source = driver.page_source
    driver.get("https://ecare.nfu.edu.tw/login/authout?out=1")
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # 查找表格
    table = soup.find('table', {'class': 'tbcls'})  # 根據實際情況修改TABLE_ID

    # 提取表格數據
    headers = [header.text for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:-1]:  # 跳過標題行
        cols = row.find_all('td')
        rows.append([col.text.strip() for col in cols])
    
    # 使用pandas創建DataFrame
    df = pd.DataFrame(rows, columns=headers)
    print(df)
    # 设置字體
    columns_to_drop = ['序號', '學年', '學期', '修課人數']
    col_widths = [0.25, 0.05, 0.05, 0.07, 0.07, 0.13, 0.15]
    df_filtered = df.drop(columns=columns_to_drop)
    prop = fm.FontProperties(fname='./font.ttf')  # 替換為字體文件的實際路徑
    # 生成图表
    background = Image.open('NFU.png')
    background = ImageOps.fit(background, (1920, 1080))
    fig, ax = plt.subplots(figsize=(19.2, 10.8))  # 设置图片大小
    ax.imshow(background, extent=[0, 1, 0, 1], aspect='auto')
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df_filtered.values, colLabels=df_filtered.columns, cellLoc='center', loc='center', colWidths=col_widths)
    table.scale(1, 1)

    # 设置单元格边距和背景颜色
    for key, cell in table.get_celld().items():
        cell_text = cell.get_text()
        cell_text.set_fontproperties(prop)
        cell_text.set_fontsize(24)  # 调整字体大小
        cell.set_edgecolor('black')  # 设置边框颜色
        cell.set_height(cell.get_height() + 0.015)  # 增加单元格高度
        cell.set_text_props(ha='center', va='center', color='black')  # 设置文本对齐方式和颜色
        row, col = key
        if row == 0:
            cell.set_facecolor('#40466e')  # Header color
            cell.set_text_props(color='w')
        elif row % 2 == 0:
            cell.set_facecolor('#BABABA')
        else:
            cell.set_facecolor('#ffffff')

    # 保存图表为图片
    plt.savefig('output_table.png', bbox_inches='tight', dpi=100)
    plt.close()
    # 打開保存的圖表
    output_image = Image.open('output_table.png')

        # 加載浮水印圖像
    watermark = Image.open('NFU_removebg.png').convert("RGBA")

    # 調整浮水印大小
    base_width = 828  # 你可以根據需要調整這個值
    w_percent = (base_width / float(watermark.size[0]))
    h_size = int((float(watermark.size[1]) * float(w_percent)))
    watermark = watermark.resize((base_width, h_size), Image.Resampling.LANCZOS)

    # 調整浮水印的透明度
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.165)
    watermark.putalpha(alpha)

    # 將浮水印放在圖表中間
    layer = Image.new('RGBA', output_image.size, (0,0,0,0))
    position = ((output_image.width - watermark.width) // 2, (output_image.height - watermark.height) // 2)
    layer.paste(watermark, position)

    # 合併兩張圖片
    final_image = Image.alpha_composite(output_image.convert('RGBA'), layer)

    # 保存最終圖像
    final_image.save('final_output.png')
