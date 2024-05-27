import numpy as np
import cv2
import pyautogui
import time
import datetime
import string
import win32api
import os
import pytesseract as tess
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from order_module import OrderClass

# Aight lets go mfs
def is_working_hours():
    now = datetime.datetime.now().time()
    start_time = datetime.time(0, 1)
    end_time = datetime.time(23, 59)
    return start_time <= now <= end_time

def calibrate():
    coordinates = []
    print('Calibration started')
    print('Click top left corner')
    while True:
        if win32api.GetKeyState(0x01) < 0:
            box_x, box_y = pyautogui.position()
            print('box_x, box_y obtained!')
            print(box_x, box_y)
            time.sleep(0.2)
            break
    print('Click bottom right corner')
    while True:
        if win32api.GetKeyState(0x01) < 0:
            box_x2, box_y2 = pyautogui.position()
            delta_x = box_x2 - box_x
            delta_y = box_y2 - box_y
            coordinates.append((box_x, box_y, delta_x, delta_y))
            print('deltas obtained!')
            print(delta_x, delta_y)
            time.sleep(0.2)
            break
    print('Click ticker search bar')
    while True:
        if win32api.GetKeyState(0x01) < 0:
            ticker_x, ticker_y = pyautogui.position()
            coordinates.append((ticker_x, ticker_y))
            print('ticker_x, ticker_y obtained!')
            print(ticker_x, ticker_y)
            time.sleep(0.2)
            break
    print('Top left dates (press A)')
    while True:
        if win32api.GetKeyState(0x41) < 0:
            date_x, date_y = pyautogui.position()
            coordinates.append((date_x, date_y))
            print('date_x, date_y obtained!')
            print(date_x, date_y)
            time.sleep(0.2)
            break
    print('Bottom right dates (press A)')
    while True:
        if win32api.GetKeyState(0x01) < 0:
            date_x2, date_y2 = pyautogui.position()
            d_delta_x = date_x2 - date_x
            d_delta_y = date_y2 - date_y
            coordinates.append((date_x, date_y, d_delta_x, d_delta_y))
            print('deltas obtained!')
            print(d_delta_x, d_delta_y)
            time.sleep(0.2)
            break
    return coordinates

def extract_string_between_markers(input_string, start_marker, end_marker):
    start_index = input_string.find(start_marker)
    end_index = input_string.find(end_marker, start_index + len(start_marker))
    if start_index != -1 and end_index != -1:
        result = input_string[start_index + len(start_marker):end_index]
        return result
    else:
        return None

def split_string_safely(input_string):
    cont_string = input_string.translate(str.maketrans("", "", string.whitespace))
    print(cont_string)
    result_list = []
    current_word = ""
    for char in cont_string:
        if current_word.isalpha() and char.isalpha():           # ticker & call/put
            current_word += char
        elif current_word.isalpha() and not char.isalpha():     # ticker & call/put
            result_list.append(current_word)
            current_word = ""
            current_word += char
        elif char == '$' or (not current_word.isalpha() and char.isalpha()):    # date & strike & price
            result_list.append(current_word)
            current_word = ""
            current_word += char
        elif not char.isalpha():                          # date & strike & price
            current_word += char
    result_list.append(current_word)
    return result_list


################# REQUIRED STEPS #################


# STEP 0: Calibrate the bounding box coordinates and points to click
calibrator = calibrate()
box_coordinates = calibrator[0]
ticker_coordinates = calibrator[1]
date_coordinates = calibrator[2]
sc_counter = 0
order_list = []
sleeptime = 10
fast_reiterate = 5

while is_working_hours():
    print("Working...")

    # STEP 1: Take screenshot from right channel to get latest messages about trade
    image = pyautogui.screenshot(region=(box_coordinates[0], box_coordinates[1], box_coordinates[2], box_coordinates[3]))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    sc_counter += 1     #be sure to include this as order feature
    sc_name = f"{'D:/Nathan Van Damme/Scripts/TradeBot/Screenshots'}/Screenshot_{sc_counter}.png"
    cv2.imwrite(sc_name, image)

    # STEP 2: Transelate image taken to string text 
    text = tess.image_to_string(image)
    #print(text)
    feature_string = extract_string_between_markers(text, 'Bought', '@everyone')

    # Create error handler!!!
    if feature_string:

        # STEP 3: Create order object with details (Tciker, strike price, call/put, date, price)
        features = split_string_safely(feature_string)
        print(features)
        order  = OrderClass(sc_counter, features)
        # Check if ticker length is legit, if not break and wait for next iteration!
        if not order.check_ticker():
            os.remove(sc_name)
            sc_counter -= 1
            print('Invalid ticker, screenshot deleted, reiterating...')
            time.sleep(fast_reiterate)
            continue
        # Check if order is already in list, if so delete and break
        if len(order_list) > 0:
            if order.is_equal(order_list[-1]):
                os.remove(sc_name)
                sc_counter -= 1
                print('Order already in list, reiterating...')
                time.sleep(sleeptime)
                continue
        order_list.append(order)

        # STEP 4: Look for ticker (either coordinate based or CV)
        order.goto_trade(ticker_coordinates)
        order.goto_search_ticker(ticker_coordinates)

        # STEP 5: Look for date and strike (will be difficult, string has to be transelated to image essentially)
        order.convert_date()
        # STEP 6: Move cursor to buy, look for price (CV) and but limit price and confirm (CV)
        # STEP 7: Sell (no idea how to do this is in TOS yet)


    # Delete screenshots that do not contain an order
    else:
        try:
            os.remove(sc_name)
            sc_counter -= 1
        except FileNotFoundError:
            print('Screenshot does not exist')
        


    time.sleep(sleeptime)


############# Safety ideas #############
# Take screenshot of ticker in search bar to be sure the correct ticker has been looked at
# Take another screenshot if ticker is longer than 4 characters
# Random check to see if order list is not negative?
# After ticker has been typed in, check if ticker exists by searching for error image
# Do this together with length in case ticker and date are confused
# Give date minimum length of 5 symbols
# Trade menu can be accessed with ctrl+1
# Old layout!!!
# Give headsup when wtarting program: close all tabs
# Separate folder from date finding screenshots
# Sleep after every mouse move command (to avoid suspision?)
# 'Weekly expiration' reject this shit, we aint doing weeklys
# close date after order has been selected

# 01/12/2023
# work with a small window for the date, if not the correct date, move window down and try again