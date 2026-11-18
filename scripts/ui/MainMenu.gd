extends Control
## Menu principal com Doguinho animado correndo.

const UI := preload("res://scripts/ui/UIBuilder.gd")

@onready var dog: AnimatedSprite2D = $Dog


func _ready() -> void:
        get_tree().paused = false
        AudioManager.play_music("menu")
        var v := UI.centered_vbox(self, 12)
        var logo := TextureRect.new()
        logo.texture = load("res://assets/sprites/ui/logo.png")
        logo.custom_minimum_size = Vector2(640, 160)
        logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        v.add_child(logo)
        v.add_child(UI.label("A Aventura Impossivel", 30, Color(1, 0.9, 0.5)))
        var play := UI.button("Jogar", _on_play)
        v.add_child(play)
        v.add_child(UI.button("Selecionar Fase", _goto.bind("res://scenes/menus/LevelSelect.tscn")))
        v.add_child(UI.button("Como Jogar", _goto.bind("res://scenes/menus/HowToPlay.tscn")))
        v.add_child(UI.button("Configuracoes", _goto.bind("res://scenes/menus/Settings.tscn")))
        v.add_child(UI.button("Creditos", _goto.bind("res://scenes/menus/Credits.tscn")))
        v.add_child(UI.button("Sair", get_tree().quit))
        play.grab_focus()
        dog.play("run")


func _process(delta: float) -> void:
        dog.position.x += 220.0 * delta
        if dog.position.x > 1340.0:
                dog.position.x = -60.0


func _on_play() -> void:
        GameManager.start_new_game(1)


func _goto(path: String) -> void:
        get_tree().change_scene_to_file(path)
