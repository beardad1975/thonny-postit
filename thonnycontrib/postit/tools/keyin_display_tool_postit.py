import time

import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from threading import Thread, Event
from queue import Queue

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
import keyboard

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

class AsyncKeyboardInput(Thread):
    def __init__(self, keyin_display):
        super().__init__()
        self.keyin_display = keyin_display
        self.last_key_event = None
        
    def run(self):
        while self.keyin_display.keyin_thread_running_event.is_set() :
            event = keyboard.read_event() 
            if self.keyin_display.keyboard_visible_event.is_set() and \
                self.keyin_display.is_focus_in_editor_or_shell() :
                if self.last_key_event != event :
                    #print('key event: ',event.event_type, event.name)
                    self.keyin_display.key_event_queue.put(event)
                    self.last_key_event = event
                else:
                    pass
                    #print('repeat keyin : ignore')
            else:
                pass
                #print("keyboard invisible : ignore")
        print('keyin thread stop')    
         


class KeyinDisplayToolWidget:

    def keyin_display_init(self, keyin_display_frame):
        """
        keyin thread started when first click tool-icon. then last to the end.
        """
        self.keyin_display_frame = keyin_display_frame
        self.is_keyin_playing = False
        self.keyin_playing_cycle = list()
        self.var_is_anchored_top = True
        self.key_event_queue = Queue()
        self.keyin_thread_running_event = Event() # thread event : default clear(false)

        self.is_fading = True
        self.fade_key_set = set()
        self.fade_key_time_dict = dict()
        self.startup_time = time.time() # time dict default value
        self.fade_total_seconds = 1
        self.fade_levels_num = 2
        self.fade_time_unit = self.fade_total_seconds/self.fade_levels_num
        self.fade_grey_lowbound = 150
        self.fade_grey_upbound = 220
        self.fade_grey_unit = (self.fade_grey_upbound - self.fade_grey_lowbound
                               ) / self.fade_levels_num  

        # print('---------------')
        # print(self.startup_time)
        # print(self.fade_time_unit)
        # print(self.fade_grey_unit)

        # normal key_info
        self.normal_key_info = keyboardlayout.KeyInfo(
            margin=3,
            color=grey,
            txt_color=dark_grey,
            txt_font=font.Font(family='Arial', size=6),
            txt_padding=(1, 1))

        # pressed key_info (red)
        self.pressed_key_info = keyboardlayout.KeyInfo(
            margin=3,
            color='red',
            txt_color='white',
            txt_font=font.Font(family='Arial', size=6),
            txt_padding=(1,1))

        # generate fade_key_info
        self.fade_keyinfo_list = []
        for i in range(self.fade_levels_num):
            c = self.fade_grey_lowbound + int(self.fade_grey_unit * i)
            color_string = '#%02x%02x%02x' % (c, c, c)
            keyinfo =  keyboardlayout.KeyInfo(
                            margin=3,
                            color=color_string,
                            txt_color=dark_grey,
                            txt_font=font.Font(family='Arial', size=6),
                            txt_padding=(1, 1))
            self.fade_keyinfo_list.append(keyinfo)

        #  packed inside library 
        self.keyin_display = get_keyboard(keyin_display_frame,
               keyboardlayout.LayoutName.QWERTY, self.normal_key_info)
        
        #  keyin display status default invisible
        self.keyboard_visible_event = Event() # thread event : default clear(false)
        self.keyin_display_frame.pack_forget()


    def switch_keyin_display(self):
        if self.keyboard_visible_event.is_set(): 
            self.keyin_display_frame.pack_forget()
            self.keyboard_visible_event.clear()
            #restore button
            self.postit_button.config(bg='SystemButtonFace')
        else: 
            self.keyboard_visible_event.set()
            self.monitor_keyin()

            if self.var_is_anchored_top:
                # re-pack keyin_display and notebook_frame
                current_mode = common.postit_view.current_mode
                common.postit_view.all_modes[current_mode].notebook_frame.pack_forget()
                common.postit_view.all_modes[current_mode].tab_notebook.pack_forget()
                self.keyin_display_frame.pack(side=tk.TOP, fill=tk.X)
                common.postit_view.all_modes[current_mode].notebook_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                common.postit_view.all_modes[current_mode].tab_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            else:
                self.keyin_display_frame.pack(side=tk.TOP, fill=tk.X)

            # highlight button
            self.postit_button.config(bg='green')
    
    def monitor_keyin(self):
        if self.keyin_thread.is_alive():
            # check the thread regularly
            if self.keyboard_visible_event.is_set():
                self.after(100, lambda: self.monitor_keyin())
            
            self.key_fade_effect()

            if not self.key_event_queue.empty():
                event = self.key_event_queue.get()
                key = key_dict.get(event.name)
                if key is None:
                    print('no key input mapping')
                    return
                # print(key)
                self.key_press_effect(event.event_type, key)

                 

    def key_press_effect(self, key_type, key):
            if key_type == 'down':
                self.keyin_display.update_key(key, self.pressed_key_info)
            elif key_type == 'up':
                if self.is_fading:
                    print('add key set and dict: ', key)
                    self.fade_key_set.add(key)
                    self.fade_key_time_dict[key] = time.time()
                else:
                    self.keyin_display.update_key(key, self.normal_key_info)

    def key_fade_effect(self):
        if not self.is_fading:
            return
        
        current_time = time.time()
        overdue_list = list()

        # fade key 
        for key in self.fade_key_set:
            pressed_time = self.fade_key_time_dict.get(key, self.startup_time)
            if pressed_time + self.fade_total_seconds <= current_time:
                # overdue
                overdue_list.append(key)
                continue
            
            # fade effect
            fade_level = int((current_time - pressed_time) / self.fade_time_unit) 
            keyinfo = self.fade_keyinfo_list[fade_level]
            self.keyin_display.update_key(key, keyinfo) 

        # overdue key process
        for key in overdue_list:
            self.fade_key_set.remove(key)
            self.keyin_display.update_key(key, self.normal_key_info)



    def is_focus_in_editor_or_shell(self):
        workbench = get_workbench()
        focus_widget = workbench.focus_get()
        if isinstance(focus_widget, CodeViewText) or isinstance(focus_widget, ShellText):
            return True
        else:
            return False
          

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

    def start_thread(self):
        self.keyin_thread = AsyncKeyboardInput(self)
        self.keyin_thread_running_event.set()
        self.keyin_thread.start()

        get_workbench().bind("WorkbenchClose", self._stop_keyin_thread, True)

        print("keyin thread started")

    def _stop_keyin_thread(self, event):
        self.keyin_thread_running_event.clear()
        print("stop keyin thread")

    def on_mouse_release(self, event):
        if not self.keyin_thread_running_event.is_set():
            self.start_thread()

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

