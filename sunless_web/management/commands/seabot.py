import random

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db.models import Q

from modules.config import config
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import validate_email, validate_slug

from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters

from sunless_web.models import Conversation, TelegramUser

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


class SeaBot:

    def __init__(self):
        self.progress = {}
        self.conversations = []
        self.reload(None, None)

    # Signing
    def signing(self, bot, update):
        # print("msg from ", update.message.from_user.username, " ", update.message.text)

        chat_user = update.message.from_user
        if chat_user.id not in self.progress:
            self.progress[chat_user.id] = {
                "phase": self.hello,
                "username": chat_user.username,
                "telegram_id": chat_user.id,
                "firstname": chat_user.first_name,
                "lastname": chat_user.last_name
            }

        progress = self.progress[chat_user.id]
        phase = progress['phase']

        #
        answer, next_phase = phase(update.message, progress)
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

            new_user = get_user_model().objects.create_user(progress['username'], progress['email'], progress['password'])
            new_user.first_name = progress['firstname']
            new_user.last_name = progress['lastname']
            new_user.is_staff = True
            new_user.groups.add(Group.objects.get(name='Translator'))
            new_user.save()

            telegram_user = TelegramUser()
            telegram_user.user = new_user
            telegram_user.telegram_id = progress['telegram_id']
            telegram_user.save()

            print("User ", new_user.username, "has created")

            bot.send_message(chat_id=update.message.chat_id,
                             text="계정 생성이 완료 되었습니다! \r\nhttp://sunless.eggpang.net/work 에서 로그인해주세요!")
            progress['phase'] = self.hello
        else:
            progress['phase'] = next_phase

    def hello(self, _, progress):
        print(f"Finding user {progress['firstname']} / {progress['lastname']} "
              f"( {progress['username']}:{progress['telegram_id']} )")

        try:
            already = get_user_model().objects.select_related('telegram').get(Q(username=progress['username']) |
                                                   Q(telegram__telegram_id=progress['telegram_id']) |
                                                   (
                                                        Q(first_name=progress['firstname']) &
                                                        Q(last_name=progress['lastname'])
                                                   ))
            print("Found " + str(already))
        except Exception as e:
            pprint(e)
            print("User Not Found")
            already = None

        if already and not hasattr(already, 'telegram'):
            print("Update old user")
            already.first_name = progress['firstname']
            already.last_name = progress['lastname']
            already.save()

            telegram = TelegramUser()
            telegram.user = already
            telegram.telegram_id = progress['telegram_id']
            telegram.save()

        if already:
            print("Exsisting User")
            return f"""안녕하세요 {progress['username']}님! 다시 봬니 반갑습니다!
{progress['username']}님은 이미 계정을 갖고 계시니 제가 도와드릴건 없지만 
나중에 제가 더 많은 일을 할 수 있게 되면 도움이 되드리겠습니다! 
참고로 번역 사이트 주소는 http://sunless.eggpang.net/work 입니다!
""", self.hello
        else:
            print("New User")
            return "안녕하세요? Sunless Sea 번역 사이트 계정을 만드실 건가요?", self.hello_yn

    def hello_yn(self, message, progress):
        if compare_ex(message.text, AGREE):
            if progress['username']:
                return f"""알겠습니다. 계정은 텔레그램과 똑같이 {progress['username']}로 할께요!
네.. 어자피 선택권 따위 없어요... 
만약의 경우 연락드릴 이메일 주소를 입력해주세요.""", self.email
            else:
                return f"""알겠습니다. 번역 사이트에서 사용하실 로그인 아이디를 정해주세요!.""", self.username

        elif compare_ex(message.text, DISAGREE):
            return "아니 그럼 뭐 땀시 저한테 말을 거셨나요? 헐.... 다시 맘이 바뀌면 말걸어 주세요", self.hello
        else:
            return "그게 무슨 의미인가요?;;; 모르겠어요! 계정을 만드실 건가요?", self.hello_yn

    def username(self, message, progress):
        if not len(message.text):
            return "음?... 잘못누른거죠? 일부러 그런거 아니죠?....음?...음?...음?!!!"

        if len(message.text) <= 2:
            return f"헐.. {len(message.text)}글자는 너무 짧잖아요; 다시 확인하고 입력해주세요!", self.username

        try:
            validate_slug(message.text)
        except ValidationError:
            return "아니.. 아실만한 분이 왜그러시나요!! 영문,숫자,언더바 만 가능합니다! 다시 확인하고 입력해주세요!", self.username

        progress['username'] = message.text
        return "네! 아이디는 %s로 하는거고요...흠... \r\n그러면 이번엔 만약의 경우 연락드릴 이메일 주소를 입력해주세요." % message.text, self.email

    def email(self, message, progress):
        if not len(message.text):
            return "음?... 잘못누른거죠? 일부러 그런거 아니죠?....음?...음?...음?!!!"

        try:
            validate_email(message.text)
        except ValidationError as e:
            return "이메일 주소가 이상한데요;; 다시 확인하고 입력해주세요!", self.email

        progress['email'] = message.text
        return "알겠습니다! 이번엔 사이트 로그인에 사용하실 비밀 번호를 입력해주세요! \r\n" \
               "!! 주의 !! 텔레그램 비밀번호를 말하는게 아닙니다!!", self.password

    def password(self, message, progress):

        if len(message.text) < 4:
            return "그렇게 짧게는 할 수 없어요... 다른 비밀번호를 입력해주세요", self.password

        if len(message.text) == progress['username']:
            return "아이디랑 비밀번호를 똑같이 하는 사람이 어딨나요!! 다른걸로 다시 입력해주세요", self.password

        progress['password'] = message.text

        return "알겠습니다! 확인을 위해서 다시 입력해주세요... \r\n사실 채팅창에 뻔히 보이지만 제가 책임을 회피해야 하니까요 ㅎㅎ", self.confirm

    def confirm(self, message, progress):

        if message.text != progress['password']:
            return "어;;.... 아까 입력한거랑 다른데요;;; 처음부터 다시! 원하는 비밀번호를 입력해주세요", self.password

        return f"오키! {progress['username']} 계정 생성을 시작합니다!", None

    #
    # chatting
    #
    def reload(self, bot, update):
        print("Reloading....")
        if update:
            bot.send_message(chat_id=update.message.chat_id, text="대화 목록 업데이트 중...")
        self.conversations = list(Conversation.objects.prefetch_related("answers").all())
        if update:
            bot.send_message(chat_id=update.message.chat_id, text="업데이트 완료! 총 %d개 로딩" % len(self.conversations))

    def chat(self, bot, update):
        print(f"Checking group chat {update.message.from_user.fullname}:"
              f" '{update.message.text[:10]}...' from {update.message.from_user.id}")
        for convers in self.conversations:
            res = convers.findall(update.message.text)
            if res and random.random() <= convers.chance:
                answer = random.choice(convers.answers.all())
                print("Answer for ", update.message.text, "as", answer, "in", update.message.chat_id)
                bot.send_message(chat_id=update.message.chat_id, text=answer.answer)

    #
    # commands
    #
    def leave_chat(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="네... 아흑...")
        bot.leave_chat(update.message.chat_id)

    def say(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text[4:])


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__(self)

    def handle(self, *args, **options):
        seabot = SeaBot()

        updater = Updater(token=config['botToken'])
        dispatcher = updater.dispatcher

        process_handler = MessageHandler(Filters.text & Filters.private, seabot.signing)
        dispatcher.add_handler(process_handler)

        helper_handler = MessageHandler(Filters.text & Filters.group, seabot.chat)
        dispatcher.add_handler(helper_handler)

        leave_handler = CommandHandler('나가이씨봇아', seabot.leave_chat)
        dispatcher.add_handler(leave_handler)

        say_handler = CommandHandler('따라해', seabot.say)
        dispatcher.add_handler(say_handler)

        say_handler = CommandHandler('reload', seabot.reload)
        dispatcher.add_handler(say_handler)

        print("Bot is Ready!")
        updater.start_polling()
