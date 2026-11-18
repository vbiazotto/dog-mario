extends Node
## Cena raiz: abre o menu principal.


func _ready() -> void:
        get_tree().change_scene_to_file.call_deferred("res://scenes/menus/Menu.tscn")
