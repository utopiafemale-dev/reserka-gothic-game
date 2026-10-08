#!/usr/bin/env python3
"""Create original procedural game audio, with no external samples or packages.
Run from any directory: python3 godot/tools/generate_audio.py
"""
import array
import math
from pathlib import Path
import random
import wave

RATE = 22050
OUT = Path(__file__).resolve().parents[1] / 'assets' / 'audio'
TAU = math.tau


def hz(note):
    return 440 * 2 ** ((note - 69) / 12)


def save(name, samples):
    peak = max(abs(x) for x in samples) or 1
    gain = 0.72 / max(peak, 0.1)
    pcm = array.array('h')
    for sample in samples:
        value = round(max(-1, min(1, sample * gain)) * 32767)
        pcm.extend((value, value))
    if __import__('sys').byteorder != 'little':
        pcm.byteswap()
    with wave.open(str(OUT / name), 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(pcm.tobytes())
    print(name, f'{len(samples) / RATE:.2f}s')


def tone(buffer, start, length, note, gain=0.12, bell=False):
    frequency = hz(note)
    for i in range(int(length * RATE)):
        t = i / RATE
        if bell:
            envelope = min(1, t / 0.008) * math.exp(-t * 4 / length)
            value = math.sin(TAU * frequency * t) + 0.3 * math.sin(TAU * frequency * 2 * t)
        else:
            envelope = min(1, t / 0.15, (length - t) / 0.2)
            value = (math.sin(TAU * frequency * t) + 0.25 * math.sin(TAU * frequency * 2 * t)
                     + 0.12 * math.sin(TAU * frequency * 3 * t))
        index = (round(start * RATE) + i) % len(buffer)
        buffer[index] += value * max(0, envelope) * gain


def music(name, bpm, transpose, active=False):
    beat = 60 / bpm
    duration = 32 * beat
    samples = [0.0] * round(duration * RATE)
    chords = [(45, 48, 52), (41, 45, 48), (38, 41, 45), (40, 43, 47)] * 2
    melody = [69, 72, 76, 72, 65, 69, 72, 69, 62, 65, 69, 65, 64, 67, 71, 67] * 2
    for bar, chord in enumerate(chords):
        start = bar * 4 * beat
        for note in chord:
            tone(samples, start, 4 * beat, note + transpose, 0.045)
        tone(samples, start, 4 * beat, chord[0] - 12 + transpose, 0.12)
    for step, note in enumerate(melody):
        if active or step % 2 == 0:
            tone(samples, step * beat, beat * 1.4, note + transpose, 0.07, bell=True)
        if active:
            tone(samples, step * beat, beat * 0.3, 33 + transpose, 0.15, bell=True)
    # Short edge fades prevent clicks when Godot repeats the track.
    for i in range(round(0.02 * RATE)):
        gain = i / (0.02 * RATE)
        samples[i] *= gain
        samples[-i - 1] *= gain
    save(name + '.wav', samples)


def effect(name, duration, kind):
    rng = random.Random(name)
    samples = []
    for i in range(round(duration * RATE)):
        t = i / RATE
        u = t / duration
        envelope = min(1, t / 0.008) * (1 - u) ** 2
        if kind == 'jump':
            phase = TAU * (180 * t + 900 * t * t)
            value = math.sin(phase) + 0.2 * math.sin(2 * phase)
        elif kind == 'sword':
            value = rng.uniform(-1, 1) * 0.6 + math.sin(TAU * 950 * t) * 0.15
        elif kind == 'hurt':
            value = math.sin(TAU * (160 * t - 130 * t * t)) + rng.uniform(-0.3, 0.3)
        elif kind == 'enemy_death':
            value = math.sin(TAU * (280 * t - 220 * t * t)) + rng.uniform(-0.4, 0.4)
        elif kind == 'death':
            value = math.sin(TAU * (240 * t - 85 * t * t)) + 0.25 * math.sin(TAU * 55 * t)
        else:
            notes = [72, 76, 79, 84] if kind == 'clear' else [76, 79, 84]
            step = min(len(notes) - 1, int(u * len(notes)))
            local_t = t - step * duration / len(notes)
            value = math.sin(TAU * hz(notes[step]) * local_t)
        samples.append(value * envelope)
    save(name + '.wav', samples)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    music('castle', 70, 0)
    music('swamp', 56, -5)
    music('battle', 96, 0, active=True)
    for name, seconds in [('jump', .18), ('sword', .16), ('hurt', .28), ('pickup', .45),
                          ('enemy_death', .4), ('death', .9), ('clear', 1.1)]:
        effect(name, seconds, name)
