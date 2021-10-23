###
###  無線通訊教學_伺服端程式 by beardad1975(2021.10)
###  (需以電腦上的python執行)
###

from collections import OrderedDict, Counter, deque
from random import randint, seed, choice
from time import sleep
import json

import PySimpleGUI as sg

# py4t 學習模組
import struct as 結構
from 語音模組 import *
from 聲音模組 import *
from 序列模組 import *


class Data:pass

# ---------------初始設定程式-------------------

def init():
    Data.font = '標楷體 32 normal'
    Data.font_small = '標楷體 20 normal'
    Data.title_color = '#484d54'
    Data.theme_background_color = sg.theme_element_background_color()
    #Data.theme_text_color = sg.theme_element_text_color()
    Data.highlight_color = 'red'
    Data.highlight_color2 = 'green'
    Data.readonly_color = 'PaleGreen1'
    Data.seed_num = 0
    
    Data.window_main = make_window_main()
    Data.window_callnum = None
    Data.window_feedback = None
    
    Data.default_names = '陳怡君\n林雅婷\n張承恩\n王采潔\n陳志明\n楊淑惠'
    Data.filename = 'data'
    
    Data.apikey_lowbound = 10000
    Data.apikey_upbound = 32767
    Data.client_code = 32  # 取號代碼
    Data.callnum_code = 64 # 叫號代碼
    Data.counter_max = 30 # 櫃台最大值
    Data.name_dict = OrderedDict()
    
    Data.answer_to_char_dict ={
            0 : '',
            1 : '1',
            2 : '2',
            3 : '3',
            4 : '4',
            5 : '是',
            6 : '否',
        }
    
    Data.lock_answer_content = '\n\n答\n\n案\n\n鎖\n\n定\n\n\n'
    Data.fill_answer_content = '\n\n\n請\n\n答\n\n題\n\n\n\n\n'
    Data.check_answer_content = '   ======== 答 對 的 人 是 ========'
    
    Data.client_max = 15
    Data.msg_max = 30
    Data.msg_show_num = 8
    
    Data.msg_deque = deque(maxlen=Data.msg_max)
    Data.client_deque = deque(maxlen=Data.client_max)
    
    
    
    Data.tts_start = False
    Data.序列連線 = None
    
    sound_init()
    load_data()

def sound_init():
    # prepare call sound
    設定語音音量(100)
    設定語音速度(1)

    音源e_up = 正弦波(659)
    音源c_up = 正弦波(523)
    
    聲音e_up = 音源e_up.轉成聲音(持續時間=150, 音量=-15.0)
    聲音c_up = 音源c_up.轉成聲音(持續時間=150, 音量=-15.0)
    聲音c_up = 聲音c_up.淡出(50)

    Data.叫號聲 = 聲音e_up.串接(聲音c_up, 交叉淡化=50)

    
    
    音源g = 正弦波(392)
    音源b = 正弦波(493)
    音源d_up = 正弦波(587)

    聲音g = 音源g.轉成聲音(持續時間=150, 音量=-10.0)
    聲音b = 音源b.轉成聲音(持續時間=150, 音量=-10.0)
    聲音d_up = 音源d_up.轉成聲音(持續時間=300, 音量=-10.0)
    聲音d_up = 聲音d_up.淡出(50)
    
    temp = 聲音g.串接(聲音b, 交叉淡化=50)
    Data.叫號聲2 = temp.串接(聲音d_up, 交叉淡化=50)
    
    
    音源a = 正弦波(440)
    音源f = 正弦波(348)
    
    
    聲音a = 音源a.轉成聲音(持續時間=200, 音量=-10.0)
    聲音f = 音源f.轉成聲音(持續時間=600, 音量=-10.0)
    
    temp = 聲音a.淡出(50)
    temp = temp + temp + temp + 聲音f
    Data.正解聲 = temp.淡出(100)
    
    
    

# ------圖形使用介面(含主程式、即時回饋、取號叫號 GUI)-----------

