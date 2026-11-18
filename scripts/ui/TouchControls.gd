extends CanvasLayer
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
