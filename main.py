import tkinter as tk
import threading as th
import random
import time
from tkinter import font
from operator import itemgetter
import os
import sys



class App:

    def __init__(self) -> None:
        # declare constants
        self.WIDTH = 700
        self.HEIGHT = 900
        self.CURRENT_FONT = "Gill Sans MT"
        # colors for GUIs (0 - bg, 1 - windows bg)
        self.GUI_COLORS = [["#0C2A43", "#103A5C"]]
        # colors for cells
        self.COLORS_PALETTE = [["", "#A621F4", "#F4EA53", "#44C7F3", "#F38930",
                                "#49E9C6", "#F23F4A", "#48DA57", "#8F53EE"]]
        # other colors (0 - normal cell, 1 - active cell)
        self.OTHER_COLORS = [["#174872", "#2169A6"]]
        # declare variables
        self.board = [[0 for i in range(j)] for j in [4, 5, 6, 7, 6, 5, 4]]
        self.current_cell = [-1, -1]
        self.current_block = -1
        self.current_powerup = 0
        self.blocks_to_choose = [-1, -1, -1]
        self.unlocked_block = 2
        self.flag_menu = False
        self.flag_animation = False
        self.flag_close = False
        self.flag_erase = False
        self.points = 0
        self.highscore_points = 0
        # load game save if it exists
        if os.path.exists(os.path.join(sys.path[0], "save.txt")):
            if not self.load_data():
                self.board = [[0 for i in range(j)] for j in [4, 5, 6, 7, 6, 5, 4]]
                self.blocks_to_choose = [-1, -1, -1]
                self.points = 0
                self.highscore_points = 0
        # init app
        self.master = tk.Tk()
        self.master.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.master.title("Hexagon puzzle")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.close_app)
        self.canvas = tk.Canvas(self.master, height=self.HEIGHT, width=self.WIDTH,
                                bd=0, highlightthickness=0, bg="#123C61")
        self.canvas.place(x=0,y=0)
        self.normal_font = lambda s, w: font.Font(family=self.CURRENT_FONT, size=s, weight=w)
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT,
                                     fill=self.GUI_COLORS[0][0], tags=("bg"))
        # create cells
        for i in range(7):
            for j in range(7-abs(i-3)):
                k = 7-i if i<=3 else i+1
                self.create_hexagon(k*35+j*70, 200+60*i, (f"cell{i}_{j}"), 
                                    self.OTHER_COLORS[0][0])
                if self.board[i][j]!=0:
                    self.create_gridcell_block(i, j)
        # create texts
        self.canvas.create_text(20, 16, justify='left', anchor='nw', 
                                text=f"Score: {self.points}", fill="#FFFFFF",
                                font=self.normal_font(24, 'bold'),
                                state='disabled', tags=("points_main"))
        self.canvas.create_text(20, 60, justify='left', anchor='nw', 
                                text=f"Highscore: {self.highscore_points}", 
                                fill="#FFFFFF", font=self.normal_font(12, 'bold'),
                                state='disabled', tags=("points_highscore"))
        help_list = [["erase_btn", "dump_btn", "reroll_btn"], ["\u2716", "\U0001F5D1", '\U0001F3B2']]
        for i in range(3):
            self.canvas.create_oval(0.6*self.WIDTH+i*90, 40,
                                    0.6*self.WIDTH+i*90+60, 100,
                                    fill=self.OTHER_COLORS[0][0], width=3,
                                    tags=(help_list[0][i]))
            self.canvas.create_text(0.6*self.WIDTH+i*90+30, 70,
                                    justify='center', anchor='center',
                                    font=self.normal_font(24, 'normal'),
                                    text=help_list[1][i], state='disabled', 
                                    tags=(help_list[0][i]+"text"))
        self.master.bind("<B1-Motion>", self.motion_left_clicked)
        self.master.bind("<ButtonRelease-1>", self.block_released)
        def turn_on_erase() -> None: 
            self.flag_erase = not self.flag_erase
            self.buttons_highlight(self.flag_erase, "erase_btn")
        self.canvas.tag_bind(help_list[0][0], "<Button-1>", lambda e: turn_on_erase())
        self.canvas.tag_bind(help_list[0][2], "<Button-1>", lambda e: self.reroll_cells())
        for i in range(3):
            if self.blocks_to_choose[i]!=-1:
                self.generate_blocks(i, self.blocks_to_choose[i])
        self.canvas.update()
        self.lose_check()
        self.master.mainloop()

    def res_path(self, rel_path: str) -> str:
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = sys.path[0]
        return os.path.join(base_path, rel_path)

    # hexagon matrix handling methods

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

    # generating hexagon blocks methods

    def create_hexagon(self, x: float, y: float, global_tags: tuple,  
                       color: str = "", text: str = "", size: float = 1, 
                       coords_tag: str = "") -> None:
        """
        Creates hexagon-like polygon
        """
        tags_list2 = global_tags + (coords_tag, ) if coords_tag!="" else global_tags
        self.canvas.create_polygon([x, y-40*size, x+35*size, y-20*size, x+35*size, y+20*size,
                                    x, y+40*size, x-35*size, y+20*size, x-35*size, y-20*size],
                                    fill=color, tags=global_tags, width=3*size, outline="#000000")
        if text != "": self.canvas.create_text(x, y, text=text, state='disabled',
                                               justify='center', anchor='center',
                                               font=self.normal_font(int(20*size), 'bold'), 
                                               tags=global_tags)
            
    def create_hexagon_block(self, x: int, y: int, mode: int, numbers: list|int, 
                             global_tags: tuple, coords_tag: str = "") -> None:
        """
        Creates single or double hexagon blocks ready to put in game
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
        Generates three blocks under the gridcell or the specific one
        """
        link = lambda x: (lambda event: self.block_icon_input(x))
        if index == -1:
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
        else:
            self.create_hexagon_block(self.WIDTH//4*(index+1), self.HEIGHT-100,
                                            block[0], block[1] if block[0]==0 else block[1:],
                                          (f"block{index}"), f"block{index}_coords")
            self.canvas.tag_bind(f"block{index}", "<Button-1>", link(index))

    def create_gridcell_block(self, a: int, b: int) -> None:
        """
        Creates a block over the gridcell at given coords
        """
        k = 7-a if a<=3 else a+1
        self.create_hexagon(k*35+b*70, 200+60*a, 
                    f"block_placed{a}_{b}", 
                    color=self.COLORS_PALETTE[0][self.board[a][b]],
                    text=str(self.board[a][b]))
        self.canvas.tag_bind(f"block_placed{a}_{b}", "<Button-1>",
                             lambda e: self.cell_left_click(a, b))

    # other methods (cosmetical, game status)

    def buttons_highlight(self, on_off: bool, tag: str = "") -> None:
        help_list = ["erase_btn", "dump_btn", "reroll_btn"]
        color = self.OTHER_COLORS[0][1] if on_off else self.OTHER_COLORS[0][0]
        if tag == "":
            for i in help_list:
                self.canvas.itemconfig(i, fill=color)
                self.canvas.tag_raise(i+"text")
        else: 
            self.canvas.itemconfig(tag, fill=color)
            self.canvas.tag_raise(tag+"text")

    def reset_gridcell(self) -> None:
        """
        Resets highlight of all cells
        """
        for i in range(7):
            for j in range(7-abs(i-3)):
                self.canvas.itemconfig(f"cell{i}_{j}", fill=self.OTHER_COLORS[0][0])

    def lose_check(self) -> None:
        """
        Checks if game is over; if yes, creates lose window with button to play again
        """
        for k in [x for x in range(3) if self.blocks_to_choose[x] !=-1]:
            for i in range(7):
                for j in range(7-abs(i-3)):
                    if self.check_if_fits(i, j, k)!=False:
                        return
        self.flag_menu = True
        self.canvas.create_rectangle(self.WIDTH//2-150, self.HEIGHT//2-100,
                                     self.WIDTH//2+150, self.HEIGHT//2+100,
                                     fill=self.GUI_COLORS[0][1], tags=("lose_panel"))
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2-50,
                                justify='center', anchor='center',
                                font=self.normal_font(30, 'normal'),
                                text="Game over", tags=("lose_panel"))
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2,
                                justify='center', anchor='center',
                                font=self.normal_font(20, 'normal'),
                                text=f"Score: {self.points-1000 if self.points>1000 else 0}", 
                                tags=("lose_panel", "lose_score"))
        self.canvas.create_rectangle(self.WIDTH//2-90, self.HEIGHT//2+30,
                                     self.WIDTH//2+90, self.HEIGHT//2+70,
                                     fill=self.OTHER_COLORS[0][0],
                                     tags=("lose_panel", "lose_resume_btn"))
        self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2+50,
                                justify='center', anchor='center',
                                font=self.normal_font(20, 'normal'),
                                text="Resume game", 
                                tags=("lose_panel"), state='disabled')
        self.points_charger_anim("lose_score", self.points-1000, self.points,
                                 start_text="Score: ", steps=25)
        self.canvas.tag_bind("lose_resume_btn", "<Button-1>", 
                             lambda event: self.new_game())

    def new_game(self) -> None:
        """
        Deletes all old elements and generate all from beginning
        """
        self.canvas.delete("lose_panel")
        for i in range(7):
            for j in range(7-abs(i-3)):
                self.board[i][j]=0
                self.canvas.delete(f"block_placed{i}_{j}")
        for i in range(3):
            self.canvas.delete(f"block{i}")
        self.generate_blocks()
        self.reset_gridcell()
        n = self.points
        self.points = 0
        self.points_charger_anim("points_main", n, 0, steps=30, start_text="Score: ")
        self.flag_menu = False

    # animation methods

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
        for i in range(16):
            self.canvas.move(f"block_placed{c_from[0]}_{c_from[1]}",
                             (c1_to[0]-c1_from[0])//15, (c1_to[1]-c1_from[1])//16)
            if not self.flag_close: time.sleep(0.01)
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
            if not self.flag_close: time.sleep(0.01)
            self.canvas.update()
        self.flag_animation = False
    
    # save handling methods

    def save_data(self) -> None:
        """
        Save game progress to save.txt
        """
        file = open(self.res_path("save.txt"), "w")
        def random_string() -> str: return " " * random.randint(200, 300)
        # write board
        for i in range(7):
            text = ""
            for j in range(7-abs(i-3)):
                text += random_string()+str(self.board[i][j])
            text += random_string()+"\n"
            file.write(text)
        # write score and highscore
        text = ""
        for i in str(self.points):
            text += random_string()+i
        text += random_string()+"\n"
        file.write(text)
        text = ""
        for i in str(self.highscore_points):
            text += random_string()+i
        text += random_string()+"\n"
        file.write(text)
        # write current blocks to choose
        for i in range(3):
            text = random_string()
            if type(self.blocks_to_choose[i])==int: text += "-1"+random_string()
            else:
                for j in self.blocks_to_choose[i]:
                    text += str(j)+random_string()
            file.write(text+"\n")
        file.write(random_string()+str(self.unlocked_block)+"\n")
        file.close()

    def load_data(self) -> bool:
        """
        Loads game progress from save.txt
        """
        try:
            file = open(self.res_path("save.txt"), "r")
            file_lines = [x.rstrip() for x in file.readlines()]
            for i in range(7):
                l = [int(x) for x in file_lines[i].split()]
                for j in range(7-abs(i-3)):
                    self.board[i][j] = l[j]
            self.points = int("".join(file_lines[7].split()))
            self.highscore_points = int("".join(file_lines[8].split()))
            for i in range(3):
                l = [int(x) for x in file_lines[i+9].split()]
                if l[0] == -1: self.blocks_to_choose[i] = -1
                else: 
                    self.blocks_to_choose[i] = []
                    for j in l: self.blocks_to_choose[i].append(j)
            self.unlocked_block = int("".join(file_lines[12].split()))
            return True
        except Exception as e:
            print(e)
            return False

    # event methods

    def cell_left_click(self, a: int, b: int) -> None:
        """
        Method loaded by clicking given block on gridcell
        """
        if self.flag_erase and not self.flag_animation:
            self.board[a][b] = 0
            self.canvas.delete(f"block_placed{a}_{b}")


    def reroll_cells(self) -> None:
        """
        Mixes all cells with themselves
        """
        if not self.flag_animation:
            empty_cells = [[i, j] for i in range(7) for j in range(7-abs(i-3))]
            blocks = [self.board[i][j] for i in range(7) for j in range(7-abs(i-3))
                    if self.board[i][j]!=0]
            for i in empty_cells:
                self.board[i[0]][i[1]] = 0
                self.canvas.delete(f"block_placed{i[0]}_{i[1]}")
            for i in blocks:
                n = empty_cells.pop(random.randint(0, len(empty_cells)-1))
                self.board[n[0]][n[1]] = i
                self.create_gridcell_block(n[0], n[1])

    def block_icon_input(self, index: int) -> None:
        """
        Method connected to blocks icons
        """
        if not self.flag_animation and not self.flag_menu:
            self.current_block = index
            self.canvas.tag_raise(f"block{index}")

    def motion_left_clicked(self, event) -> None:
        """
        Method connected to mouse move with left button pressed bind (<B1-Motion>)
        """
        if self.current_block != -1 and not self.flag_animation and not self.flag_menu:
            self.canvas.move(f"block{self.current_block}", 
                             event.x-self.canvas.coords(f"block{self.current_block}")[0], 
                             event.y-self.canvas.coords(f"block{self.current_block}")[1]-95)
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
            elif tag=="dump_btn" or tag=="dump_btntext":
                if self.current_cell != [-2, -2]:
                    self.current_cell = [-2, -2]
                    self.reset_gridcell()
            else:
                if self.current_cell != [-1, -1]:
                    self.current_cell = [-1, -1]
                    self.reset_gridcell()

    def block_released(self, event) -> None:
        """
        Method connected to left button release
        """
        if self.current_block != -1 and not self.flag_animation and not self.flag_menu:
            self.flag_animation = True
            if self.current_cell[0] >=0 and self.current_cell[1] >= 0:
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
                    self.create_gridcell_block(a, b)
                    if f!=-1: 
                        self.create_gridcell_block(c, d)
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
                            self.create_gridcell_block(cell_main[0], cell_main[1])
                            self.canvas.update()
                            # optional breaking blocks around if block is 8th one
                            if self.board[cell_main[0]][cell_main[1]]==8:
                                self.reset_gridcell()
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
            elif self.current_cell == [-2, -2]: 
                self.canvas.delete(f"block{self.current_block}")
                self.blocks_to_choose[self.current_block] = [random.randint(0, 3)]
                self.blocks_to_choose[self.current_block].extend(
                    random.sample(range(1, self.unlocked_block+1), 2) if
                    self.blocks_to_choose[self.current_block] != 0 else 
                    [random.choice(range(1, self.unlocked_block+1))]
                )
                self.generate_blocks(self.current_block,
                                     self.blocks_to_choose[self.current_block])
            else:
                self.canvas.move(f"block{self.current_block}", 
                                self.WIDTH//4*(self.current_block+1)-event.x, self.HEIGHT-50-event.y)
            self.save_data()
            self.reset_gridcell()
            self.current_block = -1
            self.lose_check()
            self.flag_animation = False

    def close_app(self) -> None:
        """
        Close app after all the animations are gone
        """
        self.flag_close = True
        def wait() -> None:
            while self.flag_animation: pass
            self.master.destroy()
        th.Thread(target=wait, daemon=True).start()



if __name__ == "__main__":
    app = App()