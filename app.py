from datetime import datetime, timedelta
import time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for  # Flask 라이브러리 선언
app = Flask(__name__)

import requests

url ="https://coinmarketcap.com/exchanges/upbit/"


timeList1 = []
timeList2 = []
timeList3 = []
timeList4 = []
timeList5 = []
timeList6 = []

top20 = []
#억단위로 표기
def get_wonwha_string(num_wonwha_amout):
    """ 입력된 원화를 4자리단위 한글로 변환한다 """
    str_result = ""  # 결과문자열 초기화
    str_sign = ""  # 부호 초기화
    num_change = num_wonwha_amout  # 최초값을 모두 잔돈에 넣는다

    if num_change == 0:  # 0원이면
        str_result = "0"
    elif num_change < 0:  # 음수이면
        str_sign = "-"  # 음의 부호(Negative Sign)를 붙이고
        num_change = abs(num_change)  # 절대값으로 변환 후 변환을 계속한다

    if num_change >= 100000000:  # 1억 이상
        str_result += f"{int(num_change // 100000000):,}억"
        num_change = num_change % 100000000
    elif num_change >= 10000:  # 1만 이상
        str_result += f" {int(num_change // 10000):,}만"
        num_change = num_change % 10000
    elif num_change >= 1:  # 1 이상
        str_result += f" {int(num_change):,}"

    str_result = str_result.strip()  # Return a copy of the string with the leading and trailing characters removed
    if len(str_result) >= 1:
        return str_sign + str_result + "원"
    else:
        return str_result


# utc -> kst
def convert_kst(dt_tm_utc):
    #dt_tm_utc = datetime.strptime(utc_string, '%Y-%m-%d %H:%M:%S')
    tm_kst = dt_tm_utc + timedelta(hours=9)
    # str_datetime = tm_kst.strftime('%Y-%m-%d %H:%M:%S')
    return tm_kst

#스케줄 실행 코드
def printListout(copyArr, preCnt, prevValue):

    pList = {
        "id": copyArr['idx'],
        "ticker": copyArr['ticker'],
        "change": str(preCnt)+"->"+str(copyArr['idx']),
        "value": copyArr['volume'],
        "prevValue": prevValue,
        "bw": preCnt - copyArr['idx']
    }
    return pList


def compareList(oldList, newList):
    result = []
    for i, n in enumerate(newList):
        for j, o in enumerate(oldList):
            if n['ticker'] == o['ticker']: #ticker 가 같은지 비교
                arr = printListout(n, o['id'], o['prevValue'])
                result.append(arr)
    return result

def get_crolling():
    print('get_crolling start')
    oldList = []
    today = convert_kst(datetime.now())
    t = today.hour
    print("hour:", t)
    if 20 <= t-4:
        oldList = timeList5
    elif 16 <= t-4:
        oldList = timeList4
    elif 12 <= t-4:
        oldList = timeList3
    elif 8 <= t-4:
        oldList = timeList2
    elif 4 <= t-4:
        oldList = timeList1
    else:
        oldList = timeList6
    print("oldList=============================")
    print(oldList)

    url1 = "https://api.upbit.com/v1/market/all"
    response = requests.get(url1)
    markets = response.json()

    krw_markets = []
    for market in markets:
        if market['market'].startswith('KRW'):
            krw_markets.append(market['market'])

    tickers = []
    for market in krw_markets:
        ticker = market.replace("KRW-", "")
        tickers.append(ticker)
    url2 = "https://api.upbit.com/v1/ticker"
    params = {"markets": ','.join(krw_markets)}
    response = requests.get(url2, params=params)
    tickers_data = response.json()

    volumes = []
    for i, ticker in enumerate(tickers, start=1):
        for ticker_data in tickers_data:
            if ticker_data['market'].startswith(f'KRW-{ticker}'):
                volumes.append({'ticker': ticker, 'volume': float(ticker_data['acc_trade_price'])})

    top_volumes = sorted(volumes, key=lambda x: x['volume'], reverse=True)

    for i, volume in enumerate(top_volumes):
        volume['idx'] = i+1
        volume['volume'] = get_wonwha_string(volume['volume'])
        print(f"{i + 1}. {volume['ticker']}: {volume['volume']}")

    result = []

    if len(oldList) == 0:
        oldList = top_volumes
        for volume in top_volumes:
            result.append(
                printListout(volume, volume['idx'], f"{volume['volume']}")
            )
    else:
        result = compareList(oldList, top_volumes)

    return result

