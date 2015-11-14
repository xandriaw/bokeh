_ = require "underscore"
ColumnDataSource = require "./column_data_source"

class GeoJSONDataSource extends ColumnDataSource.Model
  type: 'GeoJSONDataSource'

  initialize: (options) ->
    @set('geojson', JSON.parse(options.geojson))
    @set('data', @geojson_to_column_data())
    console.log('initializing data source')
    super(options)

  _get_new_nan_array: (length) ->
    array = new Array(length)
    nan_array = _.map(array, (x) -> NaN)
    console.log('nan array')
    console.log(nan_array)
    return nan_array

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
          data['x'] = @_get_new_nan_array(data_length)
        if !data.hasOwnProperty('y')
          data['y'] = @_get_new_nan_array(data_length)
        if !data.hasOwnProperty('z')
          data['z'] = @_get_new_nan_array(data_length)

        data['x'][i] = geometry_coords[0] ? NaN
        data['y'][i] = geometry_coords[1] ? NaN
        data['z'][i] = geometry_coords[2] ? NaN

      for property in properties
        if !data.hasOwnProperty(property)
          data[property] = @_get_new_nan_array(data_length)
        data[property][i] = properties[property]
    console.log('my data is finished')
    return data

module.exports =
  Model: GeoJSONDataSource
