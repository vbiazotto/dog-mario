extends "res://scripts/systems/Trap.gd"
## Plataforma que treme ao ser pisada, cai depois de 1s e volta depois de 3s.

@export var shake_time: float = 1.0
@export var reset_time: float = 3.0

var falling: bool = false
var fall_speed: float = 0.0
var start_pos: Vector2

@onready var body: AnimatableBody2D = $Body
@onready var visual: Sprite2D = $Body/Sprite2D
@onready var detector: Area2D = $Body/Detector


func _ready() -> void:
        auto_activate = false
        start_pos = body.position
        detector.body_entered.connect(_on_body_entered)


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        var tw := create_tween()
        for i in 8:
                tw.tween_property(visual, "position:x", 3.0 if i % 2 == 0 else -3.0, shake_time / 8.0)
        tw.tween_property(visual, "position:x", 0.0, 0.01)
        await tw.finished
        falling = true
        await _wait(reset_time)
        reset()


func _trap_physics(delta: float) -> void:
        if falling:
                fall_speed = minf(fall_speed + 1200.0 * delta, 900.0)
                body.position.y += fall_speed * delta


func _on_reset() -> void:
        falling = false
        fall_speed = 0.0
        body.position = start_pos
