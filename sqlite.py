import sqlite3 as sq


async def db_start():   # create this function for started database
    global db, cur

    db = sq.connect('first.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id TEXT PRIMARY KEY, name TEXT, phone TEXT, time TEXT, cur_name TEXT, cur_phone TEXT, cur_time TEXT)")

    db.commit()


async def create_profile(user_id):   # function for created profile
    user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?, ?, ?)", (user_id, '', '', ''))
        db.commit()


async def edit_profile_back_call(state, user_id):   # adding data in profile for back call
    async with state.proxy() as data:
        cur.execute("UPDATE profile SET name = '{}', phone = '{}', time = '{}' WHERE user_id == '{}'".format(
            data['name'], data['phone'], data['time'], user_id))
        db.commit()


async def edit_profile_currently(state, user_id):  # adding data in profile for currently sign
    async with state.proxy() as data:
        cur.execute("UPDATE profile SET cur_name = '{}', cur_phone = '{}', cur_time = '{}' WHERE user_id == '{}'".format(
            data['cur_name'], data['cur_phone'], data['cur_time'], user_id))
        db.commit()