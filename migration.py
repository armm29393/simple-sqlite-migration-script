#!python3

import argparse
import sys
import os
import sqlite3
from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

DB_NAME = 'migrate.db'
MIGRATION_DIR = 'migrations'
SCHEMA_TABLE = '__schema_migrations'
MIGRATE_Y = '✓'
MIGRATE_N = '✗'

def create_schema_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_file TEXT NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """.format(SCHEMA_TABLE))
    conn.commit()

def migrate_create(args):
    if len(args) != 1:
        print("Usage: python3 migration.py create <migration_name>")
        return

    migration_name = args[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    migration_file = os.path.join(MIGRATION_DIR, f"{timestamp}-{migration_name}.sql")

    migration_content = """-- +goose Up
-- +goose StatementBegin
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
-- +goose StatementEnd
"""

    with open(migration_file, 'w') as file:
        file.write(migration_content)

    print(f"{bcolors.OKGREEN}Migration file created: {migration_file}{bcolors.ENDC}")

def get_executed_migrations(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT migration_file FROM {}
    """.format(SCHEMA_TABLE))
    executed_migrations = [row[0] for row in cursor.fetchall()]
    return executed_migrations

def execute_migration(conn, statements, migration_path):
    try:
        cursor = conn.cursor()

        # Begin transaction
        cursor.execute("BEGIN TRANSACTION;")

        # Read migration file
        with open(migration_path, 'r') as file:
            migration_sql = file.read()

        # Extract migration statements
        up_statements = []
        down_statements = []
        current_statements = None

        for line in migration_sql.splitlines():
            if line.strip().startswith('-- +goose Up'):
                current_statements = up_statements
            elif line.strip().startswith('-- +goose Down'):
                current_statements = down_statements
            elif line.strip().startswith('-- +goose StatementBegin'):
                continue
            elif line.strip().startswith('-- +goose StatementEnd'):
                continue
            else:
                current_statements.append(line)

        up = '\n'.join(up_statements)
        down = '\n'.join(down_statements)

        # Execute statements
        if statements == 'up':
            print('Up Statements >>\n', up)
            cursor.execute(up)
        elif statements == 'down':
            print('Down Statements >>\n', down)
            cursor.execute(down)

        # Commit transaction
        conn.commit()
    except Exception as e:
        # Rollback transaction on error
        conn.rollback()
        raise e

def migrate_up(with_seed=False):
    conn = sqlite3.connect(DB_NAME)
    create_schema_table(conn)

    executed_migrations = get_executed_migrations(conn)
    migration_files = sorted(
        file for file in os.listdir(MIGRATION_DIR)
        if file.endswith('.sql') and file not in executed_migrations
    )

    if len(migration_files) < 1:
        print(f'{bcolors.BOLD}Nothing to migrate.{bcolors.ENDC}')
        return

    for migration_file in migration_files:
        migration_path = os.path.join(MIGRATION_DIR, migration_file)
        execute_migration(conn, 'up', migration_path)

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO {} (migration_file) VALUES (?)
        """.format(SCHEMA_TABLE), (migration_file,))
        conn.commit()
        print(f"{bcolors.OKGREEN}Executed migration: {migration_file}{bcolors.ENDC}")

    if with_seed:
        # Import seeder class
        # seeder = Seeder(conn)
        # seeder.run()
        pass

    conn.close()

def migrate_down(step=None):
    conn = sqlite3.connect(DB_NAME)

    executed_migrations = get_executed_migrations(conn)
    migration_files = sorted(executed_migrations, reverse=True)

    if step is not None:
        step = min(step, len(migration_files))
        migration_files = migration_files[:step]

    if len(migration_files) < 1:
        print(f'{bcolors.BOLD}Nothing to rollback.{bcolors.ENDC}')
        return

    for migration_file in migration_files:
        migration_path = os.path.join(MIGRATION_DIR, migration_file)
        execute_migration(conn, 'down', migration_path)

        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM {} WHERE migration_file = ?
        """.format(SCHEMA_TABLE), (migration_file,))
        conn.commit()
        print(f"{bcolors.OKGREEN}Reverted migration: {migration_file}{bcolors.ENDC}")

    conn.close()

def migrate_status():
    conn = sqlite3.connect(DB_NAME)

    executed_migrations = get_executed_migrations(conn)
    migration_files = sorted(
        file for file in os.listdir(MIGRATION_DIR)
        if file.endswith('.sql')
    )

    if len(migration_files) < 1:
        print(f'{bcolors.BOLD}Migration not found.{bcolors.ENDC}')
        return

    longest_name_length = max(len(migration_file.rsplit(".", 1)[0]) for migration_file in migration_files)
    dash_line = '-' * (longest_name_length + 12)  # Add some padding

    print(dash_line)
    print(f"{'Migration Name': <{longest_name_length}} | {'Migrated': <10}")
    print(dash_line)

    for migration_file in migration_files:
        migration_name = migration_file.rsplit(".", 1)[0]
        migration_status = f"{bcolors.OKGREEN}{MIGRATE_Y}{bcolors.ENDC}" if migration_file in executed_migrations else f"{bcolors.FAIL}{MIGRATE_N}{bcolors.ENDC}"
        migration_name_display = migration_name[:longest_name_length] + "..." if len(migration_name) > longest_name_length else migration_name
        print(f"{migration_name_display: <{longest_name_length}} | {migration_status: <10}")

    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SQLite Migration Script')
    parser.add_argument('command', choices=['up', 'down', 'create', 'reset', 'status', 'init'], help='Migration command')
    parser.add_argument('args', nargs='*', help='Additional arguments for create command')
    parser.add_argument('-s', '--seed', action='store_true', help='Apply seed data')

    args = parser.parse_args()

    if args.command == 'up':
        migrate_up(args.seed)
    elif args.command == 'down':
        if args.args and args.args[0] == 'all':
            step = None
        elif args.args:
            try:
                step = int(args.args[0])
            except ValueError:
                step = 1
        else:
            step = 1
        migrate_down(step)
    elif args.command == 'create':
        if not os.path.exists(MIGRATION_DIR):
            os.makedirs(MIGRATION_DIR)
        migrate_create(args.args)
    elif args.command == 'reset':
        if input(f"{bcolors.WARNING}For safety type 'RESET' before continue: {bcolors.ENDC}") == 'RESET':
            migrate_down()
            migrate_up(args.seed)
