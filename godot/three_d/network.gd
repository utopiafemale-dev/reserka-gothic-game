extends Node

var session

const SNAPSHOT_INTERVAL := 0.05
var game
var role := "solo"
var connected := false
var disconnected := false
var timer := 0.0
var inputs: Dictionary = {}
var avatars: Dictionary = {}
var last_sequence := 0
var sequence := 0
var status: Label
var menu_button: Button
var joining_time := 0.0
var leader_id := 1
var pending_snapshots: Dictionary = {}

func _ready() -> void:
 process_mode = Node.PROCESS_MODE_ALWAYS
 role = session.mode
 multiplayer.connected_to_server.connect(on_connected)
 multiplayer.connection_failed.connect(on_failed)
 multiplayer.server_disconnected.connect(on_server_left)
 multiplayer.peer_disconnected.connect(on_peer_left)
 var ui := CanvasLayer.new()
 ui.layer = 10
 add_child(ui)
 status = Label.new()
 status.position = Vector2(20,484)
 status.add_theme_font_size_override("font_size",14)
 ui.add_child(status)
 menu_button = Button.new()
 menu_button.text = "Menu"
 menu_button.position = Vector2(874,14)
 menu_button.size = Vector2(70,36)
 menu_button.pressed.connect(return_to_menu)
 ui.add_child(menu_button)

func start_session() -> void:
 if role == "solo":
  status.text = "Solo adventure  ·  Menu: character selection / online co-op"
 elif role == "host":
  var peer: MultiplayerPeer
  var result: int
  if session.transport == "websocket":
   peer = WebSocketMultiplayerPeer.new()
   result = peer.create_server(session.port,"127.0.0.1")
  else:
   peer = ENetMultiplayerPeer.new()
   result = peer.create_server(session.port,session.capacity-1)
  if result != OK:
   status.text = "Host failed: port unavailable (%d). Return to Menu to choose another port." % result
   role = "solo"
   session.mode = "solo"
   return
  multiplayer.multiplayer_peer = peer
  connected = true
  if not session.dedicated:
   avatars[1] = session.character
  update_status()
 else:
  var peer: MultiplayerPeer
  var result: int
  if session.transport == "websocket":
   peer = WebSocketMultiplayerPeer.new()
   result = peer.create_client(session.address)
  else:
   peer = ENetMultiplayerPeer.new()
   result = peer.create_client(session.address,session.port)
  if result != OK:
   on_failed()
   return
  multiplayer.multiplayer_peer = peer
  status.text = "Connecting to %s:%d…" % [session.address,session.port]
  game.message.text = "CONNECTING TO HOST…\nMenu to cancel"

func is_client() -> bool:
 return role == "join"

func local_id() -> int:
 return multiplayer.get_unique_id() if connected else 1

func is_remote_controller(id: int) -> bool:
 return role == "host" and id != 1

func consume_input(id: int) -> Dictionary:
 if not inputs.has(id):
  return {"axis":0.0,"jump":false,"attack":false}
 var state: Dictionary = inputs[id]
 var result := state.duplicate()
 if Time.get_ticks_msec()-int(state.get("seen",0)) > 500:
  result.axis = 0.0
 state.jump = false
 state.attack = false
 return result

@rpc("any_peer","call_remote","unreliable",1)
func submit_axis(axis: float) -> void:
 if role != "host" or not is_finite(axis):
  return
 var id := multiplayer.get_remote_sender_id()
 if not game.players.has(id):
  return
 if not inputs.has(id):
  inputs[id] = {"axis":0.0,"jump":false,"attack":false}
 inputs[id].axis = clampf(axis,-1,1)
 inputs[id].seen = Time.get_ticks_msec()

@rpc("any_peer","call_remote","reliable",2)
func submit_action(action: String) -> void:
 if role != "host" or get_tree().paused:
  return
 var id := multiplayer.get_remote_sender_id()
 if not game.players.has(id) or action not in ["jump","attack"]:
  return
 if not inputs.has(id):
  inputs[id] = {"axis":0.0,"jump":false,"attack":false}
 inputs[id][action] = true
 inputs[id].seen = Time.get_ticks_msec()

@rpc("any_peer","call_remote","reliable",0)
func request_character(avatar: String) -> void:
 if role != "host":
  return
 var id := multiplayer.get_remote_sender_id()
 if game.players.size() >= session.capacity:
  multiplayer.multiplayer_peer.disconnect_peer(id)
  return
 if id == 1 or game.players.has(id):
  return
 if session.dedicated and game.players.is_empty():
  leader_id = id
 if avatar not in session.AVATARS:
  avatar = "knight"
 avatars[id] = avatar
 game.add_coop_player(id,avatar)
 update_status()

