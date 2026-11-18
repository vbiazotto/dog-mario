extends Control
## Tela de Game Over.

const UI := preload("res://scripts/ui/UIBuilder.gd")


func _ready() -> void:
        AudioManager.stop_music()
        var v := UI.centered_vbox(self, 18)
        v.add_child(UI.label("GAME OVER", 80, Color(1, 0.25, 0.25)))
        v.add_child(UI.label("O Doguinho nao aguentou...", 30))
        v.add_child(UI.label("Mortes nesta partida: %d" % GameManager.deaths, 30, Color(1, 0.7, 0.7)))
        v.add_child(UI.label("Mortes totais: %d" % SaveManager.total_deaths, 26, Color(0.9, 0.9, 0.9)))
        var retry := UI.button("Tentar Novamente", GameManager.retry_level)
        v.add_child(retry)
        v.add_child(UI.button("Menu Principal", GameManager.go_to_menu))
        retry.grab_focus()
