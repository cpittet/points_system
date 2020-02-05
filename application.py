import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os

import file_manager as fm


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
        explications = tk.Label(self, text=expl, justify='left')

        # Put it on screen
        explications.grid(row=0, column=0, sticky='W', padx=15, pady=15)

        # Exit button
        exit = tk.Button(self, text='Quitter', command=self.exit_manager)
        exit.grid(row=3, column=4, padx=15, pady=15)

    def exit_manager(self):
        self.root.destroy()


class Statistics(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        # Reminder to update the data first
        self.reminder = tk.Label(self, text='Ne pas oublier de mettre à jour les données,\nsous l\'onglet \"Données\", en premier !', justify='left')
        self.reminder.grid(row=0, column=0, padx=15, pady=15, sticky='W')

        # Explications
        self.expl = tk.Label(self,
                                 text='Vous pouvez enregistrer les statistiques sous le bouton \"Enregister\".\nCela peut prendre quelques secondes.',
                                 justify='left')
        self.expl.grid(row=1, column=0, padx=15, pady=15, sticky='W')

        # Button to compute and save the stats
        self.save_stat = tk.Button(self, text='Enregistrer', command=self.comp_save_stat)
        self.save_stat.grid(row=2, column=1, padx=15, pady=15)

    def comp_save_stat(self):
        # Open dialog box to get location where to save the file
        self.parent.filename = filedialog.askopenfilename(initialdir='/',
                                                          title='Enregistrer les statistiques',
                                                          filetypes=(
                                                          ("Fichier Excel", "*.xlsx"), ("Fichier Excel", "*.xls"),
                                                          ("Tout les fichiers", "*.*")))


class Predictions(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)


class DataForm(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.filename = None

        # Text
        select = tk.Label(self, text='Sélectionner le fichier de données')
        select.grid(row=0, column=0, padx=15, pady=15, sticky='W')

        # Add button to select the data file
        select_but = tk.Button(self, text='Sélectionner', command=self.file_selection)
        select_but.grid(row=0, column=1, padx=15, pady=15)

        # Entry to put the year the data corresponds to
        year = tk.Label(self, text='Données pour l\'année :')
        year.grid(row=2, column=0, padx=15, pady=15, sticky='W')
        self.year_entry = tk.Entry(self, width=15)
        self.year_entry.grid(row=2, column=1, padx=15, pady=15)

        # Button to update the database with the selected file
        update_but = tk.Button(self, text='Mettre à jour la base de données', command=self.update_db)
        update_but.grid(row=4, column=2, padx=15, pady=15)

        # Display the selection
        self.path_disp = tk.Label(self, text='')
        self.path_disp.grid(row=1, column=0, padx=15, pady=15, sticky='W')

    def file_selection(self):
        # Select location of the data for current year
        self.parent.filename = filedialog.askopenfilename(initialdir='/',
                                                          title='Sélectionner le fichier de données',
                                                          filetypes=(("Fichier Excel", "*.xlsx"), ("Fichier Excel", "*.xls"), ("Tout les fichiers", "*.*")))

        # Modify the display of the path
        self.path_disp['text'] = self.parent.filename

    def update_db(self):
        # Check first if a file was selected and that the year was entered
        if not(self.parent.filename is None) and (self.parent.filename.endswith('.xlsx') or self.parent.filename.endswith('.xls'))\
           and os.path.exists(self.parent.filename)\
           and self.year_entry.get() != '':

            # First read the data
            data_full, nbr_activ = fm.read_data(self.parent.filename)
            mandatory_list, names = fm.get_mandatory_and_name_list_from_file(self.parent.filename, nbr_activ)

            # Path of the db
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join('data', 'dataApp.db'))
            print(db_path)

            # Write the data (separate, cumulative in the db
            fm.write_record(data_full, int(self.year_entry.get()), mandatory_list, names, db_path)

            # Clear out the field
            self.year_entry.delete(0, 'end')
            self.path_disp['text'] = ''

            # Display success
            messagebox.showinfo('Mise à jour des données', 'Les données ont bien été mises à jours ! Vous pouvez continuez !')

        else:
            if self.parent.filename is None or not(self.parent.filename.endswith('.xlsx') or self.parent.filename.endswith('.xls')):
                # First have to provide a valid filename
                messagebox.showerror('Erreur', 'Vous devez d\'abord sélectionner le fichier\ncontenant les données !')
            elif self.year_entry.get() == '':
                # The year was not specified
                messagebox.showerror('Erreur', 'Vous devez d\'abord spécifier l\'année à laquelle les données correspondent !')


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
        self.data_tab = DataForm(parent=tab_parent, *args, **kwargs)

        # Create and add all the tabs
        tab_parent.add(self.home_tab, text='Accueil')
        tab_parent.add(self.data_tab, text='Données')
        tab_parent.add(self.stat_tab, text='Statistiques')
        tab_parent.add(self.pred_tab, text='Estimations')

        tab_parent.pack(expand=1, fill='both')


if __name__ == "__main__":
    # The main window
    root = tk.Tk()

    # Set the title of the window
    root.title('Système de points  -  Jeunesse Marsens')

    # Fix the starting geometry
    #root.geometry('1000x500')

    # Set the icon
    #root.iconbitmap('path')

    # Creates the GUI
    MainApplication(root).pack()

    # Start it
    root.mainloop()