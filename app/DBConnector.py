import psycopg2


def retrieve_data(con, query):
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    return rows

# def format_results(self, results):
#     for row in results:
#         for key, value in row.items():


def close_db_connection(con):
    con.close()
