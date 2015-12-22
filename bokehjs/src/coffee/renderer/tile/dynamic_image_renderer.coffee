_ = require "underscore"
HasParent = require "../../common/has_parent"
PlotWidget = require "../../common/plot_widget"
properties = require "../../common/properties"
ImagePool = require "./image_pool"
{logger} = require "../../common/logging"

class DynamicImageView extends PlotWidget

  get_extent: () ->
    return [@x_range.get('start'), @y_range.get('start'), @x_range.get('end'), @y_range.get('end')]

  _set_data: () ->
    @wrap_utils = WrapAroundUtils(@mget('wrap_around_start'), @mget('wrap_around_end'))
    @map_plot = @plot_view.model
    @map_canvas = @plot_view.canvas_view.ctx
    @map_frame = @plot_view.frame
    @x_range = @map_plot.get('x_range')
    @x_mapper = this.map_frame.get('x_mappers')['default']
    @y_range = @map_plot.get('y_range')
    @y_mapper = this.map_frame.get('y_mappers')['default']
    @lastImages = []
    @extent = @get_extent()

  _map_data: () ->
    @initial_extent = @get_extent()

  _on_image_load: (e) =>
    image_data = e.target.image_data
    image_data.img = e.target
    image_data.loaded = true
    @lastImage = image_data

    if @get_extent().join(':') == image_data.cache_key
      @request_render()

  _on_image_error: (e) =>
    logger.error('Error loading image: #{e.target.src}')
    image_data = e.target.image_data
    @mget('image_source').remove_image(image_data)

  _create_images: (bounds) ->
    height = Math.ceil(@map_frame.get('height'))
    width = Math.ceil(@map_frame.get('width'))
    if @mget('wrap_around')
      for i in @_partition_bounds(bounds)
        @_create_image(i.bounds, i.height, i.width)
    else
      @_create_image(bounds, height, width)
      
  _create_image: (image_data, height, width) ->
    image = new Image()
    image.onload = @_on_image_load
    image.onerror = @_on_image_error
    image.alt = ''

    image_data.loaded = false
    image_data.cache_key = image_data.bounds.join(':')

    image.image_data = image_data

    if 'normalized_bounds' of image_data
      bounds = image_data.normalized_bounds
    else
      bounds = image_bounds.bounds

    [sxmin, symin] = @plot_view.frame.map_to_screen([bounds[0]], [bounds[3]], @plot_view.canvas)
    [sxmax, symax] = @plot_view.frame.map_to_screen([bounds[2]], [bounds[1]], @plot_view.canvas)
    sxmin = sxmin[0]
    symin = symin[0]
    sxmax = sxmax[0]
    symax = symax[0]
    sw = sxmax - sxmin
    sh = symax - symin
    sx = sxmin
    sy = symin

    @mget('image_source').add_image(image.image_data)
    image.src = @mget('image_source').get_image_url(bounds[0], bounds[1], bounds[2], bounds[3], sh, sw)
    return image


  render: (ctx, indices, args) ->

    if not @map_initialized?
      @_set_data()
      @_map_data()
      @map_initialized = true

    extent = @get_extent()

    if @render_timer
      clearTimeout(@render_timer)

    image_obj = @mget('image_source').images[extent.join(':')]
    if image_obj? and image_obj.loaded
      @_draw_image(extent.join(':'))
      return

    if @lastImages?
      @_draw_images(@lastImages)

    if not image_obj?
      @render_timer = setTimeout((=> @_create_image(extent)), 125)

  _draw_images: (images) ->
    for i in images
      @_draw_image(i)

  _draw_image: (image_key) ->
    image_obj = @mget('image_source').images[image_key]
    if image_obj?
      @map_canvas.save()
      @_set_rect()
      @map_canvas.globalAlpha = @mget('alpha')
      [sxmin, symin] = @plot_view.frame.map_to_screen([image_obj.bounds[0]], [image_obj.bounds[3]], @plot_view.canvas)
      [sxmax, symax] = @plot_view.frame.map_to_screen([image_obj.bounds[2]], [image_obj.bounds[1]], @plot_view.canvas)
      sxmin = sxmin[0]
      symin = symin[0]
      sxmax = sxmax[0]
      symax = symax[0]
      sw = sxmax - sxmin
      sh = symax - symin
      sx = sxmin
      sy = symin
      @map_canvas.drawImage(image_obj.img, sx, sy, sw, sh)
      @map_canvas.restore()

  _set_rect:() ->
    outline_width = @plot_view.outline_props.width.value()
    l = @plot_view.canvas.vx_to_sx(@map_frame.get('left')) + (outline_width/2)
    t = @plot_view.canvas.vy_to_sy(@map_frame.get('top')) + (outline_width/2)
    w = @map_frame.get('width') - outline_width
    h = @map_frame.get('height') - outline_width
    @map_canvas.rect(l, t, w, h)
    @map_canvas.clip()