def make_window_main():
    
    tab_setup_layout = [
            [sg.Text('設定名單與apikey')],
            [sg.Text('-'*20)],
            [sg.Text('請在左方輸入名單(1行1個，限32筆)\napikey產生依隨機種子，種子建議用班級數字代入')],
            [sg.Text('')],
            [sg.Text('隨機種子'),
               sg.Combo([i for i in range(1,33)],key='-RAMDOM_SEED-',default_value=1, readonly=True)],
            [sg.Multiline('',key='-INPUT_NAMES-', size=(10, 15)),
               sg.Button('====>\n產生apikey\n(取代原有)', key='-MAKE_APIKEY-' ,size=(10,4)),
             sg.Multiline('',key='-APIKEY_RESULT-', size=(26, 15), disabled=True, background_color=Data.readonly_color),
             ],
            [sg.Button('範例名單')],
            [sg.Text('')],
        ]

    tab_feedback_layout = [
            [sg.Text('')],
            [sg.Text('')],
            [sg.Text('    '),sg.Button('開始 即時回饋模擬',key='-START_FEEDBACK-')] 
    ]

    
    tab_callnum_layout = [
            [sg.Text('')],
            [sg.Text('')],
            [sg.Text('    '),sg.Button('開始 取號叫號模擬',key='-START_CALLNUM-')]
        ]
    
    tab_group_layout = [[sg.Tab('設定apikey', tab_setup_layout),
                     sg.Tab('即時回饋',tab_feedback_layout),
                     sg.Tab('取號叫號', tab_callnum_layout),                     
                     ]]
    
    layout=[
                [ sg.Text('Micro:bit與無線通訊 伺服端程式\n')],
                [ sg.TabGroup(tab_group_layout)],                
            ]
    
    return sg.Window('主視窗', layout, finalize=True,
                     #enable_close_attempted_event=True,
                     )

def make_window_feedback():
    #   版面配置
    #   
    #   上方區塊
    #   -------
    #   左 | 右
    #   -------
    #   底部區塊
    
    # 上方區塊
    top_layout = [[ sg.Text('Micro:bit 即時回饋 模擬',
                            font=Data.font,
                            text_color='yellow',
                            ),
                    sg.Button('重新作答', key='-CLEAR_ALL-'),
                    sg.Button('鎖定答案', key='-LOCK_ANSWER-'),
                    sg.Text('   正確答案:'),
                    sg.Combo(('1','2','3','4','是','否'),key='-ANSWER_COMBO-',default_value='1', readonly=True),
                    sg.Button('對答案', key='-CHECK_ANSWER-'),
                    sg.Button('檢視成績', key='-VIEW_SCORE-'),
                    sg.Button('TEST'),
                    ]]
    
    top_column = sg.Column(
        top_layout,
        size=(1200,80),
        justification='center',
        )
    
    # 右區塊
    element_list = []
    for apikey, name in Data.name_dict.items():
        element = sg.Text('', key=apikey,font=Data.font, size=(10, 1))
        element_list.append(element)
    
    # fill up to 4-multiple and count rows numbers
    num = len(element_list)
    quotient = num // 4                      
    remainder = num % 4
    if remainder == 0:
        row_num = quotient
    else:  
        for i in range(4 - remainder):
            element_list.append(sg.Text(''))
        row_num = quotient + 1
        
    right_layout = [
            [sg.Text(Data.check_answer_content,font=Data.font, key='-CHECK_ANSWER_TXT-',
                     size=(40,1),
                     justification='left',
                     background_color=Data.highlight_color2,
                     )
             ],
        ]
    
    for i in range(row_num):
        temp_list = element_list[i*4:i*4+4]
        right_layout.append(temp_list)
    
    right_col = sg.Column(
        right_layout,
        justification='left',
        size=(1150, 640),
        )
    
    # 左區塊
    left_col = sg.Column(
        [[sg.Text(Data.lock_answer_content,key='-LOCK_ANSWER_TXT-',font=Data.font,background_color=Data.highlight_color)],
         
         ],
        size=(100, 640),
        )
    
    # 底部區塊
    feedback_format = "[h]apikey [h]0~6(0無 1 2 3 4 5是 6否)"
    
    bottom_layout = [
              [
                sg.Text('訊息格式',font=Data.font_small,background_color=Data.title_color),
                sg.Text(feedback_format,font=Data.font),
              ],
        
        ]
    bottom_column = sg.Column(
            bottom_layout,
            size=(1200,80), 
        )
    
    # 全部視窗版面
    layout = [
            [top_column],
            [sg.Text('- '*100)] ,
            [left_col,  right_col],
            [sg.Text('- '*100)] ,
            [bottom_column],
        
        ]
    
    return sg.Window('Micro:bit即時回饋', layout,
                       resizable=True,
                       finalize=True,
                       #size=(1200,800),
                    )

