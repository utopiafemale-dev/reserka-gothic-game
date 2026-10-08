extends CharacterBody3D

signal health_changed(value: int)
signal died
signal sound_requested(effect: String)
signal hurt

const Sprites = preload("res://three_d/sprites.gd")
@export var rules: Resource = preload("res://three_d/gameplay.tres")
var health := 100
var world_width := 24.0
var jumps := 0
var facing := 1.0
var attack_time := 0.0
var invincible_time := 0.0
var coyote := 0.0
var jump_buffer := 0.0
var frozen := false
var hit_targets: Array = []
var sprite: AnimatedSprite3D
var slash: MeshInstance3D
var controller_id := 1
var slot := 1
var character := "knight"
var network
var simulation_enabled := true
var visual_target := Vector3.ZERO
var display_tag: Label3D
var character_color := Color.WHITE

func _ready() -> void:
 add_to_group("player3d")
 health = rules.max_health
 collision_layer = 2
 collision_mask = 1
 axis_lock_linear_z = true
 var shape := CollisionShape3D.new()
 var box := BoxShape3D.new()
 box.size = Vector3(0.26,0.48,0.3)
 shape.shape = box
 shape.position.y = 0.24
 add_child(shape)
 sprite = Sprites.hero(character)
 if character == "spectral":
  character_color = Color(0.45,0.9,1)
 elif character == "crimson":
  character_color = Color(1,0.45,0.5)
 sprite.modulate = character_color
 add_child(sprite)
 display_tag = Label3D.new()
 display_tag.text = "P%d" % slot
 display_tag.position.y = 0.85
 display_tag.font_size = 20
 display_tag.pixel_size = 0.004
 display_tag.billboard = BaseMaterial3D.BILLBOARD_ENABLED
 display_tag.modulate = Color.from_hsv(float(slot-1)/8,0.5,1)
 add_child(display_tag)
 slash = MeshInstance3D.new()
 var torus := TorusMesh.new()
 torus.inner_radius = 0.30
 torus.outer_radius = 0.34
 slash.mesh = torus
 slash.rotation.x = PI/2
 var mat := StandardMaterial3D.new()
 mat.albedo_color = Color(1,0.75,0.3)
 mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
 mat.emission_enabled = true
 mat.emission = Color(1,0.5,0.1)
 slash.material_override = mat
 slash.visible = false
 add_child(slash)

func jump() -> bool:
 if frozen:
  return false
 if jumps == 0 and not is_on_floor() and coyote <= 0:
  jumps = 1
 if jumps >= rules.max_jumps:
  return false
 velocity.y = rules.jump_speed
 jumps += 1
 coyote = 0
 jump_buffer = 0
 sound_requested.emit("jump")
 return true

func attack() -> void:
 if attack_time <= 0 and not frozen:
  attack_time = rules.attack_seconds
  hit_targets.clear()
  sprite.play("attack")
  sound_requested.emit("sword")

func body_rect() -> Rect2:
 return Rect2(Vector2(position.x-0.13,position.y),Vector2(0.26,0.48))

func attack_rect() -> Rect2:
 return Rect2(Vector2(position.x+(0.08 if facing > 0 else -0.82),position.y-0.04),Vector2(0.74,0.6))

func _physics_process(delta: float) -> void:
 if not simulation_enabled:
  return
 if frozen:
  slash.visible = false
  return
 invincible_time = maxf(0,invincible_time-delta)
 attack_time = maxf(0,attack_time-delta)
 jump_buffer = maxf(0,jump_buffer-delta)
 if is_on_floor() and velocity.y <= 0:
  jumps = 0
  coyote = rules.coyote_seconds
 else:
  coyote = maxf(0,coyote-delta)
 velocity.y -= rules.gravity*delta
 var remote: bool = network != null and network.is_remote_controller(controller_id)
 var control: Dictionary = network.consume_input(controller_id) if remote else {}
 var direction: float = control.get("axis",0.0) if remote else Input.get_axis("move_left","move_right")
 velocity.x = move_toward(velocity.x,direction*rules.move_speed,rules.acceleration*delta)
 if direction != 0:
  facing = signf(direction)
 if (control.get("jump",false) if remote else Input.is_action_just_pressed("jump")):
  jump_buffer = rules.jump_buffer_seconds
  # Zero buffering still accepts the initial press.
  jump()
 elif jump_buffer > 0:
  jump()
 if (control.get("attack",false) if remote else Input.is_action_just_pressed("attack")):
  attack()
 move_and_slide()
 position.x = clampf(position.x,0.2,world_width-0.4)
 position.z = 0
 velocity.z = 0
 sprite.flip_h = facing < 0
 sprite.modulate = Color(0.5,1,1) if invincible_time > 0 else character_color
 slash.visible = attack_time > 0
 slash.position = Vector3(facing*0.38,0.3,0.08)
 if attack_time > 0:
  for enemy in get_tree().get_nodes_in_group("enemies3d"):
   if not enemy in hit_targets and attack_rect().intersects(enemy.body_rect()):
    hit_targets.append(enemy)
    enemy.take_hit(rules.sword_damage,facing)
 elif not is_on_floor():
  sprite.play("jump")
 elif direction != 0:
  sprite.play("run")
 else:
  sprite.play("idle")
 if position.y < -2.7:
  health = 0
  health_changed.emit(health)
  died.emit()

func take_damage(amount: int) -> void:
 if invincible_time > 0 or frozen:
  return
 health = maxi(0,health-amount)
 invincible_time = rules.invulnerability_seconds
 health_changed.emit(health)
 sound_requested.emit("hurt")
 hurt.emit()
 if health == 0:
  died.emit()

func heal(amount: int) -> void:
 health = mini(rules.max_health,health+amount)
 health_changed.emit(health)

func _process(delta: float) -> void:
 if not simulation_enabled:
  position = position.lerp(visual_target,1-exp(-18*delta))

func apply_state(state: Dictionary) -> void:
 visual_target = state.position
 if position.distance_to(visual_target) > 3:
  position = visual_target
 velocity = state.velocity
 health = state.health
 frozen = state.frozen
 facing = state.facing
 jumps = state.jumps
 attack_time = state.attack
 sprite.flip_h = facing < 0
 sprite.modulate = Color(0.3,0.3,0.4) if health <= 0 else (Color(0.5,1,1) if state.invincible > 0 else character_color)
 display_tag.text = "P%d DOWN" % slot if health <= 0 else "P%d" % slot
 sprite.play(state.animation)
 slash.visible = attack_time > 0
 slash.position = Vector3(facing*0.38,0.3,0.08)
