extends SceneTree

var failures := 0

func check(condition: bool, label: String) -> void:
	if condition:
		print("PASS: " + label)
	else:
		push_error("FAIL: " + label)
		failures += 1

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var scene: PackedScene = load("res://main.tscn")
	var game = scene.instantiate()
	root.add_child(game)
	current_scene = game
	for i in 30:
		await physics_frame
	var player = game.player
	check(player.is_on_floor(), "player lands on platform collision")
	var start_x: float = player.position.x
	Input.action_press("move_right")
	for i in 12:
		await physics_frame
	Input.action_release("move_right")
	check(player.position.x > start_x + 20, "movement input advances player")
	Input.action_press("jump")
	await physics_frame
	await physics_frame
	Input.action_release("jump")
	check(player.velocity.y < 0 and player.jumps == 1, "first jump")
	await physics_frame
	player.jump()
	check(player.jumps == 2, "second jump")
	player.jump()
	check(player.jumps == 2, "third jump blocked")
	player.take_damage(10)
	player.take_damage(10)
	check(player.health == 90, "damage and temporary invulnerability")
	var enemy = get_first_node_in_group("enemies")
	enemy.position = player.position + Vector2(38, -28)
	player.facing = 1
	player.attack()
	await physics_frame
	await physics_frame
	check(enemy.health == 25, "sword hit deals damage once per swing")
	enemy.take_hit(25, 1)
	await process_frame
	check(game.souls == 1, "defeating enemy awards a soul")
	for other in get_nodes_in_group("enemies"):
		other.take_hit(50, 1)
	await process_frame
	player.position.x = 2300
	await process_frame
	await process_frame
	check(game.souls == 5 and game.finished and player.frozen, "gate completes level after five kills")
	check(player.sprite.sprite_frames.get_frame_count("run") == 12, "hero sprite frames imported")
	Input.action_press("restart")
	await process_frame
	await process_frame
	Input.action_release("restart")
	await process_frame
	game = current_scene
	player = game.player
	check(game.souls == 0 and player.health == 100 and not game.finished, "restart resets level")
	Input.action_press("pause")
	await process_frame
	await process_frame
	Input.action_release("pause")
	check(paused, "pause input pauses gameplay")
	await process_frame
	Input.action_press("pause")
	await process_frame
	await process_frame
	Input.action_release("pause")
	check(not paused, "pause input resumes gameplay")
	player.invincible_time = 0
	player.take_damage(100)
	check(game.finished and player.frozen and player.health == 0, "death ends level")
	print("Godot gameplay smoke checks complete: %d failures" % failures)
	quit(1 if failures else 0)