def make_window_callnum():
    #   版面配置
    #   
    #   上方區塊
    #   -------
    #   左 | 右
    #   -------
    #   底部區塊
    
    # 上方區塊
    top_layout = [[ sg.Text('Micro:bit 取號叫號 模擬',
                            font=Data.font,
                            #justification='center',
                            text_color='yellow',
                            ),
                    sg.Button('取號'),
                    sg.Button('叫號'),
                    sg.Button('清除等待'),
                    ]]
    top_column = sg.Column(
        top_layout,
        size=(1200,80),
        justification='center',
        #background_color='yellow'
        )

    # 右區塊
    right_layout = [
                     [sg.Text('叫號資訊',font=Data.font,
                     #expand_x=True,
                     #justification='center',
                     background_color=Data.title_color)]
                ]
    #left_layout += [[sg.Text(f'(小明) 來賓00{i}號請至{i}號櫃台',
    right_layout += [[sg.Text('',
                             key = f'-MSG{i}-',
                             font=Data.font,
                             #visible=False
                             )] for i in range(Data.msg_show_num)]

    right_col = sg.Column(
        right_layout,
        size=(900, 600),
        )

    # 左區塊
    left_col = sg.Column(
        [[sg.Text('等待0人',key='-WAIT_TITLE-',font=Data.font,background_color=Data.title_color)],
         [sg.Multiline('',key='-CLIENT_DEQUE-',font=Data.font_small, size=(18, 15), disabled=True,background_color=Data.readonly_color)],
         ],
        size=(350, 600),
        )

    
    # 底部區塊
    client_format = f"[h]key [h]{Data.client_code} [h]0"
    callnum_format = f'[h]key [h]{Data.callnum_code} [h]1~{Data.counter_max}'
    bottom_layout = [
            [ sg.Text('取號',font=Data.font_small,background_color=Data.title_color) , sg.Text(client_format,font=Data.font),
              sg.Text('叫號',font=Data.font_small,background_color=Data.title_color) ,sg.Text(callnum_format,font=Data.font) ],
        
        ]
    bottom_column = sg.Column(
            bottom_layout,
            size=(1200,80), 
        )

    # 全部視窗版面
    layout = [
            [top_column],
            [sg.Text('- '*100)] ,
            [left_col,  right_col],
            [sg.Text('- '*100)] ,
            [bottom_column],
        
        ]

    return sg.Window('Micro:bit取號叫號', layout,
                     resizable=True,
                     finalize=True,)



# ---------------主程式 相關函式-------------------

