extends "res://scripts/systems/Trap.gd"
## Parede esmagadora: ao acionar, fecha (desce) e reabre em ciclos.

@export var close_distance: float = 300.0
@export var cycle_time: float = 2.4

@onready var wall: Area2D = $Wall


func _should_activate(p) -> bool:
        return absf(p.global_position.x - (global_position.x + 32.0)) < activation_range


func _on_activate() -> void:
        while is_inside_tree():
                AudioManager.play_sfx("trap")
                var tw := create_tween()
                tw.tween_property(wall, "position:y", close_distance, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
                await tw.finished
                await _wait(0.6)
                var tw2 := create_tween()
                tw2.tween_property(wall, "position:y", 0.0, 0.9)
                await tw2.finished
                await _wait(cycle_time * 0.5)


func _trap_physics(_delta: float) -> void:
        if activated and wall.position.y > close_distance * 0.5:
                _hurt_player_in(wall)
