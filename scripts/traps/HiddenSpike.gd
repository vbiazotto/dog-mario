extends "res://scripts/systems/Trap.gd"
## Espinhos invisiveis (modulate.a = 0) que surgem quando o jogador entra na zona.

@export var width: float = 64.0

@onready var spikes: Area2D = $Spikes


func _ready() -> void:
        spikes.modulate.a = 0.0
        # Armadilha invisivel: nada aparece ate o jogador pisar na zona.
        # Ao ativar, os espinhos "brotam" do chao (feedback do dano).
        $Spikes/Sprite2D.visible = false


func _should_activate(p) -> bool:
        return absf(p.global_position.x - (global_position.x + width / 2.0)) < activation_range and absf(p.global_position.y - global_position.y) < 120.0


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        $Spikes/Sprite2D.visible = true
        spikes.position.y = 16.0
        var tw := create_tween().set_parallel(true)
        tw.tween_property(spikes, "modulate:a", 1.0, 0.08)
        tw.tween_property(spikes, "position:y", 0.0, 0.08)


func _trap_physics(_delta: float) -> void:
        if activated and spikes.modulate.a > 0.5:
                _hurt_player_in(spikes)
