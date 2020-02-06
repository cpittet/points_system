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


def read_data(path):
    """
    Read the data in the specified excel file
    :param path: the path where the excel file
    containing the data of the current year is located
    :return: a np.array of dimensions (1 x 3*nbr of activities, for present, excused, and non-excused) with the data of the current year, and the number of activities this year
    """
    # Open workbook
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name("DataApp")

    # The number of activities this year
    nbr_activ = sheet.nrows - 1

    data = np.empty((1, 3 * nbr_activ))

    # Fill the numpy array
    # Iterate over the columns (only 3 of them necessary)
    for i in range(1, 4):
        for j in range(1, sheet.nrows):
            data[0, (i - 1) * nbr_activ + j - 1] = sheet.cell_value(j, i)
    return data, nbr_activ


def get_mandatory_and_name_list_from_file(path, nbr_activ):
    """
    Read the list of mandatory activities and the name of the activities in the excel file
    :param path: the path where the excel file is located
    :param nbr_activ: the number of activities
    :return: a np.array containing booleans where at index i contains whether the ith activity is mandatory or not,
    and the name at ith index of the ith activity
    """
    # Open workbook
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name("DataApp")

    # Mandatory list
    data = np.empty(nbr_activ, dtype=bool)

    for i in range(1, sheet.nrows):
        cell = sheet.cell_value(i, 4)
        if cell == "Oui" or cell == "oui":
            data[i - 1] = True
        else:
            data[i - 1] = False
    # dtype('U50') for unicode of max 50 chars, with str it is by default only 1 char
    names = np.empty(nbr_activ, dtype=np.dtype('U50'))

    for i in range(1, sheet.nrows):
        names[i - 1] = sheet.cell_value(i, 0)

    return data, names


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
    USELESS...
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
    c.execute('''SELECT year FROM separate WHERE year=?''', (year,))
    exists = c.fetchall()

    return exists


def update_record(new_record, year, mdt, society_size, c, conn):
    """
    Update the record of the current year in the database containing the records for each year
    and the record in the table containing all years
    :param new_record: the new record for this year
    :param year: the current year
    :param mdt: the mandatory data for this year
    :param society_size: the size of the society for that year
    :param c: the cursor of the corresponding open connection to the db
    :param conn: the connection to the corresponding db
    :return:
    """
    # Query to update the separate table
    sql = ''' UPDATE separate
              SET data = ?,
              size = ?
              WHERE year = ?'''

    c.execute(sql, (new_record, society_size, year))
    conn.commit()

    # Query to update the mandatory table
    c.execute('''UPDATE mandatory
                 SET mdt = ?
                 WHERE year = ?''', (mdt, year))
    conn.commit()

    # Query to update in the cumulative table
    c.execute('''SELECT * FROM cumulative WHERE year=?''', (year,))
    current = c.fetchone()[1]

    current = current[:-1]

    if current.size == 0:
        new = new_record
    else:
        new = np.append(current, new_record, axis=0)

    # Write the updated record into the cumulative table
    c.execute('''UPDATE cumulative
                 SET data = ?
                 WHERE year = ?''', (new, year))

    conn.commit()


def write_record(record, year, mdt, names, society_size, db_path):
    """
    Write the new record for the current year in the database containing the records for each year
    and update the record in the table containing all years. Checks if a record for this year already exists,
    if yes, it updates it, if not it adds it. It also checks if the tables exists, if not it creates them.
    :param record: np.array () : the new record of the current year
    :param year: the current year
    :param mdt: the mandatory data for this year
    :param names: the names of the activities
    :param society_size: the size of the society for that year
    :param db_path: the path of the database
    :return:
    """
    # Open connection to the db
    conn, c = connect_db(db_path)

    # If the tables does not exist, we create them
    c.execute('''CREATE TABLE IF NOT EXISTS cumulative (
                year INTEGER PRIMARY KEY,
                data nparray
                  )''')

    c.execute('''CREATE TABLE IF NOT EXISTS separate (
                 year INTEGER PRIMARY KEY,
                 data nparray,
                 size INTEGER
                    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS mandatory (
                  year INTEGER PRIMARY KEY,
                  mdt nparray,
                  names nparray
                    )''')

    conn.commit()

    # Checks if there is already a record for this year
    record_exist = check_existence_record(year, c)

    if record_exist:
        print("Updating the entry")
        update_record(record, year, mdt, society_size, c, conn)
    else:
        print("Writing new entry")

        # Write new record into the separate table
        c.execute('''INSERT INTO separate (year, data, size)
                     VALUES(?, ?, ?)''', (year, record, society_size))

        conn.commit()

        # Write new record of mandatory data into the mandatory table
        c.execute('''INSERT INTO mandatory (year, mdt, names)
                     VALUES(?, ?, ?)''', (year, mdt, names))
        conn.commit()

        # Query cumulative record of previous year
        c.execute('''SELECT * FROM cumulative WHERE year=?''', (year - 1,))

        prev_year = c.fetchone()

        # Add to the array the record of this year if previous is not empty
        if prev_year is None:
            prev_year = record
        else:
            # Returns the rows corresponding to our query i.e. with (year, np.array), so we take the second one
            prev_year = prev_year[1]
            prev_year = np.append(prev_year, record, axis=0)

        print("new cumulative record " + str(prev_year))

        # Write new cumulative record into the cumulative table
        c.execute('''INSERT INTO cumulative (year, data)
                     VALUES(?, ?)''', (year, prev_year))
        conn.commit()

    close_db(conn, c)


