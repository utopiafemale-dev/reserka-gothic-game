extends Control

var session

var panel: VBoxContainer
var choice: OptionButton
var address: LineEdit
var port: SpinBox
var capacity: SpinBox
var loading: VBoxContainer
var progress_bar: ProgressBar
var load_status: Label
var starting := false
var scene_path := "res://three_d/main.tscn"
var preview: TextureRect
var web_origin := ""
var request: HTTPRequest
var requesting := false

func _ready() -> void:
 session = get_node_or_null("/root/Session")
 if session == null:
  session = preload("res://three_d/session.gd").new()
  session.name = "LocalSession"
  add_child(session)
 get_tree().paused = false
 if OS.has_feature("web"):
  web_origin = str(JavaScriptBridge.eval("window.location.origin"))
  request = HTTPRequest.new()
  request.timeout = 35
  add_child(request)
  request.request_completed.connect(room_response)
 var backdrop := TextureRect.new()
 backdrop.texture = load("res://assets/graveyard.png")
 backdrop.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
 backdrop.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
 backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_child(backdrop)
 var shade := ColorRect.new()
 shade.color = Color(0.01,0.005,0.03,0.7)
 shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_child(shade)
 var center := CenterContainer.new()
 center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_child(center)
 panel = VBoxContainer.new()
 panel.custom_minimum_size.x = 490
 panel.add_theme_constant_override("separation",9)
 center.add_child(panel)
 add_label(panel,"RESERKA",34)
 add_label(panel,"GOTHIC  ·  2.5D  ·  UP TO 8 PLAYERS",18)
 choice = OptionButton.new()
 for name in session.AVATAR_NAMES:
  choice.add_item(name)
 choice.selected = session.AVATARS.find(session.character)
 panel.add_child(choice)
 preview = TextureRect.new()
 preview.custom_minimum_size = Vector2(64,64)
 preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
 preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
 panel.add_child(preview)
 choice.item_selected.connect(update_preview)
 update_preview(choice.selected)
 add_label(panel,"Choose your character. All use the same movement and combat rules.",14)
 var settings := HBoxContainer.new()
 panel.add_child(settings)
 address = LineEdit.new()
 address.placeholder_text = "Host IP address / hostname"
 address.text = session.room_code if OS.has_feature("web") else session.address
 if OS.has_feature("web"):
  address.placeholder_text = "Room code (only needed to join)"
 address.size_flags_horizontal = Control.SIZE_EXPAND_FILL
 settings.add_child(address)
 port = SpinBox.new()
 port.min_value = 1024
 port.max_value = 65535
 port.value = session.port
 port.tooltip_text = "UDP port. Default: 24567"
 settings.add_child(port)
 port.visible = not OS.has_feature("web")
 var limit := HBoxContainer.new()
 panel.add_child(limit)
 add_label(limit,"Room player limit:",16)
 capacity = SpinBox.new()
 capacity.min_value = 2
 capacity.max_value = 8
 capacity.value = session.capacity
 limit.add_child(capacity)
 var buttons := HBoxContainer.new()
 panel.add_child(buttons)
 for item in [["Play solo","solo"],["Host co-op","host"],["Join co-op","join"]]:
  var button := Button.new()
  button.text = item[0]
  button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
  button.pressed.connect(start.bind(item[1]))
  buttons.add_child(button)
 add_label(panel,"Create a room and share its code with friends." if OS.has_feature("web") else "LAN: use host LAN IP. Internet: host must accept UDP on the chosen port.",14)
 var quit_button := Button.new()
 quit_button.text = "Quit game"
 quit_button.pressed.connect(get_tree().quit)
 panel.add_child(quit_button)
 quit_button.visible = not OS.has_feature("web")
 loading = VBoxContainer.new()
 loading.custom_minimum_size.x = 500
 center.add_child(loading)
 add_label(loading,"ENTERING RESERKA",30)
 load_status = add_label(loading,"Loading 3D scenery and characters…",18)
 progress_bar = ProgressBar.new()
 progress_bar.max_value = 100
 loading.add_child(progress_bar)
 loading.hide()

func update_preview(index: int) -> void:
 var sprites = preload("res://three_d/sprites.gd")
 var avatar = sprites.hero(session.AVATARS[index])
 preview.texture = avatar.sprite_frames.get_frame_texture("idle",0)
 preview.modulate = Color(0.45,0.9,1) if index == 2 else (Color(1,0.45,0.5) if index == 3 else Color.WHITE)
 avatar.free()

func add_label(parent: Node, text: String, size: int) -> Label:
 var label := Label.new()
 label.text = text
 label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
 label.add_theme_font_size_override("font_size",size)
 parent.add_child(label)
 return label

func start(mode: String) -> void:
 if starting or requesting:
  return
 if mode == "join" and address.text.strip_edges().is_empty():
  address.placeholder_text = "Enter the host's address first"
  return
 if OS.has_feature("web") and mode != "solo":
  requesting = true
  panel.hide()
  loading.show()
  load_status.text = "Connecting to room service…"
  var result: int
  if mode == "host":
   result = request.request(web_origin+"/api/rooms",["Content-Type: application/json"],HTTPClient.METHOD_POST,JSON.stringify({"capacity":int(capacity.value)}))
  else:
   result = request.request(web_origin+"/api/rooms/"+address.text.strip_edges().to_upper())
  if result != OK:
   room_error("Could not contact room service")
  return
 session.transport = "enet"
 session.dedicated = false
 session.character = session.AVATARS[choice.selected]
 session.mode = mode
 session.address = address.text.strip_edges()
 session.port = int(port.value)
 session.capacity = int(capacity.value)
 begin_loading()

func begin_loading() -> void:
 panel.hide()
 loading.show()
 var result := ResourceLoader.load_threaded_request(scene_path)
 if result != OK:
  load_status.text = "Could not load game (%d). Return to menu and retry." % result
  return
 starting = true

func _process(_delta: float) -> void:
 if not starting:
  return
 var progress: Array = []
 var status := ResourceLoader.load_threaded_get_status(scene_path,progress)
 if not progress.is_empty():
  progress_bar.value = float(progress[0])*100
 if status == ResourceLoader.THREAD_LOAD_LOADED:
  starting = false
  progress_bar.value = 100
  load_status.text = "Building stage…"
  var scene: PackedScene = ResourceLoader.load_threaded_get(scene_path)
  await get_tree().process_frame
  get_tree().change_scene_to_packed(scene)
 elif status == ResourceLoader.THREAD_LOAD_FAILED or status == ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
  starting = false
  load_status.text = "Game loading failed. Please restart and check imports."

func room_response(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
 requesting = false
 var data = JSON.parse_string(body.get_string_from_utf8())
 if result != HTTPRequest.RESULT_SUCCESS or code != 200 or not data is Dictionary or not data.has("socket"):
  room_error("Room unavailable. Check code and try again.")
  return
 session.transport = "websocket"
 session.dedicated = false
 session.mode = "join"
 session.character = session.AVATARS[choice.selected]
 session.room_code = data.code
 session.address = web_origin.replace("https://","wss://").replace("http://","ws://")+data.socket
 begin_loading()

func room_error(text: String) -> void:
 requesting = false
 loading.hide()
 panel.show()
 address.placeholder_text = text
 address.text = ""
