extends "res://scripts/enemies/Enemy.gd"
## Tartaruga: entra no casco (invulneravel) quando o jogador chega perto.
## Sai do casco depois de 3s com um pulinho surpresa na direcao do jogador.

enum TState { WALK, SHELL }

@export var shell_range: float = 80.0
@export var shell_duration: float = 3.0

var t_state: TState = TState.WALK
var shell_timer: float = 0.0
var cooldown: float = 0.0


func _ai(delta: float) -> void:
        cooldown -= delta
        var p = _get_player()
        if t_state == TState.WALK:
                velocity.x = direction * speed
                flip_on_wall()
                if cooldown <= 0.0 and p and not p.is_dead and global_position.distance_to(p.global_position) < shell_range:
                        t_state = TState.SHELL
                        shell_timer = shell_duration
                        stompable = false
                        sprite.play("shell")
        else:
                velocity.x = 0.0
                shell_timer -= delta
                if shell_timer <= 0.0:
                        t_state = TState.WALK
                        stompable = true
                        cooldown = 1.5
                        sprite.play("walk")
                        if p:
                                direction = 1 if p.global_position.x > global_position.x else -1
                        velocity.y = -280.0
                        AudioManager.play_sfx("trap")
