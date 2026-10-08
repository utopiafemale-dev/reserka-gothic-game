extends Node3D

var session

const Player = preload("res://three_d/player.gd")
const Enemy = preload("res://three_d/enemy.gd")
const Levels = preload("res://scripts/levels.gd")
const Sound = preload("res://scripts/audio.gd")
const Network = preload("res://three_d/network.gd")
const MODELS := {
 "arch":preload("res://assets/models/arch.glb"),"pillar":preload("res://assets/models/pillar.glb"),
 "tombstone":preload("res://assets/models/tombstone.glb"),"dead_tree":preload("res://assets/models/dead_tree.glb"),
 "crystal":preload("res://assets/models/crystal.glb"),"torch":preload("res://assets/models/torch.glb"),
 "coffin":preload("res://assets/models/coffin.glb"),"stone_block":preload("res://assets/models/stone_block.glb")
}
@export var rules: Resource = preload("res://three_d/gameplay.tres")
@export_range(0,3,1) var starting_stage := 0
@export var fog_enabled := true
@export var decorative_props := true
var player
var sound
var world: Node3D
var camera: Camera3D
var hud: Label
var message: Label
var stage: Dictionary
var level_index := 0
var souls := 0
var enemy_count := 0
var finished := false
var won_level := false
var world_width := 24.0
var raised_platforms: Array = []
var heals: Array = []
var torches: Array = []
var shake := 0.0
var elapsed := 0.0
var gate: Node3D
var model_materials: Dictionary = {}
var network
var players: Dictionary = {}
var downed: Dictionary = {}
var remote_enemies: Dictionary = {}
var remote_paused := false

func bind_action(action: String, keys: Array) -> void:
 if not InputMap.has_action(action):
  InputMap.add_action(action)
 for key in keys:
  var event := InputEventKey.new()
  event.physical_keycode = key
  if not InputMap.action_has_event(action,event):
   InputMap.action_add_event(action,event)

func _ready() -> void:
 session = get_node_or_null("/root/Session")
 if session == null:
  session = preload("res://three_d/session.gd").new()
  session.name = "LocalSession"
  add_child(session)
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
 network = Network.new()
 network.name = "Network"
 network.game = self
 network.session = session
 add_child(network)
 create_lighting()
 var ui := CanvasLayer.new()
 add_child(ui)
 var header := ColorRect.new()
 header.color = Color(0.015,0.01,0.035,0.7)
 header.size = Vector2(960,78)
 header.mouse_filter = Control.MOUSE_FILTER_IGNORE
 ui.add_child(header)
 var footer := ColorRect.new()
 footer.color = header.color
 footer.position.y = 505
 footer.size = Vector2(960,35)
 footer.mouse_filter = Control.MOUSE_FILTER_IGNORE
 ui.add_child(footer)
 hud = Label.new()
 hud.position = Vector2(22,14)
 hud.add_theme_font_size_override("font_size",18)
 ui.add_child(hud)
 var controls := Label.new()
 controls.position = Vector2(18,515)
 controls.add_theme_font_size_override("font_size",14)
 controls.text = "A/D: move   Space: double jump   X/J: sword   Esc: pause   R: retry   M: mute   [ / ]: music volume"
 ui.add_child(controls)
 message = Label.new()
 message.position = Vector2(160,190)
 message.size = Vector2(640,160)
 message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
 message.add_theme_font_size_override("font_size",26)
 ui.add_child(message)
 load_level(starting_stage)
 network.start_session()

func create_lighting() -> void:
 var environment := WorldEnvironment.new()
 var env := Environment.new()
 env.background_mode = Environment.BG_COLOR
 env.background_color = Color(0.025,0.02,0.065)
 env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
 env.ambient_light_color = Color(0.5,0.55,0.8)
 env.ambient_light_energy = 0.3
 env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
 env.fog_enabled = fog_enabled
 env.fog_light_color = Color(0.07,0.05,0.14)
 env.fog_density = 0.007
 environment.environment = env
 add_child(environment)
 var moon := DirectionalLight3D.new()
 moon.rotation_degrees = Vector3(-35,-25,0)
 moon.light_color = Color(0.58,0.68,1)
 moon.light_energy = 0.7
 moon.shadow_enabled = true
 add_child(moon)
 var fill := DirectionalLight3D.new()
 fill.rotation_degrees = Vector3(-20,150,0)
 fill.light_color = Color(0.4,0.28,0.55)
 fill.light_energy = 0.2
 add_child(fill)

