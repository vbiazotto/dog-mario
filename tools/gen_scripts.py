"""Escreve todos os scripts GDScript (Godot 4) do DOG MARIO."""
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = {}

S["systems/GameManager.gd"] = r'''extends Node
## Autoload: estado global do jogo (vidas, pontos, fases, checkpoints).

signal level_complete(level: int)
signal game_over
signal lives_changed(lives: int)
signal score_changed(score: int)
signal deaths_changed(deaths: int)

const MAX_LIVES := 3
const MENU_SCENE := "res://scenes/menus/Menu.tscn"
const LEVELS := [
        "res://scenes/levels/Level1.tscn",
        "res://scenes/levels/Level2.tscn",
        "res://scenes/levels/Level3.tscn",
]
const LEVEL_NAMES := ["Campo da Falsa Tranquilidade", "Floresta das Armadilhas", "Castelo do Cachorro Maldito"]

var lives: int = MAX_LIVES
var score: int = 0
var deaths: int = 0
var current_level: int = 1
var checkpoint_position: Vector2 = Vector2.ZERO
var has_checkpoint: bool = false
var level_time: float = 0.0
var level_start_score: int = 0
var timer_running: bool = false
var last_level_time: float = 0.0
var _fresh_level: bool = true


func _process(delta: float) -> void:
        if timer_running and not get_tree().paused:
                level_time += delta


func start_new_game(level: int = 1) -> void:
        lives = MAX_LIVES
        score = 0
        deaths = 0
        load_level(level)


func load_level(level: int) -> void:
        current_level = clampi(level, 1, LEVELS.size())
        clear_checkpoint()
        _fresh_level = true
        get_tree().paused = false
        get_tree().change_scene_to_file(LEVELS[current_level - 1])


func on_level_started(level: int) -> void:
        if level != current_level:
                current_level = level
                clear_checkpoint()
                _fresh_level = true
        if _fresh_level:
                level_time = 0.0
                level_start_score = score
                _fresh_level = false
        timer_running = true
        lives_changed.emit(lives)
        score_changed.emit(score)
        deaths_changed.emit(deaths)


func add_score(pts: int) -> void:
        score += pts
        score_changed.emit(score)


## Dano sem morte: retorna true se o jogador ainda tem vidas.
func hurt() -> bool:
        lives = max(lives - 1, 0)
        lives_changed.emit(lives)
        return lives > 0


## Chamado pelo Player depois da animacao de morte.
func player_died(life_already_lost: bool = false) -> void:
        deaths += 1
        SaveManager.add_death()
        deaths_changed.emit(deaths)
        if not life_already_lost:
                lose_life()
                return
        if lives <= 0:
                trigger_game_over()
        else:
                reset_level()


func lose_life() -> void:
        lives = max(lives - 1, 0)
        lives_changed.emit(lives)
        if lives <= 0:
                trigger_game_over()
        else:
                reset_level()


func trigger_game_over() -> void:
        timer_running = false
        game_over.emit()
        save_game()
        get_tree().paused = false
        get_tree().call_deferred("change_scene_to_file", "res://scenes/menus/GameOver.tscn")


func retry_level() -> void:
        lives = MAX_LIVES
        score = level_start_score
        load_level(current_level)


func reset_level() -> void:
        get_tree().paused = false
        get_tree().call_deferred("reload_current_scene")


func complete_level() -> void:
        if not timer_running:
                return
        timer_running = false
        last_level_time = level_time
        SaveManager.save_best_score(current_level, score)
        SaveManager.save_best_time(current_level, level_time)
        SaveManager.unlock_level(current_level + 1)
        clear_checkpoint()
        AudioManager.play_music("victory")
        level_complete.emit(current_level)
        await get_tree().create_timer(1.5).timeout
        get_tree().change_scene_to_file("res://scenes/menus/Victory.tscn")


func next_level() -> void:
        if current_level < LEVELS.size():
                load_level(current_level + 1)
        else:
                go_to_menu()


func go_to_menu() -> void:
        timer_running = false
        get_tree().paused = false
        get_tree().change_scene_to_file(MENU_SCENE)


func save_game() -> void:
        SaveManager.save_data()


func load_game() -> void:
        SaveManager.load_data()


func set_checkpoint(pos: Vector2) -> void:
        checkpoint_position = pos
        has_checkpoint = true


func clear_checkpoint() -> void:
        has_checkpoint = false
        checkpoint_position = Vector2.ZERO


func respawn_player(player: Node2D) -> void:
        if has_checkpoint and player:
                player.global_position = checkpoint_position


static func format_time(t: float) -> String:
        var total := int(t)
        return "%02d:%02d" % [total / 60, total % 60]
'''

S["systems/SaveManager.gd"] = r'''extends Node
## Autoload: salva/carrega progresso com ConfigFile.

const SAVE_PATH := "user://dog_mario_save.cfg"

var levels_unlocked: Array = [1]
var best_scores: Dictionary = {}
var best_times: Dictionary = {}
var total_deaths: int = 0
var music_volume: float = 0.7
var sfx_volume: float = 0.8
var music_muted: bool = false
var sfx_muted: bool = false


func _ready() -> void:
        load_data()


func save_data() -> void:
        var cfg := ConfigFile.new()
        cfg.set_value("progress", "levels_unlocked", levels_unlocked)
        cfg.set_value("progress", "best_scores", best_scores)
        cfg.set_value("progress", "best_times", best_times)
        cfg.set_value("progress", "total_deaths", total_deaths)
        cfg.set_value("settings", "music_volume", music_volume)
        cfg.set_value("settings", "sfx_volume", sfx_volume)
        cfg.set_value("settings", "music_muted", music_muted)
        cfg.set_value("settings", "sfx_muted", sfx_muted)
        cfg.save(SAVE_PATH)


func load_data() -> void:
        var cfg := ConfigFile.new()
        if cfg.load(SAVE_PATH) != OK:
                return
        levels_unlocked = cfg.get_value("progress", "levels_unlocked", [1])
        best_scores = cfg.get_value("progress", "best_scores", {})
        best_times = cfg.get_value("progress", "best_times", {})
        total_deaths = cfg.get_value("progress", "total_deaths", 0)
        music_volume = cfg.get_value("settings", "music_volume", 0.7)
        sfx_volume = cfg.get_value("settings", "sfx_volume", 0.8)
        music_muted = cfg.get_value("settings", "music_muted", false)
        sfx_muted = cfg.get_value("settings", "sfx_muted", false)


func unlock_level(n: int) -> void:
        if n > 3:
                return
        if not levels_unlocked.has(n):
                levels_unlocked.append(n)
                save_data()


func is_level_unlocked(n: int) -> bool:
        return levels_unlocked.has(n)


func save_best_score(level: int, s: int) -> void:
        var k := str(level)
        if s > int(best_scores.get(k, 0)):
                best_scores[k] = s
        save_data()


func save_best_time(level: int, t: float) -> void:
        var k := str(level)
        if not best_times.has(k) or t < float(best_times[k]):
                best_times[k] = t
        save_data()


func get_best_score(level: int) -> int:
        return int(best_scores.get(str(level), 0))


func get_best_time(level: int) -> float:
        return float(best_times.get(str(level), -1.0))


func add_death() -> void:
        total_deaths += 1
'''