def make_apikey(values):
    names_str = values['-INPUT_NAMES-']
    if not names_str:
        sg.popup_error('需先輸入名單才能產生apikey')
    else:
        # generate apikey
        Data.name_dict = OrderedDict()
        over_32 = False
        # 固定隨機種子
        #print(values['-RAMDOM_SEED-'], type(values['-RAMDOM_SEED-']))
        Data.seed_num = values['-RAMDOM_SEED-']
        seed(Data.seed_num)
        name_list = names_str.split('\n')
        for i, n in enumerate(name_list):
            # 限32筆
            if i+1 > 32:
                over_32 = True
                break
            
            name = n.strip()
            # find apikey
            found = False
            while not found:
                key = randint(Data.apikey_lowbound, Data.apikey_upbound)
                if not key in Data.name_dict:
                    found = True
            # key型別為文字
            Data.name_dict[str(key)] = name
            
        save_data()
        #print(Data.name_dict)
        # show in multiline
        
        show_apikey()
        
        if over_32:
            sg.popup_ok('名單超過32筆，超過部份不使用')
        
def show_apikey():
    result = f'【列印發放用】(隨機種子:{Data.seed_num})\n'
    result += '序    名稱    apikey\n'
    result += ' ===============\n'
    
    for i, (key, name) in enumerate(Data.name_dict.items()):
        result += f'{i+1:2})  {name}  (apikey:{key})\n'
    
    result += f'\n【原始名單】(隨機種子:{Data.seed_num})\n'
    
    for key, name in Data.name_dict.items():
        result += f'{name}\n'
        
    Data.window_main['-APIKEY_RESULT-'].update(result)
    Data.window_main['-INPUT_NAMES-'].update('')

def save_data():
    # need to save:
    #     [Data.seed_num, Data.name_dict ]
    data_list = [Data.seed_num, Data.name_dict]

    with open(Data.filename, 'w', encoding='utf-8') as f:
                json.dump(data_list, f)
    print('資料存檔')

def load_data():
    # need to load:
    #     [Data.seed_num, Data.name_dict ]
    
    try:
        with open(Data.filename, 'r', encoding='utf-8') as f:
                Data.seed_num, Data.name_dict = json.load(f)
                
        print('資料載入')
        show_apikey()
    except FileNotFoundError:
        print('無資料檔')
        return           

# ---------------即時回饋 相關函式---------------

def init_feedback():
    Data.answer_locking = False
    Data.msg_deque.clear()
    Data.user_answer_dict = OrderedDict()
    Data.score_counter = Counter()
        
    Data.window_feedback['-ANSWER_COMBO-'].update(disabled=True)
    Data.window_feedback['-CHECK_ANSWER-'].update(disabled=True)
    Data.window_feedback['-VIEW_SCORE-'].update(disabled=True)
    Data.window_feedback['-CLEAR_ALL-'].update(disabled=True)

    Data.window_feedback['-LOCK_ANSWER_TXT-'].update(Data.fill_answer_content,background_color=Data.highlight_color2)
    Data.window_feedback['-CHECK_ANSWER_TXT-'].update('',background_color=Data.theme_background_color)

    # microbit connect
    Data.序列連線 = 連接microbit(例外錯誤=False, 讀取等待=0)
    sleep(0.3)
    Data.序列連線.傳送(b'hh')

def lock_answer():
    Data.answer_locking = True
    Data.window_feedback['-LOCK_ANSWER-'].update(disabled=True)
    
    Data.window_feedback['-CLEAR_ALL-'].update(disabled=False)
    Data.window_feedback['-ANSWER_COMBO-'].update(disabled=False)
    Data.window_feedback['-CHECK_ANSWER-'].update(disabled=False)
    Data.window_feedback['-VIEW_SCORE-'].update(disabled=False)
    
    Data.window_feedback['-LOCK_ANSWER_TXT-'].update(Data.lock_answer_content,background_color=Data.highlight_color)

    播放聲音(Data.叫號聲2)

