import os 
import datetime
import webbrowser
import shutil
import json
import queue
from collections import OrderedDict, namedtuple

import tkinter as tk
import tkinter.font as font
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

from thonny import get_workbench, get_shell, get_runner 
from thonny.ui_utils import show_dialog, CommonDialog, create_tooltip, QueryDialog
from thonny.codeview import CodeView, CodeViewText
from thonny.shell import ShellText


from thonny.common import ToplevelCommand, InlineCommand

from .base_postit import BasePostit
from .enclosed_postit import EnclosedPostit
from .dropdown_postit import DropdownPostit
from .block_enclosed_postit import BlockEnclosedPostit
from .asset_copy import AssetCopyBtn, AssetGroup
from .aiassist import (AiassistThread, AiassistChatText, WaitingAnswerImage, 
                        ChatCodePostit)
from .common import ( CodeNTuple, common_images, TAB_DATA_PATH, AnswerNTuple
                     )
from . import common


from .tools.enter_tool_postit import EnterToolPostit
from .tools.backspace_tool_postit import BackspaceToolPostit
from .tools.undo_tool_postit import UndoToolPostit, RedoToolPostit
from .tools.indent_tool_postit import IndentToolPostit, DedentToolPostit
from .tools.comment_tool_postit import CommentToolPostit
from .tools.pilcrow_tool_postit import PilcrowToolPostit
from .tools.variables_tool_postit import ( VariableMenuPostit,
        VariableAddToolPostit, VariableFetchToolPostit)
from .tools.copy_tool_postit import ( CopyToolPostit, PasteToolPostit,
        CutToolPostit )     
from .tools.symbol_tool_postit import SymbolToolPostit
#from .tools.keyin_display_tool_postit import KeyinDisplayToolPostit




#for test
#from tkinter.messagebox import showinfo

#  tab data level
#  Mode(contain notebook) ----> TabGoup ----> Tab 
#       

class Mode:
    def __init__(self, mode_name, mode_label, has_more_tab):
        self.mode_name = mode_name
        self.mode_label = mode_label
        self.groups = OrderedDict()
        self.has_more_tab = has_more_tab



        #collect  tab group
        #print(TAB_DATA_PATH)
        #print(mode_name)
        with open(TAB_DATA_PATH / mode_name / 'groups_info.json', encoding='utf8') as fp:
            groups_info = json.load(fp)
        #print(info_data)

        for g in groups_info:
            group_name = g['group_name']
            group_label = g['group_label']
            default_tabs = g['default_tabs']
            group_path =  TAB_DATA_PATH / mode_name / g['group_name']
            self.groups[group_name] = TabGroup(group_name, self, 
                    group_label, group_path, default_tabs)

    def gui_init(self):
        # make notebook
        self.notebook_frame = ttk.Frame(common.postit_view)
        #self.notebook_frame.pack(side=tk.TOP, fill=tk.BOTH)
        ###self.notebook_frame.rowconfigure(3, weight=1)
        ###common.postit_view.rowconfigure(3, weight=1)
        ###common.postit_view.columnconfigure(0, weight=0)
        
        ###self.notebook_frame.grid(row=3, column=0, sticky='w')
        self.notebook_frame.pack(side=tk.TOP, fill=tk.Y, expand=tk.Y)
        #style = ttk.Style(self.interior)
        #style = ttk.Style(notebook_frame.interior)
        
        style = ttk.Style(self.notebook_frame)
        style.configure('lefttab.TNotebook', tabposition='wn')
        #style.configure('TNotebook.Tab', font=('Consolas','12') )

        #style.configure('lefttab.TNotebook', font=('Consolas', 16))
        #self.notebook = ttk.Notebook(self.interior, style='lefttab.TNotebook')
        #self.notebook = ttk.Notebook(notebook_frame.interior, style='lefttab.TNotebook')
        self.tab_notebook = ttk.Notebook(self.notebook_frame, style='lefttab.TNotebook')
        self.tab_notebook.pack(side='top',fill=tk.Y, expand=tk.Y)

        #notebook event (keep cursor intact in editor)
        self.tab_notebook.bind('<<NotebookTabChanged>>',common.postit_view.on_tab_changed)
        self.tab_notebook.bind('<Button-1>',common.postit_view.on_tab_click)

    def add_more_tab(self):
        if self.has_more_tab:
            self.more_tab = MoreTab(self.tab_notebook)

            # make tab popup menu
            self.tab_popup_init()
        else:
            self.more_tab = None

    def tab_popup_init(self):
        self.tab_popup_menu = tk.Menu(self.tab_notebook, tearoff=0)

        self.tab_popup_menu.add_command(label="便利貼設定",
            command=self.select_more_tab)

        self.tab_notebook.bind("<Button-3>", self.popup)

    def popup(self, event):
        #if self.tool_name != 'variable_get':
        self.tab_popup_menu.tk_popup(event.x_root, event.y_root)

    def select_more_tab(self):
        self.tab_notebook.select(self.more_tab.tab_frame)

class TabGroup:
    def __init__(self, group_name, mode, group_label, group_path, default_tabs):
        self.group_name = group_name
        self.mode = mode
        self.group_label = group_label
        self.default_tabs = default_tabs
        self.group_path = group_path

        # 3 lists are the same size, all use circular_index
        self.fill_colors = []
        self.font_colors = []
        self.icon_images = []
        self.circular_index = 0

        # all tab data in order
        self.tabs = OrderedDict()

        # init action
        self.collect_icon_color()
        self.color_num = len(self.fill_colors)

        # collect tabs info
        with open(self.group_path / 'tabs_info.json', encoding='utf8') as fp:
            tabs_info = json.load(fp)
        #print(tabs_info)

        for t in tabs_info:
            tab_name = t['tab_name']
            tab_label = t['tab_label']
            tab_title = t['tab_title']
            #always_show = t['always_visible']
            tab_path = self.group_path / (tab_name+'.json')
            if tab_name == 'aiassist' :
                self.tabs[tab_name] = AiassistTab(tab_name, self, tab_label, tab_title,  tab_path)
            else:
                self.tabs[tab_name] = Tab(tab_name, self, tab_label, tab_title,  tab_path)

    def gui_init(self):
        # dummy
        pass    

    def collect_icon_color(self):
        icon_path = self.group_path / 'icons'
        with open(icon_path / 'icons_info.json', encoding='utf8') as fp:
            icons_info = json.load(fp)
        #print(icons_info)

        for i in icons_info:
            icon_filename = i['icon_filename']
            fill_color = i['fill_color']
            font_color = i['font_color']

            im = Image.open(icon_path / icon_filename)       
            self.icon_images.append(ImageTk.PhotoImage(im)) 
            self.fill_colors.append(fill_color)
            self.font_colors.append(font_color)       

    def next_icon_color(self):
        icon_image =  self.icon_images[self.circular_index]
        fill_color = self.fill_colors[self.circular_index]
        font_color = self.font_colors[self.circular_index]

        self.circular_index += 1
        if self.circular_index >= self.color_num:
            self.circular_index = 0
        return icon_image, fill_color, font_color


class Tab:
    def __init__(self, tab_name, group, tab_label,tab_title, tab_path):
        self.tab_name = tab_name
        #self.group_name = group_name
        #self.mode_name = mode_name
        self.tab_label = tab_label
        self.tab_title = tab_title
        #self.always_show = always_show
        self.tab_path = tab_path
        self.loaded = False
        self.group = group

        self.postit_paras_list = []
        self.current_postit_para = None
        
        self.visible = False
        self.para_start_on_done = False
        self.button_tkvar = tk.BooleanVar()
        self.button_tkvar.trace('w', self.on_button_change)
        #print('mode name:', mode_name, 'group name:', group_name)


    def do_para_start_on(self):
        if self.para_start_on_done:
            return

        for para in self.postit_paras_list:
            if not para.start_on:
                para.on_button_pressed()

        self.para_start_on_done = True
        #print(self.tab_name, ': do para start on')        

    def on_button_change(self, *args):
        value = self.button_tkvar.get()
        if value != self.visible :
            # make sure button value is toggled
            #print(self.tab_name, value, args)
            
            if value:
                common.postit_view.show_tab(self)
            else:
                common.postit_view.hide_tab(self)
            
                


    def gui_init(self):
        mode = self.group.mode
        group = self.group

        self.icon_image, self.fill_color, self.font_color =  group.next_icon_color()
        self.loaded = False
        self.visible = False

        # insert empty frame and hide
        
        self.tab_frame = CustomVerticallyScrollableFrame(mode.notebook_frame)
        # add tab ref
        self.tab_frame.tab = self
        mode.tab_notebook.insert('end',self.tab_frame,
                          text = self.tab_label,
                          image = self.icon_image,
                          compound="top",
                          padding=0,
                        )
        mode.tab_notebook.hide(self.tab_frame)



    def popup_init(self, example_vars):
        self.example_vars = example_vars
        self.popup_menu = tk.Menu(self.frame, tearoff=0)

        self.popup_menu.add_command(label="範例變數匯入",
            command=self.import_example_vars)

        self.frame.bind("<Button-3>", self.popup)


    def import_example_vars(self):
        s = '【匯入變數名稱】\n'
        for i in self.example_vars:
            s = s + i + '\n'
        s += '\n'

        ans = messagebox.askokcancel('範例變數匯入',s, master=get_workbench())
        #print(ans)
        if ans: # import vars into vars_menu
            vars_counter = common.share_vars_postit.vars_counter

            for var in self.example_vars:
                if var not in vars_counter:
                    vars_counter[var] = 1
            common.share_vars_postit.update_vars_menu()            
        else: # no
            return

    def popup(self, event):
        #if self.tool_name != 'variable_get':
        self.popup_menu.tk_popup(event.x_root, event.y_root)

    # @classmethod
    # def pick_color(cls):
    #     c = cls.color_data[cls.color_circular_index]
    #     cls.color_circular_index += 1
    #     if cls.color_circular_index >= cls.color_num:
    #         cls.color_circular_index = 0
    #     return c



