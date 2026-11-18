extends Node2D
## Script raiz de cada fase: camera, musica, ligacao chefe -> saida.

@export var level_number: int = 1
@export var level_width: int = 3000
@export var music_name: String = "level1"
@export var death_y: float = 850.0


func _ready() -> void:
        GameManager.on_level_started(level_number)
        AudioManager.play_music(music_name)
        var player = get_node_or_null("Player")
        if player:
                player.death_y = death_y
                var cam := player.get_node_or_null("Camera2D") as Camera2D
                if cam:
                        cam.limit_left = 0
                        cam.limit_top = 0
                        cam.limit_right = level_width
                        cam.limit_bottom = 720
        var boss = get_node_or_null("Boss")
        var exit_area = get_node_or_null("LevelEnd")
        if boss and exit_area:
                exit_area.set_locked(true)
                boss.boss_defeated.connect(exit_area.unlock)