S["systems/AudioManager.gd"] = r'''extends Node
## Autoload: musica e efeitos sonoros (carrega WAVs de res://assets/audio/).

const MUSIC_DIR := "res://assets/audio/music/"
const SFX_DIR := "res://assets/audio/sfx/"

var music_player: AudioStreamPlayer
var sfx_players: Array[AudioStreamPlayer] = []
var current_music: String = ""
var _cache: Dictionary = {}


func _ready() -> void:
        process_mode = Node.PROCESS_MODE_ALWAYS
        music_player = AudioStreamPlayer.new()
        add_child(music_player)
        music_player.finished.connect(_on_music_finished)
        for i in 8:
                var p := AudioStreamPlayer.new()
                add_child(p)
                sfx_players.append(p)
        _apply_volumes()


func _get_stream(path: String) -> AudioStream:
        if _cache.has(path):
                return _cache[path]
        var s: AudioStream = null
        if ResourceLoader.exists(path):
                s = load(path)
        _cache[path] = s
        return s


func play_music(music_name: String) -> void:
        if current_music == music_name and music_player.playing:
                return
        current_music = music_name
        var s := _get_stream(MUSIC_DIR + music_name + ".wav")
        if s == null:
                return
        music_player.stream = s
        music_player.play()


func _on_music_finished() -> void:
        if current_music != "":
                music_player.play()


func stop_music() -> void:
        current_music = ""
        music_player.stop()


func play_sfx(sfx_name: String) -> void:
        var s := _get_stream(SFX_DIR + sfx_name + ".wav")
        if s == null:
                return
        for p in sfx_players:
                if not p.playing:
                        p.stream = s
                        p.play()
                        return
        sfx_players[0].stream = s
        sfx_players[0].play()


func _to_db(v: float, muted: bool) -> float:
        if muted or v <= 0.001:
                return -80.0
        return linear_to_db(v)


func _apply_volumes() -> void:
        music_player.volume_db = _to_db(SaveManager.music_volume, SaveManager.music_muted)
        for p in sfx_players:
                p.volume_db = _to_db(SaveManager.sfx_volume, SaveManager.sfx_muted)


func set_music_volume(v: float) -> void:
        SaveManager.music_volume = clampf(v, 0.0, 1.0)
        _apply_volumes()
        SaveManager.save_data()


func set_sfx_volume(v: float) -> void:
        SaveManager.sfx_volume = clampf(v, 0.0, 1.0)
        _apply_volumes()
        SaveManager.save_data()


func toggle_mute_music() -> void:
        SaveManager.music_muted = not SaveManager.music_muted
        _apply_volumes()
        SaveManager.save_data()


func toggle_mute_sfx() -> void:
        SaveManager.sfx_muted = not SaveManager.sfx_muted
        _apply_volumes()
        SaveManager.save_data()
'''