class AiassistTab:
    def __init__(self, tab_name, group, tab_label,tab_title, tab_path):
        self.tab_name = tab_name
        #self.group_name = group_name
        #self.mode_name = mode_name
        self.tab_label = tab_label
        self.tab_title = tab_title
        #self.always_show = always_show
        self.tab_path = tab_path
        self.loaded = False
        self.group = group

        self.postit_paras_list = []
        self.current_postit_para = None
        
        self.visible = False
        self.para_start_on_done = False
        self.button_tkvar = tk.BooleanVar()
        self.button_tkvar.trace('w', self.on_button_change)
        #print('mode name:', mode_name, 'group name:', group_name)

        # record ai_tab in common
        common.aiassist_tab = self

        # for threads 
        self.asking_queue = queue.Queue()
        self.answer_queue = queue.Queue()
        self.closing_queue = queue.Queue()

        

        self.is_chatting = False
        self.service_name = ''
        self.provider_name = ''
        # self.chat_round_num = 0

        self.LINEWRAP_OPTION = 'aiassist.linewrap_length'
        
        length = get_workbench().get_option(self.LINEWRAP_OPTION)
        if length is None :
            get_workbench().set_default(self.LINEWRAP_OPTION,24)
            get_workbench().set_option(self.LINEWRAP_OPTION,24)
            #print('set default and set option to 24 ------')
        else:
            pass
            #print('current wrap length is ----------', length)
        
 

        
        #self.linewrap_length = 24
        
        self.LINEWRAP_MIN = 20
        self.LINEWRAP_MAX = 80
        self.size_changed = False
        self.is_successive_ans = False

    
        # add menu command in shell view
        shell = get_shell()
        # shell.menu.add_separator()
        # shell.menu.add_command(label='提問AI程式助理', 
        #                        command=_cmd_in_shell_ask_aiassist,
        #                        tester=_cmd_ask_aiassist_tester,
        #                        ) 
        shell.menu.insert_command(index=0, label='向AI助理提問', 
                               command=_cmd_in_shell_ask_aiassist,
                               
                               ) 
        shell.menu.insert_separator(index=1)

        itemdata = shell.menu.entryconfigure(0)
        labeldata = itemdata.get("label")
        if labeldata:
            shell.menu._testers[labeldata] = _cmd_in_shell_ask_aiassist_tester


        

        
         


    def do_para_start_on(self):
        if self.para_start_on_done:
            return

        for para in self.postit_paras_list:
            if not para.start_on:
                para.on_button_pressed()

        self.para_start_on_done = True
            

    def on_button_change(self, *args):
        value = self.button_tkvar.get()
        if value != self.visible :
            # make sure button value is toggled
            #print(self.tab_name, value, args)
            
            if value:
                common.postit_view.show_tab(self)
            else:
                common.postit_view.hide_tab(self)

    def gui_init(self):
        mode = self.group.mode
        group = self.group

        self.icon_image, self.fill_color, self.font_color =  group.next_icon_color()
        self.loaded = False
        self.visible = False

        # chat widget
        self.chat_widget_list = []
        self.CHAT_WIDGET_MAX = 100

        self.WIDGET_TYPE_ME_TEXT = 1
        self.WIDGET_TYPE_AI_TEXT = 2
        self.WIDGET_TYPE_AI_TEXT_NO_AVATAR = 3
        self.WIDGET_TYPE_AI_CODE = 4
        self.WIDGET_TYPE_AI_CODE_NO_AVATAR = 5
        self.WIDGET_TYPE_ABNORMAL = 6

        self.BG_COLOR = '#1d1f21'
        self.LIGHT_FG_COLOR = '#eeeeee'
        self.DARK_FG_COLOR = '#000000'
        #self.ME_BG_COLOR = '#fffd9a'
        # self.ME_BG_COLOR = '#40d517'
        # self.ME_BORDER_COLOR = '#40d517'
        self.ME_BG_COLOR = '#86d97b'
        self.ME_BORDER_COLOR = '#86d97b'
        #self.AI_TEXT_BG_COLOR = '#ffffff'
        #self.AI_TEXT_BG_COLOR = '#f2f2f2'
        self.AI_TEXT_BG_COLOR = '#1d1f21'
        self.AI_TEXT_BORDER_COLOR = '#5b99d6'
        self.AI_CODE_BG_COLOR = '#0080ff'
        self.AI_CODE_BORDER_COLOR = '#bedfff'
        self.ABNORMAL_BG_COLOR = '#cd1616'
        self.ABNORMAL_BORDER_COLOR = '#ffffff'

        self.BORDER_THICKNESS = 1

        # insert empty frame and hide
        
        self.tab_frame =  tk.Frame(mode.notebook_frame, 
                                   bg=self.BG_COLOR,
                                   
                                   )
        #checking on_mousewheel scroll
        self.tab_frame.ai_assistant_exists = True


        # ai tab frame structures
        # tab_frame - 
        #        connect_frame status_frame, chat_frame, asking_frame

        # add ai assistant related frames
        self.connect_frame = tk.Frame(self.tab_frame, bg=self.BG_COLOR )
        self.connect_frame.pack(expand=1)

        self.status_frame = tk.Frame(self.tab_frame, bg=self.BG_COLOR )
        #self.status_frame.pack(fill='x')

        self.chat_frame = CustomVerticallyScrollableFrame(self.tab_frame, bg=self.BG_COLOR)
        #self.chat_frame.pack(fill='both', expand=1)

        self.separator = tk.Frame(self.tab_frame, bg="#999999", height=1, bd=0)


        self.asking_frame = tk.Frame(self.tab_frame, bg=self.BG_COLOR )
        #self.asking_frame.pack(fill='x')

        self.connect_btn = tk.Button(self.connect_frame, 
                                     font=common.postit_para_font,
                                     text='開始使用 >>',
                                     bg=self.BG_COLOR,
                                     fg=self.LIGHT_FG_COLOR,
                                     command=self.on_connect_btn)
        self.connect_btn.pack(fill='x',pady=12)


        self.services = ('AUTO','Phind', 'Perplexity','Blackboxai','Koboldai','Llama2')
        self.service_combo = ttk.Combobox(
                self.connect_frame,
                width=12,
                state="readonly",
                takefocus=0,
                font=common.postit_para_font, 
                justify=tk.CENTER,
                values=self.services)
        self.service_combo.current(0)
        self.service_combo.pack(fill='x',pady=12)

        self.ai_use_note = tk.Label(
                self.connect_frame,
                text='生成式AI可能會發生偏誤\n請評估內容與查核重要資訊\n並遵守道德及法律規範\n',
                bg=self.BG_COLOR,
                fg='#eeeeee',
                                    )
        self.ai_use_note.pack(fill='x',pady=150)


        # self.close_btn = tk.Button(self.status_frame, 
        #                            font=common.note_font,
        #                            text='結束',
        #                            command=self.on_disconnect_btn)
        # self.close_btn.pack(side='right', padx=10)

        self.close_btn = tk.Button( self.status_frame,  
                                    borderwidth=0,
                                    compound='right',
                                    image=common.common_images['disconnect'] ,
                                    bg=common.aiassist_tab.BG_COLOR,
                                    command=self.on_disconnect_btn,
                                    padx=0,
                                    pady=0)        
        self.close_btn.pack(side='right',padx=10)

        self.status_label = tk.Label(self.status_frame, 
                                      text='',
                                      bg=self.BG_COLOR,
                                      fg=self.LIGHT_FG_COLOR, 
                                      font=common.note_font)
        self.status_label.pack(side='right')

        # for i in range(40):
        #     ttk.Label(self.chat_frame.interior, text='chat'+str(i)).pack()

        # self.asking_btn = tk.Button(self.asking_frame, 
        #                             text='詢問',
        #                             font=common.postit_para_font,
        #                             command=self.on_asking_btn)
        
        self.asking_btn = tk.Button(self.asking_frame,  
                                    borderwidth=0,
                                    compound='right',
                                    image=common.common_images['send_msg'] ,
                                    bg=common.aiassist_tab.BG_COLOR,
                                    command=self.on_asking_btn,
                                    padx=0,
                                    pady=0)        
        self.asking_btn.pack(side='right',padx=5)

        self.asking_text = tk.Text(self.asking_frame, 
                                   height=2,
                                   borderwidth=0, 
                                   bg=self.BG_COLOR,
                                   fg=self.LIGHT_FG_COLOR,
                                   insertbackground='#999999',
                                   font=common.postit_para_font)        
        self.asking_text.pack(side='right', fill='x', expand=1,padx=5)
        self.asking_text.bind("<Return>", self.on_asking_btn, True)
        self.asking_text.bind('<Button-3>', lambda event : AskTextRightClicker(self.asking_text, event))
        
        self.wait_answer = WaitingAnswerImage(self.chat_frame.interior)

        # on close  , stop thread
        get_workbench().bind("WorkbenchClose", self.on_aiassist_close, True)

         

        # add tab ref
        self.tab_frame.tab = self
        mode.tab_notebook.insert('end',self.tab_frame,
                          text = self.tab_label,
                          image = self.icon_image,
                          compound="top",
                          padding=0,
                        )
        mode.tab_notebook.hide(self.tab_frame)

        common.postit_view.bind("<Configure>", self.on_configure_resize, "+")
        get_workbench()._main_pw.bind("<ButtonRelease-1>", self.on_mouse_released, "+")

    def on_configure_resize(self, event):
        # if not self.is_chatting:
        #     return
        # when postit view changes size, mark it.
        mode = common.postit_view.current_mode
        tab = common.postit_view.py4t_mode_current_tab
        
        if mode == 'py4t' and tab is self  :
            self.size_changed = True
            # print('------ size changed ------------')
            # print(event)
            # w = common.postit_view.winfo_width()
            # print('postit view length ', w)
            # print('------------------')

    def on_mouse_released(self, event):
        #  determine chat text widget wordwrap length
        if  not self.size_changed:
            return
        
        mode = common.postit_view.current_mode
        tab = common.postit_view.py4t_mode_current_tab

        if mode == 'py4t' and tab is self  :
            w = common.postit_view.winfo_width() // 16
            bounded_w = w
            bounded_w =  min(max(w, self.LINEWRAP_MIN), self.LINEWRAP_MAX)
            print('adjust line characters :', w, bounded_w)
            #self.linewrap_length = bounded_w
            get_workbench().set_option(self.LINEWRAP_OPTION, bounded_w)
            print('set linewrap length ----------: ', bounded_w)

            if self.is_chatting: 
                # change every chat widget in queqe
                # re-pack every chat widget
                length = get_workbench().get_option(self.LINEWRAP_OPTION)
                for w in self.chat_widget_list:
                    w.pack_forget()
                    if not isinstance(w, ChatCodePostit):
                        w.set_wordwrap(length)

                for w in self.chat_widget_list:
                    w.pack(side='top', fill='x', expand=1, padx=5, pady=5)

                print('do re-pack chat widget ......')
            
                
        self.size_changed = False



    def on_aiassist_close(self, event):
        self.closing_queue.put(True)
        

    def switch_connect_or_chat(self, to_chat):
        if to_chat:
            self.connect_frame.pack_forget()

            self.status_frame.pack(fill='x', pady=5)
            self.chat_frame.pack(fill='both', expand=1, pady=5)
            self.separator.pack(fill='x', pady=0)
            self.asking_frame.pack(fill='x', pady=5)

            self.chatting = True
            self.size_changed = False
            
        else: # to connect
            self.status_frame.pack_forget()
            self.chat_frame.pack_forget()
            self.separator.pack_forget()
            self.asking_frame.pack_forget()

            self.connect_frame.pack(expand=1)

            
            # clean all chat widget
            while len(self.chat_widget_list) > 0:
                item = self.chat_widget_list.pop(0)
                item.destroy()
                del item
            # clean queue
            while self.asking_queue.qsize() > 0:
                self.asking_queue.get()

            while self.answer_queue.qsize() > 0:
                self.answer_queue.get()
            
            while self.closing_queue.qsize() > 0:
                self.closing_queue.get()

            self.chatting = False
            self.size_changed = False


    def on_connect_btn(self):
            service_name = self.service_combo.get()
            aiassist_thread = AiassistThread(service_name)

            aiassist_thread.start()
            get_workbench().after(500, self.delay_connection)

    def delay_connection(self):   
            self.switch_connect_or_chat(to_chat=True)

    def on_disconnect_btn(self):
        ans = messagebox.askyesno(title='離開？', 
                                    message='要停止AI程式助理嗎？',
                                    master=get_workbench())
        if ans:
            self.closing_queue.put(True)
            self.close_btn['state'] = 'disabled'
            self.asking_btn['state'] = 'disabled'
            self.asking_text['state'] = 'disabled'
            get_workbench().after(200, self.delay_disconnect)


    def delay_disconnect(self):
        if self.closing_queue.empty():
            self.close_btn['state'] = 'normal'
            self.asking_btn['state'] = 'normal'
            self.asking_text['state'] = 'normal'
            self.asking_text.delete('1.0', tk.END)

            self.switch_connect_or_chat(to_chat=False)
        else:
            get_workbench().after(200, self.delay_disconnect)

    def on_asking_btn(self, event=None, ask_content_from_editor_or_shell=None):
        # build ai assist postit

        # todo : check text content , 要不要詢問按鈕？
        # aiassist_postit = TryAiassistPostit(self.chat_frame.interior)

        
        if ask_content_from_editor_or_shell:
            # ask from editor or shell
            question = ask_content_from_editor_or_shell

        else: # ask from asking text
            question = self.asking_text.get("1.0",tk.END)
            self.asking_text.delete('1.0', tk.END)
            question = question.strip()
            if not question :
                return
        
        # split question if too long
        
        # lines = [ question[i:i+self.line_length] \
        #            for i in range(0, len(question), self.line_length)]
        # question = '\n'.join(lines)
        
        length = get_workbench().get_option(self.LINEWRAP_OPTION)
        asking_text_postit = AiassistChatText(self.chat_frame.interior,
                                            message=question, 
                                            wrap_length = length,
                                            widget_type=self.WIDGET_TYPE_ME_TEXT,
                                            omit_avatar=False)
        asking_text_postit.pack(side='top', fill='x', expand=1, padx=10, pady=10)
        self.chat_widget_list.append(asking_text_postit)

        

        if len(self.chat_widget_list) > self.CHAT_WIDGET_MAX:
                # keep chat widget below max 
                item = self.chat_widget_list.pop(0) 
                item.destroy()
                del item
                print('Drop old chat widget ...')
                

        self.close_btn['state'] = 'disabled'
        self.asking_btn['state'] = 'disabled'
        self.asking_text['state'] = 'disabled'
        self.chat_frame_update()

        self.asking_queue.put(question)

        # wait answer 
        self.wait_answer.pack(side='top', fill='x', expand=1, padx=10, pady=10)
        self.chat_frame_update()
        get_workbench().after(300, self.checking_answer)

    def checking_answer(self): 
        if self.answer_queue.qsize() > 0:
            print(' got answer .....')

            self.wait_answer.pack_forget()

            ans_ntuple = self.answer_queue.get()
            if ans_ntuple.type == common.ANS_TYPE_TEXT:
                answer = ans_ntuple.answer
                length = get_workbench().get_option(self.LINEWRAP_OPTION)
                answer_text_postit = AiassistChatText(self.chat_frame.interior,
                                            message=answer, 
                                            wrap_length = length,
                                            widget_type=self.WIDGET_TYPE_AI_TEXT,
                                            omit_avatar=self.is_successive_ans )
            elif ans_ntuple.type == common.ANS_TYPE_CODE:
                answer = ans_ntuple.answer
                answer_text_postit = ChatCodePostit(self.chat_frame.interior,
                                            code=answer, 
                                            omit_avatar=self.is_successive_ans
                                            )
            elif ans_ntuple.type == common.ANS_TYPE_ERROR:
                answer = '服務異常，請於網頁提問!'
                length = get_workbench().get_option(self.LINEWRAP_OPTION)
                answer_text_postit = AiassistChatText(self.chat_frame.interior,
                                            message=answer, 
                                            wrap_length = length,
                                            widget_type=self.WIDGET_TYPE_ABNORMAL,
                                            omit_avatar=False)
            else:
                print('unknown answer type')
                raise TypeError
            
            answer_text_postit.pack(side='top', fill='x', expand=1, padx=5, pady=5)
            self.chat_widget_list.append(answer_text_postit)

            if len(self.chat_widget_list) > self.CHAT_WIDGET_MAX:
                # keep chat widget below max 
                item = self.chat_widget_list.pop(0) 
                item.destroy()
                del item
                print('Drop old chat widget ...')

            self.close_btn['state'] = 'normal'
            self.asking_btn['state'] = 'normal'
            self.asking_text['state'] = 'normal'
            self.chat_frame_update()

            self.is_successive_ans = True

            # handle next answer if exists
            if self.answer_queue.qsize() > 0:
                get_workbench().after(300, self.checking_answer)
            else: # all answers are handled
                self.is_successive_ans = False
                return

        else:
            # wait answer effect
            self.wait_answer.next()

            get_workbench().after(300, self.checking_answer)


    


    def chat_frame_update(self):
        self.chat_frame.update_idletasks()
        self.chat_frame.update_scrollbars()
        self.chat_frame.scroll_to_end()
        
       


    def popup_init(self, example_vars):
        self.example_vars = example_vars
        self.popup_menu = tk.Menu(self.frame, tearoff=0)

        self.popup_menu.add_command(label="範例變數匯入",
            command=self.import_example_vars)

        self.frame.bind("<Button-3>", self.popup)


    def import_example_vars(self):
        s = '【匯入變數名稱】\n'
        for i in self.example_vars:
            s = s + i + '\n'
        s += '\n'

        ans = messagebox.askokcancel('範例變數匯入',s, master=get_workbench())
        #print(ans)
        if ans: # import vars into vars_menu
            vars_counter = common.share_vars_postit.vars_counter

            for var in self.example_vars:
                if var not in vars_counter:
                    vars_counter[var] = 1
            common.share_vars_postit.update_vars_menu()            
        else: # no
            return

    def popup(self, event):
        #if self.tool_name != 'variable_get':
        self.popup_menu.tk_popup(event.x_root, event.y_root)