def findData(data):
    global timeList1, timeList2, timeList3, timeList4, timeList5, timeList6
    today = convert_kst(datetime.now())
    t = today.hour
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

def getTop20(oldList, newList):
    result = []
    for i, n in enumerate(newList):
        for j, o in enumerate(oldList):
            if n['ticker'] == o['ticker']:  # ticker 가 같은지 비교
                arr = {
                    "id": n['id'],
                    "ticker": n['ticker'],
                    "change": str(j)+"->"+str(n['id']),
                    "value": n['value'],
                    "prevValue": o['value'],
                    "bw": j - n['id']
                }
                result.append(arr)
    return result

def job0():
    global timeList1, top20
    timeList1 = get_crolling()
    top20 = getTop20(timeList6, timeList1)
    print(f'job0 : {time.strftime("%H:%M:%S")}')
    print(timeList1)
def job1():
    global timeList2, top20
    timeList2 = get_crolling()
    top20 = getTop20(timeList6, timeList1)
    print(f'job1 : {time.strftime("%H:%M:%S")}')
    print(timeList2)
def job2():
    global timeList3, top20
    timeList3 = get_crolling()
    top20 = getTop20(timeList2, timeList3)
    print(f'job2 : {time.strftime("%H:%M:%S")}')
    print(timeList3)
def job3():
    global timeList4, top20
    timeList4 = get_crolling()
    top20 = getTop20(timeList3, timeList4)
    print(f'job3 : {time.strftime("%H:%M:%S")}')
    print(timeList4)
def job4():
    global timeList5, top20
    timeList5 = get_crolling()
    top20 = getTop20(timeList4, timeList5)
    print(f'job4 : {time.strftime("%H:%M:%S")}')
    print(timeList5)
def job5():
    global timeList6, top20
    timeList6 = get_crolling()
    top20 = getTop20(timeList5, timeList6)
    print(f'job5 : {time.strftime("%H:%M:%S")}')
    print(timeList6)
@app.route('/scheduler')
def scheduler():
    print("scheduler start")
    global timeList1, timeList2, timeList3, timeList4, timeList5, timeList6
    sched = BackgroundScheduler(timezone='Asia/Seoul')

    sched.remove_all_jobs()

    # 매일 0시 실행
    sched.add_job(job0, 'cron', hour='0')
    # 매일 4시 실행
    sched.add_job(job1, 'cron', hour='4')
    # 매일 8시 실행
    sched.add_job(job2, 'cron', hour='8')
    # 매일 12시 실행
    sched.add_job(job3, 'cron', hour='12')
    # 매일 16시 실행
    sched.add_job(job4, 'cron', hour='16')
    # 매일 20시 실행
    sched.add_job(job5, 'cron', hour='20')

    # sched.add_job(job0, 'cron', hour='15')
    # sched.add_job(job1, 'cron', hour='15', minute='10')
    # sched.add_job(job2, 'cron', hour='15', minute='20')
    # sched.add_job(job3, 'cron', hour='15', minute='30')
    # sched.add_job(job4, 'cron', hour='15', minute='40')
    # sched.add_job(job5, 'cron', hour='15', minute='50')

    sched.start()
    print("scheduler start")
    return redirect( url_for('index') )

@app.route('/') # 접속하는 url
def index():

    global top20, timeList1, timeList2, timeList3, timeList4, timeList5, timeList6
    dataList = []
    dataList.append(timeList1)
    dataList.append(timeList2)
    dataList.append(timeList3)
    dataList.append(timeList4)
    dataList.append(timeList5)
    dataList.append(timeList6)
    return render_template('index.html',
                           title="bitfind23",
                           ktime=convert_kst(datetime.now()),
                           time=datetime.now(),
                           data=get_crolling(),
                           # top10=top20,
                           dataList=dataList)

if __name__ == '__main__':
    app.run()