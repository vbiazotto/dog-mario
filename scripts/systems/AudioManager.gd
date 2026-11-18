extends Node
## Autoload: musica e efeitos sonoros (carrega WAVs de res://assets/audio/).

const MUSIC_DIR := "res://assets/audio/music/"
const SFX_DIR := "res://assets/audio/sfx/"

var music_player: AudioStreamPlayer
var sfx_players: Array[AudioStreamPlayer] = []
var current_music: String = ""
var _cache: Dictionary = {}


func _ready() -> void:
        process_mode = Node.PROCESS_MODE_ALWAYS
        music_player = AudioStreamPlayer.new()
        add_child(music_player)
        music_player.finished.connect(_on_music_finished)
        for i in 8:
                var p := AudioStreamPlayer.new()
                add_child(p)
                sfx_players.append(p)
        _apply_volumes()


func _get_stream(path: String) -> AudioStream:
        if _cache.has(path):
                return _cache[path]
        var s: AudioStream = null
        if ResourceLoader.exists(path):
                s = load(path)
        _cache[path] = s
        return s


func play_music(music_name: String) -> void:
        if current_music == music_name and music_player.playing:
                return
        current_music = music_name
        var s := _get_stream(MUSIC_DIR + music_name + ".wav")
        if s == null:
                return
        music_player.stream = s
        music_player.play()


func _on_music_finished() -> void:
        if current_music != "":
                music_player.play()


func stop_music() -> void:
        current_music = ""
        music_player.stop()


func play_sfx(sfx_name: String) -> void:
        var s := _get_stream(SFX_DIR + sfx_name + ".wav")
        if s == null:
                return
        for p in sfx_players:
                if not p.playing:
                        p.stream = s
                        p.play()
                        return
        sfx_players[0].stream = s
        sfx_players[0].play()


func _to_db(v: float, muted: bool) -> float:
        if muted or v <= 0.001:
                return -80.0
        return linear_to_db(v)


func _apply_volumes() -> void:
        music_player.volume_db = _to_db(SaveManager.music_volume, SaveManager.music_muted)
        for p in sfx_players:
                p.volume_db = _to_db(SaveManager.sfx_volume, SaveManager.sfx_muted)


func set_music_volume(v: float) -> void:
        SaveManager.music_volume = clampf(v, 0.0, 1.0)
        _apply_volumes()
        SaveManager.save_data()


func set_sfx_volume(v: float) -> void:
        SaveManager.sfx_volume = clampf(v, 0.0, 1.0)
        _apply_volumes()
        SaveManager.save_data()


func toggle_mute_music() -> void:
        SaveManager.music_muted = not SaveManager.music_muted
        _apply_volumes()
        SaveManager.save_data()


func toggle_mute_sfx() -> void:
        SaveManager.sfx_muted = not SaveManager.sfx_muted
        _apply_volumes()
        SaveManager.save_data()
