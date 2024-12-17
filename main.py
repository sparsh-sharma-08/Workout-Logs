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
    return conn

def get_time():
    while True:
        choice=input("Do you want to set the current date and time (y/n): ").strip().lower()
        if choice=="y":
                current_time=datetime.datetime.now()
                formatted_time=current_time.strftime("%d-%m-%Y | %I:%M %p")
                print(formatted_time)
                return formatted_time
        elif choice=="n":
                user_input_time= input("Enter the date and time (DD-MM-YYYY HH:MM AM/PM): ")
                try:
                    custom_time=datetime.datetime.strptime(user_input_time, "%d-%m-%Y %I:%M %p")
                    formated_custom_time=custom_time.strftime("%d-%m-%Y | %I:%M %p")
                    print(f"Entered Time: {formated_custom_time}")
                    return formated_custom_time
                except ValueError:
                    print("Invalid format! Use DD-MM-YYYY HH-MM AM/PM")
        else:
            print("Enter 'y' or 'n' only!")

def log_workout(conn):
    workout_time = get_time()
    target_muscle_choice = input("Enter Target Muscles: ").strip().title()

    try:
        cursor = conn.cursor()
        insert_query = """INSERT INTO workout_sessions (date_time, target_muscle)
                          VALUES(?,?)"""
        cursor.execute(insert_query, (workout_time, target_muscle_choice))

        session_id = cursor.lastrowid
        print(f"Session Logged Successfully! session_id {session_id}")

        # Add exercises to this session
        print("\nAdd exercises to this session. Press 'ENTER' to stop.")
        while True:
            exercise_name = input("Enter Exercise Name (or press 'ENTER' to stop): ").strip().title()
            if exercise_name.lower() == "":
                break

            # Handle multiple sets for the same exercise
            sets = []
            while True:
                try:
                    set_number = int(input("Set Number: "))
                    weight = float(input("Weight Used (in KG): "))
                    reps = int(input("Total Reps Performed: "))
                    
                    if set_number <= 0 or weight <= 0 or reps <= 0:
                        print("Please enter positive values for set number, weight, and reps.")
                        continue
                    
                    sets.append((set_number, weight, reps))

                    more_sets = input("Do you want to add another set for this exercise? (y/n): ").strip().lower()
                    if more_sets != 'y':
                        break
                except ValueError:
                    print("Invalid input! Please enter valid numerical values for set, weight, and reps.")
            
            # Insert multiple sets for the exercise
            for set_number, weight, reps in sets:
                insert_exercise_query = """INSERT INTO workout_exercises
                                           (session_id, exercise_name, set_number, weight, reps)
                                           VALUES (?, ?, ?, ?, ?)"""
                cursor.execute(insert_exercise_query, (session_id, exercise_name, set_number, weight, reps))
                print(f"'{exercise_name}' - Set {set_number} added to the database.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")

def view_log(conn):
    try:
        cursor = conn.cursor()

        # Ask user if they want detailed session information
        detail_choice = input("Do you want to view session details along with exercises? (y/n): ").strip().lower()

        # Display Workout Sessions if user chooses to see session details
        if detail_choice == 'y':
            cursor.execute("SELECT * FROM workout_sessions")
            sessions = cursor.fetchall()
            print("\nWorkout Sessions:")
            print("=" * 50)
            for session in sessions:
                session_id, date_time, target_muscle = session
                print(f"Session ID: {session_id}")
                print(f"Date & Time: {date_time}")
                print(f"Target Muscle: {target_muscle}")
                print("-" * 50)

        # Display Exercises with grouped sets (always show exercises)
        cursor.execute("""
        SELECT exercise_name,
               GROUP_CONCAT(set_number ORDER BY set_number) AS set_numbers,
               GROUP_CONCAT(weight ORDER BY set_number) AS weights,
               GROUP_CONCAT(reps ORDER BY set_number) AS reps
        FROM workout_exercises
        GROUP BY exercise_name
        """)
        exercises = cursor.fetchall()

        print("\nExercises:")
        print("=" * 50)
        for exercise in exercises:
            exercise_name = exercise[0]
            set_numbers = exercise[1]
            weights = exercise[2]
            reps = exercise[3]

            # Split the concatenated values into lists
            set_numbers_list = set_numbers.split(',')
            weights_list = weights.split(',')
            reps_list = reps.split(',')

            print(f"\nExercise Name: {exercise_name}")
            print(f"Sets: {', '.join(set_numbers_list)}")
            print(f"Weights (KG): {', '.join(weights_list)}")
            print(f"Reps: {', '.join(reps_list)}")
            print("-" * 50)

    except sqlite3.Error as e:
        print(f"Database Error: {e}")

def view_exercises(conn):
    pass

def update_log():
    pass

def generate_report():
    pass

def main():
    conn=initialize_db()
    try:
        while True:
            print("Workout Tracker")
            print("1. Log New Workout")
            print("2. View Complete Workout Logs (sessions and exercises)")
            print("3. View Only Exercises Logs")
            print("4. Update Log")
            print("5. Generate Performance Report")
            print("6. Exit")

            user_input=input("Enter the operation: ")
            match user_input:
                case '1':
                    log_workout(conn)
                case '2':
                    view_log(conn)
                case '3':
                    view_exercises(conn)
                case '4':
                    update_log(conn)
                case '5':
                    generate_report(conn)
                case '6':
                    break
                case _:
                    print("Please enter a valid input!")
    except Exception as e:
        print(f"Error Encounterd: {e}")


if __name__=="__main__":
    main()