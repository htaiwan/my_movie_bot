from movie_crawler import MovieCrawler
import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    event.message.text = event.message.text.lower()
    token = event.reply_token
    if event.message.text == '@本週新片':
        handle_this_week_movie_quick_reply_message(token)
    elif '@本週新片 電影名稱' in event.message.text:
        movie = event.message.text.replace('@本週新片 電影名稱-', '')
        handle_this_week_movie_message(token, movie)
    elif event.message.text == '@即將上映':
        handle_coming_soon_movie_quick_reply_message(token)
    elif '@即將上映 電影名稱' in event.message.text:
        movie = event.message.text.replace('@即將上映 電影名稱-', '')
        handle_coming_soon_message(token, movie)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=event.message.text)
        )


def handle_this_week_movie_quick_reply_message(token):
    df = MovieCrawler.get_this_week_movie()
    quick_reply_items = []
    for name in df['電影名稱']:
        button = QuickReplyButton(action=MessageAction(label=name, text="@本週新片 電影名稱-{}".format(name)))
        quick_reply_items.append(button)

    text_message = TextSendMessage(text='請選擇電影名稱',
                                   quick_reply=QuickReply(items=quick_reply_items)
                                   )
    line_bot_api.reply_message(token, text_message)


def handle_this_week_movie_message(token, movie):
    df = MovieCrawler.get_this_week_movie()
    brief = ""
    for index, row in df.iterrows():
        if row['電影名稱'] == movie:
            brief = row['電影名稱'] + row['上映時間'] + '\n\n' + row['電影簡介']

    line_bot_api.reply_message(token, TextMessage(text=brief))


def handle_coming_soon_movie_quick_reply_message(token):
    df = MovieCrawler.get_coming_soon_movie()
    quick_reply_items = []
    for name in df['電影名稱']:
        button = QuickReplyButton(action=MessageAction(label=name, text="@即將上映 電影名稱-{}".format(name)))
        quick_reply_items.append(button)

    text_message = TextSendMessage(text='請選擇電影名稱',
                                   quick_reply=QuickReply(items=quick_reply_items)
                                   )
    line_bot_api.reply_message(token, text_message)


def handle_coming_soon_message(token, movie):
    df = MovieCrawler.get_coming_soon_movie()
    brief = ""
    for index, row in df.iterrows():
        if row['電影名稱'] == movie:
            brief = row['電影名稱'] + row['上映時間'] + '\n\n' + row['電影簡介']

    line_bot_api.reply_message(token, TextMessage(text=brief))


if __name__ == "__main__":
    # for ngrok test
    # app.run(port=5002, debug=True)

    # for heroku
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
