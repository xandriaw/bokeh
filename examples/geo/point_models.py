from bokeh.io import output_file, show
from bokeh.models import Plot, Range1d, Circle, LinearAxis, GeoJSONDataSource, HoverTool

output_file('geo_point.html', mode='relative-dev')

plot = Plot(
    x_range=Range1d(-8, 2),
    y_range=Range1d(48, 58)
)

with open('/Users/caged/Desktop/Optician.geojson', 'r') as f:
    geojson = f.read()

circle = Circle(x='x', y='y', fill_color='blue', line_color=None, fill_alpha=0.5, size=6)
geojson_source = GeoJSONDataSource(geojson)

plot.add_geo_glyph(geojson_source, circle, geometry_types=['Point'])
plot.add_tools(HoverTool(tooltips=[("x, y", "$x, $y")]))
plot.add_layout(LinearAxis(), 'below')
plot.add_layout(LinearAxis(), 'left')

show(plot)
