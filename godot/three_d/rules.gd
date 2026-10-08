extends Resource
class_name ReserkaRules

@export_group("Player movement — world units are metres")
@export_range(0.5, 12.0, 0.1) var move_speed := 2.7
@export_range(1.0, 60.0, 0.5) var acceleration := 24.0
@export_range(1.0, 30.0, 0.1) var gravity := 13.0
@export_range(1.0, 15.0, 0.1) var jump_speed := 4.9
@export_range(1, 4, 1) var max_jumps := 2
@export_range(0.0, 0.4, 0.01) var coyote_seconds := 0.12
@export_range(0.0, 0.4, 0.01) var jump_buffer_seconds := 0.12
@export_group("Combat")
@export_range(1, 500, 1) var max_health := 100
@export_range(1, 100, 1) var sword_damage := 25
@export_range(0.1, 1.0, 0.01) var attack_seconds := 0.34
@export_range(0.2, 2.0, 0.05) var invulnerability_seconds := 1.0
@export_range(1, 100, 1) var healing_amount := 30
@export_range(1, 100, 1) var spike_damage := 15
@export_group("Enemies")
@export_range(0.1, 3.0, 0.1) var enemy_speed_multiplier := 1.0
@export_range(1, 500, 1) var skull_health := 50
@export_range(1, 500, 1) var hound_health := 50
@export_range(1, 500, 1) var demon_health := 100
@export_range(1, 1000, 1) var boss_health := 250
@export_group("Presentation")
@export_range(4.0, 10.0, 0.1) var camera_size := 5.8
@export_range(1.0, 15.0, 0.5) var camera_follow_speed := 5.0
@export var screen_shake := true
