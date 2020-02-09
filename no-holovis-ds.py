from typing import List

import datashader as ds
import datashader.transfer_functions as tf
import pandas as pd
from bokeh.events import Reset
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import CheckboxGroup, ColumnDataSource, RangeTool, Range1d, Image
from bokeh.plotting import figure
from bokeh.sampledata.stocks import AAPL, GOOG
# empty_df holds no data, we plug it in when we don't want to show anything...
from pandas import DataFrame

aapl_df = pd.DataFrame(AAPL['close'], columns=['close'], index=pd.to_datetime(AAPL['date']))
goog_df = pd.DataFrame(GOOG['close'], columns=['close'], index=pd.to_datetime(GOOG['date']))
empty_df = pd.DataFrame({'close': []})

aapl_df.index.name = 'Date'
goog_df.index.name = 'Date'
empty_df.index.name = 'Date'

# Keep a set of the original data, our chooser will plug this in as needed
data_frames = [
    aapl_df
]

# Make a data source for each of our columns
# empty_df to simulate not loading the data until its chosen
main_data_sources = [
    ColumnDataSource(data=dict(image=[], x=[], y=[], dw=[], dh=[])) for _ in data_frames
]
sub_data_sources = [
    ColumnDataSource(data=dict(image=[], x=[], y=[], dw=[], dh=[])) for _ in data_frames
]

main_images = [
    Image(image='image', x='x', y='y', dw='dw', dh='dh') for _ in data_frames
]

sub_images = [
    Image(image='image', x='x', y='y', dw='dw', dh='dh') for _ in data_frames
]


def datashade(df: DataFrame, x_range: Range1d, y_range: Range1d, plot_height, plot_width):
    y_range_basic = (y_range.start, y_range.end)

    df_simplified = DataFrame(df)
    df['IDate'] = df.index.astype('int64')
    x_range_basic = df['IDate'].iloc[0], df['IDate'].iloc[-1]

    cvs = ds.Canvas(x_range=x_range_basic, y_range=y_range_basic, plot_height=plot_height, plot_width=plot_width)
    ln = cvs.line(df, 'IDate', 'close')
    return tf.shade(ln)


# Update column data sources based on check boxes
def change_active_stocks(attr, old, new):
    print(f'Change stocks {new}')
    for (i, data_source) in enumerate(main_data_sources):
        if i not in new:
            data_source.data = empty_df
        elif old and i not in old:
            resample_data_source(i, main_data_sources, x_range)
    for (i, data_source) in enumerate(sub_data_sources):
        if i not in new:
            data_source.data = empty_df
        elif old and i not in old:
            range = Range1d(
                start=min([x.index.min() for j, x in enumerate(data_frames) if j in checkbox_group.active]),
                end=max([x.index.max() for j, x in enumerate(data_frames) if j in checkbox_group.active])
            )
            resample_data_source(i, sub_data_sources, range)


checkbox_group = CheckboxGroup(labels=["AAPL", "GOOG"], active=[0, 1])
checkbox_group.on_change("active", change_active_stocks)

x_range = Range1d()
y_range = Range1d()


def do_reset(active_stocks):
    x_range.start = min([x.index.min() for i, x in enumerate(data_frames) if i in active_stocks])
    x_range.end = max([x.index.max() for i, x in enumerate(data_frames) if i in active_stocks])
    y_range.start = min([x['close'].min() for i, x in enumerate(data_frames) if i in active_stocks])
    y_range.end = max([x['close'].max() for i, x in enumerate(data_frames) if i in active_stocks])


do_reset(checkbox_group.active)

# Main plot:
tools = 'pan,wheel_zoom,box_zoom,reset'

main_plot = figure(
    plot_width=900,
    plot_height=400,
    tools=tools,
    x_axis_type='datetime',
    x_range=x_range,
    y_range=y_range)
main_image_glpyhs = [
    main_plot.add_glyph(source, glyph=image) for (source, image) in zip(main_data_sources, main_images)
]

# Overview plot:
sub_plot = figure(
    plot_width=900,
    plot_height=200,
    tools=[],
    x_axis_type='datetime')
sub_image_glyphs = [
    sub_plot.add_glyph(source, glyph=image) for (source, image) in zip(sub_data_sources, sub_images)
]


def resample_data_source(index, data_sources: List[ColumnDataSource], range: Range1d):
    for (i, source) in enumerate(main_data_sources):
        shaded = datashade(data_frames[i], x_range, y_range, main_plot.plot_width, main_plot.plot_height)
        source.data = {
            'image': [shaded.data],
            'x': [x_range.start],
            'y': [y_range.start],
            'dw': [x_range.end],
            'dh': [y_range.end]
        }

    # for (i, source) in enumerate(sub_data_sources):
    #     source.data['image'] = [datashade(data_frames[i], x_range, y_range, main_plot.plot_width, sub_plot.plot_height)]
    #     source.data['x'] = [x_range.start]
    #     source.data['y'] = [y_range.start]
    #     source.data['dw'] = [x_range.end]
    #     source.data['dh'] = [y_range.end]


range_tool = RangeTool(x_range=main_plot.x_range, y_range=main_plot.y_range)
sub_plot.add_tools(range_tool)
sub_plot.toolbar.active_multi = range_tool


def xrange_change_callback(attr, old, new):
    for i in checkbox_group.active:
        resample_data_source(i, main_data_sources, x_range)


x_range.on_change('start', xrange_change_callback)
x_range.on_change('end', xrange_change_callback)


def handle_reset(_):
    print("Trigger reset")
    do_reset(checkbox_group.active)


change_active_stocks(None, None, checkbox_group.active)
do_reset(checkbox_group.active)
for i in checkbox_group.active:
    resample_data_source(i, sub_data_sources, x_range)

main_plot.on_event(Reset, handle_reset)

doc = curdoc()
plot = layout([main_plot, sub_plot, checkbox_group])
doc.add_root(plot)
