extends CharacterBody2D
## Chefe final: Cachorro Maldito. 10 HP, 2 fases, 3 padroes de ataque.

signal boss_defeated
signal health_changed(hp: int, max_hp: int)

enum Phase { IDLE, PHASE1, PHASE2, DEFEATED }

const PROJECTILE := preload("res://scripts/bosses/BossProjectile.gd")
const PATTERN := [0, 1, 2, 1]  # 0 = projeteis, 1 = mergulho, 2 = onda

@export var max_health: int = 10
@export var arena_left: float = 3450.0
@export var arena_right: float = 3950.0
@export var hover_y: float = 380.0
@export var ground_y: float = 536.0
@export var activation_x: float = 3380.0

var health: int = 10
var phase: Phase = Phase.IDLE
var t: float = 0.0
var attack_timer: float = 2.0
var busy: bool = false
var hurt_cooldown: float = 0.0
var pattern_index: int = 0
var player = null

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var hitbox: Area2D = $Hitbox
@onready var boss_ui: CanvasLayer = $BossUI
@onready var health_bar: ProgressBar = $BossUI/HealthBar
@onready var name_label: Label = $BossUI/NameLabel


func _ready() -> void:
        add_to_group("enemy")
        add_to_group("boss")
        health = max_health
        health_bar.max_value = max_health
        health_bar.value = health
        boss_ui.visible = false
        sprite.play("idle")


func _physics_process(delta: float) -> void:
        if phase == Phase.DEFEATED:
                return
        player = get_tree().get_first_node_in_group("player") as Node2D
        if player == null:
                return
        t += delta
        hurt_cooldown -= delta
        if phase == Phase.IDLE:
                global_position.y = hover_y + sin(t * 2.0) * 10.0
                if player.global_position.x > activation_x:
                        _start_fight()
                return
        if not busy:
                var target_x := clampf(player.global_position.x, arena_left, arena_right)
                var move_speed := 90.0 if phase == Phase.PHASE1 else 160.0
                global_position.x = move_toward(global_position.x, target_x, move_speed * delta)
                global_position.y = hover_y + sin(t * 2.5) * 25.0
                attack_timer -= delta
                if attack_timer <= 0.0:
                        _choose_attack()
        sprite.flip_h = player.global_position.x > global_position.x
        _check_player_contact()


func _start_fight() -> void:
        phase = Phase.PHASE1
        boss_ui.visible = true
        attack_timer = 1.5
        AudioManager.play_music("boss")


func _choose_attack() -> void:
        var p: int = PATTERN[pattern_index % PATTERN.size()]
        pattern_index += 1
        match p:
                0:
                        _attack_projectiles()
                1:
                        _attack_dive()
                2:
                        _attack_wave()
        attack_timer = 2.6 if phase == Phase.PHASE1 else 1.5


func _wait(seconds: float) -> void:
        var tm := Timer.new()
        tm.one_shot = true
        tm.wait_time = seconds
        add_child(tm)
        tm.start()
        await tm.timeout
        tm.queue_free()


func _spawn_projectile(vel: Vector2) -> void:
        var proj = PROJECTILE.new()
        proj.velocity = vel
        proj.position = global_position
        get_parent().add_child(proj)


func _attack_projectiles() -> void:
        busy = true
        sprite.play("attack")
        var count := 3 if phase == Phase.PHASE1 else 5
        for i in count:
                if phase == Phase.DEFEATED or not is_instance_valid(player):
                        return
                _spawn_projectile((player.global_position - global_position).normalized() * 230.0)
                AudioManager.play_sfx("trap")
                await _wait(0.35)
        sprite.play("idle")
        busy = false


func _attack_dive() -> void:
        busy = true
        sprite.play("attack")
        var target_x := clampf(player.global_position.x, arena_left, arena_right)
        var tw := create_tween()
        tw.tween_property(self, "global_position", Vector2(target_x, ground_y), 0.6 if phase == Phase.PHASE1 else 0.45).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
        await tw.finished
        if phase == Phase.DEFEATED:
                return
        sprite.play("idle")
        await _wait(1.0 if phase == Phase.PHASE1 else 0.7)  # janela para pisar no chefe
        if phase == Phase.DEFEATED:
                return
        var tw2 := create_tween()
        tw2.tween_property(self, "global_position:y", hover_y, 0.6)
        await tw2.finished
        busy = false


func _attack_wave() -> void:
        busy = true
        sprite.play("attack")
        var count := 6 if phase == Phase.PHASE1 else 9
        for i in count:
                var ang := deg_to_rad(20.0 + 140.0 * float(i) / float(count - 1))
                _spawn_projectile(Vector2(cos(ang), sin(ang)) * 170.0)
        AudioManager.play_sfx("explosion")
        await _wait(0.6)
        if phase != Phase.DEFEATED:
                sprite.play("idle")
        busy = false


func _check_player_contact() -> void:
        var _bodies: Array = hitbox.get_overlapping_bodies()
        for body in _bodies:
                if not body.is_in_group("player") or body.is_dead:
                        continue
                # Contato residual logo apos o pisao: ignora.
                if body.has_method("is_stomping") and body.is_stomping():
                        continue
                var from_above: bool = body.global_position.y < global_position.y - 20.0
                if from_above:
                        if body.velocity.y >= 0.0:
                                body.bounce()
                                take_damage()
                        continue
                body.take_damage(global_position)


func take_damage(amount: int = 1) -> void:
        if hurt_cooldown > 0.0 or phase == Phase.IDLE or phase == Phase.DEFEATED:
                return
        health -= amount
        hurt_cooldown = 1.0
        health_bar.value = health
        health_changed.emit(health, max_health)
        AudioManager.play_sfx("boss_hurt")
        GameManager.add_score(500)
        sprite.play("hurt")
        var tw := create_tween()
        tw.tween_property(sprite, "modulate", Color(1, 0.2, 0.2), 0.1)
        tw.tween_property(sprite, "modulate", Color.WHITE, 0.2)
        if health <= 0:
                _defeat()
                return
        if phase == Phase.PHASE1 and health <= max_health / 2.0:
                phase = Phase.PHASE2
                name_label.text = "CACHORRO MALDITO - FURIOSO!"
                name_label.add_theme_color_override("font_color", Color(1, 0.3, 0.3))


func _defeat() -> void:
        phase = Phase.DEFEATED
        busy = true
        hitbox.set_deferred("monitoring", false)
        sprite.play("death")
        AudioManager.play_sfx("explosion")
        GameManager.add_score(5000)
        for proj in get_tree().get_nodes_in_group("boss_projectile"):
                proj.queue_free()
        boss_defeated.emit()
        AudioManager.play_music("level3")
        var tw := create_tween()
        tw.tween_interval(1.2)
        tw.tween_property(self, "modulate:a", 0.0, 0.8)
        tw.tween_callback(boss_ui.hide)
        tw.tween_callback(queue_free)
