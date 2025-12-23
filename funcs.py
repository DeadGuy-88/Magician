import sqlite3 as sl
import uuid

# WARNING, there is need to create a 'dummy' line with ticket id.
def ticket_to_db(db_chat_id, db_username, db_ticket):
    con = sl.connect('tickets.db')
    cursor = con.cursor()
    cursor.execute("""INSERT INTO tickets(chat_id, username, ticket_id, ticket_text, date) VALUES (?,?,(SELECT IFNULL(MAX(ticket_id), 0) + 1 FROM tickets),?, datetime())""",(db_chat_id, db_username, db_ticket))
    con.commit()
    cursor.close()

def check_existing_tickets(db_username, db_ticket):
    con = sl.connect('tickets.db')
    cursor = con.cursor()
    cursor.execute("""SELECT * FROM tickets WHERE username = ? AND ticket_text = ? LIMIT 1""", (db_username, db_ticket))
    existing = cursor.fetchone() is not None
    if existing:
        return True
    else:
        return False
    con.commit()
    cursor.close()

def get_last_users_ticket(db_username):
    con = sl.connect('tickets.db')
    cursor = con.cursor()
    cursor.execute("""SELECT ticket_text FROM tickets WHERE username = ? ORDER BY date DESC LIMIT 1""",(db_username,))
    last_ticket = cursor.fetchone()
    if not last_ticket or not last_ticket[0]:
        return None
    elif last_ticket[0] == ' ':
        return None
    else:
        return last_ticket[0]
    con.commit()
    cursor.close()

def add_extra_to_tickets(db_chat_id, db_username, db_ticket):
    con = sl.connect('tickets.db')
    cursor = con.cursor()
    db_ticket = f"EXTRA: {db_ticket}"
    cursor.execute("""SELECT ticket_id FROM tickets WHERE username = ? ORDER BY date DESC LIMIT 1""", (db_username,))
    last_id = cursor.fetchone()
    cursor.execute("""INSERT INTO tickets(chat_id, username, ticket_id, ticket_text, date) VALUES (?,?,?,?, datetime())""",(db_chat_id, db_username, (last_id[0]), db_ticket))
    con.commit()
    cursor.close()

