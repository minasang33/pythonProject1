from datetime import datetime
import time
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

#스케줄 실행 코드
def scheduler():
    print("Scheduler is alive!")
def printListout(copyArr, preCnt, prevValue):
    print('preCnt', preCnt, type(preCnt))
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

                if len(top10) == 0:
                    top10.append(arr)
                else:

                    for x in top10:
                        if between < 0:
                            if x['bw'] > between:
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
    print("scheduler 23")
    global timeList6
    timeList6 = get_crolling()
    print(f'job5 : {time.strftime("%H:%M:%S")}')
    print(timeList6)

def job51(data):
    print("sche 51", data)

def job52(data):
    print("sche 52", data)
def job53(data):
    print("sche 53", data)
@app.route('/scheduler')
def scheduler():
    print("scheduler start")
    global timeList1, timeList2, timeList3, timeList4, timeList5, timeList6
    sched = BackgroundScheduler(timezone='Asia/Seoul')

    sched.remove_all_jobs()

    #findData( get_crolling())

     #timeList[currentIndex] = data

    # 매일 0시 실행
    # @sched.add_job(job0, 'cron', hour='3')
    #
    # # 매일 4시 실행
    # @sched.scheduled_job('cron', hour='7',id='test_1')
    #
    # # 매일 8시 실행
    # @sched.scheduled_job('cron', hour='11', id='test_2')
    #
    #
    #
    # # 매일 12시 실행
    # @sched.scheduled_job('cron', hour='15', id='test_3')
    #
    #
    #
    # # 매일 16시 실행
    # @sched.scheduled_job('cron', hour='19', id='test_4')
    #
    #
    #
    # # 매일 20시 실행
    # @sched.scheduled_job('cron', hour='23', minute='5', id='test_5')


    sched.add_job(job51, 'cron', hour='0', minute='30', args=['utc'])
    sched.add_job(job52, 'cron', hour='0', minute='31', args=['utc'])
    sched.add_job(job53, 'cron', hour='0', minute='32', args=['utc'])
    sched.add_job(job51, 'cron', hour='9', minute='30', args=['kor'])
    sched.add_job(job52, 'cron', hour='9', minute='31', args=['kor'])
    sched.add_job(job53, 'cron', hour='9', minute='32', args=['kor'])

    sched.start()
    print("scheduler start")
    return redirect( url_for('index') )


@app.route('/') # 접속하는 url
def index():
    global top10
    t = datetime.now().hour
    print("hour:", t)
    if 23 <= t:
        data = timeList6
        prevData = timeList5
    elif 19 <= t:
        data = timeList5
        prevData = timeList4
    elif 15 <= t:
        data = timeList4
        prevData = timeList3
    elif 11 <= t:
        data = timeList3
        prevData = timeList2
    elif 7 <= t:
        data = timeList2
        prevData = timeList1
    else:
        data = timeList1
        prevData = timeList6

    print("data", data)
    print("top10", top10)
    return render_template('index.html', title="bitfind23", time=datetime.now(), data=data, prev=prevData, top10=top10)

if __name__ == '__main__':
    app.run()