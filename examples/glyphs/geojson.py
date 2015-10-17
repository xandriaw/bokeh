from bokeh.io import output_file, show
from bokeh.models import Plot, Range1d, Circle, LinearAxis

output_file('geojson.html', mode='relative-dev')

plot = Plot(
    x_range=Range1d(-180, 180),
    y_range=Range1d(-90, 90)
)

with open('/Users/caged/Desktop/Optician.geojson', 'r') as f:
    geojson = f.read()

circle = Circle(x='coordinates', y='coordinates', fill_color='blue', size=50)

plot.add_geojson(geojson, point=circle)
plot.add_layout(LinearAxis(), 'below')
plot.add_layout(LinearAxis(), 'left')

show(plot)
