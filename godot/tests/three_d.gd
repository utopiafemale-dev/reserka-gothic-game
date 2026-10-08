extends SceneTree

var failures := 0

func _initialize() -> void:
 call_deferred("run")

func check(condition: bool, label: String) -> void:
 if condition:
  print("PASS: "+label)
 else:
  push_error("FAIL: "+label)
  failures += 1

func press(action: String) -> void:
 Input.action_press(action)
 await process_frame
 await process_frame
 Input.action_release(action)
 await process_frame

func run() -> void:
 var game = load("res://three_d/main.tscn").instantiate()
 root.add_child(game)
 current_scene = game
 for i in 30:
  await physics_frame
 var player = game.player
 check(player is CharacterBody3D and player.is_on_floor(),"3D player lands on 3D floor")
 check(player.sprite is AnimatedSprite3D,"sprite character lives in 3D world")
 check(get_nodes_in_group("scenery3d").size() > 30,"real GLB scenery models instantiated")
 check(game.camera.projection == Camera3D.PROJECTION_ORTHOGONAL,"side-scrolling orthographic camera")
 var x: float = player.position.x
 Input.action_press("move_right")
 for i in 15:
  await physics_frame
 Input.action_release("move_right")
 check(player.position.x > x+0.3 and player.position.z == 0,"movement stays on gameplay plane")
 await press("jump")
 check(player.velocity.y > 0 and player.jumps == 1,"3D first jump")
 player.jump()
 check(player.jumps == 2,"3D double jump")
 check(not player.jump(),"extra jump blocked")
 player.take_damage(10)
 player.take_damage(10)
 check(player.health == 90,"3D damage and invulnerability")
 var enemy = get_first_node_in_group("enemies3d")
 enemy.position = player.position+Vector3(0.38,0,0)
 player.facing = 1
 player.attack()
 await physics_frame
 await physics_frame
 check(enemy.health == 25,"3D sword deals one hit per swing")
 var test_rules: Resource = game.rules.duplicate()
 test_rules.sword_damage = 40
 player.rules = test_rules
 player.attack_time = 0
 player.attack()
 await physics_frame
 await physics_frame
 check(game.souls == 1,"edited damage rule applies without changing code")
 await press("pause")
 check(paused,"3D pause")
 await press("pause")
 check(not paused,"3D resume")
 await press("mute")
 check(game.sound.muted,"3D audio mute")
 await press("mute")
 for level in 4:
  game.load_level(level)
  for i in 25:
   await physics_frame
  player = game.player
  check(player.is_on_floor(),"stage %d 3D spawn safe" % (level+1))
  check(game.sound.music.playing,"stage %d soundtrack playing" % (level+1))
  player.position.x = game.world_width-1.0
  await process_frame
  await process_frame
  check(not game.finished,"stage %d gate locked" % (level+1))
  player.health = 50
  var heal: Vector3 = game.heals[0].point
  player.position = heal-Vector3(0,0.2,0)
  await physics_frame
  await physics_frame
  check(player.health == 80,"stage %d 3D crystal heals" % (level+1))
  if not game.stage.hazards.is_empty():
   var rect: Rect2 = game.stage.hazards[0]
   player.position = Vector3(rect.get_center().x/100,0,0)
   player.invincible_time = 0
   await physics_frame
   await physics_frame
   check(player.health == 65,"stage %d 3D spikes hurt" % (level+1))
  for other in get_nodes_in_group("enemies3d"):
   other.take_hit(other.health,0)
  await process_frame
  player.position = Vector3(game.world_width-1.0,0.05,0)
  await process_frame
  await process_frame
  check(game.won_level and game.souls == game.enemy_count,"stage %d gate clears" % (level+1))
  if level < 3:
   await press("next_level")
   check(game.level_index == level+1 and game.player.health == game.rules.max_health,"Enter advances 3D stage")
 await press("restart")
 check(game.level_index == 0 and not game.finished,"3D campaign restart")
 game.load_level(2)
 game.player.take_damage(100)
 await press("restart")
 check(game.level_index == 2 and game.player.health == 100,"3D death retries current stage")
 game.sound.stop_all()
 await create_timer(0.2).timeout
 print("3D gameplay checks complete: %d failures" % failures)
 quit(1 if failures else 0)
