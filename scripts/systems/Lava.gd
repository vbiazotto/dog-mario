extends Area2D
## Lava: morte instantanea.

@onready var visual: Sprite2D = $Sprite2D


func _ready() -> void:
        body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
        var r := visual.region_rect
        r.position.x = fmod(r.position.x + delta * 12.0, 128.0)
        visual.region_rect = r


func _on_body_entered(body) -> void:
        if body.is_in_group("player"):
                body.die()
