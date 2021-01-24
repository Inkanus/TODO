import json
import sqlite3
from sqlite3 import Error


class Todos:
    def __init__(self):
        try:
            with open("todos.json", "r") as f:
                self.todos = json.load(f)
        except FileNotFoundError:
            self.todos = []

    def all(self):
        return self.todos

    def get(self, id):
        todo = [todo for todo in self.all() if todo['id'] == id]
        if todo:
            return todo[0]
        return []

    def create(self, data):
        data.pop('csrf_token')
        self.todos.append(data)
        self.save_all()

    def update(self, id, data):
        todo = self.get(id)
        if todo:
            index = self.todos.index(todo)
            self.todos[index] = data
            self.save_all()
            return True
        return False

    def delete(self, id):
        todo = self.get(id)
        if todo:
            self.todos.remove(todo)
            self.save_all()
            return True
        return False

    def save_all(self):
        with open("todos.json", "w") as f:
            json.dump(self.todos, f)


class SQLiteTodos:
    FILEPATH = "todos.db"

    def __init__(self):
        self.connection = self.connect_to_database(self.FILEPATH)
        self.cursor = self.connection.cursor()
        self.create_table()

    def connect_to_database(self, filepath):
        conn = None
        try:
            conn = sqlite3.connect(filepath, check_same_thread=False)
        except Error as e:
            print(e)

        return conn

    def execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Error as e:
            print(e)

    def create_table(self):
        create_todos_sql = """
        CREATE TABLE IF NOT EXISTS Todos (
            id integer PRIMARY KEY AUTOINCREMENT,
            title text NOT NULL,
            description text NOT NULL,
            done bool
        );
        """
        self.execute_sql(create_todos_sql)

    def format_row(self, *rows):
        todos = []
        for row in rows:
            todos.append({
                "title": row[0],
                "description": row[1],
                "done": bool(row[2])})
        return todos

    def all(self):
        all_sql = """
        SELECT title, description, done
        FROM Todos
        """
        self.execute_sql(all_sql)
        return self.format_row(*self.cursor.fetchall())

    def get(self, id):
        get_sql = f"""
        SELECT title, description, done
        FROM Todos
        WHERE id == {id};
        """
        self.execute_sql(get_sql)
        result = self.cursor.fetchone()
        if result:
            return self.format_row(result)[0]
        return []

    def create(self, data):
        insert_sql = f"""
        INSERT INTO Todos (title, description, done)
        VALUES (
            '{data["title"]}',
            '{data["description"]}',
            {data["done"]}
        );
        """
        self.execute_sql(insert_sql)

    def update(self, id, data):
        data.pop('csrf_token')
        update_sql = f"""
            UPDATE Todos
            SET title='{data['title']}',
                description='{data['description']}',
                done={int(data['done'])}
            WHERE id = {id};
        """
        self.execute_sql(update_sql)

    def delete(self, id):
        delete_sql = f"""
        DELETE
        FROM Todos
        WHERE id = {id};
        """
        self.execute_sql(delete_sql)

todos = SQLiteTodos()
# todos = Todos()