func world_point(point: Vector2) -> Vector3:
 return Vector3(point.x/100,(480-point.y)/100,0)

func model(name: String, point: Vector3, scale_value := Vector3.ONE) -> Node3D:
 var packed: PackedScene = MODELS[name]
 var instance: Node3D = packed.instantiate()
 instance.position = point
 instance.scale = scale_value
 instance.add_to_group("scenery3d")
 weather_materials(instance)
 world.add_child(instance)
 return instance

func weather_materials(node: Node) -> void:
 if node is MeshInstance3D:
  for surface in node.mesh.get_surface_count():
   var original = node.mesh.surface_get_material(surface)
   if original is StandardMaterial3D:
    var name: String = original.resource_name
    if not model_materials.has(name):
     var mat: StandardMaterial3D = original.duplicate()
     if "stone" in name:
      mat.albedo_color = Color(0.22,0.2,0.27) if "charcoal" in name else Color(0.32,0.3,0.36)
      var noise := FastNoiseLite.new()
      noise.seed = 821
      noise.frequency = 0.08
      var texture := NoiseTexture2D.new()
      texture.width = 128
      texture.height = 128
      texture.noise = noise
      texture.seamless = true
      var gradient := Gradient.new()
      gradient.colors = PackedColorArray([Color(0.35,0.35,0.35),Color(0.85,0.85,0.85)])
      texture.color_ramp = gradient
      mat.albedo_texture = texture
      mat.roughness = 0.95
     elif "wood" in name:
      mat.albedo_color = Color(0.16,0.11,0.13)
     model_materials[name] = mat
    node.set_surface_override_material(surface,model_materials[name])
 for child in node.get_children():
  weather_materials(child)

func load_level(index: int) -> void:
 get_tree().paused = false
 if is_instance_valid(world):
  world.free()
 raised_platforms.clear()
 heals.clear()
 torches.clear()
 players.clear()
 downed.clear()
 remote_enemies.clear()
 level_index = index
 stage = Levels.STAGES[index]
 world_width = stage.width/100.0
 souls = 0
 finished = false
 won_level = false
 message.text = ""
 world = Node3D.new()
 world.process_mode = Node.PROCESS_MODE_PAUSABLE
 add_child(world)
 for rect in stage.platforms:
  create_platform(rect)
 player = null
 if not session.dedicated:
  add_coop_player(1,"knight" if network.is_client() else session.character,1)
  player = players[1]
 if network.role == "host":
  for id in network.avatars:
   if int(id) != 1:
    add_coop_player(int(id),network.avatars[id])
 camera = Camera3D.new()
 camera.projection = Camera3D.PROJECTION_ORTHOGONAL
 camera.size = rules.camera_size
 camera.position = Vector3(6.2,4.0,12)
 camera.rotation = Vector3(-0.2,0.12,0)
 camera.current = true
 world.add_child(camera)
 enemy_count = stage.enemies.size()
 for spec in stage.enemies:
  var enemy := Enemy.new()
  enemy.kind = spec[0]
  enemy.rules = rules
  enemy.world_width = world_width
  enemy.enemy_id = remote_enemies.size()
  enemy.simulation_enabled = not network.is_client()
  enemy.position = world_point(spec[1])
  enemy.defeated.connect(collect_soul)
  enemy.sound_requested.connect(sound.play_effect)
  world.add_child(enemy)
  remote_enemies[enemy.enemy_id] = enemy
 for point in stage.heals:
  var pos := world_point(point)
  var item := model("crystal",pos-Vector3(0,0.25,0),Vector3.ONE*0.65)
  heals.append({"point":pos,"model":item,"id":heals.size()})
 for rect in stage.hazards:
  create_spikes(rect)
 gate = model("arch",Vector3(world_width-1.0,0,-0.3),Vector3.ONE*0.7)
 var gate_light := OmniLight3D.new()
 gate_light.position = Vector3(world_width-1.0,1,0.2)
 gate_light.light_color = Color(0.8,0.5,0.15)
 gate_light.light_energy = 0.8
 gate_light.omni_range = 2
 world.add_child(gate_light)
 if decorative_props:
  decorate()
 sound.play_music(stage.music)
 world.visible = not network.is_client()
 update_hud()

