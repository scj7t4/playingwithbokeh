from typing import List

import pandas as pd
from bokeh.events import Reset
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import CheckboxGroup, ColumnDataSource, RangeTool, Range1d
from bokeh.plotting import figure
from bokeh.sampledata.stocks import AAPL, GOOG

# empty_df holds no data, we plug it in when we don't want to show anything...
aapl_df = pd.DataFrame(AAPL['close'], columns=['close'], index=pd.to_datetime(AAPL['date']))
goog_df = pd.DataFrame(GOOG['close'], columns=['close'], index=pd.to_datetime(GOOG['date']))
empty_df = pd.DataFrame({'close': []})

aapl_df.index.name = 'Date'
goog_df.index.name = 'Date'
empty_df.index.name = 'Date'

# Keep a set of the original data, our chooser will plug this in as needed
data_frames = [
    aapl_df,
    goog_df
]

# Make a data source for each of our columns
# empty_df to simulate not loading the data until its chosen
main_data_sources = [
    ColumnDataSource(empty_df) for df in data_frames
]
sub_data_sources = [
    ColumnDataSource(empty_df) for df in data_frames
]

x_range = Range1d()
y_range = Range1d()


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

# Main plot:
tools = 'pan,wheel_zoom,box_zoom,reset'


def resample_data_source(index, data_sources: List[ColumnDataSource], range: Range1d):
    cds: ColumnDataSource = data_sources[index]
    df = data_frames[index]
    start = pd.to_datetime(range.start, unit='ms')
    end = pd.to_datetime(range.end, unit='ms')
    print(f'{range.start}/{start} -> {range.end}/{end}')
    if range.end == 1:
        return
    sliced = df[start: end]
    rows = len(sliced)
    print(f'Region size {index} is {rows}')
    if rows > 50:
        slicer = rows // 50
        sliced = sliced[::slicer]
    cds.data = sliced


main_plot = figure(
    plot_width=900,
    plot_height=400,
    tools=tools,
    x_axis_type='datetime',
    x_range=x_range,
    y_range=y_range)
main_lines = [
    main_plot.line('Date', 'close', source=s) for s in main_data_sources
]

# Overview plot:
sub_plot = figure(
    plot_width=900,
    plot_height=200,
    tools=[],
    x_axis_type='datetime')
sub_lines = [
    sub_plot.line('Date', 'close', source=s) for s in sub_data_sources
]
range_tool = RangeTool(x_range=main_plot.x_range, y_range=main_plot.y_range)
sub_plot.add_tools(range_tool)
sub_plot.toolbar.active_multi = range_tool


def do_reset(active_stocks):
    x_range.start = min([x.index.min() for i, x in enumerate(data_frames) if i in active_stocks])
    x_range.end = max([x.index.max() for i, x in enumerate(data_frames) if i in active_stocks])
    y_range.start = min([x['close'].min() for i, x in enumerate(data_frames) if i in active_stocks])
    y_range.end = max([x['close'].max() for i, x in enumerate(data_frames) if i in active_stocks])


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
