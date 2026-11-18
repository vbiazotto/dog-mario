extends Control
## Tela de vitoria da fase.

const UI := preload("res://scripts/ui/UIBuilder.gd")


func _ready() -> void:
        AudioManager.play_music("victory")
        var lvl := GameManager.current_level
        var final := lvl >= GameManager.LEVELS.size()
        var v := UI.centered_vbox(self, 16)
        v.add_child(UI.label("VOCE ZEROU O JOGO!" if final else "FASE %d COMPLETA!" % lvl, 64, Color(1, 0.9, 0.3)))
        v.add_child(UI.label(GameManager.LEVEL_NAMES[lvl - 1], 28))
        v.add_child(UI.label("Pontuacao: %d" % GameManager.score, 34))
        v.add_child(UI.label("Tempo: %s" % GameManager.format_time(GameManager.last_level_time), 34))
        v.add_child(UI.label("Mortes: %d" % GameManager.deaths, 28, Color(1, 0.7, 0.7)))
        v.add_child(UI.label("Recorde: %d pts | %s" % [SaveManager.get_best_score(lvl), GameManager.format_time(SaveManager.get_best_time(lvl))], 24, Color(0.7, 1, 0.7)))
        var next := UI.button("Voltar ao Menu" if final else "Proxima Fase", GameManager.next_level)
        v.add_child(next)
        if not final:
                v.add_child(UI.button("Menu Principal", GameManager.go_to_menu))
        next.grab_focus()
