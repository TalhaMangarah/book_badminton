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
from logging.handlers import TimedRotatingFileHandler
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

# begin at 12:00AM and end at 12:05AM
begin_time = datetime.time(12, 00)
end_time = datetime.time(12, 10)
max_try = 10
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

#TODO: check if logged on to website before 12AM so we can be ready
def check_login():
        print('check login > getting booking site')
        # logging.info('Check login > getting booking site')
        driver.get(booking_site_url)
        # logging.info('Check login > got booking site')
        logged_on = False

        while not logged_on:
            is_during_running_time = check_current_time(begin_time, end_time)
            # check if the user is not logged in
            if not is_during_running_time[1]:
                if "MRMLogin" in driver.current_url:
                    print("check login > User is not logged in.")
                    email_field = driver.find_element(By.XPATH,'//*[@id="ctl00_MainContent_InputLogin"]')
                    print('check login > Inputting username: '+user_email)
                    email_field.send_keys(user_email)
                    print('check login > Inputting password')
                    password_field = driver.find_element(By.XPATH,'//*[@id="ctl00_MainContent_InputPassword"]')
                    password_field.send_keys(user_password)
                    print('check login > clicking on login button')
                    sleep(2)
                    driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_btnLogin"]').click()
                    sleep(3)
                    # logged_on = True
                    # print("check login > User is now logged in.")
                    # return(logged_on)
                else:
                    logged_on = True
                    print("check login > User is now logged in.")
                    # return(logged_on)
            else:
                print('check login > running during booking time therefore returned')
                return

# def book_sectors():

#     return

# print(check_current_time(begin_time, end_time))
def make_booking():
    try:
        print('getting booking site')
        driver.get(booking_site_url)
        sleep(1)
        print('checking logged in')
        check_login()
        # print('booking sector')
        # book_sectors()
    except Exception as e:
        print(e)
        return False
    finally:
        print('quitting driver/browser')
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
