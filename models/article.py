from database.connection import get_db_connection

class Article:
    def __init__(self, id, title, content, author_id, magazine_id):
        """
        Initialize an Article instance.

        Args:
            id (int): The unique ID of the article. Can be None for unsaved articles.
            title (str): The title of the article.
            content (str): The content of the article.
            author_id (int): The ID of the author who wrote the article.
            magazine_id (int): The ID of the magazine the article belongs to.
        """
        if id is not None and not isinstance(id, int):
            raise ValueError("ID must be None or an integer.")
        self.id = id
        self._validate_title(title)
        self._title = title
        self.content = content
        self.author_id = author_id
        self.magazine_id = magazine_id

    def __repr__(self):
        return f'<Article {getattr(self, "title", "No Title")}>'

    def _validate_title(self, title):
        """
        Validate the title of the article.

        Args:
            title (str): The title to validate.

        Raises:
            ValueError: If the title is not a string or not within the required length.
        """
        if not isinstance(title, str) or not (5 <= len(title) <= 50):
            raise ValueError("Title must be a string between 5 and 50 characters.")

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        """
        Update the title of the article with validation.

        Args:
            value (str): The new title of the article.
        """
        self._validate_title(value)  # Validate the new title
        self._title = value  # Update the title

    def save_to_db(self):
        """
        Save the article to the database. If the article already has an ID, it raises an error.

        Raises:
            AttributeError: If the article has already been saved.
        """
        if hasattr(self, 'id') and self.id is not None:
            raise AttributeError("Article already saved to the database.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO articles (title, content, author_id, magazine_id)
            VALUES (?, ?, ?, ?)
            """,
            (self.title, self.content, self.author_id, self.magazine_id),
        )
        connection.commit()
        self.id = cursor.lastrowid
        connection.close()

    def update_to_db(self):
        """
        Update the article details in the database.

        Raises:
            ValueError: If the article does not exist in the database.
        """
        if not self.id:
            raise ValueError("Article must exist in the database to update.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE articles
            SET title = ?, content = ?, author_id = ?, magazine_id = ?
            WHERE id = ?
            """,
            (self.title, self.content, self.author_id, self.magazine_id, self.id),
        )
        connection.commit()
        connection.close()

    @staticmethod
    def fetch_all():
        """
        Fetch all articles from the database.

        Returns:
            list: A list of Article instances.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM articles")
        articles = cursor.fetchall()
        connection.close()
        return [
            Article(
                article["id"], article["title"], article["content"],
                article["author_id"], article["magazine_id"]
            ) for article in articles
        ]

    @staticmethod
    def fetch_by_id(article_id):
        """
        Fetch an article by its ID.

        Args:
            article_id (int): The ID of the article to fetch.

        Returns:
            Article: The Article instance or None if not found.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        article_data = cursor.fetchone()
        connection.close()
        if article_data:
            return Article(
                article_data["id"], article_data["title"], article_data["content"],
                article_data["author_id"], article_data["magazine_id"]
            )
        return None

    def delete_from_db(self):
        """
        Delete the article from the database.

        Raises:
            ValueError: If the article has not been saved to the database.
        """
        if not self.id:
            raise ValueError("Article must exist in the database to be deleted.")
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM articles WHERE id = ?", (self.id,))
        connection.commit()
        connection.close()

    @property
    def author(self):
        """
        Fetch the author of the article.

        Returns:
            Author: The Author instance associated with this article.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT authors.id, authors.name
            FROM authors
            JOIN articles ON authors.id = articles.author_id
            WHERE articles.id = ?
            """,
            (self.id,),
        )
        author_data = cursor.fetchone()
        connection.close()
        if author_data:
            return Author(author_data["id"], author_data["name"])
        return None

    @property
    def magazine(self):
        """
        Fetch the magazine of the article.

        Returns:
            Magazine: The Magazine instance associated with this article.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT magazines.id, magazines.name, magazines.category
            FROM magazines
            JOIN articles ON magazines.id = articles.magazine_id
            WHERE articles.id = ?
            """,
            (self.id,),
        )
        magazine_data = cursor.fetchone()
        connection.close()
        if magazine_data:
            return Magazine(
                magazine_data["id"], magazine_data["name"], magazine_data["category"]
            )
        return None