def clear_all():
    Data.answer_locking = False
    Data.window_feedback['-LOCK_ANSWER-'].update(disabled=False)
    
    Data.window_feedback['-CLEAR_ALL-'].update(disabled=True)
    Data.window_feedback['-ANSWER_COMBO-'].update(disabled=True)
    Data.window_feedback['-CHECK_ANSWER-'].update(disabled=True)
    Data.window_feedback['-VIEW_SCORE-'].update(disabled=True)
    
    Data.window_feedback['-LOCK_ANSWER_TXT-'].update(Data.fill_answer_content,background_color=Data.highlight_color2)
    Data.window_feedback['-CHECK_ANSWER_TXT-'].update('',background_color=Data.theme_background_color)
    
    Data.user_answer_dict = OrderedDict()
    # answer ui clear
    for k in Data.name_dict.keys():
        Data.window_feedback[k].update('', background_color=Data.theme_background_color)

    播放聲音(Data.叫號聲2)

def check_answer(values):
    #print(values['-ANSWER_COMBO-'])
    Data.window_feedback['-CHECK_ANSWER-'].update(disabled=True)
    Data.window_feedback['-CHECK_ANSWER_TXT-'].update(Data.check_answer_content,background_color=Data.highlight_color2)

    correct_answer = values['-ANSWER_COMBO-']
    
    
    for apikey, answer_char  in Data.user_answer_dict.items() :
        if answer_char == correct_answer:
            Data.score_counter[apikey] += 1
            Data.window_feedback[apikey].update(background_color=Data.highlight_color2)
    

    播放聲音(Data.正解聲)

def view_score():
    #print(Data.score_counter)

    
    
    temp_score_list = []
    for apikey in Data.name_dict.keys():
        item = (apikey, Data.score_counter[apikey])
        temp_score_list.append(item)
    
    # sort by score
    temp_score_list = sorted(temp_score_list, key=lambda s: s[1], reverse=True)
    
    #print(temp_score_list)
    
    result = '序  名單  答對數\n =============\n'
    for i, (key , score) in  enumerate(temp_score_list):
        name = Data.name_dict[key]
        result += f'{i+1:2})  {name}   {score}\n'
    
    score_layout = [
            [sg.T('答對數與排名')],
            [sg.Multiline(result,key='-SCORE-', size=(20, 15),
                          disabled=True,
                          font=Data.font_small,
                          background_color=Data.readonly_color)],
            
        ]
    
    window_score = sg.Window('目前成績', score_layout,
                             finalize=True,
                             modal=True
                             )
    window_score.read(close=True)
    
    

def handle_msg_and_answer():
    
    feedback_read_serial_and_parse()
    
    msg_num = len(Data.msg_deque)
    if msg_num == 0:
        return
    else:
        if Data.answer_locking:
            Data.msg_deque.clear() 
        else: # not locking
            for n in range(msg_num):
                apikey, value = Data.msg_deque.popleft()
                
                answer_char = Data.answer_to_char_dict[value]
                name = Data.name_dict[apikey]
                
                Data.user_answer_dict[apikey] = answer_char
                if answer_char :
                    Data.window_feedback[apikey].update(f'{name}:{answer_char}')
                else:
                    Data.window_feedback[apikey].update(f'{name}')
            播放聲音(Data.叫號聲)

def feedback_read_serial_and_parse():
    # try read max 10 times
    for try_num in range(10):
        位元組資料 = Data.序列連線.接收(位元組=4)
        if not 位元組資料:
            # no data
            #print(f'serial read break({try_num})')
            break
        else:
            apikey, value = 結構.unpack('hh',位元組資料)
            apikey = str(apikey)
            #print(清單)
            # check msg
            if not apikey  in Data.name_dict.keys():
                print('<<即時回饋>> apikey錯誤: ', apikey)
                return
            
            # only one apikey in msg_deque (prevent busy)
            name = Data.name_dict[apikey]
            for k, _ in Data.msg_deque:
                
                if k == apikey :
                    
                    print(f'<<即時回饋>> 1次超過1個以上訊息，多的忽略(apikey:{apikey}, {name})')
                    return
                    
            if not 0 <= value <= 6 :
                print('<<即時回饋>> 數值超出範圍(0~6): ', value, f'apikey:{apikey}, {value} ')
                return
                
            
                    
            # put in deque
            Data.msg_deque.append((apikey, value))
            #print('serial msg ok')


