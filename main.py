import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml
from bs4 import BeautifulSoup
from secrets import username, userpass
import time


class Content:
    def __init__(self, subject, title, date, content):
        self.subject = subject
        self.title = title
        self.date = date
        self.content = content


class Crawler:

    def cookies(self, url):
        """ 
        url을 받아서, 로그인을 한다. 
        쿠키를 리턴한다.
        """
        try:
            driver = webdriver.Chrome(
                "C:\Program Files (x86)\chromedriver.exe")
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
            return session

        except Exception as e:
            print("*********** session error ***********\n"+e)

    def lectureData(self, session):
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

            return data

        except Exception as e:
            print("lectureData error\n"+e)

    def notice(self, session, data_list):
        """
        강의별 데이터를 가지고, 
        공지사항전체를 리턴한다.
        """
        try:
            notice_list = []
            for i in data_list:
                form = {
                    "course_id": i[0],
                    "class_no": i[1]
                }
                html = session.post(
                    "http://e-campus.gnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet", data=form)
                soup = BeautifulSoup(html.content, "lxml")

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
                    notice_list.append(n.text.split("(")[0].strip())
            return notice_list

        except Exception as e:
            print("notice error\n"+e)

    def homework(self, session, data_list):
        """
        강의별 데이터를 가지고, 
        과제 전체를 리턴한다.
        """
        try:
            homework_list = []
            for i in data_list:
                form = {
                    "course_id": i[0],
                    "class_no": i[1]
                }
                html = session.post(
                    "http://e-campus.gnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet", data=form)
                soup = BeautifulSoup(html.content, "lxml")

                form = {
                    "mnid": soup.select("ul#leftSnb > li")[3].find(
                        "input", {"name": "mnid"}).attrs["value"]
                }
                html = session.post(
                    "http://e-campus.gnu.ac.kr/lms/class/report/stud/doListView.dunet", data=form)
                soup = BeautifulSoup(html.content, "lxml")

                task = soup.select("td.ta_l")
                for t in task:
                    homework_list.append(t.text.strip())
            return homework_list

        except Exception as e:
            print("homework error\n"+e)


crawler = Crawler()

cookies = crawler.cookies("http://e-campus.gnu.ac.kr/main/MainView.dunet")
session = crawler.session(cookies)
lecture_list = crawler.lectureData(session)
print(lecture_list)
notice_list = crawler.notice(session, lecture_list)
print(notice_list)
homework_list = crawler.homework(session, lecture_list)
print(homework_list)
