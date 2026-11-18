extends "res://scripts/enemies/Enemy.gd"
## Slime: patrulha e persegue o jogador quando ele chega a 150px.

enum AIState { PATROL, CHASE }

@export var chase_range: float = 150.0
@export var chase_speed: float = 120.0

var ai_state: AIState = AIState.PATROL


func _ai(_delta: float) -> void:
        var p = _get_player()
        ai_state = AIState.PATROL
        if p and not p.is_dead:
                if absf(p.global_position.x - global_position.x) < chase_range and absf(p.global_position.y - global_position.y) < 90.0:
                        ai_state = AIState.CHASE
        if ai_state == AIState.CHASE:
                direction = 1 if p.global_position.x > global_position.x else -1
                velocity.x = 0.0 if _edge_ahead_missing() else direction * chase_speed
                sprite.flip_h = direction > 0
        else:
                velocity.x = direction * speed
                flip_on_wall()
