import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell



from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup

from ..common import common_images

class SymbolWidget(ttk.Frame):

    def widget_init(self, master):
        # don't need to handle tab
        
        #self.tool_image = common_images[tool_name]

        ttk.Frame.__init__(self, master)
        f = font.Font(size=11, weight=font.NORMAL, family='Consolas')        
        self.postit_button = tk.Button(self,  
                                        relief='solid',
                                        borderwidth=1,
                                        text = '*',
                                        font = f,
                                        #fg=self.tab.font_color, 
                                        height=24,
                                        #width=40,
                                        #justify='left', 
                                        #font=f,
                                        compound='center',
                                        image=common_images['empty'],
                                        padx=0,
                                        pady=0, 
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')

class SymbolCodeMixin:
    def code_init(self, code):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.code = code
        self.code_display = code 
        self.note = ''

        self.enclosed_symbols = ('()','[]','{}',"''",'""',)

        self.postit_button.config(text=code)
            
            #self.update_postit_code()

    def update_postit_code(self):
        pass


class SymbolToolPostMixin:

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
        self.popup_menu = tk.Menu(self, tearoff=0)

        # submenu
        self.arithmetic_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.assign_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.login_compare_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.bracket_quote_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.misc_menu = tk.Menu(self.popup_menu, tearoff=0)
        

        # cascade submenu
        self.popup_menu.add_cascade(label='運算', menu=self.arithmetic_menu)
        self.popup_menu.add_cascade(label='括號與引號',
                menu=self.bracket_quote_menu)
        self.popup_menu.add_cascade(label='設值', menu=self.assign_menu)
        self.popup_menu.add_cascade(label='邏輯與比較', 
                menu=self.login_compare_menu)

        self.popup_menu.add_cascade(label='其他', menu=self.misc_menu)

        # arithmetic menu command
        self.arithmetic_menu.add_command(
            label="+  加", command=lambda:self.change_symbol(' + '))
        self.arithmetic_menu.add_command(
            label="-  減", command=lambda:self.change_symbol(' - '))
        self.arithmetic_menu.add_command(
            label="*  乘", command=lambda:self.change_symbol(' * '))
        self.arithmetic_menu.add_command(
            label="/  除", command=lambda:self.change_symbol(' / '))
        self.arithmetic_menu.add_command(
            label="%  取餘數", command=lambda:self.change_symbol(' % '))
        self.arithmetic_menu.add_command(
            label="** 次方", command=lambda:self.change_symbol(' ** '))
        # self.arithmetic_menu.add_command(
        #     label="0b  2進位表示", command=lambda:self.change_symbol('0b'))
        # self.arithmetic_menu.add_command(
        #     label="0o  8進位表示", command=lambda:self.change_symbol('0o'))
        # self.arithmetic_menu.add_command(
        #     label="0x 16進位表示", command=lambda:self.change_symbol('0x'))

        # assign menu command
        self.assign_menu.add_command(
            label="=   設值", command=lambda:self.change_symbol(' = '))
        self.assign_menu.add_command(
            label="+=  加後設值", command=lambda:self.change_symbol(' += '))
        self.assign_menu.add_command(
            label="-=  減後設值", command=lambda:self.change_symbol(' -= '))
        self.assign_menu.add_command(
            label="*=  乘後設值", command=lambda:self.change_symbol(' *= '))
        self.assign_menu.add_command(
            label="/=  除後設值", command=lambda:self.change_symbol(' /= '))
        self.assign_menu.add_command(
            label="%=  取餘數後設值", command=lambda:self.change_symbol(' %= '))
        self.assign_menu.add_command(
            label="**=  次方後設值", command=lambda:self.change_symbol(' **= '))

        # comparison menu command
        self.login_compare_menu.add_command(
            label="and   而且", command=lambda:self.change_symbol(' and '))
        self.login_compare_menu.add_command(
            label="or    或", command=lambda:self.change_symbol(' or '))
        self.login_compare_menu.add_command(
            label="not   不是", command=lambda:self.change_symbol(' not '))
        self.login_compare_menu.add_command(
            label="True   真", command=lambda:self.change_symbol('True'))
        self.login_compare_menu.add_command(
            label="False   假", command=lambda:self.change_symbol('False'))
        self.login_compare_menu.add_command(
            label="==   等於", command=lambda:self.change_symbol(' == '))
        self.login_compare_menu.add_command(
            label="!=   不等於", command=lambda:self.change_symbol(' != '))
        self.login_compare_menu.add_command(
            label=">    大於", command=lambda:self.change_symbol(' > '))
        self.login_compare_menu.add_command(
            label="<   小於", command=lambda:self.change_symbol(' < '))
        self.login_compare_menu.add_command(
            label=">=   大於等於", command=lambda:self.change_symbol(' >= '))
        self.login_compare_menu.add_command(
            label="<=   小於等於", command=lambda:self.change_symbol(' <= '))
        self.login_compare_menu.add_command(
            label="None   空值", command=lambda:self.change_symbol('None'))
        self.login_compare_menu.add_command(
            label="is   是", command=lambda:self.change_symbol(' is '))
        self.login_compare_menu.add_command(
            label="in   在裡面", command=lambda:self.change_symbol(' in '))

        # bracket and quote menu command
        self.bracket_quote_menu.add_command(
            label="( )  圓括號", command=lambda:self.change_symbol('()'))
        self.bracket_quote_menu.add_command(
            label="[ ]  方括號", command=lambda:self.change_symbol('[]'))
        self.bracket_quote_menu.add_command(
            label="{ }  大括號", command=lambda:self.change_symbol('{}'))
        self.bracket_quote_menu.add_command(
            label="' '  單引號", command=lambda:self.change_symbol("''"))
        self.bracket_quote_menu.add_command(
            label='" "  雙引號', command=lambda:self.change_symbol('""'))

        # misc menu command
        self.misc_menu.add_command(
            label=":   冒號", command=lambda:self.change_symbol(':'))
        self.misc_menu.add_command(
            label="\\n  換行(需在字串中)", command=lambda:self.change_symbol('\\n'))
        

        self.postit_button.bind("<Button-3>", self.popup)

    def popup(self, event):
         self.popup_menu.tk_popup(event.x_root, event.y_root)

    def change_symbol(self, symbol):
        self.code = symbol
        self.code_display = symbol
        self.postit_button.config(text=symbol)

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
        self.code_init(' + ')
        self.post_init()
        self.popup_init()