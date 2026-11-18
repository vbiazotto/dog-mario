extends Area2D
## Projetil fantasma lancado pelo chefe (criado via codigo).

var velocity: Vector2 = Vector2.ZERO
var life: float = 5.0


func _ready() -> void:
        add_to_group("boss_projectile")
        collision_layer = 0
        collision_mask = 2
        var cs := CollisionShape2D.new()
        var circle := CircleShape2D.new()
        circle.radius = 12.0
        cs.shape = circle
        add_child(cs)
        var tex := load("res://assets/sprites/enemies/ghost_dog.png") as Texture2D
        if tex:
                var at := AtlasTexture.new()
                at.atlas = tex
                at.region = Rect2(0, 0, 32, 32)
                var s := Sprite2D.new()
                s.texture = at
                s.modulate = Color(0.8, 0.4, 1.0, 0.85)
                add_child(s)
        body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
        position += velocity * delta
        rotation += delta * 4.0
        life -= delta
        if life <= 0.0:
                queue_free()


func _on_body_entered(body) -> void:
        if body.is_in_group("player"):
                body.take_damage(global_position)
                queue_free()
