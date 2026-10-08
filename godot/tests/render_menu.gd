extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var menu = load("res://three_d/boot.tscn").instantiate()
 root.add_child(menu)
 current_scene = menu
 for i in 10:
  await process_frame
 await RenderingServer.frame_post_draw
 var image := root.get_texture().get_image()
 image.save_png("/tmp/reserka-startup-menu.png")
 quit(0)
