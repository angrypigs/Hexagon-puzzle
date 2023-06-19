import tkinter as tk
import random
import time
from tkinter import font



class App:

    def __init__(self) -> None:
        # declare constants
        self.WIDTH = 700
        self.HEIGHT = 900
        # declare variables
        self.board = [[0 for i in range(j)] for j in [4, 5, 6, 7, 6, 5, 4]]
        self.current_cell = [-1, -1]
        # init app
        self.master = tk.Tk()
        self.master.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.master.title("Hexagon puzzle")
        self.master.resizable(False, False)
        self.canvas = tk.Canvas(self.master, height=self.HEIGHT, width=self.WIDTH,
                                bd=0, highlightthickness=0, bg="#123C61")
        self.canvas.place(x=0,y=0)
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT,
                                     fill="#0C2A43", tags="bg")
        self.canvas.tag_bind("bg", "<Enter>", lambda event: self.background_event())
        link = lambda x, y: (lambda event: self.cell_input(event, x, y))
        for i in range(4):
            for j in range(4+i):
                self.create_hexagon((7-i)*35+j*70, 200+60*i, "#174D7B", (), tags_bind=f"cell{i}_{j}")
                self.canvas.tag_bind(f"cell{i}_{j}", "<Enter>", link(i, j))
        for i in range(4, 7):
            for j in range(10-i):
                self.create_hexagon((i+1)*35+j*70, 200+60*i, "#174D7B", (), tags_bind=f"cell{i}_{j}")
                self.canvas.tag_bind(f"cell{i}_{j}", "<Enter>", link(i, j))
                

        self.master.mainloop()

    def create_hexagon(self, x: float, y: float, color: str, 
                       tags_list: tuple, text: str = "", tags_bind: str = "", size: float = 1) -> None:
        """
        Function to create hexagon-like polygon
        """
        tags_list2 = tags_list + (tags_bind, ) if tags_bind != "" else tags_list
        self.canvas.create_polygon([x, y-40*size, x+35*size, y-20*size, x+35*size, y+20*size,
                                    x, y+40*size, x-35*size, y+20*size, x-35*size, y-20*size],
                                    fill=color, tags=tags_list2, width=2*size, outline="#000000")
        if text != "": self.canvas.create_text(x, y, text=text, state='disabled',
                                               justify='center', anchor='center',
                                               font=font.Font(size=int(20*size), family="Helvetica"),
                                               tags=tags_list)

    def background_event(self) -> None:
        print("lol")

    def cell_input(self, event, a: int, b: int) -> None:
        print(event)
        print(a, b)

if __name__ == "__main__":
    app = App() 