class AskTextRightClicker:
    def __init__(self, ask_text, event):
        self.ask_text = ask_text
        right_click_menu = tk.Menu(None, tearoff=0, takefocus=0)
    
        right_click_menu.add_command(label='貼上', command=self.paste)
        right_click_menu.tk_popup(event.x_root, event.y_root)


    def paste(self):
        cliptext = get_workbench().clipboard_get()
        self.ask_text.insert("insert", cliptext)



class MoreTab:
    def __init__(self, notebook):
        im = Image.open(Path(__file__).parent / 'images' / 'more.png')       
        self.icon_image = ImageTk.PhotoImage(im) 

        # prepare  frame
        
        self.tab_frame = CustomVerticallyScrollableFrame(notebook)
        self.tab_frame.tab = self
        notebook.insert('end',self.tab_frame,
                          text = '      ',
                          image = self.icon_image,
                          compound=tk.CENTER,
                          #sticky='we',
                          padding='0',
                        )

class PostitPara:
    def __init__(self, tab, on_label, off_label, start_on):
        self.tab = tab
        self.on_label = on_label
        self.off_label = off_label
        self.start_on = start_on
        self.para_visible = True

        # text = on_label if start_on else off_label
        # if start_on :
        #     text = on_label
        # else:
        #     text = off_label

        button_font = common.postit_para_font
        self.para_button = tk.Button(tab.tab_frame.interior,
                command=self.on_button_pressed, 
                text=on_label, relief='flat', font=button_font)
        self.para_button.grid(sticky='w', padx=0, pady=12)
        #self.para_button.pack(side=tk.TOP, anchor='w', padx=2, pady=2)

        self.ori_bg_color = self.para_button.cget('bg')
        self.para_button.config(bg="#ffffff")
        

        self.para_frame = ttk.Frame(tab.tab_frame.interior,
                )
        self.para_frame.grid(sticky='we', padx=0, pady=0)
        #self.para_frame.pack(side=tk.TOP, padx=10, pady=8, anchor='w')

        # if not start_on:
        #     self.para_frame.grid_remove()

    def on_button_pressed(self):
        if self.para_visible :
            #self.para_button.config(text=self.off_label, bg=self.ori_bg_color)
            self.para_button.config(text=self.off_label, fg='#a0a0a0', bg=self.ori_bg_color)
            #self.para_button.config(text=self.off_label, bg="#e5e5e5")
            self.para_visible = False
            self.para_frame.grid_remove()
            #self.para_frame.pack_forget()
        else:
            #self.para_button.config(text=self.on_label, bg="#ffffff")
            self.para_button.config(text=self.on_label, fg="black", bg="#ffffff")
            self.para_visible = True
            self.para_frame.grid()
            #self.para_frame.grid_propagate(0)
            #self.para_frame.pack(side=tk.TOP, padx=10, pady=8, anchor='w')

            # for para in self.tab.postit_paras_list:
            #     para.para_frame.grid_remove()

            # for para in self.tab.postit_paras_list:
            #     if para.visible:
            #         para.para_frame.grid(sticky='w', padx=0, pady=0)


