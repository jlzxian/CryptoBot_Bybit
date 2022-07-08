
import time
from datetime import datetime

from rich.console import Console

import pps
import connection
import account

def execute_strategy(last_px, lines, acct, qty=1):
    def _execute_pos(acct, last_px, fr, side):
        acct.cancel_all_orders()
        active_pos = acct.get_active_position()
        active_pos.reset_index(inplace=True, drop=True)

        if active_pos['size'].sum() <= acct.pos_limit:
            # No active positions, place short order

            if side == 'Buy':
                opposite = 'Sell'
            else:
                opposite = 'Buy'

            if active_pos.shape[0] == 1:
                if active_pos.loc[0, 'side'] == opposite:
                    acct.close_all_pos()

            order_placed = acct.place_order(side, last_px, qty=qty)
            if order_placed:
                while acct.get_active_position().shape[0] == 0:
                    continue
                acct.set_trading_stop()
                print('Position entered')
            else:
                print('Order failed')

    sr = lines[0]
    fr = lines[1]
    fs = lines[2]
    ss = lines[3]
    stime, open, high, low, close, volume = last_px

    if close >= fr:
        # Execute sell order
        _execute_pos(acct, close, fr, 'Sell')
    elif close <= fs:
        # Execute buy order
        _execute_pos(acct, close, fr, 'Buy')

if __name__ == "__main__":
    bar_size = 3
    prediction_window = 30

    console = Console()
    currentTime = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    acct = account.Perpetual(buy_leverage=100, sell_leverage=100, pos_limit=5)

    # last_px = ('', '', '', '', 28001, '')
    # lines = [29000, 28000, 27000, 26000]
    # execute_strategy(last_px, lines, acct)

    with console.status(f"[bold green]Fetching data...") as status:

        try:
            ws = connection.get_connection()
            print('Connection Success')
            ws.kline_stream(connection.handle_data, 'BTCUSDT', 1)
        except:
            print("Connection Fail")

        lines = []

        while True:
            currentTime = datetime.today()
            minute = currentTime.minute
            #server_time = connection.Utility().get_server_time()
            #minute = server_time.tm_min

            history = connection.history
            if len(history) != 0:
                last_price = history[-1]
                if len(lines) != 0:
                    execute_strategy(last_price, lines, acct, qty=5)

            if (minute % prediction_window == 0) & (len(set([x[0].split(":")[1] for x in history])) > prediction_window):
                #print(server_time)
                print(currentTime)

                lines = pps.pps(history, bar_size=bar_size, prediction_window=prediction_window)

                print(lines)

                history = []

                acct.cancel_all_orders()
                time.sleep(60)

            time.sleep(10)
