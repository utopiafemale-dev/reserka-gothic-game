extends SceneTree

var role := "host"
var output := ""
var port := 24673
var avatar := "knight"
var game
var failures := 0
var checks: Array = []

func _initialize() -> void:
 call_deferred("run")

func check(condition: bool, label: String) -> void:
 checks.append({"label":label,"passed":condition})
 if condition:
  print("PASS: "+label)
 else:
  push_error("FAIL: "+label)
  failures += 1

func until(condition: Callable, seconds := 8.0) -> bool:
 var start := Time.get_ticks_msec()
 while Time.get_ticks_msec()-start < seconds*1000:
  if condition.call():
   return true
  await process_frame
 return false

func run() -> void:
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--role="):
   role = argument.substr(7)
  elif argument.begins_with("--out="):
   output = argument.substr(6)
  elif argument.begins_with("--port="):
   port = int(argument.substr(7))
  elif argument.begins_with("--avatar="):
   avatar = argument.substr(9)
 var session = root.get_node_or_null("Session")
 if session == null:
  session = load("res://three_d/session.gd").new()
  session.name = "Session"
  root.add_child(session)
 session.mode = "host" if role == "host" else "join"
 session.port = port
 session.capacity = 8
 session.address = "127.0.0.1"
 session.character = avatar
 game = load("res://three_d/main.tscn").instantiate()
 root.add_child(game)
 current_scene = game
 if role == "host":
  await host_checks()
 elif role == "overflow":
  await create_timer(3).timeout
  check(not game.network.connected,"ninth participant not admitted to full eight-player server")
 else:
  await client_checks()
 Input.action_release("move_right")
 game.sound.stop_all()
 if game.multiplayer.multiplayer_peer:
  game.multiplayer.multiplayer_peer.close()
 await create_timer(0.2).timeout
 if not output.is_empty():
  var file := FileAccess.open(output,FileAccess.WRITE)
  file.store_string(JSON.stringify({"role":role,"failures":failures,"checks":checks}))
 quit(1 if failures else 0)

func host_checks() -> void:
 check(game.network.connected,"host opens ENet UDP server")
 for enemy in get_nodes_in_group("enemies3d"):
  enemy.set_physics_process(false)
 var ready: bool = await until(func(): return game.players.size() == 8,12)
 check(ready,"seven different client processes join host (eight players total)")
 if not ready:
  return
 var starts := {}
 var kinds := {}
 for id in game.players:
  starts[id] = game.players[id].position.x
  kinds[game.players[id].character] = true
  game.players[id].invincible_time = 999
 check(kinds.size() == 4,"independent character choices reach authoritative host")
 var payload := var_to_bytes(game.snapshot()).compress(FileAccess.COMPRESSION_DEFLATE)
 check(payload.size() < 1200,"eight-player snapshot fits below UDP MTU after compression")
 var remote_id: int = game.players.keys()[1]
 var target = get_first_node_in_group("enemies3d")
 target.position = game.players[remote_id].position+Vector3(0.5,0,0)
 var original_health: int = target.health
 await create_timer(2.0).timeout
 var moved := 0
 for id in game.players:
  if id != 1 and game.players[id].position.x > float(starts[id])+0.2:
   moved += 1
 check(moved == 7,"host simulates movement received from every client")
 check(not is_instance_valid(target) or target.health < original_health,"remote sword input affects host enemy health")
 var actor = game.players[remote_id]
 actor.invincible_time = 0
 actor.take_damage(17)
 await create_timer(0.5).timeout
 check(actor.health == 83,"host applies authoritative remote-player damage")
 for enemy in get_nodes_in_group("enemies3d"):
  enemy.take_hit(enemy.health,0)
 game.player.position = Vector3(game.world_width-1,0.05,0)
 await process_frame
 await process_frame
 check(game.won_level,"host controls campaign gate completion")
 game.load_level(1)
 for enemy in get_nodes_in_group("enemies3d"):
  enemy.set_physics_process(false)
 for player in game.players.values():
  player.invincible_time = 999
 check(game.players.size() == 8,"stage transition preserves all connected players")
 await create_timer(5).timeout
 # A downed player revives beside a surviving partner rather than ending co-op.
 actor = game.players[remote_id]
 actor.invincible_time = 0
 actor.take_damage(100)
 check(not game.finished and actor.frozen,"one downed player does not end shared campaign")
 game.downed[remote_id] = 0.05
 await create_timer(0.2).timeout
 check(actor.health == 50 and not actor.frozen,"downed player revives near a surviving teammate")
 await create_timer(2).timeout

func client_checks() -> void:
 var ready: bool = await until(func(): return game.network.connected and game.players.has(game.network.local_id()) and game.players.size() == 8,12)
 check(ready,"client receives all eight replicated players")
 if not ready:
  return
 var id: int = game.network.local_id()
 var actor = game.players[id]
 check(actor.character == avatar and not actor.simulation_enabled,"selected local avatar is host simulated")
 check(game.local_player() == actor,"device camera follows its own player")
 var initial: float = actor.position.x
 Input.action_press("move_right")
 for i in 8:
  Input.action_press("attack")
  await create_timer(0.08).timeout
  Input.action_release("attack")
  await create_timer(0.17).timeout
 Input.action_release("move_right")
 check(actor.position.x > initial+0.2,"client receives authoritative movement snapshots")
 var changed: bool = await until(func(): return game.level_index == 1,8)
 check(changed,"client follows host stage transition")
 check(game.players.size() == 8 and game.players[id].character == avatar,"stage replication preserves eight character selections")
 var start := Time.get_ticks_msec()
 while game.network.connected and Time.get_ticks_msec()-start < 12_000:
  await process_frame
 check(game.network.disconnected,"host disconnect is reported on client")
 check(game.message.text.contains("HOST DISCONNECTED"),"disconnect leaves a clear return-to-menu message")
