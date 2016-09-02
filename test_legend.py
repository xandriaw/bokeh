from bokeh.io import show
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

p = figure(x_range=(-2, 8), y_range=(-2, 4))
source = ColumnDataSource({
    'x': [1, 2, 3, 4, 5, 6],
    'y': [1, 2, 1, 2, 1, 2],
    'color': ['#FF4136', '#0074D9', '#2ECC40', '#FF4136', '#0074D9', '#2ECC40'],
    'label': ['Red', 'Blue', 'Green', 'Red', 'Blue', 'Green'],
})
p.circle(x='x', y='y', color='color', radius=0.5, legend='label', source=source)
show(p)
