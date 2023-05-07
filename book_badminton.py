import sys
import os
import time
import datetime
# import logging
# from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# from logging.handlers import TimedRotatingFileHandler
# import undetected_chromedriver as uc
from typing import Tuple
from time import sleep
# from datetime import time, datetime, timezone, timedelta

# # Log setting
# # Create a timed rotating log file handler that rotates every day
# handler = TimedRotatingFileHandler('./logs/booking.log', when='D', backupCount=7)
# # Set the formatter for the log messages
# formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
# handler.setFormatter(formatter)
# # Set the logging level to INFO
# logging.basicConfig(level=logging.INFO)
# # Add the handler to the root logger
# logging.getLogger().addHandler(handler)


load_dotenv()
# params
booking_site_url = os.getenv('BOOKING_URL')
selenium_url = os.getenv('SELENIUM_URL')
user_email = os.getenv("USER_EMAIL_ADDRESS")
user_password = os.getenv("USER_PASSWORD")

# logging.info('Environment parameters set')
# logging.debug('Booking site URL set to: '+booking_site_url)
# logging.debug('Selenium URL set to: '+selenium_url)
# logging.debug('User email set to: '+user_email)
# logging.debug('User password set')

# begin at 12:00AM and end at 12:10AM
begin_time = datetime.time(12, 00)
end_time = datetime.time(12, 10)
max_try = 10
# booking_attempt = 0
bookings_that_can_be_made_per_day = 2
booked_sectors = []
booked_courts = []
# Sector Priority List: 4, 1, 2, 5, 8, 6, 3 & 7.
sector_priority_order = [4, 1, 2, 5, 8, 6, 3, 7]
# Court Priority List = last priority, any court number (courts go from 1 to 4)
num_of_days_to_look_ahead = 6
num_days_in_week = 7

weekday_session_start_time = "18:00"
weekend_session_start_time = "12:00"

# booking_times_buttons = {
# '12:00':'/html/body/form/div[3]/div/div/div/section/div/div/div[1]/div[2]/div[1]/table/tbody/tr[14]/td[8]',
# '13:00':'/html/body/form/div[3]/div/div/div/section/div/div/div[1]/div[2]/div[1]/table/tbody/tr[15]/td[8]',
# '18:00':'/html/body/form/div[3]/div/div/div/section/div/div/div[1]/div[2]/div[1]/table/tbody/tr[20]/td[8]',
# '19:00':'/html/body/form/div[3]/div/div/div/section/div/div/div[1]/div[2]/div[1]/table/tbody/tr[21]/td[8]'
# }

booking_times_buttons = {
    '12:00': '//*[@id="ctl00_MainContent_cal_calbtn90"]',
    '13:00': '//*[@id="ctl00_MainContent_cal_calbtn97"]',
    '18:00': '/html/body/form/div[3]/div/div/div/section/div/div/div[1]/div[2]/div[1]/table/tbody/tr[20]/td[8]',
    '19:00': '/html/body/form/div[3]/div/div/div/section/div/div/div[1]/div[2]/div[1]/table/tbody/tr[21]/td[8]'
}
# logging.info('Begin and end times set')
# logging.debug(f'Begin time is {begin_time} and end time is {end_time}')

options = Options()
# comment out this line to see the process in chrome
# options.add_argument('--headless')
options.add_argument('Mozilla/5.0 (Windows NT 10.0; rv:113.0) Gecko/20100101 Firefox/113.0')
# options.add_argument(webdriver.ChromeOptions())
driver = webdriver.Remote(
    command_executor=selenium_url,
    options=options
)
# logging.info('Driver options set')
# logging.debug(f'Driver options are {options}')

# def test():
#     driver = uc.Chrome()
#     # driver.get('https://nowsecure.nl')

#     driver.get("https://www.whatsmyua.info/")
#     return

# driver.get(booking_site_url)
# sleep(1)
# check_login()
# driver.get_screenshot_as_file('/config/scripts/book_badminton/screenshot.png')

# print(check_current_time(begin_time, end_time))
# print('getting booking site')
# driver.get(booking_site_url)
# sleep(1)
# # print('checking logged in')
# # check_login()
# print('quitting driver')
# driver.quit()


