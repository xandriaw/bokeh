ColumnDataSource = require "./column_data_source"

class GeoJSONDataSource extends ColumnDataSource.Model
  type: 'GeoJSONDataSource'

  initialize: (options) ->
    super(options)
    @set('geojson', JSON.parse(options.geojson))
    @set('data', @geojson_to_column_data())

  geojson_to_column_data: () ->
    geojson = @get('geojson')
    if geojson['type'] != "FeatureCollection" and "features" not in geojson
        throw new Error("Only FeatureCollections are currently supported")
    features = geojson['features']
    data_length = features.length
    data = {}
    for feature, i in features
      if feature['type'] != "Feature"
        throw new Error("Feature not found in geojson features array")
      properties = feature.properties ? {}
      geometry = feature.geometry
      geometry_type = geometry.type
      geometry_coords = geometry.coordinates

      if geometry_type == "Point"
        if !data.hasOwnProperty('x')
          data['x'] = new Array(data_length)
        if !data.hasOwnProperty('y')
          data['y'] = new Array(data_length)
        if !data.hasOwnProperty('z')
          data['z'] = new Array(data_length)

        data['x'][i] = geometry_coords[0]
        data['y'][i] = geometry_coords[1]
        data['z'][i] = geometry_coords[2]

      for property in properties
        if !data.hasOwnProperty(property)
          data[property] = new Array(data_length)
        data[property][i] = properties[property]
    return data

module.exports =
  Model: GeoJSONDataSource
