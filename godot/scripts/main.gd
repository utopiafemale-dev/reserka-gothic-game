extends Node2D

const Player = preload("res://scripts/player.gd")
const Enemy = preload("res://scripts/enemy.gd")
const Levels = preload("res://scripts/levels.gd")
const Sound = preload("res://scripts/audio.gd")
var player
var souls := 0
var finished := false
var won_level := false
var level_index := 0
var enemy_count := 0
var world_width := 2400.0
var hud: Label
var message: Label
var sound
var world: Node2D
var platforms: Array = []
var hazards: Array = []
var heals: Array = []
var background: Texture2D
var scenery: Texture2D
var stage: Dictionary

func bind_action(action: String, keys: Array) -> void:
 if not InputMap.has_action(action):
  InputMap.add_action(action)
 for key in keys:
  var event := InputEventKey.new()
  event.physical_keycode = key
  if not InputMap.action_has_event(action,event):
   InputMap.action_add_event(action,event)

func _ready() -> void:
 process_mode = Node.PROCESS_MODE_ALWAYS
 bind_action("move_left",[KEY_A,KEY_LEFT])
 bind_action("move_right",[KEY_D,KEY_RIGHT])
 bind_action("jump",[KEY_SPACE,KEY_W,KEY_UP])
 bind_action("attack",[KEY_X,KEY_J])
 bind_action("restart",[KEY_R])
 bind_action("pause",[KEY_ESCAPE])
 bind_action("next_level",[KEY_ENTER])
 bind_action("mute",[KEY_M])
 bind_action("music_down",[KEY_BRACKETLEFT])
 bind_action("music_up",[KEY_BRACKETRIGHT])
 sound = Sound.new()
 add_child(sound)
 var ui := CanvasLayer.new()
 add_child(ui)
 hud = Label.new()
 hud.position = Vector2(24,12)
 hud.add_theme_font_size_override("font_size",20)
 ui.add_child(hud)
 var controls := Label.new()
 controls.position = Vector2(18,515)
 controls.add_theme_font_size_override("font_size",14)
 controls.text = "A/D: move   Space: double jump   X/J: sword   Esc: pause   R: retry   M: mute   [ / ]: music volume"
 ui.add_child(controls)
 message = Label.new()
 message.position = Vector2(170,190)
 message.size = Vector2(620,160)
 message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
 message.add_theme_font_size_override("font_size",26)
 ui.add_child(message)
 load_level(0)

func load_level(index: int) -> void:
 get_tree().paused = false
 if is_instance_valid(world):
  world.free()
 level_index = index
 stage = Levels.STAGES[index]
 world_width = stage.width
 platforms = stage.platforms.duplicate()
 hazards = stage.hazards.duplicate()
 heals = stage.heals.duplicate()
 background = load("res://assets/%s.png" % stage.background)
 scenery = null
 if index == 1:
  scenery = load("res://assets/swamp_trees.png")
 elif index == 2:
  scenery = load("res://assets/cavern_walls.png")
 souls = 0
 finished = false
 won_level = false
 message.text = ""
 world = Node2D.new()
 world.process_mode = Node.PROCESS_MODE_PAUSABLE
 add_child(world)
 for platform in platforms:
  var body := StaticBody2D.new()
  body.position = platform.position + platform.size / 2
  var shape := CollisionShape2D.new()
  var rectangle := RectangleShape2D.new()
  rectangle.size = platform.size
  shape.shape = rectangle
  shape.one_way_collision = platform.size.y < 30
  body.add_child(shape)
  world.add_child(body)
 player = Player.new()
 player.world_width = world_width
 player.position = Vector2(100,470)
 world.add_child(player)
 player.health_changed.connect(update_hud.unbind(1))
 player.died.connect(end_game.bind(false))
 player.sound_requested.connect(sound.play_effect)
 var camera := Camera2D.new()
 camera.position.y = -210
 camera.limit_left = 0
 camera.limit_right = int(world_width)
 camera.limit_top = 0
 camera.limit_bottom = 540
 player.add_child(camera)
 enemy_count = stage.enemies.size()
 for spec in stage.enemies:
  var enemy := Enemy.new()
  enemy.kind = spec[0]
  enemy.position = spec[1]
  enemy.world_width = world_width
  enemy.defeated.connect(collect_soul)
  enemy.sound_requested.connect(sound.play_effect)
  world.add_child(enemy)
 sound.play_music(stage.music)
 update_hud()
 queue_redraw()

