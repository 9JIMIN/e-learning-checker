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
import pprint
import time

form_class = uic.loadUiType("output.ui")[0]


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        # tools
        self.setupUi(self)
        self.PATH = "C:\Program Files (x86)\chromedriver.exe"
        self.URL = "https://e-campus.gnu.ac.kr/main/MainView.dunet"
        self.driver = webdriver.Chrome(self.PATH)
        self.driver.get(self.URL)

        # data
        self.notice_list = []
        self.task_list = []
        self.data_list = []
        self.video_list = []

        # signals
        self.login_btn.clicked.connect(self.login)

    def get_data(self):
        try:
            # 1. 과제제출
            # 과목 현황판이 로딩될때까지 기다림. 이거 왜 안되지??
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "con"))
            )
            # 로딩되면, 거기서 lenAct_list를 가져옴- 없으면 finally로 다음 정보받으러감.
            try:
                overview_list = self.driver.find_elements_by_class_name("lenAct_list")\
                    # 해당 클래스에서 과제만 골라냄.
                filtered = []
                for el in overview_list:
                    if el.find_element_by_css_selector("div.len_icon > img").get_attribute(
                            "src") == "http://e-campus.gnu.ac.kr/images/classroom/main/icon_learn02_homework.gif":
                        filtered.append(el)

                # 골라낸 과제를 클래스에서 삭제함 -> 강의목록이 됨.
                for el in filtered:
                    overview_list.remove(el)

                # lenAct_list로 불러온 요소들을 과제와 강의 목록으로 나눴음.
                videos = overview_list
                tasks = filtered

                # 과제리스트에 있는 애들중에서 '미제출' 상태인 애들을 골라내고 클릭을 함.
                for el in tasks:
                    if el.find_element_by_css_selector("dd.lec_dotline").text.strip() == "미제출":
                        el.find_element_by_css_selector(
                            "div.btn_lecture_view > a").click()

                        # 과제 정보가 로딩될때까지 기다림
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[@id='pop_frm_form']/table[1]"))
                        )

                        # 과제정보를 받아서 dict을 채움, 그걸 리스트에 추가
                        task_el = {"class": self.driver.find_element_by_xpath("//*[@id='pop_frm_form']/p[1]").text.strip(),
                                   "title": self.driver.find_element_by_xpath("//*[@id='pop_frm_form']/table[1]/tbody/tr[1]/td").text.strip(),
                                   "content": self.driver.find_element_by_xpath("//*[@id='pop_frm_form']/table[1]/tbody/tr[2]/td").text.strip(),
                                   "date": self.driver.find_element_by_xpath("//*[@id='pop_frm_form']/table[1]/tbody/tr[3]/td").text.strip()}
                        self.task_list.append(task_el)

                        self.driver.find_element_by_xpath(
                            "//*[@id='leftSnb']/li[7]/a").click()
                        time.sleep(1)

            # len_Act가 있던 없던, 과목창으로 돌아옴.
            finally:
                self.driver.find_element_by_xpath(
                    "//*[@id='leftSnb']/li[1]/a").click()
                print("과제 가져오기 끝")

            # 2. 자료실

            # 자료실 버튼을 로딩 기다렸다가 클릭한다.
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='leftSnb']/li[5]/a"))
            ).click()

            # 자료내용 로딩을 기다림.
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='leftSnb']/li[5]/a"))
            )

            # 최신 게시물만 찾음.
            list_counts = self.driver.find_elements_by_css_selector(
                "tbody > tr")
            print(list_counts[0].text)
            if list_counts[0].text.strip() != "등록된 게시물이 없습니다.":
                for i in range(len(list_counts)):
                    post_date = self.driver.find_element_by_xpath(
                        f"//*[@id='con']/table/tbody/tr[{i + 1}]/td[5]").text.split(".")
                    time_post = datetime.datetime(
                        int(post_date[0]), int(post_date[1]), int(post_date[2]))
                    time_now = datetime.datetime.now()

                    # 7일 이내의 자료는 들어가서 정보를 확인함.
                    if (time_now - time_post).days < 7:
                        self.driver.find_elements_by_name(
                            "btn_board_view")[i].click()
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.ID, "td_boarditem_title"))
                        )
                        # html 정보 파싱
                        html = self.driver.page_source
                        soup = BeautifulSoup(html, "html.parser")

                        # 파싱된 정보 저장
                        data_el = {"title": soup.find(id="td_boarditem_title").get_text().strip(),
                                   "date": soup.find(id="td_f_insert_dt").get_text().strip(),
                                   "views": soup.find(id="td_boarditem_viewcnt").get_text().strip(),
                                   "content": soup.find(id="td_boarditem_content").get_text().strip()}
                        self.data_list.append(data_el)

                        # 다시 자료실로 돌아감-> 반복
                        self.driver.find_element_by_xpath(
                            "//*[@id='leftSnb']/li[4]/a").click()

            # 자료실 다 확인하면 강의홈으로
            self.driver.find_element_by_xpath(
                "//*[@id='leftSnb']/li[1]/a").click()

            # 3. 공지사항- 입장
            notice = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='leftSnb']/li[4]/a"))
            )
            notice.click()

            # 등록일 확인(7일 이내)
            list_counts = self.driver.find_elements_by_css_selector(
                "tbody > tr")
            for i in range(len(list_counts)):
                post_date = self.driver.find_element_by_xpath(
                    f"//*[@id='con']/table/tbody/tr[{i+1}]/td[5]").text.split(".")
                time_post = datetime.datetime(
                    int(post_date[0]), int(post_date[1]), int(post_date[2]))
                time_now = datetime.datetime.now()

                # 7일 이내의 공지사항은 들어가서 정보를 확인함.
                if (time_now - time_post).days < 7:
                    self.driver.find_elements_by_name(
                        "btn_board_view")[i].click()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.ID, "td_boarditem_title"))
                    )
                    # html 정보 파싱
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, "html.parser")

                    # 파싱된 정보 저장
                    notice_el = {"title": soup.find(id="td_boarditem_title").get_text().strip(),
                                 "date": soup.find(id="td_f_insert_dt").get_text().strip(),
                                 "views": soup.find(id="td_boarditem_viewcnt").get_text().strip(),
                                 "content": soup.find(id="td_boarditem_content").get_text().strip()}
                    self.notice_list.append(notice_el)

                    # 다시 공지창으로 돌아감-> 반복
                    self.driver.find_element_by_xpath(
                        "//*[@id='leftSnb']/li[4]/a").click()

            # 공지사항을 다 확인하면 다시 전체과목창으로 돌아감.-> 그리고 다른 과목 공지확인인
            self.driver.find_element_by_xpath(
                "//*[@id='gnbmenu']/ul/li[3]/a").click()

        except Exception as e:
            print("get data error")
            print(str(e))
            self.driver.quit()

    def loop_class(self):
        try:
            # 로그인 버튼을 누른후에 왼쪽바 로딩되는거를 기다림, 마이페이지 클릭
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "btn_change_info"))
            )
            self.driver.find_element_by_xpath(
                "//*[@id='gnbmenu']/ul/li[3]/a").click()

            # 마이페이지에서 강의목록란이 로딩될때까지 기다림
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "rows1"))
            )

            # 모든 수업의 "강의실 입장" 링크 요소를 저장
            my_classes = self.driver.find_elements_by_css_selector(
                "a.classin2")

            # 링크를 하나씩 타고 들어가봄.
            for i in range(len(my_classes)):
                my_classes = self.driver.find_elements_by_css_selector(
                    "a.classin2")
                my_classes[i].click()

                # 해당 과목의 정보를 받아옴.
                self.get_data()

            # 정렬된 공지 리스트를 콘솔에 출력
            # pp = pprint.PrettyPrinter().pprint
            # pp(self.notice_list)
            # print(len(self.notice_list))

            # 받아온 전체 공지, 자료를 날짜 순으로 정렬
            self.notice_list = sorted(
                self.notice_list, key=lambda i: i['date'], reverse=True)
            self.data_list = sorted(
                self.data_list, key=lambda i: i["date"], reverse=True)
            self.task_list = sorted(
                self.task_list, key=lambda i: i["date"], reverse=True)

            # 받아온 공지 정보로 Qt에 위젯 생성
            for notice in self.notice_list:
                self.notice_text.append(notice["date"])
                self.notice_text.append(notice["views"])
                self.notice_text.append(notice["title"])
                self.notice_text.append(notice["content"])
                self.notice_text.append("-----------------")

            # 자료실 정보
            for data in self.data_list:
                self.data_text.append(data["date"])
                self.data_text.append(data["views"])
                self.data_text.append(data["title"])
                self.data_text.append(data["content"])
                self.data_text.append("-----------------")

            # 과제 정보
            for task in self.task_list:
                self.task_text.append(task["date"])
                self.task_text.append(task["class"])
                self.task_text.append(task["title"])
                self.task_text.append(task["content"])
                self.task_text.append("-----------------")

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
            try:
                self.driver.find_element_by_name(
                    "btn_layer_popup_close").click()

            finally:
                # login
                self.driver.find_element_by_id("login_img").click()

                self.loop_class()

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
