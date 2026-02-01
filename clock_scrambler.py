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
except ImportError:
    print("Please install reportlab: pip install reportlab")

class ClockPuzzle(tk.Canvas):
    def __init__(self, master, app, size=550, is_front=True, **kwargs):
        super().__init__(master, width=size, height=size, bg="#ffffff", highlightthickness=0, **kwargs)
        self.app = app
        self.size = size
        self.center = size / 2
        self.is_front = is_front
        self.clock_values = []
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
        # MAXIMIZED LENGTH: Tip reaches the exact radius of the clock face
        tip_x = cx + radius * math.cos(angle_rad)
        tip_y = cy + radius * math.sin(angle_rad)
        
        # Sleek, long pointer base
        base_w, angle_deg = 11, value * 30 - 90
        l_x = cx + base_w * math.cos(math.radians(angle_deg - 110))
        l_y = cy + base_w * math.sin(math.radians(angle_deg - 110))
        r_x = cx + base_w * math.cos(math.radians(angle_deg + 110))
        r_y = cy + base_w * math.sin(math.radians(angle_deg + 110))
        
        self.create_polygon(l_x, l_y, tip_x, tip_y, r_x, r_y, fill=self.ptr_color, outline="#2d3436", width=1.5, smooth=True)
        # Center cap
        self.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ffffff", outline="#2d3436", width=1.5)

    def render_puzzle(self):
        self.delete("all")
        mode = self.app.mode_var.get()
        lobe_pos, pin_positions, clock_pos = [], [], []
        clock_r, marker_r = 40, 48

        if mode == "Triangular":
            main_r, lobe_r = 230, 80
            lobe_pos = [(0, -185), (-190, 135), (190, 135)]
            # SYMMETRICAL PIN PLACEMENT
            pin_positions = [(0, -90), (-100, 75), (100, 75)]
            clock_pos = [(0, -185), (-110, -35), (110, -35), (-190, 135), (0, 135), (190, 135)]
            clock_r, marker_r = 52, 60
        else:
            lobe_dist, lobe_r, main_r = 195, 60, 225
            lobe_pos = [(lobe_dist * math.cos(math.radians(i * 72 - 90)), lobe_dist * math.sin(math.radians(i * 72 - 90))) for i in range(5)]
            pin_positions = [(110 * math.cos(math.radians(i * 72 - 18)), 110 * math.sin(math.radians(i * 72 - 18))) for i in range(5)]
            for i in range(5): 
                a = math.radians(i * 72 - 90)
                clock_pos.append((190 * math.cos(a), 190 * math.sin(a))) 
            for i in range(5): 
                a = math.radians(i * 72 - 54) 
                clock_pos.append((155 * math.cos(a), 155 * math.sin(a))) 
            if mode == "Super-Pentagonal":
                clock_pos.append((0, -30)) 

        # Shell
        points = []
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            max_d = main_r
            centers = [(0, 0, main_r)] + [(pos[0], pos[1], lobe_r) for pos in lobe_pos]
            for cx, cy, r in centers:
                b = -2 * (cx * math.cos(rad) + cy * math.sin(rad))
                c = cx**2 + cy**2 - r**2
                delta = b**2 - 4*c
                if delta >= 0:
                    d = (-b + math.sqrt(delta)) / 2
                    max_d = max(max_d, d)
            points.extend([self.center + max_d * math.cos(rad), self.center + max_d * math.sin(rad)])
        
        self.create_polygon(points, fill=self.body_color, outline="#f78fb3", width=3, smooth=True)
        
        # Pins
        for px, py in pin_positions:
            pcx, pcy = self.center + px, self.center + py
            self.create_oval(pcx-16, pcy-16, pcx+16, pcy+16, fill=self.pin_color, outline="#2d3436" if self.is_front else "#ffffff", width=2.5)

        # Clocks
        for i, (dx, dy) in enumerate(clock_pos):
            cx, cy = self.center + dx, self.center + dy
            val = self.clock_values[i] if i < len(self.clock_values) else 12
            self.create_oval(cx-clock_r, cy-clock_r, cx+clock_r, cy+clock_r, fill=self.face_color, outline="#f78fb3", width=1.5)
            for h in range(12):
                a = math.radians(h * 30 - 90)
                if h == 0: 
                    self.create_line(cx+(marker_r-4)*math.cos(a), cy+(marker_r-4)*math.sin(a), cx+(marker_r+4)*math.cos(a), cy+(marker_r+4)*math.sin(a), fill="#ff0066", width=4)
                else:
                    px, py = cx+marker_r*math.cos(a), cy+marker_r*math.sin(a)
                    self.create_oval(px-2, py-2, px+2, py+2, fill=self.marker_color, outline="")
            self.draw_pointer(cx, cy, clock_r, val)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Super-Pentagonal Scrambler v3.0")
        self.geometry("1450x1000")
        self.configure(fg_color="#ffffff")

        self.mode_var = ctk.StringVar(value="Super-Pentagonal")
        self.round_count_var = ctk.StringVar(value="1")
        
        self.container = ctk.CTkFrame(self, fg_color="#ffffff")
        self.container.pack(expand=True, pady=10)

        self.front = ClockPuzzle(self.container, self, is_front=True)
        self.front.grid(row=0, column=0, padx=30)
        self.back = ClockPuzzle(self.container, self, is_front=False)
        self.back.grid(row=0, column=1, padx=30)

        self.status_label = ctk.CTkLabel(self, text="Pointers Maximized | Logic Isolated", text_color="#f78fb3", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=5)

        ctrl = ctk.CTkFrame(self, fg_color="#fdf2f5", corner_radius=20)
        ctrl.pack(fill="x", side="bottom", padx=50, pady=20)

        inner_ctrl = ctk.CTkFrame(ctrl, fg_color="transparent")
        inner_ctrl.pack(expand=True, pady=15)

        ctk.CTkLabel(inner_ctrl, text="Competition:", text_color="#2d3436").pack(side="left", padx=10)
        self.comp_entry = ctk.CTkEntry(inner_ctrl, placeholder_text="Pasig Open 2026", width=200)
        self.comp_entry.pack(side="left", padx=10)

        self.mode_menu = ctk.CTkOptionMenu(inner_ctrl, values=["Triangular", "Pentagonal", "Super-Pentagonal"], variable=self.mode_var, command=self.change_mode, fg_color="#f78fb3")
        self.mode_menu.pack(side="left", padx=10)

        self.round_menu = ctk.CTkOptionMenu(inner_ctrl, values=["1", "2", "3", "4"], variable=self.round_count_var, fg_color="#f78fb3", width=80)
        self.round_menu.pack(side="left", padx=10)

        self.gen_btn = ctk.CTkButton(inner_ctrl, text="GENERATE PDF", command=self.export_pdf, fg_color="#f78fb3", font=("Arial", 14, "bold"))
        self.gen_btn.pack(side="left", padx=20)
        
        self.change_mode(self.mode_var.get())

    def change_mode(self, mode):
        counts = {"Triangular": 6, "Pentagonal": 10, "Super-Pentagonal": 11}
        self.front.clock_values = [12] * counts[mode]
        self.back.clock_values = [12] * counts[mode]
        self.front.render_puzzle()
        self.back.render_puzzle()

    def apply_super_logic(self, scramble):
        move_map = {
            "UR": [2, 6, 7], "DR": [3, 7, 8], "DL": [4, 8, 9], "UL": [5, 9, 10], 
            "UM": [10, 6, 1, 11], "L": [5, 4, 9, 10, 1, 11], "U": [2, 10, 1, 5, 6, 11], 
            "R": [1, 2, 3, 6, 7, 11], "DRw": [3, 4, 2, 8, 7], "DLw": [5, 4, 3, 8, 9], 
            "ALL": list(range(1, 12))
        }
        mirror = {1:1, 2:5, 3:4, 4:3, 5:2, 6:10, 7:9, 8:8, 9:7, 10:6}
        
        is_back = False
        for move in scramble.split():
            if move == "y2": is_back = True; continue
            match = re.match(r"([a-zA-Z]+)(\d+)([+-])", move)
            if not match: continue
            cmd, val, sign = match.groups()
            delta = int(val) if sign == "+" else -int(val)
            
            if cmd in move_map:
                for clock_id in move_map[cmd]:
                    idx = clock_id - 1
                    if not is_back:
                        self.front.clock_values[idx] = (self.front.clock_values[idx] + delta - 1) % 12 + 1
                        if clock_id in mirror:
                            b_idx = mirror[clock_id] - 1
                            self.back.clock_values[b_idx] = (self.back.clock_values[b_idx] - delta - 1) % 12 + 1
                    else:
                        if clock_id in mirror:
                            b_idx = mirror[clock_id] - 1
                            f_idx = clock_id - 1
                            self.back.clock_values[b_idx] = (self.back.clock_values[b_idx] + delta - 1) % 12 + 1
                            self.front.clock_values[f_idx] = (self.front.clock_values[f_idx] - delta - 1) % 12 + 1
                        elif clock_id == 11:
                            self.back.clock_values[idx] = (self.back.clock_values[idx] + delta - 1) % 12 + 1

    def generate_single_scramble(self):
        f_moves = ["UR", "DR", "DL", "UL", "UM", "L", "U", "R", "DRw", "DLw", "ALL"]
        b_moves = ["L", "U", "R", "DRw", "DLw", "ALL"]
        def get_m(m):
            v = random.randint(0, 6); s = '+' if v in [0,6] else random.choice(['+','-'])
            return f"{m}{v}{s}"
        return f"{' '.join([get_m(m) for m in f_moves])} y2 {' '.join([get_m(m) for m in b_moves])}"

    def export_pdf(self):
        comp_name = self.comp_entry.get() or "Competition"
        mode = self.mode_var.get()
        num_rounds = int(self.round_count_var.get())
        round_names = ["Final"] if num_rounds == 1 else ["First Round", "Final"] if num_rounds == 2 else ["First Round", "Semi Final", "Final"]
        
        filename = f"{comp_name.replace(' ', '_')}_{mode}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        text_style = ParagraphStyle('ScrStyle', fontSize=8, leading=10)
        elements, temp_files = [], []
        
        for r_name in round_names:
            elements.append(Paragraph(f"<b>{comp_name}</b>", styles['Heading1']))
            elements.append(Paragraph(f"{r_name} - {mode} Scrambles", styles['Heading2']))
            elements.append(Spacer(1, 20))
            
            for i in range(7):
                label = f"{i+1}" if i < 5 else f"E{i-4}"
                self.change_mode(mode)
                scr = self.generate_single_scramble()
                self.apply_super_logic(scr)
                self.front.render_puzzle(); self.back.render_puzzle(); self.update()
                
                img_path = f"tmp_{r_name.replace(' ', '')}_{i}.png"
                x, y, w, h = self.container.winfo_rootx(), self.container.winfo_rooty(), self.container.winfo_width(), self.container.winfo_height()
                ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(img_path); temp_files.append(img_path)
                
                # GRID TABLE FORMAT
                data = [[Paragraph(f"<b>{label}</b>", styles['Normal']), 
                         Paragraph(scr.replace(" y2 ", "<br/>y2<br/>"), text_style), 
                         RLImage(img_path, width=280, height=130)]]
                t = Table(data, colWidths=[30, 160, 310])
                t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey),('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                elements.append(t); elements.append(Spacer(1, 10))
                
            elements.append(PageBreak())
        
        doc.build(elements)
        for f in temp_files:
            try: os.remove(f)
            except: pass
        self.status_label.configure(text=f"PDF Ready: {filename}")

if __name__ == "__main__":
    App().mainloop()