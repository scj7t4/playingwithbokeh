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


def stocks_callback(active, holder_crv):
    print(f"Callback {active}")
    src = [('aapl', aapl_curve), ('goog', goog_curve)]
    d = {k: v for (i, (k, v)) in enumerate(src) if i in active}
    d['_'] = holder_crv
    print(f"Plts = {d}")
    overlay = hv.NdOverlay(d)

    return overlay


def layout_cb(active):
    src_crv = hv.Curve([])
    tgt_crv = hv.Curve([])
    tgt = stocks_callback(active, tgt_crv).relabel('').opts(width=800, height=400, labelled=['y'])
    src = stocks_callback(active, src_crv).relabel('').opts(width=800, height=200, yaxis=None, default_tools=[])
    RangeToolLink(src_crv, tgt_crv)
    plt = (tgt + src).cols(1)
    print(LinkCallback.find_links(plt))
    plt.opts(opts.Layout(shared_axes=False, merge_tools=False))
    return plt


def change_active_stocks(attr, old, new):
    layout_cb(active=new)


#layout = hv.DynamicMap(layout_cb, streams=[chosen_stocks_stream])
layout = layout_cb([0, 1])

checkbox_group = CheckboxGroup(labels=["AAPL", "GOOG"], active=[0, 1])
checkbox_group.on_change("active", change_active_stocks)

renderer.server_doc(layout)