class PythonPostitView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        common.postit_view = self 
        self.last_focus = None
        self.symbol_row_index = 0
        self.current_mode = 'py4t'
        self.last_backend = ''
        self.all_modes = OrderedDict()
        self.py4t_mode_current_tab = None

        im = Image.open(Path(__file__).parent / 'images' / 'vertical_spacer.png')       
        self.spacer_image= ImageTk.PhotoImage(im) 

        self.toolbar_init()
        self.all_assets_init()
        self.all_modes_init()
        self.switch_mode_by_backend()

        get_workbench().bind("BackendRestart", self.switch_mode_by_backend, True)
        self.bind_all("<MouseWheel>", self.on_mousewheel,"+")    

        # #add notebook tabs

        # self.add_tab('builtin', '程式庫','basic')

        # self.add_tab('auto', ' 自動 ','pack')



    def on_mousewheel(self, event):
        tab_notebook = self.all_modes[self.current_mode].tab_notebook
        tab_widget_name = tab_notebook.select()
        if tab_widget_name:
            tab_frame = tab_notebook.nametowidget(tab_widget_name)
            if hasattr(tab_frame, 'ai_assistant_exists'):
                common.aiassist_tab.chat_frame._on_mousewheel(event)
                
            else:
                tab_frame._on_mousewheel(event)
        

    def switch_mode_by_backend(self, event=None):
        backend_in_option = get_workbench().get_option("run.backend_name")

        if backend_in_option == self.last_backend:
            # backend not changed, no need to switch
            #print('no need to switch mode')
            return
        else:
            # backend has changed, check which mode to switch
            #self.all_modes['bit'].notebook_frame.pack(expand=False)
            #self.all_modes['bit'].tab_notebook.pack(expand=False)
            #self.all_modes['py4t'].notebook_frame.pack(expand=False)
            #self.all_modes['py4t'].tab_notebook.pack(expand=False)
            if backend_in_option == 'microbit':
                
                #self.all_modes['bit'].tab_notebook.pack()
                self.all_modes['py4t'].notebook_frame.pack_forget()
                self.all_modes['py4t'].tab_notebook.pack_forget()
                ###self.all_modes['py4t'].notebook_frame.grid_remove()
                ###self.all_modes['py4t'].tab_notebook.grid_remove()
                #self.all_modes['py4t'].notebook_frame.config(expand=False)
                self.all_modes['bit'].notebook_frame.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                self.all_modes['bit'].tab_notebook.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                ###self.all_modes['bit'].notebook_frame.grid()
                ###self.all_modes['bit'].tab_notebook.grid()
                #self.all_modes['bit'].notebook_frame.config(expand=True)
                #self.all_modes['py4t'].tab_notebook.pack_forget()
                self.current_mode = 'bit'
            else:
                
                #self.all_modes['py4t'].tab_notebook.pack()   
                self.all_modes['bit'].notebook_frame.pack_forget()
                self.all_modes['bit'].tab_notebook.pack_forget()
                ###self.all_modes['bit'].notebook_frame.grid_remove()
                ###self.all_modes['bit'].tab_notebook.grid_remove()
                #self.all_modes['bit'].notebook_frame.config(expand=False)
                self.all_modes['py4t'].notebook_frame.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                self.all_modes['py4t'].tab_notebook.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                ###self.all_modes['py4t'].notebook_frame.grid()
                ###self.all_modes['py4t'].tab_notebook.grid()
                #self.all_modes['py4t'].notebook_frame.config(expand=True)
                #self.all_modes['bit'].tab_notebook.pack_forget()
                self.current_mode = 'py4t'              

            self.last_backend = backend_in_option

    def all_assets_init(self):
        """
        load all assets folder into asset_groups (ordered dict)

        asset structure : groups - categories - files
        """

        # all asset groups
        self.asset_groups = OrderedDict()

        # prepare asset groups
        assets_path = Path(__file__).parent / 'assets'
        
        with open(assets_path / 'groups_info.json', encoding='utf8') as fp:
            groups_info = json.load(fp)
        
        for g in groups_info:
            asset_group = g['asset_group']
            group_title = g['group_title']
            self.asset_groups[asset_group] = AssetGroup(asset_group, group_title)
        
    


    def all_modes_init(self):        

        # # collect mode, group, tabs json data (in Mode TabGroup Tab class ) 
        self.all_modes['py4t'] = Mode('py4t', 'python學習模式', has_more_tab=True)
        self.all_modes['bit'] = Mode('bit', 'microbit模式', has_more_tab=True)

        # set default option (source: group json data)
        for g in self.all_modes['py4t'].groups.values():
            mode_name = g.mode.mode_name
            group_name = g.group_name
            option_name = 'postit_tabs.{}.{}'.format(mode_name, group_name)
            #print('defalut:', option_name, g.default_tabs)
            get_workbench().set_default(option_name, g.default_tabs)

        for g in self.all_modes['bit'].groups.values():
            mode_name = g.mode.mode_name
            group_name = g.group_name
            option_name = 'postit_tabs.{}.{}'.format(mode_name, group_name)
            #print('defalut:', option_name, g.default_tabs)
            get_workbench().set_default(option_name, g.default_tabs)

        # gui init second (build notebook and empty tab frame)
        for mode in self.all_modes.values():
            mode.gui_init()
            mode.add_more_tab()
            for group in mode.groups.values():
                group.gui_init()
                for tab in group.tabs.values():
                    tab.gui_init()
            

        # build more tab content, set visible if needed
        self.more_tab_gui_init('py4t')
        self.more_tab_gui_init('bit')

        # select tab
        self.select_first_visible_tab('py4t')
        self.select_first_visible_tab('bit')


        # notebook menu
        
        #self.tab_menu = tk.Menu(self.notebook, tearoff=0)
        #self.tab_menu.add_command(label='【便利貼】')
        #self.tab_menu.add_separator()
        #self.option = tk.BooleanVar()
        #self.option.set(True)
        #self.tab_menu.add_checkbutton(label="選項", onvalue=1, offvalue=0, 
        #        variable=self.option,
        #        command=lambda:self.remove_tab('flow'),
        #        )
        #
        #self.notebook.bind("<Button-3>", self.tab_menu_popup)



    def select_first_visible_tab(self, mode_name):
        mode = self.all_modes[mode_name]
        for g in mode.groups.values():
            for tab in g.tabs.values():
                if tab.visible:
                    mode.tab_notebook.select(tab.tab_frame)
                    
                    if mode_name == 'py4t':
                        self.py4t_mode_current_tab = tab
                        #print('[py4t mode ] ', tab)
                    #print(mode_name + ' mode select first visible tab: ', tab.tab_name)
                    return

     
        
        # self.all_modes['bit'].tab_notebook.select(0)


    def more_tab_gui_init(self, mode_name):
        mode  = self.all_modes[mode_name]
        more_tab_frame = mode.more_tab.tab_frame
        
        # title label
        title_font = common.tab_title
        tk.Label(more_tab_frame.interior, 
                text='便利貼設定', font=title_font,
        ).pack(side=tk.TOP, padx=5, pady=8, anchor='center')

        ttk.Separator(more_tab_frame.interior, orient=tk.HORIZONTAL 
                    ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        

        #names_of_group = mode.groups.keys()
        #print(names_of_group)
        
        # group and tab buttons
        label_font = common.tab_label
        for g in mode.groups.values():
            text = '{}'.format(g.group_label)
            ttk.Label(more_tab_frame.interior,
                      text=text,
                      image=g.icon_images[0],
                      compound='left',
                      font=label_font,
            ).pack(side=tk.TOP, padx=5, pady=8, anchor='c')
        
            group_frame = ttk.Frame(more_tab_frame.interior,
                      #relief="groove",
            )
            group_frame.pack(side=tk.TOP, padx=10, pady=8, anchor='center')
            
            option_name = 'postit_tabs.{}.{}'.format(g.mode.mode_name, g.group_name)
            selected_group_tabs = get_workbench().get_option(option_name)
            
            #print(g.group_name, group_tab_option)

            for i, tab in enumerate(g.tabs.values()):
                #text = tab.tab_label.replace('\n','')
                #text = text.replace(' ','')
                
                tk.Radiobutton(group_frame,text='隱藏',
                    variable=tab.button_tkvar,font=label_font,
                    indicatoron=0, value=0, selectcolor='#88ebfc',
                    ).grid(row=i, column=0, padx=3, pady=2)
                tk.Radiobutton(group_frame,text='顯示',
                    variable=tab.button_tkvar,font=label_font,
                    indicatoron=0, value=1, selectcolor='#ffc526',
                    ).grid(row=i, column=1, padx=3, pady=2)
                tk.Label(group_frame,text=tab.tab_title,
                    font=label_font,
                    ).grid(row=i, column=2, padx=5, pady=2, sticky='w')

                if tab.tab_name in selected_group_tabs:
                   tab.button_tkvar.set(True)    


            ttk.Separator(more_tab_frame.interior, orient=tk.HORIZONTAL
                    ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        
        
        # for i in range(10):
        #     ttk.Label(tab_frame.interior,
        #             text=str(i),
                        
                     
        #         ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

 

    def show_tab(self, tab):
        mode = tab.group.mode
        group = tab.group
        
        if not tab.visible:
            mode.tab_notebook.add(tab.tab_frame)
            if not tab.loaded:
                if tab.tab_name == 'aiassist':
                    # already build in AiassistTab
                    pass
                else:
                    self.load_tab_json(tab)
                tab.loaded = True
            tab.visible = True

            # add tab in option 
            option_name = 'postit_tabs.{}.{}'.format(mode.mode_name, group.group_name)
            selected_group_tabs = get_workbench().get_option(option_name)
            
            if not tab.tab_name in selected_group_tabs:
                selected_group_tabs.append(tab.tab_name)
                #print('show_tab: ',option_name, selected_group_tabs)
            get_workbench().set_option(option_name, selected_group_tabs)

    def load_tab_json(self, tab):
        mode = tab.group.mode
        
        with open(tab.tab_path, encoding='utf8') as fp:
            postit_list = json.load(fp)
        
        # if name in common.postit_tabs:
        #     print('tab', name, ' already exists')
        #     return

        # tab = PostitTab(name, tab_data['label'], tab_data['type'])
        # common.postit_tabs[name] = tab

        # tab.frame = CustomVerticallyScrollableFrame(self.notebook)
        # self.notebook.insert('end',tab.frame,
        #                   text = tab.label,
        #                   image = tab.image,
        #                   compound="top",
        #                 )

        # parse json data
        #self.label_font = font.Font(size=12, weight=font.NORMAL, family='Consolas')

        # set seperator style
        

        for postit_data in postit_list:
            if postit_data['postit_type'] == 'dropdown_postit':
                self.build_dropdown_postit(tab, postit_data)

            elif postit_data['postit_type'] == 'ttk_label':
                self.build_ttk_label(tab, postit_data)

            elif postit_data['postit_type'] == 'postit_title':
                self.build_postit_title(tab, postit_data)

            elif postit_data['postit_type'] == 'ttk_separator':
                self.build_ttk_separator(tab, postit_data)

            elif postit_data['postit_type'] == 'postit_para':
                self.build_postit_para(tab, postit_data)

            elif postit_data['postit_type'] == 'in_para_dropdown_postit':
                self.build_in_para_dropdown_postit(tab, postit_data)

            elif postit_data['postit_type'] == 'in_para_block_enclosed_postit':
                self.build_in_para_block_enclosed_postit(tab, postit_data)

            elif postit_data['postit_type'] == 'asset_copy_btn':
                self.build_asset_copy_btn(tab, postit_data)
    

            #elif postit_data['postit_type'] == 'bit_install_lib_postit':
            #    self.build_bit_install_lib_postit(tab, postit_data)

        # end vertical spacer for end space scrolling
        # add 4 times to make more spaces
        tk.Label(tab.tab_frame.interior, text='',
                image=self.spacer_image).grid(sticky='ew', padx=0, pady=2)
        tk.Label(tab.tab_frame.interior, text='',
                image=self.spacer_image).grid(sticky='ew', padx=0, pady=2)
        tk.Label(tab.tab_frame.interior, text='',
                image=self.spacer_image).grid(sticky='ew', padx=0, pady=2)
        tk.Label(tab.tab_frame.interior, text='',
                image=self.spacer_image).grid(sticky='ew', padx=0, pady=2)


    def build_dropdown_postit(self, tab, postit_data):
        temp_code_list = []
        for i in postit_data["items"]:
            temp_code_list.append(CodeNTuple(
                menu_display=i['menu_display'],
                code=i['code'],
                code_display=i['code_display'],
                note=i['note'],
                long_note=i['long_note'] ))

        DropdownPostit(tab.tab_frame.interior, tab, code_list = temp_code_list,
            postfix_enter=postit_data['postfix_enter']).grid(sticky='w', padx=5, pady=8)    
            #postfix_enter=p['postfix_enter']).pack(side=tk.TOP, anchor='w', padx=5, pady=8)    

    def build_asset_copy_btn(self, tab, postit_data):
        parent = tab.current_postit_para.para_frame
        group_obj = self.asset_groups[postit_data['asset_group']]
        AssetCopyBtn(parent, group_obj,  
        ).grid( sticky='w',padx=30, pady=8)

    def build_ttk_label(self, tab, postit_data):
        ttk.Label(tab.tab_frame.interior, 
            text=postit_data['text'],
            font=common.tab_label,    
            compound=tk.LEFT, 
        ).grid( sticky='w',padx=0, pady=8)
        #).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

    def build_postit_title(self, tab, postit_data):
        ttk.Label(tab.tab_frame.interior, 
            text=tab.tab_title,
            font=common.tab_label,
            image=tab.icon_image,
            compound='left',
        ).grid( padx=0, pady=8)

    def build_ttk_separator(self, tab, postit_data):
        #ttk.Separator(tab.tab_frame.interior, orient=tk.HORIZONTAL, style="Line.TSeparator",
        #    ).grid(sticky='ew', padx=0, pady=5)

        separator = tk.Frame(tab.tab_frame.interior, bg="#cccccc", height=1, bd=0)
        separator.grid(sticky='ew', padx=0, pady=5)   

    def build_postit_para(self, tab, postit_data):
        on_label = postit_data['on_label']
        off_label = postit_data['off_label']
        start_on = postit_data['start_on']
        para = PostitPara(tab,on_label, off_label, start_on)
        tab.current_postit_para = para
        tab.postit_paras_list.append(para)

    def build_in_para_dropdown_postit(self, tab, postit_data):
        temp_code_list = []
        for i in postit_data["items"]:
            temp_code_list.append(CodeNTuple(
                menu_display=i['menu_display'],
                code=i['code'],
                code_display=i['code_display'],
                note=i['note'],
                #long_note=i['long_note'] ))
                long_note=i.get('long_note', True),
                #start_hide_note=i.get('start_hide_note', False),
                ))

        parent = tab.current_postit_para.para_frame
        DropdownPostit(parent, tab, code_list = temp_code_list,
            postfix_enter=postit_data['postfix_enter'],
            start_hide_note=postit_data.get('start_hide_note',True)
            ).grid(sticky='w', padx=4, pady=5)                
            #postfix_enter=p['postfix_enter']).pack(side=tk.TOP, anchor='w', padx=5, pady=8)  

    def build_in_para_block_enclosed_postit(self, tab, postit_data):
        temp_code_list = []
        for i in postit_data["items"]:
            temp_code_list.append(CodeNTuple(
                menu_display=i['menu_display'],
                code=i['code'],
                code_display=i['code_display'],
                note=i['note'],
                #long_note=i['long_note'] ))
                long_note=i.get('long_note', True),
                #start_hide_note=i.get('start_hide_note', False),
                ))

        parent = tab.current_postit_para.para_frame
        BlockEnclosedPostit(parent, tab, code_list = temp_code_list,
            #postfix_enter=postit_data.get('postfix_enter',True),
            # postfix_enter always True
            postfix_enter=True,
            start_hide_note=postit_data.get('start_hide_note',True)
            ).grid(sticky='w', padx=4, pady=5)                


    def hide_tab(self, tab):
        mode = tab.group.mode
        group = tab.group
        
        if tab.visible:
            mode.tab_notebook.hide(tab.tab_frame)
            tab.visible = False        

            # remove tab in option 
            option_name = 'postit_tabs.{}.{}'.format(mode.mode_name, group.group_name)
            selected_group_tabs = get_workbench().get_option(option_name)
            if tab.tab_name in selected_group_tabs:
                selected_group_tabs.remove(tab.tab_name)
                #print('hide_tab: ',option_name, selected_group_tabs)
            get_workbench().set_option(option_name, selected_group_tabs)

    

    def toolbar_init(self):

        # var toolbar
        #self.var_toolbar = ttk.Frame(self.interior)
        self.code_toolbar = ttk.Frame(self)
        self.code_toolbar.pack(side=tk.TOP, fill=tk.X)
        ###self.code_toolbar.grid(row=0, column=0, sticky='w')


        common.share_var_get_postit = VariableFetchToolPostit(
                self.code_toolbar, tool_name='variable_get')
        #common.share_var_assign_postit = VariableFetchToolPostit(
        #        self.var_toolbar, tool_name='variable_assign')
        common.share_vars_postit = VariableMenuPostit(self.code_toolbar)

        comment = CommentToolPostit(self.code_toolbar)
        comment.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(comment, '註解 (右鍵選單)')

        common.share_var_add_postit = VariableAddToolPostit(self.code_toolbar)
        common.share_var_add_postit.pack(side=tk.LEFT,padx=0, pady=3)
        create_tooltip(common.share_var_add_postit, '把選取文字加到變數清單')

        share_var = common.share_vars_postit
        share_var.pack(side=tk.LEFT,padx=0, pady=3)
        create_tooltip(share_var, '變數清單 (右鍵選單)')
        
        var_get = common.share_var_get_postit
        var_get.pack(side=tk.LEFT,padx=0, pady=3)
        create_tooltip(var_get, '貼上目前變數')
        #common.share_var_assign_postit.pack(side=tk.LEFT,padx=2, pady=3)
        
        symbol = SymbolToolPostit(self.code_toolbar)
        symbol.pack(side=tk.LEFT,padx=8, pady=3)
        create_tooltip(symbol, '符號、關鍵字與內建函式 (右鍵可換)')

        # edit_toolbar
        #self.edit_toolbar = ttk.Frame(self.interior)
        self.edit_toolbar = ttk.Frame(self)
        self.edit_toolbar.pack(side=tk.TOP, fill=tk.X)
        ###self.edit_toolbar.grid(row=1, column=0, sticky='w')

        self.keyin_display_frame = ttk.Frame(self)
        self.keyin_display_frame.pack(side=tk.TOP, fill=tk.X)
        ###self.keyin_display_frame.grid(row=2, column=0, sticky='w')

        ### todo
        #keyin_display_postit = KeyinDisplayToolPostit(self.edit_toolbar,
        #                           self.keyin_display_frame)
        #keyin_display_postit.pack(side=tk.LEFT,padx=1, pady=3)
        #create_tooltip(keyin_display_postit, '英打顯示器(右鍵可換位置)')

        pilcrow_postit = PilcrowToolPostit(self.edit_toolbar)
        pilcrow_postit.pack(side=tk.LEFT,padx=1, pady=3)
        create_tooltip(pilcrow_postit, '顯示空白鍵與換行(7秒內復原)')
        
        dedent_postit = DedentToolPostit(self.edit_toolbar)
        dedent_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(dedent_postit, '減少縮排(向左4格)')

        indent_postit = IndentToolPostit(self.edit_toolbar)
        indent_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(indent_postit, '增加縮排(向右4格)')

        undo_postit = UndoToolPostit(self.edit_toolbar)
        undo_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(undo_postit, '復原')

        redo_postit = RedoToolPostit(self.edit_toolbar)
        redo_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(redo_postit, '取消復原')

        cut_postit = CutToolPostit(self.edit_toolbar)
        cut_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(cut_postit, '剪下')

        copy_postit = CopyToolPostit(self.edit_toolbar)
        copy_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(copy_postit, '複製')

        paste_postit = PasteToolPostit(self.edit_toolbar)
        paste_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(paste_postit, '貼上')

        backspace = BackspaceToolPostit(self.edit_toolbar)
        backspace.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(backspace, '退位鍵(向左刪除)')


        enter_postit = EnterToolPostit(self.edit_toolbar)
        enter_postit.pack(side=tk.LEFT,padx=3, pady=3)
        create_tooltip(enter_postit, '輸入鍵(換行)')


    def tab_menu_popup(self, event):
        #if self.tool_name != 'variable_get':
        if event:
            self.tab_menu.tk_popup(event.x_root, event.y_root)




    def on_tab_click(self, event):
        """record focus widget"""        
        self.last_focus = get_workbench().focus_get()

    def on_tab_changed(self, event):
        tab_notebook = self.all_modes[self.current_mode].tab_notebook
        
        tab_num = tab_notebook.index('end')
        
        tab_widget_name = event.widget.select()
        if tab_num > 0 and tab_widget_name:
            tab_frame = tab_notebook.nametowidget(tab_widget_name)
            tab = tab_frame.tab
            #record current tab
            if not isinstance(tab, MoreTab) and self.current_mode == 'py4t' \
                            and tab.group.mode.mode_name == 'py4t':
                #print('-----------on tab change . py4t mode current tab: ', tab.tab_name)
                self.py4t_mode_current_tab = tab

            if not isinstance(tab, MoreTab) and not tab.para_start_on_done and tab.loaded:
                tab.do_para_start_on()
                


        """restore last focus widget"""
        if self.last_focus:
            self.last_focus.focus_set()
            self.last_focus = None



class CustomVerticallyScrollableFrame(ttk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

    def __init__(self, master, bg=''):
        if bg:
            tk.Frame.__init__(self, master, bg=bg)
            # set up scrolling with canvas
            #vscrollbar = tk.Scrollbar(self, troughcolor=bg, bg=bg, orient=tk.VERTICAL)
            ###_ , vstyle = self.make_scrollbar_styles(troughcolor='grey', background=bg, arrowcolor=bg)
            _ , vstyle = self.make_scrollbar_styles(troughcolor=bg, background='grey', arrowcolor='grey')
            vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, style=vstyle)

            self.canvas = tk.Canvas(self,bg=bg, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        else:
            tk.Frame.__init__(self, master)
            # set up scrolling with canvas
            vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
            self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)

        vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        ###self.canvas.grid(row=0, column=0, sticky=tk.NS)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        ###vscrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        if bg:
            self.interior = tk.Frame(self.canvas, bg=bg)
        else:
            self.interior = tk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)
        self.bind("<Configure>", self._configure_interior, "+")
        self.bind("<Expose>", self._expose, "+")
        #self.bind_all("<MouseWheel>", self._on_mousewheel,"+")

    def _expose(self, event):
        self.update_idletasks()
        self.update_scrollbars()

    def _configure_interior(self, event):
        self.update_scrollbars()
        

    def update_scrollbars(self):
        # update the scrollbars to match the size of the inner frame
        size = (self.canvas.winfo_width(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (
            self.interior.winfo_reqwidth() != self.canvas.winfo_width()
            and self.canvas.winfo_width() > 10
        ):
            # update the interior's width to fit canvas
            # print("CAWI", self.canvas.winfo_width())
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        #if isinstance(event.widget, BasePostit):
        if 'customverticallyscrollableframe' in str(event.widget):
            #print(str(event.widget))
            
            
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def scroll_to_end(self):
        self.canvas.yview_moveto(1)

    def make_scrollbar_styles(self, 
        troughcolor='black',
        background='green',
        arrowcolor='red') :
        """
        Style the scrollbars.  Usage:
            parent_frame = ... # tk.Frame(...) or tk.Tk() or whatever you're using for the parent
            hstyle, vstyle = make_scrollbar_styles()
            self._vbar = ttk.Scrollbar(parent_frame, orient='vertical', style=vstyle)
            self._hbar = ttk.Scrollbar(parent_frame, orient='horizontal', style=hstyle)
        """
        style = ttk.Style()

        for is_hori in (True, False):
            v = "Horizontal" if is_hori else "Vertical"
            style.element_create(f'CustomScrollbarStyle.{v}.Scrollbar.trough', 'from', 'default')
            style.element_create(f'CustomScrollbarStyle.{v}.Scrollbar.thumb', 'from', 'default')
            style.element_create(f'CustomScrollbarStyle.{v}.Scrollbar.leftarrow', 'from', 'default')
            style.element_create(f'CustomScrollbarStyle.{v}.Scrollbar.rightarrow', 'from', 'default')
            style.element_create(f'CustomScrollbarStyle.{v}.Scrollbar.grip', 'from', 'default')
            style.layout(
                f'CustomScrollbarStyle.{v}.TScrollbar',
                [(f'CustomScrollbarStyle.{v}.Scrollbar.trough', {
                    'children': [
                        # Commenting in these 2 lines adds arrows (at least horizontally)
                        # (f'CustomScrollbarStyle.{v}.Scrollbar.leftarrow', {'side': 'left', 'sticky': ''}) if is_hori else (f'CustomScrollbarStyle.{v}.Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
                        # (f'CustomScrollbarStyle.{v}.Scrollbar.rightarrow', {'side': 'right', 'sticky': ''})  if is_hori else (f'CustomScrollbarStyle.{v}.Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
                        (f'CustomScrollbarStyle.{v}.Scrollbar.thumb', {
                            'unit': '1',
                            'children': [(f'CustomScrollbarStyle.{v}.Scrollbar.grip', {'sticky': ''})],
                            'sticky': 'nswe'}
                        )
                    ],
                    'sticky': 'we' if is_hori else 'ns'}),
                ])
            style.configure(f'CustomScrollbarStyle.{v}.TScrollbar', troughcolor=troughcolor, background=background, arrowcolor=arrowcolor, borderwidth=0, relief='flat')
            # Comment in the following to customize disable/active colors, whatever that means
            # style.map(f'CustomScrollbarStyle.{v}.TScrollbar', background=[('pressed', '!disabled', disabledcolor), ('active', 'orange')])
        return "CustomScrollbarStyle.Horizontal.TScrollbar", "CustomScrollbarStyle.Vertical.TScrollbar"


class AboutDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title('關於Py4t')
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        # bg_frame = ttk.Frame(self) # gives proper color in aqua
        # bg_frame.grid()

        heading_font = tk.font.nametofont("TkHeadingFont").copy()
        heading_font.configure(size=19, weight="bold")
        heading_label = ttk.Label(
            main_frame, text="Py4t(版本:{})".format(get_version()), font=heading_font
        )
        heading_label.grid()

        

        text_font = font.Font(size=14, weight=font.NORMAL, family='Consolas')

        
        



        credits_label = ttk.Label(
            main_frame,
            font = text_font,
            text=
                "由中小學教師發起的計畫\n"
                + "採用多個開放原始碼套件\n"
                + "整合成適合青少年的python編輯器\n"
                + "\n"
                + "目的是搭一座從Scratch到Python的學習之橋\n"
                + "讓青少年實作程式、運算思維與體驗科技\n"
                + "\n"
                 + "【特別感謝(詳見連結)】\n"
                # + "桃園市建國自造教育及科技中心\n"
                # + "新竹縣博愛自造教育及科技中心\n"
                # + "臺北市新興自造教育及科技中心\n"
                # + "桃園市南門國民小學\n"
                # + "Python、Thonny及各個函式庫的開發者\n"
            ,
            #style="Url.TLabel",
            #cursor="hand2",
            #font=url_font,
            justify="center",
        )
        credits_label.grid()
        # credits_label.bind(
        #     "<Button-1>",
        #     lambda _: webbrowser.open("https://github.com/thonny/thonny/blob/master/CREDITS.rst"),
        # )

        credit_url = "https://beardad1975.github.io/py4t/about/acknowledge/"
        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        credit_url_label = ttk.Label(
            main_frame, text=credit_url, style="Url.TLabel", cursor="hand2", font=url_font
        )
        credit_url_label.grid()
        credit_url_label.bind("<Button-1>", lambda _: webbrowser.open(credit_url))

        sep_label = ttk.Label(
            main_frame, text="\n", 
        )
        sep_label.grid()

        link_note_label = ttk.Label(
            main_frame, text="【網站與討論區】", font=text_font
        )
        link_note_label.grid()


        url = "https://beardad1975.github.io/py4t/"
        #url_font = tk.font.nametofont("TkDefaultFont").copy()
        #url_font.configure(underline=1)
        url_label = ttk.Label(
            main_frame, text=url, style="Url.TLabel", cursor="hand2", font=url_font
        )
        url_label.grid()
        url_label.bind("<Button-1>", lambda _: webbrowser.open(url))

        url2 = "https://www.facebook.com/groups/856789691692686"
        #url_font = tk.font.nametofont("TkDefaultFont").copy()
        #url_font.configure(underline=1)
        url_label2 = ttk.Label(
            main_frame, text=url2, style="Url.TLabel", cursor="hand2", font=url_font
        )
        url_label2.grid()
        url_label2.bind("<Button-1>", lambda _: webbrowser.open(url2))

        sep_label = ttk.Label(
            main_frame, text="\n", 
        )
        sep_label.grid()

        license_font = font.Font(size=10, weight=font.NORMAL, family='Consolas')
        #license_font.configure(size=12)
        license_label = ttk.Label(
            main_frame,
            text="Copyright (©) "
            + str(datetime.datetime.now().year)
            + " Wen Hung, Chang 張文宏\n"
            + "採MIT授權\n",
            justify=tk.CENTER,
            font=license_font,
        )
        license_label.grid(pady=20)

        

        ok_button = ttk.Button(main_frame, text="OK", command=self._ok, default="active")
        ok_button.grid(pady=(0, 15))
        ok_button.focus_set()

        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._ok, True)

    def _ok(self, event=None):
        self.destroy()

    # def get_os_word_size_guess(self):
    #     if "32" in platform.machine() and "64" not in platform.machine():
    #         return "(32-bit)"
    #     elif "64" in platform.machine() and "32" not in platform.machine():
    #         return "(64-bit)"
    #     else:
    #         return ""

class MicrobitCommProjectDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title('Microbit無線通訊-教學程式')
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        text_font = font.Font(size=13, weight=font.NORMAL, family='Consolas')

        content = "【Microbit無線通訊-教學程式】 即時回饋 與 取號叫號模擬\n\n"
        content += "  簡要使用方式:\n"
        content += "    1.教師先在microbit上安裝「接收器程式」(脫機運行需儲存為main.py)\n"
        content += "    2.教師以電腦上python執行「伺服端程式」\n"
        content += "    3.指導學生撰寫Microbit控制器\n\n"
        content += "  開啟教學程式:\n"
        content += "    (檔案會儲存在目前的位置，若需改位置請「另存新檔」)\n"

        head_label = ttk.Label(
            main_frame, text=content, font=text_font
        )
        head_label.grid()

        # bg_frame = ttk.Frame(self) # gives proper color in aqua
        # bg_frame.grid()

        load_receiver_button = tk.Button(main_frame, 
                                    text="開啟 接收器程式(需在Microbit執行)", 
                                    command=self._load_receiver_file)
        load_receiver_button.grid()        
        
        sep_label = ttk.Label(
            main_frame, text="\n", 
        )
        sep_label.grid()

        load_server_button = tk.Button(main_frame, 
                                    text="開啟 無線通訊伺服端程式(需在電腦執行)", 
                                    command=self._load_server_file)
        load_server_button.grid()

        sep_label = ttk.Label(
            main_frame, text="\n", 
        )
        sep_label.grid()

        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._ok, True)

    def _ok(self, event=None):
        self.destroy()

    def _load_server_file(self):
        source_filename = 'microbit_radio_comm_pc_server.py'
        target_filename = '無線通訊教學_伺服端程式.py'
        self._load_file(source_filename, target_filename)

    def _load_receiver_file(self):
        source_filename = 'microbit_radio_comm_receiver.py'
        target_filename = '無線通訊教學_Microbit接受器.py'
        self._load_file(source_filename, target_filename)
    
    def _load_file(self, source_filename, target_filename):
        # determine cwd 
        notebook = get_workbench().get_editor_notebook()
        cwd = get_workbench().get_local_cwd()
        if (
            notebook.get_current_editor() is not None
            and notebook.get_current_editor().get_filename() is not None
        ):
            cwd = os.path.dirname(notebook.get_current_editor().get_filename())

        # prepare path
        source_file_path = Path(__file__).parent / 'projects' / source_filename
        target_file_path = Path(cwd) / target_filename

        # check file exists or not 
        if target_file_path.exists():
            question = '{}\n檔案已存在，是否要覆蓋'.format(str(target_file_path))
            answer = messagebox.askyesno('是否覆蓋檔案', question , master=get_workbench())
            if not answer:
                # don't copy
                return

        # copy file
        shutil.copyfile(source_file_path, target_file_path)
        notebook.show_file( str(target_file_path) )
        #print('ori :', source_file_path)
        #print('target :', target_file_path)

        # close dialog
        self.destroy()  
        

class AiassistSelectionAskDialog(CommonDialog):
    def __init__(self, master, selection):
        super().__init__(master)

        #main_frame = tk.Frame(self, bg=common.aiassist_tab.BG_COLOR)
        main_frame = tk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title('提問內容確認')
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._esc)


        # heading_font = tk.font.nametofont("TkHeadingFont").copy()
        # heading_font.configure(size=19, weight="bold")
        # heading_label = ttk.Label(
        #     main_frame, text="label", font=heading_font
        # )
        # heading_label.grid()

        # ask_chat_text = tk.Text(main_frame, 

        self.ask_chat_text = scrolledtext.ScrolledText(main_frame,                         
                                     font=common.postit_para_font,
                                     bg=common.aiassist_tab.ME_BG_COLOR, 
                                     fg=common.aiassist_tab.DARK_FG_COLOR,
                                     wrap=tk.NONE,
                                     width=50,
                                     height=10, 
                                     highlightthickness=common.aiassist_tab.BORDER_THICKNESS,
                                     highlightbackground=common.aiassist_tab.ME_BORDER_COLOR,
                                     highlightcolor=common.aiassist_tab.ME_BORDER_COLOR,
                                     relief="flat",          
                                     padx=10,
                                     pady=10)
        self.ask_chat_text.grid(ipadx=5, ipady=5, padx=10)
          
        self.ask_chat_text.delete(1.0, "end")
        self.ask_chat_text.insert("end", selection)
        self.ask_chat_text.config(state=tk.DISABLED)

        appendix_frame = tk.Frame(main_frame)
        appendix_frame.grid()

        appendix_label = tk.Label(appendix_frame, text='補充：')
        appendix_label.pack(side=tk.LEFT)

        self.ask_append_combo = ttk.Combobox(
                appendix_frame,
                width=30,
                #state="readonly",
                takefocus=0,
                font=common.postit_para_font, 
                justify=tk.CENTER,
                values=common.ask_append_list)
        self.ask_append_combo.current(0)
        self.ask_append_combo.pack(side=tk.LEFT, pady=12)
        

        ok_button = tk.Button(main_frame, text="送出提問 >>", command=self._send, default="active")
        ok_button.grid(pady=(0, 15))
        ok_button.focus_set()

        self.bind("<Return>", self._send, True)
        self.bind("<Escape>", self._esc, True)

    def _esc(self, event=None):
        self.destroy()


    def _send(self, event=None):
        ask_text_content = self.ask_chat_text.get("1.0", "end-1c")

        ask_append_content = self.ask_append_combo.get()
        if ask_append_content:
            ask_text_content = ask_text_content + '\n' + ask_append_content

        #print('-----------------')
        #print(ask_text_content)

        common.aiassist_tab.on_asking_btn(ask_content_from_editor_or_shell=ask_text_content)
        self.destroy()


