from api import interface

from dotenv import dotenv_values

from datetime import datetime, timezone, timedelta

import requests

from seleniumwire import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from webdriver_manager.firefox import GeckoDriverManager

import time
from enum import Enum

from dotenv import dotenv_values


BASIC_URL = dotenv_values(".env")["tennis_url"]

class bookingtype(Enum):
    Einzel = "2e9f4d4e58e54f49a81ea784232fe153db36dd78_2_1621324718_8735"
    Doppel = "578970bbfa2b552c1a92e83f6ee7e3860f706529_2_1621324764_6619"
    Punktspiel = "a462cba9deee1921444481410b2174cd7627b476_2_1689074726_9677"
    Training = "9337e38bd38a88dcdfa0908b40edf68ab6fcae45_2_1621324821_2935"
    Veranstaltung = "1375f66b7e7929d891857f78209487705aa1e4fe_2_1690359640_4185"
    Vereinsmeisterschaft = "789fc5480a4d26d54f6101cc723c0640fc39c327_2_1621324938_1263"


COURT_MAPPING = ['52ce7b7381388998c73ca00f0057f2f47b41d4a0_2_1621324657_1525',
                '620d8c9ed644ac2543f00975a318533afe10f100_2_1621324665_4472',
                'eeb951e0fa031563f6afbef196e7383adb71c690_2_1689073795_4153',
                '4b234154183985d1001b0d6271df0141de1ff562_2_1689073824_8038',
                '3a8d7f4f061f367844010a5d856edc376dbb8fc3_2_1689073835_8023'
]


BOOK_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

class Platzbuchung(interface.TennisAPI):

    cookies: dict[str]

    def __init__(self):
        self.cookies = dict()
        self.authenticate()

    def authenticate(self) -> None:
        """fetches and updates values for phpcookie and xincodecookie"""

        # delete previous cookies
        del self.cookies

        self.cookies = dict()

        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

        driver.implicitly_wait(30)

        driver.get(BASIC_URL)

        with open('C:\\Users\\timsc\\Desktop\\auto\\bot_key.txt', 'r') as file:
            key = file.read()

        driver.find_element('name', 'login').send_keys("bot")

        # sign in
        el = driver.find_element('name', 'password')
        el.send_keys(key)
        el.send_keys(Keys.RETURN)

        time.sleep(5)

        driver.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul[1]/li[2]/a').click()

        time.sleep(2)
        
        driver.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul[1]/li[1]/a').click()

        driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div/div[2]/div/div/div/div[1]/span[1]/button[3]/span').click()

        time.sleep(1)

        driver.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul[1]/li[2]/a').click()

        time.sleep(2)
        
        driver.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul[1]/li[1]/a').click()

        time.sleep(1)

        driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div/div[2]/div/div/div/div[1]/span[1]/button[3]/span').click()

        # start bookinng
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div/div/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[7]/td[13]").click()
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div/div/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[7]/td[13]").click()

        # first submit button
        driver.find_element(By.XPATH, "/html/body/div[12]/div/div/div[2]/div/div/div[2]/div[1]/div[2]/span[2]/button[2]").click()
        
        # second submit button
        driver.find_element(By.XPATH, "/html/body/div[12]/div/div/div[2]/div/div/div[2]/div[2]/div[2]/span[2]/button[3]").click()

        # get phpsessionid
        for cookie in driver.get_cookies():

            if cookie["name"] != "PHPSESSID":
                continue

            self.cookies["cookie"] = f"PHPSESSID={cookie['value']}"
            break 

        # get x-incode cookie
        for request in driver.requests:
            if request.response:
                for item in request.headers.items():
                    if "x-incode" in item[0]:
                        if len(item[1]) == 40:
                            self.cookies[item[0]] = item[1]
                            driver.close()
                            del driver
                            return
                        
        driver.close()
        del driver      
        
        raise RuntimeError("Cookies not found")
    
    def book(self, court: int, date: str, starttime: int, stoptime: int, btype: bookingtype, info: str = "") -> None:
        """courtNo: int in [1, 5] date: YYYY-MM-TT (string) time: int in [0, 23] duration: int (time + duration) < 24, info: String"""

        if not isinstance(court, int):
            raise TypeError("Court must be of type int")
        
        if not isinstance(btype, bookingtype):
            raise TypeError("Booking type must be of type <bookingtype>")
        
        if not (isinstance(starttime, int) and isinstance(stoptime, int)):
            raise TypeError("Starttime and stoptime must be ints")
        elif starttime >= stoptime:
            raise ValueError("Stoptime must be greater than starttime")
        
        response = requests.post(url=BASIC_URL + "onCourt/bookings/data/create.json", 
                      data=f"type={btype.value}&creator=3a5606e1fa9d370acbd2aea5091ad94c30355b1a_5_1714226811_2933&from={date}T{starttime}%3A00%3A00.000Z&to={date}T{stoptime}%3A00%3A00.000Z&court={COURT_MAPPING[court - 1]}&guests=0&info={info}",
                      headers={**BOOK_HEADERS, **self.cookies})
        
        print(response.status_code)
        print(response.content)

        if response.status_code != 200:
            raise RuntimeError(f"Request to book failed: {response.content}")
        

    def addUser(self, vorname: str, nachname: str, psswd: str) -> None:
        json = {"titelVor":"",
                "vorname": vorname,
                "nachname": nachname,
                "titelNach":"",
                "strasse":"",
                "plz":"",
                "ort":"",
                "membershipnumber":"",
                "birthdate":"1930-01-01T00:00:00.000Z",
                "sex":"0",
                "email":"",
                "telefon":"",
                "telefon_privat":"",
                "telefon_beruf":"",
                "loginname": f"{vorname.lower()}.{nachname.lower()}",
                "membershipRoleDataGuid":"76f8ea4cf1df3e1af15f7ac37fcefb58c262f59d_2_1621325133_1678",
                "suspended":"0",
                "superUser":"0",
                "setPassword": psswd,
                "memberFeeAmount":"0",
                "membershipEntryDate": f'{datetime.now(timezone.utc).strftime("%Y-%m-%d")}T00:00:00.000Z',
                "hasPaidMemberFee":"true",
                "physicalKeys":"",
                "isResting":"0",
                "isDeactivated":"0",
                "zusatz1":"",
                "zusatz2":"",
                "info":""
            }
        
        response = requests.post(url=BASIC_URL + "REST/onCourt/onCourt_members", 
                      json=json,
                      headers={**BOOK_HEADERS, **self.cookies})
        
        print(response.status_code)
        print(response.content)

        if response.status_code != 200:
            raise RuntimeError(f"Request to add user failed: {response.content}")
        

    def bookMass(self, startdate: str, starttime: int, stoptime: int, court: int, weeks: int, btype: bookingtype, info: str = "") -> None:
        for i in range(weeks):
            date = f"{(datetime.strptime('2025-03-25', r'%Y-%m-%d') + timedelta(weeks=i)).strftime(r'%Y-%m-%d')}"

            self.book(court=court, date=date, starttime=starttime, stoptime=stoptime, btype=btype, info=info)