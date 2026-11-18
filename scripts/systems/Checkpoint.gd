extends Area2D
## Checkpoint: salva a posicao no GameManager. 50% de chance de ser uma armadilha!

@export var trap_chance: float = 0.5
@export var spawn_offset: Vector2 = Vector2(0, 8)

var active: bool = false

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
        body_entered.connect(_on_body_entered)
        sprite.play("inactive")
        if GameManager.has_checkpoint and GameManager.checkpoint_position.is_equal_approx(global_position + spawn_offset):
                active = true
                sprite.play("active")


func _on_body_entered(body) -> void:
        if active or not body.is_in_group("player"):
                return
        active = true
        GameManager.set_checkpoint(global_position + spawn_offset)
        sprite.play("active")
        AudioManager.play_sfx("checkpoint")
        var tw := create_tween()
        tw.tween_property(sprite, "scale", sprite.scale * 1.3, 0.1)
        tw.tween_property(sprite, "scale", sprite.scale, 0.15)
        if randf() < trap_chance:
                var scene := load("res://scenes/enemies/Slime.tscn") as PackedScene
                if scene:
                        var slime = scene.instantiate()
                        slime.position = position + Vector2(160, -24)
                        get_parent().add_child.call_deferred(slime)
                        AudioManager.play_sfx("trap")
