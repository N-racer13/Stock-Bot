import pyautogui
import time
import string

class OrderClass:
    def __init__(self, sc_counter, features):
        self.index = sc_counter
        self.quantity = features[0]
        self.ticker = features[1]
        self.date = features[2]
        self.strike = features[3]
        self.type = features[4]
        self.price = features[5]
        if not self.quantity:
            self.quantity = "1"

    def get_quantity(self):
        return self.quantity
    def get_ticker(self):
        return self.ticker
    def get_date(self):
        return self.date
    def get_strike(self):
        return self.strike
    def get_type(self):
        return self.type
    def get_price(self):
        return self.price

    def check_ticker(self):
        if len(self.ticker) < 5:
            return True
        else:
            return False
    
    def goto_trade(self, ticker_coordinates):
        x = ticker_coordinates[0]
        y = ticker_coordinates[1]
        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'a', interval=0.1)
        time.sleep(0.1)
        return

    def goto_search_ticker(self, ticker_coordinates):
        x = ticker_coordinates[0]
        y = ticker_coordinates[1]
        pyautogui.moveTo(x, y)
        pyautogui.doubleClick()
        pyautogui.write(self.ticker)
        pyautogui.press('enter')
        return 

    def is_equal(self, order):
        #print(order.get_quantity == self.quantity)
        if order.get_quantity() == self.quantity and order.get_ticker() == self.ticker and order.get_date() == self.date and order.get_strike() == self.strike and order.get_type() == self.type and order.get_price() == self.price:
            # give price range in case of repost (convert to float first)
            return True
        else:
            return False
    
    def convert_date(self):
        string_list = self.date.split('/')
        day = string_list[1]
        if day[0] == '0':
            day = day[1:]
        print(day)
        month = string_list[0]
        if month[0] == '0':
            month = month[1:]
        print(month)
        if len(string_list) == 3:
            year = string_list[2]
            if year[:2] == '20':
                year = year[2:]
            print(year)
        else:
            year = '00'
        return
        

    #def goto_date(self):