def check_current_time(begin_time: datetime.time, end_time: datetime.time) -> Tuple[datetime.time, bool]:
    '''
    Check current time is between 00:00 and 00:15.
    Returns current time and if it is between begin and end time.
    '''

    dt_now = datetime.datetime.now()
    current_time = datetime.time(dt_now.hour, dt_now.minute, dt_now.second)
    is_between = begin_time <= current_time < end_time
    # logging.info('Checking current time and if between begin and end')
    # logging.debug(f'Time right now is {current_time}, is_between begin and end time returns {is_between}')
    # dt_now = datetime.now(bst)
    # current_time = time(dt_now.hour, dt_now.minute, dt_now.second)
    # return current_time, (begin_time <= current_time) and (current_time < end_time)
    return current_time, is_between

def get_day_of_week_x_days_ahead() -> int:
    '''
    Gets the current day of week via datetime - values are 0 to 6 with Monday being 0 and 6 being Sunday.
    The booking site shows 6 days ahead on the main booking page therefore we need the day 6 days ahead.
    '''
    current_day_of_week = datetime.datetime.now().weekday()
    dow_x_days_ahead = (current_day_of_week + num_of_days_to_look_ahead) % num_days_in_week
    return dow_x_days_ahead

def check_if_weekday(dow: int) -> bool:
    if dow >= 5:
        return False
    else: 
        return True

def does_booking_button_contain_available(booking_button_text: str) -> bool:
    if booking_button_text == 'Available':
        return True
    elif booking_button_text == 'Not Available':
        return False
    else:
        return Exception("Booking button text is not 'Available' or 'Not Available'")

#TODO: check if logged on to website before 12AM so we can be ready
def check_login():
        # is the get page again needed?
        # print('check login > getting booking site')
        # logging.info('Check login > getting booking site')
        # driver.get(booking_site_url)
        # logging.info('Check login > got booking site')
        logged_on = False

        while not logged_on:
            is_during_running_time = check_current_time(begin_time, end_time)
            # check if the user is not logged in
            if not is_during_running_time[1]:
                if "MRMLogin" in driver.current_url:
                    print("check_login: User is not logged in.")
                    email_field = driver.find_element(By.XPATH,'//*[@id="ctl00_MainContent_InputLogin"]')
                    print('check_login: Inputting username: '+user_email)
                    email_field.send_keys(user_email)
                    print('check_login: Inputting password')
                    password_field = driver.find_element(By.XPATH,'//*[@id="ctl00_MainContent_InputPassword"]')
                    password_field.send_keys(user_password)
                    print('check_login: clicking on login button')
                    # sleep(2)
                    login_button = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_btnLogin"]')
                    login_button.click()
                    # sleep(3)
                    # print('check login > clicking on top Badminton 40 mins')
                    # driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div/div/section/div[1]/div/div/div/div[2]/div[2]/div/div/ul/li[2]').click()
                    # sleep(3)
                    # logged_on = True
                    # print("check login > User is now logged in.")
                    # return(logged_on)
                else:
                    logged_on = True
                    print("check_login: User is now logged in.")
                    # return(logged_on)
            else:
                print('check_login: running during booking time therefore returned')
                return

def check_day_booking_available(is_weekday: bool, booking_attempt_num: int) -> bool:
    times = ['18:00', '19:00'] if is_weekday else ['12:00', '13:00']
    print(f'time to check is {times[booking_attempt_num]}')
    print(
        f'booking_times_buttons val is: {booking_times_buttons[times[booking_attempt_num]]}')
    booking_button_text = driver.find_element(
        By.XPATH, booking_times_buttons[times[booking_attempt_num]]).get_attribute("value")
    print(f'text in button is: {booking_button_text}')
    # return all([does_booking_button_contain_available(text) for text in booking_button_texts[:booking_attempt_num]])
    return does_booking_button_contain_available(booking_button_text)
    # booking_button_text = ''
    # booking_times = {
    #     1: booking
    # }
    # if is_weekday:
    #     if booking_attempt_num == 1:
    #         booking_button_text = driver.find_element(by.XPATH, booking_times_buttons['18:00']).text
    #         return does_booking_button_contain_available(booking_button_text)
    #     elif booking_attempt_num == 2:
    #         booking_button_text = driver.find_element(by.XPATH, booking_times_buttons['19:00']).text
    #         return does_booking_button_contain_available(booking_button_text)
    # else:
    #     if booking_attempt_num == 1:
    #         booking_button_text = driver.find_element(by.XPATH, booking_times_buttons['12:00']).text
    #         return does_booking_button_contain_available(booking_button_text)
    #     elif booking_attempt_num == 2:
    #         booking_button_text = driver.find_element(by.XPATH, booking_times_buttons['13:00']).text
    #         return does_booking_button_contain_available(booking_button_text)

