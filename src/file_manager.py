import xlrd
import numpy as np
import sqlite3
import io

"""
The separate table contains the records for each year separately and in term of persons.
The cumulative record contains the cumulative records for each year and in term of percentage w.r.t. to
each of the years an entry corresponds to.
"""


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
    :return a np.array of dimensions (1 x 3*nbr of activities, for present, excused, and non-excused) with the data of the current year, and the number of activities this year,
    and a np.array (nbr of activities, ) containing the attributed points (ith element represents the points attributed to the ith activity)
    """
    # Open workbook
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name("DataApp")

    # The number of activities this year
    nbr_activ = sheet.nrows - 1

    data = np.empty((1, 3 * nbr_activ))
    points = np.empty(nbr_activ, dtype=int)

    # Fill the numpy array
    # Iterate over the columns (only 4 of them necessary)
    for i in range(1, 5):
        for j in range(1, sheet.nrows):
            if i == 1:
                points[j - 1] = sheet.cell_value(j, i)
            else:
                data[0, (i - 2) * nbr_activ + j - 1] = sheet.cell_value(j, i)

    return data, nbr_activ, points


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
        cell = sheet.cell_value(i, 5)
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


def update_record(new_record, year, mdt, society_size, points, c, conn):
    """
    Update the record of the current year in the database containing the records for each year
    and the record in the table containing all years
    :param new_record: the new record for this year
    :param year: the current year
    :param mdt: the mandatory data for this year
    :param society_size: the size of the society for that year
    :param points: np.array of the points attributed to the activities for this year
    :param c: the cursor of the corresponding open connection to the db
    :param conn: the connection to the corresponding db
    :return:
    """
    # Query to update the separate table
    sql = ''' UPDATE separate
              SET data = ?,
              points = ?,
              size = ?
              WHERE year = ?'''

    c.execute(sql, (new_record, points, society_size, year))
    conn.commit()

    # Query to update the mandatory table
    c.execute('''UPDATE mandatory
                 SET mdt = ?
                 WHERE year = ?''', (mdt, year))
    conn.commit()


def write_record(record, year, mdt, names, society_size, points, conn, c):
    """
    Write the new record for the current year in the database containing the records for each year
    and update the record in the table containing all years. Checks if a record for this year already exists,
    if yes, it updates it, if not it adds it. It also checks if the tables exists, if not it creates them.
    :param record: np.array () : the new record of the current year
    :param year: the current year
    :param mdt: the mandatory data for this year
    :param names: the names of the activities
    :param society_size: the size of the society for that year
    :param points: np.array of the points attributed to the activities for this year
    :param conn: the connection to the db variable
    :param c: the cursor to the db variable
    :return:
    """

    # If the tables does not exist, we create them
    c.execute('''CREATE TABLE IF NOT EXISTS separate (
                 year INTEGER PRIMARY KEY,
                 data nparray,
                 points nparray,
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
        c.execute('''INSERT INTO separate (year, data, points, size)
                     VALUES(?, ?, ?, ?)''', (year, record, points, society_size))

        conn.commit()

        # Write new record of mandatory data into the mandatory table
        c.execute('''INSERT INTO mandatory (year, mdt, names)
                     VALUES(?, ?, ?)''', (year, mdt, names))
        conn.commit()


def get_all_separate(conn, c):
    """
    Returns all the records in the db corresponding, ordered by ascending year
    :param conn: the connection to the db we want to look in
    :param c: the cursor of the db
    :return: list of tuples (int, np.array, np.array, int : year, the separate entry,
             the points for each activity, size of the society)
             or None if it does not exist
    """
    # Query separate entries in the table separate
    c.execute('''SELECT * FROM separate ORDER BY year ASC''')
    records = c.fetchall()

    return records


def construct_cumulative(records):
    """
    Construct a cumulative record according to the records in the db
    :param records: the separate records (list of tuples : (int, np.array, np.array, int : year, the separate entry,
                                                            the points for each activity, size of the society)
    :return: int, np.array, array, np.array : the last year, the cumulative entry, the array of society sizes
             for each year, the np.array of the points for each years and each activity
             or None if there is no separate entries
    """
    if len(records) == 0:
        return None

    # The year of the last record
    last_year = records[len(records)-1][0]

    # The np array containing the cumulative entry (percentage w.r.t. size of the society for that year)
    cumul = np.empty((len(records), records[0][1].shape[1]))

    # The array of the size for each years
    society_sizes = [0]*len(records)

    # The array of the points for each years, divided by 3 because there are 3 categories of presence
    # concatenated in that array, so there are actually only a third of activities
    points = np.empty((len(records), records[0][1].shape[1] // 3))

    for i in range(len(records)):
        # The np array records[i][0] is of shape (1, 66) : [[...]] and we only want 1 dimension
        cumul[i] = records[i][1][0] / records[i][3]
        society_sizes[i] = records[i][3]
        points[i] = np.reshape(records[i][2], (1, -1))

    return last_year, cumul, society_sizes, points


def get_last_cumulative(conn, c):
    """
    Returns the last entry in the cumulative table in the specified db
    :param conn: the connection to the db variable
    :param c: the cursor to the db variable
    :return: int, np.array, array, np.array : the last year, the cumulative entry
             or None if there is no entries yet
    """

    # Query all the separate entries
    records = get_all_separate(conn, c)

    # Construct and return the cumulative entry
    return construct_cumulative(records)


def get_last_separate(conn, c):
    """
    Returns the last entry in the separate table in the specified db
    :param conn: the connection to the db variable
    :param c: the cursor to the db variable
    :return: int, np.array, np.array, int : the last year, the last separate entry or None if the separate table is empty
    """

    # Query last separate entry in the table separate
    c.execute('''SELECT * FROM separate ORDER BY year DESC LIMIT 1''')
    last_year, last_entry, last_points, society_size = c.fetchone()

    return last_year, last_entry, last_points, society_size


def get_last_mandatory_and_names_from_db(conn, c):
    """
    Returns the mandatory list of activities from the specified db
    :param conn: the connection to the db variable
    :param c: the cursor to the db variable
    :return: np.array (nbr of activities) : containing True if the ith activity is mandatory False otherwise
    """

    # Query mandatory array in the table mandatory
    c.execute('''SELECT * FROM mandatory ORDER BY year DESC LIMIT 1''')
    last_year, last_entry, last_names = c.fetchone()

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