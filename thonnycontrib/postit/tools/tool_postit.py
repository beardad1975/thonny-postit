import tkinter as tk
from tkinter import ttk

from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny import get_workbench, get_shell

from ..base_postit import BaseCode, BasePost, BasePopup
from ..common import common_images

class ToolWidget(ttk.Frame):

    def widget_init(self, master, tool_name):
        # don't need to handle tab
        self.tool_name = tool_name
        self.tool_image = common_images[tool_name]

        ttk.Frame.__init__(self, master)        
        self.postit_button = tk.Button(self,  
                                        relief='groove',
                                        borderwidth=0,
                                        
                                        #fg=self.tab.font_color, 
                                        #bg=self.tab.fill_color,
                                        #justify='left', 
                                        #font=f,
                                        compound='right',
                                        image=self.tool_image,
                                        padx=0,
                                        pady=0, 
                                        )
        self.postit_button.pack(side=tk.LEFT, anchor='w')
        

        #self.note_label = ttk.Label(self, text='' )
        #self.note_label.pack(side=tk.LEFT, anchor='w',padx=5)

class ToolCodeMixin:
    def code_init(self):
        # tk var
        self.var_postfix_enter = tk.BooleanVar()
        self.var_postfix_enter.set(False)

        self.code_display = '' 
        self.note = ''
        self.code = ''
            
            #self.update_postit_code()

    def update_postit_code(self):
        pass


class ToolPostMixin:

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



    # def insert_into_editor(self, text_widget, selecting, dragging):
    #     if self.tool_name == 'backspace':
    #         if not dragging:
    #             text_widget.event_generate("<BackSpace>")
    #         else: # dragging
    #             if selecting:
    #                 text_widget.event_generate("<BackSpace>")
    #             else:
    #                 text_widget.delete(tk.INSERT + '-1c')

    #     elif self.tool_name == 'undo':
    #         text_widget.edit_undo()
    #     elif self.tool_name == 'redo':
    #         text_widget.edit_redo()
    #     elif self.tool_name == 'enter':
    #         if not dragging:
    #             if selecting :
    #                 text_widget.event_generate("<BackSpace>")
    #                 text_widget.event_generate("<Return>")
    #             else : # not selecting
    #                 text_widget.event_generate("<Return>")
    #         else: # dragging
    #             if selecting:
    #                 text_widget.event_generate("<BackSpace>")
    #                 text_widget.event_generate("<Return>")
    #             else:
    #                 text_widget.insert(tk.INSERT, '\n')
    #                 #stored_index = text_widget.index(tk.INSERT)
    #                 #text_widget.tag_remove(tk.SEL, '1.0')
    #                 #text_widget.mark_set(tk.INSERT, stored_index)
    #                 #text_widget.event_generate("<Return>")
    #     elif self.tool_name == 'indent':
    #         if not dragging:
    #             text_widget.indent_region()
    #         else: # dragging
    #             if selecting:
    #                 text_widget.indent_region()
    #             else:
    #                 text_widget.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #                 text_widget.indent_region()

    #     elif self.tool_name == 'dedent':
    #         if not dragging:
    #             text_widget.dedent_region()
    #         else: # dragging
    #             if selecting:
    #                 text_widget.dedent_region()
    #             else:
    #                 text_widget.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #                 text_widget.dedent_region()


    # def insert_into_shell(self, text_widget, selecting, dragging):
    #     if text_widget.compare(tk.INSERT, '>=' , 'input_start'): 
    #         if self.tool_name == 'backspace' and text_widget.compare(tk.INSERT, '>' , 'input_start'):
    #             # just bigger than, no equal than because of backspace del left char
    #             if not dragging:
    #                 if selecting:
    #                     if text_widget.compare(tk.SEL_FIRST, '>=', 'input_start'):
    #                         text_widget.event_generate("<BackSpace>")
    #                     elif text_widget.compare(tk.SEL_LAST, '>', 'input_start'):
    #                         #print('so co')
    #                         text_widget.delete('input_start', tk.SEL_LAST)
    #                         text_widget.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #                         text_widget.mark_set(tk.INSERT, 'input_start')
    #                 else:
    #                     text_widget.event_generate("<BackSpace>")
    #             else: # dragging
    #                 if selecting:
    #                     text_widget.event_generate("<BackSpace>")
    #                 else:
    #                     text_widget.delete(tk.INSERT + '-1c')                
    #         elif self.tool_name == 'undo':
    #             if text_widget.compare('input_start', '==','end-1c'):
    #                 # empty line
    #                 text_widget.event_generate("<Up>")
    #             else: # not empty line
    #                 text_widget.edit_undo()
    #         elif self.tool_name == 'redo':
    #             text_widget.edit_redo()
    #         elif self.tool_name == 'enter':
    #             if selecting:
    #                 text_widget.event_generate("<BackSpace>")
    #                 text_widget.event_generate("<Return>")
    #             else:# not selecting
    #                 text_widget.event_generate("<Return>")




    #         elif self.tool_name == 'indent':
    #             pass # when in shell
    #         elif self.tool_name == 'dedent':
    #             pass # when in shell

    #     else: # insert before input_start
    #         if self.tool_name == 'enter':
    #             text_widget.event_generate("<Return>")
    #         elif self.tool_name == 'backspace':
    #             # check if any selecting after input_start
    #             if text_widget.compare(tk.SEL_LAST, '>', 'input_start'):
    #                 text_widget.delete('input_start', tk.SEL_LAST)
    #                 text_widget.tag_remove(tk.SEL, tk.SEL_FIRST, tk.SEL_LAST)
    #                 text_widget.mark_set(tk.INSERT, 'input_start')
    #         elif self.tool_name == 'undo':
    #             text_widget.event_generate('<Up>')
    #         elif self.tool_name == 'redo':
    #             text_widget.event_generate('<Down>')





class ToolPostit(ToolWidget, 
                 ToolCodeMixin, BaseCode,
                 ToolPostMixin, BasePost, 
                 BasePopup):
    """ composite and mixin approach postit"""
    def __init__(self, master, tool_name):
        self.widget_init(master, tool_name)
        self.code_init()
        self.post_init()
        #self.popup_init()