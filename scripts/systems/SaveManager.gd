extends Node
## Autoload: salva/carrega progresso com ConfigFile.

const SAVE_PATH := "user://dog_mario_save.cfg"

var levels_unlocked: Array = [1]
var best_scores: Dictionary = {}
var best_times: Dictionary = {}
var total_deaths: int = 0
var music_volume: float = 0.7
var sfx_volume: float = 0.8
var music_muted: bool = false
var sfx_muted: bool = false


func _ready() -> void:
        load_data()


func save_data() -> void:
        var cfg := ConfigFile.new()
        cfg.set_value("progress", "levels_unlocked", levels_unlocked)
        cfg.set_value("progress", "best_scores", best_scores)
        cfg.set_value("progress", "best_times", best_times)
        cfg.set_value("progress", "total_deaths", total_deaths)
        cfg.set_value("settings", "music_volume", music_volume)
        cfg.set_value("settings", "sfx_volume", sfx_volume)
        cfg.set_value("settings", "music_muted", music_muted)
        cfg.set_value("settings", "sfx_muted", sfx_muted)
        cfg.save(SAVE_PATH)


func load_data() -> void:
        var cfg := ConfigFile.new()
        if cfg.load(SAVE_PATH) != OK:
                return
        levels_unlocked = cfg.get_value("progress", "levels_unlocked", [1])
        best_scores = cfg.get_value("progress", "best_scores", {})
        best_times = cfg.get_value("progress", "best_times", {})
        total_deaths = cfg.get_value("progress", "total_deaths", 0)
        music_volume = cfg.get_value("settings", "music_volume", 0.7)
        sfx_volume = cfg.get_value("settings", "sfx_volume", 0.8)
        music_muted = cfg.get_value("settings", "music_muted", false)
        sfx_muted = cfg.get_value("settings", "sfx_muted", false)


func unlock_level(n: int) -> void:
        if n > 3:
                return
        if not levels_unlocked.has(n):
                levels_unlocked.append(n)
                save_data()


func is_level_unlocked(n: int) -> bool:
        return levels_unlocked.has(n)


func save_best_score(level: int, s: int) -> void:
        var k := str(level)
        if s > int(best_scores.get(k, 0)):
                best_scores[k] = s
        save_data()


func save_best_time(level: int, t: float) -> void:
        var k := str(level)
        if not best_times.has(k) or t < float(best_times[k]):
                best_times[k] = t
        save_data()


func get_best_score(level: int) -> int:
        return int(best_scores.get(str(level), 0))


func get_best_time(level: int) -> float:
        return float(best_times.get(str(level), -1.0))


func add_death() -> void:
        total_deaths += 1
