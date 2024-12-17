import sqlite3
import datetime

def initialize_db():
    conn=sqlite3.connect("workout_log.db")
    cursor=conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS workout_sessions(
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_time TEXT NOT NULL,
                    target_muscle TEXT NOT NULL)
                   """)
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS workout_exercises(
                    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    exercise_name TEXT NOT NULL,
                    set_number INTEGER NOT NULL,
                    weight REAL NOT NULL,
                    reps INTEGER NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES workout_sessions(session_id)
                   )""")
    
    conn.commit()
    conn.close()

def log_workout():
    pass

def view_log():
    pass

def generate_report():
    pass

def main():
    initialize_db()
    try:
        while True:
            print("Workout Tracker")
            print("1. Log New Workout")
            print("2. View Workout Logs")
            print("3. Generate Performance Report")
            print("4. Exit")

            user_input=input("Enter the operation: ")
            match user_input:
                case '1':
                    log_workout()
                case '2':
                    view_log()
                case '3':
                    generate_report()
                case '4':
                    break
                case _:
                    print("Please enter a valid input!")
    except Exception as e:
        print(f"Error Encounterd: {e}")


if __name__=="__main__":
    main()