def get_version():
    try: 
        with open(Path(__file__).parent / "VERSION" , encoding="ASCII") as fp:
            return fp.read().strip()
    except Exception:
        return "0.0.0"


def load_plugin():
    """postit plugin start point"""

    get_workbench().add_view(PythonPostitView, '便利貼', 'nw')

    #get_workbench().add_command("aboutPy4t", "help", '關於Py4t', get_version, group=62)

    def open_about(*args):
        show_dialog(AboutDialog(get_workbench()))

    def open_microbit_comm_projcet(*args):
        show_dialog(MicrobitCommProjectDialog(get_workbench()))

    

    get_workbench().add_command("aboutPy4t", "help", '關於Py4t', open_about, group=62)

    get_workbench().add_command("microbit_comm_project", "Py4t", 
                                'Microbit無線通訊-教學程式', 
                                open_microbit_comm_projcet, 
                                group=29)
    get_workbench().add_command("aboutPy4t", "Py4t", '關於Py4t (版本與網站連結)', open_about, group=30)



    get_workbench().add_command(command_id="ask_aiassist",
                                menu_name="edit",
                                command_label="向AI助理提問",
                                handler=_cmd_in_edit_ask_aiassist,
                                tester=_cmd_in_edit_ask_aiassist_tester,
                                group=4,
                                #default_sequence="<F2>"
                                )

    get_workbench().add_command(command_id="share_var_get",
                                menu_name="edit",
                                command_label="貼上目前變數",
                                handler=_cmd_share_var_get,
                                group=5,
                                #default_sequence="<F2>"
                                )

    get_workbench().add_command(command_id="share_var_add",
                                menu_name="edit",
                                command_label="把選取文字加到變數清單",
                                handler=_cmd_share_var_add,
                                group=5,
                                #default_sequence="<F2>"
                                )
    
    
        

    #print(get_shell().menu) # error. could be exec order

    #get_workbench().get_menu('postit','便利貼')




    #get_workbench().add_command("test", "便利貼", '測試', try_menu)
    #get_workbench().add_command("test2", "便利貼", '測試2', try_menu)

    #get_workbench().bind("BackendRestart", try_toplevel_response, True)

    #for test
    

    # get_workbench().add_command(command_id="try_get_option",
    #                                 menu_name="tools",
    #                                 command_label="測試thonny",
    #                                 handler=try_get_option,
    #                                 default_sequence="<F4>"
    #                                 )

