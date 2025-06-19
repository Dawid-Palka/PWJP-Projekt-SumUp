import tkinter as tk
from gui import GameGUI
from PIL import Image, ImageTk


if __name__ == "__main__":
    root = tk.Tk()
    icon_image = Image.open("assets/ss.ico")
    icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(False, icon_photo)
    game = GameGUI(root)
    root.mainloop()
