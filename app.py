import datetime
from datetime import timedelta
import time
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for  # Flask 라이브러리 선언
app = Flask(__name__)

import pandas as pd
pd.set_option('display.max_columns', None) ## 모든 열을 출력한다.

from pyupbit.request_api import _call_public_api

import requests

# url ="https://coinmarketcap.com/exchanges/upbit/"


timeList1 = []
timeList2 = []
timeList3 = []
timeList4 = []
timeList5 = []
timeList6 = []

# m1 = '45'
# m2 = '46'
# m3 = '47'
# m4 = '48'
# m5 = '49'
# m6 = '50'

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

    if num_change >= 1000000:  # 1백만 이상
        str_result += f"{int(num_change // 1000000)}"
        # num_change = num_change % 1000000
    # elif num_change >= 10000:  # 1만 이상
    #     str_result += f" {int(num_change // 10000):,}만"
    #     num_change = num_change % 10000
    # elif num_change >= 1:  # 1 이상
    #     str_result += f" {int(num_change):,}"

    str_result = str_result.strip()  # Return a copy of the string with the leading and trailing characters removed
    if len(str_result) >= 1:
        return str_sign + str_result
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
    diffValue = copyArr['volume'] - float(prevValue)
    pList = {
        "id": copyArr['idx'],
        "ticker": copyArr['ticker'],
        "korean_name": copyArr['korean_name'],
        "change": str(preCnt)+"->"+str(copyArr['idx']),
        "value": copyArr['volume'],
        # "valueStr": copyArr['volume'],
        "valueStr": get_wonwha_string(copyArr['volume']),
        # "diffValueStr": diffValue,
        "diffValueStr": get_wonwha_string(diffValue),
        "prevValue": prevValue,
        "bw": preCnt - copyArr['idx'],
        "volumePrice": get_wonwha_string(copyArr['volumePrice'])
    }
    return pList


def compareList(oldList, newList):
    result = []
    count = 0
    print('cnt', len(oldList), len(newList))
    for i, n in enumerate(newList):
        for j, o in enumerate(oldList):
            if n['korean_name'] == o['korean_name']: #ticker 가 같은지 비교
                arr = printListout(n, o['id'], o['prevValue'])
                result.append(arr)
                count += 1
                break
    print('count', count)
    return result

def get_crolling(oldList, type='Scheduler'):
    # m = today.minute
    # print(m)
    #
    # if str(m) == m1:
    #     print('m1', len(timeList6))
    #     oldList = timeList6
    # elif str(m) == m2:
    #     print('m2', len(timeList1))
    #     oldList = timeList1
    # elif str(m) == m3:
    #     print('m3', len(timeList2))
    #     oldList = timeList2
    # elif str(m) == m4:
    #     print('m4', len(timeList3))
    #     oldList = timeList3
    # elif str(m) == m5:
    #     print('m5', len(timeList4))
    #     oldList = timeList4
    # elif str(m) == m6:
    #     print('m6', len(timeList5))
    #     oldList = timeList5
    # print("oldList=============================")
    # print(oldList)

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
                ret = next((item for item in markets if item['market'] == ticker_data['market']), None)
                volumes.append({'ticker': ticker_data['market'],
                                'korean_name': ret['korean_name'],
                                'volume': float(ticker_data['acc_trade_price_24h']),
                                })
                print(ticker_data['market'])
                break

    top_volumes = sorted(volumes, key=lambda x: x['volume'], reverse=True)

    for i, volume in enumerate(top_volumes):
        volume['idx'] = i+1
        volume['volume'] = volume['volume']
        print(f"{i + 1}. {volume['korean_name']}: {volume['volume']}")

    result = []

    if len(oldList) == 0:
        oldList = top_volumes
        for volume in top_volumes:
            result.append(
                printListout(volume, volume['idx'], f"{volume['volume']}")
            )
    else:
        result = compareList(oldList, top_volumes)

    if(type != 'RealTime'):
        for item in result:
            df = get_ohlcv(item['ticker'])
            if len(df) != 0:
                print(df)
                value = df['volumePrice'][0]
                item["volumePrice"] = f"{value}"
                print(item)

    return result


def get_tickers(fiat="KRW", limit_info=False):
    """
    마켓 코드 조회 (업비트에서 거래 가능한 마켓 목록 조회)
    :param fiat: "ALL", "KRW", "BTC", "USDT"
    :param limit_info: 요청수 제한 리턴
    :return:
    """
    try:
        url = "https://api.upbit.com/v1/market/all"

        # call REST API
        ret = _call_public_api(url)
        if isinstance(ret, tuple):
            contents, req_limit_info = ret
        else:
            contents = None
            req_limit_info = None

        tickers = None
        if isinstance(contents, list):
            markets = [x['market'] for x in contents]

            if fiat != "ALL":
                tickers = [x for x in markets if x.startswith(fiat)]
            else:
                tickers = markets

        if limit_info is False:
            return tickers
        else:
            return tickers, req_limit_info

    except Exception as x:
        print(x.__class__.__name__)
        return None


