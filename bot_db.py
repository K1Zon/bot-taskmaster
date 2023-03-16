import psycopg2

try:
    conn = psycopg2.connect(dbname='tasks', user='postgres', password='7355608k', host='localhost')
except:
    print("Can't establish connection to database")

cur = conn.cursor()


cur.execute(
  '''
    '''
  )

conn.commit()
print("Table created")

cur.close()
conn.close()
