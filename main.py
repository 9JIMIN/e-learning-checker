import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secrets import username, userpass
import datetime
import time

form_class = uic.loadUiType("output.ui")[0]


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.PATH = "C:\Program Files (x86)\chromedriver.exe"
        self.URL = "https://e-campus.gnu.ac.kr/main/MainView.dunet"
        self.driver = webdriver.Chrome(self.PATH)
        self.driver.get(self.URL)

        # signal
        self.login_btn.clicked.connect(self.login)

    def get_data(self):
        try:
            # 공지사항- 입장
            notice = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='leftSnb']/li[4]/a"))
            )
            notice.click()

            # 등록일 확인(7일 이내)
            list_counts = self.driver.find_elements_by_css_selector("tbody > tr")
            for i in range(len(list_counts)):
                post_date = self.driver.find_element_by_xpath(f"//*[@id='con']/table/tbody/tr[{i+1}]/td[5]").text.split(".")
                time_post = datetime.datetime(int(post_date[0]), int(post_date[1]), int(post_date[2]))
                time_now = datetime.datetime.now()

                # 7일 이내의 공지사항은 들어가서 정보를 확인함.
                if (time_now - time_post).days < 7:
                    self.driver.find_elements_by_name("btn_board_view")[i].click()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "td_boarditem_title"))
                    )
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    notice_title = soup.find(id="td_boarditem_title").get_text().strip()
                    notice_date = soup.find(id="td_f_insert_dt").get_text().strip()
                    notice_eye = soup.find(id="td_boarditem_viewcnt").get_text().strip()
                    notice_content = soup.find(id="td_boarditem_content").get_text().strip()
                    self.notice_text.append(notice_title)
                    self.notice_text.append(notice_date)
                    self.notice_text.append(notice_eye)
                    self.notice_text.append(notice_content)
                    self.driver.find_element_by_xpath("//*[@id='leftSnb']/li[4]/a").click()

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
                # 과목 목록에 있는 애들을 하나하나 다 들어가봄.
                enter_class = self.driver.find_elements_by_css_selector("a.classin2")
                enter_class[i].click()

                # 해당 과목의 정보를 받아옴.
                self.get_data()

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