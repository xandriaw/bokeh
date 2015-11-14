from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, HoverTool

output_file('geo_point_plotting.html', mode='relative-dev')

with open('/Users/caged/Desktop/Optician-small.geojson', 'r') as f:
    geojson = f.read()

p = figure(tools='pan, box_zoom, reset')
geojson_source = GeoJSONDataSource(geojson)
p.circle(x='x', y='y', fill_color='blue', line_color=None, fill_alpha=0.5, size=16, source=geojson_source)
p.add_tools(HoverTool(tooltips=[("x", "@x")]))

show(p)
