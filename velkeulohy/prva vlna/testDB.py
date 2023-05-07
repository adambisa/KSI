import sqlite3
import json

from discord import Status
from classes import Check, Schedule

conn = sqlite3.connect('server_data.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS checks (
            id text,
            last_ping text,
            last_ping_timestamp integer,
            name text,
            secret_key text,
            status text
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS schedules (
            id text,
            period text,
            grace text,
            secret_key text
            )""")


def create_check(check):
    conn = sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO checks VALUES (:id, :last_ping, :last_ping_timestamp,:name,:secret_key,:status)", {'id': check.id, 'last_ping': check.last_ping, 'last_ping_timestamp': check.last_ping_timestamp, 'name':check.name,'secret_key':check.secret_key, 'status':check.status})
    conn.commit()
    conn.close()

def get_check(id):
    #return items withuot secret key, seccond change in healthclass.py
    conn = sqlite3.connect('server_data.db')
    # This enables column access by name: row['column_name']
    c = conn.cursor()
    c.execute("  SELECT id, last_ping, last_ping_timestamp, name, status FROM checks WHERE id=:id", {'id': id})
    rows = c.fetchall()
    conn.commit()
    conn.close()
    return rows

def check_check_secret(id):
    conn=sqlite3.connect('server_data.db')
    c=conn.cursor()
    c.execute("SELECT secret_key FROM CHECKS where id=:id",{'id':id})
    return c.fetchall()
def get_all_checks():
    c.execute("SELECT * FROM checks")
    return c.fetchall()
    
def put_check(id, secret_key, name):
    conn = sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute("""UPDATE checks SET name = :name
                    WHERE id = :id AND secret_key = :secret_key""",
                  {'id': id, 'secret_key': secret_key, 'name': name})

    conn.commit()
    conn.close()

def ping(id, last_ping):
    conn = sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute("UPDATE checks SET last_ping==:last_ping WHERE id=:id",{'id':id, 'last_ping':last_ping})
    conn.commit()
    conn.close()


def delete_check(id, secret_key):
    conn = sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute("DELETE from checks WHERE id = :id AND secret_key = :secret_key",
                  {'id': id, 'secret_key': secret_key})
    conn.commit()
    conn.close()


def add_to_schedule(schedule):
    conn=sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO schedules VALUES (:id, :period, :grace, :secret_key)",{'id':schedule.id, 'period':schedule.period, 'grace':schedule.grace, 'secret_key':schedule.secret_key})
    conn.commit()
    conn.close()
def check_schedule(id, secret_key):
    conn=sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute("SELECT id, period, grace FROM schedules WHERE id=:id AND secret_key=:secret_key ", {'id':id, 'secret_key':secret_key})
    rows=c.fetchall()
    return rows

def put_schedule(id, secret_key, period, grace):
    conn = sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute(""" UPDATE schedules SET period = :period, grace =:grace 
                    WHERE id=:id AND secret_key=:secret_key""",
                    {'id':id, 'secret_key':secret_key, 'period': period, 'grace':grace})
    conn.commit()
    conn.close()
def check_schedule_key(id):
    conn = sqlite3.connect('server_data.db')
    c = conn.cursor()
    c.execute("SELECT secret_key FROM schedules WHERE id=:id", {'id':id})
    rows=c.fetchall()
    return rows

newest_schedule = Schedule('id', 'key', 'period', 'grace')
add_to_schedule(newest_schedule)