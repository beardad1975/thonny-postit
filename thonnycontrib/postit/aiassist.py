import threading
import time
import pytgpt.auto  as auto

from . import common



class AiassistThread(threading.Thread):
    def __init__(self, service_name):
        threading.Thread.__init__(self)
        self.aiassist_tab = common.aiassist_tab
        self.service_name = service_name

    def run(self):
        print("ai assist thread starting .......")
        if self.service_name == 'AUTO':
            bot = auto.AUTO()
        
        ### first chat
        # self.aiassist_tab.is_chatting = False
        # result = bot.chat('以下請用繁體中文回答。你好嗎？')
        # print(result)
        self.aiassist_tab.is_chatting = True
        self.aiassist_tab.provider_name = self.service_name
        # if self.service_name == 'AUTO':
        #     self.aiassist_tab.provider_name = f'{bot.provider_name}'

        # chat cycle
        while self.aiassist_tab.closing_queue.empty():
            time.sleep(0.5)
        
        self.aiassist_tab.is_chatting = False
        self.aiassist_tab.first_chat = False
        self.aiassist_tab.closing_queue.get()
        #del bot
        print('[ai assist thread] closing thread ....')







    