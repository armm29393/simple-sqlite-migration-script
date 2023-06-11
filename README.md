## SQLite Migration Script

This is a Python script for managing SQLite database migrations. It allows you to create migration files, apply migrations (up), and revert migrations (down) in your SQLite database.

### Prerequisites

- Python 3.x
- SQLite

### Setup

1. Copy the migration script (`migration.py`) to your project directory.

2. Make sure you have the `sqlite3` package installed. You can install it by running the following command:

   ```bash
   pip install sqlite3
   ```

3. Create a new directory called `migrations` in your project directory. This directory will be used to store migration files.

### Usage

Open a terminal or command prompt and navigate to your project directory.

#### Creating a Migration File

To create a new migration file, use the `create` command followed by the table name:

```bash
python3 migration.py create <table_name>
```

This will generate a migration file with a timestamp prefix and the specified table name, e.g., `20220101120000-users.sql`. By default, the migration file will contain both the `up` and `down` SQL scripts for creating and dropping the table.

#### Applying Migrations (Up)

To apply all pending migrations, use the `up` command:

```bash
python3 migration.py up
```

This command will execute all the pending migration files that have not been previously executed. The executed migrations will be recorded in the `__schema_migrations` table.

#### Reverting Migrations (Down)

To revert the last executed migration, use the `down` command:

```bash
python3 migration.py down
```

This command will revert the most recent migration file and remove the corresponding entry from the `__schema_migrations` table.

To revert a specific number of migrations, use the `down` command followed by the step value:

```bash
python3 migration.py down <step>
```

Replace `<step>` with the number of migrations you want to revert. For example, `python3 migration.py down 2` will revert the last two migrations.

To revert all executed migrations, use the `down` command with the `all` keyword:

```bash
python3 migration.py down all
```

This command will revert all the executed migrations and clear the `__schema_migrations` table.

### Summary of Commands

- `create <table_name>`: Generates a new migration file for creating a table with the specified name.

- `up`: Applies all pending migrations.

- `down`: Reverts the last executed migration.

- `down <step>`: Reverts a specific number of executed migrations.

- `down all`: Reverts all executed migrations.

### Additional Information

- Migration files are stored in the `migrations` directory. Each migration file contains the SQL scripts for both the `up` and `down` migrations.

- The `__schema_migrations` table keeps track of the executed migrations. It stores the migration file name and the execution timestamp.

- Make sure to update the `database.db` filename in the script to match your SQLite database file name or path.

- You can modify the generated migration files to include more complex SQL scripts or additional table alterations as needed.
