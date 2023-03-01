import sqlite3
import click
from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(populate_db_command)
    app.cli.add_command(add_admins_command)


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def populate_db():
    db = get_db()
    # project_data = [
    #     ("Northrop Grumman",0,),
    #     ("Keurig", 0,),
    # ]
    # db.executemany(
    #     'INSERT INTO project (name, total) VALUES (?, ?)', project_data
    # )
    user_data = [
        (0, "mlampart@bucknell.edu", "Matt Lamparter", 0,),
        # (1, "ana002@bucknell.edu", "Arsh Noor Amin", 1,),
    ]
    db.executemany(
        'INSERT INTO user (project_id, email, name, auth_level) VALUES (?, ?, ?, ?);', user_data
    )
    db.commit()
    click.echo('DB populated.')

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

@click.command('add-admins')
def add_admins_command():
    db = get_db()

    admin_data = [
        (0, "blb033@bucknell.edu", "Ben Buentello", 0),
        (0, "srd010@bucknell.edu", "Susan Dudt", 0),
        (0, "qnt001@bucknell.edu", "Quan Nguyen Tu", 0),
        (0, "eu003@bucknell.edu", "Eren Ugur", 0)
    ]
    db.executemany(
        'INSERT INTO user (project_id, email, name, auth_level) VALUES (?, ?, ?, ?);', admin_data
    )
    db.commit()
    click.echo('Admins added.')

@click.command('populate-db')
def populate_db_command():
    populate_db()
    click.echo('DB populated.')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
