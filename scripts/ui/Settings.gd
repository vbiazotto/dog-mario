extends Control
## Configuracoes: volume de musica/sfx e mudo.

const UI := preload("res://scripts/ui/UIBuilder.gd")


func _ready() -> void:
        var v := UI.centered_vbox(self, 14)
        v.add_child(UI.label("CONFIGURACOES", 56, Color(1, 0.85, 0.3)))
        v.add_child(UI.label("Volume da Musica", 26))
        v.add_child(_slider(SaveManager.music_volume, AudioManager.set_music_volume))
        v.add_child(UI.label("Volume dos Efeitos", 26))
        v.add_child(_slider(SaveManager.sfx_volume, _on_sfx_changed))
        v.add_child(_toggle("Musica muda", SaveManager.music_muted, AudioManager.toggle_mute_music))
        v.add_child(_toggle("Efeitos mudos", SaveManager.sfx_muted, AudioManager.toggle_mute_sfx))
        v.add_child(UI.button("Voltar", GameManager.go_to_menu))


func _slider(value: float, cb: Callable) -> HSlider:
        var s := HSlider.new()
        s.min_value = 0.0
        s.max_value = 1.0
        s.step = 0.05
        s.value = value
        s.custom_minimum_size = Vector2(360, 32)
        s.value_changed.connect(cb)
        return s


func _toggle(text: String, pressed: bool, cb: Callable) -> CheckButton:
        var c := CheckButton.new()
        c.text = text
        c.button_pressed = pressed
        c.add_theme_font_size_override("font_size", 24)
        c.toggled.connect(func(_on: bool) -> void: cb.call())
        return c


func _on_sfx_changed(v: float) -> void:
        AudioManager.set_sfx_volume(v)
        AudioManager.play_sfx("coin")