func add_coop_player(id: int, avatar: String, requested_slot := 0) -> void:
 if players.has(id):
  return
 var slot := requested_slot
 if slot == 0:
  for candidate in range(1,9):
   var used := false
   for actor in players.values():
    if actor.slot == candidate:
     used = true
   if not used:
    slot = candidate
    break
 var actor := Player.new()
 actor.rules = rules
 actor.network = network
 actor.controller_id = id
 actor.character = avatar
 actor.slot = slot
 actor.world_width = world_width
 actor.simulation_enabled = not network.is_client()
 actor.position = Vector3(1+float(slot-1)*0.32,0.1,0)
 actor.visual_target = actor.position
 actor.frozen = finished
 players[id] = actor
 world.add_child(actor)
 actor.health_changed.connect(update_hud.unbind(1))
 actor.died.connect(on_player_died.bind(id))
 actor.sound_requested.connect(on_player_sound.bind(id))
 actor.hurt.connect(kick_camera)
 if id == 1 or not is_instance_valid(player):
  player = actor
 if is_instance_valid(hud):
  update_hud()

func remove_coop_player(id: int) -> void:
 if not players.has(id):
  return
 var actor = players[id]
 actor.remove_from_group("player3d")
 actor.queue_free()
 players.erase(id)
 if player == actor:
  player = players.values()[0] if not players.is_empty() else null
 downed.erase(id)
 update_hud()
 var alive := false
 for remaining in players.values():
  if remaining.health > 0:
   alive = true
 if not alive and not finished and not players.is_empty():
  end_game(false)

func local_player():
 return players.get(network.local_id(),players.values()[0] if not players.is_empty() else null)

func on_player_sound(effect: String, id: int) -> void:
 sound.play_effect(effect)
 if network.role == "host" and network.connected:
  network.play_remote_sound.rpc(effect,id)

func on_player_died(id: int) -> void:
 players[id].frozen = true
 players[id].velocity = Vector3.ZERO
 players[id].sprite.play("idle")
 players[id].sprite.modulate = Color(0.3,0.3,0.4)
 players[id].display_tag.text = "P%d DOWN" % players[id].slot
 downed[id] = 6.0
 var alive := false
 for actor in players.values():
  if actor.health > 0:
   alive = true
 if not alive:
  end_game(false)
 else:
  on_player_sound("death",id)
  update_hud()

func create_platform(rect: Rect2) -> void:
 var width := rect.size.x/100
 var height := rect.size.y/100
 var top := (480-rect.position.y)/100
 var left := rect.position.x/100
 var body := StaticBody3D.new()
 body.position = Vector3(left+width/2,top-height/2,0)
 var box := BoxShape3D.new()
 box.size = Vector3(width,height,1.8)
 var collision := CollisionShape3D.new()
 collision.shape = box
 body.add_child(collision)
 world.add_child(body)
 if rect.size.y < 30:
  raised_platforms.append({"body":body,"top":top})
 var chunks := int(ceil(width/2))
 var chunk_width := width/chunks
 for i in chunks:
  model("stone_block",Vector3(left+chunk_width*(i+0.5),top-height,0),Vector3(chunk_width/2,height/0.48,1))

func create_spikes(rect: Rect2) -> void:
 var metal := StandardMaterial3D.new()
 metal.albedo_color = Color(0.28,0.22,0.29)
 metal.metallic = 0.7
 metal.roughness = 0.4
 for x in range(int(rect.position.x),int(rect.end.x),14):
  var spike := MeshInstance3D.new()
  var cone := CylinderMesh.new()
  cone.top_radius = 0
  cone.bottom_radius = 0.08
  cone.height = 0.22
  cone.radial_segments = 5
  spike.mesh = cone
  spike.material_override = metal
  spike.position = Vector3((x+7)/100.0,0.11,0)
  world.add_child(spike)

