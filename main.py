import cv2
import numpy as np
import pytesseract
import requests
import base64
from dotenv import get_key
from bs4 import BeautifulSoup

username = get_key(".env","USERNAME")
password = get_key(".env","PASSWORD")
URL = "https://identity.nfu.edu.tw/auth/realms/nfu/protocol/cas/login?service=https://ulearn.nfu.edu.tw/login"
Agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
session = requests.Session()

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    adaptive_threshold = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 7.5)
    kernel = np.ones((4, 3), np.uint8)
    dilated = cv2.dilate(adaptive_threshold, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    return eroded

def codeImg():
    captcha_url = 'https://identity.nfu.edu.tw/auth/realms/nfu/captcha/code'
    with session.get(captcha_url) as response:
        if response.status_code != 200:
            response.raise_for_status()
        data = response.json()
        base64_data = data['image'].split(',')[1]
        img_data = base64.b64decode(base64_data)
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img, data['key']

with session.get(URL, headers=Agent) as response:
    body = BeautifulSoup(response.text, 'html.parser')
    form = body.find('form', {'class': 'form-signin form-login'})
    action_url = form['action']
    img, key = codeImg()
    processed_img = preprocess_image(img)
    text = pytesseract.image_to_string(processed_img, config=custom_config)
    code = text.replace(" ", "").strip()
    print(f"text: {text}")

    pay = {
        'username': username,
        'password': password,
        'captchaCode': code,
        'captchaKey': key
    }
    print(action_url)
    response = session.post(action_url, data=pay, headers=Agent)

    if response.status_code == 200:
        response_body = BeautifulSoup(response.text, 'html.parser')
        logout_links = response_body.find_all('a', string="登出")
        if logout_links:
            print("登入成功")
        else:
            print("驗證碼錯誤")