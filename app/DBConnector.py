import psycopg2
import pandas as pd
import numpy as np
import sys


def retrieve_data(con, query):
    cur = con.cursor()
    cur.execute(query)
    try:
        rows = cur.fetchall()
        return rows
    except:
        return


def drop_tables(con, cur, db):
    """
    Drop all tables of database you given.
    """

    try:
        cur.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
        rows = cur.fetchall()
        for row in rows:
            print ("dropping table: ", row[1])
            cur.execute("drop table " + row[1] + " cascade")
        cur.close()
        con.close()
    except:
        print ("Error: ", sys.exc_info()[1])

    db.session.commit()



# def nan_to_null(csv_file):
#     df = pd.read_csv(csv_file)
#     df = df.where(pd.notnull(df), None)
#     df.to_csv(csv_file, encoding='utf-8', index=False)


def string_to_int(con, this_table, this_column, db):
    cur = con.cursor()
    #query = "ALTER TABLE " + this_table + " ALTER COLUMN " + this_column + " TYPE NUMERIC(8, 2) USING (NULLIF(" + this_column + ",'')::NUMERIC(8, 2));"
    query = "ALTER TABLE " + this_table + " ALTER COLUMN " + this_column + " TYPE DOUBLE PRECISION USING NULLIF(" + this_column + ", '')::DOUBLE PRECISION"
    print(query)
    cur.execute(query)
    db.session.commit()


def close_db_connection(con, cur):
    cur.close()
    con.close()
