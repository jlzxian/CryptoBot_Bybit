import sys, re

import pybit.exceptions

sys.path.insert(1, '../config')
import credentials
from pybit import spot, usdt_perpetual

import pandas as pd

class Perpetual:
    def __init__(self, symbol='BTCUSDT', margin_isolated=False,buy_leverage=10, sell_leverage=10, pos_limit=1):
        self.http = usdt_perpetual.HTTP("https://api-testnet.bybit.com",
                                   api_key=credentials.API_KEY, api_secret=credentials.API_SECRET)

        self.symbol = symbol
        self.pos_limit = pos_limit
        self.cancel_all_orders()

        err_cde = re.compile('''(ErrCode: [0-9]*)''')

        try:
            self.http.cross_isolated_margin_switch(symbol=symbol,is_isolated=margin_isolated, buy_leverage=1, sell_leverage=1)
        except pybit.exceptions.InvalidRequestError as e:
            msg = re.findall(err_cde, e.args[0])[0]
            if msg == 'ErrCode: 130056':
                pass
            else:
                print('Set margin mode fail')
        try:
            self.http.full_partial_position_tp_sl_switch(symbol=symbol, tp_sl_mode='Full')
        except pybit.exceptions.FailedRequestError as e:
            msg = re.findall(err_cde, e.args[0])[0]
            if msg == 'ErrCode: 400':
                pass
            else:
                print('Set full/Partial position fail')

        try:
            self.http.set_leverage(symbol=symbol, buy_leverage=buy_leverage, sell_leverage=sell_leverage)
        except pybit.exceptions.InvalidRequestError as e:
            msg = re.findall(err_cde, e.args[0])[0]
            if msg == 'ErrCode: 34036':
                pass
            else:
                print('Set margin fail')

        print("Account initialized\n", '*'*40)

    # Query Orders
    def get_active_orders(self):
        temp = self.http.query_active_order(symbol=self.symbol)['result']
        return pd.DataFrame(temp)

    def get_orders(self):
        temp = self.http.get_active_order(symbol=self.symbol)['result']['data']
        return pd.DataFrame(temp)

    # Orders place/cancel
    def place_order(self, side, price, order_type='Market', qty=1, time_in_force='GoodTillCancel', reduce_only=False, close_on_trigger=False):
        # Reduce_only: False = open position, True = close position
        active_pos = self.get_active_position()

        if active_pos['size'].sum() >= self.pos_limit:
            print("Exceeded positioin limit")
            return False
        else:
            try:
                self.http.place_active_order(symbol=self.symbol, side=side, order_type=order_type, qty=qty, price=price, time_in_force=time_in_force,
                                             reduce_only=reduce_only, close_on_trigger=close_on_trigger)
                print('Order placed')
                return True
            except pybit.exceptions.InvalidRequestError as e:
                print(e)
                print('Unable to place order')
                return False

    def cancel_order(self, orderID):
        try:
            return_msg = self.http.cancel_active_order(symbol=self.symbol, order_id=orderID)
            print(return_msg['ret_msg'])
        except pybit.exceptions.InvalidRequestError as e:
            print(e)
            print('Unable to cancel order')

    def cancel_all_orders(self):
        try:
            return_msg = self.http.cancel_all_active_orders(symbol=self.symbol)
            print(return_msg['ret_msg'])
        except pybit.exceptions.InvalidRequestError as e:
            print(e)
            print('Unable to cancel order')

    def set_trading_stop(self, stop_loss_pcr=0.1):
        positions = self.get_positions()
        active_pos = positions[positions['size'] != 0]
        active_pos.reset_index(inplace=True, drop=True)

        if active_pos.shape[0] == 0:
            print('No active positions')
        else:
            entry_price = active_pos.loc[0,'entry_price']
            side = active_pos.loc[0, 'side']

            if side == 'Buy':
                self.http.set_trading_stop(symbol=self.symbol, side=side, stop_loss=round(entry_price*(1-stop_loss_pcr), 2))
            else:
                self.http.set_trading_stop(symbol=self.symbol, side=side, stop_loss=round(entry_price*(1+stop_loss_pcr), 2))

    def close_all_pos(self):
        self.http.close_position(self.symbol)

    # Account Info/Settings
    def get_positions(self):
        temp = self.http.my_position(symbol=self.symbol)['result']
        return pd.DataFrame(temp)

    def get_active_position(self):
        positions = self.get_positions()
        active_pos = positions[positions['size'] != 0]

        if active_pos['size'].sum() == 0:
            print('No active positions')
            return active_pos
        else:
            return active_pos

    def set_leverage(self, buy_leverage=10, sell_leverage=10):
        self.set_leverage(symbol=self.symbol, buy_leverage=buy_leverage, sell_leverage=sell_leverage)

    def set_cross_isolated(self,mode='Cross', buy_leverage=10, sell_leverage=10):
        if mode == 'Cross':
            self.http.cross_isolated_margin_switch(symbol=self.symbol, is_isolated=False, buy_leverage=buy_leverage, sell_leverage=sell_leverage)
        elif mode == 'Isoldated':
            self.http.cross_isolated_margin_switch(symbol=self.symbol, is_isolated=True, buy_leverage=buy_leverage,
                                                   sell_leverage=sell_leverage)
        else:
            print('Invalid mode')

if __name__ == '__main__':
    http = usdt_perpetual.HTTP("https://api-testnet.bybit.com",
               api_key=credentials.API_KEY, api_secret=credentials.API_SECRET)

    perp = Perpetual()

    perp.set_trading_stop()