def get_ohlcv(ticker, count=1, to=None):
    """
    캔들 조회
    :return:
    """
    try:
        url = "https://api.upbit.com/v1/candles/minutes/240"

        if to == None:
            to = datetime.datetime.now()
        elif isinstance(to, str):
            to = pd.to_datetime(to).to_pydatetime()
        elif isinstance(to, pd._libs.tslibs.timestamps.Timestamp):
            to = to.to_pydatetime()

        if to.tzinfo is None:
            to = to.astimezone()
        to = to.astimezone(datetime.timezone.utc)
        to = to.strftime("%Y-%m-%d %H:%M:%S")

        contents = _call_public_api(url, market=ticker, count=count, to=to)[0]
        dt_list = [datetime.datetime.strptime(x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S") for x in contents]
        df = pd.DataFrame(contents, columns=['market','opening_price', 'high_price', 'low_price', 'trade_price',
                                             'candle_acc_trade_price',
                                             'candle_acc_trade_volume'],
                          index=dt_list)
        df = df.rename(
            columns={"market":"market", "opening_price": "open", "high_price": "high", "low_price": "low", "trade_price": "close",
                     "candle_acc_trade_price": "volumePrice",
                     "candle_acc_trade_volume": "volume"})
        return df.sort_index()
    except Exception as x:
        print(x.__class__.__name__)
        return []
def job0():
    global timeList1, timeList6
    timeList1 = get_crolling(timeList6)
    print(f'job0 : {time.strftime("%H:%M:%S")}')
    print(len(timeList1))
def job1():
    global timeList2, timeList1
    timeList2 = get_crolling(timeList1)
    print(f'job1 : {time.strftime("%H:%M:%S")}')
    print(len(timeList2))
def job2():
    global timeList3, timeList2
    timeList3 = get_crolling(timeList2)
    print(f'job2 : {time.strftime("%H:%M:%S")}')
    print(len(timeList3))
def job3():
    global timeList4, timeList3
    timeList4 = get_crolling(timeList3)
    print(f'job3 : {time.strftime("%H:%M:%S")}')
    print(len(timeList4))
def job4():
    global timeList5, timeList4
    timeList5 = get_crolling(timeList4)
    print(f'job4 : {time.strftime("%H:%M:%S")}')
    print(len(timeList5))
def job5():
    global timeList6, timeList5
    timeList6 = get_crolling(timeList5)
    print(f'job5 : {time.strftime("%H:%M:%S")}')
    print(len(timeList6))
@app.route('/scheduler')
def scheduler():
    print("scheduler start")

    sched = BackgroundScheduler(timezone='Asia/Seoul')

    sched.remove_all_jobs()

    # 매일 16시 실행
    sched.add_job(job0, 'cron', hour='1')
    # 매일 20시 실행
    sched.add_job(job1, 'cron', hour='5')
    #매일 0시 실행
    sched.add_job(job2, 'cron', hour='9')
    # 매일 4시 실행
    sched.add_job(job3, 'cron', hour='13')
    # 매일 8시 실행
    sched.add_job(job4, 'cron', hour='17')
    # 매일 12시 실행
    sched.add_job(job5, 'cron', hour='21')


    # sched.add_job(job0, 'cron', hour='16', minute=m1)
    # sched.add_job(job1, 'cron', hour='16', minute=m2)
    # sched.add_job(job2, 'cron', hour='16', minute=m3)
    # sched.add_job(job3, 'cron', hour='17', minute=m4)
    # sched.add_job(job4, 'cron', hour='17', minute=m5)
    # sched.add_job(job5, 'cron', hour='17', minute=m6)

    sched.start()
    print("scheduler start")
    return redirect( url_for('index') )

@app.route('/') # 접속하는 url
def index():
    global timeList1, timeList2, timeList3, timeList4, timeList5, timeList6
    dataList = []
    dataList.append(timeList1)
    dataList.append(timeList2)
    dataList.append(timeList3)
    dataList.append(timeList4)
    dataList.append(timeList5)
    dataList.append(timeList6)

    oldList = []
    today = convert_kst(datetime.datetime.now())
    t = today.hour
    print("hour:", t)

    if 21 <= t:
        oldList = timeList5
    elif 17 <= t:
        oldList = timeList4
    elif 13 <= t:
        oldList = timeList3
    elif 9 <= t:
        oldList = timeList2
    elif 5 <= t:
        oldList = timeList1
    else:
        oldList = timeList6
    return render_template('index.html',
                           title="bitfind23",
                           ktime=convert_kst(datetime.datetime.now()),
                           time=datetime.datetime.now(),
                           data=get_crolling(oldList, type="RealTime"),
                           dataList=dataList)

if __name__ == '__main__':
    app.run()