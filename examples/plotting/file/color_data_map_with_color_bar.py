import numpy as np

from bokeh.io import show
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import Viridis3
from bokeh.plotting import figure

x = np.random.random(2500) * 10
y = np.random.normal(size=2500) * 2 + 5
source = ColumnDataSource(dict(x=x, y=y))

lin_mapper = LinearColorMapper(palette=Viridis3, low=0, high=10)
color_bar = ColorBar(
    color_mapper=lin_mapper,
    legend_width='auto',
    legend_height='auto'
)

p = figure()
opts = dict(x='x', line_color=None, source=source)
p.circle(y='y', fill_color={'field': 'x', 'transform': lin_mapper}, **opts)
p.add_layout(color_bar)

show(p)
