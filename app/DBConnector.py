import psycopg2
from psycopg2 import sql
import pandas as pd
import numpy as np
import sys


def retrieve_data(con, cursor, query):
    cursor = con.cursor()
    cursor.execute(query)
    try:
        rows = cursor.fetchall()
        return rows
    except:
        return


def drop_tables(con, db):
    """
    Drop all tables of database you given.
    """
    cursor = con.cursor()

    try:
        cursor.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
        rows = cursor.fetchall()
        for row in rows:
            print ("dropping table: ", row[1])
            cursor.execute("drop table " + row[1] + " cascade")
        cursor.close()
        con.close()
    except:
        print ("Error: ", sys.exc_info()[1])

    db.session.commit()
    cursor.close()


def get_table_list(con, cursor, t_schema):
    tables = []

    # Retrieve the table list
    s = ""
    s += "SELECT"
    s += " table_schema"
    s += ", table_name"
    s += " FROM information_schema.tables"
    s += " WHERE"
    s += " ("
    s += " table_schema = '" + t_schema + "'"
    s += " )"
    s += " ORDER BY table_schema, table_name;"

    # Retrieve all the rows from the cursor
    cursor.execute(s)
    list_tables = cursor.fetchall()

    # Print the names of the tables
    for t_name_table in list_tables:
        tables.append(t_name_table)

    return tables


# define a function that gets the column names from a PostgreSQL table
def get_columns_names(con, cursor, table):
    columns = []

    col_names_str = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE "
    col_names_str += "table_name = '{}';".format( table )

    try:
        sql_object = sql.SQL(
            # pass SQL statement to sql.SQL() method
            col_names_str
        ).format(
            # pass the identifier to the Identifier() method
            sql.Identifier( table )
        )

        cursor.execute( sql_object )
        col_names = (cursor.fetchall())

        for tup in col_names:
            columns += [ tup[0] ]

    except Exception as err:
        print ("get_columns_names ERROR:", err)

    return columns


def close_db_connection(con, cursor):
    cursor.close()
    con.close()
