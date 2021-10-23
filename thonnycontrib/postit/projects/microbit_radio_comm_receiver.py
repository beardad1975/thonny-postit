###
###  無線通訊教學_Microbit接受器程式 by beardad1975(2021.10)
###  (需以Microbit上的micropython執行)
###

import radio as 無線廣播
import utime as 時間
from microbit import uart as 序列
from microbit import display as 燈光, Image as 圖示
from microbit import button_a as A鈕, button_b as B鈕


序列.init(115200)
無線廣播.on()

data_format = ''
bytes_num = 0
start_receiving = False

燈光.show('S')

while True :
    if 序列.any():
        位元組 = 序列.read()
        
        data_string = str(位元組, 'ascii')
        if data_string == 'hhh':
            data_format = 'hhh'
            bytes_num = 6
            start_receiving = True
            燈光.show(bytes_num)
        elif data_string == 'hh':
            data_format = 'hh'
            bytes_num = 4
            start_receiving = True
            燈光.show(bytes_num)
        
    
    
    if start_receiving:
        接收位元組 = 無線廣播.receive_bytes()
        if 接收位元組:
            if len(接收位元組) == bytes_num:             
                序列.write(接收位元組)
                燈光.show('.')           
                時間.sleep_ms(50)
                燈光.clear()
            else: # wrong bytes_num
                燈光.show('x')
                時間.sleep_ms(50)
                燈光.clear()
    else:
        時間.sleep_ms(50)
    
    if A鈕.is_pressed():
        燈光.show(bytes_num)           
        時間.sleep_ms(50)
        燈光.clear()
            
    