func update_hud() -> void:
 if not is_instance_valid(player):
  return
 hud.text = "%d/4  %s  ·  Health %d  ·  Souls %d/%d\n%s  ·  Sound %s" % [level_index+1,stage.name,player.health,souls,enemy_count,
  "Gate unlocked →" if souls >= enemy_count else "Defeat every enemy to unlock the gate →","OFF" if sound.muted else "ON"]

func collect_soul() -> void:
 souls += 1
 sound.play_effect("enemy_death")
 update_hud()
 queue_redraw()

func end_game(won: bool) -> void:
 if finished:
  return
 finished = true
 won_level = won
 player.frozen = true
 sound.play_effect("clear" if won else "death")
 if not won:
  message.text = "YOU FELL\nR to retry this stage"
 elif level_index < Levels.STAGES.size()-1:
  message.text = "STAGE CLEARED\nEnter: next stage\nR: replay this stage"
 else:
  message.text = "THE WARDEN HAS FALLEN\nAll four stages cleared!\nR: start a new journey"

func _process(_delta: float) -> void:
 if Input.is_action_just_pressed("restart"):
  var index: int = 0 if won_level and level_index == Levels.STAGES.size()-1 else level_index
  load_level(index)
  return
 if Input.is_action_just_pressed("next_level") and won_level and level_index < Levels.STAGES.size()-1:
  load_level(level_index+1)
  return
 if Input.is_action_just_pressed("mute"):
  sound.toggle_mute()
  update_hud()
 if Input.is_action_just_pressed("music_down"):
  sound.change_music_volume(-3)
 if Input.is_action_just_pressed("music_up"):
  sound.change_music_volume(3)
 if Input.is_action_just_pressed("pause") and not finished:
  get_tree().paused = not get_tree().paused
  message.text = "PAUSED\nEsc: continue\nM: mute   [ / ]: music volume" if get_tree().paused else ""
 if not finished and not get_tree().paused:
  if souls >= enemy_count and player.position.x > world_width-150:
   end_game(true)

func _physics_process(_delta: float) -> void:
 if finished or get_tree().paused:
  return
 var body := Rect2(player.position-Vector2(13,48),Vector2(26,48))
 for hazard in hazards:
  if body.intersects(hazard):
   player.take_damage(15)
 for i in range(heals.size()-1,-1,-1):
  if body.intersects(Rect2(heals[i]-Vector2(13,13),Vector2(26,26))) and player.health < 100:
   player.heal(30)
   heals.remove_at(i)
   sound.play_effect("pickup")
   queue_redraw()

func _draw() -> void:
 if background == null:
  return
 draw_tiled_layer(background,stage.tint)
 if scenery != null:
  draw_tiled_layer(scenery,stage.tint)
 for platform in platforms:
  draw_rect(platform,stage.stone)
  draw_rect(Rect2(platform.position,Vector2(platform.size.x,5)),stage.stone.lightened(0.35))
  for x in range(int(platform.position.x),int(platform.end.x),40):
   draw_line(Vector2(x,platform.position.y+5),Vector2(x,platform.end.y),stage.stone.darkened(0.5))
 for hazard in hazards:
  for x in range(int(hazard.position.x),int(hazard.end.x),14):
   draw_colored_polygon(PackedVector2Array([Vector2(x,hazard.end.y),Vector2(x+7,hazard.position.y),Vector2(x+14,hazard.end.y)]),Color(0.8,0.35,0.4))
 for pickup in heals:
  draw_circle(pickup,12,Color(0.2,0.75,0.5))
  draw_rect(Rect2(pickup-Vector2(7,2),Vector2(14,4)),Color.WHITE)
  draw_rect(Rect2(pickup-Vector2(2,7),Vector2(4,14)),Color.WHITE)
 var gate_color := Color(0.95,0.72,0.23) if souls >= enemy_count else Color(0.45,0.35,0.4)
 draw_rect(Rect2(world_width-130,360,70,120),gate_color,false,5)

func draw_tiled_layer(texture: Texture2D, tint: Color) -> void:
 var tile_width := int(ceil(texture.get_width()*540.0/texture.get_height()))
 for x in range(0,int(world_width),tile_width):
  draw_texture_rect(texture,Rect2(x,0,tile_width,540),false,tint)
