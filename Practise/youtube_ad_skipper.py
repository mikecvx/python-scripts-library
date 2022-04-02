import cv2
import numpy as np
import pyautogui
import time

template3 = cv2.imread("YouTube Ad Skipper Images\\template3.png", 0)
template4 = cv2.imread("YouTube Ad Skipper Images\\template4.png", 0)
template5 = cv2.imread("YouTube Ad Skipper Images\\template5.png", 0)
template6 = cv2.imread("YouTube Ad Skipper Images\\template6.png", 0)

threshold = 0.7

pyautogui.alert(text="Keep the mouse pointer on the top left corner of the screen to stop the program", title="Stopping Criteria")

while True:
    
    time.sleep(1)
    iml = pyautogui.screenshot()
    inl = np.asarray(iml.convert(mode="L"))

    res = cv2.matchTemplate(inl, template3, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if loc[0].size != 0:
        pyautogui.click(list(zip(*loc[::-1]))[0])
    
    res = cv2.matchTemplate(inl, template4, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if loc[0].size != 0:
        pyautogui.click(list(zip(*loc[::-1]))[0])
    
    res = cv2.matchTemplate(inl, template5, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if loc[0].size != 0:
        pyautogui.click(list(zip(*loc[::-1]))[0])

    res = cv2.matchTemplate(inl, template6, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if loc[0].size != 0:
        pyautogui.click(list(zip(*loc[::-1]))[0])
    
    if pyautogui.position() == (0, 0):
        pyautogui.alert(text="Adskipper is closed", title="Adskipper closed")
        break
