import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secrets import username, userpass

form_class = uic.loadUiType("e-learning-checker.ui")[0]


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.PATH = "C:\Program Files (x86)\chromedriver.exe"
        self.URL = "https://e-campus.gnu.ac.kr/main/MainView.dunet"
        self.driver = webdriver.Chrome(self.PATH)
        self.driver.get(self.URL)

        # signal
        self.notice_btn.clicked.connect(self.login)

    def get_notice(self):
        try:
            notice = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='leftSnb']/li[4]/a"))
            )
            notice.click()
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            notice_list = soup.find_all("td", {"class": "ta_l"})
            for one in notice_list:
                self.allList.append(one.get_text().split("(")[0].strip())
            print(self.allList)
            for i in range(len(self.allList)):
                self.notice_list.addItem(self.allList[i])
            self.driver.find_element_by_xpath("//*[@id='gnbmenu']/ul/li[3]/a").click()

        except Exception as e:
            print("get notice error")
            print(str(e))
            self.driver.quit()

    def loop_my_class(self):
        try:
            # explicit wait and click my course menu button
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "btn_change_info"))
            )
            self.driver.find_element_by_xpath("//*[@id='gnbmenu']/ul/li[3]/a").click()

            # enter class
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "rows1"))
            )
            enter_class = self.driver.find_elements_by_css_selector("a.classin2")
            for i in range(len(enter_class)):
                enter_class = self.driver.find_elements_by_css_selector("a.classin2")
                enter_class[i].click()
                self.allList=[]
                self.allList.append(enter_class[i].text.split("[")[0].strip())
                self.get_notice()



        except Exception as e:
            print("loop course error")
            print(str(e))
            self.driver.quit()

    def login(self):
        try:
            # explicit wait and login button click
            login_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "pop_login"))
            )
            login_link.click()

            # send user ID, PW
            user_id = self.driver.find_element_by_id("id")
            user_id.send_keys(username)
            user_pw = self.driver.find_element_by_id("pass")
            user_pw.send_keys(userpass)

            # close popup which block login button
            if self.driver.find_element_by_name("btn_layer_popup_close"):
                self.driver.find_element_by_name("btn_layer_popup_close").click()

            # login
            self.driver.find_element_by_id("login_img").click()

            self.loop_my_class()

        except Exception as e:
            print("login error")
            print(str(e))
            self.driver.quit()


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()