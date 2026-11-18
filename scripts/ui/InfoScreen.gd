extends Control
## Telas de texto: Como Jogar e Creditos.

const UI := preload("res://scripts/ui/UIBuilder.gd")

@export_enum("howto", "credits") var mode: String = "howto"

const TEXTS := {
        "howto": ["COMO JOGAR", "A / D ou Setas  -  Andar\nW / Espaco / Seta Cima  -  Pular (segure para pular mais alto)\nShift  -  Correr\nEsc  -  Pausar      R  -  Reiniciar fase\n\nPule em cima dos inimigos para derrota-los.\nCuidado: NADA e o que parece! Moedas explodem,\nplataformas somem, checkpoints mentem...\nVoce tem 3 vidas. Boa sorte, Doguinho!"],
        "credits": ["CREDITOS", "DOG MARIO - A Aventura Impossivel\n\nTrabalho universitario de Desenvolvimento de Jogos\nEngine: Godot 4.x  |  Linguagem: GDScript 2.0\n\nArte: pixel art original gerada proceduralmente (Python + Pillow)\nAudio: sintese procedural em Python (struct + math)\n\nInspirado em Super Mario Bros e jogos 'troll' como Cat Mario.\nObrigado por jogar!"],
}


func _ready() -> void:
        var data: Array = TEXTS.get(mode, TEXTS["howto"])
        var v := UI.centered_vbox(self, 24)
        v.add_child(UI.label(data[0], 56, Color(1, 0.85, 0.3)))
        v.add_child(UI.label(data[1], 24))
        var back := UI.button("Voltar", GameManager.go_to_menu)
        v.add_child(back)
        back.grab_focus()
