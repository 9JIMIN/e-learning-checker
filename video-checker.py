from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secret import username, userpass
import time

PATH = "C:\Program Files (x86)\chromedriver.exe"
URL = "https://e-campus.gnu.ac.kr/main/MainView.dunet"

driver = webdriver.Chrome(PATH)
driver.get(URL)
html = driver.page_source

class VideoChecker():
    def login(self):
        try:
            # explicit wait and login button click
            login_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "pop_login"))
            )
            login_link.click()

            # send user ID, PW
            user_id = driver.find_element_by_id("id")
            user_id.send_keys(username)
            user_pw = driver.find_element_by_id("pass")
            user_pw.send_keys(userpass)

            # close popup which block login button
            if driver.find_element_by_name("btn_layer_popup_close"):
                driver.find_element_by_name("btn_layer_popup_close").click()

            # login
            driver.find_element_by_id("login_img").click()

            self.enter_course()

        except Exception as e:
            print("login error")
            print(str(e))
            driver.quit()

    def enter_course(self):
        try:
            # explicit wait and click my course menu button
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "btn_change_info"))
            )
            driver.find_element_by_xpath("//*[@id='gnbmenu']/ul/li[3]/a").click()

            # find entire courses, find target course, click the course
            my_courses = driver.find_element_by_xpath("//*[@id='rows1']/table/tbody").find_elements_by_xpath(".//*")
            com = my_courses[3].find_element_by_xpath("//*[@id='rows1']/table/tbody/tr[3]/td[4]/span[1]/a")
            com.find_element_by_xpath("//*[@id='rows1']/table/tbody/tr[3]/td[9]/a").click()
            self.play_video()

        except Exception as e:
            print("enter course error")
            print(str(e))
            driver.quit()

    def play_video(self):
        try:
            # explicit wait
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='con']/p[1]/span[2]"))
            )
            video_list = driver.find_elements_by_class_name("lenAct_list")

            # filters out things that are not videos.
            filtered = []
            for el in video_list:
                if el.find_element_by_css_selector("div.len_icon > img").get_attribute(
                        "src") == "http://e-campus.gnu.ac.kr/images/classroom/main/icon_learn01_lec.gif":
                    filtered.append(el)
            video_list = filtered

            # check the progress if it is lower than 100%, if so, click the view button
            for video in video_list:
                progress = video.find_element_by_css_selector(
                    "dd.lec_dotline:nth-child(2)")
                if int(progress.text.strip().split("%")[0]) < 100:
                    # get time to play(left)
                    time_left = int(progress.text.strip().split("/")[2].strip().split("분")[0]) - int(progress.text.strip().split("/")[1].split(":")[1].split("분")[0].strip())

                    video.find_element_by_css_selector("a.lectureWindow>img").click()

                    # switch to new window
                    time.sleep(1)
                    driver.switch_to.window(driver.window_handles[1])

                    # get progress time
                    current_time = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "current_time"))
                    )
                    current_time_min = int(current_time.text.split(":")[0])*60 + int(current_time.text.split(":")[1])

                    # wait until time to finish
                    waiting_time=time_left-current_time_min
                    time.sleep(waiting_time*60)

                    # when finish, close the window and switch previous window
                    driver.find_element_by_id("close_lectureWindow").click()

                    driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print("find video error")
            print(str(e))
            driver.quit()


VideoChecker().login()
