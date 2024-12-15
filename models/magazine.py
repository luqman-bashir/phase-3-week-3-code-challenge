from database.connection import get_db_connection

class Magazine:
    def __init__(self, id, name, category):
        """
        Initialize a Magazine instance.

        Args:
            id (int): The unique ID of the magazine. Can be None for unsaved magazines.
            name (str): The name of the magazine.
            category (str): The category of the magazine.
        """
        if id is not None and not isinstance(id, int):
            raise ValueError("ID must be None or an integer.")
        self.id = id
        self._validate_name(name)
        self._validate_category(category)
        self._name = name
        self._category = category

    def __repr__(self):
        return f'<Magazine {self.name}>'

    def _validate_name(self, name):
        """
        Validate the name of the magazine.

        Args:
            name (str): The name to validate.

        Raises:
            ValueError: If the name is not a string or not within the required length.
        """
        if not isinstance(name, str) or not (2 <= len(name) <= 16):
            raise ValueError("Name must be a string between 2 and 16 characters.")

    def _validate_category(self, category):
        """
        Validate the category of the magazine.

        Args:
            category (str): The category to validate.

        Raises:
            ValueError: If the category is not a non-empty string.
        """
        if not isinstance(category, str) or len(category) == 0:
            raise ValueError("Category must be a non-empty string.")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        """
        Update the name of the magazine with validation.

        Args:
            value (str): The new name of the magazine.
        """
        self._validate_name(value)
        self._name = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        """
        Update the category of the magazine with validation.

        Args:
            value (str): The new category of the magazine.
        """
        self._validate_category(value)
        self._category = value

    def save_to_db(self):
        """
        Save the magazine to the database. If the magazine already has an ID, it raises an error.

        Raises:
            AttributeError: If the magazine has already been saved.
        """
        if hasattr(self, 'id') and self.id is not None:
            raise AttributeError("Magazine already saved to the database.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO magazines (name, category) VALUES (?, ?)",
            (self.name, self.category),
        )
        connection.commit()
        self.id = cursor.lastrowid
        connection.close()

    def update_to_db(self):
        """
        Update the magazine details in the database.

        Raises:
            ValueError: If the magazine does not exist in the database.
        """
        if not self.id:
            raise ValueError("Magazine must exist in the database to update.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE magazines SET name = ?, category = ? WHERE id = ?",
            (self.name, self.category, self.id),
        )
        connection.commit()
        connection.close()

    @staticmethod
    def fetch_all():
        """
        Fetch all magazines from the database.

        Returns:
            list: A list of Magazine instances.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM magazines")
        magazines = cursor.fetchall()
        connection.close()
        return [
            Magazine(magazine["id"],magazine["name"],magazine["category"])
            for magazine in magazines

        ]

    @staticmethod
    def fetch_by_id(magazine_id):
        """
        Fetch a magazine by its ID.

        Args:
            magazine_id (int): The ID of the magazine to fetch.

        Returns:
            Magazine: The Magazine instance or None if not found.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM magazines WHERE id = ?", (magazine_id,))
        magazine_data = cursor.fetchone()
        connection.close()
        if magazine_data:
            return Magazine(magazine_data["id"], magazine_data["name"], magazine_data["category"])
        return None

    def delete_from_db(self):
        """
        Delete the magazine from the database.

        Raises:
            ValueError: If the magazine has not been saved to the database.
        """
        if not self.id:
            raise ValueError("Magazine must exist in the database to be deleted.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM magazines WHERE id = ?", (self.id,))
        connection.commit()
        connection.close()

    def articles(self):
        """
        Fetch all articles associated with this magazine.

        Returns:
            list: A list of Article instances.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT articles.id, articles.title, articles.content, articles.author_id, articles.magazine_id
            FROM articles
            WHERE articles.magazine_id = ?
            """,
            (self.id,),
        )
        articles = cursor.fetchall()
        connection.close()
        return [
            Article(
                article["id"], article["title"], article["content"],
                article["author_id"], article["magazine_id"]
            )
            for article in articles
        ]

    def contributors(self):
        """
        Fetch all unique authors who have written for this magazine.

        Returns:
            list: A list of Author instances.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT DISTINCT authors.id, authors.name
            FROM authors
            JOIN articles ON authors.id = articles.author_id
            WHERE articles.magazine_id = ?
            """,
            (self.id,),
        )
        authors = cursor.fetchall()
        connection.close()
        return [
            Author(author["id"], author["name"]) for author in authors
        ]

    def article_titles(self):
        """
        Fetch all article titles associated with this magazine.

        Returns:
            list: A list of article titles or None if there are no articles.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT articles.title
            FROM articles
            WHERE articles.magazine_id = ?
            """,
            (self.id,),
        )
        titles = cursor.fetchall()
        connection.close()
        return [title["title"] for title in titles] or None

    def contributing_authors(self):
        """
        Fetch all authors who have contributed more than 2 articles to this magazine.

        Returns:
            list: A list of Author instances or None if no such authors exist.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT authors.id, authors.name
            FROM authors
            JOIN articles ON authors.id = articles.author_id
            WHERE articles.magazine_id = ?
            GROUP BY authors.id, authors.name
            HAVING COUNT(articles.id) > 2
            """,
            (self.id,),
        )
        authors = cursor.fetchall()
        connection.close()
        if not authors:
            return None
        return [
            Author(author["id"], author["name"]) for author in authors
        ]
