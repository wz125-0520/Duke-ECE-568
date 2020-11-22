import psycopg2

#Connect to the database
def connect():
    try:
        conn = psycopg2.connect(database="upsDB", user="yl655", password="a2oC7tGm5D", host="127.0.0.1", port="5432")
        print ('Open the databse upsDB created by Django')
        return conn
    except:
        print ('Cannot connect to the database')

def update():
    conn = connect()
    cur = conn.cursor()
    cur.execute("update ups_package set destx=1090 where packageid=123")
    #cur.execute("insert into ups_search (trackingNumber) values (000)")
    conn.commit()
    cur.close()
    conn.close()

def main():
    update()

if __name__ == "__main__":
    main()