func on_connected() -> void:
 connected = true
 disconnected = false
 status.text = "Connected to host. Synchronizing campaign…"
 request_character.rpc_id(1,session.character)

func on_failed() -> void:
 connected = false
 disconnected = true
 status.text = "Connection failed. Check room code / server availability." if session.transport == "websocket" else "Connection failed. Check address, UDP port, firewall and host availability."
 game.message.text = "COULD NOT CONNECT\nReturn to Menu to retry"

func on_server_left() -> void:
 connected = false
 disconnected = true
 status.text = "Host disconnected. Return to Menu to reconnect or play solo."
 game.message.text = "HOST DISCONNECTED\nMenu to return"

func on_peer_left(id: int) -> void:
 if role == "host":
  avatars.erase(id)
  pending_snapshots.erase(id)
  inputs.erase(id)
  game.remove_coop_player(id)
  if leader_id == id:
   leader_id = int(game.players.keys()[0]) if not game.players.is_empty() else 1
  update_status()

func update_status() -> void:
 if role == "host":
  status.text = "Hosting UDP %d  ·  Players %d/%d  ·  Share your reachable IP with friends" % [session.port,game.players.size(),session.capacity]
 elif connected:
  status.text = "Room %s  ·  %d/8 players  ·  %s" % [session.room_code,game.players.size(),"You control pause / retry / next stage" if local_id() == leader_id else "Room leader controls stage transitions"] if session.transport == "websocket" else "Online co-op  ·  %d players  ·  Host controls pause and stage transitions" % game.players.size()

func return_to_menu() -> void:
 if multiplayer.multiplayer_peer:
  multiplayer.multiplayer_peer.close()
 multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()
 session.mode = "solo"
 get_tree().paused = false
 get_tree().change_scene_to_file("res://three_d/boot.tscn")

func _process(delta: float) -> void:
 if role == "join" and not disconnected:
  if not connected:
   joining_time += delta
   if joining_time > 12:
    multiplayer.multiplayer_peer.close()
    on_failed()
   return
  if session.transport == "websocket":
   for action in ["restart","pause","next_level"]:
    if Input.is_action_just_pressed(action):
     request_control.rpc_id(1,action)
  if Input.is_action_just_pressed("jump"):
   submit_action.rpc_id(1,"jump")
  if Input.is_action_just_pressed("attack"):
   submit_action.rpc_id(1,"attack")
 timer += delta
 if timer < SNAPSHOT_INTERVAL or not connected:
  return
 timer = 0
 if role == "join":
  submit_axis.rpc_id(1,Input.get_axis("move_left","move_right"))
 elif role == "host":
  sequence += 1
  var payload := var_to_bytes(game.snapshot()).compress(FileAccess.COMPRESSION_DEFLATE)
  if session.transport == "websocket":
   for id in avatars:
    var socket = multiplayer.multiplayer_peer.get_peer(id)
    if socket != null and socket.get_ready_state() == WebSocketPeer.STATE_OPEN and not pending_snapshots.has(id):
     pending_snapshots[id] = sequence
     receive_snapshot.rpc_id(id,sequence,payload)
  else:
   receive_snapshot.rpc(sequence,payload)

@rpc("authority","call_remote","unreliable_ordered",1)
func receive_snapshot(number: int, payload: PackedByteArray) -> void:
 if role != "join" or number <= last_sequence:
  return
 var data := payload.decompress_dynamic(65536,FileAccess.COMPRESSION_DEFLATE)
 if data.is_empty():
  return
 var state = bytes_to_var(data)
 if not state is Dictionary:
  return
 last_sequence = number
 leader_id = int(state.get("leader",1))
 game.apply_snapshot(state)
 if session.transport == "websocket":
  acknowledge_snapshot.rpc_id(1,number)
 update_status()

@rpc("authority","call_remote","reliable",2)
func play_remote_sound(effect: String, _actor_id: int) -> void:
 if role == "join" and game.sound.EFFECTS.has(effect):
  game.sound.play_effect(effect)

@rpc("any_peer","call_remote","reliable",0)
func request_control(action: String) -> void:
 if role != "host" or multiplayer.get_remote_sender_id() != leader_id:
  return
 if action == "restart":
  game.load_level(0 if game.won_level and game.level_index == 3 else game.level_index)
 elif action == "next_level" and game.won_level and game.level_index < 3:
  game.load_level(game.level_index+1)
 elif action == "pause" and not game.finished:
  get_tree().paused = not get_tree().paused
  game.message.text = "PAUSED\nRoom leader: Esc to continue" if get_tree().paused else ""

@rpc("any_peer","call_remote","reliable",0)
func acknowledge_snapshot(number: int) -> void:
 var id := multiplayer.get_remote_sender_id()
 if role == "host" and pending_snapshots.get(id,-1) == number:
  pending_snapshots.erase(id)