func decorate() -> void:
 # Existing illustrations are distant backdrops; these foreground props are actual meshes.
 var mesh := MeshInstance3D.new()
 var quad := QuadMesh.new()
 quad.size = Vector2(world_width+12,12)
 mesh.mesh = quad
 mesh.position = Vector3(world_width/2,3,-10)
 var mat := StandardMaterial3D.new()
 mat.albedo_texture = load("res://assets/%s.png" % stage.background)
 mat.albedo_color = Color(0.48,0.45,0.62)
 mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
 mesh.material_override = mat
 world.add_child(mesh)
 for x in range(1,int(world_width),3):
  if level_index in [1,3]:
   model("dead_tree",Vector3(x,0,-2.5),Vector3.ONE*(1.0+float(x%3)*0.15))
  elif level_index == 2:
   model("stone_block",Vector3(x,0,-3),Vector3(1.2,5+float(x%3),1.7))
   model("crystal",Vector3(x+0.4,0.2,-1.4),Vector3.ONE*1.1)
  else:
   model("pillar",Vector3(x,0,-2.4),Vector3.ONE*1.3)
   model("arch",Vector3(x+1.5,0,-4),Vector3.ONE*1.4)
  if level_index == 3:
   model("tombstone",Vector3(x+0.8,0,-1.5),Vector3.ONE*0.8)
   if x%2 == 0:
    model("coffin",Vector3(x,0,-2.0),Vector3.ONE*0.8)
 for x in range(2,int(world_width),4):
  var torch := model("torch",Vector3(x,0,-0.9),Vector3.ONE*0.7)
  var light := OmniLight3D.new()
  light.position = Vector3(x,1.15,-0.7)
  light.light_color = Color(1,0.35,0.09)
  light.light_energy = 0.8
  light.omni_range = 2.8
  world.add_child(light)
  torches.append({"light":light,"model":torch})

func update_hud() -> void:
 var health_text := "Waiting for players"
 if is_instance_valid(player):
  health_text = "Health %d" % player.health
 if players.size() > 1:
  var parts := PackedStringArray()
  for actor in players.values():
   parts.append("P%d:%d" % [actor.slot,actor.health])
  health_text = "  ".join(parts)
 hud.text = "2.5D  ·  %d/4  %s  ·  Souls %d/%d\n%s\n%s  ·  Sound %s" % [level_index+1,stage.name,souls,enemy_count,health_text,
  "Gate unlocked >" if souls >= enemy_count else "Defeat every enemy to unlock the gate >","OFF" if sound.muted else "ON"]

func collect_soul() -> void:
 souls += 1
 on_player_sound("enemy_death",1)
 update_hud()

func kick_camera() -> void:
 if rules.screen_shake:
  shake = 0.15

func end_game(won: bool) -> void:
 if finished:
  return
 finished = true
 won_level = won
 for actor in players.values():
  actor.frozen = true
 on_player_sound("clear" if won else "death",1)
 if not won:
  message.text = "YOU FELL\nR: retry this stage"
 elif level_index < 3:
  message.text = "STAGE CLEARED\nEnter: next stage   R: replay"
 else:
  message.text = "THE WARDEN HAS FALLEN\nAll four stages cleared!\nR: start a new journey"

func _process(delta: float) -> void:
 if Input.is_action_just_pressed("restart") and not network.is_client():
  load_level(0 if won_level and level_index == 3 else level_index)
  return
 if Input.is_action_just_pressed("next_level") and won_level and level_index < 3 and not network.is_client():
  load_level(level_index+1)
  return
 if Input.is_action_just_pressed("mute"):
  sound.toggle_mute()
  update_hud()
 if Input.is_action_just_pressed("music_down"):
  sound.change_music_volume(-3)
 if Input.is_action_just_pressed("music_up"):
  sound.change_music_volume(3)
 if Input.is_action_just_pressed("pause") and not finished and not network.is_client():
  get_tree().paused = not get_tree().paused
  message.text = "PAUSED\nEsc: continue" if get_tree().paused else ""
 if get_tree().paused:
  return
 elapsed += delta
 for item in torches:
  item.light.light_energy = 0.75+sin(elapsed*9+item.light.position.x)*0.1
 for item in heals:
  item.model.rotation.y += delta
 var half_width: float = rules.camera_size*get_viewport().get_visible_rect().size.x/get_viewport().get_visible_rect().size.y/2
 var focus = local_player()
 if focus == null:
  return
 var target_x := clampf(focus.position.x+0.6,half_width,world_width-half_width)+1.4
 var amount := 1-exp(-rules.camera_follow_speed*delta)
 camera.position.x = lerpf(camera.position.x,target_x,amount)
 shake = maxf(0,shake-delta)
 camera.h_offset = sin(elapsed*90)*shake*0.3
 camera.v_offset = cos(elapsed*75)*shake*0.2
 if not finished and not network.is_client() and souls >= enemy_count:
  for actor in players.values():
   if actor.health > 0 and actor.position.x > world_width-1.5:
    end_game(true)
    break

