import json
import cv2
import numpy as np
import pytesseract
import requests
import base64
import json_edit
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

async def Ulearn(interaction, username, password, user_id, initial=True, message=None):
    if initial:
        await interaction.response.defer()
        message = await interaction.followup.send('正在嘗試登入...')
    else:
        await interaction.followup.edit_message(message_id=message.id, content=f'{message.content}\n重試中...')

    with session.get(URL, headers=Agent) as response:
        body = BeautifulSoup(response.text, 'html.parser')
        action_url = body.find('form', class_='form-signin form-login')['action']
        img, key = codeImg()
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        code = text.replace(" ", "").strip()
        await interaction.followup.edit_message(message_id=message.id, content=f"驗證碼: {text}")

        login_pay = {
            'username': username,
            'password': password,
            'captchaCode': code,
            'captchaKey': key
        }
        response = session.post(action_url, data=login_pay, headers=Agent)

        if response.status_code == 200:
            response_body = BeautifulSoup(response.text, 'html.parser')
            logout_links = response_body.find_all('a', string="登出")
            root_scope_var = response_body.find('root-scope-variable', {'name': 'currentUserName'})
            if logout_links:
                json_edit.add_user(username, password)
                await interaction.followup.edit_message(message_id=message.id, content=f"{interaction.user.mention}\n登入成功 {root_scope_var['value']}")
            else:
                info = response_body.find('span', {'style': 'color:red'})
                if info:
                    message_content = info.get_text()
                    await interaction.followup.edit_message(message_id=message.id, content=f"驗證碼: {text}\n{message_content}")
                    if message_content == "驗證碼錯誤":
                        await Ulearn(interaction, username, password, initial=False, message=message)
                    elif message_content == "無效的帳號或密碼":
                        await interaction.followup.edit_message(message_id=message.id, content=f"驗證碼: {text}\n無效的帳號或密碼，請檢查您的帳號和密碼。")
                    return
                else:
                    await interaction.followup.edit_message(message_id=message.id, content="未知的錯誤")
                return
        
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
                if not result:
                    await interaction.channel.send("暫無點名")
            except Exception as e:
                await interaction.send("點名列表獲取失敗")
                return

        answer_pay = {
            "numberCode": "1234"
        }
        async def return_rollcall():
            _rollcall = session.put(f"{API}/api/rollcall/{class_id}/answer_number_rollcall", data=answer_pay, headers=Agent)
            await interaction.followup.send(_rollcall)
            "https://tronclass.com.tw/api/radar/rollcalls?api_version=1.1.0" #可點名列表
            "https://tronclass.com.tw/statistics/api/user-visits" #用戶狀態
            "https://tronclass.com.tw/api/rollcall/{class_id}/answer_number_rollcall" #數字點名code返回
