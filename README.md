เมื่อลองให้ chatGPT เขียน script migration ให้..

# SQLite Migration Script

The SQLite Migration Script is a Python script that allows you to perform database schema migrations using SQL migration files. It provides functionality to create migration files, execute migrations in the 'up' and 'down' directions, and maintain a schema migration history.

## Prerequisites

- Python 3.x
- SQLite

## Getting Started

1. Clone the repository or download the migration script file (`migration.py`) to your local machine.

2. Install the required dependencies by running the following command:

   ```
   pip install sqlite3
   ```

3. Initialize a new SQLite database file (e.g., `migrate.db`) if you don't have one already.

4. Create a new directory named `migrations` in the same directory as the migration script. This directory will store your migration files.

## Usage

The migration script supports the following commands:

### Create a New Migration

To create a new migration file, use the `create` command followed by the desired migration name. For example:

```
python3 migration.py create users_table
```

This command will generate a migration file with the format `<timestamp>-users_table.sql` inside the `migrations` directory.

Open the generated migration file and fill in the migration statements in the `-- +goose Up` and `-- +goose Down` sections.

### Execute Migrations

To apply the migrations and update the database schema, use the `up` command:

```
python3 migration.py up
```

This command will execute any pending migrations that haven't been applied yet.

To revert the last applied migration, use the `down` command:

```
python3 migration.py down
```

This command will revert the last applied migration and roll back the corresponding changes.

If you want to revert a specific number of migrations, you can provide a step count as an argument. For example, to revert the last three migrations, use:

```
python3 migration.py down 3
```

To revert all applied migrations, use the following command:

```
python3 migration.py down all
```

### Reset Migrations

To reset the migrations and revert all applied migrations, use the `reset` command:

```
python3 migration.py reset
```

**Note:** The `reset` command will first execute the `down` command to revert all applied migrations, and then execute the `up` command to reapply all migrations.

### Migrations Status

The `status` command displays a table showing the migration files and their current status (applied or pending).

```
python3 migration.py status
```

### Schema Migration History

The script maintains a schema migration history by recording the executed migrations in a schema table named `__schema_migrations` within the SQLite database.

Each time a migration is executed, a record is inserted into the `__schema_migrations` table with the migration file name and the execution timestamp.

You can view the executed migrations by querying the `__schema_migrations` table directly.

## Contributing

Contributions to this SQLite Migration Script are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

This SQLite Migration Script is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---
