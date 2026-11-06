#!/usr/bin/env python3
"""Generate the Kiesel system overview diagram (overview.svg).

Rough overview only: which components exist and what kind of connection runs
between them. Pin-level wiring is not shown here.

Usage: python3 overview.py  ->  writes overview.svg next to this script
"""
from pathlib import Path

W, H = 1480, 900

# Connection types: (color, width, dash, legend label)
STYLE = {
    "bat":   ("#d62828", 5, None,  "Battery power (12 V)"),
    "sense": ("#d62828", 2, "6 5", "Battery voltage (measurement)"),
    "motor": ("#9d0208", 4, None,  "Motor power"),
    "5v":    ("#f77f00", 5, None,  "5 V supply"),
    "ctrl":  ("#2a9d8f", 4, None,  "Motor control (PWM + direction)"),
    "enc":   ("#2a9d8f", 3, "8 6", "Encoder signals"),
    "uart":  ("#e0a800", 4, None,  "Serial data (UART)"),
    "usb":   ("#5c677d", 4, None,  "USB (power + data)"),
    "i2c":   ("#277da1", 4, None,  "I²C bus"),
    "swd":   ("#7b2cbf", 3, None,  "Flashing (SWD)"),
    "csi":   ("#b0b7bf", 5, None,  "Camera ribbon cable (CSI)"),
}

out = []


def add(s):
    out.append(s)


def text(x, y, s, size=13, weight="normal", color="#222", anchor="middle"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
        f'text-anchor="{anchor}">{s}</text>')


# ---------- icons (drawn around a center point) ----------
def pcb(cx, cy, w, h, color):
    add(f'<rect x="{cx - w/2}" y="{cy - h/2}" width="{w}" height="{h}" rx="4" fill="{color}" stroke="#00000033"/>')


def chip(cx, cy, s, label=""):
    add(f'<rect x="{cx - s/2}" y="{cy - s/2}" width="{s}" height="{s}" rx="2" fill="#1d1d1d"/>')
    if label:
        text(cx, cy + 3, label, size=8, color="#ddd")


def icon_battery(cx, cy):
    add(f'<rect x="{cx - 40}" y="{cy - 20}" width="80" height="40" rx="6" fill="#3a6ea5"/>')
    add(f'<rect x="{cx + 40}" y="{cy - 8}" width="7" height="16" rx="2" fill="#3a6ea5"/>')
    add(f'<polygon points="{cx+4},{cy-15} {cx-10},{cy+3} {cx-1},{cy+3} {cx-5},{cy+15} {cx+10},{cy-3} {cx+1},{cy-3}" fill="#ffd166"/>')


def icon_fuse(cx, cy):
    add(f'<rect x="{cx - 22}" y="{cy - 8}" width="44" height="16" rx="3" fill="#e9c46a" stroke="#b08900"/>')
    add(f'<rect x="{cx - 8}" y="{cy - 14}" width="16" height="6" rx="1" fill="#999"/>')
    add(f'<path d="M {cx - 14} {cy} q 7 -7 14 0 t 14 0" stroke="#7a5c00" stroke-width="2" fill="none"/>')


def icon_switch(cx, cy):
    add(f'<rect x="{cx - 22}" y="{cy - 4}" width="44" height="16" rx="8" fill="#555"/>')
    add(f'<line x1="{cx}" y1="{cy + 4}" x2="{cx + 14}" y2="{cy - 16}" stroke="#333" stroke-width="6" stroke-linecap="round"/>')


def icon_driver(cx, cy):
    pcb(cx, cy, 70, 40, "#b5332b")
    chip(cx, cy, 18)
    for i in range(6):
        add(f'<circle cx="{cx - 27 + i*10.8}" cy="{cy - 15}" r="2" fill="#f0c040"/>')
        add(f'<circle cx="{cx - 27 + i*10.8}" cy="{cy + 15}" r="2" fill="#f0c040"/>')


