extends CharacterBody2D
## Base dos inimigos: patrulha, contato causa dano, pisar em cima mata.

signal defeated

@export var health: int = 1
@export var speed: float = 80.0
@export var direction: int = -1
@export var gravity: float = 800.0
@export var use_gravity: bool = true
@export var avoid_edges: bool = true
@export var stompable: bool = true
@export var score_value: int = 200

var is_dead: bool = false
var player = null
var _edge_ray: RayCast2D = null

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var hitbox: Area2D = $Hitbox


func _ready() -> void:
        add_to_group("enemy")
        if avoid_edges and use_gravity:
                _edge_ray = RayCast2D.new()
                _edge_ray.target_position = Vector2(0, 56)
                _edge_ray.collision_mask = 1
                add_child(_edge_ray)
        if sprite.sprite_frames.has_animation("walk"):
                sprite.play("walk")
        _enemy_ready()


func _enemy_ready() -> void:
        pass


func _get_player():
        if player == null or not is_instance_valid(player):
                player = get_tree().get_first_node_in_group("player") as Node2D
        return player


func _physics_process(delta: float) -> void:
        if is_dead:
                return
        _ai(delta)
        if use_gravity:
                velocity.y = minf(velocity.y + gravity * delta, 900.0)
        move_and_slide()
        _check_player_contact()


func _ai(_delta: float) -> void:
        velocity.x = direction * speed
        flip_on_wall()


func _edge_ahead_missing() -> bool:
        if _edge_ray == null or not is_on_floor():
                return false
        _edge_ray.position.x = 24.0 * direction
        _edge_ray.force_raycast_update()
        return not _edge_ray.is_colliding()


func flip_on_wall() -> void:
        if is_on_wall() or _edge_ahead_missing():
                direction *= -1
                velocity.x = direction * speed
        sprite.flip_h = direction > 0


func _check_player_contact() -> void:
        var _bodies: Array = hitbox.get_overlapping_bodies()
        for body in _bodies:
                if body.is_in_group("player"):
                        _on_player_collision(body)


func _on_player_collision(p) -> void:
        if is_dead or p.is_dead:
                return
        # Logo apos um pisao o jogador ainda sobrepoe a hitbox por alguns frames;
        # esse contato residual e ignorado.
        if p.has_method("is_stomping") and p.is_stomping():
                return
        var from_above: bool = p.global_position.y < global_position.y - 12.0
        if from_above:
                # So pisa se estiver caindo/parado em cima; subindo por cima nao fere ninguem.
                if p.velocity.y >= 0.0:
                        p.bounce()
                        if stompable:
                                take_damage()
                return
        p.take_damage(global_position)


func take_damage(amount: int = 1) -> void:
        if is_dead:
                return
        health -= amount
        if health <= 0:
                die()
        else:
                var tw := create_tween()
                tw.tween_property(sprite, "modulate", Color(1, 0.3, 0.3), 0.1)
                tw.tween_property(sprite, "modulate", Color.WHITE, 0.1)


func die() -> void:
        if is_dead:
                return
        is_dead = true
        AudioManager.play_sfx("enemy_die")
        GameManager.add_score(score_value)
        defeated.emit()
        hitbox.set_deferred("monitoring", false)
        $CollisionShape2D.set_deferred("disabled", true)
        if sprite.sprite_frames.has_animation("dead"):
                sprite.play("dead")
        var tw := create_tween()
        tw.tween_property(sprite, "scale", Vector2(sprite.scale.x * 1.3, sprite.scale.y * 0.3), 0.25)
        tw.tween_property(self, "modulate:a", 0.0, 0.3)
        tw.tween_callback(queue_free)