S["player/Player.gd"] = r'''extends CharacterBody2D
## Doguinho: state machine com 9 estados, pulo variavel e invencibilidade.

signal died

enum State { IDLE, WALK, RUN, JUMP, FALL, LAND, HURT, DEAD, VICTORY }

const ANIMS := {
        State.IDLE: "idle", State.WALK: "walk", State.RUN: "run", State.JUMP: "jump",
        State.FALL: "fall", State.LAND: "land", State.HURT: "hurt", State.DEAD: "death",
        State.VICTORY: "victory",
}

@export var speed: float = 200.0
@export var run_speed: float = 350.0
@export var jump_velocity: float = -550.0
@export var gravity: float = 1200.0
@export var max_fall_speed: float = 900.0
@export var acceleration: float = 2200.0
@export var invincibility_time: float = 1.5
@export var death_y: float = 900.0

var state: State = State.IDLE
var is_dead: bool = false
var is_invincible: bool = false
var max_lives: int = 3
var facing: int = 1
var coyote: float = 0.0
var jump_buffer: float = 0.0
var hurt_time: float = 0.0
var land_time: float = 0.0
var _was_on_floor: bool = true

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var invincibility_timer: Timer = $InvincibilityTimer


func _ready() -> void:
        add_to_group("player")
        max_lives = GameManager.MAX_LIVES
        invincibility_timer.one_shot = true
        invincibility_timer.wait_time = invincibility_time
        invincibility_timer.timeout.connect(_on_invincibility_timer_timeout)
        if GameManager.has_checkpoint:
                GameManager.respawn_player(self)
        sprite.play("idle")


func _physics_process(delta: float) -> void:
        if state == State.DEAD:
                velocity.y = minf(velocity.y + gravity * delta, max_fall_speed)
                position += velocity * delta
                return
        velocity.y = minf(velocity.y + gravity * delta, max_fall_speed)
        if state == State.VICTORY:
                velocity.x = 0.0
                move_and_slide()
                return
        if Input.is_action_just_pressed("restart"):
                GameManager.reset_level()
                return

        var on_floor := is_on_floor()
        coyote = 0.1 if on_floor else coyote - delta
        jump_buffer = 0.12 if Input.is_action_just_pressed("jump") else jump_buffer - delta
        var dir := Input.get_axis("move_left", "move_right")
        var running := Input.is_action_pressed("run")
        var target_speed := run_speed if running else speed

        if state == State.HURT:
                hurt_time -= delta
                if hurt_time <= 0.0:
                        state = State.IDLE
        else:
                velocity.x = move_toward(velocity.x, dir * target_speed, acceleration * delta)
                if dir != 0.0:
                        facing = 1 if dir > 0.0 else -1
                if jump_buffer > 0.0 and coyote > 0.0:
                        velocity.y = jump_velocity
                        jump_buffer = 0.0
                        coyote = 0.0
                        jump_effect()
        # pulo variavel: soltar o botao corta a subida
        if Input.is_action_just_released("jump") and velocity.y < 0.0:
                velocity.y *= 0.5

        move_and_slide()

        var now_floor := is_on_floor()
        if now_floor and not _was_on_floor:
                land_time = 0.1
        _was_on_floor = now_floor
        land_time -= delta
        _update_state(running, now_floor)
        _update_animation()
        if global_position.y > death_y:
                die()


func _update_state(running: bool, on_floor: bool) -> void:
        if state == State.HURT or state == State.DEAD or state == State.VICTORY:
                return
        if not on_floor:
                state = State.JUMP if velocity.y < 0.0 else State.FALL
        elif land_time > 0.0:
                state = State.LAND
        elif absf(velocity.x) > 10.0:
                state = State.RUN if running else State.WALK
        else:
                state = State.IDLE


func _update_animation() -> void:
        var anim: String = ANIMS[state]
        if sprite.animation != anim:
                sprite.play(anim)
        sprite.flip_h = facing < 0
        if is_invincible:
                sprite.modulate.a = 0.35 if (Time.get_ticks_msec() / 80) % 2 == 0 else 1.0
        else:
                sprite.modulate.a = 1.0


func take_damage(from_position = null) -> void:
        if is_dead or is_invincible or state == State.VICTORY:
                return
        AudioManager.play_sfx("hurt")
        if not GameManager.hurt():
                die(true)
                return
        state = State.HURT
        hurt_time = 0.35
        var kb := -facing
        if from_position is Vector2:
                kb = 1 if global_position.x >= from_position.x else -1
        velocity = Vector2(kb * 260.0, -320.0)
        is_invincible = true
        invincibility_timer.start(invincibility_time)
        _update_animation()


func die(life_already_lost: bool = false) -> void:
        if is_dead:
                return
        is_dead = true
        state = State.DEAD
        AudioManager.play_sfx("death")
        sprite.modulate.a = 1.0
        sprite.play("death")
        velocity = Vector2(0.0, -450.0)
        died.emit()
        await get_tree().create_timer(1.4).timeout
        GameManager.player_died(life_already_lost)


func bounce() -> void:
        velocity.y = jump_velocity * (0.9 if Input.is_action_pressed("jump") else 0.6)
        AudioManager.play_sfx("jump")


func win() -> void:
        state = State.VICTORY
        is_invincible = true
        sprite.modulate.a = 1.0
        sprite.play("victory")


func _on_invincibility_timer_timeout() -> void:
        is_invincible = false
        sprite.modulate.a = 1.0


func jump_effect() -> void:
        AudioManager.play_sfx("jump")
'''

S["enemies/Enemy.gd"] = r'''extends CharacterBody2D
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
var player: Node2D = null
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


func _get_player() -> Node2D:
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
        for body in hitbox.get_overlapping_bodies():
                if body.is_in_group("player"):
                        _on_player_collision(body)


func _on_player_collision(p) -> void:
        if is_dead or p.is_dead:
                return
        var stomp: bool = p.velocity.y > 0.0 and p.global_position.y < global_position.y - 12.0
        if stomp:
                p.bounce()
                if stompable:
                        take_damage()
        else:
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
'''

S["enemies/Slime.gd"] = r'''extends "res://scripts/enemies/Enemy.gd"
## Slime: patrulha e persegue o jogador quando ele chega a 150px.

enum AIState { PATROL, CHASE }

@export var chase_range: float = 150.0
@export var chase_speed: float = 120.0

var ai_state: AIState = AIState.PATROL


func _ai(_delta: float) -> void:
        var p := _get_player()
        ai_state = AIState.PATROL
        if p and not p.is_dead:
                if absf(p.global_position.x - global_position.x) < chase_range and absf(p.global_position.y - global_position.y) < 90.0:
                        ai_state = AIState.CHASE
        if ai_state == AIState.CHASE:
                direction = 1 if p.global_position.x > global_position.x else -1
                velocity.x = 0.0 if _edge_ahead_missing() else direction * chase_speed
                sprite.flip_h = direction > 0
        else:
                velocity.x = direction * speed
                flip_on_wall()
'''

S["enemies/TurtleEnemy.gd"] = r'''extends "res://scripts/enemies/Enemy.gd"
## Tartaruga: entra no casco (invulneravel) quando o jogador chega perto.
## Sai do casco depois de 3s com um pulinho surpresa na direcao do jogador.

enum TState { WALK, SHELL }

@export var shell_range: float = 80.0
@export var shell_duration: float = 3.0

var t_state: TState = TState.WALK
var shell_timer: float = 0.0
var cooldown: float = 0.0


func _ai(delta: float) -> void:
        cooldown -= delta
        var p := _get_player()
        if t_state == TState.WALK:
                velocity.x = direction * speed
                flip_on_wall()
                if cooldown <= 0.0 and p and not p.is_dead and global_position.distance_to(p.global_position) < shell_range:
                        t_state = TState.SHELL
                        shell_timer = shell_duration
                        stompable = false
                        sprite.play("shell")
        else:
                velocity.x = 0.0
                shell_timer -= delta
                if shell_timer <= 0.0:
                        t_state = TState.WALK
                        stompable = true
                        cooldown = 1.5
                        sprite.play("walk")
                        if p:
                                direction = 1 if p.global_position.x > global_position.x else -1
                        velocity.y = -280.0
                        AudioManager.play_sfx("trap")
'''

