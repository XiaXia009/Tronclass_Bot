# 👾Tronclass_Bot👾
最近因該會開始重構這個東西  
可以在各Tronclass變體使用 如:虎尾科技大學Ulearn  
該程式掛載在discord機器人上  
目前僅支援數字點名 雷達點名還沒測試  
  
你會需要[ocr-tesseract](https://github.com/UB-Mannheim/tesseract/wiki) 並且需要把路徑加到環境變數💩  

<table>
  <tr>
    <td>
      <b>雷達點名:</b><br>
      (但我沒有更新到機器人裡 你要自己接🫶)
      <br><br>
      <a href="https://github.com/XiaXia009/Tronclass_Position">
        <img src="https://github-readme-stats.vercel.app/api/pin/?username=XiaXia009&repo=Tronclass_Position&theme=prussian" />
      </a>
    </td>
    <td>
      <b>數字點名 (簡潔版本):</b><br>
      如果你只是要幫自己點名的話，用這個版本就好
      <br><br>
      <a href="https://github.com/silvercow002/tronclass-script">
        <img src="https://github-readme-stats.vercel.app/api/pin/?username=silvercow002&repo=tronclass-script&theme=prussian" />
      </a>
    </td>
  </tr>
</table>

## 如果你想自己架設或開發
#### 文件介紹
`ulearn.py`: Tronclass的登入/點名模組，這需要替換為自己學校的網址跟登入方法  
`fkustupidbot.py`: 機器人的主文件(啟動方法) 在這裡替換為你的token  
`score.py`: 教育部的[cloud school](https://stern-information.gitbook.io/)網站的分數查詢  
(如果你的學校有使用教育部[cloud school](https://stern-information.gitbook.io/)系統)  
`wcin.py`: 一個很難維護的課表時間查詢😵  
`json_edit.py`: 編輯/讀取帳密  
`userdata.json`: 儲存在這裡的帳密是為經加密的 請自己確保資料安全🫵  
`userimg`: 這個資料夾是學生頭像的緩存  
  
有給dockerfile可以自己構建docker :>  
如果你需要幫助或者有任何問題: [issues👾](https://github.com/XiaXia009/Tronclass_Bot/issues/new)  

## 或許你想看看怎麼樣
### 可以使用的指令
```
/set_channel 設定頻道
/ulearn_login 登入自己的帳號
/test_my_account 在機器人測試帳號登入
/del_my_account 讓機器人解綁帳號
/ulearn_sign_in 簽到
/shut_up 使用人與被使用人各有50%機率被禁言10秒
/課表 顯示課表
/教學問卷 NFU 教學問卷連結
/反饋 
/修復 執行此指令有機會修復登入失敗
/下節甚麼課 
```
### 在機器人登入帳號
![login](https://github.com/XiaXia009/NFU_Ulearn_Signin/blob/main/readme/login.png)
### 使用機器人點名
![roll_all](https://github.com/XiaXia009/NFU_Ulearn_Signin/blob/main/readme/roll%20call.png)
### 更多功能
![next](https://github.com/XiaXia009/NFU_Ulearn_Signin/blob/main/readme/next%20class.png)
![table](https://github.com/XiaXia009/NFU_Ulearn_Signin/blob/main/readme/curriculum.png)
