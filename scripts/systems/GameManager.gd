extends Node
## Autoload: estado global do jogo (vidas, pontos, fases, checkpoints).

signal level_complete(level: int)
signal game_over
signal lives_changed(lives: int)
signal score_changed(score: int)
signal deaths_changed(deaths: int)

const MAX_LIVES := 3
const MENU_SCENE := "res://scenes/menus/Menu.tscn"
const LEVELS := [
        "res://scenes/levels/Level1.tscn",
        "res://scenes/levels/Level2.tscn",
        "res://scenes/levels/Level3.tscn",
]
const LEVEL_NAMES := ["Campo da Falsa Tranquilidade", "Floresta das Armadilhas", "Castelo do Cachorro Maldito"]

var lives: int = MAX_LIVES
var score: int = 0
var deaths: int = 0
var current_level: int = 1
var checkpoint_position: Vector2 = Vector2.ZERO
var has_checkpoint: bool = false
var level_time: float = 0.0
var level_start_score: int = 0
var timer_running: bool = false
var last_level_time: float = 0.0
var _fresh_level: bool = true


func _process(delta: float) -> void:
        if timer_running and not get_tree().paused:
                level_time += delta


func start_new_game(level: int = 1) -> void:
        lives = MAX_LIVES
        score = 0
        deaths = 0
        load_level(level)


func load_level(level: int) -> void:
        current_level = clampi(level, 1, LEVELS.size())
        clear_checkpoint()
        _fresh_level = true
        get_tree().paused = false
        get_tree().change_scene_to_file(LEVELS[current_level - 1])


func on_level_started(level: int) -> void:
        if level != current_level:
                current_level = level
                clear_checkpoint()
                _fresh_level = true
        if _fresh_level:
                level_time = 0.0
                level_start_score = score
                _fresh_level = false
        timer_running = true
        lives_changed.emit(lives)
        score_changed.emit(score)
        deaths_changed.emit(deaths)


func add_score(pts: int) -> void:
        score += pts
        score_changed.emit(score)


## Dano sem morte: retorna true se o jogador ainda tem vidas.
func hurt() -> bool:
        lives = max(lives - 1, 0)
        lives_changed.emit(lives)
        return lives > 0


## Chamado pelo Player depois da animacao de morte.
func player_died(life_already_lost: bool = false) -> void:
        deaths += 1
        SaveManager.add_death()
        deaths_changed.emit(deaths)
        if not life_already_lost:
                lose_life()
                return
        if lives <= 0:
                trigger_game_over()
        else:
                reset_level()


func lose_life() -> void:
        lives = max(lives - 1, 0)
        lives_changed.emit(lives)
        if lives <= 0:
                trigger_game_over()
        else:
                reset_level()


func trigger_game_over() -> void:
        timer_running = false
        game_over.emit()
        save_game()
        get_tree().paused = false
        get_tree().call_deferred("change_scene_to_file", "res://scenes/menus/GameOver.tscn")


func retry_level() -> void:
        lives = MAX_LIVES
        score = level_start_score
        load_level(current_level)


func reset_level() -> void:
        get_tree().paused = false
        get_tree().call_deferred("reload_current_scene")


func complete_level() -> void:
        if not timer_running:
                return
        timer_running = false
        last_level_time = level_time
        SaveManager.save_best_score(current_level, score)
        SaveManager.save_best_time(current_level, level_time)
        SaveManager.unlock_level(current_level + 1)
        clear_checkpoint()
        AudioManager.play_music("victory")
        level_complete.emit(current_level)
        await get_tree().create_timer(1.5).timeout
        get_tree().change_scene_to_file("res://scenes/menus/Victory.tscn")


func next_level() -> void:
        if current_level < LEVELS.size():
                load_level(current_level + 1)
        else:
                go_to_menu()


func go_to_menu() -> void:
        timer_running = false
        get_tree().paused = false
        get_tree().change_scene_to_file(MENU_SCENE)


func save_game() -> void:
        SaveManager.save_data()


func load_game() -> void:
        SaveManager.load_data()


func set_checkpoint(pos: Vector2) -> void:
        checkpoint_position = pos
        has_checkpoint = true


func clear_checkpoint() -> void:
        has_checkpoint = false
        checkpoint_position = Vector2.ZERO


func respawn_player(player: Node2D) -> void:
        if has_checkpoint and player:
                player.global_position = checkpoint_position


static func format_time(t: float) -> String:
        var total := int(t)
        return "%02d:%02d" % [total / 60, total % 60]
