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
import cjkwrap

from thonny import get_workbench

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



class AiassistChatPostit(ttk.Frame):
    def __init__(self, parent, message:str, wrap_length, widget_type):
        self.parent = parent
        ttk.Frame.__init__(self, self.parent)

        self.original_message = message

        # get message's biggest length
        self.conext_biggest_line_length = 0
        for li in message.split('\n'):
            line_length = len(li)
            if self.conext_biggest_line_length < line_length:
                self.conext_biggest_line_length = line_length
        print('----get message s biggest length--------', self.conext_biggest_line_length)
        

        self.widget_type = widget_type

        

        self.avatar_frame = tk.Frame(self, bg=common.aiassist_tab.BG_COLOR)
        self.avatar_frame.pack(fill='x', expand=1)
        self.main_frame = tk.Frame(self, bg=common.aiassist_tab.BG_COLOR)
        self.main_frame.pack(fill='x', expand=1)

        if widget_type == common.aiassist_tab.WIDGET_TYPE_ME_TEXT :
            position = 'e'
            # name = '我'
            # self.avatar_label = tk.Label(self.avatar_frame, 
            #                           font=common.postit_para_font,
            #                           text=name, 
            #                           bg=common.aiassist_tab.BG_COLOR,
            #                           fg=common.aiassist_tab.LIGHT_FG_COLOR,
            #                           borderwidth=2, 
            #                           #relief="groove",
            #                           ) 
            avatar_me_image = common.common_images['avatar_me']   
            self.avatar_button = tk.Button(self.avatar_frame,  
                                        relief='groove',
                                        borderwidth=0,
                                        compound='right',
                                        image=avatar_me_image,
                                        bg=common.aiassist_tab.BG_COLOR,
                                        padx=0,
                                        pady=0, 
                                        )
            self.avatar_button.pack(anchor=position, padx=5, pady=5)

            # self.label = tk.Label(self.main_frame,
            #                   font=common.postit_para_font,
            #                   text='', 
            #                   justify='left',
            #                   bg=common.aiassist_tab.ME_BG_COLOR,
            #                   fg=common.aiassist_tab.DARK_FG_COLOR,
            #                   highlightthickness=common.aiassist_tab.BORDER_THICKNESS,
            #                   highlightbackground = common.aiassist_tab.ME_BORDER_COLOR,
            #                   highlightcolor= common.aiassist_tab.ME_BORDER_COLOR,
            #                   relief="flat")
            # self.label.pack( anchor=position, ipadx=5, ipady=5)     
            self.chat_text = tk.Text(self.main_frame, 
                                     font=common.postit_para_font,
                                     bg=common.aiassist_tab.ME_BG_COLOR, 
                                     fg=common.aiassist_tab.DARK_FG_COLOR,
                                     wrap='word',
                                     #width=wrap_length,
                                     highlightthickness=common.aiassist_tab.BORDER_THICKNESS,
                                     highlightbackground=common.aiassist_tab.ME_BORDER_COLOR,
                                     highlightcolor=common.aiassist_tab.ME_BORDER_COLOR,
                                     relief="flat",          
                                     padx=10,
                                     pady=10)
            self.chat_text.pack( anchor=position, ipadx=5, ipady=5)

        elif widget_type == common.aiassist_tab.WIDGET_TYPE_AI_TEXT:
            position = 'w'
            name = 'AI'
            avatar_ai_image = common.common_images['avatar_ai']   
            self.avatar_button = tk.Button(self.avatar_frame,  
                                        relief='groove',
                                        borderwidth=0,
                                        compound='right',
                                        image=avatar_ai_image,
                                        bg=common.aiassist_tab.BG_COLOR,
                                        padx=0,
                                        pady=0, 
                                        )
            self.avatar_button.pack(anchor=position, padx=5, pady=5)

            # self.label = tk.Label(self.main_frame,
            #                   font=common.postit_para_font,
            #                   text='', 
            #                   justify='left',
            #                   bg=common.aiassist_tab.AI_TEXT_BG_COLOR,
            #                   fg=common.aiassist_tab.LIGHT_FG_COLOR,
            #                   highlightthickness=common.aiassist_tab.BORDER_THICKNESS,
            #                   highlightbackground = common.aiassist_tab.AI_TEXT_BORDER_COLOR,
            #                   highlightcolor= common.aiassist_tab.AI_TEXT_BORDER_COLOR,
            #                   relief="flat")
            # self.label.pack( anchor=position, ipadx=5, ipady=5)

            self.chat_text = tk.Text(self.main_frame, 
                                     font=common.postit_para_font,
                                     bg=common.aiassist_tab.AI_TEXT_BG_COLOR, 
                                     fg=common.aiassist_tab.LIGHT_FG_COLOR,
                                     wrap='word',
                                     #width=wrap_length,
                                     highlightthickness=common.aiassist_tab.BORDER_THICKNESS,
                                     highlightbackground = common.aiassist_tab.AI_TEXT_BORDER_COLOR,
                                     highlightcolor= common.aiassist_tab.AI_TEXT_BORDER_COLOR,  
                                     relief="flat",         
                                     padx=10,
                                     pady=10)
            self.chat_text.pack( anchor=position, ipadx=5, ipady=5)
                  
        elif widget_type == common.aiassist_tab.WIDGET_TYPE_ABNORMAL:
            # no avatar
            position = 'w'
            # self.label = tk.Label(self.main_frame,
            #                   font=common.postit_para_font,
            #                   text='', 
            #                   justify='left',
            #                   bg=common.aiassist_tab.ABNORMAL_BG_COLOR,
            #                   fg=common.aiassist_tab.LIGHT_FG_COLOR,
            #                   highlightthickness=common.aiassist_tab.BORDER_THICKNESS,
            #                   highlightbackground = common.aiassist_tab.ABNORMAL_BORDER_COLOR,
            #                   highlightcolor= common.aiassist_tab.ABNORMAL_BORDER_COLOR,
            #                   relief="flat")
            # self.label.pack( anchor=position, ipadx=5, ipady=5)

            self.chat_text = tk.Text(self.main_frame, 
                                     font=common.postit_para_font,
                                     bg=common.aiassist_tab.ABNORMAL_BG_COLOR, 
                                     fg=common.aiassist_tab.LIGHT_FG_COLOR,
                                     wrap='word',
                                     #width=wrap_length,
                                     highlightthickness=common.aiassist_tab.BORDER_THICKNESS,
                                     highlightbackground = common.aiassist_tab.ABNORMAL_BORDER_COLOR,
                                     highlightcolor= common.aiassist_tab.ABNORMAL_BORDER_COLOR,  
                                     relief="flat",         
                                     padx=10,
                                     pady=10)
            self.chat_text.pack( anchor=position, ipadx=5, ipady=5)


        else:
            print('wrong widget type')
            raise Exception
        

        self.set_wordwrap(wrap_length)

        self.chat_text.bind('<Button-3>', lambda event : ChatTextRightClicker(self.chat_text, event))

    def get_message(self):
        return self.original_message

    def set_message(self, new_message):
        self.label['text'] = new_message

    def set_wordwrap(self, wrap_length):
        """
        Preventing too long in one line. Length calculating consider CJK text(double character). 
        """
        
        result_lines = []
        context_max_line_length = 0

        text = self.original_message
        lines = text.split('\n')
        for line in lines:
            line_length = cjkwrap.cjklen(line)
            if line_length <= wrap_length:
                result_lines.append(line)
                # record max line length 
                if context_max_line_length < line_length:
                    context_max_line_length = line_length
            else:
                result_lines += cjkwrap.wrap(line, wrap_length)
                context_max_line_length = wrap_length

        
        line_count = len(result_lines)
        value = '\n'.join(result_lines)
        self.chat_text.config(height=line_count)
        self.chat_text.config(width=context_max_line_length)
        print('context max line length ----', context_max_line_length, '   ', ' -- wrap length ', wrap_length )
        

        # change text widget cotent , remain read only.
        self.chat_text.config(state=tk.NORMAL)            
        self.chat_text.delete(1.0, "end")
        self.chat_text.insert("end", value)
        self.chat_text.config(state=tk.DISABLED)
        
        common.aiassist_tab.tab_frame.update_idletasks()

