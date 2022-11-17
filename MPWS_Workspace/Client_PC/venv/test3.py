from tkinter import *
from functools import partial

class Game:
    def __init__(self):
        self.root = Tk()

        self.frame1 = Frame(self.root, width = 900, height = 30)
        self.frame1.grid()

        self.label=Label(self.frame1, text="")
        self.label.grid(row=0, column=0, columnspan=5)

        ## save each button id in a list
        self.list_of_button_ids=[]
        for ctr in range(15):
            ## use partial to pass the button number to the
            ## function each time the button is pressed
            button = Button(self.frame1, text=str(ctr), width = 20,
                            height = 20, padx = 2, pady = 2,
                            command=partial(self.button_callback, ctr))
            this_row, this_col=divmod(ctr, 5)
            ## the label is in the top row so add one to each row
            button.grid(row=this_row+1, column=this_col)

            ## add button's id to list
            self.list_of_button_ids.append(button)
        self.root.mainloop()

    def button_callback(self, button_num):
        """ display button number pressed in the label
        """
        self.label.config(text="Button number %s and it's id=%s"
                   % (button_num, self.list_of_button_ids[button_num]))


app = Game()