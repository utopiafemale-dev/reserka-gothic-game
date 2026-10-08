extends CharacterBody2D

signal defeated

var health := 50
var origin := Vector2.ZERO
var elapsed := 0.0
var hurt_time := 0.0
var sprite: AnimatedSprite2D

func _ready() -> void:
	add_to_group("enemies")
	origin = position
	collision_layer = 4
	collision_mask = 1
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(36, 36)
	shape.shape = rect
	add_child(shape)
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = SpriteFrames.new()
	var sheet: Texture2D = load("res://assets/skull.png")
	for i in 8:
		var frame := AtlasTexture.new()
		frame.atlas = sheet
		frame.region = Rect2(i * sheet.get_width() / 8.0, 0, sheet.get_width() / 8.0, sheet.get_height())
		sprite.sprite_frames.add_frame("default", frame)
	sprite.sprite_frames.set_animation_speed("default", 10)
	sprite.scale = Vector2(0.5, 0.5)
	add_child(sprite)
	sprite.play()

func body_rect() -> Rect2:
	return Rect2(global_position - Vector2(20, 20), Vector2(40, 40))

func _physics_process(delta: float) -> void:
	if health <= 0:
		return
	elapsed += delta
	hurt_time = maxf(0, hurt_time - delta)
	sprite.modulate = Color(1, 0.4, 0.4) if hurt_time > 0 else Color.WHITE
	var player = get_tree().get_first_node_in_group("player")
	if player == null or player.frozen:
		return
	var target: Vector2 = player.global_position + Vector2(0, -28)
	if target.distance_to(global_position) < 250:
		velocity = global_position.direction_to(target) * 80
	else:
		velocity = Vector2(cos(elapsed) * 55, sin(elapsed * 2) * 20)
	move_and_slide()
	sprite.flip_h = velocity.x < 0
	if body_rect().intersects(Rect2(player.global_position - Vector2(13, 48), Vector2(26, 48))):
		player.take_damage(10)

func take_hit(amount: int, direction: float) -> void:
	if health <= 0:
		return
	health -= amount
	hurt_time = 0.2
	position.x += direction * 28
	if health <= 0:
		remove_from_group("enemies")
		defeated.emit()
		queue_free()
