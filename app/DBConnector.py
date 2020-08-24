import psycopg2


con = psycopg2.connect(database="testdb", user="admin", password="supersecretpwd", host="db", port="5432")


def retrieve_data(query):
    
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    return rows


# def format_results(self, results):
#     for row in results:
#         for key, value in row.items():


def close_db_connection():
    con.close()