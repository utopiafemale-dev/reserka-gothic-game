extends SceneTree

func _initialize() -> void:
 call_deferred("start")

func start() -> void:
 var session = root.get_node_or_null("Session")
 if session == null:
  session = load("res://three_d/session.gd").new()
  session.name = "Session"
  root.add_child(session)
 session.mode = "host"
 session.transport = "websocket"
 session.dedicated = true
 var args := OS.get_cmdline_user_args()
 session.port = int(args[0])
 session.capacity = int(args[1])
 var game = load("res://three_d/main.tscn").instantiate()
 game.decorative_props = false
 game.fog_enabled = false
 root.add_child(game)
 current_scene = game
 if game.network.connected:
  print("RESERKA_ROOM_READY")
 else:
  quit(1)