def icon_motor(cx, cy):
    add(f'<rect x="{cx - 42}" y="{cy - 11}" width="44" height="22" rx="4" fill="#a9a9a9"/>')
    add(f'<rect x="{cx + 2}" y="{cy - 12}" width="10" height="24" rx="2" fill="#c9a227"/>')
    add(f'<circle cx="{cx + 34}" cy="{cy}" r="22" fill="#222"/>')
    add(f'<circle cx="{cx + 34}" cy="{cy}" r="8" fill="#888"/>')


def icon_pico(cx, cy):
    pcb(cx, cy, 52, 150, "#2e7d4f")
    add(f'<rect x="{cx - 8}" y="{cy - 82}" width="16" height="10" rx="2" fill="#c0c0c0"/>')
    for i in range(14):
        y = cy - 65 + i * 10
        add(f'<circle cx="{cx - 20}" cy="{y}" r="2.2" fill="#f0c040"/>')
        add(f'<circle cx="{cx + 20}" cy="{y}" r="2.2" fill="#f0c040"/>')
    chip(cx, cy - 5, 20, "RP2350")


def icon_pi(cx, cy):
    pcb(cx, cy, 130, 84, "#2e7d4f")
    for i in range(20):
        add(f'<circle cx="{cx - 52 + i*5.5}" cy="{cy - 34}" r="1.8" fill="#f0c040"/>')
    chip(cx - 18, cy + 6, 24)
    for j, (h, w) in enumerate([(16, 20), (16, 20), (22, 20)]):
        add(f'<rect x="{cx + 48}" y="{cy - 22 + j*20}" width="{w}" height="{h}" rx="2" fill="#c0c0c0"/>')
    add(f'<circle cx="{cx + 22}" cy="{cy + 8}" r="12" fill="#444"/>')


def icon_lidar(cx, cy):
    add(f'<rect x="{cx - 26}" y="{cy - 2}" width="52" height="24" rx="4" fill="#333"/>')
    add(f'<rect x="{cx - 22}" y="{cy - 22}" width="44" height="22" rx="10" fill="#555"/>')
    add(f'<rect x="{cx - 10}" y="{cy - 14}" width="20" height="5" rx="2" fill="#e63946"/>')
    for a in (-1, 1):
        add(f'<path d="M {cx + a*30} {cy - 18} q {a*10} 7 0 14" stroke="#e63946" stroke-width="2" fill="none"/>')


def icon_camera(cx, cy):
    pcb(cx, cy, 46, 46, "#2e7d4f")
    add(f'<rect x="{cx - 12}" y="{cy - 12}" width="24" height="24" rx="3" fill="#222"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#3d5a80"/>')
    add(f'<circle cx="{cx - 3}" cy="{cy - 3}" r="2" fill="#fff"/>')


def icon_imu(cx, cy):
    pcb(cx, cy, 52, 36, "#5a3e8e")
    chip(cx, cy, 16)
    for a in (-1, 1):
        add(f'<circle cx="{cx + a*20}" cy="{cy}" r="3" fill="#ddd"/>')


def icon_tof(cx, cy):
    pcb(cx, cy, 52, 36, "#5a3e8e")
    add(f'<rect x="{cx - 9}" y="{cy - 6}" width="18" height="12" rx="2" fill="#111"/>')
    add(f'<circle cx="{cx - 4}" cy="{cy}" r="2.5" fill="#666"/>')
    add(f'<circle cx="{cx + 4}" cy="{cy}" r="2.5" fill="#666"/>')


# ---------- component cards ----------
def card(x, y, w, h, icon, title, sub, note="", dashed=False, icon_dy=None):
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#ffffff" stroke="#b8b8b8" stroke-width="1.5"{dash}/>')
    icon(x + w/2, y + (icon_dy if icon_dy is not None else 42))
    ty = y + h - (48 if note else 22)
    text(x + w/2, ty, title, size=15, weight="bold")
    text(x + w/2, ty + 16, sub, size=12, color="#555")
    if note:
        text(x + w/2, ty + 31, note, size=11, color="#888")


