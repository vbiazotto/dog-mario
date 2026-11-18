extends CanvasLayer
## Menu de pausa (ESC): Continuar, Reiniciar, Menu Principal.

const UI := preload("res://scripts/ui/UIBuilder.gd")

var root: Control


func _ready() -> void:
        add_to_group("pause_menu")
        process_mode = Node.PROCESS_MODE_ALWAYS
        layer = 20
        root = Control.new()
        root.set_anchors_preset(Control.PRESET_FULL_RECT)
        add_child(root)
        var dim := ColorRect.new()
        dim.color = Color(0, 0, 0, 0.6)
        dim.set_anchors_preset(Control.PRESET_FULL_RECT)
        root.add_child(dim)
        var v := UI.centered_vbox(root)
        v.add_child(UI.label("PAUSADO", 64, Color(1, 0.85, 0.3)))
        v.add_child(UI.button("Continuar", toggle))
        v.add_child(UI.button("Reiniciar Fase", _on_restart))
        v.add_child(UI.button("Menu Principal", _on_menu))
        visible = false


func _unhandled_input(event: InputEvent) -> void:
        if event.is_action_pressed("pause"):
                toggle()
                get_viewport().set_input_as_handled()


func toggle() -> void:
        visible = not visible
        get_tree().paused = visible


func _on_restart() -> void:
        get_tree().paused = false
        GameManager.reset_level()


func _on_menu() -> void:
        GameManager.go_to_menu()
