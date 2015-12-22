_ = require "underscore"
{expect, assert} = require "chai"
utils = require "../../utils"
base = utils.require "common/base"
{WrapAroundUtils} = utils.require "renderer/tile/dynamic_image_renderer"
ImageSource = utils.require "renderer/tile/image_source"

describe "dynamic image renderer", ->

  describe "image source", ->

    it "should handle case-insensitive url parameters (template url)", ->
      image_options =
        url : 'http://test/{height}/{width}/{xmin}/{ymin}/{xmax}/{ymax}.png'

      expect_url = 'http://test/5/6/1/2/3/4.png'
      image_source = new ImageSource.Model(image_options)
      expect(image_source.get_image_url(1,2,3,4,5,6)).to.be.equal(expect_url)
   
    it "should successfully set extra_url_vars property", ->

      test_extra_url_vars =
        test_key : 'test_value'
        test_key2 : 'test_value2'

      image_options =
        url : 'http://{test_key}/{test_key2}/{XMIN}/{YMIN}/{XMAX}/{YMAX}.png'
        extra_url_vars : test_extra_url_vars

      image_source = new ImageSource.Model(image_options)
      expect_url = 'http://test_value/test_value2/0/0/0/0.png'
      expect(image_source.get('extra_url_vars')).to.have.any.keys('test_key')
      expect(image_source.get('extra_url_vars')).to.have.any.keys('test_key2')
      formatted_url = image_source.get_image_url(0,0,0,0,0,0)
      expect(formatted_url).to.be.equal(expect_url)

  describe "wrap around utils", ->

    it "should calculate world to its corresponding 1d range (int -> [min, max])", ->

      utils = new WrapAroundUtils(-10, 10)

      [wmin, wmax] = utils.world_to_1d_range(-2)
      expect(wmin).to.be.equal(-50)
      expect(wmax).to.be.equal(-30)

      [wmin, wmax] = utils.world_to_1d_range(-1)
      expect(wmin).to.be.equal(-30)
      expect(wmax).to.be.equal(-10)

      [wmin, wmax] = utils.world_to_1d_range(0)
      expect(wmin).to.be.equal(-10)
      expect(wmax).to.be.equal(10)

      [wmin, wmax] = utils.world_to_1d_range(1)
      expect(wmin).to.be.equal(10)
      expect(wmax).to.be.equal(30)

      [wmin, wmax] = utils.world_to_1d_range(2)
      expect(wmin).to.be.equal(30)
      expect(wmax).to.be.equal(50)

    it "should convert extent to world range", ->
      utils = new WrapAroundUtils(-10, 10)

      bounds = [-5, -5, 5, 5]
      [wmin, wmax] = utils.extent_to_world_range(bounds)
      expect(wmin).to.be.equal(0)
      expect(wmax).to.be.equal(0)

      bounds = [-5, -5, 15, 15]
      [wmin, wmax] = utils.extent_to_world_range(bounds)
      expect(wmin).to.be.equal(0)
      expect(wmax).to.be.equal(1)

      bounds = [-25, -5, 15, 15]
      [wmin, wmax] = utils.extent_to_world_range(bounds)
      expect(wmin).to.be.equal(-1)
      expect(wmax).to.be.equal(1)

      bounds = [-35, -5, 15, 15]
      [wmin, wmax] = utils.extent_to_world_range(bounds)
      expect(wmin).to.be.equal(-2)
      expect(wmax).to.be.equal(1)

    it "should remap values between ranges", ->
      utils = new WrapAroundUtils()

      val = utils.map_range(75, 0, 100, -50, 50)
      expect(val).to.be.equal(25)

    it "should clip extent by world", ->
      utils = new WrapAroundUtils(-10, 10)

      bounds = [-5, -5, 5, 5]
      val = utils.clip_extent_by_world(bounds, 0)
      expect(val).to.deep.equal(bounds)

      bounds = [-15, -5, 15, 5]
      val = utils.clip_extent_by_world(bounds, 0)
      expect(val).to.deep.equal([-10, -5, 10, 5])

      bounds = [-100, -5, 100, 5]
      val = utils.clip_extent_by_world(bounds, -1)
      expect(val).to.deep.equal([-30, -5, -10, 5])

    it "should partition bounds by wrap around extents", ->
      utils = new WrapAroundUtils(-10, 10)

      bounds = [-25, -5, 25, 5]
      parts = utils.partition_bounds(bounds)
      assert.isArray(parts, 'output is not an array')
      expect(parts.length).to.be.equal(3)

      for p in parts
        expect(p).to.have.property('bounds')
        expect(p).to.have.property('normalized_bounds')

      expect(parts[0].bounds).to.deep.equal([-25, -5, -10, 5])
      expect(parts[0].normalized_bounds).to.deep.equal([-5, -5, 10, 5])
      expect(parts[1].bounds).to.deep.equal([-10, -5, 10, 5])
      expect(parts[1].normalized_bounds).to.deep.equal([-10, -5, 10, 5])
      expect(parts[2].bounds).to.deep.equal([10, -5, 25, 5])
      expect(parts[2].normalized_bounds).to.deep.equal([-10, -5, 5, 5])
