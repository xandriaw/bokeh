from bokeh.io import output_file, show
from bokeh.models import Plot, Range1d, GeoCircle, LinearAxis, GeoJSONDataSource

output_file('geo_point.html', mode='relative-dev')

plot = Plot(
    x_range=Range1d(-180, 180),
    y_range=Range1d(-90, 90)
)

with open('/Users/caged/Desktop/Optician.geojson', 'r') as f:
    geojson = f.read()

geo_circle = GeoCircle(fill_color='blue', size=50, geometry_types=['Point'])
geojson_source = GeoJSONDataSource(geojson)

plot.add_geo_glyph(geojson_source, geo_circle)
plot.add_layout(LinearAxis(), 'below')
plot.add_layout(LinearAxis(), 'left')

show(plot)