class DynamicImageRenderer extends HasParent
  default_view: DynamicImageView
  type: 'DynamicImageRenderer'
  visuals: []
  angles: ['angle']

  defaults: ->
    return _.extend {}, super(), {
      angle: 0
      alpha: 1.0
      image_source:undefined
      wrap_around: False
      wrap_around_start: -1 * Math.PI * 6378137
      wrap_around_end: Math.PI * 6378137
    }

  display_defaults: ->
    return _.extend {}, super(), {
      level: 'underlay'
    }

class WrapAroundUtils

  constructor: (wrap_min, wrap_max, canvas) ->
    @wrap_min = wrap_min
    @wrap_max = wrap_max
    @wrap_range = wrap_max - wrap_min

  world_to_1d_range: (world_x) ->
    offset = @wrap_range * world_x
    return [@wrap_min + offset, @wrap_max + offset]

  extent_to_world_range:(bounds) ->
    [xmin, ymin, xmax, ymax] = bounds
    world_min = Math.floor((xmin - @wrap_min)  / @wrap_range)
    world_max = Math.floor((xmax + @wrap_max) / @wrap_range)
    return [world_min, world_max]

  clip_extent_by_world:(bounds, world) ->
    [xmin, ymin, xmax, ymax] = bounds
    [wmin, wmax] = @world_to_1d_range(world)
    return [Math.max(xmin, wmin), ymin, Math.min(xmax, wmax), ymax]

  map_range:(x, o_min, o_max, n_min, n_max) ->

    #check reversed input ranges
    reverse_input = false
    old_min = Math.min(o_min, o_max)
    old_max = Math.max(o_min, o_max)
    if not old_min == o_min
        reverse_input = True

    reverse_output = false
    new_min = Math.min(n_min, n_max)
    new_max = Math.max(n_min, n_max)
    if not new_min == n_min
        reverse_output = true

    portion = (x - old_min) * (new_max - new_min) / (old_max - old_min)
    if reverse_input
        portion = (old_max - x) * (new_max - new_min) / (old_max - old_min)

    result = portion + new_min
    if reverse_output
        result = new_max - portion

    return result

  normalize_bounds: (bounds, world) ->
      [xmin, ymin, xmax, ymax] = bounds
      [world_min, world_max] = @world_to_1d_range(world)
      nxmin = @map_range(xmin, world_min, world_max, @wrap_min, @wrap_max)
      nxmax = @map_range(xmax, world_min, world_max, @wrap_min, @wrap_max)
      return [nxmin, ymin, nxmax, ymax]

  partition_bounds: (bounds) ->
    [world_min, world_max] = @extent_to_world_range(bounds)
    parts = []
    for w in [world_min..world_max] by 1
      actual_bounds = @clip_extent_by_world(bounds, w)
      normalized_bounds = @normalize_bounds(actual_bounds, w)
      part =
        bounds:actual_bounds
        normalized_bounds:normalized_bounds
      parts.push(part)

    return parts


module.exports =
  Model: DynamicImageRenderer
  View: DynamicImageView
  WrapAroundUtils: WrapAroundUtils
