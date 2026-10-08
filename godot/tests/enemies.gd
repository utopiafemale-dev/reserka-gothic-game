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

func run() -> void:
 var game = load("res://main.tscn").instantiate()
 root.add_child(game)
 current_scene = game
 for enemy in get_nodes_in_group("enemies"):
  enemy.free()
 var player = game.player
 player.position = Vector2(400,480)
 player.invincible_time = 999
 var hound = game.Enemy.new()
 hound.kind = "hound"
 hound.position = Vector2(200,480)
 hound.cooldown = 0
 game.world.add_child(hound)
 await physics_frame
 await physics_frame
 check(hound.charge_time > 0 and absf(hound.velocity.x) == 250, "hound charges faster than normal pursuit")
 hound.free()
 var demon = game.Enemy.new()
 demon.kind = "demon"
 demon.position = Vector2(200,480)
 demon.cooldown = 0
 game.world.add_child(demon)
 player.position = Vector2(275,480)
 player.invincible_time = 0
 for i in 3:
  await physics_frame
 check(demon.windup > 0 and player.health == 100, "demon telegraphs before striking")
 for i in 50:
  await physics_frame
 check(player.health == 80, "demon strike deals damage after windup")
 demon.free()
 var boss = game.Enemy.new()
 boss.kind = "warden"
 boss.position = Vector2(200,480)
 game.world.add_child(boss)
 player.position = Vector2(370,480)
 player.invincible_time = 999
 await physics_frame
 await physics_frame
 check(absf(boss.velocity.x) == 85, "warden first phase pursuit")
 boss.take_hit(125,1)
 boss.position = Vector2(200,480)
 await physics_frame
 await physics_frame
 check(absf(boss.velocity.x) == 115, "warden accelerates below half health")
 boss.position = Vector2(200,480)
 boss.cooldown = 0
 player.position = Vector2(300,480)
 player.invincible_time = 0
 for i in 3:
  await physics_frame
 check(boss.windup > 0, "warden telegraphs area strike")
 var before: int = player.health
 for i in 50:
  await physics_frame
 check(player.health == before-25, "warden area strike deals boss damage")
 game.sound.stop_all()
 await create_timer(0.2).timeout
 print("Enemy checks complete: %d failures" % failures)
 quit(1 if failures else 0)
