extends RefCounted
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
