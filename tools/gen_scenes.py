"""Gera project.godot, todas as cenas .tscn (formato texto Godot 4) e assets auxiliares."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SP = "res://assets/sprites/"


def V(x, y):
    return f"Vector2({x}, {y})"


def q(s):
    return '"' + s.replace('"', '\\"') + '"'


class Scene:
    def __init__(self):
        self.ext, self.sub, self.nodes, self.extmap = [], [], [], {}

    def res(self, path, typ=None):
        if path not in self.extmap:
            if typ is None:
                typ = {"gd": "Script", "tscn": "PackedScene", "png": "Texture2D"}[path.rsplit(".", 1)[1]]
            rid = f"{len(self.ext) + 1}_r"
            self.ext.append((typ, path, rid))
            self.extmap[path] = f'ExtResource("{rid}")'
        return self.extmap[path]

    def subres(self, typ, props):
        rid = f"{typ}_{len(self.sub) + 1}"
        self.sub.append((typ, rid, props))
        return f'SubResource("{rid}")'

    def node(self, name, typ=None, parent=None, props=None, instance=None, groups=None):
        h = f'[node name="{name}"'
        if typ:
            h += f' type="{typ}"'
        if parent is not None:
            h += f' parent="{parent}"'
        if instance:
            h += f" instance={self.res(instance)}"
        if groups:
            h += " groups=[" + ", ".join(q(g) for g in groups) + "]"
        h += "]"
        self.nodes.append((h, props or {}))
        return name

    def save(self, rel):
        out = [f"[gd_scene load_steps={len(self.ext) + len(self.sub) + 1} format=3]", ""]
        for typ, path, rid in self.ext:
            out.append(f'[ext_resource type="{typ}" path="{path}" id="{rid}"]')
        out.append("")
        for typ, rid, props in self.sub:
            out.append(f'[sub_resource type="{typ}" id="{rid}"]')
            out += [f"{k} = {v}" for k, v in props.items()]
            out.append("")
        for h, props in self.nodes:
            out.append(h)
            out += [f"{k} = {v}" for k, v in props.items()]
            out.append("")
        p = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write("\n".join(out))


# ---------- helpers ----------
def frames(sc, anims):
    """anims: (name, png, fw, fh, indices, speed, loop)"""
    parts = []
    for name, png, fw, fh, idx, speed, loop in anims:
        tex = sc.res(SP + png)
        fr = []
        for i in idx:
            at = sc.subres("AtlasTexture", {"atlas": tex, "region": f"Rect2({i * fw}, 0, {fw}, {fh})"})
            fr.append('{\n"duration": 1.0,\n"texture": ' + at + "\n}")
        parts.append('{\n"frames": [' + ", ".join(fr) + '],\n"loop": ' + ("true" if loop else "false") +
                     f',\n"name": &"{name}",\n"speed": {speed}\n' + "}")
    return sc.subres("SpriteFrames", {"animations": "[" + ", ".join(parts) + "]"})


def rect(sc, w, h):
    return sc.subres("RectangleShape2D", {"size": V(w, h)})


def circle(sc, r):
    return sc.subres("CircleShape2D", {"radius": r})


def shape(sc, parent, w, h, pos=(0, 0), name="CollisionShape2D"):
    sc.node(name, "CollisionShape2D", parent, {"position": V(*pos), "shape": rect(sc, w, h)})


def anim_sprite(sc, parent, sf, anim, scale=2, name="AnimatedSprite2D", extra=None):
    p = {"scale": V(scale, scale), "sprite_frames": sf, "animation": f'&"{anim}"'}
    p.update(extra or {})
    sc.node(name, "AnimatedSprite2D", parent, p)


def region_sprite(sc, parent, png, w, h, scale=1, pos=(0, 0), name="Sprite2D", extra=None):
    p = {"position": V(*pos), "scale": V(scale, scale), "texture": sc.res(png), "centered": "false",
         "texture_repeat": 2, "region_enabled": "true", "region_rect": f"Rect2(0, 0, {w // scale}, {h // scale})"}
    p.update(extra or {})
    sc.node(name, "Sprite2D", parent, p)


AREA = {"collision_layer": 0, "collision_mask": 2}
FULL = {"anchors_preset": 15, "anchor_right": "1.0", "anchor_bottom": "1.0", "grow_horizontal": 2, "grow_vertical": 2}


def st(n, png, fw, fh, count, speed=8.0, loop=True, idx=None):
    return (n, png, fw, fh, idx if idx is not None else list(range(count)), speed, loop)


# ---------- assets auxiliares ----------
def make_aux_assets():
    for theme in ("grass", "forest", "castle"):
        ts = Image.open(f"{ROOT}/assets/sprites/environment/tileset_{theme}.png").convert("RGBA")
        ts.crop((32, 0, 64, 32)).save(f"{ROOT}/assets/sprites/environment/tile_{theme}_top.png")
        ts.crop((32, 32, 64, 64)).save(f"{ROOT}/assets/sprites/environment/tile_{theme}_fill.png")
    icons = {"left": "<", "right": ">", "jump": "^", "run": "R", "pause": "II"}
    for name in icons:
        size = 64 if name == "pause" else 110
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([2, 2, size - 3, size - 3], fill=(255, 255, 255, 90), outline=(255, 255, 255, 220), width=4)
        c, s = size / 2, size / 4
        if name == "left":
            d.polygon([(c - s, c), (c + s * 0.7, c - s), (c + s * 0.7, c + s)], fill=(255, 255, 255, 230))
        elif name == "right":
            d.polygon([(c + s, c), (c - s * 0.7, c - s), (c - s * 0.7, c + s)], fill=(255, 255, 255, 230))
        elif name == "jump":
            d.polygon([(c, c - s), (c - s, c + s * 0.7), (c + s, c + s * 0.7)], fill=(255, 255, 255, 230))
        elif name == "run":
            for k in (-1, 1):
                ox = k * s * 0.45
                d.polygon([(c + ox + s * 0.5, c), (c + ox - s * 0.4, c - s * 0.8), (c + ox - s * 0.4, c + s * 0.8)], fill=(255, 255, 255, 230))
        else:
            d.rectangle([c - s * 0.8, c - s, c - s * 0.25, c + s], fill=(255, 255, 255, 230))
            d.rectangle([c + s * 0.25, c - s, c + s * 0.8, c + s], fill=(255, 255, 255, 230))
        im.save(f"{ROOT}/assets/sprites/ui/btn_{name}.png")


# ---------- project.godot ----------
def key_event(code):
    return ('Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,'
            '"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,'
            f'"keycode":0,"physical_keycode":{code},"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)')


def project_godot():
    keys = {"move_left": [65, 4194319], "move_right": [68, 4194321], "jump": [87, 32, 4194320],
            "run": [4194325], "pause": [4194305], "restart": [82]}
    inp = []
    for act, codes in keys.items():
        inp.append(f'{act}={{\n"deadzone": 0.5,\n"events": [' + ", ".join(key_event(c) for c in codes) + "]\n}")
    txt = f'''; Engine configuration file.
; DOG MARIO - A Aventura Impossivel (Godot 4.x)

config_version=5

[application]

config/name="DOG MARIO - A Aventura Impossivel"
config/description="Plataforma 2D troll com o Doguinho."
run/main_scene="res://scenes/main/Main.tscn"
config/features=PackedStringArray("4.2")

[autoload]

SaveManager="*res://scripts/systems/SaveManager.gd"
GameManager="*res://scripts/systems/GameManager.gd"
AudioManager="*res://scripts/systems/AudioManager.gd"

[display]

window/size/viewport_width=1280
window/size/viewport_height=720
window/stretch/mode="canvas_items"
window/stretch/aspect="keep"

[input]

{chr(10).join(inp)}

[input_devices]

pointing/emulate_touch_from_mouse=false

[layer_names]

2d_physics/layer_1="world"
2d_physics/layer_2="player"
2d_physics/layer_3="enemies"

[rendering]

textures/canvas_textures/default_texture_filter=0
2d/snap/snap_2d_transforms_to_pixel=true
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
'''
    open(f"{ROOT}/project.godot", "w").write(txt)


# ---------- cenas simples ----------
def player_scene():
    sc = Scene()
    sc.node("Player", "CharacterBody2D", None, {"collision_layer": 2, "collision_mask": 1, "script": sc.res("res://scripts/player/Player.gd")})
    P = "player/doguinho_"
    sf = frames(sc, [st("idle", P + "idle.png", 32, 32, 4, 6), st("walk", P + "walk.png", 32, 32, 6, 10),
                     st("run", P + "run.png", 32, 32, 6, 14), st("jump", P + "jump.png", 32, 32, 2, 8),
                     st("fall", P + "fall.png", 32, 32, 2, 8), st("land", P + "land.png", 32, 32, 2, 16, False),
                     st("hurt", P + "hurt.png", 32, 32, 2, 10), st("death", P + "death.png", 32, 32, 4, 6, False),
                     st("victory", P + "victory.png", 32, 32, 4, 8)])
    anim_sprite(sc, ".", sf, "idle")
    shape(sc, ".", 34, 50, (0, 7))
    sc.node("InvincibilityTimer", "Timer", ".", {"wait_time": 1.5, "one_shot": "true"})
    sc.node("Camera2D", "Camera2D", ".", {"position": V(0, -60), "position_smoothing_enabled": "true", "position_smoothing_speed": 6.0})
    sc.save("scenes/player/Player.tscn")


def enemy_scene(name, script, anims, first, exports=None, body_mask=1, hit=(46, 42)):
    sc = Scene()
    p = {"collision_layer": 4, "collision_mask": body_mask, "script": sc.res(script)}
    p.update(exports or {})
    sc.node(name, "CharacterBody2D", None, p)
    anim_sprite(sc, ".", frames(sc, anims), first)
    shape(sc, ".", 36, 36, (0, 14))
    sc.node("Hitbox", "Area2D", ".", dict(AREA))
    shape(sc, "Hitbox", hit[0], hit[1], (0, 10))
    sc.save(f"scenes/enemies/{name}.tscn")


def enemies():
    E = "enemies/"
    enemy_scene("Slime", "res://scripts/enemies/Slime.gd",
                [st("walk", E + "slime.png", 32, 32, 4, 6), st("dead", E + "slime_dead.png", 32, 32, 2, 6, False)], "walk")
    enemy_scene("TurtleEnemy", "res://scripts/enemies/TurtleEnemy.gd",
                [st("walk", E + "turtle.png", 32, 32, 4, 6), st("shell", E + "turtle_shell.png", 32, 32, 2, 8)], "walk",
                {"speed": 60.0})
    enemy_scene("BirdEnemy", "res://scripts/enemies/BirdEnemy.gd",
                [st("fly", E + "bird.png", 32, 32, 4, 10), st("dive", E + "bird_dive.png", 32, 32, 2, 10)], "fly",
                {"use_gravity": "false", "avoid_edges": "false", "speed": 90.0}, body_mask=0)
    enemy_scene("GhostDog", "res://scripts/enemies/GhostDog.gd",
                [st("float", E + "ghost_dog.png", 32, 32, 4, 6)], "float",
                {"use_gravity": "false", "avoid_edges": "false", "health": 2, "score_value": 400}, body_mask=0)
    sc = Scene()
    sc.node("LivingSpike", "Area2D", None, dict(AREA, script=sc.res("res://scripts/enemies/LivingSpike.gd")))
    sf = frames(sc, [st("hidden", E + "spike_live.png", 32, 32, 1, 1, idx=[0]),
                     st("appear", E + "spike_live.png", 32, 32, 2, 10, False, idx=[1, 2]),
                     st("attack", E + "spike_live.png", 32, 32, 1, 4, idx=[3])])
    anim_sprite(sc, ".", sf, "hidden")
    shape(sc, ".", 40, 36, (0, 12))
    sc.save("scenes/enemies/LivingSpike.tscn")


def boss_scene():
    sc = Scene()
    sc.node("Boss", "CharacterBody2D", None, {"collision_layer": 4, "collision_mask": 0, "script": sc.res("res://scripts/bosses/Boss.gd")})
    B = "boss/boss_"
    sf = frames(sc, [st("idle", B + "idle.png", 64, 64, 4, 6), st("attack", B + "attack.png", 64, 64, 4, 10),
                     st("hurt", B + "hurt.png", 64, 64, 2, 8), st("death", B + "death.png", 64, 64, 4, 5, False)])
    anim_sprite(sc, ".", sf, "idle")
    shape(sc, ".", 90, 80, (0, 16))
    sc.node("Hitbox", "Area2D", ".", dict(AREA))
    shape(sc, "Hitbox", 96, 84, (0, 16))
    sc.node("BossUI", "CanvasLayer", ".", {"layer": 5})
    sc.node("NameLabel", "Label", "BossUI", {"offset_left": 340.0, "offset_top": 630.0, "offset_right": 940.0, "offset_bottom": 666.0,
                                             "theme_override_colors/font_outline_color": "Color(0, 0, 0, 1)",
                                             "theme_override_constants/outline_size": 8,
                                             "theme_override_font_sizes/font_size": 26,
                                             "text": q("CACHORRO MALDITO"), "horizontal_alignment": 1})
    bg = sc.subres("StyleBoxFlat", {"bg_color": "Color(0.15, 0.05, 0.1, 0.9)", "border_width_left": 3, "border_width_top": 3,
                                    "border_width_right": 3, "border_width_bottom": 3, "border_color": "Color(0, 0, 0, 1)"})
    fill = sc.subres("StyleBoxFlat", {"bg_color": "Color(0.85, 0.1, 0.2, 1)"})
    sc.node("HealthBar", "ProgressBar", "BossUI", {"offset_left": 340.0, "offset_top": 670.0, "offset_right": 940.0, "offset_bottom": 698.0,
                                                   "theme_override_styles/background": bg, "theme_override_styles/fill": fill,
                                                   "max_value": 10.0, "step": 1.0, "value": 10.0, "show_percentage": "false"})
    sc.save("scenes/bosses/Boss.tscn")


def canvas_scene(rel, name, script):
    sc = Scene()
    sc.node(name, "CanvasLayer", None, {"script": sc.res(script)})
    sc.save(rel)


def menu_scene(rel, name, script, bg="res://assets/sprites/ui/bg_menu.png", exports=None, dog=False):
    sc = Scene()
    p = dict(FULL)
    p["script"] = sc.res(script)
    p.update(exports or {})
    sc.node(name, "Control", None, p)
    sc.node("Background", "TextureRect", ".", dict(FULL, texture=sc.res(bg), expand_mode=1, stretch_mode=6))
    sc.node("Shade", "ColorRect", ".", dict(FULL, color="Color(0, 0, 0, 0.35)", mouse_filter=2))
    if dog:
        sf = frames(sc, [st("run", "player/doguinho_run.png", 32, 32, 6, 14)])
        anim_sprite(sc, ".", sf, "run", 3, "Dog", {"position": V(-60, 670)})
    sc.save(rel)


def trap_root(sc, name, script, pos_props=None):
    p = {"script": sc.res(script)}
    p.update(pos_props or {})
    sc.node(name, "Node2D", None, p)


def traps():
    T, S = SP + "traps/", "res://scripts/traps/"
    # FallingPlatform
    sc = Scene(); trap_root(sc, "FallingPlatform", S + "FallingPlatform.gd")
    sc.node("Body", "AnimatableBody2D", ".")
    region_sprite(sc, "Body", T + "platform_fall.png", 96, 32, 2)
    shape(sc, "Body", 96, 32, (48, 16))
    sc.node("Detector", "Area2D", "Body", dict(AREA))
    shape(sc, "Body/Detector", 88, 10, (48, -4))
    sc.save("scenes/traps/FallingPlatform.tscn")
    # FakePlatform
    sc = Scene(); trap_root(sc, "FakePlatform", S + "FakePlatform.gd")
    sc.node("Body", "StaticBody2D", ".")
    region_sprite(sc, "Body", SP + "environment/tile_grass_top.png", 96, 32)
    shape(sc, "Body", 96, 32, (48, 16))
    sc.node("Detector", "Area2D", "Body", dict(AREA))
    shape(sc, "Body/Detector", 88, 10, (48, -4))
    sc.save("scenes/traps/FakePlatform.tscn")
    # MovingPlatform
    sc = Scene(); trap_root(sc, "MovingPlatform", S + "MovingPlatform.gd")
    sc.node("Body", "AnimatableBody2D", ".")
    region_sprite(sc, "Body", T + "platform_move.png", 96, 32, 2)
    shape(sc, "Body", 96, 32, (48, 16))
    sc.save("scenes/traps/MovingPlatform.tscn")
    # HiddenSpike
    sc = Scene(); trap_root(sc, "HiddenSpike", S + "HiddenSpike.gd", {"activation_range": 50.0, "width": 96.0})
    sc.node("Spikes", "Area2D", ".", dict(AREA))
    region_sprite(sc, "Spikes", T + "spike.png", 96, 32, 2)
    shape(sc, "Spikes", 88, 22, (48, 20))
    sc.save("scenes/traps/HiddenSpike.tscn")
    # InvisibleBlock
    sc = Scene(); trap_root(sc, "InvisibleBlock", S + "InvisibleBlock.gd")
    sc.node("Block", "StaticBody2D", ".", {"collision_layer": 0})
    sc.node("Sprite2D", "Sprite2D", "Block", {"scale": V(2, 2), "texture": sc.res(T + "block_invisible.png"), "centered": "false"})
    shape(sc, "Block", 64, 64, (32, 32))
    sc.save("scenes/traps/InvisibleBlock.tscn")
    # ExplosiveCoin
    sc = Scene(); trap_root(sc, "ExplosiveCoin", S + "ExplosiveCoin.gd")
    sc.node("Area", "Area2D", ".", dict(AREA))
    anim_sprite(sc, "Area", frames(sc, [st("spin", "environment/coin_trap.png", 16, 16, 4, 8)]), "spin")
    sc.node("CollisionShape2D", "CollisionShape2D", "Area", {"shape": circle(sc, 14.0)})
    anim_sprite(sc, ".", frames(sc, [st("boom", "effects/poof.png", 32, 32, 4, 10, False)]), "boom", 3, "Explosion")
    sc.save("scenes/traps/ExplosiveCoin.tscn")
    # FallingCeiling
    sc = Scene(); trap_root(sc, "FallingCeiling", S + "FallingCeiling.gd")
    sc.node("Block", "Area2D", ".", dict(AREA))
    sc.node("Sprite2D", "Sprite2D", "Block", {"scale": V(2, 2), "texture": sc.res(T + "falling_block.png"), "centered": "false"})
    shape(sc, "Block", 60, 60, (32, 32))
    sc.save("scenes/traps/FallingCeiling.tscn")
    # ClosingWall
    sc = Scene(); trap_root(sc, "ClosingWall", S + "ClosingWall.gd", {"activation_range": 160.0})
    sc.node("Wall", "Area2D", ".", dict(AREA))
    sc.node("Sprite2D", "Sprite2D", "Wall", {"scale": V(2, 2), "texture": sc.res(T + "wall_close.png"), "centered": "false"})
    shape(sc, "Wall", 60, 124, (32, 64))
    sc.save("scenes/traps/ClosingWall.tscn")
    # DisappearingFloor
    sc = Scene(); trap_root(sc, "DisappearingFloor", S + "DisappearingFloor.gd",
                            {"tile_texture": sc.res(SP + "environment/tile_forest_top.png")})
    sc.save("scenes/traps/DisappearingFloor.tscn")


def systems():
    sc = Scene()
    sc.node("Checkpoint", "Area2D", None, dict(AREA, script=sc.res("res://scripts/systems/Checkpoint.gd")))
    sf = frames(sc, [st("inactive", "environment/checkpoint.png", 32, 48, 1, 1, idx=[0]),
                     st("active", "environment/checkpoint.png", 32, 48, 1, 1, idx=[1])])
    anim_sprite(sc, ".", sf, "inactive")
    shape(sc, ".", 40, 96)
    sc.save("scenes/systems/Checkpoint.tscn")

    sc = Scene()
    sc.node("Coin", "Area2D", None, dict(AREA, script=sc.res("res://scripts/systems/Coin.gd")))
    anim_sprite(sc, ".", frames(sc, [st("spin", "environment/coin.png", 16, 16, 4, 8)]), "spin")
    sc.node("CollisionShape2D", "CollisionShape2D", ".", {"shape": circle(sc, 14.0)})
    sc.save("scenes/systems/Coin.tscn")

    sc = Scene()
    sc.node("LevelEnd", "Area2D", None, dict(AREA, script=sc.res("res://scripts/systems/LevelEnd.gd")))
    shape(sc, ".", 64, 220, (0, -110))
    sc.node("Flag", "Node2D", ".")
    sc.node("Pole", "ColorRect", "Flag", {"offset_left": -3.0, "offset_top": -200.0, "offset_right": 3.0, "offset_bottom": 0.0,
                                          "color": "Color(0.9, 0.9, 0.9, 1)"})
    sc.node("Banner", "ColorRect", "Flag", {"offset_left": 3.0, "offset_top": -200.0, "offset_right": 63.0, "offset_bottom": -160.0,
                                            "color": "Color(1, 0.8, 0.1, 1)"})
    sc.node("Star", "Sprite2D", "Flag", {"position": V(33, -180), "scale": V(2, 2), "texture": sc.res(SP + "ui/star.png")})
    sc.node("Hint", "Label", ".", {"offset_left": -140.0, "offset_top": -260.0, "offset_right": 100.0, "offset_bottom": -230.0,
                                   "theme_override_colors/font_outline_color": "Color(0, 0, 0, 1)",
                                   "theme_override_constants/outline_size": 6,
                                   "text": q("Derrote o chefe!"), "horizontal_alignment": 1})
    sc.save("scenes/systems/LevelEnd.tscn")


# ---------- niveis ----------
GY = 600  # topo do chao


def level(n, width, theme, music, data):
    sc = Scene()
    sc.node(f"Level{n}", "Node2D", None, {"script": sc.res("res://scripts/systems/Level.gd"), "level_number": n,
                                         "level_width": width, "music_name": q(music), "death_y": 850.0})
    sc.node("ParallaxBackground", "ParallaxBackground", ".")
    sc.node("ParallaxLayer", "ParallaxLayer", "ParallaxBackground", {"motion_scale": V(0.3, 0.1), "motion_mirroring": V(1280, 0)})
    sc.node("Background", "Sprite2D", "ParallaxBackground/ParallaxLayer",
            {"texture": sc.res(f"res://assets/backgrounds/bg_level{n}.png"), "centered": "false"})
    if data.get("lava"):
        sc.node("Lava", "Area2D", ".", dict(AREA, position=V(0, 665), script=sc.res("res://scripts/systems/Lava.gd")))
        region_sprite(sc, "Lava", SP + "environment/lava.png", width, 60, 2)
        shape(sc, "Lava", width, 50, (width // 2, 35))
    sc.node("Platforms", "Node2D", ".")
    top, fill = SP + f"environment/tile_{theme}_top.png", SP + f"environment/tile_{theme}_fill.png"
    plats = [(x0, GY, x1 - x0, 160) for x0, x1 in data["ground"]] + [(x, y, w, 32) for x, y, w in data["floating"]]
    for i, (x, y, w, h) in enumerate(plats):
        nm = f"Platform{i}"
        sc.node(nm, "StaticBody2D", "Platforms", {"position": V(x, y)})
        shape(sc, f"Platforms/{nm}", w, h, (w // 2, h // 2))
        region_sprite(sc, f"Platforms/{nm}", top, w, 32, name="Top")
        if h > 32:
            region_sprite(sc, f"Platforms/{nm}", fill, w, h - 32, pos=(0, 32), name="Fill")
    for i, x in enumerate((-32, width)):  # paredes invisiveis nas bordas
        sc.node(f"Bound{i}", "StaticBody2D", "Platforms", {"position": V(x, -400)})
        shape(sc, f"Platforms/Bound{i}", 32, 2000, (16, 1000))
    counters = {}
    for scene_name, pos, props in data["objects"]:
        k = counters[scene_name] = counters.get(scene_name, 0) + 1
        nm = scene_name.split("/")[-1].replace(".tscn", "") + (str(k) if scene_name not in ("bosses/Boss.tscn", "systems/LevelEnd.tscn") else "")
        p = {"position": V(*pos)}
        p.update(props)
        sc.node(nm, None, ".", p, instance=f"res://scenes/{scene_name}")
    sc.node("Player", None, ".", {"position": V(100, 560)}, instance="res://scenes/player/Player.tscn")
    for ui in ("HUD", "PauseMenu", "TouchControls"):
        sc.node(ui, None, ".", instance=f"res://scenes/ui/{ui}.tscn")
    sc.save(f"scenes/levels/Level{n}.tscn")


def O(name, x, y, **props):
    return (name, (x, y), props)


def coins(*pts):
    return [O("systems/Coin.tscn", x, y) for x, y in pts]


def levels():
    E, T, Sy = "enemies/", "traps/", "systems/"
    level(1, 3000, "grass", "level1", {
        "ground": [(0, 700), (800, 1400), (1550, 2100), (2260, 3000)],
        "floating": [(350, 480, 128), (1000, 470, 128), (1180, 370, 128), (1750, 460, 160), (2500, 470, 128)],
        "objects": coins((380, 440), (420, 440), (460, 440), (900, 560), (1030, 430), (1070, 430), (1210, 330),
                         (1250, 330), (1800, 420), (1850, 420), (2550, 430), (2600, 560), (2700, 560))
        + [O(T + "ExplosiveCoin.tscn", 1290, 330), O(T + "ExplosiveCoin.tscn", 1950, 560), O(T + "ExplosiveCoin.tscn", 2800, 560),
           O(E + "Slime.tscn", 550, 568), O(E + "Slime.tscn", 1100, 568), O(E + "Slime.tscn", 1900, 568),
           O(T + "FakePlatform.tscn", 702, 600), O(T + "FakePlatform.tscn", 2680, 470),
           O(T + "FallingPlatform.tscn", 2132, 580), O(T + "HiddenSpike.tscn", 2380, 568),
           O(Sy + "Checkpoint.tscn", 1600, 552), O(Sy + "LevelEnd.tscn", 2900, 600)],
    })
    level(2, 3500, "forest", "level2", {
        "ground": [(0, 600), (700, 1000), (1384, 2000), (2450, 3500)],
        "floating": [(250, 480, 128), (420, 370, 128), (600, 270, 160), (1500, 470, 128), (2500, 460, 128),
                     (2660, 350, 128), (2820, 250, 128)],
        "objects": coins((280, 440), (450, 330), (630, 230), (670, 230), (710, 230), (1530, 430), (2540, 420),
                         (2700, 310), (2850, 210), (2890, 210), (3200, 560), (1150, 540))
        + [O(E + "TurtleEnemy.tscn", 850, 568), O(E + "TurtleEnemy.tscn", 1650, 568), O(E + "TurtleEnemy.tscn", 3100, 568),
           O(E + "BirdEnemy.tscn", 1200, 280), O(E + "BirdEnemy.tscn", 2200, 300), O(E + "BirdEnemy.tscn", 3000, 280),
           O(E + "LivingSpike.tscn", 1900, 568),
           O(T + "DisappearingFloor.tscn", 1000, 600),
           O(T + "MovingPlatform.tscn", 2030, 570, point_b=V(300, 0), speed=1.2),
           O(T + "InvisibleBlock.tscn", 2950, 430),
           O(T + "HiddenSpike.tscn", 2600, 568), O(T + "HiddenSpike.tscn", 3250, 568),
           O(T + "ExplosiveCoin.tscn", 2930, 210),
           O(Sy + "Checkpoint.tscn", 1750, 552), O(Sy + "LevelEnd.tscn", 3400, 600)],
    })
    level(3, 4000, "castle", "level3", {
        "lava": True,
        "ground": [(0, 600), (700, 1100), (1220, 1700), (1820, 2300), (2420, 2900), (3020, 4000)],
        "floating": [(3500, 470, 128), (3820, 470, 128)],
        "objects": coins((300, 560), (800, 560), (1300, 560), (2000, 560), (2600, 560), (3100, 560))
        + [O(T + "ClosingWall.tscn", 900, 200, close_distance=272.0), O(T + "ClosingWall.tscn", 2100, 200, close_distance=272.0),
           O(T + "FallingCeiling.tscn", 1450, 150, fall_distance=386.0), O(T + "FallingCeiling.tscn", 2650, 150, fall_distance=386.0),
           O(E + "GhostDog.tscn", 1600, 350), O(E + "GhostDog.tscn", 2750, 350),
           O(E + "LivingSpike.tscn", 1000, 568), O(E + "Slime.tscn", 2550, 568),
           O(T + "HiddenSpike.tscn", 1950, 568), O(T + "ExplosiveCoin.tscn", 3200, 560),
           O(Sy + "Checkpoint.tscn", 2480, 552),
           O("bosses/Boss.tscn", 3700, 380), O(Sy + "LevelEnd.tscn", 3960, 600)],
    })


def main_scene():
    sc = Scene()
    sc.node("Main", "Node", None, {"script": sc.res("res://scripts/systems/Main.gd")})
    sc.save("scenes/main/Main.tscn")


if __name__ == "__main__":
    make_aux_assets()
    project_godot()
    player_scene(); enemies(); boss_scene(); traps(); systems()
    canvas_scene("scenes/ui/HUD.tscn", "HUD", "res://scripts/ui/HUD.gd")
    canvas_scene("scenes/ui/PauseMenu.tscn", "PauseMenu", "res://scripts/ui/PauseMenu.gd")
    canvas_scene("scenes/ui/TouchControls.tscn", "TouchControls", "res://scripts/ui/TouchControls.gd")
    U = "res://scripts/ui/"
    menu_scene("scenes/menus/Menu.tscn", "Menu", U + "MainMenu.gd", dog=True)
    menu_scene("scenes/menus/LevelSelect.tscn", "LevelSelect", U + "LevelSelect.gd")
    menu_scene("scenes/menus/HowToPlay.tscn", "HowToPlay", U + "InfoScreen.gd", exports={"mode": q("howto")})
    menu_scene("scenes/menus/Credits.tscn", "Credits", U + "InfoScreen.gd", exports={"mode": q("credits")})
    menu_scene("scenes/menus/Settings.tscn", "Settings", U + "Settings.gd")
    menu_scene("scenes/menus/GameOver.tscn", "GameOver", U + "GameOver.gd", bg="res://assets/backgrounds/bg_level3.png")
    menu_scene("scenes/menus/Victory.tscn", "Victory", U + "Victory.gd", bg="res://assets/backgrounds/bg_level1.png")
    levels(); main_scene()
    print("cenas geradas")