class KeyinDisplayToolPopup:
    def popup_init(self):
        # button popup menu
        #f2 = font.Font(size=10, weight=font.NORMAL, family='Consolas')
        self.popup_menu = tk.Menu(self, tearoff=0, font=common.popup_menu_font)

        self.popup_menu.add_command(label="鍵盤在上", #value=1, 
                #variable=self.var_is_anchored_top,
                command=lambda top_pos=True: self.rearrange_keyin_display(top_pos))

        self.popup_menu.add_command(label="鍵盤在下", #value=0,  
                #variable=self.var_is_anchored_top,
                command=lambda top_pos=False: self.rearrange_keyin_display(top_pos))

        self.postit_button.bind("<Button-3>", self.popup)

    def popup(self, event):
        self.popup_menu.tk_popup(event.x_root, event.y_root)


    def rearrange_keyin_display(self, top_pos):
        if top_pos:
            self.var_is_anchored_top = True
        else:
            self.var_is_anchored_top = False


        if not self.keyboard_visible_event.is_set():
            # highlight button
            self.postit_button.config(bg='green')
            self.keyboard_visible_event.set()
            self.monitor_keyin()

        self.keyin_display_frame.pack_forget()

        if self.var_is_anchored_top:
            # re-pack keyin_display and notebook_frame
            current_mode = common.postit_view.current_mode
            common.postit_view.all_modes[current_mode].notebook_frame.pack_forget()
            common.postit_view.all_modes[current_mode].tab_notebook.pack_forget()
            self.keyin_display_frame.pack(side=tk.TOP, fill=tk.X)
            common.postit_view.all_modes[current_mode].notebook_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            common.postit_view.all_modes[current_mode].tab_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            self.keyin_display_frame.pack(side=tk.TOP, fill=tk.X)


class KeyinDisplayToolPostit(KeyinDisplayToolWidget, ToolWidget,
                 ToolCodeMixin, BaseCode,
                 KeyinDisplayToolPostMixin, BasePost, 
                 KeyinDisplayToolPopup):
    """ composite and mixin approach postit"""
    def __init__(self, master, keyin_display_frame):
        self.widget_init(master, 'keyin_display')
        self.keyin_display_init(keyin_display_frame)
        self.code_init()
        self.post_init()
        self.popup_init()