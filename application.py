import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class Home(ttk.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.root = root

        # The explications about how to use the app
        expl = """
        En premier, mise à jour des données (onglet données)
        Ensuite, les statistiques sont disponibles sous l'onglet Statistiques,
        les estimations selon les points données sont disponibles sous l'onglet Estimations
        """
        explications = tk.Label(parent, text=expl, justify='left')

        #Put it on screen
        explications.grid(row=0, column=0, sticky='W', padx=10, pady=30)

        # Exit button
        exit = tk.Button(parent, text='Quitter', command=self.exit_manager)
        exit.grid(row=3, column=4, padx=15, pady=15)

        #Spacer
        space = tk.Label(parent, text='''                                                   
                                                           ''')
        space.grid(row=2, column=2)

    def exit_manager(self):
        self.root.destroy()


class Statistics(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.parent = parent







class Predictions(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)


class DataForm(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        # Add button to select the data file
        select_but = tk.Button(parent, text='Sélectionner', command=self.file_selection)


    def file_selection(self):
        # Select location of the data for current year
        file_location = filedialog.askopenfilename(initialdir='/home/cpittet/jeunesse_app',
                                                   title='Sélectionner le fichier de données',
                                                   filetypes=(("Fichier Excel", "*.xlsx"), ("Fichier Excel", "*.xls")))


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        # I.e the root window
        self.parent = parent

        # <create the rest of your GUI here>
        tab_parent = ttk.Notebook(parent)

        # Create all the frames that will be in each tab
        self.home_tab = Home(parent=tab_parent, root=parent, *args, **kwargs)
        self.stat_tab = Statistics(tab_parent, *args, **kwargs)
        self.pred_tab = Predictions(tab_parent, *args, **kwargs)
        self.data_tab = DataForm(tab_parent, *args, **kwargs)

        # Create and add all the tabs
        tab_parent.add(self.home_tab, text='Accueil')
        tab_parent.add(self.data_tab, text='Données')
        tab_parent.add(self.stat_tab, text='Statistiques')
        tab_parent.add(self.pred_tab, text='Estimations')

        tab_parent.pack(expand=1, fill='both')




if __name__ == "__main__":
    #The main window
    root = tk.Tk()

    #Set the title of the window
    root.title('Système de points  -  Jeunesse Marsens')

    #Fix the starting geometry
    #root.geometry('1000x500')

    #Set the icon
    #root.iconbitmap('path')

    #Creates the GUI
    MainApplication(root).pack()

    #Start it
    root.mainloop()