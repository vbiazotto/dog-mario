extends "res://scripts/systems/Trap.gd"
## Plataforma falsa: parece normal, some ao contato (collision_layer = 0).

@export var respawn_time: float = 4.0
## Largura da plataforma (px). Use a largura exata do buraco.
@export var width: float = 96.0
## Preenchimento de terra abaixo do topo (para o chao falso ficar identico ao chao real).
@export var fill_texture: Texture2D
@export var fill_height: float = 0.0

@onready var body: StaticBody2D = $Body
@onready var detector: Area2D = $Body/Detector


func _ready() -> void:
        auto_activate = false
        detector.body_entered.connect(_on_body_entered)
        _apply_size()


func _apply_size() -> void:
        var top := $Body/Sprite2D as Sprite2D
        top.region_rect = Rect2(0, 0, width, 32)
        var cs := $Body/CollisionShape2D as CollisionShape2D
        cs.shape = cs.shape.duplicate()
        (cs.shape as RectangleShape2D).size = Vector2(width, 32)
        cs.position = Vector2(width / 2.0, 16)
        var dcs := $Body/Detector/CollisionShape2D as CollisionShape2D
        dcs.shape = dcs.shape.duplicate()
        (dcs.shape as RectangleShape2D).size.x = maxf(width - 8.0, 8.0)
        dcs.position.x = width / 2.0
        if fill_texture and fill_height > 0.0:
                var fill := Sprite2D.new()
                fill.name = "Fill"
                fill.texture = fill_texture
                fill.centered = false
                fill.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
                fill.region_enabled = true
                fill.region_rect = Rect2(0, 0, width, fill_height)
                fill.position = Vector2(0, 32)
                body.add_child(fill)


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        await _wait(0.12)
        body.set_deferred("collision_layer", 0)
        var tw := create_tween()
        tw.tween_property(body, "modulate:a", 0.0, 0.2)
        await _wait(respawn_time)
        reset()


func _on_reset() -> void:
        body.collision_layer = 1
        body.modulate.a = 1.0
