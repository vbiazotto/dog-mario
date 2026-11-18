extends "res://scripts/enemies/Enemy.gd"
## Cachorro fantasma: flutua (seno), atravessa paredes e persegue o jogador.

@export var float_amplitude: float = 20.0
@export var chase_speed: float = 70.0
@export var wake_range: float = 650.0

var t: float = 0.0


func _enemy_ready() -> void:
        use_gravity = false
        sprite.play("float")
        modulate.a = 0.8


func _ai(delta: float) -> void:
        t += delta
        var p = _get_player()
        velocity = Vector2(0.0, cos(t * 3.0) * float_amplitude * 3.0)
        if p and not p.is_dead:
                var to: Vector2 = p.global_position - global_position
                if to.length() < wake_range and to.length() > 4.0:
                        velocity += to.normalized() * chase_speed
                        sprite.flip_h = to.x > 0.0
