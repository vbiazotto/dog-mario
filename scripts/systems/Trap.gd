extends Node2D
## Base das armadilhas: ativa quando o jogador chega perto (activation_range).

signal triggered

@export var activation_range: float = 100.0
@export var auto_activate: bool = true

var activated: bool = false
var player = null


func _process(delta: float) -> void:
        if player == null or not is_instance_valid(player):
                player = get_tree().get_first_node_in_group("player") as Node2D
        if not activated and auto_activate and player and not player.is_dead and _should_activate(player):
                activate()
        _trap_process(delta)


func _physics_process(delta: float) -> void:
        _trap_physics(delta)


func _should_activate(p) -> bool:
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


func _on_body_entered(body) -> void:
        if body.is_in_group("player"):
                activate()


func _hurt_player_in(area: Area2D) -> void:
        var _bodies: Array = area.get_overlapping_bodies()
        for b in _bodies:
                if b.is_in_group("player"):
                        b.take_damage(area.global_position)


func _kill_player_in(area: Area2D) -> void:
        var _bodies: Array = area.get_overlapping_bodies()
        for b in _bodies:
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
