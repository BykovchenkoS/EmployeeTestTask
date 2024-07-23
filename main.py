from connect_db import *
import sys
import random
import time
from datetime import datetime

def create_table():
    conn = connect()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lastName VARCHAR(50) NOT NULL,
                firstName VARCHAR(50) NOT NULL,
                middleName VARCHAR(50) NOT NULL,
                birthDate DATE NOT NULL,
                gender ENUM('Male', 'Female') NOT NULL,
                UNIQUE (lastName, firstName, middleName, birthDate)
            )
        ''')
        conn.commit()
        conn.close()


def optimize_database():
    try:
        conn = connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SHOW INDEX FROM employees WHERE Key_name = 'idx_gender'")
            result = cursor.fetchone()
            if not result:
                cursor.execute('CREATE INDEX idx_gender ON employees (gender)')

            cursor.execute("SHOW INDEX FROM employees WHERE Key_name = 'idx_lastName'")
            result = cursor.fetchone()
            if not result:
                cursor.execute('CREATE INDEX idx_lastName ON employees (lastName)')

            conn.commit()
            conn.close()
            print("Database optimized successfully.")
    except mysql.connector.Error as error:
        print(f"Error optimizing database: {error}")


class Employee:
    def __init__(self, lastName, firstName, middleName, birthDate, gender):
        self.lastName = lastName
        self.firstName = firstName
        self.middleName = middleName
        self.birthDate = birthDate
        self.gender = gender

    def save_to_db(self):
        try:
            conn = connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO employees (lastName, firstName, middleName, birthDate, gender)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (self.lastName, self.firstName, self.middleName, self.birthDate, self.gender))
                conn.commit()
                conn.close()
                print(f"Employee {self.lastName} {self.firstName} {self.middleName} saved to DB.")
        except mysql.connector.Error as error:
            print(f"Error saving employee to the database: {error}")

    def calculate_age(self):
        birth_date = datetime.strptime(self.birthDate, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

def list_employees():
    try:
        conn = connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lastName, firstName, middleName, birthDate, gender,
                       TIMESTAMPDIFF(YEAR, birthDate, CURDATE()) AS age
                FROM employees
                ORDER BY lastName
            ''')
            rows = cursor.fetchall()
            for row in rows:
                print(f"{row[0]} {row[1]} {row[2]}, {row[3]}, {row[4]}, {row[5]} years")
            conn.close()
    except mysql.connector.Error as error:
        print(f"Error listing employees: {error}")

def fill_data(count):
    genders = ['Male', 'Female']
    batch_size = 1000
    employees = []
    for i in range(count):
        lastName = f"Last{i}"
        firstName = f"First{i}"
        middleName = f"Middle{i}"
        birthDate = '2000-01-01'
        gender = random.choice(genders)
        employees.append((lastName, firstName, middleName, birthDate, gender))
        if len(employees) == batch_size:
            bulk_insert(employees)
            employees = []
    if employees:
        bulk_insert(employees)

    specific_employees = [(f"FLast{i}", f"First{i}", f"Middle{i}", '2000-01-01', 'Male') for i in range(100)]
    bulk_insert(specific_employees)

def bulk_insert(employees):
    try:
        conn = connect()
        if conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO employees (lastName, firstName, middleName, birthDate, gender)
                VALUES (%s, %s, %s, %s, %s)
            ''', employees)
            conn.commit()
            conn.close()
    except mysql.connector.Error as error:
        print(f"Error bulk inserting employees: {error}")

def query_and_measure_time():
    start_time = time.time()
    try:
        conn = connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM employees
                WHERE gender = 'Male' AND lastName LIKE 'F%'
            ''')
            rows = cursor.fetchall()
            for row in rows:
                print(f"ID: {row[0]}, Last Name: {row[1]}, First Name: {row[2]}, Middle Name: {row[3]}, Birth Date: {row[4]}, Gender: {row[5]}")
            conn.close()
    except mysql.connector.Error as error:
        print(f"Error querying employees: {error}")
    end_time = time.time()
    print(f"Query executed in {end_time - start_time:.2f} seconds")

def main():
    print("Arguments passed:", sys.argv)
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == '1':
            create_table()
        elif mode == '2':
            if len(sys.argv) == 7:
                _, _, lastName, firstName, middleName, birthDate, gender = sys.argv
                employee = Employee(lastName, firstName, middleName, birthDate, gender)
                employee.save_to_db()
            else:
                print("Invalid number of arguments for mode 2")
        elif mode == '3':
            list_employees()
        elif mode == '4':
            fill_data(1000000)
        elif mode == '5':
            query_and_measure_time()
        elif mode == '6':
            optimize_database()
        else:
            print("Unknown mode")
    else:
        print("No mode specified")

if __name__ == "__main__":
    main()