# ---------------取號叫號 相關函式-------------------

def init_callnum():    
    

    # init deque counter and list
    Data.client_deque.clear()
    Data.msg_deque.clear()
    Data.client_counter = 0
    Data.msg_called_list = []

    # init elements
    update_client_ui()
    update_msg_called_ui()
    
    # microbit connect
    Data.序列連線 = 連接microbit(例外錯誤=False, 讀取等待=0)
    sleep(0.3)
    Data.序列連線.傳送(b'hhh')
    
def update_client_ui():
    result = ''
    for num, name in Data.client_deque:
        if name:
            result += f'{num}號來賓 by {name}\n'
        else:
            result += f'{num}號來賓\n'
    Data.window_callnum['-CLIENT_DEQUE-'].update(result)
    
    wait_num = len(Data.client_deque)
    Data.window_callnum['-WAIT_TITLE-'].update(f'等待{wait_num}人')

def update_msg_called_ui():
    total_called_num = len(Data.msg_called_list)
    if total_called_num == 0 :
        for i in range(Data.msg_show_num):
            Data.window_callnum[f'-MSG{i}-'].update('')
    elif total_called_num <= Data.msg_show_num:
        for i in range(Data.msg_show_num):
            Data.window_callnum[f'-MSG{i}-'].update('')
            
        for i, msg in enumerate(reversed(Data.msg_called_list)):
            Data.window_callnum[f'-MSG{i}-'].update(msg)
    else: # more than show_num
        newer_list = reversed(Data.msg_called_list[-Data.msg_show_num:])
        for i, msg in enumerate(newer_list):
            Data.window_callnum[f'-MSG{i}-'].update(msg)



def add_client(name=None):
    if len(Data.client_deque) >= Data.client_max:
        print(f'<<取號叫號>> 超過等待人數上限{Data.client_max}人')
        return           
    
    Data.client_counter += 1
    Data.client_deque.append((Data.client_counter, name))
    播放聲音(Data.叫號聲)

def handle_msg_and_client():
    #read serial
    callnum_read_serial_and_parse()
    
    
    # update client deque
    update_client_ui()
    
    #check voice
    if Data.tts_start:
        if not 語音說完了嗎():
            return
        else:
            Data.window_callnum['-MSG0-'].update(background_color=Data.theme_background_color)
            Data.tts_start = False
    #check deque
    if len(Data.msg_deque) == 0:
        return
    else:
        # got msg
        #print('len: ',len(Data.msg_queqe))
        apikey, code,  value = Data.msg_deque.popleft()
        
        if code == Data.callnum_code :     
            if len(Data.client_deque) == 0:
                print('<<取號叫號>> 目前沒有來賓排隊')
                return
            else:
                # got client
                guest_num, _ = Data.client_deque.popleft()
                name = Data.name_dict[apikey]
                name_txt = f' by {name}'
                sound_txt = f'來賓{guest_num}號請至{value}號櫃台' 
            
                Data.msg_called_list.append(sound_txt + name_txt)
                
                update_msg_called_ui()
            
                Data.window_callnum['-MSG0-'].update(background_color=Data.highlight_color)
                Data.tts_start = True
                播放聲音(Data.叫號聲2)
                語音合成(sound_txt, 等待=False)
        elif code == Data.client_code :
            name = Data.name_dict[apikey]
            add_client(name)

