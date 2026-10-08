extends CharacterBody2D

signal health_changed(value: int)
signal died
signal sound_requested(effect: String)

const SPEED := 270.0
const JUMP := -490.0
var health := 100
var jumps := 0
var facing := 1.0
var attack_time := 0.0
var invincible_time := 0.0
var hit_targets: Array = []
var sprite: AnimatedSprite2D
var frozen := false
var world_width := 2400.0

func _ready() -> void:
	add_to_group("player")
	collision_layer = 2
	collision_mask = 1
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = Vector2(26, 48)
	shape.shape = rectangle
	shape.position.y = -24
	add_child(shape)
	sprite = AnimatedSprite2D.new()
	sprite.position.y = -32
	sprite.scale = Vector2(1.35, 1.35)
	sprite.sprite_frames = SpriteFrames.new()
	make_animation("idle", 4, Vector2i(38, 48), 6.0)
	make_animation("run", 12, Vector2i(66, 48), 14.0)
	make_animation("attack", 6, Vector2i(96, 48), 18.0)
	make_animation("jump", 5, Vector2i(61, 77), 10.0)
	add_child(sprite)
	sprite.play("idle")

func make_animation(anim: String, count: int, size: Vector2i, fps: float) -> void:
	var sheet: Texture2D = load("res://assets/hero_%s.png" % anim)
	sprite.sprite_frames.add_animation(anim)
	sprite.sprite_frames.set_animation_speed(anim, fps)
	sprite.sprite_frames.set_animation_loop(anim, anim != "attack" and anim != "jump")
	for i in count:
		var frame := AtlasTexture.new()
		frame.atlas = sheet
		frame.region = Rect2(Vector2(i * size.x, 0), size)
		sprite.sprite_frames.add_frame(anim, frame)

func jump() -> void:
	if jumps < 2 and not frozen:
		velocity.y = JUMP
		jumps += 1
		sound_requested.emit("jump")

func attack() -> void:
	if attack_time <= 0.0 and not frozen:
		attack_time = 0.34
		hit_targets.clear()
		sprite.play("attack")
		sound_requested.emit("sword")

func attack_rect() -> Rect2:
	return Rect2(global_position + Vector2(8 if facing > 0 else -82, -56), Vector2(74, 60))

func _physics_process(delta: float) -> void:
	if frozen:
		return
	invincible_time = maxf(0, invincible_time - delta)
	attack_time = maxf(0, attack_time - delta)
	if is_on_floor() and velocity.y >= 0:
		jumps = 0
	velocity.y += 1300.0 * delta
	var direction := Input.get_axis("move_left", "move_right")
	velocity.x = direction * SPEED
	if direction != 0:
		facing = signf(direction)
	if Input.is_action_just_pressed("jump"):
		jump()
	if Input.is_action_just_pressed("attack"):
		attack()
	move_and_slide()
	position.x = clampf(position.x, 20, world_width - 40)
	sprite.flip_h = facing < 0
	sprite.modulate.a = 0.45 if invincible_time > 0 else 1.0
	if attack_time > 0:
		for enemy in get_tree().get_nodes_in_group("enemies"):
			if not enemy in hit_targets and attack_rect().intersects(enemy.body_rect()):
				hit_targets.append(enemy)
				enemy.take_hit(25, facing)
	elif not is_on_floor():
		sprite.play("jump")
	elif direction != 0:
		sprite.play("run")
	else:
		sprite.play("idle")
	if position.y > 750:
		health = 0
		health_changed.emit(health)
		died.emit()
	queue_redraw()

func take_damage(amount: int) -> void:
	if invincible_time > 0 or frozen:
		return
	health = maxi(0, health - amount)
	invincible_time = 1.0
	health_changed.emit(health)
	sound_requested.emit("hurt")
	if health == 0:
		died.emit()

func heal(amount: int) -> void:
	health = mini(100, health + amount)
	health_changed.emit(health)

func _draw() -> void:
	if attack_time > 0:
		var center := Vector2(38 * facing, -30)
		draw_arc(center, 34, -1.6, 1.6, 12, Color(1, 0.85, 0.4, 0.65), 3)
