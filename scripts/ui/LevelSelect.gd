extends Control
## Selecao de fases: desbloqueio via SaveManager, mostra recordes.

const UI := preload("res://scripts/ui/UIBuilder.gd")


func _ready() -> void:
        var v := UI.centered_vbox(self, 16)
        v.add_child(UI.label("SELECIONE A FASE", 56, Color(1, 0.85, 0.3)))
        for i in range(1, 4):
                var unlocked := SaveManager.is_level_unlocked(i)
                var best_t := SaveManager.get_best_time(i)
                var info := "Recorde: %d pts | %s" % [SaveManager.get_best_score(i), GameManager.format_time(best_t) if best_t >= 0.0 else "--:--"]
                var text := "Fase %d - %s\n%s" % [i, GameManager.LEVEL_NAMES[i - 1], info if unlocked else "BLOQUEADA"]
                var b := UI.button(text, GameManager.start_new_game.bind(i), 22)
                b.custom_minimum_size = Vector2(560, 80)
                b.disabled = not unlocked
                v.add_child(b)
        v.add_child(UI.button("Voltar", GameManager.go_to_menu))
