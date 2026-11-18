extends "res://scripts/systems/Trap.gd"
## Bloco do teto que cai quando o jogador passa embaixo.

@export var fall_distance: float = 400.0

var falling: bool = false
var fall_speed: float = 0.0
var start_pos: Vector2

@onready var block: Area2D = $Block


func _ready() -> void:
        start_pos = block.position


func _should_activate(p) -> bool:
        return absf(p.global_position.x - (global_position.x + 32.0)) < 60.0 and p.global_position.y > global_position.y


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        var tw := create_tween()
        for i in 4:
                tw.tween_property(block, "position:x", start_pos.x + (2.0 if i % 2 == 0 else -2.0), 0.05)
        tw.tween_property(block, "position:x", start_pos.x, 0.01)
        await tw.finished
        falling = true


func _trap_physics(delta: float) -> void:
        if not falling:
                return
        fall_speed += 1500.0 * delta
        block.position.y += fall_speed * delta
        _hurt_player_in(block)
        if block.position.y >= start_pos.y + fall_distance:
                block.position.y = start_pos.y + fall_distance
                falling = false
                _land()


func _land() -> void:
        AudioManager.play_sfx("boss_hurt")
        await _wait(1.5)
        var tw := create_tween()
        tw.tween_property(block, "modulate:a", 0.0, 0.4)
        await tw.finished
        await _wait(1.5)
        reset()


func _on_reset() -> void:
        fall_speed = 0.0
        block.position = start_pos
        block.modulate.a = 1.0
