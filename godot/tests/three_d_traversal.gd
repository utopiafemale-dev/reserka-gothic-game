extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var game = load("res://three_d/main.tscn").instantiate()
 root.add_child(game)
 current_scene = game
 for level in 4:
  game.load_level(level)
  for enemy in get_nodes_in_group("enemies3d"):
   enemy.take_hit(enemy.health,0)
  game.player.invincible_time = 9999
  Input.action_press("move_right")
  for frame in 1200:
   await physics_frame
   if game.player.is_on_floor():
    game.player.jump()
   elif game.player.velocity.y < 0 and game.player.jumps == 1 and game.player.position.y < 1.5:
    game.player.jump()
   if game.finished:
    break
  Input.action_release("move_right")
  if not game.won_level:
   push_error("3D traversal failed on stage %d at %s" % [level+1,game.player.position])
   game.sound.stop_all()
   await create_timer(0.2).timeout
   quit(1)
   return
  print("PASS: 3D movement and physics reach stage %d gate" % (level+1))
 game.sound.stop_all()
 await create_timer(0.2).timeout
 quit(0)
