import threading
import time
import tkinter as tk
import tkinter.font as font
from tkinter import ttk

import pytgpt.auto as auto
import pytgpt.phind as phind
import pytgpt.perplexity as perplexity
import pytgpt.blackboxai as blackboxai
import pytgpt.koboldai as koboldai
import pytgpt.llama2 as llama2
from pytgpt.auto.errors import AllProvidersFailure
from pytgpt.exceptions import FailedToGenerateResponseError
from requests.exceptions import ConnectionError


from . import common
from .common import AnswerNTuple


class AiassistThread(threading.Thread):
    def __init__(self, service_name):
        threading.Thread.__init__(self)
        self.aiassist_tab = common.aiassist_tab
        self.service_name = service_name

    def run(self):
        print("ai assist thread starting .......")
        print("choosed service name : ", self.service_name)
        common.aiassist_tab.provider_name = ''
        # common.aiassist_tab.chat_round_num = 0
        common.aiassist_tab.status_label.config(text="")

        if self.service_name == 'AUTO':
            bot = auto.AUTO(intro=common.aiassist_intro)
            self.aiassist_tab.provider_name = 'AUTO'
        elif self.service_name == 'Phind':
            bot = phind.PHIND()
            self.aiassist_tab.provider_name = 'Phind'
        elif self.service_name == 'Perplexity':
            bot = perplexity.PERPLEXITY()
            self.aiassist_tab.provider_name = 'Perplexity'
        elif self.service_name == 'Blackboxai':
            bot = blackboxai.BLACKBOXAI()
            self.aiassist_tab.provider_name = 'Blackboxai'
        elif self.service_name == 'Koboldai':
            bot = koboldai.KOBOLDAI()
            self.aiassist_tab.provider_name = 'Koboldai'
        elif self.service_name == 'Llama2':
            bot = llama2.LLAMA2()
            self.aiassist_tab.provider_name = 'Llama2'
        else:
            print('Fallback to AUTO ai assist...')
            self.service_name = 'AUTO'
            self.aiassist_tab.provider_name = 'AUTO'
            bot = auto.AUTO(intro=common.aiassist_intro)

        # mark service label (excep AUTO)
        if self.aiassist_tab.provider_name:
            self.aiassist_tab.status_label.config(
                            text=f"使用 {self.aiassist_tab.provider_name} 服務")

            
        self.aiassist_tab.is_chatting = True
        
        ### first chat
        # self.aiassist_tab.is_chatting = False
        # result = bot.chat('以下請用繁體中文回答。你好嗎？')
        # print(result)
        
        
        # if self.service_name == 'AUTO':
        #     self.aiassist_tab.provider_name = f'{bot.provider_name}'

        # chat loops
        while self.aiassist_tab.closing_queue.empty():
            if self.aiassist_tab.asking_queue.qsize() > 0 :
                print('got question ...')
                question = self.aiassist_tab.asking_queue.get()

                try:
                    answer = bot.chat(question)
                    ans_ntuple = AnswerNTuple(success=True, answer=answer)
                except (AllProvidersFailure, FailedToGenerateResponseError, ConnectionError) as e:
                    print('Got exception when chat :', e)
                    ans_ntuple = AnswerNTuple(success=False, answer=None)

                
                self.aiassist_tab.answer_queue.put(ans_ntuple)
                # self.aiassist_tab.chat_round_num += 1

                # if self.service_name == 'AUTO' and \
                #     self.aiassist_tab.chat_round_num == 1:
                #         self.aiassist_tab.provider_name = f'AUTO ({bot.provider_name})'
                #         self.aiassist_tab.status_label.config(
                #             text=f"使用 {self.aiassist_tab.provider_name} 服務")
                if self.service_name == 'AUTO' :
                    if bot.provider_name != self.aiassist_tab.provider_name:
                        self.aiassist_tab.provider_name = f'AUTO ({bot.provider_name})'
                        self.aiassist_tab.status_label.config(
                            text=f"使用 {self.aiassist_tab.provider_name} 服務")
                    

            time.sleep(0.1)
        
        self.aiassist_tab.is_chatting = False
        self.aiassist_tab.first_chat = False
        self.aiassist_tab.closing_queue.get()
        #del bot
        print('[ai assist thread] closing thread ....')



class ChatTextPostit(ttk.Frame):
    def __init__(self, parent, message, told_by_ai):
        self.parent = parent
        ttk.Frame.__init__(self, self.parent)

        self.original_message = message
        self.told_by_ai = told_by_ai

        if not told_by_ai :
            position = 'e'
            name = '我'
        else:
            position = 'w'
            name = 'AI'

        self.avatar_frame = ttk.Frame(self)
        self.avatar_frame.pack(fill='x', expand=1)
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='x', expand=1)

        self.avatar_label = ttk.Label(self.avatar_frame, 
                                      font=common.postit_para_font,
                                      text=name, 
                                      borderwidth=2, 
                                      relief="groove")       
        self.avatar_label.pack(anchor=position)

        #self.dialog_text = tk.Text(self.main_frame, height=7)
        #self.dialog_text.pack()

        self.label = tk.Label(self.main_frame,
                              font=common.postit_para_font,
                              text=message, 
                              justify='left',
                              borderwidth=2, 
                              relief="groove")
        self.label.pack( anchor=position)

    def get_message(self):
        return self.original_message

    def set_message(self, new_message):
        self.label['text'] = new_message
        


class ChatCodePostit(ttk.Frame):
    def __init__(self, parent, code):        
        pass

try_counter = 0

class TryAiassistPostit(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        ttk.Frame.__init__(self, self.parent)

        global try_counter
        try_counter += 1

        if try_counter % 2 :
            position = 'e'
            name = '我'
        else:
            position = 'w'
            name = 'AI'

        self.avatar_frame = ttk.Frame(self)
        self.avatar_frame.pack(fill='x', expand=1)
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='x', expand=1)

        self.avatar_label = ttk.Label(self.avatar_frame, text=name, borderwidth=2, relief="groove")
        
        
        
        self.avatar_label.pack(anchor=position)

        #self.dialog_text = tk.Text(self.main_frame, height=7)
        #self.dialog_text.pack()

        
        try_str = str(try_counter) * 15 + '\n'
        try_str = try_str * 4
        self.label = tk.Label(self.main_frame, text=try_str, borderwidth=2, relief="groove")
        self.label.pack( anchor=position)
        
        
        #self.dialog_text.insert('0.0', str(try_counter))
        







    