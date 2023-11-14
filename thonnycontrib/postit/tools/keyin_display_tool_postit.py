import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from .tool_postit import ToolWidget, ToolCodeMixin
from ..base_postit import BaseCode, BasePost, BasePopup
from .. import common

# keyboardlayout code adopted from 
# https://github.com/spacether/keyboardlayout
# version 2.0.1 and modified to fit this project
import keyboardlayout
from keyboardlayout import tkinter as kbl_tkinter
from keyboardlayout.key import Key

grey = '#eeeeee'
dark_grey = '#626262'
key_size = 30

key_dict = {
    '`': Key.BACKQUOTE,
    '~': Key.ASCII_TILDE,
    '1': Key.DIGIT_1,
    '!': Key.EXCLAMATION,
    '2': Key.DIGIT_2,
    '@': Key.AT,
    '3': Key.DIGIT_3,
    '#': Key.NUMBER,
    '4': Key.DIGIT_4,
    '$': Key.DOLLAR,
    '5': Key.DIGIT_5,
    '%': Key.PERCENT,
    '6': Key.DIGIT_6,
    94: Key.CIRCUMFLEX,
    '7': Key.DIGIT_7,
    '&': Key.AMPERSAND,
    '8': Key.DIGIT_8,
    '*': Key.ASTERISK,
    '9': Key.DIGIT_9,
    '(': Key.LEFTPAREN,
    '0': Key.DIGIT_0,
    ')': Key.RIGHTPAREN,
    '-': Key.MINUS,
    '+': Key.PLUS,
    '=': Key.EQUALS,
    'backspace': Key.BACKSPACE,
    'tab': Key.TAB,
    'q': Key.Q,
    'Q': Key.Q_UPPER,
    'w': Key.W,
    'W': Key.W_UPPER,
    'e': Key.E,
    'E': Key.E_UPPER,
    'r': Key.R,
    'R': Key.R_UPPER,
    't': Key.T,
    'T': Key.T_UPPER,
    'y': Key.Y,
    'Y': Key.Y_UPPER,
    'u': Key.U,
    'U': Key.U_UPPER,
    'i': Key.I,
    'I': Key.I_UPPER,
    'o': Key.O,
    'O': Key.O_UPPER,
    'p': Key.P,
    'P': Key.P_UPPER,
    '[': Key.LEFTBRACKET,
    '{': Key.BRACELEFT,
    ']': Key.RIGHTBRACKET,
    '}': Key.BRACERIGHT,
    '\\': Key.BACKSLASH,
    '|': Key.PIPE,
    'caps lock': Key.CAPSLOCK,
#    65792: Key.CAPSLOCK, # MACOS
    'a': Key.A,
    'A': Key.A_UPPER,
    's': Key.S,
    'S': Key.S_UPPER,
    'd': Key.D,
    'D': Key.D_UPPER,
    'f': Key.F,
    'F': Key.F_UPPER,
    'g': Key.G,
    'G': Key.G_UPPER,
    'h': Key.H,
    'H': Key.H_UPPER,
    'j': Key.J,
    'J': Key.J_UPPER,
    'k': Key.K,
    'K': Key.K_UPPER,
    'l': Key.L,
    'L': Key.L_UPPER,
    ';': Key.SEMICOLON,
    ':': Key.COLON,
    "'": Key.SINGLEQUOTE,
    '"': Key.DOUBLEQUOTE,
    'enter': Key.RETURN,
#    'shift': Key.LEFT_SHIFT, # macOs
#    131330: Key.LEFT_SHIFT, # macOs
    'shift': Key.LEFT_SHIFT,
    'z': Key.Z,
    'Z': Key.Z_UPPER,
    'x': Key.X,
    'X': Key.X_UPPER,
    'c': Key.C,
    'C': Key.C_UPPER,
    'v': Key.V,
    'V': Key.V_UPPER,
    'b': Key.B,
    'B': Key.B_UPPER,
    'n': Key.N,
    'N': Key.N_UPPER,
    'm': Key.M,
    'M': Key.M_UPPER,
    ',': Key.COMMA,
    '<': Key.LESSTHAN,
    '.': Key.PERIOD,
    '>': Key.GREATERTHAN,
    '/': Key.FORWARDSLASH,
    '?': Key.QUESTION,
#    131076: Key.RIGHT_SHIFT, # macOs
    'right shift': Key.RIGHT_SHIFT,
#    262145: Key.LEFT_CONTROL, # macOs
    'ctrl': Key.LEFT_CONTROL,
#    1048584: Key.LEFT_META, # macOs
    65511: Key.LEFT_META,
#    524320: Key.LEFT_ALT, # macOs
    'alt': Key.LEFT_ALT,
    'space': Key.SPACE,
#    524352: Key.RIGHT_ALT, # macOs
    'right alt': Key.RIGHT_ALT,
#    1048592: Key.RIGHT_META, # macOs
    65512: Key.RIGHT_META,
#    7208976: Key.CONTEXT_MENU, # macOs
    1073741925: Key.CONTEXT_MENU,
    'right ctrl': Key.RIGHT_CONTROL,
#    65508: Key.RIGHT_CONTROL, # macOs
    'up': Key.UP_ARROW,
    'down': Key.DOWN_ARROW,
    'left': Key.LEFT_ARROW,
    'right': Key.RIGHT_ARROW,
}

