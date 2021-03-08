from microbit import *

暫停毫秒 = sleep

class base:
    pass

LED = base()
LED.捲動 = display.scroll
LED.設定像素 = display.set_pixel
LED.取得像素 = display.get_pixel
LED.清除 = display.clear
LED.顯示 = display.show
LED.感測亮度 = display.read_light_level

圖示 = base()
圖示.愛心 = Image.HEART
圖示.小愛心 = Image.HEART_SMALL