import tkinter as tk
import threading as th
import random
import time
from tkinter import font
from operator import itemgetter



class App:

    def __init__(self) -> None:
        # declare constants
        self.WIDTH = 700
        self.HEIGHT = 900
        self.CURRENT_FONT = "Gill Sans MT"
        self.OTHER_COLORS = [["#174872", "#2169A6"]]
        self.COLORS_PALETTE = [["", "#A621F4", "#F4EA53", "#44C7F3", "#F38930",
                                "#49E9C6", "#F23F4A", "#48DA57", "#8F53EE"]]
        # declare variables
        self.board = [[0 for i in range(j)] for j in [4, 5, 6, 7, 6, 5, 4]]
        self.current_cell = [-1, -1]
        self.current_block = -1
        self.blocks_to_choose = [-1, -1, -1]
        self.unlocked_block = 2
        self.flag_working = True
        self.flag_animation = False
        self.points = 0
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
        # create cells
        for i in range(4):
            for j in range(4+i):
                self.create_hexagon((7-i)*35+j*70, 200+60*i, (f"cell{i}_{j}"), 
                                    self.OTHER_COLORS[0][0])
        for i in range(4, 7):
            for j in range(10-i):
                self.create_hexagon((i+1)*35+j*70, 200+60*i, (f"cell{i}_{j}"), 
                                    self.OTHER_COLORS[0][0])
        # create texts
        self.canvas.create_text(20, 16, justify='left', anchor='nw', text="Score: 0", fill="#FFFFFF",
                                font=font.Font(family=self.CURRENT_FONT, size=24, weight='bold'),
                                state='disabled', tags=("points_main"))
        self.canvas.create_text(20, 60, justify='left', anchor='nw', text="Highscore: 0", fill="#FFFFFF",
                                font=font.Font(family=self.CURRENT_FONT, size=12, weight='bold'),
                                state='disabled', tags=("points_highscore"))
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

    def find_all_same(self, a: int, b: int) -> list:
        """
        Return a list of all cells which are connected to main cell or to themselves 
        and have same value
        """ 
        cells = [[a, b]]
        n = 1
        while True:
            for k in cells:
                cells.extend([x for x in self.get_all_neighbors(k[0], k[1])
                                if self.board[x[0]][x[1]]==self.board[a][b]!=0
                                and x not in cells])
            if len(cells)==n: break
            else: n = len(cells)
        return cells

    def create_hexagon(self, x: float, y: float, global_tags: tuple,  
                       color: str = "", text: str = "", size: float = 1, 
                       coords_tag: str = "") -> None:
        """
        Function to create hexagon-like polygon
        """
        tags_list2 = global_tags + (coords_tag, ) if coords_tag!="" else global_tags
        self.canvas.create_polygon([x, y-40*size, x+35*size, y-20*size, x+35*size, y+20*size,
                                    x, y+40*size, x-35*size, y+20*size, x-35*size, y-20*size],
                                    fill=color, tags=global_tags, width=3*size, outline="#000000")
        if text != "": self.canvas.create_text(x, y, text=text, state='disabled',
                                               justify='center', anchor='center',
                                               font=font.Font(size=int(20*size), 
                                                              family=self.CURRENT_FONT, weight='bold'),
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
                self.blocks_to_choose[i] = [random.choice([0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 3, 3])]
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

    def matching_blocks_anim(self, c_from: list, c_to: list) -> None:
        """
        Little animation for "matching" blocks
        """
        self.canvas.tag_raise(f"block_placed{c_to[0]}_{c_to[1]}")
        # get coords of two blocks on gridcell
        k = 7-c_from[0] if c_from[0] < 4 else c_from[0]+1
        c1_from = [k*35+c_from[1]*70, 200+60*c_from[0]]
        k = 7-c_to[0] if c_to[0] < 4 else c_to[0]+1
        c1_to = [k*35+c_to[1]*70, 200+60*c_to[0]]
        for i in range(15):
            self.canvas.move(f"block_placed{c_from[0]}_{c_from[1]}",
                             (c1_to[0]-c1_from[0])//15, (c1_to[1]-c1_from[1])//15)
            time.sleep(0.001)
            self.canvas.update()
        self.canvas.delete(f"block_placed{c_from[0]}_{c_from[1]}")

    def points_charger_anim(self, tag: str, start: int, stop: int, 
                            steps: int = 10, 
                            start_text: str = "", stop_text: str = "") -> None:  
        """
        Animation to go smoothly from start to stop value in text widget
        """
        self.flag_animation = True
        for i in range(steps+1):
            self.canvas.itemconfig(tag, 
                text=start_text+str(int(start+(stop-start)*i/steps))+stop_text)
            time.sleep(0.001)
            self.canvas.update()
        self.flag_animation = False

    def block_icon_input(self, index: int) -> None:
        """
        Method connected to blocks icons
        """
        if not self.flag_animation:
            self.current_block = index
            self.canvas.tag_raise(f"block{index}")

    def motion_left_clicked(self, event) -> None:
        """
        Method connected to mouse move with left button pressed bind (<B1-Motion>)
        """
        if self.current_block != -1 and not self.flag_animation:
            self.canvas.move(f"block{self.current_block}", 
                             event.x-self.canvas.coords(f"block{self.current_block}")[0], 
                             event.y-self.canvas.coords(f"block{self.current_block}")[1]-85)
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
        """
        Method connected to left button release
        """
        if self.current_block != -1 and not self.flag_animation:
            self.flag_animation = True
            if self.current_cell != [-1, -1]:
                # get coords of both possible cells
                a, b = self.current_cell
                c, d = self.get_second_block(
                            self.current_cell[0], self.current_cell[1],
                            self.blocks_to_choose[self.current_block][0])
                # check if block fits in gridcell
                if (a>=0 and a<7 and b>=0 and b<7-abs(a-3) and 
                            c>=0 and c<7 and d>=0 and d<7-abs(c-3) and
                            self.board[a][b]==0 and self.board[c][d]==0):
                    self.canvas.delete(f"block{self.current_block}")
                    self.board[a][b] = self.blocks_to_choose[self.current_block][1]
                    # get number (numbers) of block
                    e, f = self.blocks_to_choose[self.current_block][1], -1
                    if [a, b]!=[c, d]:
                        self.board[c][d] = self.blocks_to_choose[self.current_block][2]
                        f = self.blocks_to_choose[self.current_block][2]
                    k = 7-a if a<=3 else a+1
                    # create blocks on gridcell
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
                    combo_counter = 0
                    points_counter = 0
                    while True:
                        flags = [False, False]
                        if len(self.find_all_same(a, b))>2: flags[0]=True
                        if len(self.find_all_same(c, d))>2: flags[1]=True
                        if not flags[0] and not flags[1]:
                            break
                        else:
                            combo_counter += 1
                            if flags[0] and not flags[1]: cell_main = [a, b]
                            elif flags[1] and not flags[0]: cell_main = [c, d]
                            else: cell_main = [a, b] if self.board[a][b]<self.board[c][d] else [c, d]
                            cells = self.find_all_same(cell_main[0], cell_main[1])
                            cells = sorted(cells, key=itemgetter(0))
                            # list for same cells around main cell
                            cells_divided = [[], [], []]
                            # divide same cells into that around main cell and further ones
                            for k in cells:
                                if k != cell_main:
                                    if cell_main in self.get_all_neighbors(k[0], k[1]):
                                        cells_divided[0].append(k)
                                    else:
                                        cells_divided[1].append(k)
                            # check for cells which are two cells away main cell
                            for i in cells_divided[1]:
                                flag = True
                                for j in cells_divided[0]:
                                    if j in self.get_all_neighbors(i[0], i[1]):
                                        flag = False
                                        break
                                if flag:
                                    cells_divided[2].append(i)
                                    cells_divided[1].remove(i)
                                    break
                            # match cells which are two cells away main cell
                            # with those which are one cell away
                            for i in cells_divided[2]:
                                for j in cells_divided[1]:
                                    if j in self.get_all_neighbors(i[0], i[1]):
                                        self.board[i[0]][i[1]]=0
                                        self.matching_blocks_anim(i, j)
                                        break
                            # match cells which are two cells away main cell
                            # with those which are one cell away
                            for i in cells_divided[1]:
                                for j in cells_divided[0]:
                                    if j in self.get_all_neighbors(i[0], i[1]):
                                        self.board[i[0]][i[1]]=0
                                        self.matching_blocks_anim(i, j)
                                        break
                            # match cells which are around main cell 
                            # with main one
                            for i in cells_divided[0]:
                                self.board[i[0]][i[1]]=0
                                self.matching_blocks_anim(i, cell_main)
                            cell_type = self.board[cell_main[0]][cell_main[1]]
                            if self.board[cell_main[0]][cell_main[1]]<8:
                                self.board[cell_main[0]][cell_main[1]]+=1
                            if (self.board[cell_main[0]][cell_main[1]]>self.unlocked_block
                                and self.unlocked_block<7):
                                self.unlocked_block+=1
                            # delete old block and create new
                            if self.board[cell_main[0]][cell_main[1]]!=8:
                                self.canvas.delete(f"block_placed{cell_main[0]}_{cell_main[1]}")
                            k = 7-cell_main[0] if cell_main[0]<=3 else cell_main[0]+1
                            self.create_hexagon(k*35+cell_main[1]*70, 200+60*cell_main[0], 
                                        f"block_placed{cell_main[0]}_{cell_main[1]}", 
                                        color=self.COLORS_PALETTE[0][self.board[cell_main[0]][cell_main[1]]],
                                        text=str(self.board[cell_main[0]][cell_main[1]]))
                            self.canvas.update()
                            # optional breaking blocks around if block is 8th one
                            if self.board[cell_main[0]][cell_main[1]]==8:
                                l = [x for x in self.get_all_neighbors(cell_main[0], cell_main[1])
                                     if self.board[x[0]][x[1]]!=0 and x!=cell_main]
                                self.board[cell_main[0]][cell_main[1]]=0
                                for i in l:
                                    self.matching_blocks_anim(i, cell_main)
                                    points_counter += self.board[i[0]][i[1]]
                                    self.board[i[0]][i[1]]=0
                                self.canvas.delete(f"block_placed{cell_main[0]}_{cell_main[1]}")
                                self.canvas.update()
                            points_counter += len(cells)*cell_type
                    points_counter *= combo_counter                 
                    self.points += points_counter
                    if points_counter>0: self.points_charger_anim("points_main", 
                        self.points-points_counter, self.points, start_text="Score: ")  

                    self.blocks_to_choose[self.current_block] = -1
                    if self.blocks_to_choose.count(-1)==3:
                        self.generate_blocks()
            else:
                self.canvas.move(f"block{self.current_block}", 
                                self.WIDTH//4*(self.current_block+1)-event.x, self.HEIGHT-50-event.y)
            self.reset_gridcell()
            self.current_block = -1
            self.flag_animation = False

if __name__ == "__main__":
    app = App()