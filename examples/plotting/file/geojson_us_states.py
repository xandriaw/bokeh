from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource, Range1d, HoverTool
from bokeh.plotting import figure

output_file("us_states.html", title="GeoJSON US States", mode='inline')

with open('gz_2010_us_040_00_20m.json', 'r') as f:
    geojson = f.read()

p = figure(x_range=Range1d(-175, -50), y_range=Range1d(-10, 80), tools='pan,box_zoom,box_select,wheel_zoom,tap,reset')
p.add_tools(HoverTool(tooltips=[('state', '@NAME')]))
p.patches(line_width=2, line_color='black', line_alpha=0.8, fill_color='gray', fill_alpha=0.2, source=GeoJSONDataSource(geojson=geojson))
show(p)
