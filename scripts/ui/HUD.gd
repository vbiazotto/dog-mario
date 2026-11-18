extends CanvasLayer
## HUD: vidas, pontos, fase, tempo, mortes e botao de pausa.

const UI := preload("res://scripts/ui/UIBuilder.gd")

var hearts: Array[TextureRect] = []
var score_label: Label
var level_label: Label
var time_label: Label
var deaths_label: Label
var heart_tex: Texture2D
var heart_empty_tex: Texture2D


func _ready() -> void:
        heart_tex = load("res://assets/sprites/ui/heart.png")
        heart_empty_tex = load("res://assets/sprites/ui/heart_empty.png")
        var bar := HBoxContainer.new()
        bar.position = Vector2(16, 12)
        bar.add_theme_constant_override("separation", 28)
        add_child(bar)
        var hbox := HBoxContainer.new()
        bar.add_child(hbox)
        for i in GameManager.MAX_LIVES:
                var tr := TextureRect.new()
                tr.texture = heart_tex
                tr.custom_minimum_size = Vector2(36, 36)
                tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
                tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
                hbox.add_child(tr)
                hearts.append(tr)
        score_label = UI.label("", 26)
        level_label = UI.label("", 26, Color(1, 0.9, 0.4))
        time_label = UI.label("", 26)
        deaths_label = UI.label("", 26, Color(1, 0.6, 0.6))
        for l in [score_label, level_label, time_label, deaths_label]:
                bar.add_child(l)
        var pause_btn := Button.new()
        pause_btn.text = " II "
        pause_btn.add_theme_font_size_override("font_size", 26)
        pause_btn.position = Vector2(1200, 10)
        pause_btn.focus_mode = Control.FOCUS_NONE
        pause_btn.pressed.connect(_on_pause_pressed)
        add_child(pause_btn)
        GameManager.lives_changed.connect(_on_lives_changed)
        GameManager.score_changed.connect(_on_score_changed)
        GameManager.deaths_changed.connect(_on_deaths_changed)
        _on_lives_changed(GameManager.lives)
        _on_score_changed(GameManager.score)
        _on_deaths_changed(GameManager.deaths)
        level_label.text = "FASE %d" % GameManager.current_level


func _process(_delta: float) -> void:
        time_label.text = "TEMPO " + GameManager.format_time(GameManager.level_time)
        level_label.text = "FASE %d" % GameManager.current_level


func _on_lives_changed(lives: int) -> void:
        for i in hearts.size():
                hearts[i].texture = heart_tex if i < lives else heart_empty_tex


func _on_score_changed(score: int) -> void:
        score_label.text = "PONTOS %06d" % score


func _on_deaths_changed(deaths: int) -> void:
        deaths_label.text = "MORTES %d" % deaths


func _on_pause_pressed() -> void:
        var pm = get_tree().get_first_node_in_group("pause_menu")
        if pm:
                pm.toggle()
