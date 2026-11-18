# 🐶 DOG MARIO — A Aventura Impossível

Jogo de plataforma 2D no estilo *Super Mario* com pitadas de jogos "troll" (como *Cat Mario*), feito em **Godot 4.x** com **GDScript 2.0**. Você controla o **Doguinho** em 3 fases cheias de armadilhas onde *nada é o que parece*: moedas explodem, plataformas somem, blocos invisíveis surgem do nada e até o checkpoint pode ser uma cilada!

---

## ▶️ Como abrir na Godot 4.x

1. Baixe a Godot **4.2 ou superior** (versão padrão, não precisa ser .NET): https://godotengine.org/download
2. Extraia o arquivo `dog_mario_completo.zip`.
3. Abra a Godot → no Gerenciador de Projetos clique em **Importar** (*Import*) → selecione o arquivo `project.godot` dentro da pasta `dog_mario`.
4. Clique em **Importar e Editar**. Na primeira abertura a Godot importa automaticamente sprites e áudios (pode levar alguns segundos).
5. Pressione **F5** (ou o botão ▶ *Run Project*) para jogar.

> Testado com Godot 4.3 (modo headless): o projeto importa e as cenas rodam sem erros de script.

---

## 🎮 Controles

### Teclado
| Ação | Tecla |
|---|---|
| Andar | **A / D** ou **← / →** |
| Pular (segure para pular mais alto) | **W**, **Espaço** ou **↑** |
| Correr | **Shift** |
| Pausar | **Esc** |
| Reiniciar fase | **R** |

### Mobile (touch)
Os controles virtuais aparecem automaticamente em telas touch (`DisplayServer.is_touchscreen_available()`):
- **◀ ▶** no canto inferior esquerdo — andar
- **R** (correr) e **▲** (pular) no canto inferior direito
- **II** no topo direito — pausar

---

## 🗺️ Fases

1. **Campo da Falsa Tranquilidade** (3000 px) — campo verde aparentemente inocente: 3 Slimes perseguidores, ponte falsa sobre um buraco, plataforma que cai, moedas explosivas, espinhos escondidos e um checkpoint (x≈1600).
2. **Floresta das Armadilhas** (3500 px) — mais vertical: Tartarugas que se escondem no casco e saem de surpresa, Pássaros que mergulham, chão que desaparece em sequência, plataforma móvel sobre um abismo, bloco invisível, espinhos vivos/escondidos e checkpoint (x≈1750).
3. **Castelo do Cachorro Maldito** (4000 px) — lava no fundo, paredes esmagadoras, tetos que caem, Cachorros Fantasmas que atravessam tudo e a arena do **Chefe Final** (x 3400–4000). A saída só é liberada depois de derrotar o chefe.

---

## ✅ Funcionalidades implementadas

- **Player** com máquina de estados de 9 estados (IDLE, WALK, RUN, JUMP, FALL, LAND, HURT, DEAD, VICTORY), pulo variável, *coyote time*, *jump buffer*, knockback e invencibilidade temporária (piscando).
- **3 vidas**, contador de mortes, pontuação e cronômetro por fase.
- **5 inimigos**: Slime (patrulha/perseguição), Pássaro (patrulha + mergulho), Tartaruga (casco invulnerável + surpresa), Espinho Vivo (surge do chão), Cachorro Fantasma (flutua e atravessa paredes). Pule em cima para derrotá-los.
- **Chefe final** com barra de vida (10 HP), 2 fases (fica mais rápido e agressivo com 50% de HP) e 3 padrões de ataque: projéteis fantasmas, mergulho (janela para pisar nele) e onda de fantasmas.
- **9 armadilhas**: plataforma que cai, plataforma falsa, plataforma móvel, espinho escondido, bloco invisível, moeda explosiva, teto que cai, parede esmagadora e chão que desaparece.
- **Checkpoints** (50% de chance de soltar um Slime surpresa!) e **moedas** (+100 pontos).
- **Menus completos**: principal (com Doguinho animado), seleção de fases (com desbloqueio e recordes), como jogar, configurações (volume/mudo), créditos, pausa, game over e vitória.
- **Save automático** (`user://dog_mario_save.cfg`): fases desbloqueadas, melhores pontuações/tempos, mortes totais e configurações de áudio.
- **Áudio procedural**: 9 efeitos sonoros + 6 músicas em WAV gerados por código.
- **Controles touch** para mobile.

---

## 🏗️ Arquitetura do projeto

```
dog_mario/
├── project.godot              # configuração (1280x720, InputMap, autoloads, pixel art)
├── assets/
│   ├── sprites/               # pixel art (player, enemies, boss, traps, environment, ui, effects)
│   ├── backgrounds/           # fundos das fases e menu
│   └── audio/{sfx,music}/     # WAVs procedurais
├── scenes/
│   ├── main/Main.tscn         # cena inicial -> Menu
│   ├── menus/                 # Menu, LevelSelect, HowToPlay, Settings, Credits, GameOver, Victory
│   ├── player/Player.tscn
│   ├── enemies/               # Slime, BirdEnemy, TurtleEnemy, LivingSpike, GhostDog
│   ├── bosses/Boss.tscn
│   ├── traps/                 # 9 armadilhas
│   ├── systems/               # Checkpoint, Coin, LevelEnd
│   ├── ui/                    # HUD, PauseMenu, TouchControls
│   └── levels/                # Level1, Level2, Level3
├── scripts/
│   ├── systems/               # GameManager, SaveManager, AudioManager (autoloads), Trap, Checkpoint, Coin, Level, LevelEnd, Lava, Main
│   ├── player/Player.gd
│   ├── enemies/               # Enemy (base) + 5 inimigos
│   ├── bosses/                # Boss, BossProjectile
│   ├── traps/                 # 9 armadilhas (herdam de Trap.gd)
│   └── ui/                    # HUD, PauseMenu, MainMenu, LevelSelect, GameOver, Victory, Settings, InfoScreen, TouchControls, UIBuilder
└── tools/                     # scripts Python que geraram sprites, cenas e áudios
```

**Autoloads:** `SaveManager` → `GameManager` → `AudioManager` (nesta ordem).
**Camadas de física:** 1 = mundo, 2 = jogador, 3 = inimigos. Áreas de dano/coleta detectam apenas a camada do jogador.
**Fluxo:** Main → Menu → Level1 → Victory → Level2 → Victory → Level3 (chefe) → Victory final → Menu.

### Ferramentas (opcional)
Os assets podem ser regenerados com Python 3:
```bash
python3 tools/generate_sprites.py   # sprites (requer Pillow)
python3 tools/gen_scripts.py        # scripts GDScript
python3 tools/gen_scenes.py         # cenas .tscn + project.godot (requer Pillow)
python3 tools/generate_audio.py     # áudios WAV (só struct/math)
```

---

## 👥 Créditos

- **Projeto:** DOG MARIO — A Aventura Impossível — trabalho universitário de Desenvolvimento de Jogos.
- **Engine:** Godot Engine 4.x (MIT) — **Linguagem:** GDScript 2.0.
- **Arte:** pixel art original gerada proceduralmente (Python + Pillow).
- **Áudio:** síntese procedural (Python, módulos `struct` e `math`).
- **Inspiração:** Super Mario Bros. (Nintendo) e Syobon Action / Cat Mario.
