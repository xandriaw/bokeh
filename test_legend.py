from bokeh.io import show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Legend, Circle
from bokeh.plotting import figure

source = ColumnDataSource({
    'x': [1, 2, 3, 4, 5, 6],
    'y': [1, 2, 1, 2, 1, 2],
    'color': ['#FF4136', '#0074D9', '#2ECC40', '#FF4136', '#0074D9', '#2ECC40'],
    'label': ['Color Red', 'Color Blue', 'Color Green', 'Color Red', 'Color Blue', 'Color Green'],
})
opts = dict(x_range=(-2, 8), y_range=(-2, 4), width=600, height=300, tools='')


# Data legends
new = figure(**opts)
circle = Circle(x='x', y='y', fill_color='color', line_color='color', radius=0.5, legend_label='label')
cr = new.add_glyph(source, circle)
new.add_layout(Legend(data_legends=[cr]))


# Old style
old = figure(**opts)
old.circle(x='x', y='y', color='color', radius=0.5, legend_label='label', source=source, legend='circle')

show(column(new, old))
