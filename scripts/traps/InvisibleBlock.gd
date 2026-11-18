extends "res://scripts/systems/Trap.gd"
## Bloco invisivel: aparece quando o jogador pula por baixo dele (bate a cabeca!).

@onready var block: StaticBody2D = $Block


func _ready() -> void:
        block.modulate.a = 0.0
        block.collision_layer = 0


func _should_activate(p) -> bool:
        var c := global_position + Vector2(32, 32)
        return absf(p.global_position.x - c.x) < 44.0 and p.global_position.y > c.y and p.global_position.y - c.y < 150.0 and p.velocity.y < 0.0


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        block.collision_layer = 1
        var tw := create_tween()
        tw.tween_property(block, "modulate:a", 1.0, 0.1)
        tw.tween_property(block, "position:y", -6.0, 0.05)
        tw.tween_property(block, "position:y", 0.0, 0.05)
