# %load "../utils.py"
import pandas as pd
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import warnings

def read_data(data, time='time'):
    # Assumes df is in descending order for date
    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'])
    df.set_index(df['time'], drop=True, inplace=True)
    df.drop(columns=['time'], inplace=True)

    df = df.iloc[::-1]
    # df = df.asfreq("T")
    #
    # cols = ['open', 'high', 'low', 'close']
    # for col in cols:
    #     df[col] = df[col].ffill()
    #
    # df['volume'].fillna(0, inplace=True)

    return df
    
def resample_df(df, resample_size, open='open', close='close', high='high', low='low', volume='volume'):
    # resample_size: how many minutes to condensed into
    # df assumed to be in 1 minute interval, sort oldest to newest
    df = df.resample(resample_size).agg({open:"first", high:"max", low:"min", close:"last", volume:"sum"})
    #df = df.shift(1)
    return df

# def plot(df, date='time', open='open', close='close', high='high', low='low', volume='volume',
#                    file_name='file', price_lines=[], non_price_lines=[], volume_disp=False):
#     # non_price_lines = [{'Primary':[(), ()], 'Secondary' : [(), ()]},...]
#
#     specs = []
#     if volume_disp:
#         specs.append([{"secondary_y": True}])
#         secondary_price = True
#     else:
#         specs.append([{}])
#         secondary_price = False
#
#     for non_price in non_price_lines:
#         if 'Secondary' in non_price:
#             specs.append([{"secondary_y": True}])
#         else:
#             specs.append([{}])
#
#     fig = make_subplots(rows=1 + len(non_price_lines), cols=1, shared_xaxes=True, specs=specs)
#
#     # include candlestick with rangeselector
#     fig.add_trace(go.Candlestick(x=df.index, open=df[open], high=df[high], low=df[low], close=df[close], name='Price'),
#                   secondary_y=secondary_price, row=1, col=1)
#
#     # include a go.Bar trace for volumes
#     if volume_disp:
#         fig.add_trace(go.Bar(x=df.index, y=df[volume], name='Volume'), secondary_y=False, row=1, col=1)
#
#     # Plot lines
#     if price_lines is not None:
#         for line in price_lines:
#             fig.add_trace(
#                 go.Scatter(x=df.index, y=df[line], mode='lines', name=line, line=dict(shape='linear', width=1)),
#                 secondary_y=secondary_price, row=1, col=1)
#
#     # Non_Price_Lines
#     if non_price_lines is not None:
#         for idx, line in enumerate(non_price_lines):
#             idx += 2
#             for sub_lines in line['Primary']:
#                 name, type = sub_lines
#
#                 if type == 'Line':
#                     fig.add_trace(go.Scatter(x=df.index, y=df[name], mode='lines', name=name, line=dict(shape='linear', width=1)), secondary_y=False, row=idx, col=1)
#                 elif type == 'Bar':
#                     fig.add_trace(go.Bar(x=df.index, y=df[name], name=name), secondary_y=False, row=idx, col=1)
#                 else:
#                     warnings.warn("Does not support following type: (%s)" % sub_lines)
#
#             if 'Secondary' in line:
#                 for sub_lines in line['Secondary']:
#                     name, type = sub_lines
#
#                     if type == 'Line':
#                         fig.add_trace(go.Scatter(x=df.index, y=df[name], mode='lines', name=name,
#                                                  line=dict(shape='linear', width=1)), secondary_y=True, row=idx, col=1)
#                     elif type == 'Bar':
#                         fig.add_trace(go.Bar(x=df.index, y=df[name], name=name), secondary_y=True, row=idx, col=1)
#                     else:
#                         warnings.warn("Does not support following type: (%s)" % sub_lines)
#
#     fig.update_xaxes(row=1, col=1, rangeslider_thickness=0.05)
#     try:
#         fig.layout.yaxis2.showgrid = False
#     except:
#         pass
#     fig.update_yaxes(fixedrange=False)
#
#     # fig.update_yaxes(showgrid=False)
#     # fig.update_yaxes(range=[-1,1], dtick=0.25, secondary_y=True, rangemode = 'tozero', row=2, col=1)
#     fig.update_yaxes(secondary_y=False, rangemode='tozero', row=2, col=1)
#     fig.update_layout(barmode='relative')
#
#     fig.write_html(rf"C:\Users\jlzxi\Desktop\{file_name}.html")
#
#     return fig