def _cmd_share_var_get():
    postit = common.share_var_get_postit
    state = postit.postit_button.cget('state')
    if state in ('normal', 'active') :
        
        postit.determine_post_place_and_type(postit.postit_button)
        #print('here')
    else: # state is disable . do nothing
        #print('else')
        #print(self.postit_button.cget('state'))
        pass

def _cmd_share_var_add():
    postit = common.share_var_add_postit
    state = postit.postit_button.cget('state')
    if state in ('normal', 'active') :
        postit.on_mouse_click()
        #print('here')
    else: # state is disable . do nothing
        #print('else')
        #print(self.postit_button.cget('state'))
        pass    

def open_aiassist_selection_ask(selection):
        show_dialog(AiassistSelectionAskDialog(get_workbench(), selection))

def _cmd_in_edit_ask_aiassist_tester():
    # print('in edit tester ................')
    mode = common.postit_view.current_mode
    tab = common.postit_view.py4t_mode_current_tab

    if mode == 'py4t' and tab is common.aiassist_tab \
                and common.aiassist_tab.answer_queue.qsize() == 0 \
                and common.aiassist_tab.is_chatting is True  :
        # check if codeview text has selection 
        focus_widget = get_workbench().focus_get()
        if isinstance(focus_widget, CodeViewText):
            # cursor in editor
            editor_text = focus_widget 
            # has selection ?
            if editor_text.tag_ranges(tk.SEL):
                # make sure not select white space
                if editor_text.selection_get().strip():
                    common.editor_text = editor_text
                    return True
    else:
        return False


