from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secret import username, userpass

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("https://e-campus.gnu.ac.kr/main/MainView.dunet")

try:
    # 로그인 요소 기다렸다가, 클릭
    login_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pop_login"))
    )
    login_link.click()

    # 아이디, 비번 입력
    user_id = driver.find_element_by_id("id")
    user_id.send_keys(username)
    user_pw = driver.find_element_by_id("pass")
    user_pw.send_keys(userpass)

    # close popup 팝업창이 로그인 버튼을 막고 있어서 꺼줌.
    driver.find_element_by_name("btn_layer_popup_close").click()

    # 로그인 버튼 클릭!
    driver.find_element_by_id("login_img").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "btn_change_info"))
    )
    driver.find_element_by_xpath("//*[@id='gnbmenu']/ul/li[3]/a").click()

    # 진행중 강의에서 컴사코 입장
    my_courses = driver.find_element_by_xpath("//*[@id='rows1']/table/tbody").find_elements_by_xpath(".//*")
    com_sci_co = my_courses[3].find_element_by_xpath("//*[@id='rows1']/table/tbody/tr[3]/td[4]/span[1]/a")
    com_sci_co.find_element_by_xpath("//*[@id='rows1']/table/tbody/tr[3]/td[9]/a").click()

    # 입장후, 강의목록에서 진행률을 확인후, 100%가 아닌 애들은 교육을 시작한다.
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='con']/p[1]/span[2]"))
    )
    video_list = driver.find_elements_by_class_name("lenAct_list")

    # 리스트에서 강의만 골라냄
    removed = []
    for el in video_list:
        if el.find_element_by_css_selector("div.len_icon > img").get_attribute("src") == "http://e-campus.gnu.ac.kr/images/classroom/main/icon_learn01_lec.gif":
            removed.append(el)
    video_list = removed

    # 골라낸 강의에서 진행률이 100보다 낮은 애들을 찾아내서 클릭
    for video in video_list:
        progress = video.find_element_by_css_selector("dd.lec_dotline:nth-child(2)").text.strip() # strip()은 앞뒤 공백을 없애줌
        if int(progress.split("%")[0]) < 100:
            video.find_element_by_css_selector("a.lectureWindow>img").click()

except:
    print("error")
    driver.quit()



















class ElearningBot():
    def __init__(self):
        self.driver = webdriver.Chrome(PATH)

    def login(self):
        self.driver.get("https://e-campus.gnu.ac.kr/main/MainView.dunet")

        # user_id = self.driver.find_element_by_id("id")
        # user_id.send_keys("2015011984")
        #
        # user_pw = self.driver.find_element_by_id("pass")
        # user_pw.send_keys("dkdlvkzm1901")



