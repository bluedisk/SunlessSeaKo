import telegram

class TelegramLog:
    
    def __init__(self, token, group_id):
        self.bot = telegram.Bot(token = token) 
        self.group = group_id
        
    def log(self, text):
        self.bot.sendMessage(self.group, text)
        
class PrintLog:
    
    def __init__(self):
        pass
        
    def log(self, text):
        print(text)