S["enemies/BirdEnemy.gd"] = r'''extends "res://scripts/enemies/Enemy.gd"
## Passaro: patrulha no ar e mergulha quando ve o jogador abaixo.

enum BState { PATROL, DIVE, RETURN }

@export var patrol_distance: float = 150.0
@export var dive_speed: float = 380.0
@export var detect_range: float = 220.0

var b_state: BState = BState.PATROL
var origin: Vector2 = Vector2.ZERO
var t: float = 0.0
var dive_target: Vector2 = Vector2.ZERO


func _enemy_ready() -> void:
        use_gravity = false
        origin = global_position
        sprite.play("fly")


func _ai(delta: float) -> void:
        t += delta
        var p := _get_player()
        match b_state:
                BState.PATROL:
                        var tx := origin.x + sin(t * 1.2) * patrol_distance
                        var ty := origin.y + sin(t * 3.0) * 12.0
                        velocity = Vector2((tx - global_position.x) * 4.0, (ty - global_position.y) * 4.0)
                        if p and not p.is_dead:
                                var dx := absf(p.global_position.x - global_position.x)
                                var dy: float = p.global_position.y - global_position.y
                                if dx < detect_range * 0.5 and dy > 40.0 and dy < detect_range * 1.5:
                                        b_state = BState.DIVE
                                        dive_target = p.global_position
                                        sprite.play("dive")
                BState.DIVE:
                        var to := dive_target - global_position
                        if to.length() < 12.0:
                                b_state = BState.RETURN
                                sprite.play("fly")
                        else:
                                velocity = to.normalized() * dive_speed
                BState.RETURN:
                        var back := origin - global_position
                        if back.length() < 10.0:
                                b_state = BState.PATROL
                        else:
                                velocity = back.normalized() * speed * 2.0
        if absf(velocity.x) > 1.0:
                sprite.flip_h = velocity.x > 0.0
'''

S["enemies/GhostDog.gd"] = r'''extends "res://scripts/enemies/Enemy.gd"
## Cachorro fantasma: flutua (seno), atravessa paredes e persegue o jogador.

@export var float_amplitude: float = 20.0
@export var chase_speed: float = 70.0
@export var wake_range: float = 650.0

var t: float = 0.0


func _enemy_ready() -> void:
        use_gravity = false
        sprite.play("float")
        modulate.a = 0.8


func _ai(delta: float) -> void:
        t += delta
        var p := _get_player()
        velocity = Vector2(0.0, cos(t * 3.0) * float_amplitude * 3.0)
        if p and not p.is_dead:
                var to: Vector2 = p.global_position - global_position
                if to.length() < wake_range and to.length() > 4.0:
                        velocity += to.normalized() * chase_speed
                        sprite.flip_h = to.x > 0.0
'''

S["enemies/LivingSpike.gd"] = r'''extends Area2D
## Espinho vivo: escondido ate o jogador chegar a 100px, entao surge e ataca.

@export var detect_range: float = 100.0

var spike_state: int = 0  # 0 = escondido, 1 = surgindo, 2 = atacando

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
        add_to_group("enemy")
        sprite.play("hidden")


func _physics_process(_delta: float) -> void:
        var p := get_tree().get_first_node_in_group("player") as Node2D
        if p == null:
                return
        if spike_state == 0 and global_position.distance_to(p.global_position) < detect_range:
                _appear()
        if spike_state == 2:
                for b in get_overlapping_bodies():
                        if b.is_in_group("player"):
                                b.take_damage(global_position)


func _appear() -> void:
        spike_state = 1
        sprite.play("appear")
        AudioManager.play_sfx("trap")
        await get_tree().create_timer(0.25).timeout
        if is_inside_tree():
                spike_state = 2
                sprite.play("attack")
'''

S["bosses/BossProjectile.gd"] = r'''extends Area2D
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


func _on_body_entered(body: Node) -> void:
        if body.is_in_group("player"):
                body.take_damage(global_position)
                queue_free()
'''

S["bosses/Boss.gd"] = r'''extends CharacterBody2D
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
var player: Node2D = null

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
        for body in hitbox.get_overlapping_bodies():
                if not body.is_in_group("player") or body.is_dead:
                        continue
                var stomp: bool = body.velocity.y > 0.0 and body.global_position.y < global_position.y - 20.0
                if stomp:
                        body.bounce()
                        take_damage()
                else:
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
'''

S["systems/Trap.gd"] = r'''extends Node2D
## Base das armadilhas: ativa quando o jogador chega perto (activation_range).

signal triggered

@export var activation_range: float = 100.0
@export var auto_activate: bool = true

var activated: bool = false
var player: Node2D = null


func _process(delta: float) -> void:
        if player == null or not is_instance_valid(player):
                player = get_tree().get_first_node_in_group("player") as Node2D
        if not activated and auto_activate and player and not player.is_dead and _should_activate(player):
                activate()
        _trap_process(delta)


func _physics_process(delta: float) -> void:
        _trap_physics(delta)


func _should_activate(p: Node2D) -> bool:
        return global_position.distance_to(p.global_position) < activation_range


func _trap_process(_delta: float) -> void:
        pass


func _trap_physics(_delta: float) -> void:
        pass


func activate() -> void:
        if activated:
                return
        activated = true
        triggered.emit()
        _on_activate()


func _on_activate() -> void:
        pass


func reset() -> void:
        activated = false
        _on_reset()


func _on_reset() -> void:
        pass


func _on_body_entered(body: Node) -> void:
        if body.is_in_group("player"):
                activate()


func _hurt_player_in(area: Area2D) -> void:
        for b in area.get_overlapping_bodies():
                if b.is_in_group("player"):
                        b.take_damage(area.global_position)


func _kill_player_in(area: Area2D) -> void:
        for b in area.get_overlapping_bodies():
                if b.is_in_group("player"):
                        b.die()


func _wait(seconds: float) -> void:
        var tm := Timer.new()
        tm.one_shot = true
        tm.wait_time = seconds
        add_child(tm)
        tm.start()
        await tm.timeout
        tm.queue_free()
'''

S["traps/FallingPlatform.gd"] = r'''extends "res://scripts/systems/Trap.gd"
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
'''

S["traps/FakePlatform.gd"] = r'''extends "res://scripts/systems/Trap.gd"
## Plataforma falsa: parece normal, some ao contato (collision_layer = 0).

@export var respawn_time: float = 4.0

@onready var body: StaticBody2D = $Body
@onready var detector: Area2D = $Body/Detector


func _ready() -> void:
        auto_activate = false
        detector.body_entered.connect(_on_body_entered)


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
'''

