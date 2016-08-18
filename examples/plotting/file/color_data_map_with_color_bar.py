import numpy as np

from bokeh.io import show
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import Spectral10
from bokeh.plotting import figure

x = np.random.random(2500) * 100
y = np.random.normal(size=2500) * 2 + 5
source = ColumnDataSource(dict(x=x, y=y))

mapper = LinearColorMapper(palette=Spectral10, low=0, high=100)
color_bar = ColorBar(
    orientation='horizontal',
    color_mapper=mapper,
    legend_width=500,
    legend_height='auto',
    location='center',
)

p = figure()
opts = dict(x='x', line_color=None, source=source)
p.circle(y='y', fill_color={'field': 'x', 'transform': mapper}, **opts)
p.add_layout(color_bar)

show(p)
