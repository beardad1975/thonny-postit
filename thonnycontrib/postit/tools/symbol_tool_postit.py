import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell



from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

from ..common import common_images

from .. import common

class SymbolWidget(ttk.Frame):

    def widget_init(self, master):
        # don't need to handle tab
        
        #self.tool_image = common_images[tool_name]

        ttk.Frame.__init__(self, master)
        #f = font.Font(size=10, weight=font.NORMAL, family='Consolas')        
        self.postit_button = tk.Button(self,  
                                        relief='raised',
                                        borderwidth=1,
                                        text = '*',
                                        font = common.symbol_font,
                                        #fg=self.tab.font_color, 
                                        height=24,
                                        #width=40,
                                        #justify='left', 
                                        #font=f,
                                        compound='center',
                                        image=common_images['empty'],
                                        padx=0,
                                        pady=0, 
                                        bg='#bcfabb',
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')

class SymbolCodeMixin:
    def code_init(self, code, code_display):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.code = code
        self.code_display = code_display
        self.note = ''

        self.enclosed_symbols = ('()','[]','{}',"''",'""','r""',"r''")

        self.postit_button.config(text=code_display)
            
            #self.update_postit_code()

    def update_postit_code(self):
        pass


class SymbolToolPostMixin:

    def on_mouse_drag(self, event):
        ###print('drag ...')
        #create drag window
        if not self.drag_window: 
            self.create_drag_window()
            self.postit_button.config(cursor='hand2')

        x_root, y_root = event.x_root, event.y_root
        
        self.drag_window.geometry('+{}+{}'.format(x_root-10, y_root+10))

        #change insert over editor or shell (but not postit button)
        
        hover_widget = event.widget.winfo_containing(x_root, y_root)
        
        if isinstance(hover_widget, CodeViewText):
            # hover editor
            editor_text = hover_widget
            relative_x = x_root - editor_text.winfo_rootx()
            relative_y =  y_root - editor_text.winfo_rooty()
            mouse_index = editor_text.index(f"@{relative_x},{relative_y}")
            # set cursor in editor
            editor_text.focus_set()
            editor_text.mark_set(tk.INSERT, mouse_index)

            if editor_text.tag_ranges(tk.SEL):
                #check darg hover selection
                if editor_text.compare(tk.SEL_FIRST, "<=", mouse_index) and \
                    editor_text.compare(mouse_index, "<=", tk.SEL_LAST):
                    #print(self.code, self.code_display)
                    if self.code in self.enclosed_symbols or self.code[-2:] == '()': 
                        self.drag_hover_selection = True
                        self.drag_button.config(text='【包含】'+self.hover_text_backup)
                    else:
                        self.drag_hover_selection = True
                        self.drag_button.config(text='【取代】'+self.hover_text_backup)
                    
                else:
                    self.drag_hover_selection = False
                    self.drag_button.config(text=self.hover_text_backup)
                    
                    
        elif isinstance(hover_widget, ShellText):
            # hover shell 
            shell_text = hover_widget
            relative_x = x_root - shell_text.winfo_rootx()
            relative_y = y_root - shell_text.winfo_rooty()
            # set cursor in shell
            shell_text.focus_set()
            mouse_index = shell_text.index(f"@{relative_x},{relative_y}")
            input_start_index = shell_text.index('input_start')
            if shell_text.compare(mouse_index, '>=', input_start_index):
                shell_text.mark_set(tk.INSERT, mouse_index)

                if shell_text.tag_ranges(tk.SEL):
                    #check darg hover selection
                    if shell_text.compare(tk.SEL_FIRST, "<=", mouse_index) and \
                        shell_text.compare(mouse_index, "<=", tk.SEL_LAST):
                        if self.code in self.enclosed_symbols or self.code[-2:] == '()': 
                            self.drag_hover_selection = True
                            self.drag_button.config(text='【包含】'+self.hover_text_backup)
                        else:
                            self.drag_hover_selection = True
                            self.drag_button.config(text='【取代】'+self.hover_text_backup)
                        
                    else:
                        self.drag_hover_selection = False
                        self.drag_button.config(text=self.hover_text_backup)


    def create_drag_window(self):
            self.drag_window = tk.Toplevel()
            # clone postit_button in drag window
            image = self.postit_button.cget('image')
            compound = self.postit_button.cget('compound')
            font = self.postit_button.cget('font')
            bg = self.postit_button.cget('bg')
            fg = self.postit_button.cget('fg')
            text = '  ' + self.postit_button.cget('text')
            self.hover_text_backup = text
            justify = self.postit_button.cget('justify')
            self.drag_button = tk.Button(self.drag_window, text=text, bg=bg, 
                        fg=fg,font=font, compound=compound, image=image,
                        relief='solid', justify=justify, bd=0 )
            self.drag_button.pack()
            self.drag_window.overrideredirect(True)
            self.drag_window.attributes('-topmost', 'true')


    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            self.content_insert(editor_text, self.code)
            if self.var_postfix_enter.get():
                editor_text.event_generate("<Return>")

        elif pressing and selecting:
            if self.code in self.enclosed_symbols:
                # handle enclosed
                head = self.code[0] # ex: (
                tail = self.code[1] # ex: )

                editor_text.insert(tk.SEL_FIRST, head)
                stored_index = editor_text.index(tk.SEL_LAST)
                editor_text.insert(tk.SEL_LAST, tail)
                #keep insert cursor in the stored_index 
                editor_text.mark_set(tk.INSERT, stored_index)
                editor_text.tag_remove(tk.SEL,'0.0', tk.END)
            elif self.code[-2:] == '()':
                # builtin function
                head = self.code[:-1] 
                tail = self.code[-1] 

                editor_text.insert(tk.SEL_FIRST, head)
                stored_index = editor_text.index(tk.SEL_LAST)
                editor_text.insert(tk.SEL_LAST, tail)
                #keep insert cursor in the stored_index 
                editor_text.mark_set(tk.INSERT, stored_index)
                editor_text.tag_remove(tk.SEL,'0.0', tk.END)                

            else:
                editor_text.event_generate("<BackSpace>")
                self.content_insert(editor_text, self.code)
                if self.var_postfix_enter.get():
                    editor_text.event_generate("<Return>")

        elif dragging and not hovering:
            # cancel selection
 
            if editor_text.tag_ranges(tk.SEL):
                ori_sel_first = editor_text.index(tk.SEL_FIRST)
                ori_sel_last = editor_text.index(tk.SEL_LAST)
                editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
            
            self.content_insert(editor_text, self.code)
            if self.var_postfix_enter.get():
                editor_text.event_generate("<Return>")



        elif dragging and hovering:
            if self.code in self.enclosed_symbols:
                # handle enclosed
                head = self.code[0] # ex: (
                tail = self.code[1] # ex: )

                editor_text.insert(tk.SEL_FIRST, head)
                stored_index = editor_text.index(tk.SEL_LAST)
                editor_text.insert(tk.SEL_LAST, tail)
                #keep insert cursor in the stored_index 
                editor_text.mark_set(tk.INSERT, stored_index)
                editor_text.tag_remove(tk.SEL,'0.0', tk.END)

            elif self.code[-2:] == '()':
                # builtin function
                head = self.code[:-1] 
                tail = self.code[-1] 

                editor_text.insert(tk.SEL_FIRST, head)
                stored_index = editor_text.index(tk.SEL_LAST)
                editor_text.insert(tk.SEL_LAST, tail)
                #keep insert cursor in the stored_index 
                editor_text.mark_set(tk.INSERT, stored_index)
                editor_text.tag_remove(tk.SEL,'0.0', tk.END)

            else:
                editor_text.event_generate("<BackSpace>")
                self.content_insert(editor_text, self.code)
                if self.var_postfix_enter.get():
                    editor_text.event_generate("<Return>")

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        if pressing and not selecting:
            if shell_text.compare(tk.INSERT, '>=', 'input_start'):
                # cursor after input_start
                self.content_insert(shell_text, self.code)
                if self.var_postfix_enter.get():
                    shell_text.event_generate("<Return>")
            else: # cursor before input_start
                # append last line
                shell_text.mark_set(tk.INSERT, 'end-1c')
                self.content_insert(shell_text, self.code)
                if self.var_postfix_enter.get():
                    shell_text.event_generate("<Return>")
        elif pressing and selecting:
            if shell_text.compare(tk.SEL_LAST, '>', 'input_start'):
                if shell_text.compare(tk.SEL_FIRST, '>=', 'input_start'):
                    if self.code in self.enclosed_symbols:
                        # handle enclosed
                        head = self.code[0] # ex: (
                        tail = self.code[1] # ex: )
                        
                        shell_text.insert(tk.SEL_FIRST, head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)
                    elif self.code[-2:] == '()':
                        # builtin function
                        head = self.code[:-1] 
                        tail = self.code[-1] 

                        shell_text.insert(tk.SEL_FIRST, head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)

                    else:
                        shell_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        self.content_insert(shell_text, self.code)
                        if self.var_postfix_enter.get():
                            shell_text.event_generate("<Return>")

                else: # input_start among selection
                    if self.code in self.enclosed_symbols:
                        # handle enclosed
                        head = self.code[0] # ex: (
                        tail = self.code[1] # ex: )

                        shell_text.insert('input_start', head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)
                    elif self.code[-2:] == '()':
                        # builtin function
                        head = self.code[:-1] 
                        tail = self.code[-1] 

                        shell_text.insert('input_start', head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)

                    else:
                        shell_text.delete('input_start', tk.SEL_LAST)
                        shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                        self.content_insert(shell_text, self.code)
                        if self.var_postfix_enter.get():
                            shell_text.event_generate("<Return>")
                
        elif dragging and not hovering:
            if shell_text.tag_ranges(tk.SEL):
                shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)

            if shell_text.compare(tk.INSERT, '>=', 'input_start'):
                # cursor after input_start
                self.content_insert(shell_text, self.code)
                if self.var_postfix_enter.get():
                    shell_text.event_generate("<Return>")

        elif dragging and hovering:
            if shell_text.compare(tk.SEL_LAST, '>', 'input_start'):
                if shell_text.compare(tk.SEL_FIRST, '>=', 'input_start'):
                    if self.code in self.enclosed_symbols:
                        # handle enclosed
                        head = self.code[0] # ex: (
                        tail = self.code[1] # ex: )

                        shell_text.insert(tk.SEL_FIRST, head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)

                    elif self.code[-2:] == '()':
                        # builtin function
                        head = self.code[:-1] 
                        tail = self.code[-1] 

                        shell_text.insert(tk.SEL_FIRST, head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)

                    else:
                        shell_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        self.content_insert(shell_text, self.code)
                        if self.var_postfix_enter.get():
                            shell_text.event_generate("<Return>")
                else: # input_start among selection
                    if self.code in self.enclosed_symbols:
                        # handle enclosed
                        head = self.code[0] # ex: (
                        tail = self.code[1] # ex: )

                        shell_text.insert('input_start', head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)
                    elif self.code[-2:] == '()':
                        # builtin function
                        head = self.code[:-1] 
                        tail = self.code[-1] 

                        shell_text.insert('input_start', head)
                        stored_index = shell_text.index(tk.SEL_LAST)
                        #keep insert cursor in the last of selection
                        shell_text.insert(tk.SEL_LAST, tail) 
                        shell_text.mark_set(tk.INSERT, stored_index)
                        shell_text.tag_remove(tk.SEL,tk.SEL_FIRST, tk.SEL_LAST)
                    else:
                        shell_text.delete('input_start', tk.SEL_LAST)
                        shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
                        self.content_insert(shell_text, self.code)
                        if self.var_postfix_enter.get():
                            shell_text.event_generate("<Return>")


