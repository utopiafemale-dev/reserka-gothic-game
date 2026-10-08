extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var game = load("res://three_d/main.tscn").instantiate()
 root.add_child(game)
 current_scene = game
 for level in 4:
  game.load_level(level)
  game.player.frozen = true
  for i in 20:
   await process_frame
  await RenderingServer.frame_post_draw
  var image := root.get_texture().get_image()
  if image.is_empty():
   push_error("Renderer produced an empty image")
   quit(1)
   return
  var result := image.save_png("/tmp/reserka-3d-stage%d.png" % (level+1))
  if result != OK:
   quit(1)
   return
  print("PASS: rendered 3D stage %d to PNG" % (level+1))
 game.sound.stop_all()
 await create_timer(0.2).timeout
 quit(0)