def _cmd_in_edit_ask_aiassist():
    selection = common.editor_text.selection_get()
    print('---------------------------')
    print('[in edit] 提問AI程式助理...')
    print(selection)
    open_aiassist_selection_ask(selection)


def _cmd_in_shell_ask_aiassist_tester():
    # print('in shell tester ................')
    mode = common.postit_view.current_mode
    tab = common.postit_view.py4t_mode_current_tab
        
    if mode == 'py4t' and tab is common.aiassist_tab \
                and common.aiassist_tab.answer_queue.qsize() == 0 \
                and common.aiassist_tab.is_chatting is True  :
        # check if codeview text has selection 
        focus_widget = get_workbench().focus_get()
        if isinstance(focus_widget, ShellText):
            # cursor in shell
            shell_text = focus_widget 
            # has selection ?
            if shell_text.tag_ranges(tk.SEL)  :
                # make sure not select white space
                if shell_text.selection_get().strip():
                    common.shell_text = shell_text
                    return True
    else:
        return False

def _cmd_in_shell_ask_aiassist():
    selection = common.shell_text.selection_get()
    print('---------------------------')
    print('[in shell] 提問AI程式助理...')
    print(selection)
    open_aiassist_selection_ask(selection)


# def try_runner():
#     #s = get_runner().get_state()
#     #print('runner state: ', s)
#     backend_name = get_workbench().get_option("run.backend_name")
#     ready = get_runner().ready_for_remote_file_operations(show_message=True)

