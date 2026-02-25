import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab
import math
import re
import random
import os
from datetime import datetime

# PDF Generation imports
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
except ImportError:
    print("Please install reportlab: pip install reportlab")

class CuboidPuzzle(tk.Canvas):
    def __init__(self, master, width=1100, height=600, **kwargs):
        super().__init__(master, width=width, height=height, bg="#ffffff", highlightthickness=0, **kwargs)
        self.mode = "3x3x2 Cuboid"
        self.state = {}
        self.reset_state()

    def reset_state(self):
        cols = {'U': 'white', 'D': 'yellow', 'L': '#FF8C00', 'R': '#FF0000', 'F': '#00FF00', 'B': '#0000FF'}
        # Specific colors for Pyraminx Duo
        duo_cols = {"G": "#39FF14", "Y": "#FFFF00", "P": "#FF1493", "B": "#00BFFF"}
        
        self.state = {}
        if self.mode == "Pyraminx Duo":
            for c in "GYPB":
                for i in range(4): self.state[f"{c}{i}"] = duo_cols[c]
        elif "Ivy" in self.mode:
            for f in 'UDLRFB':
                for i in ['1','2','3']: self.state[f+i] = cols[f]
        elif "3x3x2" in self.mode or "3x3x1" in self.mode:
            for f in 'UD':
                for i in range(1, 10): self.state[f'{f}{i}'] = cols[f]
            for f in 'LRFB':
                limit = 4 if "3x3x1" in self.mode else 7
                for i in range(1, limit): self.state[f'{f}{i}'] = cols[f]
        elif "1x2x3" in self.mode:
            for f in 'UD':
                for i in range(1, 3): self.state[f'{f}{i}'] = cols[f]
            for f in 'LRFB':
                count = 3 if f in 'LR' else 6
                for i in range(1, count + 1): self.state[f'{f}{i}'] = cols[f]
        else: # 2x2x3
            for f in 'UD':
                for i in range(1, 5): self.state[f'{f}{i}'] = cols[f]
            for f in 'LRFB':
                for i in range(1, 7): self.state[f'{f}{i}'] = cols[f]

    def swap(self, a, b):
        if a in self.state and b in self.state:
            self.state[a], self.state[b] = self.state[b], self.state[a]

    def apply_move(self, move_string):
        moves = re.findall(r"([RUFDLB][2']?)", move_string.upper())
        s = self.state
        def cycle(p, rev=False):
            if rev: p = p[::-1]
            temp = s[p[-1]]
            for i in range(len(p)-1, 0, -1): s[p[i]] = s[p[i-1]]
            s[p[0]] = temp

        for m in moves:
            inv = "'" in m
            if self.mode == "Pyraminx Duo":
                if 'U' in m:
                    cycle(["G0", "B0", "P0"], inv)
                    cycle(["G1", "B3", "P2"], inv)
                elif 'R' in m:
                    cycle(["G0", "P0", "Y0"], inv)
                    cycle(["G3", "P1", "Y3"], inv)
                elif 'L' in m:
                    cycle(["G0", "Y0", "B0"], inv)
                    cycle(["G2", "Y2", "B1"], inv)
                elif 'B' in m:
                    cycle(["B0", "Y0", "P0"], inv)
                    cycle(["B2", "Y1", "P3"], inv)
            elif "Ivy" in self.mode:
                if 'L' in m:
                    cycle(['L2', 'U2', 'F2'], inv)
                    cycle(['L3', 'U1', 'F1'], inv)
                elif 'R' in m:
                    cycle(['R2', 'U2', 'B2'], inv)
                    cycle(['R3', 'U3', 'B1'], inv)
                elif 'D' in m:
                    cycle(['D2', 'F2', 'R2'], inv)
                    cycle(['D3', 'F3', 'R1'], inv)
                elif 'B' in m:
                    cycle(['B2', 'L2', 'D2'], inv)
                    cycle(['B3', 'L1', 'D1'], inv)
            elif "3x3x2" in self.mode or "3x3x1" in self.mode:
                is_331 = "3x3x1" in self.mode
                if 'U' in m and not is_331:
                    count = 2 if '2' in m else (3 if "'" in m else 1)
                    for _ in range(count):
                        s['U1'],s['U3'],s['U9'],s['U7'] = s['U7'],s['U1'],s['U3'],s['U9']
                        s['U2'],s['U6'],s['U8'],s['U4'] = s['U4'],s['U2'],s['U6'],s['U8']
                        s['F1'],s['L1'],s['B1'],s['R1'] = s['R1'],s['F1'],s['L1'],s['B1']
                        s['F2'],s['L2'],s['B2'],s['R2'] = s['R2'],s['F2'],s['L2'],s['B2']
                        s['F3'],s['L3'],s['B3'],s['R3'] = s['R3'],s['F3'],s['L3'],s['B3']
                elif 'D' in m and not is_331:
                    count = 2 if '2' in m else (3 if "'" in m else 1)
                    for _ in range(count):
                        s['D1'],s['D3'],s['D9'],s['D7'] = s['D7'],s['D1'],s['D3'],s['D9']
                        s['D2'],s['D6'],s['D8'],s['D4'] = s['D4'],s['D2'],s['D6'],s['D8']
                        s['F4'],s['R4'],s['B4'],s['L4'] = s['L4'],s['F4'],s['R4'],s['B4']
                        s['F5'],s['R5'],s['B5'],s['L5'] = s['L5'],s['F5'],s['R5'],s['B5']
                        s['F6'],s['R6'],s['B6'],s['L6'] = s['L6'],s['F6'],s['R6'],s['B6']
                elif 'R' in m:
                    for i in [3, 6, 9]: self.swap(f'U{i}', f'D{i}')
                    if is_331: self.swap('F3', 'B1'); self.swap('R1', 'R3')
                    else:
                        self.swap('F3', 'B4'); self.swap('F6', 'B1')
                        self.swap('R1', 'R6'); self.swap('R2', 'R5'); self.swap('R3', 'R4')
                elif 'L' in m:
                    for i in [1, 4, 7]: self.swap(f'U{i}', f'D{i}')
                    if is_331: self.swap('F1', 'B3'); self.swap('L1', 'L3')
                    else:
                        self.swap('F1', 'B6'); self.swap('F4', 'B3')
                        self.swap('L1', 'L6'); self.swap('L2', 'L5'); self.swap('L3', 'L4')
                elif 'F' in m:
                    self.swap('U7', 'D3'); self.swap('U8', 'D2'); self.swap('U9', 'D1')
                    if is_331: self.swap('L3', 'R1'); self.swap('F1', 'F3')
                    else:
                        self.swap('L3', 'R4'); self.swap('L6', 'R1')
                        self.swap('F1', 'F6'); self.swap('F2', 'F5'); self.swap('F3', 'F4')
                elif 'B' in m:
                    self.swap('U1', 'D9'); self.swap('U2', 'D8'); self.swap('U3', 'D7')
                    if is_331: self.swap('L1', 'R3'); self.swap('B1', 'B3')
                    else:
                        self.swap('L1', 'R6'); self.swap('L4', 'R3')
                        self.swap('B1', 'B6'); self.swap('B2', 'B5'); self.swap('B3', 'B4')
            elif "1x2x3" in self.mode:
                if "R" in m:
                    self.swap('F2', 'B5'); self.swap('R1', 'R3'); self.swap('U2', 'D2')
                    self.swap('B1', 'F6'); self.swap('F4', 'B3')
                elif "U" in m:
                    self.swap('F1', 'B1'); self.swap('L1', 'R1'); self.swap('U1', 'U2'); self.swap('B2', 'F2')
                elif "D" in m:
                    self.swap('F5', 'B5'); self.swap('L3', 'R3'); self.swap('D1', 'D2'); self.swap('B6', 'F6')
            else: # 2x2x3
                char = m[0]
                if char == 'U':
                    count = 2 if '2' in m else (3 if "'" in m else 1)
                    for _ in range(count % 4):
                        cycle(['U1', 'U2', 'U4', 'U3'])
                        cycle(['F1', 'R1', 'B1', 'L1'], rev=True)
                        cycle(['F2', 'R2', 'B2', 'L2'], rev=True)
                elif char == 'D':
                    count = 2 if '2' in m else (3 if "'" in m else 1)
                    for _ in range(count % 4):
                        cycle(['D1', 'D2', 'D4', 'D3'])
                        cycle(['F5', 'R5', 'B5', 'L5'])
                        cycle(['F6', 'R6', 'B6', 'L6'])
                elif char == 'R':
                    for a, b in [('U2','D2'),('U4','D4'),('F2','B5'),('F4','B3'),('F6','B1'),('R1','R6'),('R2','R5'),('R3','R4')]:
                        self.swap(a, b)
                elif char == 'F':
                    for a, b in [('U3','D2'),('U4','D1'),('L2','R5'),('L4','R3'),('L6','R1'),('F1','F6'),('F2','F5'),('F3','F4')]:
                        self.swap(a, b)
                elif char == 'B':
                    for a, b in [('U1','D4'),('U2','D3'),('L1','R6'),('L3','R4'),('L5','R2'),('B1','B6'),('B2','B5'),('B3','B4')]:
                        self.swap(a, b)

    def draw_ivy_face(self, x, y, f, size, rotated=False):
        s = size
        if not rotated:
            self.create_polygon(x, y, x+s, y, x, y+s, fill=self.state[f+'1'], outline="black", width=2)
            self.create_polygon(x+s, y+s, x+s, y, x, y+s, fill=self.state[f+'3'], outline="black", width=2)
        else:
            self.create_polygon(x, y+s, x, y, x+s, y+s, fill=self.state[f+'1'], outline="black", width=2)
            self.create_polygon(x+s, y, x, y, x+s, y+s, fill=self.state[f+'3'], outline="black", width=2)
        
        leaf_pts = []
        steps = 20
        if not rotated:
            for i in range(steps + 1):
                a = (math.pi/2) * (i/steps)
                leaf_pts.append((x + s * math.cos(a), y + s * math.sin(a)))
            for i in range(steps + 1):
                a = math.pi + (math.pi/2) * (i/steps)
                leaf_pts.append((x + s + s * math.cos(a), y + s + s * math.sin(a)))
        else:
            for i in range(steps + 1):
                a = -math.pi/2 + (math.pi/2) * (i/steps)
                leaf_pts.append((x + s * math.cos(a), y + s + s * math.sin(a)))
            for i in range(steps + 1):
                a = math.pi/2 + (math.pi/2) * (i/steps)
                leaf_pts.append((x + s + s * math.cos(a), y + s * math.sin(a)))
        self.create_polygon(leaf_pts, fill=self.state[f+'2'], outline="black", width=2, smooth=True)

    def draw_duo_face(self, cx, cy, prefix, side=120, inv_orient=False):
        h = (side * math.sqrt(3)) / 2
        d_base = h / 3
        inner_s = side * 0.35
        inner_h = (inner_s * math.sqrt(3)) / 2
        inner_d = inner_h / 3

        if not inv_orient:
            v = [(cx, cy - 2*d_base), (cx - side/2, cy + d_base), (cx + side/2, cy + d_base)]
        else:
            v = [(cx, cy + 2*d_base), (cx - side/2, cy - d_base), (cx + side/2, cy - d_base)]

        m = [((v[0][0]+v[1][0])/2, (v[0][1]+v[1][1])/2),
             ((v[1][0]+v[2][0])/2, (v[1][1]+v[2][1])/2),
             ((v[2][0]+v[0][0])/2, (v[2][1]+v[0][1])/2)]

        self.create_polygon(v[0], m[0], (cx, cy), m[2], fill=self.state[f"{prefix}1"], outline="black", width=2)
        self.create_polygon(v[1], m[1], (cx, cy), m[0], fill=self.state[f"{prefix}2"], outline="black", width=2)
        self.create_polygon(v[2], m[2], (cx, cy), m[1], fill=self.state[f"{prefix}3"], outline="black", width=2)

        iv = [(cx, cy-2*inner_d), (cx-inner_s/2, cy+inner_d), (cx+inner_s/2, cy+inner_d)] if not inv_orient else \
             [(cx, cy+2*inner_d), (cx-inner_s/2, cy-inner_d), (cx+inner_s/2, cy-inner_d)]
        self.create_polygon(iv, fill=self.state[f"{prefix}0"], outline="black", width=2)

    def render_puzzle(self):
        self.delete("all")
        if self.mode == "Pyraminx Duo":
            side = 130
            h = (side * math.sqrt(3)) / 2
            gap = (h * 2/3) + 12
            self.draw_duo_face(550, 180, "G", side)
            self.draw_duo_face(550, 180 + gap, "Y", side, True)
            px, py = 550 + gap * math.cos(math.radians(30)), 180 - gap * math.sin(math.radians(30))
            self.draw_duo_face(px, py, "P", side, True)
            bx, by = 550 - gap * math.cos(math.radians(30)), 180 - gap * math.sin(math.radians(30))
            self.draw_duo_face(bx, by, "B", side, True)
            return

        if "Ivy" in self.mode:
            s, g = 100, 12
            start_x, start_y = 250, 40
            faces = [('U', start_x+s+g, start_y, True), 
                     ('L', start_x, start_y+s+g, True),
                     ('F', start_x+s+g, start_y+s+g, False), 
                     ('R', start_x+2*(s+g), start_y+s+g, True),
                     ('B', start_x+3*(s+g), start_y+s+g, False), 
                     ('D', start_x+s+g, start_y+2*(s+g), True)]
            for f, x, y, rot in faces: self.draw_ivy_face(x, y, f, s, rot)
            return

        s, p, g = 50, 3, 20
        def draw_sq(x, y, label):
            self.create_rectangle(x, y, x+s, y+s, fill=self.state.get(label, 'grey'), outline="black", width=2)

        start_x, start_y = 350, 40
        if "3x3x" in self.mode:
            is_331 = "3x3x1" in self.mode
            rows = 1 if is_331 else 2
            unit = 3 * (s + p)
            for r in range(3):
                for c in range(3): draw_sq(start_x + c*(s+p), start_y + r*(s+p), f"U{r*3+c+1}")
            mid_y = start_y + unit + g
            faces = [("L", start_x - unit - g), ("F", start_x), ("R", start_x + unit + g), ("B", start_x + 2*(unit + g))]
            for f, fx in faces:
                for r in range(rows):
                    for c in range(3): draw_sq(fx + c*(s+p), mid_y + r*(s+p), f"{f}{r*3+c+1}")
            bot_y = mid_y + rows*(s+p) + g
            for r in range(3):
                for c in range(3): draw_sq(start_x + c*(s+p), bot_y + r*(s+p), f"D{r*3+c+1}")
        else:
            is_123 = "1x2x3" in self.mode
            top_r = 1 if is_123 else 2
            for r in range(top_r):
                for c in range(2): draw_sq(start_x + c*(s+p), start_y + r*(s+p), f"U{r*2+c+1}")
            mid_y = start_y + top_r*(s+p) + g
            face_configs = [("L", 1 if is_123 else 2), ("F", 2), ("R", 1 if is_123 else 2), ("B", 2)]
            curr_x = start_x - (1 if is_123 else 2)*(s+p) - g
            for f, face_c in face_configs:
                for r in range(3):
                    for c in range(face_c): 
                        draw_sq(curr_x + c*(s+p), mid_y + r*(s+p), f"{f}{r*face_c+c+1}")
                curr_x += face_c*(s+p) + g
            bot_y = mid_y + 3*(s+p) + g
            for r in range(top_r):
                for c in range(2): draw_sq(start_x + c*(s+p), bot_y + r*(s+p), f"D{r*2+c+1}")

