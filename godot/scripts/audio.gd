extends Node

const EFFECTS := {
 "jump":preload("res://assets/audio/jump.wav"), "sword":preload("res://assets/audio/sword.wav"),
 "hurt":preload("res://assets/audio/hurt.wav"), "pickup":preload("res://assets/audio/pickup.wav"),
 "enemy_death":preload("res://assets/audio/enemy_death.wav"), "death":preload("res://assets/audio/death.wav"),
 "clear":preload("res://assets/audio/clear.wav")
}
const MUSIC := {
 "castle":preload("res://assets/audio/castle.wav"), "swamp":preload("res://assets/audio/swamp.wav"),
 "battle":preload("res://assets/audio/battle.wav")
}
var music: AudioStreamPlayer
var voices: Array[AudioStreamPlayer] = []
var voice_index := 0
var muted := false
var music_volume := -16.0

func _ready() -> void:
 music = AudioStreamPlayer.new()
 add_child(music)
 for i in 8:
  var voice := AudioStreamPlayer.new()
  voice.volume_db = -10
  add_child(voice)
  voices.append(voice)

func play_music(track: String) -> void:
 music.stop()
 var stream: AudioStreamWAV = MUSIC[track].duplicate()
 stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
 stream.loop_begin = 0
 stream.loop_end = stream.data.size() / 4
 music.stream = stream
 music.volume_db = music_volume
 music.play()

func play_effect(effect: String) -> void:
 if not EFFECTS.has(effect):
  return
 var voice := voices[voice_index]
 voice.stop()
 voice_index = (voice_index + 1) % voices.size()
 voice.stream = EFFECTS[effect]
 voice.pitch_scale = randf_range(0.95,1.05) if effect in ["jump","sword"] else 1.0
 voice.play()

func toggle_mute() -> void:
 muted = not muted
 AudioServer.set_bus_mute(0,muted)

func change_music_volume(amount: float) -> void:
 music_volume = clampf(music_volume + amount,-40,0)
 music.volume_db = music_volume

func stop_all() -> void:
 music.stop()
 music.stream = null
 for voice in voices:
  voice.stop()
  voice.stream = null

func _exit_tree() -> void:
 stop_all()