func _physics_process(_delta: float) -> void:
 if not is_instance_valid(player) or get_tree().paused or network.is_client():
  return
 # Only the hero ignores a ledge while ascending/below it; enemies keep collision.
 for platform in raised_platforms:
  for actor in players.values():
   if actor.position.y >= platform.top-0.04 and actor.velocity.y <= 0:
    actor.remove_collision_exception_with(platform.body)
   else:
    actor.add_collision_exception_with(platform.body)
 if finished:
  return
 for actor in players.values():
  var body: Rect2 = actor.body_rect()
  for rect in stage.hazards:
   var area := Rect2(rect.position.x/100,0,rect.size.x/100,rect.size.y/100)
   if body.intersects(area):
    actor.take_damage(rules.spike_damage)
  for i in range(heals.size()-1,-1,-1):
   var point: Vector3 = heals[i].point
   if body.intersects(Rect2(Vector2(point.x-0.13,point.y-0.13),Vector2(0.26,0.26))) and actor.health > 0 and actor.health < rules.max_health:
    actor.heal(rules.healing_amount)
    heals[i].model.queue_free()
    heals.remove_at(i)
    on_player_sound("pickup",actor.controller_id)
 for id in downed.keys():
  downed[id] -= _delta
  if downed[id] <= 0 and not finished:
   for partner in players.values():
    if partner.health > 0:
     var actor = players[id]
     actor.position = partner.position+Vector3(0.25,0.15,0)
     actor.health = maxi(1,rules.max_health/2)
     actor.invincible_time = 2
     actor.frozen = false
     actor.display_tag.text = "P%d" % actor.slot
     downed.erase(id)
     on_player_sound("pickup",id)
     update_hud()
     break

func snapshot() -> Dictionary:
 var actors: Array = []
 for id in players:
  var actor = players[id]
  actors.append({"id":id,"slot":actor.slot,"avatar":actor.character,"position":actor.position,"velocity":actor.velocity,
   "health":actor.health,"frozen":actor.frozen,"facing":actor.facing,"jumps":actor.jumps,"attack":actor.attack_time,
   "animation":actor.sprite.animation,"invincible":actor.invincible_time})
 var enemies: Array = []
 for enemy in get_tree().get_nodes_in_group("enemies3d"):
  enemies.append({"id":enemy.enemy_id,"position":enemy.position,"health":enemy.health,
   "windup":enemy.windup,"facing":enemy.sprite.flip_h,"hurt":enemy.hurt_time})
 var items: Array = []
 for item in heals:
  items.append(item.id)
 return {"level":level_index,"players":actors,"enemies":enemies,"heals":items,"souls":souls,
  "leader":network.leader_id,"finished":finished,"won":won_level,"message":message.text,"paused":get_tree().paused}

func apply_snapshot(state: Dictionary) -> void:
 if level_index != state.level:
  load_level(state.level)
 world.visible = true
 var ids: Array = []
 for actor_state in state.players:
  var id: int = actor_state.id
  ids.append(id)
  if players.has(id) and players[id].character != actor_state.avatar:
   players[id].free()
   players.erase(id)
  if not players.has(id):
   add_coop_player(id,actor_state.avatar,actor_state.slot)
  players[id].apply_state(actor_state)
 for id in players.keys():
  if not id in ids:
   remove_coop_player(id)
 if players.has(network.local_id()):
  player = players[network.local_id()]
 var live: Array = []
 for enemy_state in state.enemies:
  live.append(enemy_state.id)
  if remote_enemies.has(enemy_state.id) and is_instance_valid(remote_enemies[enemy_state.id]):
   remote_enemies[enemy_state.id].apply_state(enemy_state)
 for id in remote_enemies.keys():
  if not id in live:
   if is_instance_valid(remote_enemies[id]):
    remote_enemies[id].queue_free()
   remote_enemies.erase(id)
 for i in range(heals.size()-1,-1,-1):
  if not heals[i].id in state.heals:
   heals[i].model.queue_free()
   heals.remove_at(i)
 souls = state.souls
 finished = state.finished
 won_level = state.won
 message.text = state.message
 get_tree().paused = state.paused
 update_hud()
