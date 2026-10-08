extends Node

const AVATARS := ["knight","adventurer","spectral","crimson"]
const AVATAR_NAMES := ["Gothic Knight","Adventurer","Spectral Knight (palette)","Crimson Knight (palette)"]
var mode := "solo"
var character := "knight"
var address := "127.0.0.1"
var port := 24567
var capacity := 8
var transport := "enet"
var dedicated := false
var room_code := ""

func reset_network() -> void:
 mode = "solo"
