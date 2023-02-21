from datetime import datetime, timedelta
import time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for  # Flask 라이브러리 선언
app = Flask(__name__)

import requests

url ="https://coinmarketcap.com/exchanges/upbit/"
oldList =[]

timeList1 = []
timeList2 = []
timeList3 = []
timeList4 = []
timeList5 = []
timeList6 = []

top10 = []
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
        "prevValue": prevValue,
        "bw": preCnt - copyArr['idx']
    }
    return pList


def compareList(oldList, newList):
    global top10
    result = []
    for i, n in enumerate(newList):
        for j, o in enumerate(oldList):
            if n['ticker'] == o['ticker']: #ticker 가 같은지 비교
                arr = printListout(n, o['idx'], o['volume'])
                result.append(arr)
                between = i - j
                fArr = []
                bArr = []

                if len(top10) < 10:
                    top10.append(arr)
                else:
                    for k, x in enumerate(top10):
                        if between < 0:
                            if x['bw'] < between:
                                fArr = top10[0:k]
                                fArr.append(arr)
                                fArr.append(top10[k:all])


                    if len(fArr) > 10:
                        top10 = fArr[0:10]
                    print('top10', top10)
                break
    return result


def get_crolling():
    print('get_crolling start')
    global oldList
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
        print(f"{i + 1}. {volume['ticker']}: {volume['volume']}")

    # ticker_list = [x.text for x in top_volumes]
    # print(ticker_list)

    # newList = top_volumes[0:10]
    result = []

    if len(oldList) == 0:
        oldList = top_volumes
        for volume in top_volumes:
            result.append(printListout(volume, volume['idx'], f"{volume['volume']}"))

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

def job0():
    global timeList1
    timeList1 = get_crolling()
    print(f'job0 : {time.strftime("%H:%M:%S")}')
    print(timeList1)
def job1():
    global timeList2
    timeList2 = get_crolling()
    print(f'job1 : {time.strftime("%H:%M:%S")}')
    print(timeList2)
def job2():
    global timeList3
    timeList3 = get_crolling()
    print(f'job2 : {time.strftime("%H:%M:%S")}')
    print(timeList3)
def job3():
    global timeList4
    timeList4 = get_crolling()
    print(f'job3 : {time.strftime("%H:%M:%S")}')
    print(timeList4)
def job4():
    global timeList5
    timeList5 = get_crolling()
    print(f'job4 : {time.strftime("%H:%M:%S")}')
    print(timeList5)
def job5():
    global timeList6
    timeList6 = get_crolling()
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
    sched.add_job(job3, 'cron', hour='12', minute='10')
    # 매일 16시 실행
    sched.add_job(job4, 'cron', hour='16')
    # 매일 20시 실행
    sched.add_job(job5, 'cron', hour='20')

    sched.start()
    print("scheduler start")
    return redirect( url_for('index') )

@app.route('/') # 접속하는 url
def index():
    global top10, timeList1, timeList2, timeList3, timeList4, timeList5, timeList6
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
                           top10=top10,
                           dataList=dataList)

if __name__ == '__main__':
    app.run()