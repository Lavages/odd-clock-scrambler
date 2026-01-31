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
            self.body_color = "#ffffff"   
            self.face_color = "#f78fb3"   
            self.pin_color = "#f78fb3"    
            self.marker_color = "#2d3436" 
            self.ptr_color = "#2d3436"
        else:
            self.body_color = "#f78fb3"   
            self.face_color = "#ffffff"   
            self.pin_color = "#ffffff"    
            self.marker_color = "#2d3436" 
            self.ptr_color = "#f78fb3"

    def draw_pointer(self, cx, cy, radius, value):
        angle_rad = math.radians(value * 30 - 90)
        ptr_color = self.ptr_color
        tip_x, tip_y = cx + (radius - 12) * math.cos(angle_rad), cy + (radius - 12) * math.sin(angle_rad)
        base_w, angle_deg = 10, value * 30 - 90
        l_x, l_y = cx + base_w * math.cos(math.radians(angle_deg - 90)), cy + base_w * math.sin(math.radians(angle_deg - 90))
        r_x, r_y = cx + base_w * math.cos(math.radians(angle_deg + 90)), cy + base_w * math.sin(math.radians(angle_deg + 90))
        self.create_polygon(l_x, l_y, tip_x, tip_y, r_x, r_y, fill=ptr_color, outline="#2d3436", width=1, smooth=True)
        self.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#ffffff", outline="#2d3436", width=1)

    def render_puzzle(self):
        self.delete("all")
        mode = self.app.mode_var.get()
        if mode == "Triangular":
            main_r, lobe_r, lobe_pos = 230, 80, [(0, -185), (-190, 135), (190, 135)]
            pin_positions = [(0, -42), (-36.37, 21), (36.37, 21)]
            clock_pos = [(0, -185), (-110, -35), (110, -35), (-190, 135), (0, 135), (190, 135)]
            clock_r, marker_r = 52, 60
        else:
            lobe_dist, lobe_r, main_r = 195, 60, 225
            lobe_pos = [(lobe_dist * math.cos(math.radians(i * 72 - 90)), lobe_dist * math.sin(math.radians(i * 72 - 90))) for i in range(5)]
            pin_positions = [(65 * math.cos(math.radians(i * 72 - 18)), 65 * math.sin(math.radians(i * 72 - 18))) for i in range(5)]
            clock_pos = []
            for i in range(5): 
                a = math.radians(i * 72 - 90)
                clock_pos.append((190 * math.cos(a), 190 * math.sin(a)))
            for i in range(5): 
                a = math.radians(i * 72 - 54) 
                clock_pos.append((155 * math.cos(a), 155 * math.sin(a)))
            clock_r, marker_r = 40, 48

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
        for px, py in pin_positions:
            pcx, pcy = self.center + px, self.center + py
            out_c = "#2d3436" if self.is_front else "#ffffff"
            self.create_oval(pcx-18, pcy-18, pcx+18, pcy+18, fill=self.pin_color, outline=out_c, width=2)

        for i, (dx, dy) in enumerate(clock_pos):
            cx, cy = self.center + dx, self.center + dy
            self.create_oval(cx-clock_r, cy-clock_r, cx+clock_r, cy+clock_r, fill=self.face_color, outline="#f78fb3", width=1.5)
            for h in range(12):
                a = math.radians(h * 30 - 90)
                if h == 0: self.create_line(cx+(marker_r-4)*math.cos(a), cy+(marker_r-4)*math.sin(a), cx+(marker_r+4)*math.cos(a), cy+(marker_r+4)*math.sin(a), fill="#ff0066", width=4)
                else:
                    px, py = cx+marker_r*math.cos(a), cy+marker_r*math.sin(a)
                    self.create_oval(px-2, py-2, px+2, py+2, fill=self.marker_color, outline="")
            self.draw_pointer(cx, cy, clock_r, self.clock_values[i])

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Odd Clock Scrambler")
        self.geometry("1450x1000")
        self.configure(fg_color="#ffffff")

        self.mode_var = ctk.StringVar(value="Triangular")
        self.round_count_var = ctk.StringVar(value="1")
        
        self.container = ctk.CTkFrame(self, fg_color="#ffffff")
        self.container.pack(expand=True, pady=10)

        self.front = ClockPuzzle(self.container, self, is_front=True)
        self.front.grid(row=0, column=0, padx=30)
        self.back = ClockPuzzle(self.container, self, is_front=False)
        self.back.grid(row=0, column=1, padx=30)

        self.status_label = ctk.CTkLabel(self, text=f"Generated on {datetime.now().strftime('%B %d, %Y')}", text_color="#f78fb3", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=5)

        ctrl = ctk.CTkFrame(self, fg_color="#fdf2f5", corner_radius=20)
        ctrl.pack(fill="x", side="bottom", padx=50, pady=20)

        ctk.CTkLabel(ctrl, text="Competition Name:", text_color="#2d3436").pack(side="left", padx=(20, 5))
        self.comp_entry = ctk.CTkEntry(ctrl, placeholder_text="Pasig Open 2026", width=150)
        self.comp_entry.pack(side="left", padx=10)

        self.mode_menu = ctk.CTkOptionMenu(ctrl, values=["Triangular", "Pentagonal"], variable=self.mode_var, command=self.change_mode, fg_color="#f78fb3")
        self.mode_menu.pack(side="left", padx=10)

        ctk.CTkLabel(ctrl, text="Rounds:", text_color="#2d3436").pack(side="left", padx=5)
        self.round_menu = ctk.CTkOptionMenu(ctrl, values=["1", "2", "3", "4"], variable=self.round_count_var, fg_color="#f78fb3", width=80)
        self.round_menu.pack(side="left", padx=10)

        ctk.CTkButton(ctrl, text="GENERATE COMPETITION PDF", command=self.export_pdf, fg_color="#f78fb3", text_color="#ffffff", font=("Arial", 14, "bold")).pack(side="right", padx=20, pady=20)
        
        self.change_mode("Triangular")

    def change_mode(self, mode):
        count = 6 if mode == "Triangular" else 10
        self.front.clock_values = [12] * count
        self.back.clock_values = [12] * count
        self.front.render_puzzle()
        self.back.render_puzzle()

    def generate_scramble_set(self):
        return [self.generate_single_scramble() for _ in range(7)]

    def generate_single_scramble(self):
        if self.mode_var.get() == "Triangular":
            m1 = ["DR", "DL", "U", "R", "D", "L", "ALL"]; m2 = ["DR", "DL", "U", "ALL"]
        else:
            m1 = ["UR", "DR", "DL", "UL", "UM", "L", "U", "R", "DRw", "DLw", "ALL"]; m2 = ["L", "U", "R", "DRw", "DLw", "ALL"]
        f = lambda: f"{random.randint(0, 6)}{random.choice(['+', '-'])}"
        return f"{' '.join([m+f() for m in m1])} y2 {' '.join([m+f() for m in m2])}"

    def apply_logic(self, text):
        mode = self.mode_var.get()
        count = 6 if mode == "Triangular" else 10
        self.front.clock_values, self.back.clock_values = [12]*count, [12]*count
        is_back = False
        
        if mode == "Triangular":
            move_map = {"DR":[5,4,2], "DL":[3,4,1], "U":[0,1,2], "R":[0,1,2,4,5], "D":[1,2,3,4,5], "L":[0,1,2,3,4], "ALL":[0,1,2,3,4,5]}
            mirror, idx_map = {0:0, 3:5, 5:3}, {i:i for i in range(6)}
        else:
            idx_map = {1:0, 3:2, 5:4, 7:6, 9:8, 2:1, 4:3, 6:5, 8:7, 10:9}
            mirror = {0:0, 1:4, 2:3, 3:2, 4:1} 
            move_map = {'UR': [2,6,7], 'DR': [3,7,8], 'DL': [4,8,9], 'UL': [5,9,10], 'UM': [10,6,1], 'L': [5,4,9,10,1], 'U': [2,10,1,5,6], 'R': [1,2,3,6,7], 'DRw': [3,4,2,8,7], 'DLw': [5,4,3,8,9], 'ALL': [1,2,3,4,5,6,7,8,9,10]}
        
        for move in text.split():
            if move.lower() == 'y2': 
                is_back = True
                continue
            
            match = re.match(r"([A-Za-z]+)(\d+)([+\-−])", move)
            if not match: 
                continue
            
            cmd, val, sign = match.groups()
            delta = int(val) if sign in ['+', '+'] else -int(val)
            t, o = (self.back, self.front) if is_back else (self.front, self.back)
            
            if cmd in move_map:
                for target in move_map[cmd]:
                    idx = idx_map[target]
                    t.clock_values[idx] = (t.clock_values[idx] + delta - 1) % 12 + 1
                    if not is_back:
                        if idx in mirror:
                            o.clock_values[mirror[idx]] = (o.clock_values[mirror[idx]] - delta - 1) % 12 + 1
                    else:
                        inv = {v: k for k, v in mirror.items()}
                        if idx in inv:
                            o.clock_values[inv[idx]] = (o.clock_values[inv[idx]] - delta - 1) % 12 + 1

    def export_pdf(self):
        comp_name = self.comp_entry.get() or "Odd Clock Competition"
        mode = self.mode_var.get()
        num_rounds = int(self.round_count_var.get())
        
        if num_rounds == 1: round_names = ["Final"]
        elif num_rounds == 2: round_names = ["First Round", "Final"]
        elif num_rounds == 3: round_names = ["First Round", "Semi Final", "Final"]
        else: round_names = ["First Round", "Second Round", "Semi Final", "Final"]

        filename = f"{comp_name.replace(' ', '_')}_{mode}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        text_style = ParagraphStyle('ScrStyle', fontSize=8, leading=10)
        elements = []
        temp_files = []

        for r_name in round_names:
            elements.append(Paragraph(f"{comp_name} - {r_name}", styles['Heading1']))
            elements.append(Paragraph(f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
            elements.append(Spacer(1, 15))
            
            scrambles = self.generate_scramble_set()
            for i, scr in enumerate(scrambles):
                label = f"{i+1}" if i < 5 else f"E{i-4}"
                self.apply_logic(scr)
                self.front.render_puzzle()
                self.back.render_puzzle()
                self.update()
                
                img_path = f"tmp_{r_name.replace(' ', '')}_{i}.png"
                x, y, w, h = self.container.winfo_rootx(), self.container.winfo_rooty(), self.container.winfo_width(), self.container.winfo_height()
                ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(img_path)
                temp_files.append(img_path)
                
                data = [[
                    Paragraph(f"<b>{label}</b>", styles['Normal']), 
                    Paragraph(scr.replace(" y2 ", "<br/>y2<br/>"), text_style), 
                    RLImage(img_path, width=280, height=130)
                ]]
                t = Table(data, colWidths=[30, 160, 310])
                t.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
                ]))
                elements.append(t)
                elements.append(Spacer(1, 10))
            
            elements.append(PageBreak())

        doc.build(elements)
        
        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass
                
        self.status_label.configure(text=f"PDF Generated: {filename}")

if __name__ == "__main__":
    App().mainloop()