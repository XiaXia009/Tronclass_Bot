import json
import cv2
import numpy as np
import pytesseract
import requests
import base64
from dotenv import get_key
from bs4 import BeautifulSoup


API = "https://ulearn.nfu.edu.tw"
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

def Ulearn(username, password):
    with session.get(URL, headers=Agent) as response:
        body = BeautifulSoup(response.text, 'html.parser')
        form = body.find('div ', {'class': 'form-signin form-login'})
        action_url = body.find('form', class_='form-signin form-login')['action']
        img, key = codeImg()
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        code = text.replace(" ", "").strip()
        print(f"text: {text}")

        login_pay = {
            'username': username,
            'password': password,
            'captchaCode': code,
            'captchaKey': key
        }
        print(action_url)
        response = session.post(action_url, data=login_pay, headers=Agent)

        if response.status_code == 200:
            response_body = BeautifulSoup(response.text, 'html.parser')
            logout_links = response_body.find_all('a', string="登出")
            if logout_links:
                print("登入成功")
            else:
                info = response_body.find('span', {'style': 'color:red'})
                if info:
                    message = info.get_text()
                    print(message)
                    if message == "驗證碼錯誤":
                        print("重試中...")
                        Ulearn(username, password)
                else:
                    print("未知的錯誤")
                exit(0)
        
            rollcalls = session.get(f"{API}/api/radar/rollcalls?api_version=1.1.0").json()
            
            try:
                result = []
                for rollcall in rollcalls["rollcalls"]:
                    result.append({
                        "course_title": rollcall["course_title"],
                        "created_by_name": rollcall["created_by_name"],
                        "rollcall_id": rollcall["rollcall_id"],
                        "is_number": rollcall["is_number"],
                        "source": rollcall["source"],
                        "status": rollcall["status"]
                    })
                    class_id = rollcall["rollcall_id"]
                print(json.dumps(result, ensure_ascii=False, indent=4))
                if result == []:
                    print("暫無點名")
            except:
                print("點名列表獲取失敗")
                exit(1)
        answer_pay = {
            "numberCode": "1234"
        }
        def return_rollcall():
            _rollcall = session.put(f"{API}/api/rollcall/{class_id}/answer_number_rollcall", data=answer_pay, headers=Agent)
            print(_rollcall)
            "https://tronclass.com.tw/api/radar/rollcalls?api_version=1.1.0" #可點名列表
            "https://tronclass.com.tw/statistics/api/user-visits" #用戶狀態
            "https://tronclass.com.tw/api/rollcall/{class_id}/answer_number_rollcall" #數字點名code返回
        
Ulearn("51215128", "RayLi97420")