class ChatTextRightClicker:
    def __init__(self, chat_text, event):
        self.chat_text = chat_text
        right_click_menu = tk.Menu(None, tearoff=0, takefocus=0)
        
        self.selection_tuple = self.chat_text.tag_ranges("sel")
        if len(self.selection_tuple) == 2: # got selection area
            right_click_menu.add_command(label='複製所選文字', command=self.copy_selection)
        else: # no selection
            right_click_menu.add_command(label='複製全部', command=self.copy_all)

        right_click_menu.tk_popup(event.x_root, event.y_root)


    def copy_selection(self):
        sel_start, sel_end = self.selection_tuple
        if sel_start and sel_end:
            selected_text = self.chat_text.get(sel_start, sel_end)
            get_workbench().clipboard_clear()
            get_workbench().clipboard_append(selected_text)
        else:
            print('no selection on chat text')
            
    def copy_all(self):
        text = self.chat_text.get("1.0", "end-1c")
        get_workbench().clipboard_clear()
        get_workbench().clipboard_append(text)
        #print(text)        


class WaitAnswerPostit(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        ttk.Frame.__init__(self, self.parent)

        self.counter = 0

        self.main_frame = tk.Frame(self, bg=common.aiassist_tab.BG_COLOR)
        self.main_frame.pack(fill='x', expand=1)

        #self.wait_answer_img0 = common.common_images['wait_answer0']   
        

        self.wait_answer_btn = tk.Button(self.main_frame,  
                                        #relief='groove',
                                        borderwidth=0,
                                        compound='right',
                                        image=common.common_images['wait_answer0'],
                                        bg=common.aiassist_tab.BG_COLOR,
                                        padx=0,
                                        pady=0)
        self.wait_answer_btn.pack(anchor='w', padx=5, pady=5)

    def next(self):
        self.counter += 1
        img_num = self.counter % 4
        img_name_str = f'wait_answer{img_num}'
        #print('change wait image to --------', img_name_str)
        self.wait_answer_btn['image'] = common.common_images[img_name_str]

        
                    


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
        







    