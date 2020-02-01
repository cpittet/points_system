import xlrd
import numpy as np
import sqlite3
import os.path
import io


def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# Automatically executed when the modul (file_manager) is imported in another file
sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("nparray", convert_array)


def read_data(path, nbr_activ):
    """
    Read the data in the specified excel file
    :param path: the path where the excel file
    containing the data of the current year is located
    :param nbr_activ: the number of activities
    :return: a np.array of dimensions (1 x 3*nbr of activities, for present, excused, and non-excused) with the data of the current year
    """
    # Open workbook
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name("DataApp")

    data = np.empty((1, 3 * nbr_activ))

    # Fill the numpy array
    # Iterate over the columns (only 3 of them necessary)
    for i in range(1, 4):
        for j in range(1, sheet.nrows):
            data[0, (i - 1) * nbr_activ + j - 1] = sheet.cell_value(j, i)
    return data


def get_mandatory_list(path, nbr_activ):
    """
    Read the list of mandatory activities in the excel file
    :param path: the path where the excel file is located
    :param nbr_activ: the number of activities
    :return: a list containing boolean where at index i contains whether the ith activity is mandatory or not
    """
    # Open workbook
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name("DataApp")

    data = np.empty((1, nbr_activ), dtype=str)

    for i in range(1, sheet.nrows):
        cell = sheet.cell_value(i, 4)
        if cell == "Oui" or cell == "oui":
            data[0, i - 1] = True
        else:
            data[0, i - 1] = False
    return data


def connect_db(db_path):
    """
    Connects to the db specified
    :param db_path: the db we want to connect to
    :return: the connection and cursor variable
    """
    conn = None
    try:
        # Connects to the db
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)

        # Creates the cursor
        c = conn.cursor()
    except sqlite3.Error as err:
        print(err)
    return conn, c


def close_db(conn, cursor):
    """
    Close the connection given to the db
    :param conn: the connection to the db
    :param cursor: the cursor of the connection
    :return: Nothing
    """
    cursor.close()
    conn.close()


def check_existence_tables(db_path):
    """
    Checks whether the db already contains the tables
    :param db_path: location of the db if it already has been created
    :return: False if the db does not exists or does not contains the tables, True otherwise
    """
    if not (os.path.isfile(db_path)):
        return False

    conn, c = connect_db(db_path)

    # Query the number of tables with the name cumulative
    c.execute('''SELECT count(name) FROM sqlite_master
    WHERE type='table' AND name='cumulative' ''')

    # Fetch the result
    cumul = False
    if c.fetchone()[0] == 1:
        cumul = True

    # Query the number of tables with the name separate
    c.execute('''SELECT count(name) FROM sqlite_master
    WHERE type='table' AND name='separate' ''')

    # Fetch the result
    sep = False
    if c.fetchone()[0] == 1:
        sep = True

    close_db(conn, c)

    return cumul and sep


def check_existence_record(year, c):
    """
    Checks if the record for the given year already exists
    :param year: the year to check whether there already is a record for this year
    :param c: the cursor of the corresponding open connection to the db
    :return: boolean : true if there already is a record for this year,
    false otherwise
    """
    # Query the entry
    c.execute('''SELECT year FROM separate WHERE year=?''', year)
    exists = c.fetchall()

    return exists


def update_record(new_record, year, c, conn):
    """
    Update the record of the current year in the database containing the records for each year
    and the record in the table containing all years
    :param new_record: the new record for this year
    :param year: the current year
    :param c: the cursor of the corresponding open connection to the db
    :param conn: the connection to the corresponding db
    :return:
    """
    # Query
    sql = ''' UPDATE separate
              SET data = ?
              WHERE year = ?'''

    c.execute(sql, (new_record, year))
    conn.commit()


def write_record(record, year, db_path):
    """
    Write the new record for the current year in the database containing the records for each year
    and update the record in the table containing all years. Checks if a record for this year already exists,
    if yes, it updates it, if not it adds it. It also checks if the tables exists, if not it creates them.
    :param record: the new record of the current year
    :param year: the current year
    :param db_path: the path of the database
    :return:
    """
    #Open connection to the db
    conn, c = connect_db(db_path)

    #If the tables does not exist, we create them
    c.execute('''CREATE TABLE IF NOT EXISTS cumulative (
                year INTEGER PRIMARY KEY,
                data nparray
                  )''')
    c.execute('''CREATE TABLE IF NOT EXISTS separate (
                 year INTEGER PRIMARY KEY,
                 data nparray''')

    c.execute('''CREATE TABLE IF NOT EXISTS mandatory (
                  year INTEGER PRIMARY KEY,
                  mdt INTEGER''')

    conn.commit()

    #Checks if there is already a record for this year
    record_exist = check_existence_record(year, c)

    if record_exist:
        update_record(record, year, c, conn)
    else:
        #Write new record into the separate table
        c.execute('''INSERT INTO separate(year, data)
                     VALUES(?, ?)''', (year, record))

        conn.commit()

        #Query cumulative record of previous year

        #Add to the array the record of this year

        #Write new cumulative record into the cumulative table

    return


# data = readData("/home/cpittet/jeunesse_app/presence.xlsx", 22)
# print(data)
# print(data.shape)

# data = getMandatoryList("/home/cpittet/jeunesse_app/presence.xlsx", 22)
# print(data)

conn, c = connect_db('/home/cpittet/jeunesse_app/data/dataApp.db')

# c.execute('''CREATE TABLE cumulative (
#             year INTEGER PRIMARY KEY,
#             data nparray
#             )''')
#
# c.execute('''CREATE TABLE separate (
#             year INTEGER PRIMARY KEY,
#             data nparray
#             )''')

conn.commit()

close_db(conn, c)

exist = check_existence_tables('/home/cpittet/jeunesse_app/data/dataApp.db')
print("table exist" + str(exist))
