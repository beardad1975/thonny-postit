import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell



from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup



class SymbolToolPostMixin:
    """ before insert , popup a menu  """


    def on_mouse_release(self, event):
        #check and destroy drag window        
        if self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None
            self.postit_button.config(cursor='arrow')
            
        # restore mouse cursor 

        # find out post type and target   
        x_root, y_root = event.x_root, event.y_root
        # keep x_root, y_root for later_use
        self.mouse_x_root = x_root
        self.mouse_y_root = y_root

        hover_widget = event.widget.winfo_containing(x_root,y_root)
        self.determine_post_place_and_type(hover_widget)
        #reset hover state 
        self.drag_hover_selection = False


    def insert_into_editor(self, editor_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        self.insert_widget = editor_text
        self.insert_pressing = pressing
        self.insert_dragging = dragging
        self.insert_selecting = selecting
        self.insert_hovering = hovering
        self.popup_menu.tk_popup(self.mouse_x_root, self.mouse_y_root)

    def insert_into_shell(self, shell_text, 
                           pressing=False, dragging=False,
                           selecting=False, hovering=False):
        self.insert_widget = shell_text
        self.insert_pressing = pressing
        self.insert_dragging = dragging
        self.insert_selecting = selecting
        self.insert_hovering = hovering
        self.popup_menu.tk_popup(self.mouse_x_root, self.mouse_y_root)


class SymbolToolPopup:
    def popup_init(self):
        self.popup_menu = tk.Menu(self, tearoff=0)

        # submenu
        self.arithmetic_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.assign_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.compare_flow_menu = tk.Menu(self.popup_menu, tearoff=0)
        self.bracket_quote_menu = tk.Menu(self.popup_menu, tearoff=0)


        # cascade submenu
        self.popup_menu.add_cascade(label='運算', menu=self.arithmetic_menu)
        self.popup_menu.add_cascade(label='設值', menu=self.assign_menu)
        self.popup_menu.add_cascade(label='比較與流程', 
                menu=self.compare_flow_menu)
        self.popup_menu.add_cascade(label='括號與引號',
                menu=self.bracket_quote_menu)


        # arithmetic menu command
        self.arithmetic_menu.add_command(
            label="+  加", command=lambda:self.menu_post(' + '))
        self.arithmetic_menu.add_command(
            label="-  減", command=lambda:self.menu_post(' - '))
        self.arithmetic_menu.add_command(
            label="*  乘", command=lambda:self.menu_post(' * '))
        self.arithmetic_menu.add_command(
            label="/  除", command=lambda:self.menu_post(' / '))
        self.arithmetic_menu.add_command(
            label="%  取餘數", command=lambda:self.menu_post(' % '))
        self.arithmetic_menu.add_command(
            label="** 次方", command=lambda:self.menu_post(' ** '))
        self.arithmetic_menu.add_command(
            label="0b  2進位表示", command=lambda:self.menu_post('0b'))
        self.arithmetic_menu.add_command(
            label="0o  8進位表示", command=lambda:self.menu_post('0o'))
        self.arithmetic_menu.add_command(
            label="0x 16進位表示", command=lambda:self.menu_post('0x'))

        # assign menu command
        self.assign_menu.add_command(
            label="=   設值", command=lambda:self.menu_post(' = '))
        self.assign_menu.add_command(
            label="+=  加後設值", command=lambda:self.menu_post(' += '))
        self.assign_menu.add_command(
            label="-=  減後設值", command=lambda:self.menu_post(' -= '))
        self.assign_menu.add_command(
            label="*=  乘後設值", command=lambda:self.menu_post(' *= '))
        self.assign_menu.add_command(
            label="/=  除後設值", command=lambda:self.menu_post(' /= '))
        self.assign_menu.add_command(
            label="%=  取餘數後設值", command=lambda:self.menu_post(' %= '))
        self.assign_menu.add_command(
            label="**=  次方後設值", command=lambda:self.menu_post(' **= '))

        # comparison menu command
        self.compare_flow_menu.add_command(
            label="==   等於", command=lambda:self.menu_post(' == '))
        self.compare_flow_menu.add_command(
            label="!=   不等於", command=lambda:self.menu_post(' != '))
        self.compare_flow_menu.add_command(
            label=">    大於", command=lambda:self.menu_post(' > '))
        self.compare_flow_menu.add_command(
            label="<   小於", command=lambda:self.menu_post(' < '))
        self.compare_flow_menu.add_command(
            label=">=   大於等於", command=lambda:self.menu_post(' >= '))
        self.compare_flow_menu.add_command(
            label="<=   小於等於", command=lambda:self.menu_post(' <= '))
        self.compare_flow_menu.add_command(
            label=":   冒號", command=lambda:self.menu_post(':'))

        # bracket and quote menu command
        self.bracket_quote_menu.add_command(
            label="( )  圓括號", command=lambda:self.menu_post('()'))
        self.bracket_quote_menu.add_command(
            label="[ ]  方括號", command=lambda:self.menu_post('[]'))
        self.bracket_quote_menu.add_command(
            label="{ }  大括號", command=lambda:self.menu_post('{}'))
        self.bracket_quote_menu.add_command(
            label="' '  單引號", command=lambda:self.menu_post("''"))
        self.bracket_quote_menu.add_command(
            label='" "  單引號', command=lambda:self.menu_post('""'))

        

        #self.postit_button.bind("<Button-3>", self.popup)

    # def popup(self, event):
    #     self.popup_menu.tk_popup(event.x_root, event.y_root)

    def menu_post(self, symbol):
        if isinstance(self.insert_widget, CodeViewText):
            self.menu_insert_into_editor(symbol)
        elif isinstance(self.insert_widget, ShellText):
            self.menu_insert_into_shell(symbol)

    def menu_insert_into_editor(self, symbol):
        if self.insert_pressing and not self.insert_selecting:
            self.insert_widget.insert(tk.INSERT, symbol)

        elif self.insert_pressing and self.insert_selecting:
            self.insert_widget.event_generate("<BackSpace>")
            self.insert_widget.insert(tk.INSERT, symbol)

        elif self.insert_dragging and not self.insert_hovering:
            self.insert_widget.insert(tk.INSERT, symbol)

        elif self.insert_dragging and self.insert_hovering:
            self.insert_widget.event_generate("<BackSpace>")
            self.insert_widget.insert(tk.INSERT, symbol)

    def menu_insert_into_shell(self, symbol):
        if self.insert_pressing and not self.insert_selecting:
            if self.insert_widget.compare(tk.INSERT, '>=', 'input_start'):
                self.insert_widget.insert(tk.INSERT, symbol)
            else:
                self.insert_widget.insert('end-1c', symbol)

        elif self.insert_pressing and self.insert_selecting:
            if self.insert_widget.compare(tk.SEL_LAST, '>', 'input_start'):
                if self.insert_widget.compare(tk.SEL_FIRST,'>=', 'input_start'):
                    self.insert_widget.event_generate("<BackSpace>")
                    self.insert_widget.insert(tk.INSERT, symbol)
                else:
                    self.insert_widget.delete('input_start', tk.SEL_LAST)
                    self.insert_widget.tag_remove(tk.SEL,
                            tk.SEL_FIRST,tk.SEL_LAST)
                    self.insert_widget.insert('input_start', symbol)
            else:
                self.insert_widget.insert('end-1c', symbol)

        elif self.insert_dragging and not self.insert_hovering:
            if self.insert_widget.compare(tk.INSERT, '>=', 'input_start'):
                self.insert_widget.insert(tk.INSERT, symbol)

        elif self.insert_dragging and self.insert_hovering:
            if self.insert_widget.compare(tk.SEL_LAST, '>', 'input_start'):
                if self.insert_widget.compare(tk.SEL_FIRST,'>=', 'input_start'):
                    self.insert_widget.event_generate("<BackSpace>")
                    self.insert_widget.insert(tk.INSERT, symbol)
                else:
                    self.insert_widget.delete('input_start', tk.SEL_LAST)
                    self.insert_widget.tag_remove(tk.SEL,
                            tk.SEL_FIRST,tk.SEL_LAST)
                    self.insert_widget.insert('input_start', symbol)
            #else:
            #    self.insert_widget.insert('end-1c', symbol)


class SymbolToolPostit(ToolWidget,     
                 ToolCodeMixin, BaseCode,
                 SymbolToolPostMixin, BasePost, 
                 SymbolToolPopup):
    """ composite and mixin approach postit"""
    def __init__(self, master):
        self.widget_init(master, 'symbol')
        self.code_init()
        self.post_init()
        self.popup_init()