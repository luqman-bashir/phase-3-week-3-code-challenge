from database.connection import get_db_connection

class Author:
    def __init__(self, id, name):
        """
        Initialize an Author instance.

        Args:
            id (int): The unique ID of the author. Can be None for unsaved authors.
            name (str): The name of the author.
        """
        if id is not None and not isinstance(id, int):
            raise ValueError("ID must be None or an integer.")
        self.id = id
        self._validate_name(name)
        self._name = name

    def __repr__(self):
        return f'<Author {self.name}>'

    def _validate_name(self, name):
        """
        Validate the name of the author.

        Args:
            name (str): The name to validate.

        Raises:
            ValueError: If the name is not a string or is empty.
        """
        if not isinstance(name, str) or len(name) == 0:
            raise ValueError("Name must be a non-empty string.")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        """
        Update the name of the author with validation.

        Args:
            value (str): The new name of the author.

        Raises:
            AttributeError: If trying to modify the name after it has been set.
        """
        if hasattr(self, '_name'):
            raise AttributeError("Cannot modify the name of the author after it is set.")
        self._validate_name(value)
        self._name = value

#CREATE
    def save_to_db(self):
        """
        Save the author to the database. If the author already has an ID, it raises an error.

        Raises:
            AttributeError: If the author has already been saved.
        """
        if hasattr(self, 'id') and self.id is not None:
            raise AttributeError("Author already saved to the database.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", (self.name,))
        connection.commit()
        self.id = cursor.lastrowid
        connection.close()

#UPDATE
    def update_to_db(self):
        """
        Update the author's details in the database.

        Raises:
            ValueError: If the author does not exist in the database.
        """
        if not self.id:
            raise ValueError("Author must exist in the database to update.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE authors SET name = ? WHERE id = ?",
            (self.name, self.id),
        )
        connection.commit()
        connection.close()

#READ ALL 
    @staticmethod
    def fetch_all():
        """
        Fetch all authors from the database.

        Returns:
            list: A list of Author instances.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM authors")
        authors = cursor.fetchall()
        connection.close()
        return [Author(author["id"], author["name"]) for author in authors]

#READ SINGLE
    @staticmethod
    def fetch_by_id(author_id):
        """
        Fetch an author by their ID.

        Args:
            author_id (int): The ID of the author to fetch.

        Returns:
            Author: The Author instance or None if not found.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM authors WHERE id = ?", (author_id,))
        author_data = cursor.fetchone()
        connection.close()
        if author_data:
            return Author(author_data["id"], author_data["name"])
        return None
#DELETE
    def delete_from_db(self):
        """
        Delete the author from the database.

        Raises:
            ValueError: If the author has not been saved to the database.
        """
        if not self.id:
            raise ValueError("Author must exist in the database to be deleted.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM authors WHERE id = ?", (self.id,))
        connection.commit()
        connection.close()

    def articles(self):
        """
        Fetch all articles written by this author.

        Returns:
            list: A list of Article instances.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT articles.id, articles.title, articles.content, articles.author_id, articles.magazine_id
            FROM articles
            WHERE articles.author_id = ?
            """,
            (self.id,),
        )
        articles = cursor.fetchall()
        connection.close()
        return [
            Article(
                article["id"], article["title"], article["content"],
                article["author_id"], article["magazine_id"]
            ) for article in articles
        ]

    def magazines(self):
        """
        Fetch all magazines to which this author has contributed articles.

        Returns:
            list: A list of Magazine instances.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT DISTINCT magazines.id, magazines.name, magazines.category
            FROM magazines
            JOIN articles ON magazines.id = articles.magazine_id
            WHERE articles.author_id = ?
            """,
            (self.id,),
        )
        magazines = cursor.fetchall()
        connection.close()
        return [
            Magazine(magazine["id"], magazine["name"], magazine["category"])
            for magazine in magazines
        ]
