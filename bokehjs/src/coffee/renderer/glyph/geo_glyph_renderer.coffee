_ = require "underscore"
{logger} = require "../../common/logging"
GlyphRenderer = require "../glyph/glyph_renderer"

class GeoGlyphRendererView extends GlyphRenderer.View

  set_data: (request_render=true, arg) ->
    t0 = Date.now()
    source = @mget('data_source')

    @glyph.set_data(source, arg)

    @glyph.set_visuals(source)
    @decimated_glyph.set_visuals(source)
    @selection_glyph.set_visuals(source)
    @nonselection_glyph.set_visuals(source)

    length = source.get_length()
    length = 1 if not length?
    @all_indices = [0...length]

    lod_factor = @plot_model.get('lod_factor')
    @decimated = []
    for i in [0...Math.floor(@all_indices.length/lod_factor)]
      @decimated.push(@all_indices[i*lod_factor])

    dt = Date.now() - t0
    logger.debug("#{@glyph.model.type} GlyphRenderer (#{@model.id}): set_data finished in #{dt}ms")

    @set_data_timestamp = Date.now()

    if request_render
      @request_render()

class GeoGlyphRenderer extends GlyphRenderer.Model
  default_view: GeoGlyphRendererView
  type: 'GeoGlyphRenderer'

module.exports =
  Model: GeoGlyphRenderer
  View: GeoGlyphRendererView
