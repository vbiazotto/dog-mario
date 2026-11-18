extends "res://scripts/enemies/Enemy.gd"
## Passaro: patrulha no ar e mergulha quando ve o jogador abaixo.

enum BState { PATROL, DIVE, RETURN }

@export var patrol_distance: float = 150.0
@export var dive_speed: float = 380.0
@export var detect_range: float = 220.0

var b_state: BState = BState.PATROL
var origin: Vector2 = Vector2.ZERO
var t: float = 0.0
var dive_target: Vector2 = Vector2.ZERO


func _enemy_ready() -> void:
        use_gravity = false
        origin = global_position
        sprite.play("fly")


func _ai(delta: float) -> void:
        t += delta
        var p = _get_player()
        match b_state:
                BState.PATROL:
                        var tx := origin.x + sin(t * 1.2) * patrol_distance
                        var ty := origin.y + sin(t * 3.0) * 12.0
                        velocity = Vector2((tx - global_position.x) * 4.0, (ty - global_position.y) * 4.0)
                        if p and not p.is_dead:
                                var dx := absf(p.global_position.x - global_position.x)
                                var dy: float = p.global_position.y - global_position.y
                                if dx < detect_range * 0.5 and dy > 40.0 and dy < detect_range * 1.5:
                                        b_state = BState.DIVE
                                        dive_target = p.global_position
                                        sprite.play("dive")
                BState.DIVE:
                        var to := dive_target - global_position
                        if to.length() < 12.0:
                                b_state = BState.RETURN
                                sprite.play("fly")
                        else:
                                velocity = to.normalized() * dive_speed
                BState.RETURN:
                        var back := origin - global_position
                        if back.length() < 10.0:
                                b_state = BState.PATROL
                        else:
                                velocity = back.normalized() * speed * 2.0
        if absf(velocity.x) > 1.0:
                sprite.flip_h = velocity.x > 0.0
