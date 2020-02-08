import holoviews as hv
from bokeh.models import CheckboxGroup

from bokeh.sampledata.stocks import AAPL, GOOG
from holoviews import opts
from holoviews.plotting.bokeh.callbacks import LinkCallback
from holoviews.plotting.links import RangeToolLink
import pandas as pd
from holoviews.streams import Stream

hv.extension('bokeh')
renderer = hv.renderer('bokeh')

aapl_df = pd.DataFrame(AAPL['close'], columns=['close'], index=pd.to_datetime(AAPL['date']))
goog_df = pd.DataFrame(GOOG['close'], columns=['close'], index=pd.to_datetime(GOOG['date']))
aapl_df.index.name = 'Date'
goog_df.index.name = 'Date'

aapl_curve = hv.Curve(aapl_df, 'Date', ('close', 'Price ($)'))
goog_curve = hv.Curve(goog_df, 'Date', ('close', 'Price ($)'))

chosen_stocks_stream = Stream.define('Toggle Stocks', active=[0, 1])()
stock_symbols = [('aapl', aapl_curve), ('goog', goog_curve)]


def stocks_callback(idx, active):
    print(f"Callback {active}")

    if idx in active:
        return stock_symbols[idx][1]
    return hv.Curve([])


def change_active_stocks(attr, old, new):
    pass


dmap = hv.DynamicMap(stocks_callback, kdims=['idx'], streams=[chosen_stocks_stream])
dmap = dmap.redim.values(idx=list(range(len(stock_symbols))))

olayed = dmap.groupby(dimensions=['idx'], group_type=hv.NdOverlay)
src_crv = hv.Curve([])
tgt_crv = hv.Curve([])
tgt_olay = hv.Overlay([tgt_crv, olayed.relabel('')]).opts(width=800, height=400, labelled=['y']).collate()
src_olay = hv.Overlay([src_crv, olayed.relabel('')]).opts(width=800, height=200, yaxis=None, default_tools=[]).collate()
RangeToolLink(src_crv, tgt_crv)
plt = (tgt_olay + src_olay).cols(1)
plt.opts(opts.Layout(shared_axes=False, merge_tools=False))

checkbox_group = CheckboxGroup(labels=["AAPL", "GOOG"], active=[0, 1])
checkbox_group.on_change("active", change_active_stocks)

renderer.server_doc(plt)
