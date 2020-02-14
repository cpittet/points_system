import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import numpy as np

# Personal modules
import points_system.file_manager as fm
import points_system.statistics as stat
from points_system.KRR import linear_kernel


class Home(ttk.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.root = root

        # The explications about how to use the app
        expl = """
        Salut ! Voici la marche à suivre, dans l'ordre :
        
        1) Mise à jour des données sous l'onglet \"Données\",
        2) PDF des statistiques sous l'onglet \"Satistiques\",
        3.a) Si c'est votre première utilisation de cette application, vous devez
        quitter et la redémarrer. (Pas nécessaire, pour les prochaines utilisations !)
        3.b ) Outils d'estimations des points sous l'onglet \"Estimations\".
        Attention, cela reste des estimations !
        
        Remarques :
            - Vous trouverez un \"mode d'emploi\" détaillé sous ...
            - Veillez à bien entrer les fichiers de données dans l'ordre croissant des années !
            - Bien utiliser le format de fichier excel convenu et non un autre !
        """
        explications = tk.Label(self, text=expl, justify='left')

        # Put it on screen
        explications.grid(row=0, column=0, sticky='W', padx=15, pady=15)

        # Exit button
        exit_but = tk.Button(self, text='Quitter', command=self.exit_manager)
        exit_but.grid(row=3, column=4, padx=15, pady=15)

    def exit_manager(self):
        self.root.destroy()


class Statistics(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.filename = ''

        # Reminder to update the data first
        self.reminder = tk.Label(self, text='Ne pas oublier de mettre à jour les données,\nsous l\'onglet \"Données\", en premier !', justify='left')
        self.reminder.grid(row=0, column=0, padx=15, pady=15, sticky='W')

        # Explications
        self.expl = tk.Label(self,
                             text='Vous pouvez enregistrer les statistiques sous le bouton \"Enregister\".\nCela peut prendre quelques secondes.',
                             justify='left')
        self.expl.grid(row=1, column=0, padx=15, pady=15, sticky='W')

        # Button to compute and save the stats
        save_stat = tk.Button(self, text='Enregistrer', command=self.comp_save_stat)
        save_stat.grid(row=2, column=1, padx=15, pady=15)

    def comp_save_stat(self):
        # Open dialog box to get location where to save the file
        self.filename = filedialog.askdirectory(title='Enregistrer le fichier sous')

        # Retrieve the data
        last_year, data_full, society_size, last_points = fm.get_last_cumulative(db_path)
        last_year2, mdt_list, last_names = fm.get_last_mandatory_and_names_from_db(db_path)

        # Reput cumulative data in term of persons
        society_size = np.array(society_size).reshape((data_full.shape[0], -1))
        print(society_size)
        print(data_full)
        data_full = data_full * society_size
        print(data_full)

        # Compute the stats and save the pdf at the specified location
        path_pdf = stat.create_pdf(data_full, mdt_list, last_year, last_names, society_size[-1,0], self.filename)

        # Display success
        messagebox.showinfo('Statistiques - ' + str(last_year),
                            'Calcul terminé, le fichier se trouve sous ' + path_pdf)


class Predictions(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)

        # The "prediction matrix", at beginning empty to avoid computing it multiple times
        self.pred_matrix = None
        self.nbr_activ = 0

        # If there is no db yet, it will crash, so I put an if and the user must first create the db and
        # restart for the first time
        if os.path.exists(db_path):
            # Retrieve the cumulative data
            last_year, self.data_full_cumul, self.society_size, self.last_points = fm.get_last_cumulative(db_path)

            # Retrieve the mandatory list and names from the db
            last_year, mdt, self.name_list = fm.get_last_mandatory_and_names_from_db(db_path)

            self.nbr_activ = self.data_full_cumul.shape[1] // 3

        # The "titles" of the columns
        names = tk.Label(self, text='Activités :', justify='left')
        names.grid(row=0, column=0, padx=15, pady=15, sticky='W')

        points = tk.Label(self, text='Points accordés :', justify='left')
        points.grid(row=0, column=1, padx=15, pady=15, sticky='W')

        #mandat = tk.Label(self, text='Obligatoires :', justify='left')
        #mandat.grid(row=0, column=2, padx=15, pady=15, sticky='W')

        prediction = tk.Label(self, text='Pourcentage de présence estimé,\nnbr. de personnes (par rapport au nombre actuel de personnes)')
        prediction.grid(row=0, column=3, padx=15, pady=15, sticky='W')

        # The list for the labels corresponding to activities
        self.activities_labels = [None] * self.nbr_activ
        self.activities_entries = [None] * self.nbr_activ
        self.activities_mdt = [None] * self.nbr_activ
        # self.activities_var_check = np.empty(self.nbr_activ, dtype=int)
        self.activities_predict = [None] * self.nbr_activ

        for i in range(self.nbr_activ):
            self.activities_labels[i] = tk.Label(self, text=self.name_list[i], justify='left')
            self.activities_labels[i].grid(row=i + 1, column=0, padx=15, pady=15, sticky='W')

            self.activities_entries[i] = tk.Entry(self, width=15)
            self.activities_entries[i].grid(row=i + 1, column=1, padx=15, pady=15)

            #self.activities_mdt[i] = tk.Checkbutton(self, text='Obligatoire', variable=self.activities_var_check[i],
            #                                   onvalue=1, offvalue=0)
            #self.activities_mdt[i].grid(row=i + 1, column=2, padx=15, pady=15)
            #self.activities_mdt[i].deselect()

            self.activities_predict[i] = tk.Label(self, text='')
            self.activities_predict[i].grid(row=i + 1, column=3, padx=15, pady=15)

        # Button to compute the predictions
        pred_but = tk.Button(self, text='Calculer', command=self.compute_predictions)
        pred_but.grid(row=self.nbr_activ + 1, column=4, padx=15, pady=15)

    def compute_predictions(self):
        # Get the data from input gui
        input_points = np.empty(self.nbr_activ, dtype=int)

        for i in range(self.nbr_activ):
            user_in = self.activities_entries[i].get()
            if user_in == '':
                messagebox.showerror('Erreur', 'Vous n\'avez pas entré de points pour l\'activité \"' + self.name_list[i] + '\" !')
                return
            input_points[i] = int(user_in)

        # Retrieve the values of the checkboxes
        # input_mdt = self.activities_var_check

        # input = np.append(input_points, input_mdt, axis=0)

        # Expand the input with the bias term and put it into percentages
        x = np.append(input_points, np.ones((1, 1)))

        # Construct matrix of input training data and expand the training data with the bias term
        nbr_years = self.last_points.shape[0]
        X = np.concatenate((self.last_points, np.ones((nbr_years, 1))), axis=1)

        # Rename ground truth training data
        Y = self.data_full_cumul[:, :self.nbr_activ]

        # Check if the prediction matrix was already computed, if not compute it
        if self.pred_matrix is None:
            K = KRR.matrix_kernel(X, linear_kernel)
            lambd = 0
            self.pred_matrix = KRR.prediction_matrix(Y, K, lambd)

        # Compute the predictions
        predictions = KRR.predict_KRR(X, x, Y, lambd=0, kernel_function=linear_kernel, pred_matrix=self.pred_matrix)

        # Display the results, note that we display 0 % if the prediction is negative, as it is non sense to have negative presence
        for i in range(self.nbr_activ):
            presence = predictions[i,0]
            if presence < 0:
                presence = 0
            self.activities_predict[i]['text'] = "{:.2f} %, {:d} personnes".format(presence, int(presence * self.society_size[-1][0]))


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

        # Entry to specify the society size
        size = tk.Label(self, text='Nombre de personnes dans la société pour cette année :')
        size.grid(row=3, column=0, padx=15, pady=15, sticky='W')
        self.size_entry = tk.Entry(self, width=15)
        self.size_entry.grid(row=3, column=1, padx=15, pady=15)

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
           and self.year_entry.get() != ''\
           and self.size_entry.get() != '':

            # First read the data
            data_full, nbr_activ, points = fm.read_data(self.parent.filename)
            mandatory_list, names = fm.get_mandatory_and_name_list_from_file(self.parent.filename, nbr_activ)

            print(db_path)

            # Write the data (separate, cumulative) in the db
            fm.write_record(data_full, int(self.year_entry.get()), mandatory_list, names, int(self.size_entry.get()), points, db_path)

            # Clear out the field
            self.year_entry.delete(0, 'end')
            self.path_disp['text'] = ''
            self.size_entry.delete(0, 'end')

            # Display success
            messagebox.showinfo('Mise à jour des données', 'Les données ont bien été mises à jours ! Vous pouvez continuez !')

        else:
            if self.parent.filename is None or not(self.parent.filename.endswith('.xlsx') or self.parent.filename.endswith('.xls')):
                # First have to provide a valid filename
                messagebox.showerror('Erreur', 'Vous devez d\'abord sélectionner le fichier\ncontenant les données !')
            elif self.year_entry.get() == '':
                # The year was not specified
                messagebox.showerror('Erreur', 'Vous devez d\'abord spécifier l\'année à laquelle les données correspondent !')
            elif self.size_entry.get() == '':
                # The size was not specified
                messagebox.showerror('Erreur', 'Vous devez d\'abord spécifier le nombre de personnes dans la société pour cette année !')


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        # I.e the root window
        self.parent = parent

        # <create the rest of your GUI here>
        tab_parent = ttk.Notebook(parent)

        # Path of the db
        global db_path
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join('data', 'dataApp.db'))

        # Create all the frames that will be in each tab
        self.home_tab = Home(parent=tab_parent, root=parent, *args, **kwargs)
        self.stat_tab = Statistics(parent=tab_parent, *args, **kwargs)
        self.pred_tab = Predictions(parent=tab_parent, *args, **kwargs)
        self.data_tab = DataForm(parent=tab_parent, *args, **kwargs)

        # Create and add all the tabs
        tab_parent.add(self.home_tab, text='Accueil')
        tab_parent.add(self.data_tab, text='Données')
        tab_parent.add(self.stat_tab, text='Statistiques')
        tab_parent.add(self.pred_tab, text='Estimations')

        tab_parent.pack(expand=1, fill='both')

def main():
    # The main window
    root = tk.Tk()

    # Set the title of the window
    root.title('Système de points  -  Jeunesse Marsens')

    # Fix the starting geometry
    # root.geometry('1000x500')

    # Set the icon
    # root.iconbitmap('path')

    # Creates the GUI
    MainApplication(root).pack(padx=15, pady=15)

    # Start it
    root.mainloop()

if __name__ == "__main__":
    main()