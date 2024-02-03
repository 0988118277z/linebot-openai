from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, StickerSendMessage, ImageSendMessage
from linebot.models import TextMessage, ImageMessage, VideoMessage, AudioMessage, LocationMessage
from linebot.models import MessageEvent, FollowEvent, UnfollowEvent, JoinEvent
import os, requests, re
from chatbot import txt_to_img_openai, img_to_img_openai
from config import channel_access_token, channel_secret



app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        print(body, signature)
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def join_event(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='很高興你邀請ChatGpt API機器加入入群'))

@handler.add(FollowEvent)
def follow_event(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='歡迎加我好友'))

def ai_img(spell, userid, timestamp):
    #取得openai回權的圖片URL，將URL回覆給使用者
    img_url = txt_to_img_openai(spell)
     
    #儲存0.04美金的圖片
    sess = requests.Session()
    myHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    filename = f"./{userid}/{timestamp}.jpg"
    get_img = sess.get(img_url, headers = myHeader)  
    with open(filename,'wb') as output:  
        for chunk in get_img:
            output.write(chunk)
    return img_url

@handler.add(MessageEvent, message=TextMessage)
def text_request(event):
    #將使用該機器人的用戶，建立資料夾
    timestamp = event.timestamp
    userid = r'users/' + event.source.user_id
    if not os.path.exists(userid):
        os.makedirs(userid)
    spell_library = f"./{userid}/sl.csv"
    spell = ''
    
    if event.message.text == '#':
        with open(spell_library, 'r+', encoding='utf-8') as txt: 
            spell = '關鍵字,咒文\n'
            for i in txt:
                spell += i
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=spell))
            return 0
            
    elif event.message.text == '!':
        spell = '金嘆號後面要帶數字，才可使用咒語庫的咒語，若要查詢咒語庫 請輸入#'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=spell))
        return 0
        
    elif '#' == event.message.text[0]:
        re_title = re.compile(r'^#[\d\w._]+\s')
        re_num = re.compile(r'[\d\w._]+')
        spell_title = re_title.search(event.message.text).group()
        spell_num = re_num.search(spell_title).group()
        spell_txt = event.message.text.split(spell_title)[1]
        
        try:
            with open(spell_library, 'r', encoding='utf-8') as txt:  
                temp = [i.split(',')[0] for i in txt] 
        except:
            temp = ''
            with open(spell_library, 'a+', encoding='utf-8') as txt:  
                txt.write('')
        
        if spell_txt == 'del':  #刪除關鍵字
            temp_str = ''
            with open(spell_library, 'r', encoding='utf-8') as txt: 
                for i in txt:
                    if i.split(',')[0] == spell_num:
                        continue
                    else:
                        temp_str += i
            with open(spell_library, 'w', encoding='utf-8') as text:  
                text.write(temp_str)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='此關鍵字已成功被刪除'))
            return 0
        elif spell_num in temp:  #若已有關鍵字，則不給設置
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='此關鍵字已設置，請刪除或另外新增'))
            return 0
        else:   #若都沒有，則設置關鍵字            
            with open(spell_library, 'a+', encoding='utf-8') as txt:  
                txt.write(f'{spell_num},{spell_txt}' + '\n')
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=f'{spell_num}新增成功'))   
            return 0            
        
    elif '!' == event.message.text[0]:
        re_title = re.compile(r'^![\d\w._]+\s')
        re_num = re.compile(r'[\d\w._]+')
        spell_title = re_title.search(event.message.text).group()
        spell_num = re_num.search(spell_title).group()
        spell_txt = event.message.text.split(spell_title)[1]
        with open(spell_library, 'r', encoding='utf-8') as txt:  
            temp = {i.split(',')[0]:i.split(',')[1] for i in txt} 
        try:
            spell = temp[spell_num] + spell_txt
            img_url = ai_img(spell, userid, timestamp)
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
            return 0
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='並未設置此關鍵字'))
            return 0
        
    elif event.message.text == '使用說明':
        spell = ''' AI繪圖機器人使用說明
  #       可查詢目前已設定的咒語庫，
          咒語庫是由自己設定 關鍵字 與 咒語 的資料庫
  #temp      井字號後面帶關鍵字，可儲存咒語至咒語庫
             關鍵字只支援 文字,數字,底線,小數點
  #temp del  井字號後面帶關鍵字，空格後再帶del，可將關鍵字從咒語庫中刪除
  !temp      金嘆號後面帶關鍵字，可使用咒語庫關鍵字的咒語
  '''
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=spell))
        return 0
    else:
        img_url = ai_img(event.message.text, userid, timestamp)
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return 0

@handler.add(MessageEvent, message=ImageMessage)
def text_request(event):
    uploadid = r'upload/' + event.source.user_id
    if not os.path.exists(uploadid):
        os.makedirs(uploadid) 
    message_content = line_bot_api.get_message_content(event.message.id)  # 根據訊息 ID 取得訊息內容
    with open(f'./{uploadid}/{event.message.id}.PNG', 'wb') as fd:
        fd.write(message_content.content)             # 以二進位的方式寫入檔案

    img_url = img_to_img_openai(str(f'./{uploadid}/{event.message.id}.PNG'))
    line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)) 
    
    userid = r'users/' + event.source.user_id
    if not os.path.exists(userid):
        os.makedirs(userid) 
    sess = requests.Session()
    myHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    filename = f"./{userid}/{event.timestamp}.jpg"
    get_img = sess.get(img_url, headers = myHeader)  
    with open(filename,'wb') as output:  
        for chunk in get_img:
            output.write(chunk)

    
if __name__ == "__main__":
    app.run("0.0.0.0", port=80)
