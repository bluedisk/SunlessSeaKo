from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from modules.config import config
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import validate_email

from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters

import logging
import re
from pprint import pprint

AGREE = (
    '응.*',
    'ㅇㅇ.*',
    'ㅇㅋ.*',
    '그래.*',
    '좋아.*',
    '알았어.*',
    'y.*',
    'ok.*',
    'go.*',
    'agree.*',
    'positive.*'
)

DISAGREE = (
    '아니.*',
    '싫어.*',
    '노.*',
    'ㄴㄴ.*',
    'no.*',
    'not.*',
    'don\'?t.*',
    'negative.*',
    'disagree.*'
)


def compare_ex(text, exlist):
    value = re.sub('[^\w]', '', text)
    for express in exlist:
        if re.match(express, value, re.IGNORECASE):
            return True

    return False


class SignupBot:

    def __init__(self):
        self.progress = {}

    def process(self, bot, update):
        # print("msg from ", update.message.from_user.username, " ", update.message.text)

        user = update.message.from_user.username
        if user not in self.progress:
            self.progress[user] = {
                "phase": self.hello,
                "username": user
            }

        progress = self.progress[user]
        phase = progress['phase']

        #
        answer, next_phase = phase(update.message.text, progress)
        if next_phase == self.hello_yn:
            bot.send_message(chat_id=update.message.chat_id, text=answer,
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[
                                     [KeyboardButton(text="응"), KeyboardButton(text="아니")]
                                 ]
                             ))
        else:
            bot.send_message(chat_id=update.message.chat_id, text=answer, reply_markup=ReplyKeyboardRemove())

        if not next_phase:
            #pprint(progress)

            user = get_user_model().objects.create_user(progress['username'], progress['email'], progress['password'])
            user.is_staff = True
            user.groups.add(Group.objects.get(name='Translator'))
            user.save()

            bot.send_message(chat_id=update.message.chat_id,
                             text="계정 생성이 완료 되었습니다! \r\nhttp://sunless.eggpang.net/admin 에서 로그인해주세요!")
            progress['phase'] = self.hello
        else:
            progress['phase'] = next_phase

    def hello(self, _, progress):
        already = get_user_model().objects.filter(username=progress['username']).exists()
        if already:
            return f"""안녕하세요 {progress['username']}님! 다시 봬니 반갑습니다!
{progress['username']}님은 이미 계정을 갖고 계시니 제가 도와드릴건 없지만 
나중에 제가 더 많은 일을 할 수 있게 되면 도움이 되드리겠습니다! 
참고로 번역 사이트 주소는 http://sunless.eggpang.net/admin 입니다!
""", self.hello
        else:
            return "안녕하세요? Sunless Sea 번역 사이트 계정을 만드실 건가요?", self.hello_yn

    def hello_yn(self, text, progress):
        if compare_ex(text, AGREE):
            return f"""알겠습니다. 계정은 텔레그램과 똑같이 {progress['username']}로 할께요!
네.. 어자피 선택권 따위 없어요... 
만약의 경우 연락드릴 이메일 주소를 입력해주세요.""", self.email

        elif compare_ex(text, DISAGREE):
            return "아니 그럼 뭐 땀시 저한테 말을 거셨나요? 헐.... 다시 맘이 바뀌면 말걸어 주세요", self.hello
        else:
            return "그게 무슨 의미인가요?;;; 모르겠어요! 계정을 만드실 건가요?", self.hello_yn

    def email(self, text, progress):
        try:
            validate_email(text)
        except ValidationError as e:
            return "이메일 주소가 이상한데요;; 다시 확인하고 입력해주세요!", self.email

        progress['email'] = text
        return "알겠습니다! 이번엔 사이트 로그인에 사용하실 비밀 번호를 입력해주세요! \r\n" \
               "!! 주의 !! 텔레그램 비밀번호를 말하는게 아닙니다!!", self.password

    def password(self, text, progress):
        if len(text) < 4:
            return "그렇게 짧게는 할 수 없어요... 다른 비밀번호를 입력해주세요", self.password

        if len(text) == progress['username']:
            return "아이디랑 비밀번호를 똑같이 하는 사람이 어딨나요!! 다른걸로 다시 입력해주세요", self.password

        progress['password'] = text
        return "알겠습니다! 확인을 위해서 다시 입력해주세요... \r\n사실 채팅창에 뻔히 보이지만 제가 책임을 회피해야 하니까요 ㅎㅎ", self.confirm

    def confirm(self, text, progress):
        if text != progress['password']:
            return "어;;.... 아까 입력한거랑 다른데요;;; 처음부터 다시! 원하는 비밀번호를 입력해주세요", self.password

        return f"오키! {progress['username']} 계정 생성을 시작합니다!", None


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__(self)
        self.updater = None
        self.dispatcher = None
        self.signup_bot = SignupBot()

    def handle(self, *args, **options):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        self.updater = Updater(token=config['botToken'])
        self.dispatcher = self.updater.dispatcher

        process_handler = MessageHandler(Filters.text & Filters.private, self.signup_bot.process)
        self.dispatcher.add_handler(process_handler)

        print("Bot is Ready!")
        self.updater.start_polling()