# class SymbolToolPostMixin:
#     """ before insert , popup a menu  """


#     # def on_mouse_release(self, event):
#     #     #check and destroy drag window        
#     #     if self.drag_window:
#     #         self.drag_window.destroy()
#     #         self.drag_window = None
#     #         self.postit_button.config(cursor='arrow')
            
#     #     # restore mouse cursor 

#     #     # find out post type and target   
#     #     x_root, y_root = event.x_root, event.y_root
#     #     # keep x_root, y_root for later_use
#     #     self.mouse_x_root = x_root
#     #     self.mouse_y_root = y_root

#     #     hover_widget = event.widget.winfo_containing(x_root,y_root)
#     #     self.determine_post_place_and_type(hover_widget)
#     #     #reset hover state 
#     #     self.drag_hover_selection = False


#     def insert_into_editor(self, editor_text, 
#                            pressing=False, dragging=False,
#                            selecting=False, hovering=False):
#         pass
#         # self.insert_widget = editor_text
#         # self.insert_pressing = pressing
#         # self.insert_dragging = dragging
#         # self.insert_selecting = selecting
#         # self.insert_hovering = hovering
#         # self.popup_menu.tk_popup(self.mouse_x_root, self.mouse_y_root)

#     def insert_into_shell(self, shell_text, 
#                            pressing=False, dragging=False,
#                            selecting=False, hovering=False):
#         pass
#         # self.insert_widget = shell_text
#         # self.insert_pressing = pressing
#         # self.insert_dragging = dragging
#         # self.insert_selecting = selecting
#         # self.insert_hovering = hovering
#         # self.popup_menu.tk_popup(self.mouse_x_root, self.mouse_y_root)


