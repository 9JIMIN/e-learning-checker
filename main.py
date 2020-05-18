import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml
from bs4 import BeautifulSoup
from secrets import username, userpass
import time
import re
import sys
from PyQt5 import QtWidgets
from PyQt5 import uic


class Crawler:

    def cookies(self, url):
        """ 
        url을 받아서, 로그인을 한다. 
        쿠키를 리턴한다.
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(
                "C:\Program Files (x86)\chromedriver.exe", options=chrome_options)
            driver.get(url)
            driver.execute_script(
                "document.getElementById('loginArea').style.display='block'")

            driver.find_element_by_id("id").clear()
            driver.find_element_by_id("id").send_keys(username)

            driver.find_element_by_id("pass").clear()
            driver.find_element_by_id("pass").send_keys(userpass)

            driver.find_element_by_id("login_img").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "utill"))
            )

            return driver.get_cookies()

        except Exception as e:
            print("*********** login error ***********\n"+e)

    def session(self, cookie_list):
        """ 
        쿠키를 받아서, 
        세션 객체를 리턴한다.
        """
        try:
            with requests.Session() as session:
                headers = {
                    "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
                }
                session.headers.update(headers)
                session.cookies.update({c["name"]: c["value"]
                                        for c in cookie_list})
            print("session done!")
            return session

        except Exception as e:
            print("*********** session error ***********\n"+e)

    def lectureDataList(self, session):
        """ 
        세션을 받아서, 
        전체 강의 id, no의 list를 리턴한다.
        """
        try:
            html = session.get(
                "http://e-campus.gnu.ac.kr/lms/myLecture/doListView.dunet")
            soup = BeautifulSoup(html.content, "lxml")
            class_list = soup.find_all("a", {"class": "classin2"})

            data = []
            for i in class_list:
                course_id = i.attrs["course_id"]
                class_no = i.attrs["class_no"]
                data.append([course_id, class_no])

            print("lecture list done!")
            return data

        except Exception as e:
            print("lectureData error\n"+e)

    def lectrueSoup(self, session, lectureData):
        try:
            form = {
                "course_id": lectureData[0],
                "class_no": lectureData[1]
            }
            html = session.post(
                "http://e-campus.gnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet", data=form)

            soup = BeautifulSoup(html.content, "lxml")
            return soup

        except Exception as e:
            print("error\n"+e)

    def notice(self, session, soup):
        """
        강의별 데이터를 가지고, 
        공지사항전체를 리턴한다.
        """
        try:
            notice_list = []

            form = {
                "mnid": soup.select("ul#leftSnb > li")[3].find(
                    "input", {"name": "mnid"}).attrs["value"],
                "board_no": soup.select("ul#leftSnb > li")[3].find(
                    "input", {"name": "board_no"}).attrs["value"]
            }
            html = session.post(
                "http://e-campus.gnu.ac.kr/lms/class/boardItem/doListView.dunet", data=form)
            soup = BeautifulSoup(html.content, "lxml")

            notice = soup.select("td.ta_l >a")
            for n in notice:
                form = {
                    "page": soup.select_one("form#frm").select_one("#page").attrs["value"],
                    "rows": soup.select_one("form#frm").select_one("#rows").attrs["value"],
                    "sidx": soup.select_one("form#frm").select_one("#sidx").attrs["value"],
                    "sord": soup.select_one("form#frm").select_one("#sord").attrs["value"],
                    "course_id": soup.select_one("form#frm").select_one("#course_id").attrs["value"],
                    "class_no": soup.select_one("form#frm").select_one("#class_no").attrs["value"],
                    "menu_type": soup.select_one("form#frm").select_one("#menu_type").attrs["value"],
                    "q_mnid": soup.select_one("form#frm").select_one("#q_mnid").attrs["value"],
                    "board_no": soup.select_one("form#frm").select_one("#board_no").attrs["value"],
                    "boarditem_no": n.attrs["id"]
                }
                html = session.post(
                    "http://e-campus.gnu.ac.kr/lms/class/boardItem/doViewBoardItem.dunet", data=form)
                item_soup = BeautifulSoup(html.content, "lxml")

                subject = item_soup.select_one(
                    "div#con > p").text.split("|")[1].strip()
                title = item_soup.select_one(
                    "td#td_boarditem_title").text.strip()
                date = item_soup.select_one("td#td_f_insert_dt").text.strip()
                view = item_soup.select_one(
                    "td#td_boarditem_viewcnt").text.strip()
                content = item_soup.select_one(
                    "#td_boarditem_content").text.strip()

                content = dict(subject=subject, title=title,
                               date=date, content=content, view=view)

                notice_list.append(content)
            return notice_list

        except Exception as e:
            print("notice error\n"+e)

    def homework(self, session, soup):
        """
        강의별 데이터를 가지고, 
        과제 전체를 리턴한다.
        """
        try:
            homework_list = []

            form = {
                "mnid": soup.select("ul#leftSnb > li")[3].find(
                    "input", {"name": "mnid"}).attrs["value"]
            }
            html = session.post(
                "http://e-campus.gnu.ac.kr/lms/class/report/stud/doListView.dunet", data=form)
            soup = BeautifulSoup(html.content, "lxml")

            task = soup.select("td.ta_l a")
            for t in task:
                form = {
                    "report_no": re.findall(r"'(\w+)'", t.attrs["onclick"])[0],
                    "apply_yn": re.findall(r"'(\w+)'", t.attrs["onclick"])[1],
                    "report_seq": re.findall(r"'(\w+)'", t.attrs["onclick"])[2],
                    "report_modify_yn": re.findall(r"'(\w+)'", t.attrs["onclick"])[3],
                    "req_asp_id": soup.select("form#list_frm_form td>input")[0].attrs["value"],
                    "page": soup.select("form#list_frm_form td>input")[1].attrs["value"],
                    "rows": soup.select("form#list_frm_form td>input")[2].attrs["value"],
                    "sidx": soup.select("form#list_frm_form td>input")[3].attrs["value"],
                    "sord": soup.select("form#list_frm_form td>input")[4].attrs["value"],
                    "course_id": soup.select("form#list_frm_form td>input")[10].attrs["value"],
                    "class_no": soup.select("form#list_frm_form td>input")[11].attrs["value"],
                    "mode": "U",
                    "ie_version": "NO10"
                }

                html = session.post(
                    "http://e-campus.gnu.ac.kr/lms/class/report/stud/doFormReport.dunet", data=form)
                task_soup = BeautifulSoup(html.content, "lxml")

                subject = task_soup.select_one(
                    "div#con p").text.split("|")[1].strip()
                title = task_soup.select(
                    "table.datatable>tbody>tr")[0].td.text.strip()
                content = task_soup.select(
                    "table.datatable>tbody>tr")[1].td.text.strip()
                date = task_soup.select(
                    "table.datatable>tbody>tr")[2].td.text.strip()
                submit = re.findall(r"'(\w+)'", t.attrs["onclick"])[1]

                content = dict(subject=subject, title=title,
                               date=date, content=content, submit=submit)

                homework_list.append(content)
            return homework_list

        except Exception as e:
            print("homework error\n"+e)


def getList():
    crawler = Crawler()

    cookies = crawler.cookies("http://e-campus.gnu.ac.kr/main/MainView.dunet")

    session = crawler.session(cookies)
    lecture_list = crawler.lectureDataList(session)

    notice_list = []
    homework_list = []

    for i in lecture_list:
        lecture_soup = crawler.lectrueSoup(session, i)
        notice_list.extend(crawler.notice(session, lecture_soup))
        homework_list.extend(crawler.homework(session, lecture_soup))

    notice_list = sorted(notice_list, key=lambda i: i['date'], reverse=True)
    homework_list = sorted(
        homework_list, key=lambda i: i['date'], reverse=True)
    return [notice_list, homework_list]


form_class = uic.loadUiType("output.ui")[0]


class WindowClass(QtWidgets.QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.getBtn.clicked.connect(self.getData)

    def getData(self):
        [notice_list, homework_list] = getList()

        for i in notice_list:
            self.noticeView.append(i["subject"])
            self.noticeView.append(i["title"])
            self.noticeView.append(i["view"])
            self.noticeView.append(i["date"])
            self.noticeView.append(i["content"])
            self.noticeView.append("-"*10)

        for i in homework_list:
            self.homeworkView.append(i["subject"])
            self.homeworkView.append(i["title"])
            self.homeworkView.append(i["date"])
            self.homeworkView.append(i["submit"])
            self.homeworkView.append(i["content"])
            self.homeworkView.append("-"*10)


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QtWidgets.QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
