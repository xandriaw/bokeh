Circle = require "../glyph/circle"

class GeoCircleView extends Circle.View

class GeoCircle extends Circle.Model
  default_view: GeoCircleView

module.exports =
  Model: GeoCircle
  View: GeoCircleView
