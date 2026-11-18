extends "res://scripts/systems/Trap.gd"
## Chao que desaparece em sequencia quando o jogador pisa nele.

@export var count: int = 6
@export var block_size: float = 64.0
@export var delay: float = 0.35
@export var reset_time: float = 4.0
@export var tile_texture: Texture2D
## Terra abaixo de cada bloco, para o chao que some ficar identico ao chao real.
@export var fill_texture: Texture2D
@export var fill_height: float = 0.0

var blocks: Array[StaticBody2D] = []


func _ready() -> void:
        auto_activate = true
        for i in count:
                var b := StaticBody2D.new()
                b.position = Vector2(i * block_size, 0)
                var cs := CollisionShape2D.new()
                var rect := RectangleShape2D.new()
                rect.size = Vector2(block_size, 32)
                cs.shape = rect
                cs.position = Vector2(block_size / 2.0, 16)
                b.add_child(cs)
                if tile_texture:
                        var s := Sprite2D.new()
                        s.texture = tile_texture
                        s.centered = false
                        s.region_enabled = true
                        s.region_rect = Rect2(0, 0, block_size, 32)
                        s.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
                        b.add_child(s)
                if fill_texture and fill_height > 0.0:
                        var f := Sprite2D.new()
                        f.texture = fill_texture
                        f.centered = false
                        f.region_enabled = true
                        f.region_rect = Rect2(0, 0, block_size, fill_height)
                        f.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
                        f.position = Vector2(0, 32)
                        b.add_child(f)
                add_child(b)
                blocks.append(b)


func _should_activate(p) -> bool:
        var feet: float = p.global_position.y + 32.0
        return p.global_position.x > global_position.x and p.global_position.x < global_position.x + count * block_size and absf(feet - global_position.y) < 8.0


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        for b in blocks:
                var tw := create_tween()
                tw.tween_property(b, "modulate", Color(1, 0.3, 0.3, 1), delay * 0.8)
                await _wait(delay)
                b.collision_layer = 0
                b.visible = false
        await _wait(reset_time)
        reset()


func _on_reset() -> void:
        for b in blocks:
                b.collision_layer = 1
                b.visible = true
                b.modulate = Color.WHITE
