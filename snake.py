import tkinter as tk
import random
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

SIRKA = 500
VYSKA = 580
VELIKOST_BUNKY = 20
PADDING = 10
SPODNI_OKRAJ = 30

class SnakeGame:
    def __init__(self, okno):
        self.okno = okno
        self.okno.title("Snake")
        self.okno.configure(bg="black")
        self.okno.geometry(f"{SIRKA}x{VYSKA}")
        self.okno.resizable(False, False)
        self.blikajici_skore = 0

        self.platno = tk.Canvas(self.okno, width=SIRKA, height=VYSKA, bg="black", highlightthickness=0)
        self.platno.pack()

        self.reset_hra()
        self.menu_okno()

    def reset_hra(self):
        self.smer = "Right"
        self.novy_smer = "Right"
        self.had = []
        self.jidlo = None
        self.hra_bezi = False
        self.konec = False
        self.skore = 0
        self.highscore = 0
        self.zakladni_rychlost = 120
        self.min_rychlost = 50
        self.rychlost = self.zakladni_rychlost
        self.animace_menu_id = None

    def menu_okno(self):
        self.platno.delete("all")
        self.animace_menu()

        self.platno.create_text(SIRKA//2, VYSKA//4, text="🐍 SNAKE 🐍", fill="lime", font=("Arial", 40, "bold"))
        self.vytvor_tlacitko("PLAY", self.start_hry, VYSKA//2)
        self.vytvor_tlacitko("QUIT", self.okno.quit, VYSKA//2 + 80)

    def vytvor_tlacitko(self, text, command, y):
        btn = tk.Button(
            self.okno,
            text=text,
            font=("Arial", 18, "bold"),
            bg="#111111",
            fg="lime",
            activebackground="#222222",
            activeforeground="white",
            command=command,
            relief="flat",
            highlightthickness=0
        )
        self.platno.create_window(SIRKA//2, y, window=btn, width=200, height=50)

    def animace_menu(self):
        self.platno.delete("animace")
        for _ in range(50):
            x = random.randint(0, SIRKA)
            y = random.randint(0, VYSKA)
            r = random.randint(1, 2)
            self.platno.create_oval(x, y, x+r, y+r, fill="gray30", outline="", tags="animace")
        self.animace_menu_id = self.okno.after(150, self.animace_menu)

    def start_hry(self):
        if self.animace_menu_id:
            self.okno.after_cancel(self.animace_menu_id)

        self.platno.delete("all")
        self.odstran_tlacitka()

        self.had = [(PADDING + 100, PADDING + 100), (PADDING + 80, PADDING + 100), (PADDING + 60, PADDING + 100)]
        self.smer = self.novy_smer = "Right"
        self.konec = False
        self.hra_bezi = True
        self.skore = 0
        self.rychlost = self.zakladni_rychlost
        self.vytvor_jidlo()
        self.kresli()
        self.pohyb()

    def odstran_tlacitka(self):
        for widget in self.okno.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

    def kresli(self):
        self.platno.delete("all")
        self.kresli_mrizku()

        for idx, (x, y) in enumerate(self.had):
            barva = "#00ff00" if idx == 0 else "#007700"
            self.platno.create_oval(x + 2, y + 2, x + VELIKOST_BUNKY - 2, y + VELIKOST_BUNKY - 2, fill=barva,
                                    outline="black")

        if self.jidlo:
            jx, jy = self.jidlo
            self.platno.create_oval(jx + 2, jy + 2, jx + VELIKOST_BUNKY - 2, jy + VELIKOST_BUNKY - 2, fill="red",
                                    outline="black")

        if self.blikajici_skore > 0:
            barva_textu = "yellow"
            self.blikajici_skore -= 1
        else:
            barva_textu = "white"

        score_text = f"SCORE: {self.skore}   |   HIGHSCORE: {self.highscore}"
        self.platno.create_text(SIRKA // 2, VYSKA - SPODNI_OKRAJ // 2, text=score_text, fill=barva_textu,
                                font=("Arial", 14, "bold"))

    def kresli_mrizku(self):
        for i in range(PADDING, SIRKA - PADDING + 1, VELIKOST_BUNKY):
            self.platno.create_line(i, PADDING, i, VYSKA - SPODNI_OKRAJ, fill="gray25")
        for i in range(PADDING, VYSKA - SPODNI_OKRAJ + 1, VELIKOST_BUNKY):
            self.platno.create_line(PADDING, i, SIRKA - PADDING, i, fill="gray25")

    def vytvor_jidlo(self):
        while True:
            x = random.randint(0, (SIRKA - 2*PADDING - VELIKOST_BUNKY) // VELIKOST_BUNKY) * VELIKOST_BUNKY + PADDING
            y = random.randint(0, (VYSKA - SPODNI_OKRAJ - 2*PADDING - VELIKOST_BUNKY) // VELIKOST_BUNKY) * VELIKOST_BUNKY + PADDING
            if (x, y) not in self.had:
                self.jidlo = (x, y)
                break

    def pohyb(self):
        if not self.hra_bezi or self.konec:
            return

        self.smer = self.novy_smer
        x, y = self.had[0]

        if self.smer == "Up":
            y -= VELIKOST_BUNKY
        elif self.smer == "Down":
            y += VELIKOST_BUNKY
        elif self.smer == "Left":
            x -= VELIKOST_BUNKY
        elif self.smer == "Right":
            x += VELIKOST_BUNKY

        nova_hlava = (x, y)

        if (
            x < PADDING or x >= SIRKA - PADDING or
            y < PADDING or y >= VYSKA - SPODNI_OKRAJ or
            nova_hlava in self.had
        ):
            self.konec = True
            self.hra_bezi = False
            self.end_screen()
            return

        self.had.insert(0, nova_hlava)

        if nova_hlava == self.jidlo:
            self.skore += 1
            self.blikajici_skore = 5
            self.highscore = max(self.highscore, self.skore)
            self.vytvor_jidlo()
            if self.rychlost > self.min_rychlost:
                self.rychlost -= 1.5
        else:
            self.had.pop()

        self.kresli()
        self.okno.after(int(self.rychlost), self.pohyb)

    def end_screen(self):
        self.platno.delete("all")
        self.platno.configure(bg="black")

        self.platno.create_text(SIRKA//2, VYSKA//4, text="GAME OVER", fill="red", font=("Arial", 40, "bold"))
        self.platno.create_text(SIRKA//2, VYSKA//4 + 70, text=f"SCORE: {self.skore}", fill="red", font=("Arial", 20, "bold"))

        self.vytvor_tlacitko_konec("RESTART", self.start_hry, VYSKA//2)
        self.vytvor_tlacitko_konec("MENU", self.menu_okno, VYSKA//2 + 80)

    def vytvor_tlacitko_konec(self, text, command, y):
        btn = tk.Button(
            self.okno,
            text=text,
            font=("Arial", 18, "bold"),
            bg="#111111",
            fg="red",
            activebackground="#222222",
            activeforeground="white",
            command=command,
            relief="flat",
            highlightthickness=0
        )
        self.platno.create_window(SIRKA//2, y, window=btn, width=200, height=50)

    def zmen_smer(self, event):
        nove_smerovani = event.keysym
        opacny_smer = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if nove_smerovani in opacny_smer and opacny_smer[nove_smerovani] != self.smer:
            self.novy_smer = nove_smerovani

if __name__ == "__main__":
    okno = tk.Tk()
    okno.iconbitmap("snake.ico")
    frame = tk.Frame(okno, bg='black')
    hra = SnakeGame(okno)
    okno.bind("<KeyPress>", hra.zmen_smer)
    okno.mainloop()