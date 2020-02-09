import holoviews as hv
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import CheckboxGroup
from bokeh.sampledata.stocks import AAPL, GOOG
from holoviews import opts
from holoviews.plotting.links import RangeToolLink
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


def stocks_callback(active):
    print(f"Callback {active}")
    return hv.Overlay([(crv if i in active else hv.Curve([])) for (i, (sym, crv)) in enumerate(stock_symbols)])


def change_active_stocks(attr, old, new):
    chosen_stocks_stream.event(active=new)


dmap = hv.DynamicMap(stocks_callback, streams=[chosen_stocks_stream])
olayed = dmap
src_crv = hv.Curve(list(), 'Date', 'Price ($)').opts(height=200, default_tools=[])
tgt_crv = hv.Curve(list(), 'Date', 'Price ($)').opts(height=400)
src_olay = hv.Overlay([src_crv, olayed.relabel('')]) \
    .opts(width=800, yaxis=None) \
    .collate() \
    .opts(height=200)
tgt_olay = hv.Overlay([tgt_crv, olayed.relabel('')]) \
    .opts(width=800) \
    .collate() \
    .opts(height=400)
RangeToolLink(src_crv, tgt_crv, axes=['x', 'y'])
plt = (tgt_olay + src_olay).cols(1)
plt.opts(opts.Layout(shared_axes=False, merge_tools=False))

checkbox_group = CheckboxGroup(labels=["AAPL", "GOOG"], active=[0, 1])
checkbox_group.on_change("active", change_active_stocks)

doc = curdoc()
hvplot = renderer.get_plot(plt, doc)  # displayed is the laidout hv
plot = layout([hvplot.state, checkbox_group])
doc.add_root(plot)
