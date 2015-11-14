ColumnDataSource = require "./column_data_source"

class GeoJSONDataSource extends ColumnDataSource.Model
  type: 'GeoJSONDataSource'

  initialize: (options) ->
    super(options)
    @set('geojson', JSON.parse(options.geojson))
    @set('data', {
      'lon': [10, 20, 30],
      'lat': [15, 20, 30],
      'sizes': [10, 10, 10]
    })

module.exports =
  Model: GeoJSONDataSource
