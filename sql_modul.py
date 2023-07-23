import sqlite3 as sql

# conn = sql.connect("admins.db")
# cur = conn.cursor()

# cur.execute("""CREATE TABLE IF NOT EXISTS admins(
#             amdinid INT
# )""")

# conn = sql.connect("founds.db")
# cur = conn.cursor()

# cur.execute("""CREATE TABLE IF NOT EXISTS users(
#             name TEXT,
#             city TEXT,
#             age INT,
#             birthdate TEXT
# );""")

def is_admin(user_id):
    conn = sql.connect("admins.db")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM admins;""")
    ids = cur.fetchall()
    conn.close()
    for x in ids:
        if user_id in x:
            return True
    return False

def array_of_users(user_id):
    if not(is_admin(user_id)):
        return False
    else:
        conn = sql.connect("founds.db")
        cur = conn.cursor()
        cur.execute("""SELECT * FROM users;""")
        founds = cur.fetchall()
        conn.close()
        return founds
    
def del_field(num):
    conn=sql.connect("founds.db")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM users;""")
    list = cur.fetchall()
    data = list[num-1]
    cur.execute(f"""DELETE FROM users WHERE name='{data[0]}' and city='{data[1]}' and age='{data[2]}' and birthdate={data[3]};""")
    conn.commit()
    conn.close()

def insert_field(string):
    a = [str(x) for x in string.split('\n')]
    a = (a[0],a[1],a[2],a[3])
    conn = sql.connect('founds.db')
    cur = conn.cursor()
    if (int(a[2])>18) and (int(a[2])<70):
        daymonthyear = [int(x) for x in a[2].split('.')]
        if (1<=daymonthyear[0]<=31)and(1<=daymonthyear[1]<=12)and(1953<=daymonthyear[2]<=2005)and((2023-daymonthyear[2]) == daymonthyear[0]):
            cur.execute(f"""INSERT INTO users (name, city, age, birthdate) VALUES ('{a[0]}','{a[1]}',{a[2]},'{a[3]}');""")
        else:
            return 'Unsuccess'
    else:
        return 'Unsuccess'
    conn.commit()
    conn.close()
    return 'Success'

def user_wth_num(num):
    conn = sql.connect('founds.db')
    cur = conn.cursor()
    list_of_users = cur.fetchall()
    ret = f'Информация о поиске:\nИмя{list_of_users[num-1][0]}\nГород: {list_of_users[num-1][1]}\nВозраст: {str(list_of_users[num-1][2])}\nДата рождения: {list_of_users[num-1][3]}\n\n' 
    return ret