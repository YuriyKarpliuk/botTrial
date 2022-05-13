import telebot
import config
from telebot import types
import psycopg2
from config import host, user, password, db_name
bot = telebot.TeleBot(config.token)

try:
    con = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    c = con.cursor()

except Exception as ex:
    print("[INFO] Error while working with PostgreSQL", ex)


def db_user_table_create():
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL NOT NULL ,
                first_name TEXT NOT NULL,
                last_name TEXT  NOT NULL,
                username TEXT NOT NULL,
                position_name TEXT NOT NULL
                )""")
    con.commit()

def db_timetable_table_create():
    c.execute("""CREATE TABLE IF NOT EXISTS timetable (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                week TEXT  NOT NULL,
                start_hour TEXT NOT NULL,
                end_hour TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
                )""")
    con.commit()

def db_event_table_create():
    c.execute("""CREATE TABLE IF NOT EXISTS event (
                id SERIAL PRIMARY KEY,
                timetable_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT  NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY (timetable_id) REFERENCES timetable(id)
                )""")
    con.commit()

db_user_table_create()
db_timetable_table_create()
db_event_table_create()


def save_info(id: int, first_name: str, last_name: str, username: str, position_name: str):
    c.execute('INSERT INTO users (user_id, first_name, last_name, username, position_name) VALUES (%s, %s, %s, %s, %s)',
              (id, first_name, last_name, username, position_name,))
    con.commit()


@bot.message_handler(commands=["start"])
def welcome(message):
    check_if_user_exist(message.from_user.id)
    if c.fetchone() == None:
        bot.send_message(message.chat.id,
                         "Oops!You don't have access to MICB bot.\nIt is available only for our company workers")
    else:
        rmk3 = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        rmk3.add(types.KeyboardButton("Admin"), types.KeyboardButton("User"))
        bot.send_message(message.chat.id,
                         "Welcome, {0.first_name}!\nI am - <b>{1.first_name}</b> bot.".format(message.from_user,
                                                                                              bot.get_me()),
                         parse_mode='html', reply_markup=rmk3)
        bot.register_next_step_handler(message, user_choice1)


def user_choice1(message):
    if message.text == "Admin":
        admin(message)
    if message.text == "User":
        user(message)


def user(message):
    rmk2 = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    rmk2.add(types.KeyboardButton("My info"))
    bot.send_message(message.chat.id, 'Choose what command you want to do:', reply_markup=rmk2)
    bot.register_next_step_handler(message, user_choice3)


def user_choice3(message):
    if message.text == "My info":
        user_info(message)


def user_info(message):
    c.execute('SELECT first_name, last_name, position_name FROM users WHERE user_id = %s', (message.from_user.id,))
    con.commit()
    sql = c.fetchone()
    mylist = list()
    for row in sql:
        mylist.append(row)
    output = 'First name: %s \nLast name: %s \nPosition: %s' % (mylist[0], mylist[1], mylist[2])
    bot.send_message(message.chat.id, output)



def admin(message):
    rmk = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    rmk.add(types.KeyboardButton("Add user"), types.KeyboardButton("Delete user"), types.KeyboardButton("Update user"), types.KeyboardButton("Add user timetable"))

    c.execute("SELECT user_id FROM users WHERE position_name = 'Admin'")
    sql_query = c.fetchone()[0]
    if message.from_user.id == sql_query:
        bot.send_message(message.chat.id, 'Choose what command you want to do:', reply_markup=rmk)
        bot.register_next_step_handler(message, user_choice2)
    else:
        bot.send_message(message.chat.id, 'Sorry, you dont have access to do this operation!')


def user_choice2(message):
    if message.text == "Add user":
        bot.send_message(message.chat.id, 'Write user telegram id:')
        bot.register_next_step_handler(message, first_name)
    if message.text == "Delete user":
        bot.send_message(message.chat.id, 'Write user telegram id, which you want to delete:')
        bot.register_next_step_handler(message, delete_user)
    if message.text == "Update user":
        bot.send_message(message.chat.id, 'Write user telegram id, which you want to update:')
        bot.register_next_step_handler(message, update_user)
    if message.text == "Add user timetable":
        bot.send_message(message.chat.id, 'Write user telegram id, to add timetable:')
        bot.register_next_step_handler(message, add_timetable_user)

def add_timetable_user(message):
    global u_id
    u_id = message.text
    check_if_user_exist(u_id)
    if c.fetchone() == None:
        bot.send_message(message.chat.id, "There is no user with such id")

def first_name(message):
    global id
    id = message.text
    bot.send_message(message.chat.id, 'Write user first name:')
    bot.register_next_step_handler(message, last_name)


def last_name(message):
    global first_name
    first_name = message.text
    bot.send_message(message.chat.id, 'Write user last name:')
    bot.register_next_step_handler(message, username)


def username(message):
    global last_name
    last_name = message.text
    bot.send_message(message.chat.id, 'Write username:')
    bot.register_next_step_handler(message, position)


def position(message):
    global username
    username = message.text
    bot.send_message(message.chat.id, 'Write user position:')
    bot.register_next_step_handler(message, success)


def success(message):
    global position_name
    position_name = message.text
    save_info(id, first_name, last_name, username, position_name)
    bot.send_message(message.chat.id, 'User have been saved successfully!!!')


def check_if_user_exist(u_id: int):
    c.execute('SELECT * FROM users WHERE user_id = %s', (u_id,))
    con.commit()


def delete(u_id: int):
    c.execute('DELETE FROM users WHERE user_id = %s', (u_id,))
    con.commit()


def delete_user(message):
    global u_id
    u_id = message.text
    check_if_user_exist(u_id)
    if c.fetchone() == None:
        bot.send_message(message.chat.id, "There is no user with such id")
    else:
        delete(u_id)
        bot.send_message(message.chat.id, "User successfully deleted!")


def update_first_name(u_id: int, new_fs: str):
    c.execute('UPDATE users SET first_name = %s WHERE user_id = %s', (new_fs, u_id,))
    con.commit()


def new_first_name(message):
    global new_fs
    new_fs = message.text
    update_first_name(u_id, new_fs)
    user_update(message)


def update_last_name(u_id: int, new_ls: str):
    c.execute('UPDATE users SET last_name = %s WHERE user_id = %s', (new_ls, u_id,))
    con.commit()


def new_last_name(message):
    global new_ls
    new_ls = message.text
    update_last_name(u_id, new_ls)
    user_update(message)


def update_username(u_id: int, new_un: str):
    c.execute('UPDATE users SET username = %s WHERE user_id = %s', (new_un, u_id,))
    con.commit()


def new_username(message):
    global new_un
    new_un = message.text
    update_username(u_id, new_un)
    user_update(message)


def update_position(u_id: int, new_pos: str):
    c.execute('UPDATE users SET position_name = %s WHERE user_id = %s', (new_pos, u_id,))
    con.commit()


def new_position(message):
    global new_pos
    new_pos = message.text
    update_position(u_id, new_pos)
    user_update(message)


def user_update(message):
    bot.send_message(message.chat.id, "User successfully updated!")


def update(message):
    if message.text == "First name":
        bot.send_message(message.chat.id, 'Write new first name:')
        bot.register_next_step_handler(message, new_first_name)

    if message.text == "Last name":
        bot.send_message(message.chat.id, 'Write new last name:')
        bot.register_next_step_handler(message, new_last_name)

    if message.text == "Username":
        bot.send_message(message.chat.id, 'Write new username:')
        bot.register_next_step_handler(message, new_username)

    if message.text == "Position":
        bot.send_message(message.chat.id, 'Write new position:')
        bot.register_next_step_handler(message, new_position)


def update_user(message):
    global u_id
    u_id = message.text
    check_if_user_exist(u_id)
    if c.fetchone() == None:
        bot.send_message(message.chat.id, "There is no user with such id")
    else:
        rmk1 = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        rmk1.add(types.KeyboardButton("First name"), types.KeyboardButton("Last name"),
                 types.KeyboardButton("Username"), types.KeyboardButton("Position"))
        bot.send_message(message.chat.id, "Choose which field you want to update:", reply_markup=rmk1)
        bot.register_next_step_handler(message, update)


bot.polling(none_stop=True)
