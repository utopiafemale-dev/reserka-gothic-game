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
 var session = root.get_node_or_null("Session")
 if session == null:
  session = load("res://three_d/session.gd").new()
  session.name = "Session"
  root.add_child(session)
 var menu = load("res://three_d/boot.tscn").instantiate()
 root.add_child(menu)
 current_scene = menu
 await process_frame
 check(menu.choice.item_count == 4,"startup offers four independently selectable appearances")
 check(menu.capacity.max_value == 8 and menu.capacity.value == 8,"menu supports eight-player host capacity")
 check(menu.port.value == 24567,"menu shows configurable UDP port")
 for index in 4:
  menu.choice.selected = index
  menu.update_preview(index)
  check(menu.preview.texture != null,"character preview %d loads" % index)
 menu.address.text = ""
 menu.start("join")
 check(not menu.starting,"empty host address prevents accidental connection")
 menu.choice.selected = 1
 menu.start("solo")
 check(menu.loading.visible and not menu.panel.visible,"loading screen shown before game scene")
 var start := Time.get_ticks_msec()
 while current_scene.name != "Reserka25D" and Time.get_ticks_msec()-start < 8000:
  await process_frame
 check(current_scene.name == "Reserka25D","threaded loading enters 2.5D game")
 if current_scene.name == "Reserka25D":
  check(current_scene.player.character == "adventurer","menu character choice persists into gameplay")
  current_scene.sound.stop_all()
 await create_timer(0.2).timeout
 print("Menu and loading checks complete: %d failures" % failures)
 quit(1 if failures else 0)