def get_last_cumulative(db_path):
    """
    Returns the last entry in the cumulative table in the specified db
    :param db_path: the location of the db
    :return: int, np.array, int : the last year, the last cumulative entry or None if the cumulative table is empty
    """
    conn, c = connect_db(db_path)

    # Query the last cumulative entry in the table cumulative
    c.execute('''SELECT * FROM cumulative ORDER BY year DESC LIMIT 1''')
    last_year, last_entry = c.fetchone()

    # Query the society size in the separate table
    c.execute('''SELECT size FROM separate ORDER BY year DESC LIMIT 1''')
    society_size = c.fetchone()[0]

    close_db(conn, c)

    return last_year, last_entry, society_size


def get_last_separate(db_path):
    """
    Returns the last entry in the separate table in the specified db
    :param db_path: the location of the db
    :return: int, np.array, int : the last year, the last separate entry or None if the separate table is empty
    """
    conn, c = connect_db(db_path)

    # Query last separate entry in the table separate
    c.execute('''SELECT * FROM separate ORDER BY year DESC LIMIT 1''')
    last_year, last_entry, society_size = c.fetchone()

    close_db(conn, c)

    return last_year, last_entry, society_size


def get_last_mandatory_and_names_from_db(db_path):
    """
    Returns the mandatory list of activities from the specified db
    :param db_path: the location of the db
    :return: np.array (nbr of activities) : containing True if the ith activity is mandatory False otherwise
    """
    conn, c = connect_db(db_path)

    # Query mandatory array in the table mandatory
    c.execute('''SELECT * FROM mandatory ORDER BY year DESC LIMIT 1''')
    last_year, last_entry, last_names = c.fetchone()

    close_db(conn, c)

    return last_year, last_entry, last_names


#data = read_data("/home/cpittet/jeunesse_app/presence.xlsx", 22)
# print(data)
# print(data.shape)
#
#mdt, names = get_mandatory_and_name_list_from_file("/home/cpittet/jeunesse_app/presence.xlsx", 22)
# print(mdt)
#
#conn, c = connect_db('/home/cpittet/jeunesse_app/points_system/data/dataApp.db')
#
# c.execute('''CREATE TABLE cumulative (
#             year INTEGER PRIMARY KEY,
#             data nparray
#             )''')
# c.execute('''CREATE TABLE separate (
#              year INTEGER PRIMARY KEY,
#              data nparray
#              )''')
#
# conn.commit()
#
# close_db(conn, c)
#
# exist = check_existence_tables('/home/cpittet/jeunesse_app/data/dataApp.db')
# print("table exist" + str(exist))
#
#write_record(data, 2021, mdt, names, '/home/cpittet/jeunesse_app/data/dataApp.db')
#
# c.execute('''SELECT * FROM cumulative''')
# cumul = c.fetchall()
#
# print(cumul)
#
# c.execute('''SELECT * FROM separate''')
# sep = c.fetchall()
#
# print(sep)
#
# c.execute('''SELECT * FROM mandatory''')
# mandat = c.fetchall()
#
# print(mandat)
#

#last_year, data_full, size = get_last_cumulative('/home/cpittet/jeunesse_app/points_system/data/dataApp.db')

#print(last_year)
#print(data_full)
#print(size)

#close_db(conn, c)

#ly, le = get_last_cumulative('/home/cpittet/jeunesse_app/data/dataApp.db')

#print(ly)
#print(le)

#ly, le = get_last_separate('/home/cpittet/jeunesse_app/data/dataApp.db')
#print(ly)
#print(le)

#ly, le, ln = get_last_mandatory_and_names_from_db('/home/cpittet/jeunesse_app/data/dataApp.db')
#print(ly)
#print(le)
#print(ln)

#close_db(conn, c)