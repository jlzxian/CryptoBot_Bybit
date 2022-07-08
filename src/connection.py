import sys
sys.path.insert(1, '../config')
import credentials
import datetime, time
from pybit import spot, usdt_perpetual

history = []

class Utility:
    def __init__(self):
        pass

    def get_server_time(self):
        http = spot.HTTP()
        data = http.server_time()
        server_time = data['result']['serverTime']

        return time.localtime(server_time / 1000)

def get_connection(instrument='usdt'):
    if instrument == 'usdt':
        ws = usdt_perpetual.WebSocket(test=True,
                                      api_key=credentials.API_KEY,
                                      api_secret=credentials.API_SECRET,
                                      domain='bytick')
    return ws

def handle_data(message):
    # Handle data message
    data = message['data'][0]
    start_time = datetime.datetime.fromtimestamp(data['timestamp']/1000000).strftime("%Y-%m-%d %H:%M:%S")
    open = data['open']
    close = data['close']
    high = data['high']
    low = data['low']
    volume = data['volume']

    history.append((start_time, open, high, low, close, volume))

    print('Close price: ', str(close))

if __name__ == "__main__":
    try:
        ws = get_connection()
        print('Connection Success')
        ws.kline_stream(handle_data, 'BTCUSD', 1)
    except:
        print("Connection Fail")

    while True:
        time.sleep(30)
        # if len(history) > 5:
        #     history = history[1:]
        # print(history)
        server_time = Utility().get_server_time()
        if server_time.tm_min % 10 == 0:
            print(server_time)
            history = []
