extends Area2D
## Espinho vivo: escondido ate o jogador chegar a 100px, entao surge e ataca.

@export var detect_range: float = 100.0

var spike_state: int = 0  # 0 = escondido, 1 = surgindo, 2 = atacando

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
        add_to_group("enemy")
        sprite.play("hidden")
        # Armadilha invisivel: so o colisor (CollisionShape2D) continua ativo.
        sprite.visible = false


func _physics_process(_delta: float) -> void:
        var p := get_tree().get_first_node_in_group("player") as Node2D
        if p == null:
                return
        if spike_state == 0 and global_position.distance_to(p.global_position) < detect_range:
                _appear()
        if spike_state == 2:
                var _bodies: Array = get_overlapping_bodies()
                for b in _bodies:
                        if b.is_in_group("player"):
                                b.take_damage(global_position)


func _appear() -> void:
        spike_state = 1
        # Invisivel ate o bote: so aparece no instante em que ataca.
        sprite.visible = true
        sprite.play("appear")
        AudioManager.play_sfx("trap")
        await get_tree().create_timer(0.25).timeout
        if is_inside_tree():
                spike_state = 2
                sprite.play("attack")