def callnum_read_serial_and_parse():
    # try read max 10 times
    for try_num in range(10):
        位元組資料 = Data.序列連線.接收(位元組=6)
        if not 位元組資料:
            # no data
            #print(f'serial read break({try_num})')
            break
        else:
            apikey, code, value = 結構.unpack('hhh',位元組資料)
            apikey = str(apikey)
            #print(清單)
            # check msg
            if not apikey  in Data.name_dict.keys():
                print('<<取號叫號>> apikey錯誤: ', apikey)
                return
            
            # only one apikey in msg_deque (prevent busy)
            name = Data.name_dict[apikey]
            for k, _, _ in Data.msg_deque:
                
                if k == apikey :
                    
                    print(f'<<取號叫號>> 1次超過1個以上訊息，多的忽略(apikey:{apikey}, {name})')
                    return
                    
            if code not in (Data.client_code, Data.callnum_code):
                print('<<取號叫號>> 指令碼錯誤: ', code, f'(apikey:{apikey}, {name} )')
                return
                
            if code == Data.callnum_code and not 1 <= value <= Data.counter_max :
                print('<<取號叫號>> 叫號櫃台({}) 超過範圍1~{}  (apikey:{}, {})'.format(value,Data.counter_max, apikey, name))
                return
                    
            # put in deque
            Data.msg_deque.append((apikey, code, value))
            #print('serial msg ok')   

# ---------------事件主迴圈-------------------

def event_loop():
    while True:
        window, event, values = sg.read_all_windows(timeout=100)
              
        # 主程式 事件--------
        
        if event == sg.WIN_CLOSED and window == Data.window_main:
            print(window)
            break

        if event == '-START_CALLNUM-' and not Data.window_callnum:
            if len(Data.name_dict) == 0 :
                sg.popup_error('需先產生apikey')
            
            else:
                Data.window_main.hide()
                Data.window_callnum = make_window_callnum()
                init_callnum()
                
        if event == '-START_FEEDBACK-' and not Data.window_feedback:
            if len(Data.name_dict) == 0 :
                sg.popup_error('需先產生apikey')
            
            else:
                Data.window_main.hide()
                Data.window_feedback = make_window_feedback()
                init_feedback()
            
        if window == Data.window_main and event == '範例名單':
            Data.window_main['-INPUT_NAMES-'].update(Data.default_names)
            
        if window == Data.window_main and event == '-MAKE_APIKEY-':
            make_apikey(values)        
        
        # 即時回饋 事件----------
        if window == Data.window_feedback and (event == sg.WIN_CLOSED) and sg.popup_yes_no('要離開即時回饋功能嗎?') == 'Yes':
            Data.window_feedback.close()
            Data.window_feedback = None
            Data.序列連線.關閉()
            Data.window_main.un_hide()
            
        if window == Data.window_feedback and event == '-LOCK_ANSWER-':
            lock_answer()
            
            
        if window == Data.window_feedback and event == '-CLEAR_ALL-':
            clear_all()
              
        if window == Data.window_feedback and event == '-CHECK_ANSWER-':      
            check_answer(values)
            
        if window == Data.window_feedback and event == '-VIEW_SCORE-':      
            view_score()
              
        if window == Data.window_feedback and event == 'TEST':
            for i in range(3):
                k = choice(list(Data.name_dict.keys()))
                Data.msg_deque.append((k, randint(0, 6)))
            
        if Data.window_feedback and event == '__TIMEOUT__':
            handle_msg_and_answer()
        
        
        # 取號叫號 事件----------
        
        if Data.window_callnum and event == '__TIMEOUT__':
            handle_msg_and_client()
        
        if window == Data.window_callnum and (event == sg.WIN_CLOSED) and sg.popup_yes_no('要離開取號叫號功能嗎?') == 'Yes':
            Data.window_callnum.close()
            Data.window_callnum = None
            Data.序列連線.關閉()
            Data.window_main.un_hide()
            
        if window == Data.window_callnum and event == '取號':
            key = choice(list(Data.name_dict.keys()))
            Data.msg_deque.append((key, Data.client_code, 0))
        if window == Data.window_callnum and event == '叫號':
            key = choice(list(Data.name_dict.keys()))
            
            num = randint(1,20)
            Data.msg_deque.append((key, Data.callnum_code, num))
        if window == Data.window_callnum and event == '清除等待':
            Data.client_deque.clear()
            
        

            
    Data.window_main.close()

# ---------------啟動函式-------------------

def main():
    init()
    event_loop()

if __name__ == '__main__':
    main()