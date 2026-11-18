extends Area2D
## Moeda: +100 pontos.

@export var value: int = 100

var collected: bool = false

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
        sprite.play("spin")
        body_entered.connect(_on_body_entered)


func _on_body_entered(body) -> void:
        if collected or not body.is_in_group("player"):
                return
        collected = true
        GameManager.add_score(value)
        AudioManager.play_sfx("coin")
        set_deferred("monitoring", false)
        var tw := create_tween().set_parallel(true)
        tw.tween_property(self, "position:y", position.y - 40.0, 0.3)
        tw.tween_property(self, "modulate:a", 0.0, 0.3)
        tw.chain().tween_callback(queue_free)
