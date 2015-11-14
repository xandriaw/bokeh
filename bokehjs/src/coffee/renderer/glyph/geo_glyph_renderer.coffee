GlyphRenderer = require "../glyph/glyph_renderer"

class GeoGlyphRendererView extends GlyphRenderer.View

class GeoGlyphRenderer extends GlyphRenderer.Model
  default_view: GeoGlyphRendererView
  type: 'GeoGlyphRenderer'

module.exports =
  Model: GeoGlyphRenderer
  View: GeoGlyphRendererView