class ClockPuzzle(tk.Canvas):
    def __init__(self, master, app, size=550, is_front=True, **kwargs):
        super().__init__(master, width=size, height=size, bg="#ffffff", highlightthickness=0, **kwargs)
        self.app, self.size, self.center, self.is_front = app, size, size / 2, is_front
        self.clock_values = [12] * 11
        self.update_theme()

    def update_theme(self):
        if self.is_front:
            self.body_color, self.face_color, self.pin_color = "#ffffff", "#f78fb3", "#f78fb3"
            self.marker_color, self.ptr_color = "#2d3436", "#2d3436"
        else:
            self.body_color, self.face_color, self.pin_color = "#f78fb3", "#ffffff", "#ffffff"
            self.marker_color, self.ptr_color = "#2d3436", "#f78fb3"

    def draw_pointer(self, cx, cy, radius, value):
        angle_rad = math.radians(value * 30 - 90)
        tip_x, tip_y = cx + radius * math.cos(angle_rad), cy + radius * math.sin(angle_rad)
        base_w, angle_deg = 11, value * 30 - 90
        l_x, l_y = cx + base_w * math.cos(math.radians(angle_deg - 110)), cy + base_w * math.sin(math.radians(angle_deg - 110))
        r_x, r_y = cx + base_w * math.cos(math.radians(angle_deg + 110)), cy + base_w * math.sin(math.radians(angle_deg + 110))
        self.create_polygon(l_x, l_y, tip_x, tip_y, r_x, r_y, fill=self.ptr_color, outline="#2d3436", width=1.5, smooth=True)
        self.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ffffff", outline="#2d3436", width=1.5)

    def render_puzzle(self):
        self.delete("all")
        mode = self.app.mode_var.get()
        if "Cuboid" in mode or "Ivy" in mode or "Pyraminx" in mode: return
        lobe_pos, pin_positions, clock_pos = [], [], []
        clock_r, marker_r = 40, 48
        if mode == "Triangular":
            lobe_pos, pin_positions = [(0, -185), (-190, 135), (190, 135)], [(0, -90), (-100, 75), (100, 75)]
            clock_pos = [(0, -185), (-110, -35), (110, -35), (-190, 135), (0, 135), (190, 135)]
            clock_r, marker_r, main_r, lobe_r = 52, 60, 230, 80
        else:
            lobe_dist, lobe_r, main_r = 195, 60, 225
            lobe_pos = [(lobe_dist * math.cos(math.radians(i * 72 - 90)), lobe_dist * math.sin(math.radians(i * 72 - 90))) for i in range(5)]
            pin_positions = [(110 * math.cos(math.radians(i * 72 - 18)), 110 * math.sin(math.radians(i * 72 - 18))) for i in range(5)]
            for i in range(5):
                clock_pos.append((190 * math.cos(math.radians(i * 72 - 90)), 190 * math.sin(math.radians(i * 72 - 90)))) 
            for i in range(5):
                clock_pos.append((155 * math.cos(math.radians(i * 72 - 54)), 155 * math.sin(math.radians(i * 72 - 54)))) 
            if mode == "Super-Pentagonal": clock_pos.append((0, -30)) 

        points = []
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            max_d = main_r
            centers = [(0, 0, main_r)] + [(pos[0], pos[1], lobe_r) for pos in lobe_pos]
            for cx, cy, r in centers:
                b, c = -2 * (cx * math.cos(rad) + cy * math.sin(rad)), cx**2 + cy**2 - r**2
                delta = b**2 - 4*c
                if delta >= 0:
                    d = (-b + math.sqrt(delta)) / 2
                    max_d = max(max_d, d)
            points.extend([self.center + max_d * math.cos(rad), self.center + max_d * math.sin(rad)])
        
        self.create_polygon(points, fill=self.body_color, outline="#f78fb3", width=3, smooth=True)
        for px, py in pin_positions:
            pcx, pcy = self.center + px, self.center + py
            self.create_oval(pcx-16, pcy-16, pcx+16, pcy+16, fill=self.pin_color, outline="#2d3436" if self.is_front else "#ffffff", width=2.5)
        for i, (dx, dy) in enumerate(clock_pos):
            cx, cy, val = self.center + dx, self.center + dy, self.clock_values[i] if i < len(self.clock_values) else 12
            self.create_oval(cx-clock_r, cy-clock_r, cx+clock_r, cy+clock_r, fill=self.face_color, outline="#f78fb3", width=1.5)
            for h in range(12):
                a = math.radians(h * 30 - 90)
                if h == 0: self.create_line(cx+(marker_r-4)*math.cos(a), cy+(marker_r-4)*math.sin(a), cx+(marker_r+4)*math.cos(a), cy+(marker_r+4)*math.sin(a), fill="#ff0066", width=4)
                else: 
                    px, py = cx+marker_r*math.cos(a), cy+marker_r*math.sin(a)
                    self.create_oval(px-2, py-2, px+2, py+2, fill=self.marker_color, outline="")
            self.draw_pointer(cx, cy, clock_r, val)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Global Scrambler - Pink Professional PDF")
        self.geometry("1400x950")
        self.configure(fg_color="#ffffff")
        self.mode_var = ctk.StringVar(value="3x3x2 Cuboid")
        
        # UI Container
        self.container = ctk.CTkFrame(self, fg_color="#ffffff")
        self.container.pack(expand=True, pady=10)
        self.clock_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.front = ClockPuzzle(self.clock_frame, self, is_front=True); self.front.grid(row=0, column=0, padx=20)
        self.back = ClockPuzzle(self.clock_frame, self, is_front=False); self.back.grid(row=0, column=1, padx=20)
        self.cuboid = CuboidPuzzle(self.container)
        
        self.status_label = ctk.CTkLabel(self, text="System Ready", text_color="#2d3436", font=("Arial", 16))
        self.status_label.pack(pady=5)

        # Control Panel
        ctrl = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=20)
        ctrl.pack(fill="x", side="bottom", padx=50, pady=20)
        
        inner_ctrl = ctk.CTkFrame(ctrl, fg_color="transparent")
        inner_ctrl.pack(expand=True, pady=15)

        # Config Inputs
        self.comp_entry = ctk.CTkEntry(inner_ctrl, placeholder_text="Competition Name", width=180)
        self.comp_entry.pack(side="left", padx=5)
        self.comp_entry.insert(0, "Greenwoods Clonk Clash")

        self.date_entry = ctk.CTkEntry(inner_ctrl, placeholder_text="Date (YYYY-MM-DD)", width=120)
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkLabel(inner_ctrl, text="Rounds:").pack(side="left", padx=2)
        self.round_spin = ctk.CTkEntry(inner_ctrl, width=40)
        self.round_spin.pack(side="left", padx=5)
        self.round_spin.insert(0, "1")

        modes = ["Triangular", "Pentagonal", "Super-Pentagonal", "1x2x3 Cuboid", "2x2x3 Cuboid", "3x3x2 Cuboid", "3x3x1 Cuboid", "Ivy Cube", "Pyraminx Duo"]
        self.mode_menu = ctk.CTkOptionMenu(inner_ctrl, values=modes, variable=self.mode_var, command=self.change_mode, fg_color="#f78fb3")
        self.mode_menu.pack(side="left", padx=10)
        
        self.gen_btn = ctk.CTkButton(inner_ctrl, text="GENERATE PDF", command=self.export_pdf, fg_color="#2ecc71")
        self.gen_btn.pack(side="left", padx=20)
        
        self.change_mode(self.mode_var.get())

    def change_mode(self, mode):
        if "Cuboid" in mode or "Ivy" in mode or "Pyraminx" in mode:
            self.clock_frame.pack_forget(); self.cuboid.pack(expand=True)
            self.cuboid.mode = mode; self.cuboid.reset_state(); self.cuboid.render_puzzle()
        else:
            self.cuboid.pack_forget(); self.clock_frame.pack(expand=True)
            count = {"Triangular": 6, "Pentagonal": 10, "Super-Pentagonal": 11}.get(mode, 11)
            self.front.clock_values = [12] * count
            self.back.clock_values = [12] * count
            self.front.render_puzzle(); self.back.render_puzzle()

    def apply_clock_logic(self, text, mode):
        max_clocks = 11 if mode == "Super-Pentagonal" else (10 if mode == "Pentagonal" else 6)
        self.front.clock_values, self.back.clock_values = [12]*max_clocks, [12]*max_clocks
        is_back = False
        if mode == "Triangular":
            move_map = {"DR":[5,4,2], "DL":[3,4,1], "U":[0,1,2], "R":[0,1,2,4,5], "D":[1,2,3,4,5], "L":[0,1,2,3,4], "ALL":[0,1,2,3,4,5]}
            mirror_indices = {0:0, 3:5, 5:3}
        else:
            l2i = {1:0, 3:2, 5:4, 7:6, 9:8, 2:1, 4:3, 6:5, 8:7, 10:9}
            if mode == "Super-Pentagonal": l2i[11] = 10
            move_map_labels = {'UR': [2,6,7], 'DR': [3,7,8], 'DL': [4,8,9], 'UL': [5,9,10], 'UM': [10,6,1], 'L': [5,4,9,10,1], 'U': [2,10,1,5,6], 'R': [1,2,3,6,7], 'DRW': [3,4,2,8,7], 'DLW': [5,4,3,8,9], 'ALL': [1,2,3,4,5,6,7,8,9,10]}
            if mode == "Super-Pentagonal":
                move_map_labels['ALL'].append(11)
                for k in ['UR', 'DR', 'DL', 'UL', 'UM']: move_map_labels[k].append(11)
            move_map = {k: [l2i[lbl] for lbl in v] for k, v in move_map_labels.items()}
            mirror_indices = {0:0, 1:4, 2:3, 3:2, 4:1}
        for move in text.split():
            if move.lower() == 'y2': is_back = True; continue
            match = re.match(r"([A-Za-z]+)(\d+)([+\-−])", move)
            if not match: continue
            cmd, val, sign = match.groups()
            delta = int(val) if sign == '+' else -int(val)
            t, o = (self.back, self.front) if is_back else (self.front, self.back)
            cmd_upper = cmd.upper()
            if cmd_upper in move_map:
                for idx in move_map[cmd_upper]:
                    if idx < len(t.clock_values):
                        t.clock_values[idx] = (t.clock_values[idx] + delta - 1) % 12 + 1
                        if not is_back:
                            if idx in mirror_indices:
                                b_idx = mirror_indices[idx]; o.clock_values[b_idx] = (o.clock_values[b_idx] - delta - 1) % 12 + 1
            else:
                inv_mirror = {v: k for k, v in mirror_indices.items()}
                if idx in inv_mirror:
                    f_idx = inv_mirror[idx]; o.clock_values[f_idx] = (o.clock_values[f_idx] - delta - 1) % 12 + 1

    def generate_single_scramble(self):
        mode = self.mode_var.get()
        
        if "Cuboid" in mode or "Ivy" in mode or "Pyraminx" in mode:
            self.cuboid.mode = mode
            self.cuboid.reset_state()
            solved_state = self.cuboid.state.copy()
            
            if mode == "Pyraminx Duo":
                moves = ["U", "U'", "L", "L'", "R", "R'", "B", "B'"]
                length = random.randint(6, 7)
            elif mode == "3x3x2 Cuboid":
                moves = ["U", "U'", "U2", "R2", "L2", "F2", "B2"]
                length = 25
            elif mode == "3x3x1 Cuboid":
                moves = ["R", "L", "F", "B"]
                length = random.randint(4, 8)
            elif mode == "2x2x3 Cuboid":
                moves = ["U", "U'", "U2", "D", "D'", "D2", "R2", "F2"]
                length = random.randint(10, 13)
            elif mode == "1x2x3 Cuboid":
                moves = ["U2", "D2", "R2"]
                length = random.randint(8, 10)
            elif mode == "Ivy Cube":
                moves = ["R", "R'", "L", "L'", "U", "U'", "B", "B'"]
                length = random.randint(7, 10)
            else:
                moves, length = ["U2", "D2", "R2"], 10

            while True:
                scr = []
                while len(scr) < length:
                    m = random.choice(moves)
                    if scr and m[0] == scr[-1][0]: continue
                    if len(scr) >= 2:
                        pattern = [scr[-2][0], scr[-1][0], m[0]]
                        if pattern == ['U', 'D', 'U'] or pattern == ['D', 'U', 'D']: continue
                    if mode == "3x3x2 Cuboid" and len(scr) >= 2:
                        if scr[-2][0] == m[0]:
                            pair = {scr[-2][0], m[0]}
                            if pair == {'R', 'L'} or pair == {'F', 'B'}: continue
                    scr.append(m)
                
                scr_str = " ".join(scr)
                self.cuboid.reset_state()
                self.cuboid.apply_move(scr_str)
                if self.cuboid.state != solved_state: return scr_str

        elif mode == "Triangular":
            m1, m2 = ["DR", "DL", "U", "R", "D", "L", "ALL"], ["DR", "DL", "U", "ALL"]
            def get_m(m):
                v = random.randint(0, 6); s = '+' if v in [0,6] else random.choice(['+','-'])
                return f"{m}{v}{s}"
            return f"{' '.join([get_m(m) for m in m1])} y2 {' '.join([get_m(m) for m in m2])}"
        else:
            m1, m2 = ["UR", "DR", "DL", "UL", "UM", "L", "U", "R", "DRw", "DLw", "ALL"], ["L", "U", "R", "DRw", "DLw", "ALL"]
            def get_m(m):
                v = random.randint(0, 6); s = '+' if v in [0,6] else random.choice(['+','-'])
                return f"{m}{v}{s}"
            return f"{' '.join([get_m(m) for m in m1])} y2 {' '.join([get_m(m) for m in m2])}"

    def export_pdf(self):
        comp_name = self.comp_entry.get() or "Pink_Comp"
        comp_date = self.date_entry.get() or datetime.now().strftime("%Y-%m-%d")
        mode = self.mode_var.get()
        num_rounds = int(self.round_spin.get() or 1)
        
        filename = f"{comp_name}_{mode}_{datetime.now().strftime('%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=11, leading=14)
        scramble_style = ParagraphStyle('ScrambleStyle', parent=styles['Normal'], fontSize=10, leading=13)
        
        elements = []
        temp_files = []
        is_clock = "Cuboid" not in mode and "Ivy" not in mode and "Pyraminx" not in mode
        
        img_w, img_h = (4.5*inch, 2.2*inch) if is_clock else (4.0*inch, 2.3*inch)

        for r_num in range(1, num_rounds + 1):
            title_table = Table([
                [Paragraph(f"<b>{comp_date}</b>", header_style), ""],
                [Paragraph(f"<b>{comp_name}</b>", header_style), ""],
                [Paragraph(f"<b>{mode} Round {r_num}</b>", header_style), ""]
            ], colWidths=[400, 100])
            elements.append(title_table)
            elements.append(Spacer(1, 15))

            for i in range(1, 8):
                is_extra = (i > 5)
                label = f"{i}" if not is_extra else f"E{i-5}"
                if i == 6:
                    elements.append(Spacer(1, 10))
                    elements.append(Paragraph("<b>Extra Scrambles</b>", header_style))
                    elements.append(Spacer(1, 5))

                scr = self.generate_single_scramble()
                self.change_mode(mode) 
                
                if not is_clock:
                    self.cuboid.reset_state(); self.cuboid.apply_move(scr); self.cuboid.render_puzzle()
                    target = self.cuboid
                else: 
                    self.apply_clock_logic(scr, mode)
                    self.front.render_puzzle(); self.back.render_puzzle()
                    target = self.clock_frame
                
                self.update()
                img_path = f"tmp_{r_num}_{i}.png"
                x, y, w, h = target.winfo_rootx(), target.winfo_rooty(), target.winfo_width(), target.winfo_height()
                ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(img_path)
                temp_files.append(img_path)

                row_content = [
                    Paragraph(f"<b>{label}</b>", header_style),
                    Paragraph(scr.replace(" y2 ", "<br/>y2<br/>"), scramble_style),
                    RLImage(img_path, width=img_w, height=img_h)
                ]
                
                t = Table([row_content], colWidths=[0.4*inch, 1.8*inch, 4.6*inch])
                t.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                    ('BACKGROUND', (0,0), (0,0), colors.pink if is_extra else colors.white)
                ]))
                elements.append(t)
                elements.append(Spacer(1, 2))

            elements.append(PageBreak())

        doc.build(elements)
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)
        self.status_label.configure(text=f"PDF Saved: {filename}")

if __name__ == "__main__":
    App().mainloop()