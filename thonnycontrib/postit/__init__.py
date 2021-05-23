import os 
import datetime
import webbrowser
from pathlib import Path
import json
from collections import OrderedDict

import tkinter as tk
import tkinter.font as font
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

from thonny import get_workbench, get_shell, get_runner 
from thonny.ui_utils import show_dialog, CommonDialog, create_tooltip



from thonny.common import ToplevelCommand, InlineCommand

from .base_postit import BasePostit
from .enclosed_postit import EnclosedPostit
from .dropdown_postit import DropdownPostit
from .common import ( CodeNTuple, common_images, TAB_DATA_PATH
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




#for test
from tkinter.messagebox import showinfo

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
        self.notebook_frame.pack(side=tk.TOP, fill=tk.BOTH)
        #self.notebook_frame.pack(side=tk.TOP, fill=tk.Y)
        #style = ttk.Style(self.interior)
        #style = ttk.Style(notebook_frame.interior)
        
        style = ttk.Style(self.notebook_frame)
        style.configure('lefttab.TNotebook', tabposition='wn')
        #style.configure('TNotebook.Tab', font=('Consolas','12') )

        #style.configure('lefttab.TNotebook', font=('Consolas', 16))
        #self.notebook = ttk.Notebook(self.interior, style='lefttab.TNotebook')
        #self.notebook = ttk.Notebook(notebook_frame.interior, style='lefttab.TNotebook')
        self.tab_notebook = ttk.Notebook(self.notebook_frame, style='lefttab.TNotebook')
        self.tab_notebook.pack(side='top',fill=tk.Y)

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

        self.tab_popup_menu.add_command(label="更多便利貼…",
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

        

        # #pick a color
        # color = self.pick_color()
        # self.fill_color = color['fill_color']
        # self.font_color = color['font_color']

        # #load image
        # if tab_type == 'more':
        #     abs_image_path =Path(__file__).parent/'images'/ 'more.png'
        # else:
        #     abs_image_path =Path(__file__).parent/'images'/color[tab_type+'_filename']
        # im = Image.open(abs_image_path)       
        # self.image = ImageTk.PhotoImage(im) 

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

        ans = messagebox.askokcancel('範例變數匯入',s)
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


class MoreTab:
    def __init__(self, notebook):
        im = Image.open(Path(__file__).parent / 'images' / 'more.png')       
        self.icon_image = ImageTk.PhotoImage(im) 

        # prepare  frame
        
        self.tab_frame = CustomVerticallyScrollableFrame(notebook)
        self.tab_frame.tab = self
        notebook.insert('end',self.tab_frame,
                          text = ' ',
                          image = self.icon_image,
                          compound=tk.CENTER,
                          #padding='3',
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

        button_font = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        self.para_button = tk.Button(tab.tab_frame.interior,
                command=self.on_button_pressed, 
                text=on_label, relief='flat', font=button_font)
        self.para_button.grid(sticky='w', padx=0, pady=12)
        #self.para_button.pack(side=tk.TOP, anchor='w', padx=2, pady=2)

        self.ori_bg_color = self.para_button.cget('bg')
        self.para_button.config(bg="#fefefe")

        self.para_frame = ttk.Frame(tab.tab_frame.interior,
                )
        self.para_frame.grid(sticky='we', padx=0, pady=0)
        #self.para_frame.pack(side=tk.TOP, padx=10, pady=8, anchor='w')

        # if not start_on:
        #     self.para_frame.grid_remove()

    def on_button_pressed(self):
        if self.para_visible :
            self.para_button.config(text=self.off_label, bg=self.ori_bg_color)
            self.para_visible = False
            self.para_frame.grid_remove()
            #self.para_frame.pack_forget()
        else:
            self.para_button.config(text=self.on_label, bg="#fefefe")
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

        im = Image.open(Path(__file__).parent / 'images' / 'vertical_spacer.png')       
        self.spacer_image= ImageTk.PhotoImage(im) 

        self.toolbar_init()
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
            #print(type(tab),tab)
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
                #self.all_modes['py4t'].notebook_frame.config(expand=False)
                self.all_modes['bit'].notebook_frame.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                self.all_modes['bit'].tab_notebook.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                #self.all_modes['bit'].notebook_frame.config(expand=True)
                #self.all_modes['py4t'].tab_notebook.pack_forget()
                self.current_mode = 'bit'
            else:
                
                #self.all_modes['py4t'].tab_notebook.pack()   
                self.all_modes['bit'].notebook_frame.pack_forget()
                self.all_modes['bit'].tab_notebook.pack_forget()
                #self.all_modes['bit'].notebook_frame.config(expand=False)
                self.all_modes['py4t'].notebook_frame.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                self.all_modes['py4t'].tab_notebook.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
                #self.all_modes['py4t'].notebook_frame.config(expand=True)
                #self.all_modes['bit'].tab_notebook.pack_forget()
                self.current_mode = 'py4t'              

            self.last_backend = backend_in_option

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
                    #print(mode_name + ' mode select first visible tab: ', tab.tab_name)
                    return

     
        
        # self.all_modes['bit'].tab_notebook.select(0)


    def more_tab_gui_init(self, mode_name):
        mode  = self.all_modes[mode_name]
        more_tab_frame = mode.more_tab.tab_frame
        
        # title label
        title_font = font.Font(size=12, weight=font.NORMAL, family='Consolas')
        tk.Label(more_tab_frame.interior, 
                text='更多便利貼', font=title_font,
        ).pack(side=tk.TOP, padx=5, pady=8, anchor='center')

        ttk.Separator(more_tab_frame.interior, orient=tk.HORIZONTAL 
                    ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
        

        #names_of_group = mode.groups.keys()
        #print(names_of_group)
        
        # group and tab buttons
        label_font = font.Font(size=12, weight=font.NORMAL, family='Consolas')
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
        self.label_font = font.Font(size=12, weight=font.NORMAL, family='Consolas')

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
              
            elif postit_data['postit_type'] == 'bit_install_lib_postit':
                self.build_bit_install_lib_postit(tab, postit_data)

        # end vertical spacer for end space scrolling
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

    def build_ttk_label(self, tab, postit_data):
        ttk.Label(tab.tab_frame.interior, 
            text=postit_data['text'],
            font=self.label_font,    
            compound=tk.LEFT, 
        ).grid( sticky='w',padx=0, pady=8)
        #).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

    def build_postit_title(self, tab, postit_data):
        ttk.Label(tab.tab_frame.interior, 
            text=tab.tab_title,
            font=self.label_font,
            image=tab.icon_image,
            compound='left',
        ).grid( padx=0, pady=8)

    def build_ttk_separator(self, tab, postit_data):
        ttk.Separator(tab.tab_frame.interior, orient=tk.HORIZONTAL
            ).grid(sticky='ew', padx=0, pady=5)
            #).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)

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
                long_note=i['long_note'] ))

        parent = tab.current_postit_para.para_frame
        DropdownPostit(parent, tab, code_list = temp_code_list,
            postfix_enter=postit_data['postfix_enter']).grid(sticky='w', padx=4, pady=5)                
            #postfix_enter=p['postfix_enter']).pack(side=tk.TOP, anchor='w', padx=5, pady=8)  

    def build_bit_install_lib_postit(self, tab, postit_data):
        logo_path = Path(__file__).parent / 'images' / 'install.png'
        im = Image.open(logo_path)       
        self.install_image = ImageTk.PhotoImage(im) 

        f = font.Font(size=12, weight=font.NORMAL, family='Consolas')

        def install_lib():
            ready = get_runner().ready_for_remote_file_operations(show_message=False)
            
            if not ready:
                messagebox.showwarning(
                    '連線問題',
                    '未連接microbit，請接上硬體並連線',
                    master=self,
                )
                return

            answer = messagebox.askyesno(
                '安裝模組',
                '是否在microbit上安裝模組？\n(至少需安裝一次，才可使用中文模組)',
                master=self,
            )

            if answer:
                lib_path = Path(__file__).parent / 'microbit_lib' / 'microbit模組.py'
                #lib_path = Path(__file__).parent / 'microbit_lib' / 'boot.py'
                with open(lib_path, 'rb') as f:
                    content_bytes = f.read()

                get_runner().send_command_and_wait(
                InlineCommand(
                    "write_file",
                    path="microbit模組.py",
                    #path="boot.py",
                    content_bytes=content_bytes,
                    editor_id=id(tab),
                    blocking=True,
                    description="安裝boot.py模組",
                ),
                dialog_title="安裝...",
            )
            else:
                return



        tk.Button(tab.tab_frame.interior,
            relief='solid', 
            borderwidth=1,
            text=postit_data['postit_label'],
            #fg='#333333',
            #fg=tab.font_color, 
            #bg=tab.fill_color,
            #bg='#aaaaff',
            justify='left',
            font=f,  
            image=self.install_image,  
            compound=tk.LEFT, 
            padx=0,
            pady=0,
            command=install_lib,
        ).grid( sticky='e',padx=20, pady=8)

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









    #     ttk.Separator(common_postit_tabs['builtin'].frame.interior, orient=tk.HORIZONTAL
    #         ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     ttk.Label(common_postit_tabs['builtin'].frame.interior, 
    #                 #text='='*6 +' 【 條件分支 】 '+'='*6,
    #                 text=' >> 隨機模組random',
    #                 font=f,    
    #                 compound=tk.LEFT, 
    #             ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')        

    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='匯入隨機模組 random',
    #             code='import random as 隨機',
    #             code_display='import random as 隨機',
    #             note='匯入隨機模組 random',
    #             long_note=True))
    #     DropdownPostit(tab_name='builtin', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='隨機挑個整數(範圍內) random.randint',
    #             code='隨機.randint(1,10)',
    #             code_display='隨機.randint(1,10)',
    #             note='隨機挑個整數(範圍內)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='隨機項目 choice',
    #             code='隨機.choice([3,5,9])',
    #             code_display='隨機.choice([3,5,9])',
    #             note='隨機挑個項目',
    #             long_note=True))
    #     DropdownPostit(tab_name='builtin', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    #     ttk.Separator(common_postit_tabs['builtin'].frame.interior, orient=tk.HORIZONTAL
    #         ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     ttk.Label(common_postit_tabs['builtin'].frame.interior, 
    #                 #text='='*6 +' 【 條件分支 】 '+'='*6,
    #                 text=' >> 時間模組time',
    #                 font=f,    
    #                 compound=tk.LEFT, 
    #             ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='匯入時間模組time',
    #             code='import time as 時間',
    #             code_display='import time as 時間',
    #             note='匯入時間模組time',
    #             long_note=True))
    #     # temp_code_list.append(CodeNTuple(
    #     #         menu_display='從時間模組匯入sleep',
    #     #         code='from time import sleep',
    #     #         code_display='from time import sleep',
    #     #         note='從時間模組匯入sleep',
    #     #         long_note=True))
    #     DropdownPostit(tab_name='builtin', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='時間(累計秒數) time',
    #             code='時間.time()',
    #             code_display='時間.time()',
    #             note='時間(累計秒數)',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='暫停幾秒(睡眠) sleep',
    #             code='時間.sleep(2)',
    #             code_display='時間.sleep(2)',
    #             note='暫停幾秒(睡眠)',
    #             long_note=False))
    #     DropdownPostit(tab_name='builtin', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    #     ttk.Separator(common_postit_tabs['builtin'].frame.interior, orient=tk.HORIZONTAL
    #         ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     ttk.Label(common_postit_tabs['builtin'].frame.interior, 
    #                 #text='='*6 +' 【 條件分支 】 '+'='*6,
    #                 text=' >> 數學模組math',
    #                 font=f,    
    #                 compound=tk.LEFT, 
    #             ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='匯入數學模組math',
    #             code='import math as 數學',
    #             code_display='import math as 數學',
    #             note='匯入數學模組math',
    #             long_note=True))
    #     # temp_code_list.append(CodeNTuple(
    #     #         menu_display='從時間模組匯入sleep',
    #     #         code='from time import sleep',
    #     #         code_display='from time import sleep',
    #     #         note='從時間模組匯入sleep',
    #     #         long_note=True))
    #     DropdownPostit(tab_name='builtin', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='最大公因數 gcd',
    #             code='數學.gcd(8, 12)',
    #             code_display='數學.gcd(8, 12)',
    #             note='最大公因數',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='圓周率 pi',
    #             code='數學.pi',
    #             code_display='數學.pi',
    #             note='圓周率 pi',
    #             long_note=False))
    #     # temp_code_list.append(CodeNTuple(
    #     #         menu_display='最小公倍數 lcm',
    #     #         code='數學.lcm(8, 12)',
    #     #         code_display='數學.lcm(8, 12)',
    #     #         note='最小公倍數',
    #     #         long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='開平方根 sqrt',
    #             code='數學.sqrt(9)',
    #             code_display='數學.sqrt(9)',
    #             note='開平方根',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='三角函數 sin',
    #             code='數學.sin(數學.pi / 2)',
    #             code_display='數學.sin(數學.pi / 2)',
    #             note='三角函數 sin',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='三角函數 cos',
    #             code='數學.cos(數學.pi / 2)',
    #             code_display='數學.cos(數學.pi / 2)',
    #             note='三角函數 cos',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='角度轉弧度 radians',
    #             code='數學.radians(180)',
    #             code_display='數學.radians(180)',
    #             note='角度轉弧度 radians',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='弧度轉角度 degrees',
    #             code='數學.degrees(數學.pi)',
    #             code_display='數學.degrees(數學.pi)',
    #             note='弧度轉角度 degrees',
    #             long_note=True))
    #     DropdownPostit(tab_name='builtin', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)
















    # def threed_tab_init(self):
    #     # title and setup tool
    #     tab = common_postit_tabs['threed']
    #     #example_vars = ['長','角度','邊','小海龜','Turtle','海龜模組'] 
    #     example_vars = ['x','y','z','物體','物體父' ,'物體母','座標','角度' ] 
    #     tab.popup_init(example_vars)

    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     label =ttk.Label(common_postit_tabs['threed'].frame.interior, 
    #             text='【模擬3D】', 
    #             image= common_images['gear'],
    #             font=f,
    #             compound=tk.RIGHT,
    #             )                
    #     label.pack(side=tk.TOP, padx=5, pady=8, anchor='w')
    #     label.bind("<Button-1>", common_postit_tabs['threed'].popup)



    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定縮放x ',
    #             code="物體.縮放x = 1",
    #             code_display="物體.縮放x = 1",
    #             note='設定縮放x ',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定縮放y ',
    #             code="物體.縮放y = 1",
    #             code_display="物體.縮放y = 1",
    #             note='設定縮放y ',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定縮放z ',
    #             code="物體.縮放z = 1",
    #             code_display="物體.縮放z = 1",
    #             note='設定縮放z ',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定縮放 (3軸同時)',
    #             code="物體.縮放 = 1, 1, 1",
    #             code_display="物體.縮放 = 1, 1, 1",
    #             note='設定縮放 (3軸同時)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定全域縮放 (3軸同時)',
    #             code="物體.全域縮放 = 1, 1, 1",
    #             code_display="物體.全域縮放 = 1, 1, 1",
    #             note='設定全域縮放 (3軸同時)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定縮放動畫(持續)',
    #             code="物體.縮放動畫([2,1,1], 持續=1)",
    #             code_display="物體.縮放動畫([2,1,1], 持續=1)",
    #             note='設定縮放動畫',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定縮放動畫(延遲與持續)',
    #             code="比例 = 2,1,1\n物體.縮放動畫(比例, 延遲=0, 持續=1)",
    #             code_display="比例 = 2,1,1\n物體.縮放動畫(比例, 延遲=0, 持續=1)",
    #             note='設定縮放動畫(延遲與持續)',
    #             long_note=True))
    #     DropdownPostit(tab_name='threed', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定旋轉x (x軸順逆時針)',
    #             code="物體.旋轉x = 0",
    #             code_display="物體.旋轉x = 0",
    #             note='設定旋轉x (x軸順逆時針)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定旋轉y (y軸順逆時針)',
    #             code="物體.旋轉y = 0",
    #             code_display="物體.旋轉y = 0",
    #             note='設定旋轉y (y軸順逆時針)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定旋轉z (z軸順逆時針)',
    #             code="物體.旋轉z = 0",
    #             code_display="物體.旋轉z = 0",
    #             note='設定旋轉z (z軸順逆時針)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定旋轉 (3軸)',
    #             code="物體.旋轉 = 0, 0, 0",
    #             code_display="物體.旋轉 = 0, 0, 0",
    #             note='設定旋轉 (3軸)',
    #             long_note=True))
    #     # temp_code_list.append(CodeNTuple(
    #     #         menu_display='設定全域旋轉x (x軸順逆時針)',
    #     #         code="物體.全域旋轉x = 0",
    #     #         code_display="物體.全域旋轉x = 0",
    #     #         note='設定全域旋轉x (x軸順逆時針)',
    #     #         long_note=True))
    #     # temp_code_list.append(CodeNTuple(
    #     #         menu_display='設定全域旋轉y (y軸順逆時針)',
    #     #         code="物體.全域旋轉y = 0",
    #     #         code_display="物體.全域旋轉y = 0",
    #     #         note='設定全域旋轉y (y軸順逆時針)',
    #     #         long_note=True))
    #     # temp_code_list.append(CodeNTuple(
    #     #         menu_display='設定全域旋轉z (z軸順逆時針)',
    #     #         code="物體.全域旋轉z = 0",
    #     #         code_display="物體.全域旋轉z = 0",
    #     #         note='設定全域旋轉z (z軸順逆時針)',
    #     #         long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定全域旋轉 (3軸)',
    #             code="物體.全域旋轉 = 0, 0, 0",
    #             code_display="物體.全域旋轉 = 0, 0, 0",
    #             note='設定全域旋轉 (3軸)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定旋轉動畫(持續)',
    #             code="物體.旋轉動畫([90,0,0], 持續=1)",
    #             code_display="物體.旋轉動畫([2,0,0], 持續=1)",
    #             note='設定旋轉動畫',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='設定旋轉動畫(延遲與持續)',
    #             code="角度 = 90,0,0\n物體.旋轉動畫(角度, 延遲=0, 持續=1)",
    #             code_display="角度 = 90,0,0\n物體.旋轉動畫(角度, 延遲=0, 持續=1)",
    #             note='設定旋轉動畫(延遲與持續)',
    #             long_note=True))
    #     DropdownPostit(tab_name='threed', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)




    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='匯入pyautogui模組',
    #             code='import pyautogui as 自動',
    #             code_display='import pyautogui as 自動',
    #             note='匯入pyautogui模組',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    #     # separator and note
    #     ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
    #         ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
    #                 text=' >> 設定與資訊',
    #                 font=f,   
    #                 compound=tk.LEFT, 
    #             ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')


    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='螢幕大小 size',
    #             code='自動.size()',
    #             code_display='自動.size()',
    #             note='螢幕大小',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='查詢滑鼠位置 position',
    #             code='自動.position()',
    #             code_display='自動.position()',
    #             note='查詢滑鼠位置',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='在螢幕內嗎 onScreen',
    #             code='自動.onScreen(100, 100)',
    #             code_display='自動.onScreen(100, 100)',
    #             note='在螢幕內嗎',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='每次暫停(秒) PAUSE',
    #             code='自動.PAUSE = 1',
    #             code_display='自動.PAUSE = 1',
    #             note='每次暫停(秒)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='失效安全  FAILSAFE',
    #             code='自動.FAILSAFE = True',
    #             code_display='自動.FAILSAFE = True',
    #             note='失效安全(移到螢幕左上角)',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    #     # separator and note
    #     ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
    #         ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
    #                 text=' >> 滑鼠操作',
    #                 font=f,   
    #                 compound=tk.LEFT, 
    #             ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

 
    #     # dropdown list postit
    #     temp_code_list = [] 
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='移動滑鼠(到座標)',
    #             code='自動.moveTo(100, 100, 2)',
    #             code_display='自動.moveTo(100, 100, 1)',
    #             note='移動滑鼠(x座標, y座標, 幾秒)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='移動滑鼠(距離)',
    #             code='自動.moveRel(0, 50, 1)',
    #             code_display='自動.moveRel(0, 50, 1)',
    #             note='移動滑鼠(x距離, y距離, 幾秒)',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)                

 
    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='點擊滑鼠(滑鼠按鍵)',
    #             code="自動.click(button='left')",
    #             code_display="自動.click(button='left')",
    #             note='點擊滑鼠(滑鼠按鍵)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='拖曳滑鼠(到座標)',
    #             code='自動.dragTo(100, 100, 2)',
    #             code_display='自動.dragTo(100, 100, 2)',
    #             note='拖曳滑鼠(x座標, y座標, 幾秒)',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='拖曳滑鼠(距離)',
    #             code='自動.dragRel(0, 50, 1)',
    #             code_display='自動.dragRel(0, 50, 1)',
    #             note='拖曳滑鼠(x距離, y距離, 幾秒)',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    #     # separator and note
    #     ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
    #         ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
    #                 text=' >> 鍵盤操作',
    #                 font=f,   
    #                 compound=tk.LEFT, 
    #             ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='按鍵 perss',
    #             code="自動.press('space')",
    #             code_display="自動.press('space')",
    #             note='按鍵',
    #             long_note=True))

    #     temp_code_list.append(CodeNTuple(
    #             menu_display='按著鍵 keyDown',
    #             code="自動.keyDown('space')",
    #             code_display="自動.keyDown('space')",
    #             note='按著鍵',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='放開鍵 keyUp',
    #             code="自動.keyUp('space')",
    #             code_display="自動.keyUp('space')",
    #             note='放開鍵',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='組合鍵 hotkey',
    #             code="自動.hotkey('ctrl','v')",
    #             code_display="自動.hotkey('ctrl','v')",
    #             note='組合鍵',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display="空白鍵 space",
    #             code="'space'",
    #             code_display="'space'",
    #             note='空白鍵',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display="輸入鍵 enter",
    #             code="'enter'",
    #             code_display="'enter'",
    #             note='空白鍵',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display="控制鍵 ctrl",
    #             code="'ctrl'",
    #             code_display="'ctrl'",
    #             note='空白鍵',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display="shift鍵 shift",
    #             code="'shift'",
    #             code_display="'shift'",
    #             note='shift鍵',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display="字母鍵 a",
    #             code="'a'",
    #             code_display="'a'",
    #             note='空白鍵',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display="向上鍵 up",
    #             code="'up'",
    #             code_display="'up'",
    #             note='向上鍵',
    #             long_note=False))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='鍵盤列表 KEYBOARD_KEYS',
    #             code='自動.KEYBOARD_KEYS',
    #             code_display='自動.KEYBOARD_KEYS',
    #             note='鍵盤列表',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

    #     # separator and note
    #     ttk.Separator(common_postit_tabs['auto'].frame.interior, orient=tk.HORIZONTAL
    #         ).pack(side=tk.TOP, fill=tk.X, padx=0, pady=10)
    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     label =ttk.Label(common_postit_tabs['auto'].frame.interior, 
    #             text='【pyperclip模組】', 
    #             #image= common_images['gear'],
    #             font=f,
    #             compound=tk.RIGHT,
    #             )                
    #     label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')



    #     ttk.Label(common_postit_tabs['auto'].frame.interior, 
                    
    #                 text=' >> 剪貼簿',
    #                 font=f,   
    #                 compound=tk.LEFT, 
    #             ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='匯入pyperclip模組',
    #             code='import pyperclip as 剪貼簿',
    #             code_display='import pyperclip as 剪貼簿',
    #             note='匯入pyperclip模組',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    #     # dropdown list postit
    #     temp_code_list = []
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='字串複製到剪貼簿 copy',
    #             code='剪貼簿.copy("你好")',
    #             code_display='剪貼簿.copy("你好")',
    #             note='字串複製到剪貼簿',
    #             long_note=True))
    #     temp_code_list.append(CodeNTuple(
    #             menu_display='從剪貼簿傳回字串 paste',
    #             code='文字 = 剪貼簿.paste()',
    #             code_display='文字 = 剪貼簿.paste()',
    #             note='從剪貼簿傳回字串',
    #             long_note=True))
    #     DropdownPostit(tab_name='auto', code_list = temp_code_list,
    #         postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


    # def numpy_tab_init(self):
    #      # title and setup tool
    #     tab = common_postit_tabs['numpy']
    #     example_vars = ['陣列','行1','行2','列1','列2'] 
    #     tab.popup_init(example_vars)

    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     label =ttk.Label(common_postit_tabs['numpy'].frame.interior, 
    #             text='【多維陣列numpy】', 
    #             image= common_images['gear'],
    #             font=f,
    #             compound=tk.RIGHT,
    #             )                
    #     label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
    #     label.bind("<Button-1>", common_postit_tabs['numpy'].popup)      


    # def cv_tab_init(self):
    #     # title and setup tool
    #     tab = common_postit_tabs['cv']
    #     example_vars = ['陣列','行1','行2','列1','列2'] 
    #     tab.popup_init(example_vars)

    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     label =ttk.Label(common_postit_tabs['cv'].frame.interior, 
    #             text='【電腦視覺cv】', 
    #             image= common_images['gear'],
    #             font=f,
    #             compound=tk.RIGHT,
    #             )                
    #     label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
    #     label.bind("<Button-1>", common_postit_tabs['cv'].popup)   






    # def speech_tab_init(self):
    #     # title and setup tool
    #     tab = common_postit_tabs['speech']
    #     example_vars = [''] 
    #     tab.popup_init(example_vars)

    #     f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
    #     label =ttk.Label(common_postit_tabs['speech'].frame.interior, 
    #             text='【語音】', 
    #             image= common_images['gear'],
    #             font=f,
    #             compound=tk.RIGHT,
    #             )                
    #     label.pack(side=tk.TOP, padx=5, pady=8,anchor='w')
    #     label.bind("<Button-1>", common_postit_tabs['speech'].popup)   






        # #separator and note
        # ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
        #     ).pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)
        # f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        # ttk.Label(common_postit_tabs['flow'].frame.interior, 
        #             #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
        #             text=' >> 例外(錯誤)處理',
        #             font=f,    
        #             compound=tk.LEFT, 
        #         ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # # dropdown list postit
        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='捕捉例外(錯誤)',
        #         code='try:\npass\nexcept Exception:\npass',
        #         code_display='try:\n    pass\nexcept Exception:\n    pass',
        #         note='測試:\n        測試區塊\n例外發生:\n        錯誤處理區塊',
        #         long_note=True))
        # DropdownPostit(tab_name='flow', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)



        # #separator and note
        # ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
        #     ).pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)
        # f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        # ttk.Label(common_postit_tabs['flow'].frame.interior, 
        #             #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
        #             text=' >> 物件類別',
        #             font=f,    
        #             compound=tk.LEFT, 
        #         ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # # dropdown list postit
        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='定義新類別',
        #         code='class 類別:\n屬性 = 1\ndef 方法(self):\npass',
        #         code_display='class 類別:\n    屬性 = 1\n    def 方法(self):\n    pass',
        #         note='定義新類別',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='繼承類別',
        #         code='class 子類別(父母類別):\n屬性 = 1\ndef 方法(self):\npass',
        #         code_display='class 子類別(父母類別):\n    屬性 = 1\n    def 方法(self):\n    pass',
        #         note='繼承類別',
        #         long_note=True))                
        # DropdownPostit(tab_name='flow', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)


        # #separator and note
        # ttk.Separator(common_postit_tabs['flow'].frame.interior, orient=tk.HORIZONTAL
        #     ).pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)
        # f = font.Font(size=11, weight=font.NORMAL, family='Consolas')
        # ttk.Label(common_postit_tabs['flow'].frame.interior, 
        #             #text='='*6 +' 【 條 件 分 支 】 '+'='*6,
        #             text=' >> 有限狀態機',
        #             font=f,    
        #             compound=tk.LEFT, 
        #         ).pack(side=tk.TOP, padx=5, pady=8, anchor='w')

        # # dropdown list postit
        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='匯入狀態機模組',
        #         code='from transitions import Machine as 狀態機',
        #         code_display='from transitions import Machine as 狀態機',
        #         note='匯入狀態機模組',
        #         long_note=True))
        # DropdownPostit(tab_name='flow', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # # dropdown list postit
        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='階段清單',
        #         code="階段清單 = ['開頭','關卡','結尾']",
        #         code_display="階段清單 = ['開頭','關卡','結尾']",
        #         note='階段清單',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='程式狀態類別',
        #         code="class 程式狀態(狀態機):\ndef on_enter_開頭(self):\nprint('進入 開頭階段')",
        #         code_display="class 程式狀態(狀態機)):\n    def on_enter_開頭(self):\n        print('進入 開頭')",
        #         note='繼承類別',
        #         long_note=True)) 
        # temp_code_list.append(CodeNTuple(
        #         menu_display='程式狀態方法(離開)',
        #         code="    def on_exit_開頭(self):\nprint('離開 開頭階段')",
        #         code_display="def on_exit_開頭(self):\n    print('離開 開頭階段')",
        #         note='程式狀態方法(離開)',
        #         long_note=True))  
        # temp_code_list.append(CodeNTuple(
        #         menu_display='主流程物件',
        #         code="主流程 = 程式狀態(states=階段清單, initial='開頭')",
        #         code_display="主流程 = 程式狀態(states=階段清單, initial='開頭')",
        #         note='主流程物件',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='依序轉換',
        #         code="主流程.add_ordered_transitions()",
        #         code_display="主流程.add_ordered_transitions()",
        #         note='依序轉換',
        #         long_note=True))    
        # DropdownPostit(tab_name='flow', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)

        # # dropdown list postit
        # temp_code_list = []
        # temp_code_list.append(CodeNTuple(
        #         menu_display='目前階段',
        #         code='主流程.state',
        #         code_display='主流程.state',
        #         note='目前階段',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='跳到階段',
        #         code='主流程.to_開頭()',
        #         code_display='主流程.to_開頭()',
        #         note='跳到階段',
        #         long_note=True))
        # temp_code_list.append(CodeNTuple(
        #         menu_display='下一階段(依序)',
        #         code='主流程.next_state()',
        #         code_display='主流程.next_state()',
        #         note='下一階段(依序)',
        #         long_note=True))
        # DropdownPostit(tab_name='flow', code_list = temp_code_list,
        #     postfix_enter=False).pack(side=tk.TOP, anchor='w', padx=2, pady=8)





    def toolbar_init(self):

        # var toolbar
        #self.var_toolbar = ttk.Frame(self.interior)
        self.code_toolbar = ttk.Frame(self)
        self.code_toolbar.pack(side=tk.TOP, fill=tk.X)



        common.share_var_get_postit = VariableFetchToolPostit(
                self.code_toolbar, tool_name='variable_get')
        #common.share_var_assign_postit = VariableFetchToolPostit(
        #        self.var_toolbar, tool_name='variable_assign')
        common.share_vars_postit = VariableMenuPostit(self.code_toolbar)

        comment = CommentToolPostit(self.code_toolbar)
        comment.pack(side=tk.LEFT,padx=8, pady=3)
        create_tooltip(comment, '註解(右鍵選擇)')

        common.share_var_add_postit = VariableAddToolPostit(self.code_toolbar)
        common.share_var_add_postit.pack(side=tk.LEFT,padx=0, pady=3)
        create_tooltip(common.share_var_add_postit, '加入變數')

        share_var = common.share_vars_postit
        share_var.pack(side=tk.LEFT,padx=0, pady=3)
        create_tooltip(share_var, '變數清單(右鍵選擇)')
        
        var_get = common.share_var_get_postit
        var_get.pack(side=tk.LEFT,padx=0, pady=3)
        create_tooltip(var_get, '貼上變數')
        #common.share_var_assign_postit.pack(side=tk.LEFT,padx=2, pady=3)
        
        symbol = SymbolToolPostit(self.code_toolbar)
        symbol.pack(side=tk.LEFT,padx=8, pady=3)
        create_tooltip(symbol, '名稱與符號(右鍵選擇)')

        # edit_toolbar
        #self.edit_toolbar = ttk.Frame(self.interior)
        self.edit_toolbar = ttk.Frame(self)
        self.edit_toolbar.pack(side=tk.TOP, fill=tk.X)

        pilcrow_postit = PilcrowToolPostit(self.edit_toolbar)
        pilcrow_postit.pack(side=tk.LEFT,padx=1, pady=3)
        create_tooltip(pilcrow_postit, '顯示空白鍵與換行')
        
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
            if not isinstance(tab, MoreTab) and not tab.para_start_on_done and tab.loaded:
                tab.do_para_start_on()
                


        """restore last focus widget"""
        if self.last_focus:
            self.last_focus.focus_set()
            self.last_focus = None


class CustomVerticallyScrollableFrame(ttk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.interior = ttk.Frame(self.canvas)
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
            main_frame, text="Py4t " + get_version(), font=heading_font
        )
        heading_label.grid()

        text_font = font.Font(size=14, weight=font.NORMAL, family='Consolas')

        url = "https://beardad1975.github.io/py4t/"
        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label = ttk.Label(
            main_frame, text=url, style="Url.TLabel", cursor="hand2", font=url_font
        )
        url_label.grid()
        url_label.bind("<Button-1>", lambda _: webbrowser.open(url))



        credits_label = ttk.Label(
            main_frame,
            font = text_font,
            text=
                "\nPy4t是個由中小學教師發起的計畫\n"
                + "採用多個開放原始碼套件\n"
                + "整合成簡易的python程式環境\n"
                + "\n"
                + "目的是搭一座學習之橋\n"
                + "從Scratch到Python\n"
                + "讓青少年學習程式、體驗科技\n"
                + "\n"
                + "【感謝】\n"
                + "桃園市建國自造教育及科技中心\n"
                + "新竹縣博愛自造教育及科技中心\n"
                + "桃園市南門國民小學\n"
                + "Python、Thonny及各個函式庫的開發者\n"
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

    def get_os_word_size_guess(self):
        if "32" in platform.machine() and "64" not in platform.machine():
            return "(32-bit)"
        elif "64" in platform.machine() and "32" not in platform.machine():
            return "(64-bit)"
        else:
            return ""

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

    get_workbench().add_command("aboutPy4t", "help", '關於Py4t', open_about, group=62)


    get_workbench().add_command(command_id="share_var_get",
                                menu_name="edit",
                                command_label="貼上變數",
                                handler=_cmd_share_var_get,
                                group=5,
                                #default_sequence="<F2>"
                                )

    get_workbench().add_command(command_id="share_var_add",
                                menu_name="edit",
                                command_label="加入變數",
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

