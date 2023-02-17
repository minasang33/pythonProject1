from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for  # Flask 라이브러리 선언
app = Flask(__name__)

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

url ="https://coinmarketcap.com/exchanges/upbit/"
oldList =[]

timeList1 = []
timeList2 = []
timeList3 = []
timeList4 = []
timeList5 = []
timeList6 = []

top10 = []

#스케줄 실행 코드
def scheduler():
    print("Scheduler is alive!")
def printListout(copyArr, preCnt, prevValue):
    pList = {
        "id": copyArr[0],
        "ticker": copyArr[1],
        "change": preCnt+"->"+copyArr[0],
        "prevValue": prevValue,
        "bw": int(preCnt) - int(copyArr[0])
    }
    return pList


def compareList(oldList, newList):
    global top10
    result = []
    for n in newList:
        for o in oldList:
            if n[1] == o[1]: #ticker 가 같은지 비교
                arr = printListout(n, o[0], o[6])
                result.append(arr)
                between = int(n[0]) - int(o[0])
                fArr = []
                bArr = []

                if len(top10) == 0:
                    top10.append(arr)
                else:

                    for x in top10:

                        if x['bw'] >= between:
                            bArr.append(x.copy())
                        else:
                            fArr.append(x.copy())

                    if len(fArr) == 0:
                        fArr = [arr.copy()]
                    else:
                        fArr += [arr]

                    if len(bArr) != 0:
                        fArr += bArr
                    top10 = fArr.copy()


                    if len(top10) > 10:
                        top10.pop()
                    print('top10', top10)
                break
    return result


def get_crolling():
    print('get_crolling start')
    global oldList

    # Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(3)
    # chrome 창을 원하는 가로폭과 세로폭으로 저정합니다.
    driver.set_window_size(1024, 968)

    driver.get(url)
    # res = requests.get(url)
    # page load
    driver.implicitly_wait(1)

    # 스크롤 내리기 이동 전 위치
    scroll_location = driver.execute_script("return document.body.scrollHeight")

    dropdown = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[2]/div/div[2]/div/div[2]/div')

    dropdown.click()
    driver.implicitly_wait(2)

    krw = driver.find_element(By.XPATH, '//*[@id="tippy-1"]/div/div[1]/div/div/button[2]')
    krw.click()
    driver.implicitly_wait(2)

    while True:
        try:
            # 현재 스크롤의 가장 아래로 내림
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

            # 전체 스크롤이 늘어날 때까지 대기
            time.sleep(1)

            # 늘어난 스크롤 높이
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            # print("sh", scroll_height)
            # 늘어난 스크롤 위치와 이동 전 위치 같으면(더 이상 스크롤이 늘어나지 않으면) 종료
            if scroll_location == scroll_height:
                more_list = driver.find_element(By.XPATH,
                                                '//*[@id="__next"]/div/div[1]/div[2]/div/div[3]/div[3]/button')
                more_list.click()
                time.sleep(3)

            # 같지 않으면 스크롤 위치 값을 수정하여 같아질 때까지 반복
            else:
                # 스크롤 위치값을 수정
                scroll_location = driver.execute_script("return document.body.scrollHeight")
        except:
            break

    res = driver.page_source

    bs = BeautifulSoup(res, 'html.parser')
    selector = "tbody > tr > td"
    columns = bs.select(selector)
    # print(columns)
    driver.close()
    # ticker_list = [x.text.strip().replace('/', '-') for x in columns]
    ticker_list = [x.text for x in columns]
    # print(ticker_list)

    newList = [ticker_list[i:i + 10] for i in range(0, len(ticker_list), 10)]
    result = []

    if len(oldList) == 0:
        oldList = newList
        for i in newList:
            result.append(printListout(i, i[0], i[6]))

    else:
        result = compareList(oldList, newList)

    print(result)
    return result

def findData(data):
    global timeList1, timeList2, timeList3, timeList4, timeList5, timeList6

    t = datetime.now().hour
    print("hour:", t)
    if 20 <= t:
        timeList6 = data
    elif 16 <= t:
        timeList5 = data
    elif 12 <= t:
        timeList4 = data
    elif 8 <= t:
        timeList3 = data
    elif 4 <= t:
        timeList2 = data
    else:
        timeList1 = data
@app.route('/scheduler')
def scheduler():
    global timeList1, timeList2, timeList3, timeList4, timeList5, timeList6
    sched = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')

    sched.remove_all_jobs()

    #findData( get_crolling())

     #timeList[currentIndex] = data

    # 매일 0시 실행
    @sched.scheduled_job('cron', hour='15', id='test_0')
    def job0():
        global timeList1
        timeList1 = get_crolling()
        print(f'job0 : {time.strftime("%H:%M:%S")}')
        print(timeList1)

    # 매일 4시 실행
    @sched.scheduled_job('cron', hour='19',id='test_1')
    def job1():
        global timeList2
        timeList2 = get_crolling()
        print(f'job1 : {time.strftime("%H:%M:%S")}')
        print(timeList2)

    # 매일 8시 실행
    @sched.scheduled_job('cron', hour='23', id='test_2')
    def job2():
        global timeList3
        timeList3 = get_crolling()
        print(f'job2 : {time.strftime("%H:%M:%S")}')
        print(timeList3)


    # 매일 12시 실행
    @sched.scheduled_job('cron', hour='1', id='test_3')
    def job3():
        global timeList4
        timeList4 = get_crolling()
        print(f'job3 : {time.strftime("%H:%M:%S")}')
        print(timeList4)


    # 매일 16시 실행
    @sched.scheduled_job('cron', hour='7', id='test_4')
    def job4():
        global timeList5
        timeList5 = get_crolling()
        print(f'job4 : {time.strftime("%H:%M:%S")}')
        print(timeList5)


    # 매일 20시 실행
    @sched.scheduled_job('cron', hour='11', id='test_5')
    def job5():
        global timeList6
        timeList6 = get_crolling()
        print(f'job5 : {time.strftime("%H:%M:%S")}')
        print(timeList6)

    sched.start()
    return redirect( url_for('index') )


@app.route('/') # 접속하는 url
def index():
    t = datetime.now().hour
    print("hour:", t)
    if 20 <= t:
        data = timeList6
        prevData = timeList5
    elif 16 <= t:
        data = timeList5
        prevData = timeList4
    elif 12 <= t:
        data = timeList4
        prevData = timeList3
    elif 8 <= t:
        data = timeList3
        prevData = timeList2
    elif 4 <= t:
        data = timeList2
        prevData = timeList1
    else:
        data = timeList1
        prevData = timeList6

    return render_template('index.html', title="bitfind23", time=datetime.now(), data=data, prev=prevData, top10=top10)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)