S["traps/MovingPlatform.gd"] = r'''extends "res://scripts/systems/Trap.gd"
## Plataforma que oscila entre point_a e point_b (lerp suave).

@export var point_a: Vector2 = Vector2.ZERO
@export var point_b: Vector2 = Vector2(200, 0)
@export var speed: float = 1.0

var t: float = 0.0

@onready var body: AnimatableBody2D = $Body


func _ready() -> void:
        auto_activate = false
        body.position = point_a


func _trap_physics(delta: float) -> void:
        t += delta * speed
        var w := (sin(t - PI / 2.0) + 1.0) * 0.5
        body.position = point_a.lerp(point_b, w)
'''

S["traps/HiddenSpike.gd"] = r'''extends "res://scripts/systems/Trap.gd"
## Espinhos invisiveis (modulate.a = 0) que surgem quando o jogador entra na zona.

@export var width: float = 64.0

@onready var spikes: Area2D = $Spikes


func _ready() -> void:
        spikes.modulate.a = 0.0


func _should_activate(p: Node2D) -> bool:
        return absf(p.global_position.x - (global_position.x + width / 2.0)) < activation_range and absf(p.global_position.y - global_position.y) < 120.0


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        spikes.position.y = 16.0
        var tw := create_tween().set_parallel(true)
        tw.tween_property(spikes, "modulate:a", 1.0, 0.08)
        tw.tween_property(spikes, "position:y", 0.0, 0.08)


func _trap_physics(_delta: float) -> void:
        if activated and spikes.modulate.a > 0.5:
                _hurt_player_in(spikes)
'''

S["traps/InvisibleBlock.gd"] = r'''extends "res://scripts/systems/Trap.gd"
## Bloco invisivel: aparece quando o jogador pula por baixo dele (bate a cabeca!).

@onready var block: StaticBody2D = $Block


func _ready() -> void:
        block.modulate.a = 0.0
        block.collision_layer = 0


func _should_activate(p: Node2D) -> bool:
        var c := global_position + Vector2(32, 32)
        return absf(p.global_position.x - c.x) < 44.0 and p.global_position.y > c.y and p.global_position.y - c.y < 150.0 and p.velocity.y < 0.0


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        block.collision_layer = 1
        var tw := create_tween()
        tw.tween_property(block, "modulate:a", 1.0, 0.1)
        tw.tween_property(block, "position:y", -6.0, 0.05)
        tw.tween_property(block, "position:y", 0.0, 0.05)
'''

S["traps/ExplosiveCoin.gd"] = r'''extends "res://scripts/systems/Trap.gd"
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
        for b in area.get_overlapping_bodies():
                if b.is_in_group("player"):
                        b.take_damage(global_position)
        await _wait(0.6)
        queue_free()
'''

S["traps/FallingCeiling.gd"] = r'''extends "res://scripts/systems/Trap.gd"
## Bloco do teto que cai quando o jogador passa embaixo.

@export var fall_distance: float = 400.0

var falling: bool = false
var fall_speed: float = 0.0
var start_pos: Vector2

@onready var block: Area2D = $Block


func _ready() -> void:
        start_pos = block.position


func _should_activate(p: Node2D) -> bool:
        return absf(p.global_position.x - (global_position.x + 32.0)) < 60.0 and p.global_position.y > global_position.y


func _on_activate() -> void:
        AudioManager.play_sfx("trap")
        var tw := create_tween()
        for i in 4:
                tw.tween_property(block, "position:x", start_pos.x + (2.0 if i % 2 == 0 else -2.0), 0.05)
        tw.tween_property(block, "position:x", start_pos.x, 0.01)
        await tw.finished
        falling = true


func _trap_physics(delta: float) -> void:
        if not falling:
                return
        fall_speed += 1500.0 * delta
        block.position.y += fall_speed * delta
        _hurt_player_in(block)
        if block.position.y >= start_pos.y + fall_distance:
                block.position.y = start_pos.y + fall_distance
                falling = false
                _land()


func _land() -> void:
        AudioManager.play_sfx("boss_hurt")
        await _wait(1.5)
        var tw := create_tween()
        tw.tween_property(block, "modulate:a", 0.0, 0.4)
        await tw.finished
        await _wait(1.5)
        reset()


func _on_reset() -> void:
        fall_speed = 0.0
        block.position = start_pos
        block.modulate.a = 1.0
'''

S["traps/ClosingWall.gd"] = r'''extends "res://scripts/systems/Trap.gd"
## Parede esmagadora: ao acionar, fecha (desce) e reabre em ciclos.

@export var close_distance: float = 300.0
@export var cycle_time: float = 2.4

@onready var wall: Area2D = $Wall


func _should_activate(p: Node2D) -> bool:
        return absf(p.global_position.x - (global_position.x + 32.0)) < activation_range


func _on_activate() -> void:
        while is_inside_tree():
                AudioManager.play_sfx("trap")
                var tw := create_tween()
                tw.tween_property(wall, "position:y", close_distance, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
                await tw.finished
                await _wait(0.6)
                var tw2 := create_tween()
                tw2.tween_property(wall, "position:y", 0.0, 0.9)
                await tw2.finished
                await _wait(cycle_time * 0.5)


func _trap_physics(_delta: float) -> void:
        if activated and wall.position.y > close_distance * 0.5:
                _hurt_player_in(wall)
'''

S["traps/DisappearingFloor.gd"] = r'''extends "res://scripts/systems/Trap.gd"
## Chao que desaparece em sequencia quando o jogador pisa nele.

@export var count: int = 6
@export var block_size: float = 64.0
@export var delay: float = 0.35
@export var reset_time: float = 4.0
@export var tile_texture: Texture2D

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
                        s.modulate = Color(1, 0.85, 0.85)
                        b.add_child(s)
                add_child(b)
                blocks.append(b)


func _should_activate(p: Node2D) -> bool:
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
'''

S["systems/Checkpoint.gd"] = r'''extends Area2D
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


func _on_body_entered(body: Node) -> void:
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
                        var slime := scene.instantiate()
                        slime.position = position + Vector2(160, -24)
                        get_parent().add_child.call_deferred(slime)
                        AudioManager.play_sfx("trap")
'''