#     from thonny.common import  InlineCommand
#     from thonny.languages import tr
#     if backend_name == 'microbit' and ready:
#         get_runner().send_command_and_wait(
#                 InlineCommand(
#                     "write_file",
#                     path="microbit模組.py",
#                     content_bytes=b'pass\n\xe6\x84\x9b\xe5\xbf\x83 = 5',
#                     editor_id=id(Tab),
#                     blocking=True,
#                     description=tr("Saving to microbit模組.py") ,
#                 ),
#                 dialog_title=tr("Saving"),
#             )
#     else:
#         print('f2: cannot write file')
    
# def try_notebook():
#     tab_notebook = common.postit_view.all_modes['py4t'].tab_notebook        
#     s = tab_notebook.select()
#     print(type(s), s)

# def try_toplevel_response(event):
#     #backend_name = get_runner().get_backend_proxy().backend_name
#     backend_name = get_workbench().get_option("run.backend_name")
#     print('got BackendRestart event. backend: ', backend_name)




# def try_set_option():
#     builtin_list = ['common', 'flow']
#     get_workbench().set_default('postit_tabs_view.builtin',builtin_list)
#     get_workbench().set_option('postit_tabs_view.builtin', ['a','b'])

# def try_get_option():
#     builtin_list = ['common', 'flow']
#     get_workbench().set_default('postit_tabs_view.builtin',builtin_list)
#     r = get_workbench().get_option('postit_tabs_view.builtin')
#     print(type(r), r)

