import radio as 無線電
import ustruct as 結構
import utime as 時間
from microbit import button_a as A鈕, button_b as B鈕

# 請填入你的apikey
apikey = 0

無線電.on()

while True :
    if A鈕.is_pressed():
        # h:16位元資料
        位元組資料 = 結構.pack('hh',apikey, 0)
        無線電.send_bytes(位元組資料)
        
    時間.sleep_ms(100)