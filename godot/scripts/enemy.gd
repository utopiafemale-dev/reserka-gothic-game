extends CharacterBody2D

signal defeated
signal sound_requested(effect: String)

var kind := "skull"
var health := 50
var max_health := 50
var world_width := 2400.0
var origin := Vector2.ZERO
var elapsed := 0.0
var hurt_time := 0.0
var windup := 0.0
var cooldown := 1.0
var charge_time := 0.0
var charge_direction := 1.0
var sprite: AnimatedSprite2D
var body_size := Vector2(40,40)

func _ready() -> void:
 add_to_group("enemies")
 origin = position
 collision_layer = 4
 collision_mask = 1
 if kind == "demon":
  health = 100
  body_size = Vector2(44,70)
 elif kind == "warden":
  health = 250
  body_size = Vector2(66,100)
 elif kind == "hound":
  body_size = Vector2(50,30)
 max_health = health
 var shape := CollisionShape2D.new()
 var rect := RectangleShape2D.new()
 rect.size = body_size
 shape.shape = rect
 shape.position.y = -body_size.y/2
 add_child(shape)
 sprite = AnimatedSprite2D.new()
 sprite.sprite_frames = SpriteFrames.new()
 var file := "skull" if kind == "skull" else ("hound" if kind == "hound" else "demon")
 var sheet: Texture2D = load("res://assets/%s.png" % file)
 var count := 8 if kind == "skull" else (5 if kind == "hound" else 12)
 for i in count:
  var frame := AtlasTexture.new()
  frame.atlas = sheet
  frame.region = Rect2(i*sheet.get_width()/float(count),0,sheet.get_width()/float(count),sheet.get_height())
  sprite.sprite_frames.add_frame("default",frame)
 sprite.sprite_frames.set_animation_speed("default",10)
 var scale_factor := 0.5 if kind == "skull" else (1.0 if kind == "hound" else (0.75 if kind == "warden" else 0.55))
 sprite.scale = Vector2.ONE * scale_factor
 sprite.position.y = -sheet.get_height()*scale_factor/2
 add_child(sprite)
 sprite.play()

func body_rect() -> Rect2:
 return Rect2(global_position-Vector2(body_size.x/2,body_size.y),body_size)

func _physics_process(delta: float) -> void:
 if health <= 0:
  return
 var player = get_tree().get_first_node_in_group("player")
 if player == null or player.frozen:
  return
 elapsed += delta
 hurt_time = maxf(0,hurt_time-delta)
 cooldown = maxf(0,cooldown-delta)
 sprite.modulate = Color(1,0.4,0.4) if hurt_time > 0 else (Color(1,0.75,0.3) if windup > 0 else Color.WHITE)
 var target: Vector2 = player.global_position
 var distance: float = global_position.distance_to(target)
 var direction := signf(target.x-position.x)
 if kind == "skull":
  if distance < 260:
   velocity = global_position.direction_to(target) * 80
  else:
   velocity = Vector2(cos(elapsed)*55,sin(elapsed*2)*20)
 else:
  velocity.y += 1300*delta
  var speed := 70.0 if kind == "demon" else (85.0 if kind == "warden" else 125.0)
  if kind == "warden" and health <= max_health/2:
   speed = 115
  velocity.x = direction*speed if distance < 350 else cos(elapsed)*35
  if kind == "hound":
   if cooldown <= 0 and distance < 220:
    charge_time = 0.55
    charge_direction = direction
    cooldown = 2.0
   if charge_time > 0:
    charge_time -= delta
    velocity.x = charge_direction*250
  elif kind in ["demon","warden"]:
   var reach := 125.0 if kind == "warden" else 85.0
   if windup > 0:
    velocity.x = 0
    windup -= delta
    if windup <= 0:
     if distance < reach and absf(target.y-position.y) < 70:
      player.take_damage(25 if kind == "warden" else 20)
     cooldown = 1.5 if kind == "warden" else 2.0
   elif cooldown <= 0 and distance < reach:
    windup = 0.7
  # Ground enemies stop at ledges; the player can jump the cavern gaps.
  if is_on_floor() and absf(velocity.x) > 0:
   var look := position+Vector2(signf(velocity.x)*35,-5)
   var query := PhysicsRayQueryParameters2D.create(look,look+Vector2(0,35),1)
   if get_world_2d().direct_space_state.intersect_ray(query).is_empty():
    velocity.x = 0
 move_and_slide()
 position.x = clampf(position.x,30,world_width-30)
 sprite.flip_h = velocity.x < 0
 if body_rect().intersects(Rect2(player.global_position-Vector2(13,48),Vector2(26,48))):
  player.take_damage(10 if kind != "warden" else 20)
 if position.y > 750:
  take_hit(health,0)
 queue_redraw()

func take_hit(amount: int, direction: float) -> void:
 if health <= 0:
  return
 health -= amount
 hurt_time = 0.2
 position.x += direction*28
 if health <= 0:
  remove_from_group("enemies")
  defeated.emit()
  queue_free()
 else:
  sound_requested.emit("sword")

func _draw() -> void:
 if health < max_health or kind == "warden":
  var width := 70.0 if kind == "warden" else 40.0
  draw_rect(Rect2(-width/2,-body_size.y-14,width,5),Color(0.15,0.05,0.08))
  draw_rect(Rect2(-width/2,-body_size.y-14,width*maxf(health,0)/max_health,5),Color(0.9,0.3,0.3))
 if windup > 0:
  draw_arc(Vector2(0,-18),125 if kind == "warden" else 85,PI,TAU,20,Color(1,0.6,0.2,0.6),3)