def carry_out_booking():

    return


# TODO: check sectors availability with the priority, then click on it in book_sector_or_court function
def check_sectors_available():
    match sector:
        case 'sector4':

            return
        case _:
            return
    return

def check_courts_available():
    return


def book_sectors_or_court():
    print('book_sectors_or_court: clicking on top Badminton 40 mins')
    book_badminton_button = driver.find_element(
        By.XPATH, '//*[@id="ctl00_MainContent_MostRecentBookings1_Bookings_ctl01_bookingLink"]')
    book_badminton_button.click()
    # sleep(2)
    # booking_button_text1 = driver.find_element(
    #     By.XPATH, '// *[@id="ctl00_MainContent_cal_calbtn90"]')
    # print(booking_button_text1.get_attribute('value'))
    # print(f'text in button is: {booking_button_text1}')
    is_booking_day_weekday = check_if_weekday(get_day_of_week_x_days_ahead())
    print(f'is booking day a weekday? {is_booking_day_weekday}')
    booking_attempt = 0
    while booking_attempt < bookings_that_can_be_made_per_day:
        is_day_avail = check_day_booking_available(is_booking_day_weekday, booking_attempt)
        print(f'booking attempt is {booking_attempt+1}, bookling time is avail?: {is_day_avail}')
        if is_day_avail:
            return
        else:
            return 
        booking_attempt += 1
        # return

def make_booking():
    try:
        print('make_booking: Starting booking flow')
        print('make_booking: Getting booking site')
        driver.get(booking_site_url)
        # sleep(1)
        print('make_booking: Checking logged in')
        check_login()
        # while True:
        #     if not is_during_running_time:
        #         print(
        #             f'make_booking: Not Running the program. It is {current_time} and not between {begin_time} and {end_time}')



        print('booking sector')
        book_sectors_or_court()
        # book_sectors()
    except Exception as e:
        print(e)
        return False
    finally:
        print('make_booking: Quitting driver/browser')
        driver.quit()

# def try_booking():
#     '''
#     Try booking a reservation until either one reservation is made successfully or the attempt time reaches the max_try
#     '''
#     # initialize the params
#     current_time, is_during_running_time = check_current_time(begin_time, end_time)
#     reservation_completed = False
#     try_num = 1

#     # repreat booking a reservation every second
#     while True:
#       if not is_during_running_time:
#         print(f'Not Running the program. It is {current_time} and not between {begin_time} and {end_time}')

#         # sleep less as the time gets close to the begin_time
#         if current_time >= time(23, 59, 59):
#             sleep(0.001)
#         elif time(23, 59, 58) <= current_time < time(23, 59, 59):
#             sleep(0.5)
#         else:
#             sleep(1)

#         try_num += 1
#         current_time, is_during_running_time = check_current_time(begin_time, end_time)
#         continue

#       print(f'----- try : {try_num} -----')
#       # try to get ticket
#       reservation_completed = make_a_reservation(reservation_time, reservation_name)

#       if reservation_completed:
#           print('Got a ticket!!')
#           break
#       elif try_num == max_try:
#           print(f'Tried {try_num} times, but couldn\'t get tickets..')
#           break
#       else:
#           sleep(1)
#           try_num += 1
#           current_time, is_during_running_time = check_current_time(begin_time, end_time)


if __name__ == '__main__':
    # try_booking(reservation_time, reservation_name, max_try)
    # start_booking()
    make_booking()
