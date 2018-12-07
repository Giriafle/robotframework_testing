"""This module for working with a database.
It gets values from config module and uses db_work module for querying a database.
The module checks existence tha database, gets users with positive balance from it,
inserts users with positive balance and gets users' balance from it.
"""

import os
import sqlite3
from config import DB


class DBRequests:
    """
     This is a class for working with SQLite3 database.
     At initialization it opens connection and makes a cursor to a database.
     After initialization implements methods with this database.
     After implementation it does commit and closes connection.
     """

    def open_connection(self) -> sqlite3.Connection:
        """Initiates connection to a database and makes a cursor.

        :return: Object - Connection to the database
        """

        try:
            db_connection = sqlite3.connect(DB)
            return db_connection
        except sqlite3.Error as e:
            raise Exception(f'An error occurred while accessing the service "Connecting to the database": {e}')

    def get_cursor(self, db_connection: sqlite3.Connection) -> sqlite3.Cursor:
        """
        Initiates connection to a database and makes a cursor.

        :param db_connection: Object - Connection to the database.
        :return: Object - Cursor to the database.
        """

        try:
            db_cur = db_connection.cursor()
            return db_cur
        except sqlite3.Error as e:
            raise Exception(f'An error occurred while accessing the service "Getting the cursor to the database": {e}')

    def close_db(self, db_connection: sqlite3.Connection):
        """Committing and closing the database.

        :param db_connection: Object - Connection to the database.
        """

        try:
            db_connection.close()
        except sqlite3.Error as e:
            raise Exception(f'An error occurred while accessing the service "Closing the database": {e}')

    def check_file(self) -> bool:
        """
        Checking existence a database.

        :return: Boolean value: True if it's exist, False - not exist.
        """

        return os.path.isfile(DB)

    def get_client_with_positive_balance(self, db_cur: sqlite3.Cursor) -> \
            tuple or None:
        """
        This function gets values from a database: it selects users with a positive balance.
        If such users doesn't exist the function calls another function (called insert_user_with_positive_balance)
        to add it, and after this function calls itself. Using the flag to call itself once.

        :param db_cur: Object - Cursor to the database.
        :return: Int - client's id,
                Int - client's balance,
                None - if the client is not found.
        """

        try:
            result = db_cur.execute('''SELECT CLIENT_ID, CLIENT_NAME, BALANCE FROM CLIENTS JOIN BALANCES 
                                ON CLIENTS.CLIENT_ID = BALANCES.CLIENTS_CLIENT_ID WHERE BALANCE > 0''').fetchone()
        except sqlite3.Error as e:
            raise Exception(f'An error occurred while accessing the service "Selection client with positive balance '
                            f'from the database": {e}')
        if result:
            return result[0], result[2]
        else:
            return None, None

    def insert_user_with_positive_balance(self, db_connection: sqlite3.Connection, db_cur: sqlite3.Cursor) -> \
            tuple:
        """
        This function is called from another function (called get_select_with_positive_balance). It needs to add to
        the database users with positive balance.

        :param db_connection: Object - Connection to the database.
        :param db_cur: Object - Cursor to the database.
        :return Int - client's id,
                Int - client's balance,
        """

        try:
            db_cur.execute("INSERT INTO CLIENTS (CLIENT_NAME) VALUES ('Monsen')")
            db_cur.execute("INSERT INTO BALANCES (BALANCE) VALUES (5.0)")
            db_connection.commit()
            result = db_cur.execute('''SELECT CLIENT_ID, CLIENT_NAME, BALANCE FROM CLIENTS JOIN BALANCES 
                              ON CLIENTS.CLIENT_ID = BALANCES.CLIENTS_CLIENT_ID WHERE BALANCE > 0''').fetchone()
        except sqlite3.Error as e:
            raise Exception(f'An error occurred while accessing the service "Insertion information to the database":'
                            f' {e}')
        assert result
        try:
            return result[0], result[2]
        except IndexError:
            raise Exception(f'An error occurred while accessing the service "Insertion information to the database":'
                            f'got empty select response after insert: {e}')

    def get_balance(self, client_id: int, db_cur: sqlite3.Cursor) -> float:
        """
        The function select user's balance with his id from the database. The pending request is a tuple, which contains
        the client's balance in the first position.

        :param db_cur: Object - Cursor to the database.
        :param client_id: Integer - Id to find user in the database.
        :return: Float - User's balance from the database
        """
        try:
            result = db_cur.execute(f'SELECT BALANCE FROM BALANCES WHERE CLIENTS_CLIENT_ID={client_id}').fetchone()
        except sqlite3.Error as e:
            raise Exception(f'An error occurred while accessing the service "Getting client\'s balance from the '
                            f'database": {e}')
        assert result
        try:
            return result[0]
        except IndexError:
            raise Exception(f'An error occurred while accessing the service "Getting client\'s balance from the '
                            f'database", got empty response: {e}')

