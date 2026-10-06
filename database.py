import sqlite3


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_NAME = "lost_found.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE TABLE
# =========================================================

def create_table():

    connection = get_connection()

    cursor = connection.cursor()

    # -----------------------------------------------------
    # Create table if it does not exist
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lost_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            owner_name TEXT NOT NULL,

            item_name TEXT NOT NULL,

            description TEXT,

            contact TEXT NOT NULL,

            location TEXT,

            date_lost TEXT,

            status TEXT DEFAULT 'Lost'

        )
        """
    )

    connection.commit()

    # -----------------------------------------------------
    # Check whether old database already has status column
    # -----------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(lost_items)"
    )

    columns = [
        column["name"]
        for column in cursor.fetchall()
    ]

    # -----------------------------------------------------
    # Add status column to an existing database
    # -----------------------------------------------------

    if "status" not in columns:

        cursor.execute(
            """
            ALTER TABLE lost_items
            ADD COLUMN status TEXT DEFAULT 'Lost'
            """
        )

        connection.commit()

    # -----------------------------------------------------
    # Make sure old rows have Lost status
    # -----------------------------------------------------

    cursor.execute(
        """
        UPDATE lost_items
        SET status = 'Lost'
        WHERE status IS NULL
        OR status = ''
        """
    )

    connection.commit()

    connection.close()


# =========================================================
# ADD LOST ITEM
# =========================================================

def add_lost_item(
    owner_name,
    item_name,
    description,
    contact,
    location,
    date_lost
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO lost_items (
            owner_name,
            item_name,
            description,
            contact,
            location,
            date_lost,
            status
        )

        VALUES (?, ?, ?, ?, ?, ?, 'Lost')
        """,

        (
            owner_name,
            item_name,
            description,
            contact,
            location,
            date_lost
        )
    )

    connection.commit()

    connection.close()


# =========================================================
# GET LOST ITEMS
# =========================================================

def get_lost_items(status=None):

    connection = get_connection()

    cursor = connection.cursor()

    if status is None:

        cursor.execute(
            """
            SELECT *
            FROM lost_items
            ORDER BY id DESC
            """
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM lost_items
            WHERE status = ?
            ORDER BY id DESC
            """,
            (status,)
        )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# =========================================================
# GET ACTIVE LOST ITEMS
# =========================================================

def get_active_lost_items():

    return get_lost_items(
        status="Lost"
    )


# =========================================================
# GET FOUND ITEMS
# =========================================================

def get_found_items():

    return get_lost_items(
        status="Found"
    )


# =========================================================
# UPDATE ITEM STATUS
# =========================================================

def update_item_status(
    item_id,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE lost_items

        SET status = ?

        WHERE id = ?
        """,

        (
            status,
            item_id
        )
    )

    connection.commit()

    affected_rows = cursor.rowcount

    connection.close()

    return affected_rows > 0


# =========================================================
# MARK ITEM AS FOUND
# =========================================================

def mark_item_as_found(
    item_id
):

    return update_item_status(
        item_id,
        "Found"
    )


# =========================================================
# MARK ITEM AS LOST
# =========================================================

def mark_item_as_lost(
    item_id
):

    return update_item_status(
        item_id,
        "Lost"
    )


# =========================================================
# DELETE LOST ITEM
# =========================================================

def delete_lost_item(
    item_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM lost_items

        WHERE id = ?
        """,

        (item_id,)
    )

    connection.commit()

    connection.close()