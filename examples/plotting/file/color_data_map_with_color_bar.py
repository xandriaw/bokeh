import numpy as np

from bokeh.io import show
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import Viridis3
from bokeh.plotting import figure

x = np.random.random(2500) * 100
y = np.random.normal(size=2500) * 2 + 5
source = ColumnDataSource(dict(x=x, y=y))

mapper = LinearColorMapper(palette=Viridis3, low=0, high=100)
color_bar = ColorBar(color_mapper=mapper, location=(0,0))

p = figure(toolbar_location='above')
opts = dict(x='x', line_color=None, source=source)
p.circle(y='y', fill_color={'field': 'x', 'transform': mapper}, **opts)
p.add_layout(color_bar, 'right')

show(p)
