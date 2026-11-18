extends Area2D
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


func _on_body_entered(body) -> void:
        if done or locked or not body.is_in_group("player") or body.is_dead:
                return
        done = true
        body.win()
        GameManager.complete_level()
