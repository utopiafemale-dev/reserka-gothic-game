extends RefCounted

static func animation(frames: SpriteFrames, name: String, path: String, count: int, size: Vector2, fps: float) -> void:
 var sheet: Texture2D = load(path)
 frames.add_animation(name)
 frames.set_animation_speed(name,fps)
 frames.set_animation_loop(name,name not in ["attack","jump"])
 for i in count:
  var atlas := AtlasTexture.new()
  atlas.atlas = sheet
  atlas.region = Rect2(Vector2(i*size.x,0),size)
  frames.add_frame(name,atlas)

static func hero(character := "knight") -> AnimatedSprite3D:
 var sprite := AnimatedSprite3D.new()
 sprite.sprite_frames = SpriteFrames.new()
 animation(sprite.sprite_frames,"idle","res://assets/hero_idle.png",4,Vector2(38,48),6)
 animation(sprite.sprite_frames,"run","res://assets/hero_run.png",12,Vector2(66,48),14)
 animation(sprite.sprite_frames,"attack","res://assets/hero_attack.png",6,Vector2(96,48),18)
 animation(sprite.sprite_frames,"jump","res://assets/hero_jump.png",5,Vector2(61,77),10)
 if character == "adventurer":
  sprite.sprite_frames = SpriteFrames.new()
  for anim in ["idle","run","attack","jump"]:
   var sheet: Texture2D = load("res://assets/adventurer/%s.png" % anim)
   sprite.sprite_frames.add_animation(anim)
   sprite.sprite_frames.set_animation_speed(anim,12 if anim != "idle" else 6)
   for i in 6:
    var atlas := AtlasTexture.new()
    atlas.atlas = sheet
    atlas.region = Rect2(i*64+16,16,32,32)
    sprite.sprite_frames.add_frame(anim,atlas)
  sprite.pixel_size = 0.023
  sprite.position.y = 0.30
 else:
  sprite.pixel_size = 0.0135
  sprite.position.y = 0.32
 setup(sprite)
 sprite.play("idle")
 return sprite

static func enemy(kind: String) -> AnimatedSprite3D:
 var sprite := AnimatedSprite3D.new()
 sprite.sprite_frames = SpriteFrames.new()
 var file := "skull" if kind == "skull" else ("hound" if kind == "hound" else "demon")
 var count := 8 if kind == "skull" else (5 if kind == "hound" else 12)
 var sheet: Texture2D = load("res://assets/%s.png" % file)
 animation(sprite.sprite_frames,"idle","res://assets/%s.png" % file,count,Vector2(sheet.get_width()/float(count),sheet.get_height()),10)
 var scale_factor := 0.5 if kind == "skull" else (1.0 if kind == "hound" else (0.75 if kind == "warden" else 0.55))
 sprite.pixel_size = 0.01*scale_factor
 sprite.position.y = sheet.get_height()*sprite.pixel_size/2
 setup(sprite)
 sprite.play("idle")
 return sprite

static func setup(sprite: AnimatedSprite3D) -> void:
 sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
 sprite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
 sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
 sprite.shaded = false