def wire(kind, pts, label=None, at=None):
    color, width, dash, _ = STYLE[kind]
    d = " ".join(f"{'M' if i == 0 else 'L'} {x} {y}" for i, (x, y) in enumerate(pts))
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}/>')
    if label:
        lx, ly = at
        tw = 7.2 * len(label) + 14
        add(f'<rect x="{lx - tw/2}" y="{ly - 11}" width="{tw}" height="20" rx="10" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
        text(lx, ly + 4, label, size=12, color="#333")


add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="Helvetica, Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#f7f7f5"/>')
text(40, 45, "Kiesel – system overview", size=24, weight="bold", anchor="start")

# Wires first, so the cards sit on top of the line ends
wire("bat", [(200, 140), (230, 140)])
wire("bat", [(310, 140), (340, 140)])
wire("bat", [(390, 185), (390, 330)], "12 V", (390, 300))
wire("bat", [(440, 140), (920, 140), (920, 320), (950, 320)], "12 V · XT30", (680, 140))
wire("sense", [(390, 260), (620, 260), (620, 340), (660, 340)], "battery voltage", (505, 260))
wire("5v", [(950, 405), (810, 405)], "5 V", (880, 405))
wire("ctrl", [(660, 390), (450, 390)], "PWM + direction", (555, 390))
wire("motor", [(320, 450), (320, 560), (130, 560), (130, 620)], "motor power", (225, 560))
wire("motor", [(390, 450), (390, 620)])
wire("enc", [(480, 685), (600, 685), (600, 520), (660, 520)])
wire("enc", [(130, 750), (130, 790), (620, 790), (620, 555), (660, 555)], "encoders", (380, 790))
wire("uart", [(810, 370), (950, 370)], "micro-ROS (UART)", (880, 370))
wire("swd", [(950, 440), (810, 440)], "flashing (SWD)", (880, 440))
wire("usb", [(1080, 210), (1080, 300)], "power + scan data (USB)", (1080, 255))
wire("csi", [(1290, 395), (1210, 395)])
wire("i2c", [(735, 600), (735, 700)])
wire("i2c", [(735, 650), (915, 650), (915, 700)], "I²C", (825, 650))

card(40, 80, 160, 120, icon_battery, "Battery", "3S LiPo")
card(230, 100, 80, 80, icon_fuse, "Fuse", "", icon_dy=30)
card(340, 95, 100, 90, icon_switch, "Switch", "", icon_dy=34)
card(270, 330, 180, 120, icon_driver, "Motor driver", "TB6612FNG")
card(40, 620, 180, 130, icon_motor, "Left motor", "JGA25-370 + encoder", icon_dy=48)
card(300, 620, 180, 130, icon_motor, "Right motor", "JGA25-370 + encoder", icon_dy=48)
card(660, 300, 150, 300, icon_pico, "Microcontroller", "Pi Pico 2 H", "motors · odometry · IMU", icon_dy=120)
card(950, 300, 260, 190, icon_pi, "Single-board computer", "e.g. Jetson Orin NX (Seeed A603)", "ROS 2 · SLAM · navigation", icon_dy=70)
card(990, 80, 180, 130, icon_lidar, "Lidar", "LDROBOT D500", icon_dy=50)
card(1290, 330, 160, 130, icon_camera, "Camera", "e.g. IMX219 camera", icon_dy=48)
card(640, 700, 150, 120, icon_imu, "IMU", "ICM-42688-P")
card(830, 700, 170, 120, icon_tof, "Distance sensor", "VL53L1X (optional)", dashed=True)

# Legend
lx, ly = 1060, 560
add(f'<rect x="{lx - 20}" y="{ly - 30}" width="400" height="{len(STYLE)*26 + 40}" rx="12" fill="#fff" stroke="#b8b8b8" stroke-width="1.5"/>')
text(lx, ly - 6, "Connections", size=14, weight="bold", anchor="start")
for i, (color, width, dash, label) in enumerate(STYLE.values()):
    y = ly + 20 + i * 26
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{lx}" y1="{y}" x2="{lx + 50}" y2="{y}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{dash_attr}/>')
    text(lx + 64, y + 4, label, size=13, anchor="start")

text(40, 872, "All grounds (GND) are connected – not shown.", size=15, color="#555", anchor="start")
add("</svg>")

Path(__file__).with_name("overview.svg").write_text("\n".join(out) + "\n", encoding="utf-8")
