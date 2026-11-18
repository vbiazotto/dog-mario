extends "res://scripts/systems/Trap.gd"
## Plataforma que oscila entre point_a e point_b (lerp suave).

@export var point_a: Vector2 = Vector2.ZERO
@export var point_b: Vector2 = Vector2(200, 0)
@export var speed: float = 1.0

var t: float = 0.0

@onready var body: AnimatableBody2D = $Body


func _ready() -> void:
        auto_activate = false
        body.position = point_a


func _trap_physics(delta: float) -> void:
        t += delta * speed
        var w := (sin(t - PI / 2.0) + 1.0) * 0.5
        body.position = point_a.lerp(point_b, w)
