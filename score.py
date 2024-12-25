from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import matplotlib.font_manager as fm
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
from PIL import Image, ImageOps, ImageEnhance
from bs4 import BeautifulSoup
from io import BytesIO
import pandas as pd
import numpy as np
import pytesseract
import cv2

Home_URL = "https://ecare.nfu.edu.tw"
Login_URL = f"{Home_URL}/login/auth"
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    adaptive_threshold = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 7.5)
    return adaptive_threshold

async def ecare_login(account, password):
    global headers
    while True:
        driver.get(Home_URL)
        driver.execute_script("window.alert = function() {};")
        driver.execute_script("window.confirm = function() { return true; };")
        driver.execute_script("window.prompt = function() { return null; };")

        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="authimg"]')))

        screenshot_as_bytes = element.screenshot_as_png
        captcha_image = Image.open(BytesIO(screenshot_as_bytes))
        img_np = np.array(captcha_image)
        
        preprocessed_image = preprocess_image(img_np)
        chksum = pytesseract.image_to_string(preprocessed_image, config=custom_config).strip()
        print(f"識別出的驗證碼: {chksum}")
        driver.find_element(By.ID, "login_acc").send_keys(account)
        driver.find_element(By.ID, "login_pwd").send_keys(password)
        driver.find_element(By.ID, "login_chksum").send_keys(chksum)
        driver.find_element(By.ID, "bt_login").click()
        print(driver.page_source)
        if "回上一頁，重新登入" in driver.page_source:
            print("重新登入...")
            continue
        break
    try:
        driver.get("https://ecare.nfu.edu.tw/aaiqry/studscore")
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/aside/section/ul/li[6]/ul/li[4]'))).click()

        page_source = driver.page_source
        driver.get("https://ecare.nfu.edu.tw/login/authout?out=1")
        soup = BeautifulSoup(page_source, 'html.parser')
        
        table = soup.find('table', {'class': 'tbcls'})
        headers = [header.text for header in table.find_all('th')]
        rows = []
        for row in table.find_all('tr')[1:-1]:  # 跳過標題行
            cols = row.find_all('td')
            rows.append([col.text.strip() for col in cols])
        
        df = pd.DataFrame(rows, columns=headers)
        print(df)
        columns_to_drop = ['序號', '學年', '學期', '修課人數']
        col_widths = [0.25, 0.05, 0.05, 0.07, 0.07, 0.13, 0.15]
        df_filtered = df.drop(columns=columns_to_drop)
        prop = fm.FontProperties(fname='./font.ttf')
        background = Image.open('NFU.png')
        background = ImageOps.fit(background, (1920, 1080))
        fig, ax = plt.subplots(figsize=(19.2, 10.8))
        ax.imshow(background, extent=[0, 1, 0, 1], aspect='auto')
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=df_filtered.values, colLabels=df_filtered.columns, cellLoc='center', loc='center', colWidths=col_widths)
        table.scale(1, 1)

        for key, cell in table.get_celld().items():
            cell_text = cell.get_text()
            cell_text.set_fontproperties(prop)
            cell_text.set_fontsize(24)
            cell.set_edgecolor('black')
            cell.set_height(cell.get_height() + 0.015)
            cell.set_text_props(ha='center', va='center', color='black')
            row, col = key
            if row == 0:
                cell.set_facecolor('#40466e')
                cell.set_text_props(color='w')
            elif row % 2 == 0:
                cell.set_facecolor('#BABABA')
            else:
                cell.set_facecolor('#ffffff')

        plt.savefig('output_table.png', bbox_inches='tight', dpi=100)
        plt.close()

        output_image = Image.open('output_table.png')
        watermark = Image.open('NFU_removebg.png').convert("RGBA")
        base_width = 828
        w_percent = (base_width / float(watermark.size[0]))
        h_size = int((float(watermark.size[1]) * float(w_percent)))
        watermark = watermark.resize((base_width, h_size), Image.Resampling.LANCZOS)
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.165)
        watermark.putalpha(alpha)
        layer = Image.new('RGBA', output_image.size, (0,0,0,0))
        position = ((output_image.width - watermark.width) // 2, (output_image.height - watermark.height) // 2)
        layer.paste(watermark, position)
        final_image = Image.alpha_composite(output_image.convert('RGBA'), layer)

        final_image.save('final_output.png')
    except:
        driver.get("https://ecare.nfu.edu.tw/login/authout?out=1")
        await ecare_login(account, password)