class SymbolToolPopup:
    def popup_init(self):
        #f = font.Font(size=10, weight=font.NORMAL, family='Consolas')
        f = common.popup_menu_font
        self.popup_menu = tk.Menu(self, tearoff=0, font=f)

        # submenu
        self.common_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.assign_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.arithmetic_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.data_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.string_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        
        self.collection_menu =  tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.flow_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.comparison_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.logic_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.module_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        self.builtin_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        #self.bracket_quote_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.punctuation_menu = tk.Menu(self.popup_menu, tearoff=0, font=f)
        

        # cascade submenu
        self.popup_menu.add_cascade(label='常用', menu=self.common_menu)
        self.popup_menu.add_cascade(label='運算', menu=self.arithmetic_menu)
        self.popup_menu.add_cascade(label='設值', menu=self.assign_menu)
        self.popup_menu.add_cascade(label='比較', 
                menu=self.comparison_menu)
        self.popup_menu.add_cascade(label='邏輯', 
                menu=self.logic_menu)
        self.popup_menu.add_cascade(label='資料類型', menu=self.data_menu)
        self.popup_menu.add_cascade(label='字串', menu=self.string_menu)
        
        self.popup_menu.add_cascade(label='群集', menu=self.collection_menu)
        #self.popup_menu.add_cascade(label='括號引號',
        #        menu=self.bracket_quote_menu)
        self.popup_menu.add_cascade(label='流程', menu=self.flow_menu)
        self.popup_menu.add_cascade(label='模組', menu=self.module_menu)
        self.popup_menu.add_cascade(label='內建函式', menu=self.builtin_menu)
        self.popup_menu.add_cascade(label='標點符號', menu=self.punctuation_menu)

        # common menu command
        self.common_menu.add_command( label='print() 列印', 
                command=lambda:self.change_symbol('print()','print() 列印'))
        self.common_menu.add_command( label=" = 設值 ", 
                command=lambda:self.change_symbol(' = '," = 設值 "))
        self.common_menu.add_command( label="input() 鍵盤輸入 ", 
                command=lambda:self.change_symbol('input()'," input() 鍵盤輸入 "))
        self.common_menu.add_command( label="True 真(成立) ", 
                command=lambda:self.change_symbol('True'," True 真(成立) "))
        self.common_menu.add_command( label="False 假(不成立) ", 
                command=lambda:self.change_symbol('False'," False 假(不成立) "))
        self.common_menu.add_command( label="len() 長度 ", 
                command=lambda:self.change_symbol('len()'," len() 長度 "))
        self.common_menu.add_command( label=" ' ' 單引號 ", 
                command=lambda:self.change_symbol("''"," ' ' 單引號 "))
        self.common_menu.add_command( label=" ( ) 圓括號 ", 
                command=lambda:self.change_symbol('()'," ( ) 圓括號 "))
        self.common_menu.add_command( label=" [ ] 方括號)", 
                command=lambda:self.change_symbol('[]'," [ ]  方括號"))


        # arithmetic menu command

        
        self.arithmetic_menu.add_command( label=' + 加 ', 
                command=lambda:self.change_symbol(' + ',' + 加 '))
        
        self.arithmetic_menu.add_command( label=' - 減(負) ', 
                command=lambda:self.change_symbol(' - ',' - 減(負) '))

        self.arithmetic_menu.add_command( label=' * 乘 ', 
                command=lambda:self.change_symbol(' * ',' * 乘 '))

        self.arithmetic_menu.add_command( label=' / 除 ', 
                command=lambda:self.change_symbol(' / ',' / 除 '))

        self.arithmetic_menu.add_command( label='( ) 圓括號 ', 
                command=lambda:self.change_symbol('()','( ) 圓括號 '))

        self.arithmetic_menu.add_command( label=' // 除法取商數', 
                command=lambda:self.change_symbol(' // ',' // 除法取商數'))

        

        self.arithmetic_menu.add_command( label=' % 除法取餘數', 
                command=lambda:self.change_symbol(' % ',' % 除法取餘數'))

        self.arithmetic_menu.add_command( label=' ** 次方 ', 
                command=lambda:self.change_symbol(' ** ',' ** 次方 '))

        # self.arithmetic_menu.add_command(
        #     label="0b  2進位表示", command=lambda:self.change_symbol('0b'))
        # self.arithmetic_menu.add_command(
        #     label="0o  8進位表示", command=lambda:self.change_symbol('0o'))
        # self.arithmetic_menu.add_command(
        #     label="0x 16進位表示", command=lambda:self.change_symbol('0x'))


        # string menu command
        # self.string_menu.add_command(
        #     label=" ' ' 單引號(字串)", command=lambda:self.change_symbol("''"))
        # self.string_menu.add_command(
        #     label=' " " 雙引號(字串)', command=lambda:self.change_symbol('""'))
        # self.string_menu.add_command(
        #     label='r" "  原始字串', command=lambda:self.change_symbol('r""'))
        # self.string_menu.add_command(
        #     label=" r' '  原始字串", command=lambda:self.change_symbol("r''"))
        # self.string_menu.add_command(
        #     label="\\n  換行(需在字串中)", command=lambda:self.change_symbol('\\n'))

        self.data_menu.add_command( label=" int() 整數 ", 
                command=lambda:self.change_symbol('int()'," int() 整數 "))
        self.data_menu.add_command( label=" float() 浮點數", 
                command=lambda:self.change_symbol('float()'," float() 浮點數"))
        self.data_menu.add_command( label=" bool() 布林值", 
                command=lambda:self.change_symbol('bool()'," bool() 布林值"))
        self.data_menu.add_command( label=" str() 字串", 
                command=lambda:self.change_symbol('str()'," str() 字串"))
        self.data_menu.add_command( label=" type() 查詢類型 ", 
                command=lambda:self.change_symbol('type()'," type() 查詢類型 "))
        self.data_menu.add_command( label=" None 空值 ", 
                command=lambda:self.change_symbol('None'," None 空值 "))
 

        self.string_menu.add_command( label=" str() 字串", 
                command=lambda:self.change_symbol('str()'," str() 字串"))
        self.string_menu.add_command( label=" ' ' 單引號(字串) ", 
                command=lambda:self.change_symbol("''"," ' ' 單引號(字串) "))
        self.string_menu.add_command( label=' " " 雙引號(字串) ', 
                command=lambda:self.change_symbol('""',' " " 雙引號(字串) '))
        self.string_menu.add_command( label="\\n  換行(需在字串中) ", 
                command=lambda:self.change_symbol('\\n',"\\n  換行(需在字串中) "))
        self.string_menu.add_command( label="{}  替換(需在字串中)", 
                command=lambda:self.change_symbol('{}',"{}  替換(需在字串中)"))
        self.string_menu.add_command( label=" r' '  原始字串 ", 
                command=lambda:self.change_symbol("r''"," r' '  原始字串 "))
        self.string_menu.add_command( label=".format() 格式替換", 
                command=lambda:self.change_symbol('.format()',".format() 格式替換"))
        self.string_menu.add_command( label=" repr() 表示字串", 
                command=lambda:self.change_symbol('repr()',"repr() 表示字串"))



        



        # assign menu command
        # self.assign_menu.add_command(
        #     label=" = 設值 ", command=lambda:self.change_symbol(' = '))
        # self.assign_menu.add_command(
        #     label=" += 加後設值 ", command=lambda:self.change_symbol(' += '))
        # self.assign_menu.add_command(
        #     label=" -= 減後設值 ", command=lambda:self.change_symbol(' -= '))
        # self.assign_menu.add_command(
        #     label=" *= 乘後設值 ", command=lambda:self.change_symbol(' *= '))
        # self.assign_menu.add_command(
        #     label=" /= 除後設值 ", command=lambda:self.change_symbol(' /= '))

        self.assign_menu.add_command( label=" = 設值 ", 
                command=lambda:self.change_symbol(' = '," = 設值 "))
        self.assign_menu.add_command( label=" += 加後設值 ", 
                command=lambda:self.change_symbol(' += '," += 加後設值 "))
        self.assign_menu.add_command( label=" -= 減後設值 ", 
                command=lambda:self.change_symbol(' -= '," -= 減後設值 "))
        self.assign_menu.add_command( label=" *= 乘後設值 ", 
                command=lambda:self.change_symbol(' *= '," *= 乘後設值 "))
        self.assign_menu.add_command( label=" /= 除後設值 ", 
                command=lambda:self.change_symbol(' /= '," /= 除後設值 "))


        # self.assign_menu.add_command(
        #     label="%=  取餘數後設值", command=lambda:self.change_symbol(' %= '))
        # self.assign_menu.add_command(
        #     label="**=  次方後設值", command=lambda:self.change_symbol(' **= '))

        # comparison menu command
        # self.comparison_menu.add_command(
        #     label=" == 等於 ", command=lambda:self.change_symbol(' == '))
        # self.comparison_menu.add_command(
        #     label=" != 不等於 ", command=lambda:self.change_symbol(' != '))
        # self.comparison_menu.add_command(
        #     label=" > 大於 ", command=lambda:self.change_symbol(' > '))
        # self.comparison_menu.add_command(
        #     label=" < 小於 ", command=lambda:self.change_symbol(' < '))
        # self.comparison_menu.add_command(
        #     label=" >= 大於等於 ", command=lambda:self.change_symbol(' >= '))
        # self.comparison_menu.add_command(
        #     label=" <= 小於等於 ", command=lambda:self.change_symbol(' <= '))

        self.comparison_menu.add_command( label=" == 等於 ", 
                command=lambda:self.change_symbol(' == '," == 等於 "))
        self.comparison_menu.add_command( label=" != 不等於 ", 
                command=lambda:self.change_symbol(' != '," != 不等於 "))
        self.comparison_menu.add_command( label=" > 大於 ", 
                command=lambda:self.change_symbol(' > '," > 大於 "))
        self.comparison_menu.add_command( label=" < 小於 ", 
                command=lambda:self.change_symbol(' < '," < 小於 "))
        self.comparison_menu.add_command( label=" >= 大於等於 ", 
                command=lambda:self.change_symbol(' >= '," >= 大於等於 "))
        self.comparison_menu.add_command( label=" <= 小於等於 ", 
                command=lambda:self.change_symbol(' <= '," <= 小於等於 "))


        # logic menu command
        # self.logic_menu.add_command(
        #     label=" and 而且 ", command=lambda:self.change_symbol(' and '))
        # self.logic_menu.add_command(
        #     label=" or 或 ", command=lambda:self.change_symbol(' or '))
        # self.logic_menu.add_command(
        #     label=" not 不是(否) ", command=lambda:self.change_symbol(' not '))
        # self.logic_menu.add_command(
        #     label=" True 真(成立) ", command=lambda:self.change_symbol('True'))
        # self.logic_menu.add_command(
        #     label=" False 假(不成立) ", command=lambda:self.change_symbol('False'))
        # self.logic_menu.add_command(
        #     label=" None 空值 ", command=lambda:self.change_symbol('None'))
        # self.logic_menu.add_command(
        #     label=" is 是 ", command=lambda:self.change_symbol(' is '))
        # self.logic_menu.add_command(
        #     label=" in 在裡面 ", command=lambda:self.change_symbol(' in '))

        self.logic_menu.add_command( label=" and 而且 ", 
                command=lambda:self.change_symbol(' and '," and 而且 "))
        self.logic_menu.add_command( label=" or 或 ", 
                command=lambda:self.change_symbol(' or '," or 或 "))
        self.logic_menu.add_command( label=" not 不是(否) ", 
                command=lambda:self.change_symbol(' not '," not 不是(否) "))
        self.logic_menu.add_command( label=" True 真(成立) ", 
                command=lambda:self.change_symbol('True'," True 真(成立) "))
        self.logic_menu.add_command( label=" False 假(不成立) ", 
                command=lambda:self.change_symbol('False'," False 假(不成立) "))
        self.logic_menu.add_command( label=" None 空值 ", 
                command=lambda:self.change_symbol('None'," None 空值 "))
        self.logic_menu.add_command( label=" is 是 ", 
                command=lambda:self.change_symbol(' is '," is 是 "))
        self.logic_menu.add_command( label=" in 在裡面 ", 
                command=lambda:self.change_symbol(' in '," in 在裡面 "))

        # collection menu command
        # self.collection_menu.add_command(
        #     label=" [ ] 方括號(清單、字典)", command=lambda:self.change_symbol('[]'))
        # self.collection_menu.add_command(
        #     label=" ( ) 圓括號(元組)", command=lambda:self.change_symbol('()'))
        # self.collection_menu.add_command(
        #     label=" { } 大括號(字典、集合)", command=lambda:self.change_symbol('{}'))
        # self.collection_menu.add_command(
        #     label=",   逗號", command=lambda:self.change_symbol(', '))

        self.collection_menu.add_command( label=" [ ] 清單、字典", 
                command=lambda:self.change_symbol('[]'," [ ] 清單、字典"))
        self.collection_menu.add_command( label=" ( ) 元組 ", 
                command=lambda:self.change_symbol('()'," ( ) 元組 "))
        self.collection_menu.add_command( label=" { } 字典、集合", 
                command=lambda:self.change_symbol('{}'," { } 字典、集合"))
        self.collection_menu.add_command( label=" list() 清單", 
                command=lambda:self.change_symbol('list()'," list() 清單"))
        self.collection_menu.add_command( label=" tuple() 元組", 
                command=lambda:self.change_symbol('tuple()'," tuple() 元組"))
        self.collection_menu.add_command( label=" dict() 字典", 
                command=lambda:self.change_symbol('dict()'," dict() 字典"))
        self.collection_menu.add_command( label=" set() 集合", 
                command=lambda:self.change_symbol('set()'," set() 集合"))

        # flow menu command
        # self.flow_menu.add_command(
        #     label=" () 呼叫 ", command=lambda:self.change_symbol('()'))
        # self.flow_menu.add_command(
        #     label=",   逗號", command=lambda:self.change_symbol(', '))
        # self.flow_menu.add_command(
        #     label=" : 後接區塊", command=lambda:self.change_symbol(':'))
        # self.flow_menu.add_command(
        #     label=" pass 略過(佔位)", command=lambda:self.change_symbol('pass'))

        self.flow_menu.add_command( label=" ( ) 呼叫 ", 
                command=lambda:self.change_symbol('()'," ( ) 呼叫 "))
        self.flow_menu.add_command( label=" , 分隔 ", 
                command=lambda:self.change_symbol(', '," , 分隔 "))
        self.flow_menu.add_command( label=" : 後接區塊", 
                command=lambda:self.change_symbol(':'," : 後接區塊"))
        self.flow_menu.add_command( label=" break 中斷(迴圈)", 
                command=lambda:self.change_symbol('break'," break 中斷(迴圈)"))
        self.flow_menu.add_command( label=" continue 繼續(迴圈)", 
                command=lambda:self.change_symbol('continue'," continue 繼續(迴圈)"))
        self.flow_menu.add_command( label=" pass 略過(佔位)", 
                command=lambda:self.change_symbol('pass'," pass 略過(佔位)"))
        self.flow_menu.add_command( label=" global 全域 ", 
                command=lambda:self.change_symbol('global '," global 全域 "))

        self.module_menu.add_command( label=" import 匯入 ", 
                command=lambda:self.change_symbol('import '," import 匯入"))
        self.module_menu.add_command( label=" from 從 ", 
                command=lambda:self.change_symbol('from '," from 從 "))

        self.builtin_menu.add_command( label="abs() 絕對值 ", 
                command=lambda:self.change_symbol('abs()'," abs() 絕對值 "))
        # self.builtin_menu.add_command( label=" all() 全部為真 ", 
        #         command=lambda:self.change_symbol('all()'," all() 全部為真 "))
        # self.builtin_menu.add_command( label=" any() 有一個為真 ", 
        #         command=lambda:self.change_symbol('any()'," any() 有一個為真 "))
        self.builtin_menu.add_command( label="bin() 二進位字串 ", 
                command=lambda:self.change_symbol('bin()'," bin() 二進位字串 "))
        self.builtin_menu.add_command( label="hex() 十六進位字串", 
                command=lambda:self.change_symbol('hex()',"hex() 十六進位字串"))
        self.builtin_menu.add_command( label="chr() 傳回字元 ", 
                command=lambda:self.change_symbol('chr()'," chr() 傳回字元 "))
        self.builtin_menu.add_command( label="ord() 傳回字碼 ", 
                command=lambda:self.change_symbol('ord()'," ord() 傳回字碼 "))
        
        self.builtin_menu.add_command( label="min() 最小值 ", 
                command=lambda:self.change_symbol('min()'," min() 最小值 "))
        self.builtin_menu.add_command( label="max() 最大值 ", 
                command=lambda:self.change_symbol('max()'," max() 最大值 "))
        self.builtin_menu.add_command( label="divmod() 商與餘數", 
                command=lambda:self.change_symbol('divmod()',"divmod() 商與餘數"))
        self.builtin_menu.add_command( label="round() 4捨6入5成雙", 
                command=lambda:self.change_symbol('round()',"round() 4捨6入5成雙"))
        self.builtin_menu.add_command( label="help() 說明 ", 
                command=lambda:self.change_symbol('help()'," help() 說明 "))
        self.builtin_menu.add_command( label="dir() 查看內部 ", 
                command=lambda:self.change_symbol('dir()'," dir() 說明 "))
        
        self.builtin_menu.add_command( label="sorted() 排序 ", 
                command=lambda:self.change_symbol('sorted()'," sorted() 排序 "))
        self.builtin_menu.add_command( label="reversed() 反轉 ", 
                command=lambda:self.change_symbol('reversed()',"reversed() 反轉 "))


        # punctuation menu command 
        # self.punctuation_menu.add_command(
        #     label=" , 逗號 ", command=lambda:self.change_symbol(', '))
        # self.punctuation_menu.add_command(
        #     label=" . 句號 ", command=lambda:self.change_symbol('.'))
        # self.punctuation_menu.add_command(
        #     label=" : 冒號 ", command=lambda:self.change_symbol(':'))
        # self.punctuation_menu.add_command(
        #     label=" ; 分號 ", command=lambda:self.change_symbol(';'))
        # self.punctuation_menu.add_command(
        #     label="( )  圓括號(呼叫)", command=lambda:self.change_symbol('()'))
        # self.punctuation_menu.add_command(
        #     label="' '  單引號(字串)", command=lambda:self.change_symbol("''"))
        # self.punctuation_menu.add_command(
        #     label=" # 井字號(註解)", command=lambda:self.change_symbol("# "))
        # self.punctuation_menu.add_command(
        #     label="\\  反斜線", command=lambda:self.change_symbol("\\"))
        # self.punctuation_menu.add_command(
        #     label="@  小老鼠", command=lambda:self.change_symbol("@"))

        self.punctuation_menu.add_command( label=" , 逗號 ", 
                command=lambda:self.change_symbol(', '," , 逗號 "))
        self.punctuation_menu.add_command( label=" . 句號 ", 
                command=lambda:self.change_symbol('.'," . 句號 "))
        self.punctuation_menu.add_command( label=" : 冒號 ", 
                command=lambda:self.change_symbol(':'," : 冒號 "))
        self.punctuation_menu.add_command( label=" ; 分號 ", 
                command=lambda:self.change_symbol(';'," ; 分號 "))
        self.punctuation_menu.add_command( label=" _ 底線 ", 
                command=lambda:self.change_symbol('_'," _ 底線 "))
        self.punctuation_menu.add_command( label=" # 井字號(註解)", 
                command=lambda:self.change_symbol("# "," # 井字號(註解)"))
        self.punctuation_menu.add_command( label=" @ 小老鼠(at)", 
                command=lambda:self.change_symbol("@ "," @ 小老鼠(at)"))
        self.punctuation_menu.add_command( label=" \\ 反斜線", 
                command=lambda:self.change_symbol("\\"," \\ 反斜線"))



        self.postit_button.bind("<Button-3>", self.popup)

    def popup(self, event):
         self.popup_menu.tk_popup(event.x_root, event.y_root)

    def change_symbol(self, code, code_display):
        self.code = code
        self.code_display = code_display
        self.postit_button.config(text=code_display)
        
        #return


        # insert at the same time
        workbench = get_workbench()
        focus_widget = workbench.focus_get()
        if isinstance(focus_widget, CodeViewText):
            # cursor in editor
            editor_text = focus_widget 
            if editor_text.tag_ranges(tk.SEL)  :
                # has selection
                self.insert_into_editor(editor_text, 
                                        pressing=True, selecting=True)
            else:# no selection
                self.insert_into_editor(editor_text, 
                                        pressing=True, selecting=False)
        elif isinstance(focus_widget, ShellText):
            # cusor in shell
            shell_text = focus_widget
            if shell_text.tag_ranges(tk.SEL):
                # has selection
                self.insert_into_shell(shell_text, 
                                        pressing=True, selecting=True)
            else:# no selection
                self.insert_into_shell(shell_text, 
                                        pressing=True, selecting=False) 

    # def menu_post(self, symbol):
    #     if isinstance(self.insert_widget, CodeViewText):
    #         self.menu_insert_into_editor(symbol)
    #     elif isinstance(self.insert_widget, ShellText):
    #         self.menu_insert_into_shell(symbol)

    # def menu_insert_into_editor(self, symbol):
    #     if self.insert_pressing and not self.insert_selecting:
    #         self.insert_widget.insert(tk.INSERT, symbol)

    #     elif self.insert_pressing and self.insert_selecting:
    #         self.insert_widget.event_generate("<BackSpace>")
    #         self.insert_widget.insert(tk.INSERT, symbol)

    #     elif self.insert_dragging and not self.insert_hovering:
    #         self.insert_widget.insert(tk.INSERT, symbol)

    #     elif self.insert_dragging and self.insert_hovering:
    #         self.insert_widget.event_generate("<BackSpace>")
    #         self.insert_widget.insert(tk.INSERT, symbol)

    # def menu_insert_into_shell(self, symbol):
    #     if self.insert_pressing and not self.insert_selecting:
    #         if self.insert_widget.compare(tk.INSERT, '>=', 'input_start'):
    #             self.insert_widget.insert(tk.INSERT, symbol)
    #         else:
    #             self.insert_widget.insert('end-1c', symbol)

    #     elif self.insert_pressing and self.insert_selecting:
    #         if self.insert_widget.compare(tk.SEL_LAST, '>', 'input_start'):
    #             if self.insert_widget.compare(tk.SEL_FIRST,'>=', 'input_start'):
    #                 self.insert_widget.event_generate("<BackSpace>")
    #                 self.insert_widget.insert(tk.INSERT, symbol)
    #             else:
    #                 self.insert_widget.delete('input_start', tk.SEL_LAST)
    #                 self.insert_widget.tag_remove(tk.SEL,
    #                         tk.SEL_FIRST,tk.SEL_LAST)
    #                 self.insert_widget.insert('input_start', symbol)
    #         else:
    #             self.insert_widget.insert('end-1c', symbol)

    #     elif self.insert_dragging and not self.insert_hovering:
    #         if self.insert_widget.compare(tk.INSERT, '>=', 'input_start'):
    #             self.insert_widget.insert(tk.INSERT, symbol)

    #     elif self.insert_dragging and self.insert_hovering:
    #         if self.insert_widget.compare(tk.SEL_LAST, '>', 'input_start'):
    #             if self.insert_widget.compare(tk.SEL_FIRST,'>=', 'input_start'):
    #                 self.insert_widget.event_generate("<BackSpace>")
    #                 self.insert_widget.insert(tk.INSERT, symbol)
    #             else:
    #                 self.insert_widget.delete('input_start', tk.SEL_LAST)
    #                 self.insert_widget.tag_remove(tk.SEL,
    #                         tk.SEL_FIRST,tk.SEL_LAST)
    #                 self.insert_widget.insert('input_start', symbol)
            #else:
            #    self.insert_widget.insert('end-1c', symbol)


# class SymbolToolPostit(ToolWidget,     
#                  ToolCodeMixin, BaseCode,
#                  SymbolToolPostMixin, BasePost, 
#                  SymbolToolPopup):
class SymbolToolPostit(SymbolWidget,     
                  SymbolCodeMixin, BaseCode,
                  SymbolToolPostMixin, BasePost, 
                 SymbolToolPopup):


    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master)
        self.code_init('print()', "print() 列印")
        self.post_init()
        self.popup_init()