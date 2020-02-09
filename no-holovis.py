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
data_sources = [
    ColumnDataSource(empty_df) for df in data_frames
]

# Main plot:
tools = 'pan,wheel_zoom,box_zoom,reset'
x_range = Range1d()
y_range = Range1d()

main_plot = figure(
    plot_width=900,
    plot_height=400,
    tools=tools,
    x_axis_type='datetime',
    x_range=x_range,
    y_range=y_range)
main_lines = [
    main_plot.line('Date', 'close', source=s) for s in data_sources
]

# Overview plot:
sub_plot = figure(
    plot_width=900,
    plot_height=200,
    tools=[],
    x_axis_type='datetime')
sub_lines = [
    sub_plot.line('Date', 'close', source=s) for s in data_sources
]
range_tool = RangeTool(x_range=main_plot.x_range, y_range=main_plot.y_range)
sub_plot.add_tools(range_tool)
sub_plot.toolbar.active_multi = range_tool


# Update column data sources based on check boxes
def change_active_stocks(attr, old, new):
    print(f'Change stocks {new}')
    for (i, line) in enumerate(main_lines):
        if i not in new:
            line.data_source.data = empty_df
        else:
            line.data_source.data = data_frames[i]


def selection_change(attrname, old, new):
    print(new)


data_sources[0].selected.on_change('indices', selection_change)


def do_reset(active_stocks):
    x_range.start = min([x.index.min() for i, x in enumerate(data_frames) if i in active_stocks])
    x_range.end = max([x.index.max() for i, x in enumerate(data_frames) if i in active_stocks])
    y_range.start = min([x['close'].min() for i, x in enumerate(data_frames) if i in active_stocks])
    y_range.end = max([x['close'].max() for i, x in enumerate(data_frames) if i in active_stocks])


checkbox_group = CheckboxGroup(labels=["AAPL", "GOOG"], active=[0, 1])
checkbox_group.on_change("active", change_active_stocks)


def handle_reset(_):
    print("Trigger reset")
    do_reset(checkbox_group.active)


change_active_stocks(None, None, checkbox_group.active)
do_reset(checkbox_group.active)

main_plot.on_event(Reset, handle_reset)

doc = curdoc()
plot = layout([main_plot, sub_plot, checkbox_group])
doc.add_root(plot)
