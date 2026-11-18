"""Gera os audios WAV (PCM 16-bit mono) do DOG MARIO usando apenas struct e math."""
import math
import os
import random
import struct

RATE = 22050
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "audio")


def write_wav(rel, samples):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32000)) for s in samples)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, RATE, RATE * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", len(data)) + data)


def square(phase):
    return 1.0 if (phase % 1.0) < 0.5 else -1.0


def tri(phase):
    p = phase % 1.0
    return 4 * p - 1 if p < 0.5 else 3 - 4 * p


def sweep(f0, f1, dur, wave=square, vol=0.4):
    n, out, ph = int(RATE * dur), [], 0.0
    for i in range(n):
        t = i / n
        ph += (f0 + (f1 - f0) * t) / RATE
        out.append(wave(ph) * vol * (1 - t))
    return out


def noise(dur, vol=0.5, decay=True):
    n = int(RATE * dur)
    return [random.uniform(-1, 1) * vol * ((1 - i / n) if decay else 1) for i in range(n)]


def tone(freq, dur, wave=square, vol=0.3):
    n = int(RATE * dur)
    return [wave(freq * i / RATE) * vol * min(1.0, (n - i) / (RATE * 0.02)) for i in range(n)]


def note_freq(n):  # n = semitons a partir de A4
    return 440.0 * 2 ** (n / 12.0)


def song(melody, bass, bpm, length, lead=square, bass_wave=tri):
    """melody/bass: listas de (semitom ou None, batidas). Repete ate 'length' segundos."""
    total = int(RATE * length)
    out = [0.0] * total
    beat = 60.0 / bpm
    for seq, wave, vol, octave in ((melody, lead, 0.18, 0), (bass, bass_wave, 0.25, -24)):
        pos = 0
        while pos < total:
            for n, beats in seq:
                ln = int(beats * beat * RATE)
                if n is not None:
                    f = note_freq(n + octave)
                    for i in range(min(ln, total - pos)):
                        env = min(1.0, (ln - i) / (RATE * 0.03)) * (0.6 + 0.4 * (1 - i / ln))
                        out[pos + i] += wave(f * i / RATE) * vol * env
                pos += ln
                if pos >= total:
                    break
    return out


def main():
    random.seed(7)
    write_wav("sfx/jump.wav", sweep(300, 900, 0.18))
    write_wav("sfx/coin.wav", tone(988, 0.07) + tone(1319, 0.25))
    write_wav("sfx/death.wav", sweep(700, 120, 0.9, tri, 0.5))
    write_wav("sfx/hurt.wav", [a * 0.6 + b for a, b in zip(noise(0.2, 0.4), sweep(400, 200, 0.2))])
    write_wav("sfx/trap.wav", sweep(200, 1200, 0.12) + sweep(1200, 300, 0.2))
    write_wav("sfx/checkpoint.wav", tone(523, 0.1) + tone(659, 0.1) + tone(784, 0.1) + tone(1047, 0.3))
    write_wav("sfx/enemy_die.wav", sweep(900, 200, 0.12, square, 0.5))
    write_wav("sfx/boss_hurt.wav", [a + b for a, b in zip(noise(0.35, 0.5), sweep(160, 40, 0.35, tri, 0.6))])
    write_wav("sfx/explosion.wav", noise(0.7, 0.8))
    _ = None
    write_wav("music/menu.wav", song([(3, 1), (7, 1), (10, 1), (7, 1), (5, 1), (8, 1), (12, 2)],
                                     [(3, 2), (-2, 2), (5, 2), (-2, 2)], 120, 8))
    write_wav("music/level1.wav", song([(3, .5), (3, .5), (_, .5), (3, .5), (_, .5), (-1, .5), (3, 1), (10, 1), (_, 1), (-2, 1),
                                        (_, 1), (3, .5), (7, .5), (5, 1), (3, 1)],
                                       [(3, 1), (10, 1), (8, 1), (10, 1)], 140, 12))
    write_wav("music/level2.wav", song([(0, 1), (3, 1), (7, 1), (6, 1), (3, 2), (_, 1), (2, 1), (0, 2)],
                                       [(0, 2), (-4, 2), (-5, 2), (-2, 2)], 96, 12, tri))
    write_wav("music/level3.wav", song([(0, .5), (0, .5), (1, .5), (0, .5), (-2, 1), (3, 1), (1, .5), (0, .5), (-2, 1), (_, 1)],
                                       [(0, 1), (0, 1), (-4, 1), (-5, 1)], 120, 12))
    write_wav("music/boss.wav", song([(0, .25), (3, .25), (6, .25), (3, .25), (1, .25), (4, .25), (7, .25), (4, .25)],
                                     [(0, .5), (0, .5), (1, .5), (-1, .5)], 160, 12))
    write_wav("music/victory.wav", song([(3, .5), (7, .5), (10, .5), (15, 1.5), (12, .5), (15, 2), (_, 2)],
                                        [(3, 2), (8, 2), (10, 4)], 120, 8))
    print("15 audios gerados em", os.path.abspath(ROOT))


if __name__ == "__main__":
    main()
