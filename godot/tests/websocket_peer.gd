extends SceneTree
var game
func _initialize() -> void:
 call_deferred("run")
func wait_until(condition: Callable) -> bool:
 var deadline := Time.get_ticks_msec()+15000
 while Time.get_ticks_msec() < deadline:
  if condition.call():
   return true
  await process_frame
 return false
func run() -> void:
 var args := OS.get_cmdline_user_args()
 var session = root.get_node("Session")
 session.mode = "join"
 session.transport = "websocket"
 session.address = args[0]
 session.character = session.AVATARS[int(args[1])%4]
 game = load("res://three_d/main.tscn").instantiate()
 root.add_child(game)
 current_scene = game
 var admitted := await wait_until(func(): return game.players.size() == 8 and not game.players.has(1))
 if not admitted:
  push_error("Eight real WebSocket players not synchronized")
  quit(1)
  return
 var actor = game.local_player()
 if actor.character != session.character:
  push_error("Independent character selection lost")
  quit(1)
  return
 var x: float = actor.position.x
 Input.action_press("move_right")
 await create_timer(0.7).timeout
 Input.action_release("move_right")
 if game.local_player().position.x <= x+0.4:
  push_error("Authoritative remote movement failed")
  quit(1)
  return
 print("PASS: eight WebSocket players, own character, authoritative movement")
 await create_timer(3).timeout
 game.multiplayer.multiplayer_peer.close()
 quit(0)