S["systems/Coin.gd"] = r'''extends Area2D
## Moeda: +100 pontos.

@export var value: int = 100

var collected: bool = false

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
        sprite.play("spin")
        body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
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
'''

S["systems/Level.gd"] = r'''extends Node2D
## Script raiz de cada fase: camera, musica, ligacao chefe -> saida.

@export var level_number: int = 1
@export var level_width: int = 3000
@export var music_name: String = "level1"
@export var death_y: float = 850.0


func _ready() -> void:
        GameManager.on_level_started(level_number)
        AudioManager.play_music(music_name)
        var player := get_node_or_null("Player")
        if player:
                player.death_y = death_y
                var cam := player.get_node_or_null("Camera2D") as Camera2D
                if cam:
                        cam.limit_left = 0
                        cam.limit_top = 0
                        cam.limit_right = level_width
                        cam.limit_bottom = 720
        var boss := get_node_or_null("Boss")
        var exit_area := get_node_or_null("LevelEnd")
        if boss and exit_area:
                exit_area.set_locked(true)
                boss.boss_defeated.connect(exit_area.unlock)
'''

S["systems/LevelEnd.gd"] = r'''extends Area2D
## Saida da fase: ao tocar, completa a fase (bloqueada ate derrotar o chefe no nivel 3).

@export var locked: bool = false

var done: bool = false

@onready var flag: Node2D = $Flag
@onready var hint: Label = $Hint


func _ready() -> void:
        body_entered.connect(_on_body_entered)
        set_locked(locked)


func set_locked(v: bool) -> void:
        locked = v
        if not is_node_ready():
                return
        flag.modulate = Color(0.4, 0.4, 0.4, 0.6) if locked else Color.WHITE
        hint.visible = locked


func unlock() -> void:
        set_locked(false)
        AudioManager.play_sfx("checkpoint")


func _on_body_entered(body: Node) -> void:
        if done or locked or not body.is_in_group("player") or body.is_dead:
                return
        done = true
        body.win()
        GameManager.complete_level()
'''

S["systems/Lava.gd"] = r'''extends Area2D
## Lava: morte instantanea.

@onready var visual: Sprite2D = $Sprite2D


func _ready() -> void:
        body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
        var r := visual.region_rect
        r.position.x = fmod(r.position.x + delta * 12.0, 128.0)
        visual.region_rect = r


func _on_body_entered(body: Node) -> void:
        if body.is_in_group("player"):
                body.die()
'''

S["systems/Main.gd"] = r'''extends Node
## Cena raiz: abre o menu principal.


func _ready() -> void:
        get_tree().change_scene_to_file.call_deferred("res://scenes/menus/Menu.tscn")
'''

S["ui/UIBuilder.gd"] = r'''extends RefCounted
## Funcoes utilitarias para montar interfaces via codigo.


static func button(text: String, cb: Callable, font_size: int = 28) -> Button:
        var b := Button.new()
        b.text = text
        b.custom_minimum_size = Vector2(360, 56)
        b.add_theme_font_size_override("font_size", font_size)
        b.pressed.connect(cb)
        return b


static func label(text: String, font_size: int = 32, color: Color = Color.WHITE) -> Label:
        var l := Label.new()
        l.text = text
        l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        l.add_theme_font_size_override("font_size", font_size)
        l.add_theme_color_override("font_color", color)
        l.add_theme_color_override("font_outline_color", Color.BLACK)
        l.add_theme_constant_override("outline_size", 8)
        return l


static func centered_vbox(parent: Node, separation: int = 14) -> VBoxContainer:
        var center := CenterContainer.new()
        center.set_anchors_preset(Control.PRESET_FULL_RECT)
        parent.add_child(center)
        var v := VBoxContainer.new()
        v.alignment = BoxContainer.ALIGNMENT_CENTER
        v.add_theme_constant_override("separation", separation)
        center.add_child(v)
        return v
'''

UIB = 'const UI := preload("res://scripts/ui/UIBuilder.gd")\n'

S["ui/HUD.gd"] = r'''extends CanvasLayer
## HUD: vidas, pontos, fase, tempo, mortes e botao de pausa.

''' + UIB + r'''
var hearts: Array[TextureRect] = []
var score_label: Label
var level_label: Label
var time_label: Label
var deaths_label: Label
var heart_tex: Texture2D
var heart_empty_tex: Texture2D


func _ready() -> void:
        heart_tex = load("res://assets/sprites/ui/heart.png")
        heart_empty_tex = load("res://assets/sprites/ui/heart_empty.png")
        var bar := HBoxContainer.new()
        bar.position = Vector2(16, 12)
        bar.add_theme_constant_override("separation", 28)
        add_child(bar)
        var hbox := HBoxContainer.new()
        bar.add_child(hbox)
        for i in GameManager.MAX_LIVES:
                var tr := TextureRect.new()
                tr.texture = heart_tex
                tr.custom_minimum_size = Vector2(36, 36)
                tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
                tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
                hbox.add_child(tr)
                hearts.append(tr)
        score_label = UI.label("", 26)
        level_label = UI.label("", 26, Color(1, 0.9, 0.4))
        time_label = UI.label("", 26)
        deaths_label = UI.label("", 26, Color(1, 0.6, 0.6))
        for l in [score_label, level_label, time_label, deaths_label]:
                bar.add_child(l)
        var pause_btn := Button.new()
        pause_btn.text = " II "
        pause_btn.add_theme_font_size_override("font_size", 26)
        pause_btn.position = Vector2(1200, 10)
        pause_btn.focus_mode = Control.FOCUS_NONE
        pause_btn.pressed.connect(_on_pause_pressed)
        add_child(pause_btn)
        GameManager.lives_changed.connect(_on_lives_changed)
        GameManager.score_changed.connect(_on_score_changed)
        GameManager.deaths_changed.connect(_on_deaths_changed)
        _on_lives_changed(GameManager.lives)
        _on_score_changed(GameManager.score)
        _on_deaths_changed(GameManager.deaths)
        level_label.text = "FASE %d" % GameManager.current_level


func _process(_delta: float) -> void:
        time_label.text = "TEMPO " + GameManager.format_time(GameManager.level_time)
        level_label.text = "FASE %d" % GameManager.current_level


func _on_lives_changed(lives: int) -> void:
        for i in hearts.size():
                hearts[i].texture = heart_tex if i < lives else heart_empty_tex


func _on_score_changed(score: int) -> void:
        score_label.text = "PONTOS %06d" % score


func _on_deaths_changed(deaths: int) -> void:
        deaths_label.text = "MORTES %d" % deaths


func _on_pause_pressed() -> void:
        var pm := get_tree().get_first_node_in_group("pause_menu")
        if pm:
                pm.toggle()
'''

