import threading
import time
import tkinter as tk
import tkinter.font as font
from tkinter import ttk

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

        # chat loops
        while self.aiassist_tab.closing_queue.empty():
            if self.aiassist_tab.asking_queue.qsize() > 0 :
                print('got question ...')
                question = self.aiassist_tab.asking_queue.get()
                answer = bot.chat(question)
                self.aiassist_tab.answer_queue.put(answer)
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
        







    