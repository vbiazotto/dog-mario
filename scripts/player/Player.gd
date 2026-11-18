extends CharacterBody2D
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
# Pulo maximo de ~176 px: alcanca todas as plataformas das fases.
@export var jump_velocity: float = -640.0
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
## Janela curta apos pisar num inimigo: impede que o contato do proprio
## inimigo (no frame seguinte ao quique) cause dano ao jogador.
const STOMP_GRACE_TIME := 0.2
var stomp_grace: float = 0.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var invincibility_timer: Timer = $InvincibilityTimer


func _ready() -> void:
        add_to_group("player")
        # Fisica de chao: mantem os pes "grudados" no piso.
        up_direction = Vector2.UP
        floor_stop_on_slope = true
        floor_constant_speed = true
        floor_max_angle = deg_to_rad(45.0)
        floor_snap_length = 8.0
        safe_margin = 0.04
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
        if stomp_grace > 0.0:
                stomp_grace -= delta
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

        # Durante a subida o snap precisa ser desligado, senao o pulo "gruda" no chao.
        floor_snap_length = 0.0 if velocity.y < 0.0 else 8.0
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
        stomp_grace = STOMP_GRACE_TIME
        coyote = 0.0
        AudioManager.play_sfx("jump")


func is_stomping() -> bool:
        return stomp_grace > 0.0


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
