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

func press(action: String) -> void:
	Input.action_press(action)
	await process_frame
	await process_frame
	Input.action_release(action)
	await process_frame

func run() -> void:
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	current_scene = game
	await process_frame
	for effect in game.sound.EFFECTS:
		var stream: AudioStream = game.sound.EFFECTS[effect]
		check(stream.get_length() > 0, "decoded audio effect: " + effect)
		game.sound.play_effect(effect)
	check(game.sound.voices[6].playing, "sound effect starts playback")
	await press("mute")
	check(AudioServer.is_bus_mute(0) and game.sound.muted, "mute key silences audio bus")
	await press("mute")
	check(not AudioServer.is_bus_mute(0), "mute key restores audio")
	await press("music_down")
	check(game.sound.music.volume_db == -19, "music volume control")
	await press("music_up")
	check(game.sound.music.volume_db == -16, "music volume restored")
	for level in 4:
		check(game.level_index == level, "stage %d loaded through campaign" % (level + 1))
		check(game.background != null and game.world_width == game.stage.width, "stage background and width")
		check(game.sound.music.playing and game.sound.music.stream.loop_mode == AudioStreamWAV.LOOP_FORWARD, "stage music starts and loops")
		check(game.sound.music.stream.get_length() > 0, "stage music decodes")
		for i in 25:
			await physics_frame
		check(game.player.is_on_floor(), "stage spawn lands safely")
		game.player.position.x = game.world_width - 100
		await process_frame
		await process_frame
		check(not game.finished, "gate remains locked before combat")
		game.player.health = 50
		var heal: Vector2 = game.heals[0]
		game.player.position = heal + Vector2(0, 20)
		var heal_count: int = game.heals.size()
		await physics_frame
		await physics_frame
		check(game.player.health == 80 and game.heals.size() == heal_count - 1, "healing pickup restores health once")
		if not game.hazards.is_empty():
			game.player.invincible_time = 0
			var hazard: Rect2 = game.hazards[0]
			game.player.position = Vector2(hazard.get_center().x, 480)
			await physics_frame
			await physics_frame
			check(game.player.health == 65, "spikes apply damage")
		# Kill via combat damage API to verify counting, gate, and level transitions.
		for enemy in get_nodes_in_group("enemies"):
			if enemy.kind == "warden":
				check(enemy.max_health == 250, "final warden has boss health")
				enemy.take_hit(125, 1)
				check(enemy.health == 125, "warden enters second phase threshold")
			enemy.take_hit(enemy.health, 1)
		await process_frame
		check(game.souls == game.enemy_count and get_nodes_in_group("enemies").is_empty(), "all enemy defeats award souls")
		game.player.position = Vector2(game.world_width - 100, 470)
		await process_frame
		await process_frame
		check(game.finished and game.won_level, "stage gate completes level")
		if level < 3:
			await press("next_level")
			check(game.player.health == 100 and game.souls == 0 and not game.finished, "next stage resets health and souls")
	check(game.message.text.contains("All four stages cleared"), "campaign victory message")
	await press("restart")
	check(game.level_index == 0 and not game.finished, "victory restart begins new campaign")
	game.load_level(2)
	game.player.take_damage(100)
	await press("restart")
	check(game.level_index == 2 and game.player.health == 100, "death retries current stage")
	print("Campaign and audio checks complete: %d failures" % failures)
	game.sound.stop_all()
	await create_timer(0.2).timeout
	quit(1 if failures else 0)
