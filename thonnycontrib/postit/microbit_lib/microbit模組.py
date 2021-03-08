# microbit 模組 v0.1

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

按鈕A = base()
按鈕A.按下嗎 = button_a.is_pressed
按鈕A.按過嗎 = button_a.was_pressed
按鈕A.取得次數 = button_a.get_presses
按鈕B = base()
按鈕B.按下嗎 = button_b.is_pressed
按鈕B.按過嗎 = button_b.was_pressed
按鈕B.取得次數 = button_b.get_presses

加速度計 = base()
加速度計.取得x軸 = accelerometer.get_x
加速度計.取得y軸 = accelerometer.get_y
加速度計.取得z軸 = accelerometer.get_z
加速度計.取得3軸 = accelerometer.get_values
加速度計.目前動作 = accelerometer.current_gesture
加速度計.動作是 = accelerometer.is_gesture


圖示 = base()
圖示.愛心 = Image.HEART
圖示.小愛心 = Image.HEART_SMALL