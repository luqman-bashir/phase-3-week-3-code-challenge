import os
from database.setup import create_tables
from models.article import Article
from models.author import Author
from models.magazine import Magazine
from database.connection import get_db_connection

def clear_terminal():
    """
    Clear the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    create_tables()

    while True:
        clear_terminal()
        print("\nOptions:")
        print("1. Create a new record")
        print("2. Update a record")
        print("3. Delete a record")
        print("4. View all records")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            clear_terminal()
            # Create new records
            author_name = input("Enter author's name: ")
            magazine_name = input("Enter magazine name: ")
            magazine_category = input("Enter magazine category: ")
            article_title = input("Enter article title: ")
            article_content = input("Enter article content: ")

            author = Author(None, author_name)
            author.save_to_db()

            magazine = Magazine(None, magazine_name, magazine_category)
            magazine.save_to_db()

            article = Article(None, article_title, article_content, author.id, magazine.id)
            article.save_to_db()
            print("Records created successfully!")
            input("Press Enter to continue...")

        elif choice == "2":
            clear_terminal()
            # Update records
            print("\nRecord Types:")
            print("1. Author")
            print("2. Magazine")
            print("3. Article")
            record_choice = input("Enter your choice: ")

            if record_choice == "1":
                record_id = int(input("Enter Author ID: "))
                author = Author.fetch_by_id(record_id)
                if author:
                    new_name = input("Enter new name for the author: ")
                    author.name = new_name
                    author.update_to_db()
                    print("Author updated successfully.")
                else:
                    print("Author not found.")

            elif record_choice == "2":
                print("\nWhat would you like to update:")
                print("1. Name")
                print("2. Category")
                print("3. Both")
                update_choice = input("Enter your choice: ")

                record_id = int(input("Enter Magazine ID: "))
                magazine = Magazine.fetch_by_id(record_id)
                if magazine:
                    if update_choice == "1":
                        new_name = input("Enter new name for the magazine: ")
                        magazine.name = new_name
                    elif update_choice == "2":
                        new_category = input("Enter new category for the magazine: ")
                        magazine.category = new_category
                    elif update_choice == "3":
                        new_name = input("Enter new name for the magazine: ")
                        new_category = input("Enter new category for the magazine: ")
                        magazine.name = new_name
                        magazine.category = new_category
                    magazine.update_to_db()
                    print("Magazine updated successfully.")
                else:
                    print("Magazine not found.")

            elif record_choice == "3":
                record_id = int(input("Enter Article ID: "))
                article = Article.fetch_by_id(record_id)
                if article:
                    new_title = input("Enter new title for the article: ")
                    new_content = input("Enter new content for the article: ")
                    article.title = new_title
                    article.content = new_content
                    article.update_to_db()
                    print("Article updated successfully.")
                else:
                    print("Article not found.")
            input("Press Enter to continue...")

        elif choice == "3":
            clear_terminal()
            # Delete a record
            print("\nRecord Types:")
            print("1. Author")
            print("2. Magazine")
            print("3. Article")
            record_choice = input("Enter your choice: ")

            if record_choice == "1":
                record_id = int(input("Enter Author ID: "))
                author = Author.fetch_by_id(record_id)
                if author:
                    author.delete_from_db()
                    print("Author deleted successfully.")
                else:
                    print("Author not found.")

            elif record_choice == "2":
                record_id = int(input("Enter Magazine ID: "))
                magazine = Magazine.fetch_by_id(record_id)
                if magazine:
                    magazine.delete_from_db()
                    print("Magazine deleted successfully.")
                else:
                    print("Magazine not found.")

            elif record_choice == "3":
                record_id = int(input("Enter Article ID: "))
                article = Article.fetch_by_id(record_id)
                if article:
                    article.delete_from_db()
                    print("Article deleted successfully.")
                else:
                    print("Article not found.")
            input("Press Enter to continue...")

        elif choice == "4":
            clear_terminal()
            # View all records
            print("\nAuthors:")
            for author in Author.fetch_all():
                print(author)

            print("\nMagazines:")
            for magazine in Magazine.fetch_all():
                print(magazine)

            print("\nArticles:")
            for article in Article.fetch_all():
                print(article)

            # Example of Aggregate Method: Contributing Authors
            print("\nContributing Authors (Authors with more than 2 articles):")
            for magazine in Magazine.fetch_all():
                contributors = magazine.contributing_authors()
                if contributors:
                    print(f"Magazine: {magazine.name}")
                    for contributor in contributors:
                        print(contributor)

            input("Press Enter to continue...")

        elif choice == "5":
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