def get_keyboard(frame,
    layout_name: keyboardlayout.LayoutName,
    key_info: keyboardlayout.KeyInfo
    ) -> keyboardlayout.tkinter.KeyboardLayout:
    
    keyboard_info = keyboardlayout.KeyboardInfo(
        position=(0, 0),
        padding=2,
        color=dark_grey)
    
    letter_key_size = (key_size, key_size)  # width, height
    keyboard_widget = kbl_tkinter.KeyboardLayout(
        layout_name,
        keyboard_info,
        letter_key_size,
        key_info,
        master=frame)
    
    return keyboard_widget   

class KeyinDisplayToolWidget(ToolWidget):

    def keyin_display_init(self, keyin_display_frame):
        self.keyin_display_frame = keyin_display_frame
        self.keyboard_visible = True
        self.is_keyin_playing = False
        self.keyin_playing_cycle = []

        key_info = keyboardlayout.KeyInfo(
        margin=3,
        color=grey,
        txt_color=dark_grey,
        txt_font=font.Font(family='Arial', size=6),
        txt_padding=(1, 1))

        pressed_key_info = keyboardlayout.KeyInfo(
        margin=3,
        color='red',
        txt_color='white',
        txt_font=font.Font(family='Arial', size=6),
        txt_padding=(1,1))

        self.keyin_display = get_keyboard(keyin_display_frame,
               keyboardlayout.LayoutName.QWERTY, key_info)
        
        # hide keyboard frame
        self.switch_keyin_display()
    
    def switch_keyin_display(self):
        if self.keyboard_visible:
            
            self.keyin_display_frame.pack_forget()
            #self.keyin_display.grid_remove()
            self.keyboard_visible = False
        else:
            current_mode = common.postit_view.current_mode
            common.postit_view.all_modes[current_mode].notebook_frame.pack_forget()
            common.postit_view.all_modes[current_mode].tab_notebook.pack_forget()
            #common.postit_view.update_idletasks()
            self.keyin_display_frame.pack(side=tk.TOP, fill=tk.X)
            common.postit_view.all_modes[current_mode].notebook_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            common.postit_view.all_modes[current_mode].tab_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            #self.keyin_display.grid()
            self.keyboard_visible = True
    
# class EnterToolPostMixin:
#     def insert_into_editor(self, editor_text, 
#                            pressing=False, dragging=False,
#                            selecting=False, hovering=False):
#         if pressing and not selecting:
#             pass
#         elif pressing and selecting:
#             pass
#         elif dragging and not hovering:
#             pass
#         elif dragging and hovering:
#             pass

#     def insert_into_shell(self, shell_text, 
#                            pressing=False, dragging=False,
#                            selecting=False, hovering=False):
#         if pressing and not selecting:
#             pass
#         elif pressing and selecting:
#             pass
#         elif dragging and not hovering:
#             pass
#         elif dragging and hovering:
#             pass


class KeyinDisplayToolPostMixin:
    def post_init(self):
        self.drag_window = None
        self.drag_button = None
        self.drag_hover_selection = False
        self.hover_text_backup = ''
        #self.mouse_dragging = False
        # drag and press event
        #self.postit_button.bind("<B1-Motion>", self.on_mouse_drag)
        self.postit_button.bind("<Button-1>", self.on_mouse_release)
        #self.postit_button.config(cursor='arrow')

    def on_mouse_release(self, event):
        self.switch_keyin_display()

    # def insert_into_editor(self, editor_text, 
    #                        pressing=False, dragging=False,
    #                        selecting=False, hovering=False):
    #     if pressing and not selecting:
    #         editor_text.event_generate("<Return>")
        
    #     elif pressing and selecting:
    #         editor_text.event_generate("<BackSpace>")
    #         editor_text.event_generate("<Return>")

    #     elif dragging and not hovering:
    #         if editor_text.tag_ranges(tk.SEL):
    #             editor_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #         editor_text.event_generate("<Return>")

    #     elif dragging and hovering:
    #         editor_text.event_generate("<BackSpace>")
    #         editor_text.event_generate("<Return>")

    # def insert_into_shell(self, shell_text, 
    #                        pressing=False, dragging=False,
    #                        selecting=False, hovering=False):
    #     if pressing and not selecting:
    #         shell_text.event_generate("<Return>")

    #     elif pressing and selecting:
    #         shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #         #shell_text.event_generate("<BackSpace>")
    #         shell_text.event_generate("<Return>")

    #     elif dragging and not hovering:
    #         if shell_text.tag_ranges(tk.SEL):
    #             shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #         shell_text.event_generate("<Return>")

    #     elif dragging and hovering:
    #         shell_text.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #         #shell_text.event_generate("<BackSpace>")
    #         shell_text.event_generate("<Return>")

class KeyinDisplayToolPostit(KeyinDisplayToolWidget, 
                 ToolCodeMixin, BaseCode,
                 KeyinDisplayToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master, keyin_display_frame):
        self.widget_init(master, 'keyin_display')
        self.keyin_display_init(keyin_display_frame)
        self.code_init()
        self.post_init()
        #self.popup_init()