S["ui/PauseMenu.gd"] = r'''extends CanvasLayer
## Menu de pausa (ESC): Continuar, Reiniciar, Menu Principal.

''' + UIB + r'''
var root: Control


func _ready() -> void:
        add_to_group("pause_menu")
        process_mode = Node.PROCESS_MODE_ALWAYS
        layer = 20
        root = Control.new()
        root.set_anchors_preset(Control.PRESET_FULL_RECT)
        add_child(root)
        var dim := ColorRect.new()
        dim.color = Color(0, 0, 0, 0.6)
        dim.set_anchors_preset(Control.PRESET_FULL_RECT)
        root.add_child(dim)
        var v := UI.centered_vbox(root)
        v.add_child(UI.label("PAUSADO", 64, Color(1, 0.85, 0.3)))
        v.add_child(UI.button("Continuar", toggle))
        v.add_child(UI.button("Reiniciar Fase", _on_restart))
        v.add_child(UI.button("Menu Principal", _on_menu))
        visible = false


func _unhandled_input(event: InputEvent) -> void:
        if event.is_action_pressed("pause"):
                toggle()
                get_viewport().set_input_as_handled()


func toggle() -> void:
        visible = not visible
        get_tree().paused = visible


func _on_restart() -> void:
        get_tree().paused = false
        GameManager.reset_level()


func _on_menu() -> void:
        GameManager.go_to_menu()
'''

S["ui/TouchControls.gd"] = r'''extends CanvasLayer
## Controles virtuais para telas touch (Input.action_press / action_release).

@export var force_visible: bool = false

const BUTTONS := [
        ["left", "move_left", Vector2(40, 590)],
        ["right", "move_right", Vector2(170, 590)],
        ["run", "run", Vector2(1010, 590)],
        ["jump", "jump", Vector2(1140, 560)],
        ["pause", "pause", Vector2(1180, 70)],
]


func _ready() -> void:
        layer = 15
        visible = force_visible or DisplayServer.is_touchscreen_available()
        if not visible:
                return
        for data in BUTTONS:
                var b := TouchScreenButton.new()
                b.texture_normal = load("res://assets/sprites/ui/btn_%s.png" % data[0])
                b.position = data[2]
                b.modulate.a = 0.75
                b.pressed.connect(_press.bind(data[1]))
                b.released.connect(_release.bind(data[1]))
                add_child(b)


func _press(action: String) -> void:
        if action == "pause":
                var ev := InputEventAction.new()
                ev.action = "pause"
                ev.pressed = true
                Input.parse_input_event(ev)
                return
        Input.action_press(action)


func _release(action: String) -> void:
        if action != "pause":
                Input.action_release(action)
'''

S["ui/MainMenu.gd"] = r'''extends Control
## Menu principal com Doguinho animado correndo.

''' + UIB + r'''
@onready var dog: AnimatedSprite2D = $Dog


func _ready() -> void:
        get_tree().paused = false
        AudioManager.play_music("menu")
        var v := UI.centered_vbox(self, 12)
        var logo := TextureRect.new()
        logo.texture = load("res://assets/sprites/ui/logo.png")
        logo.custom_minimum_size = Vector2(640, 160)
        logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        v.add_child(logo)
        v.add_child(UI.label("A Aventura Impossivel", 30, Color(1, 0.9, 0.5)))
        var play := UI.button("Jogar", _on_play)
        v.add_child(play)
        v.add_child(UI.button("Selecionar Fase", _goto.bind("res://scenes/menus/LevelSelect.tscn")))
        v.add_child(UI.button("Como Jogar", _goto.bind("res://scenes/menus/HowToPlay.tscn")))
        v.add_child(UI.button("Configuracoes", _goto.bind("res://scenes/menus/Settings.tscn")))
        v.add_child(UI.button("Creditos", _goto.bind("res://scenes/menus/Credits.tscn")))
        v.add_child(UI.button("Sair", get_tree().quit))
        play.grab_focus()
        dog.play("run")


func _process(delta: float) -> void:
        dog.position.x += 220.0 * delta
        if dog.position.x > 1340.0:
                dog.position.x = -60.0


func _on_play() -> void:
        GameManager.start_new_game(1)


func _goto(path: String) -> void:
        get_tree().change_scene_to_file(path)
'''

S["ui/LevelSelect.gd"] = r'''extends Control
## Selecao de fases: desbloqueio via SaveManager, mostra recordes.

''' + UIB + r'''

func _ready() -> void:
        var v := UI.centered_vbox(self, 16)
        v.add_child(UI.label("SELECIONE A FASE", 56, Color(1, 0.85, 0.3)))
        for i in range(1, 4):
                var unlocked := SaveManager.is_level_unlocked(i)
                var best_t := SaveManager.get_best_time(i)
                var info := "Recorde: %d pts | %s" % [SaveManager.get_best_score(i), GameManager.format_time(best_t) if best_t >= 0.0 else "--:--"]
                var text := "Fase %d - %s\n%s" % [i, GameManager.LEVEL_NAMES[i - 1], info if unlocked else "BLOQUEADA"]
                var b := UI.button(text, GameManager.start_new_game.bind(i), 22)
                b.custom_minimum_size = Vector2(560, 80)
                b.disabled = not unlocked
                v.add_child(b)
        v.add_child(UI.button("Voltar", GameManager.go_to_menu))
'''

S["ui/GameOver.gd"] = r'''extends Control
## Tela de Game Over.

''' + UIB + r'''

func _ready() -> void:
        AudioManager.stop_music()
        var v := UI.centered_vbox(self, 18)
        v.add_child(UI.label("GAME OVER", 80, Color(1, 0.25, 0.25)))
        v.add_child(UI.label("O Doguinho nao aguentou...", 30))
        v.add_child(UI.label("Mortes nesta partida: %d" % GameManager.deaths, 30, Color(1, 0.7, 0.7)))
        v.add_child(UI.label("Mortes totais: %d" % SaveManager.total_deaths, 26, Color(0.9, 0.9, 0.9)))
        var retry := UI.button("Tentar Novamente", GameManager.retry_level)
        v.add_child(retry)
        v.add_child(UI.button("Menu Principal", GameManager.go_to_menu))
        retry.grab_focus()
'''

