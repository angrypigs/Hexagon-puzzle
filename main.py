import tkinter as tk
import random
import time
from tkinter import font



class App:

    def __init__(self) -> None:
        # declare constants
        self.WIDTH = 700
        self.HEIGHT = 900
        self.OTHER_COLORS = [["#174872", "#2169A6"]]
        self.COLORS_PALETTE = [["", "#AC34F3", "#FBF8CC", "#90DBF4", "#FDE4CF",
                                "#98F5E1", "#FFCFD2", "#B9FBC0", "#CFBAF0"]]
        # declare variables
        self.board = [[0 for i in range(j)] for j in [4, 5, 6, 7, 6, 5, 4]]
        self.current_cell = [-1, -1]
        self.current_block = -1
        self.blocks_to_choose = [-1, -1, -1]
        self.unlocked_block = 2
        # init app
        self.master = tk.Tk()
        self.master.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.master.title("Hexagon puzzle")
        self.master.resizable(False, False)
        self.canvas = tk.Canvas(self.master, height=self.HEIGHT, width=self.WIDTH,
                                bd=0, highlightthickness=0, bg="#123C61")
        self.canvas.place(x=0,y=0)
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT,
                                     fill="#0C2A43", tags=("bg"))
        for i in range(4):
            for j in range(4+i):
                self.create_hexagon((7-i)*35+j*70, 200+60*i, (f"cell{i}_{j}"), 
                                    self.OTHER_COLORS[0][0])
        for i in range(4, 7):
            for j in range(10-i):
                self.create_hexagon((i+1)*35+j*70, 200+60*i, (f"cell{i}_{j}"), 
                                    self.OTHER_COLORS[0][0])
        self.master.bind("<B1-Motion>", self.motion_left_clicked)
        self.master.bind("<ButtonRelease-1>", self.block_released)
        self.generate_blocks()
        self.master.mainloop()

    def get_all_neighbors(self, a: int, b: int) -> list:
        """
        Returns a list of all valid adjacent cells
        """
        cells = [[a, b]]
        cells.extend([[a, b-1], [a, b+1]])
        if a<3: cells.extend([[a-1, b-1], [a-1, b], [a+1, b], [a+1, b+1]])
        elif a==3: cells.extend([[a-1, b-1], [a-1, b], [a+1, b-1], [a+1, b]])
        else: cells.extend([[a-1, b], [a-1, b+1], [a+1, b-1], [a+1, b]])
        return [x for x in cells if (x[0]>=0 and x[0]<7 and x[1]>=0 and
                                     x[1]<7-abs(x[0]-3))]

    def get_second_block(self, a: int, b: int, mode: int) -> list:
        """
        Returns coords of second hexagon in block
        """
        if mode==1: return [a, b-1]
        elif mode==2: return [a-1, b-1] if a <= 3 else [a-1, b]
        elif mode==3: return [a-1, b] if a <= 3 else [a-1, b+1]
        else: return [a, b]
    
    def check_if_fits(self, a: int, b: int, index: int) -> bool|list:
        c, d = self.get_second_block(a, b, self.blocks_to_choose[index][0])
        if (a>=0 and a<7 and b>=0 and b<7-abs(a-3) and 
                    c>=0 and c<7 and d>=0 and d<7-abs(c-3) and
                    self.board[a][b]==0 and self.board[c][d]==0):
            return [a, b, c, d]
        return False

    def create_hexagon(self, x: float, y: float, global_tags: tuple,  
                       color: str = "", text: str = "", size: float = 1, 
                       coords_tag: str = "") -> None:
        """
        Function to create hexagon-like polygon
        """
        tags_list2 = global_tags + (coords_tag, ) if coords_tag!="" else global_tags
        self.canvas.create_polygon([x, y-40*size, x+35*size, y-20*size, x+35*size, y+20*size,
                                    x, y+40*size, x-35*size, y+20*size, x-35*size, y-20*size],
                                    fill=color, tags=global_tags, width=2*size, outline="#000000")
        if text != "": self.canvas.create_text(x, y, text=text, state='disabled',
                                               justify='center', anchor='center',
                                               font=font.Font(size=int(20*size), family="Helvetica"),
                                               tags=global_tags)
            
    def create_hexagon_block(self, x: int, y: int, mode: int, numbers: list|int, 
                             global_tags: tuple, coords_tag: str = "") -> None:
        """
        Function to create single or double hexagon blocks ready to put in game
        """
        global_tags = tuple(global_tags.split(" "))
        if mode==0:
            self.create_hexagon(x, y, global_tags, self.COLORS_PALETTE[0][numbers], 
                                text=str(numbers), coords_tag=coords_tag)
        elif mode==1:
            self.create_hexagon(x+35, y, global_tags, text=str(numbers[0]), 
                                color=self.COLORS_PALETTE[0][numbers[0]], 
                                coords_tag=coords_tag)
            self.create_hexagon(x-35, y, global_tags, text=str(numbers[1]), 
                                color=self.COLORS_PALETTE[0][numbers[1]])
        elif mode==2:
            self.create_hexagon(x, y, global_tags, text=str(numbers[0]), 
                                color=self.COLORS_PALETTE[0][numbers[0]], 
                                coords_tag=coords_tag)
            self.create_hexagon(x-35, y-60, global_tags, text=str(numbers[1]), 
                                color=self.COLORS_PALETTE[0][numbers[1]])
        elif mode==3:
            self.create_hexagon(x, y, global_tags, text=str(numbers[0]), 
                                color=self.COLORS_PALETTE[0][numbers[0]], 
                                coords_tag=coords_tag)
            self.create_hexagon(x+35, y-60, global_tags, text=str(numbers[1]), 
                                color=self.COLORS_PALETTE[0][numbers[1]])

    def generate_blocks(self, index: int = -1, block: list = []) -> None:
        """
        Generate three blocks under the gridcell or the specific one
        """
        if index == -1:
            link = lambda x: (lambda event: self.block_icon_input(x))
            for i in range(3):
                self.blocks_to_choose[i] = [random.randint(0, 3)]
                if self.blocks_to_choose[i][0] != 0:
                    self.blocks_to_choose[i].extend(random.sample(range(1, self.unlocked_block+1), 2))
                else:
                    self.blocks_to_choose[i].append(random.choice(range(1, self.unlocked_block+1)))
                l = self.blocks_to_choose[i][1] if self.blocks_to_choose[i][0] == 0 else self.blocks_to_choose[i][1:]
                self.create_hexagon_block(self.WIDTH//4*(i+1), self.HEIGHT-100,
                                          self.blocks_to_choose[i][0], l, 
                                          (f"block{i}"), f"block{i}_coords")
                self.canvas.tag_bind(f"block{i}", "<Button-1>", link(i))

    def reset_gridcell(self) -> None:
        for i in range(7):
            for j in range(7-abs(i-3)):
                self.canvas.itemconfig(f"cell{i}_{j}", fill=self.OTHER_COLORS[0][0])

    def block_icon_input(self, index: int) -> None:
        self.current_block = index
        self.canvas.tag_raise(f"block{index}")

    def motion_left_clicked(self, event) -> None:
        if self.current_block != -1:
            self.canvas.move(f"block{self.current_block}", 
                             event.x-self.canvas.coords(f"block{self.current_block}")[0], 
                             event.y-self.canvas.coords(f"block{self.current_block}")[1]-100)
            tag = self.canvas.itemcget(self.canvas.find_closest(event.x, event.y), "tags").split()[0]
            if "cell" in tag:
                if [int(tag[4]), int(tag[6])] != self.current_cell and self.check_if_fits(
                    int(tag[4]), int(tag[6]), self.current_block)!=False:
                    a, b, = int(tag[4]), int(tag[6])
                    c, d = self.get_second_block(a, b, self.blocks_to_choose[self.current_block][0])
                    self.reset_gridcell()
                    self.canvas.itemconfig(f"cell{a}_{b}", fill=self.OTHER_COLORS[0][1])
                    self.canvas.itemconfig(f"cell{c}_{d}", fill=self.OTHER_COLORS[0][1])
                    self.current_cell = [int(tag[4]), int(tag[6])]
            else:
                if self.current_cell != [-1, -1]:
                    self.current_cell = [-1, -1]
                    self.reset_gridcell()
            

            

    def block_released(self, event) -> None:
        if self.current_block != -1:
            if self.current_cell != [-1, -1]:
                a, b = self.current_cell
                c, d = self.get_second_block(
                            self.current_cell[0], self.current_cell[1],
                            self.blocks_to_choose[self.current_block][0])
                if (a>=0 and a<7 and b>=0 and b<7-abs(a-3) and 
                            c>=0 and c<7 and d>=0 and d<7-abs(a-3) and
                            self.board[a][b]==0 and self.board[c][d]==0):
                    self.canvas.delete(f"block{self.current_block}")
                    self.board[a][b] = self.blocks_to_choose[self.current_block][1]
                    e, f = self.blocks_to_choose[self.current_block][1], -1
                    if [a, b]!=[c, d]:
                        self.board[c][d] = self.blocks_to_choose[self.current_block][2]
                        f = self.blocks_to_choose[self.current_block][2]
                    k = 7-a if a<=3 else a+1
                    self.create_hexagon(k*35+b*70, 200+60*a, 
                                        f"block_placed{a}_{b}", 
                                        color=self.COLORS_PALETTE[0][e],
                                        text=str(e))
                    if f!=-1: 
                        k = 7-c if c<=3 else c+1
                        self.create_hexagon(k*35+d*70, 200+60*c, 
                                        f"block_placed{c}_{d}", 
                                        color=self.COLORS_PALETTE[0][f],
                                        text=str(f))
                    self.blocks_to_choose[self.current_block] = -1
                    if self.blocks_to_choose.count(-1)==3:
                        self.generate_blocks()
            else:
                self.canvas.move(f"block{self.current_block}", 
                                self.WIDTH//4*(self.current_block+1)-event.x, self.HEIGHT-40-event.y)
            self.reset_gridcell()
            self.current_block = -1

if __name__ == "__main__":
    app = App() 