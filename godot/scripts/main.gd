extends Node2D

const Player = preload("res://scripts/player.gd")
const Enemy = preload("res://scripts/enemy.gd")
var player
var souls := 0
var finished := false
var hud: Label
var message: Label
var platforms: Array[Rect2] = []
var background := preload("res://assets/castle.png")

func bind_action(action: String, keys: Array) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	for key in keys:
		var event := InputEventKey.new()
		event.physical_keycode = key
		InputMap.action_add_event(action, event)

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	bind_action("move_left", [KEY_A, KEY_LEFT])
	bind_action("move_right", [KEY_D, KEY_RIGHT])
	bind_action("jump", [KEY_SPACE, KEY_W, KEY_UP])
	bind_action("attack", [KEY_X, KEY_J])
	bind_action("restart", [KEY_R])
	bind_action("pause", [KEY_ESCAPE])
	platforms = [Rect2(0, 480, 2400, 60), Rect2(240, 380, 230, 22),
		Rect2(570, 305, 220, 22), Rect2(920, 375, 230, 22),
		Rect2(1300, 290, 220, 22), Rect2(1680, 365, 240, 22), Rect2(2040, 300, 220, 22)]
	for platform in platforms:
		var body := StaticBody2D.new()
		body.position = platform.position + platform.size / 2
		var shape := CollisionShape2D.new()
		var rectangle := RectangleShape2D.new()
		rectangle.size = platform.size
		shape.shape = rectangle
		body.add_child(shape)
		add_child(body)
	player = Player.new()
	player.process_mode = Node.PROCESS_MODE_PAUSABLE
	player.position = Vector2(100, 470)
	add_child(player)
	player.health_changed.connect(update_hud.unbind(1))
	player.died.connect(end_game.bind(false))
	var camera := Camera2D.new()
	camera.position.y = -210
	camera.limit_left = 0
	camera.limit_right = 2400
	camera.limit_top = 0
	camera.limit_bottom = 540
	player.add_child(camera)
	for point in [Vector2(410, 340), Vector2(720, 260), Vector2(1080, 430), Vector2(1440, 250), Vector2(1840, 320)]:
		var enemy := Enemy.new()
		enemy.process_mode = Node.PROCESS_MODE_PAUSABLE
		enemy.position = point
		enemy.defeated.connect(collect_soul)
		add_child(enemy)
	var ui := CanvasLayer.new()
	add_child(ui)
	hud = Label.new()
	hud.position = Vector2(24, 16)
	hud.add_theme_font_size_override("font_size", 22)
	ui.add_child(hud)
	var controls := Label.new()
	controls.position = Vector2(24, 510)
	controls.text = "A/D or arrows: move    Space: double jump    X/J: attack    Esc: pause    R: restart"
	ui.add_child(controls)
	message = Label.new()
	message.position = Vector2(200, 200)
	message.size = Vector2(560, 130)
	message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message.add_theme_font_size_override("font_size", 28)
	ui.add_child(message)
	update_hud()

func update_hud() -> void:
	hud.text = "RESERKA  ·  Health %d  ·  Souls %d/5\nDefeat the skulls and reach the golden gate →" % [player.health, souls]

func collect_soul() -> void:
	souls += 1
	update_hud()

func end_game(won: bool) -> void:
	finished = true
	player.frozen = true
	message.text = ("CASTLE CLEARED\n" if won else "YOU FELL\n") + "Press R to play again"

func _process(_delta: float) -> void:
	if Input.is_action_just_pressed("restart"):
		get_tree().paused = false
		get_tree().reload_current_scene()
	if Input.is_action_just_pressed("pause") and not finished:
		get_tree().paused = not get_tree().paused
		message.text = "PAUSED\nEsc to continue" if get_tree().paused else ""
	if not finished and souls >= 5 and player.position.x > 2250:
		end_game(true)

func _draw() -> void:
	for x in range(0, 2400, 960):
		draw_texture_rect(background, Rect2(x, 0, 960, 540), false, Color(0.55, 0.5, 0.65))
	for platform in platforms:
		draw_rect(platform, Color(0.17, 0.13, 0.24))
		draw_rect(Rect2(platform.position, Vector2(platform.size.x, 5)), Color(0.52, 0.38, 0.57))
		for x in range(int(platform.position.x), int(platform.end.x), 40):
			draw_line(Vector2(x, platform.position.y + 5), Vector2(x, platform.end.y), Color(0.09, 0.07, 0.13))
	draw_rect(Rect2(2270, 360, 70, 120), Color(0.95, 0.72, 0.23, 0.7), false, 5)