S["ui/Victory.gd"] = r'''extends Control
## Tela de vitoria da fase.

''' + UIB + r'''

func _ready() -> void:
        AudioManager.play_music("victory")
        var lvl := GameManager.current_level
        var final := lvl >= GameManager.LEVELS.size()
        var v := UI.centered_vbox(self, 16)
        v.add_child(UI.label("VOCE ZEROU O JOGO!" if final else "FASE %d COMPLETA!" % lvl, 64, Color(1, 0.9, 0.3)))
        v.add_child(UI.label(GameManager.LEVEL_NAMES[lvl - 1], 28))
        v.add_child(UI.label("Pontuacao: %d" % GameManager.score, 34))
        v.add_child(UI.label("Tempo: %s" % GameManager.format_time(GameManager.last_level_time), 34))
        v.add_child(UI.label("Mortes: %d" % GameManager.deaths, 28, Color(1, 0.7, 0.7)))
        v.add_child(UI.label("Recorde: %d pts | %s" % [SaveManager.get_best_score(lvl), GameManager.format_time(SaveManager.get_best_time(lvl))], 24, Color(0.7, 1, 0.7)))
        var next := UI.button("Voltar ao Menu" if final else "Proxima Fase", GameManager.next_level)
        v.add_child(next)
        if not final:
                v.add_child(UI.button("Menu Principal", GameManager.go_to_menu))
        next.grab_focus()
'''

S["ui/Settings.gd"] = r'''extends Control
## Configuracoes: volume de musica/sfx e mudo.

''' + UIB + r'''

func _ready() -> void:
        var v := UI.centered_vbox(self, 14)
        v.add_child(UI.label("CONFIGURACOES", 56, Color(1, 0.85, 0.3)))
        v.add_child(UI.label("Volume da Musica", 26))
        v.add_child(_slider(SaveManager.music_volume, AudioManager.set_music_volume))
        v.add_child(UI.label("Volume dos Efeitos", 26))
        v.add_child(_slider(SaveManager.sfx_volume, _on_sfx_changed))
        v.add_child(_toggle("Musica muda", SaveManager.music_muted, AudioManager.toggle_mute_music))
        v.add_child(_toggle("Efeitos mudos", SaveManager.sfx_muted, AudioManager.toggle_mute_sfx))
        v.add_child(UI.button("Voltar", GameManager.go_to_menu))


func _slider(value: float, cb: Callable) -> HSlider:
        var s := HSlider.new()
        s.min_value = 0.0
        s.max_value = 1.0
        s.step = 0.05
        s.value = value
        s.custom_minimum_size = Vector2(360, 32)
        s.value_changed.connect(cb)
        return s


func _toggle(text: String, pressed: bool, cb: Callable) -> CheckButton:
        var c := CheckButton.new()
        c.text = text
        c.button_pressed = pressed
        c.add_theme_font_size_override("font_size", 24)
        c.toggled.connect(func(_on: bool) -> void: cb.call())
        return c


func _on_sfx_changed(v: float) -> void:
        AudioManager.set_sfx_volume(v)
        AudioManager.play_sfx("coin")
'''

S["ui/InfoScreen.gd"] = r'''extends Control
## Telas de texto: Como Jogar e Creditos.

''' + UIB + r'''
@export_enum("howto", "credits") var mode: String = "howto"

const TEXTS := {
        "howto": ["COMO JOGAR", "A / D ou Setas  -  Andar\nW / Espaco / Seta Cima  -  Pular (segure para pular mais alto)\nShift  -  Correr\nEsc  -  Pausar      R  -  Reiniciar fase\n\nPule em cima dos inimigos para derrota-los.\nCuidado: NADA e o que parece! Moedas explodem,\nplataformas somem, checkpoints mentem...\nVoce tem 3 vidas. Boa sorte, Doguinho!"],
        "credits": ["CREDITOS", "DOG MARIO - A Aventura Impossivel\n\nTrabalho universitario de Desenvolvimento de Jogos\nEngine: Godot 4.x  |  Linguagem: GDScript 2.0\n\nArte: pixel art original gerada proceduralmente (Python + Pillow)\nAudio: sintese procedural em Python (struct + math)\n\nInspirado em Super Mario Bros e jogos 'troll' como Cat Mario.\nObrigado por jogar!"],
}


func _ready() -> void:
        var data: Array = TEXTS.get(mode, TEXTS["howto"])
        var v := UI.centered_vbox(self, 24)
        v.add_child(UI.label(data[0], 56, Color(1, 0.85, 0.3)))
        v.add_child(UI.label(data[1], 24))
        var back := UI.button("Voltar", GameManager.go_to_menu)
        v.add_child(back)
        back.grab_focus()
'''

import re
FIXES = [
    ("(body: Node)", "(body)"), ("(p: Node2D)", "(p)"),
    ("var player: Node2D = null", "var player = null"),
    ("func _get_player() -> Node2D:", "func _get_player():"),
    ("var p := _get_player()", "var p = _get_player()"),
    ("var slime := scene", "var slime = scene"),
    ('var player := get_node_or_null("Player")', 'var player = get_node_or_null("Player")'),
    ('var boss := get_node_or_null', 'var boss = get_node_or_null'),
    ('var exit_area := get_node_or_null', 'var exit_area = get_node_or_null'),
    ("var pm := ", "var pm = "),
]
for rel in list(S):
    code = S[rel]
    for a, b in FIXES:
        code = code.replace(a, b)
    # iterar sobre Array nao tipado (acesso dinamico a metodos do Player)
    code = re.sub(r'( +)for (\w+) in ([\w.]*get_overlapping_bodies\(\)):',
                  r'\1var _bodies: Array = \3\n\1for \2 in _bodies:', code)
    S[rel] = code

for rel, code in S.items():
    p = os.path.join(ROOT, "scripts", rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(code)
print(len(S), "scripts escritos")
