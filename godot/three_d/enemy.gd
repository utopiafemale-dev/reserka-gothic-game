extends CharacterBody3D

signal defeated
signal sound_requested(effect: String)

const Sprites = preload("res://three_d/sprites.gd")
@export var kind := "skull"
@export var rules: Resource = preload("res://three_d/gameplay.tres")
var world_width := 24.0
var health := 50
var max_health := 50
var elapsed := 0.0
var hurt_time := 0.0
var windup := 0.0
var cooldown := 1.0
var charge_time := 0.0
var charge_direction := 1.0
var body_size := Vector2(0.4,0.4)
var sprite: AnimatedSprite3D
var label: Label3D
var enemy_id := 0
var simulation_enabled := true
var visual_target := Vector3.ZERO

func _ready() -> void:
 add_to_group("enemies3d")
 health = rules.skull_health
 if kind == "demon":
  health = rules.demon_health
  body_size = Vector2(0.44,0.7)
 elif kind == "warden":
  health = rules.boss_health
  body_size = Vector2(0.66,1)
 elif kind == "hound":
  health = rules.hound_health
  body_size = Vector2(0.5,0.3)
 max_health = health
 collision_layer = 4
 collision_mask = 1
 axis_lock_linear_z = true
 var shape := CollisionShape3D.new()
 var box := BoxShape3D.new()
 box.size = Vector3(body_size.x,body_size.y,0.3)
 shape.shape = box
 shape.position.y = body_size.y/2
 add_child(shape)
 sprite = Sprites.enemy(kind)
 add_child(sprite)
 label = Label3D.new()
 label.position.y = body_size.y+0.18
 label.pixel_size = 0.005
 label.font_size = 22
 label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
 label.modulate = Color(1,0.65,0.5)
 add_child(label)
 update_label()

func update_label() -> void:
 label.text = ("WARDEN  " if kind == "warden" else "") + "%d/%d" % [maxi(0,health),max_health]
 label.visible = health < max_health or kind == "warden"

func body_rect() -> Rect2:
 return Rect2(Vector2(position.x-body_size.x/2,position.y),body_size)

func _physics_process(delta: float) -> void:
 if not simulation_enabled:
  return
 var player = null
 var nearest := INF
 for candidate in get_tree().get_nodes_in_group("player3d"):
  var distance: float = position.distance_to(candidate.position)
  if not candidate.frozen and distance < nearest:
   nearest = distance
   player = candidate
 if health <= 0 or player == null or player.frozen:
  return
 elapsed += delta
 hurt_time = maxf(0,hurt_time-delta)
 cooldown = maxf(0,cooldown-delta)
 sprite.modulate = Color(1,0.4,0.4) if hurt_time > 0 else (Color(1,0.75,0.3) if windup > 0 else Color.WHITE)
 var target: Vector3 = player.position
 var distance := position.distance_to(target)
 var direction := signf(target.x-position.x)
 if kind == "skull":
  velocity = position.direction_to(target)*0.8 if distance < 2.6 else Vector3(cos(elapsed)*0.55,sin(elapsed*2)*0.2,0)
  velocity *= rules.enemy_speed_multiplier
 else:
  velocity.y -= rules.gravity*delta
  var speed := 0.7 if kind == "demon" else (0.85 if kind == "warden" else 1.25)
  if kind == "warden" and health <= max_health/2:
   speed = 1.15
  velocity.x = (direction*speed if distance < 3.5 else cos(elapsed)*0.35)*rules.enemy_speed_multiplier
  if kind == "hound":
   if cooldown <= 0 and distance < 2.2:
    charge_time = 0.55
    charge_direction = direction
    cooldown = 2
   if charge_time > 0:
    charge_time -= delta
    velocity.x = charge_direction*2.5*rules.enemy_speed_multiplier
  else:
   var reach := 1.25 if kind == "warden" else 0.85
   if windup > 0:
    velocity.x = 0
    windup -= delta
    if windup <= 0:
     if distance < reach and absf(target.y-position.y) < 0.7:
      player.take_damage(25 if kind == "warden" else 20)
     cooldown = 1.5 if kind == "warden" else 2
   elif cooldown <= 0 and distance < reach:
    windup = 0.7
  if is_on_floor() and absf(velocity.x) > 0:
   var look := position+Vector3(signf(velocity.x)*0.35,0.05,0)
   var query := PhysicsRayQueryParameters3D.create(look,look-Vector3(0,0.35,0),1)
   if get_world_3d().direct_space_state.intersect_ray(query).is_empty():
    velocity.x = 0
 move_and_slide()
 position.z = 0
 velocity.z = 0
 position.x = clampf(position.x,0.3,world_width-0.3)
 sprite.flip_h = velocity.x < 0
 for candidate in get_tree().get_nodes_in_group("player3d"):
  if body_rect().intersects(candidate.body_rect()):
   candidate.take_damage(20 if kind == "warden" else 10)
 if position.y < -2.7:
  take_hit(health,0)

func take_hit(amount: int, direction: float) -> void:
 if not simulation_enabled:
  return
 if health <= 0:
  return
 health -= amount
 hurt_time = 0.2
 position.x += direction*0.28
 update_label()
 if health <= 0:
  remove_from_group("enemies3d")
  defeated.emit()
  queue_free()
 else:
  sound_requested.emit("sword")

func _process(delta: float) -> void:
 if not simulation_enabled:
  position = position.lerp(visual_target,1-exp(-18*delta))

func apply_state(state: Dictionary) -> void:
 visual_target = state.position
 if position.distance_to(visual_target) > 3:
  position = visual_target
 health = state.health
 windup = state.windup
 sprite.flip_h = state.facing
 sprite.modulate = Color(1,0.4,0.4) if state.hurt > 0 else (Color(1,0.75,0.3) if windup > 0 else Color.WHITE)
 update_label()
