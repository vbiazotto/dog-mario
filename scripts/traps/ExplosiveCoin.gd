extends "res://scripts/systems/Trap.gd"
## Moeda explosiva: parece uma moeda normal, mas explode ao ser coletada.

@onready var area: Area2D = $Area
@onready var coin_sprite: AnimatedSprite2D = $Area/AnimatedSprite2D
@onready var explosion: AnimatedSprite2D = $Explosion


func _ready() -> void:
        auto_activate = false
        explosion.visible = false
        coin_sprite.play("spin")
        area.body_entered.connect(_on_body_entered)


func _on_activate() -> void:
        AudioManager.play_sfx("explosion")
        coin_sprite.visible = false
        area.set_deferred("monitoring", false)
        explosion.visible = true
        explosion.play("boom")
        var _bodies: Array = area.get_overlapping_bodies()
        for b in _bodies:
                if b.is_in_group("player"):
                        b.take_damage(global_position)
        await _wait(0.6)
        queue_free()
