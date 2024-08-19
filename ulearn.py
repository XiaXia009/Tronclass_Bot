import json
import cv2
import numpy as np
import pytesseract
import aiohttp
import base64
import os
from bs4 import BeautifulSoup
import json_edit

API = "https://ulearn.nfu.edu.tw"
URL = "https://identity.nfu.edu.tw/auth/realms/nfu/protocol/cas/login?service=https://ulearn.nfu.edu.tw/login"
Agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

if not os.path.exists('./userimg/'):
    os.makedirs('./userimg/')

async def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    adaptive_threshold = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 7.5)
    kernel = np.ones((4, 3), np.uint8)
    dilated = cv2.dilate(adaptive_threshold, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    return eroded

async def codeImg(session):
    captcha_url = 'https://identity.nfu.edu.tw/auth/realms/nfu/captcha/code'
    async with session.get(captcha_url) as response:
        if response.status != 200:
            response.raise_for_status()
        data = await response.json()
        base64_data = data['image'].split(',')[1]
        img_data = base64.b64decode(base64_data)
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img, data['key']

async def Relord(session):
    try:
        await session.get("https://ulearn.nfu.edu.tw/logout")
        await session.get("https://identity.nfu.edu.tw/auth/realms/nfu/protocol/cas/logout?service=https%3A//ulearn.nfu.edu.tw&locale=zh_TW")
    except:
        pass

async def Ulearn(interaction, username, password, DC_user_id, retry_count, put):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers=Agent) as response:
            body = BeautifulSoup(await response.text(), 'html.parser')
            action_url = body.find('form', class_='form-signin form-login')['action']
            img, key = await codeImg(session)
            processed_img = await preprocess_image(img)
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            code = text.replace(" ", "").strip()

            status_message = f"驗證碼: {text}".strip()
            if retry_count > 0:
                status_message += f"\n重試中: {retry_count}"

            await interaction.edit_original_response(content=status_message)

            login_pay = {
                'username': username,
                'password': password,
                'captchaCode': code,
                'captchaKey': key
            }
            async with session.post(action_url, data=login_pay, headers=Agent) as login_response:
                if login_response.status != 200:
                    return None, None, "登入失敗"

                response_body = BeautifulSoup(await login_response.text(), 'html.parser')
                logout_links = response_body.find_all('a', string="登出")
                ch_name = response_body.find('root-scope-variable', {'name': 'currentUserName'})
                
                try:
                    header_div = response_body.find('div', class_='header header-autocollapse wg-header')
                    if header_div is not None:
                        ng_init_content = header_div.get('ng-init', '')
                        start = ng_init_content.find("avatarSmallUrl = '") + len("avatarSmallUrl = '")
                        end = ng_init_content.find("';", start)
                        avatar_small_url = ng_init_content[start:end]
                        avatar_url = avatar_small_url.replace('?thumbnail=32x32', '?thumbnail=300x300')
                        async with session.get(avatar_url) as avatar_response:
                            img_data = await avatar_response.read()
                            img_path = f'./userimg/{username}.png'
                            with open(img_path, 'wb') as handler:
                                handler.write(img_data)
                    else:
                        img_path = None
                except:
                    img_path = None
                
                if logout_links:
                    if put == False:
                        await Relord(session)
                    elif isinstance(put, str):
                        async with session.get(f"{API}/api/radar/rollcalls?api_version=1.1.0") as rollcalls_response:
                            rollcalls = await rollcalls_response.json()
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
                                answer_pay = {
                                    "numberCode": put
                                }
                                if not result:
                                    await Relord(session)
                                    return None, None, "暫無點名"
                            except:
                                await Relord(session)
                                return None, None, "意外錯誤"
                            
                            async with session.put(f"{API}/api/rollcall/{class_id}/answer_number_rollcall", json=answer_pay, headers=Agent) as rollcall_response:
                                _rollcall = await rollcall_response.json()
                                await Relord(session)
                                if _rollcall['status'] == "on_call":
                                    return ch_name["value"], True, None
                                else:
                                    return ch_name["value"], False, None
                    
                    json_edit.add_user(username, password, DC_user_id)
                    return ch_name["value"], img_path, None
                else:
                    info = response_body.find('span', {'style': 'color:red'})
                    if info:
                        message_content = info.get_text()
                        return None, None, message_content
                    else:
                        return None, None, "未知的錯誤"