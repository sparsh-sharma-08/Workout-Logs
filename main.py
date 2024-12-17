import sqlite3
import datetime

def initialize_db():
    conn = sqlite3.connect("workout_log.db")
    cursor = conn.cursor()

    # Create Workout Sessions table
    cursor.execute("""CREATE TABLE IF NOT EXISTS workout_sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_time TEXT NOT NULL,
                        target_muscle TEXT NOT NULL)
                   """)
    
    # Create Workout Exercises table
    cursor.execute("""CREATE TABLE IF NOT EXISTS workout_exercises (
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

def reset_autoincrement(conn):
    """Reset AUTOINCREMENT if tables are empty."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='workout_sessions'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='workout_exercises'")
    except sqlite3.Error as e:
        print(f"Error resetting AUTOINCREMENT: {e}")

def get_time():
    """Prompt user for time input or use current time."""
    while True:
        choice = input("Do you want to set the current date and time (y/n): ").strip().lower()
        if choice == "y":
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%d-%m-%Y | %I:%M %p")
            print(f"Current Time: {formatted_time}")
            return formatted_time
        elif choice == "n":
            user_input_time = input("Enter the date and time (DD-MM-YYYY HH:MM AM/PM): ")
            try:
                custom_time = datetime.datetime.strptime(user_input_time, "%d-%m-%Y %I:%M %p")
                formatted_custom_time = custom_time.strftime("%d-%m-%Y | %I:%M %p")
                print(f"Entered Time: {formatted_custom_time}")
                return formatted_custom_time
            except ValueError:
                print("Invalid format! Use DD-MM-YYYY HH:MM AM/PM.")
        else:
            print("Please enter 'y' or 'n' only.")

def log_workout(conn):
    """Log a new workout session and exercises."""
    workout_time = get_time()
    target_muscle = input("Enter Target Muscle Group: ").strip().title()

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO workout_sessions (date_time, target_muscle) VALUES (?, ?)", 
                       (workout_time, target_muscle))
        session_id = cursor.lastrowid
        print(f"\nSession Logged Successfully! Session ID: {session_id}")

        # Add exercises to the session
        print("\nAdd exercises to this session. Press 'ENTER' to stop.")
        while True:
            exercise_name = input("Enter Exercise Name (or press 'ENTER' to stop): ").strip().title()
            if not exercise_name:
                break
            
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
                    print("Invalid input! Please enter valid numerical values.")
            
            # Insert all sets into the database
            for set_number, weight, reps in sets:
                cursor.execute("""INSERT INTO workout_exercises 
                                  (session_id, exercise_name, set_number, weight, reps) 
                                  VALUES (?, ?, ?, ?, ?)""", 
                               (session_id, exercise_name, set_number, weight, reps))
                print(f"'{exercise_name}' - Set {set_number} added.")
        conn.commit()
        print("\nAll exercises logged successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def view_logs(conn):
    """View workout sessions and exercises."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workout_sessions")
        sessions = cursor.fetchall()

        if not sessions:
            print("\nNo workout sessions found!")
            return

        print("\nWorkout Sessions:")
        print("=" * 60)
        for session in sessions:
            print(f"Session ID: {session[0]} | Date & Time: {session[1]} | Target Muscle: {session[2]}")
        print("=" * 60)

        # Display exercises grouped by session
        cursor.execute("""SELECT session_id, exercise_name, set_number, weight, reps 
                          FROM workout_exercises ORDER BY session_id, set_number""")
        exercises = cursor.fetchall()

        print("\nExercises:")
        print("=" * 60)
        for session_id, exercise_name, set_number, weight, reps in exercises:
            print(f"Session ID: {session_id} | Exercise: {exercise_name} | Set: {set_number} | "
                  f"Weight: {weight} KG | Reps: {reps}")
        print("=" * 60)
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def delete_log(conn):
    """Delete a workout session or exercise."""
    try:
        cursor = conn.cursor()
        print("\n1. Delete a Workout Session")
        print("2. Delete a Specific Exercise")

        choice = input("Choose the option (1 or 2): ").strip()
        if choice == "1":
            cursor.execute("SELECT * FROM workout_sessions")
            sessions = cursor.fetchall()
            if not sessions:
                print("\nNo sessions to delete!")
                return

            for session in sessions:
                print(f"Session ID: {session[0]} | Date & Time: {session[1]} | Target Muscle: {session[2]}")

            session_id = input("Enter the Session ID to delete: ").strip()
            cursor.execute("DELETE FROM workout_exercises WHERE session_id=?", (session_id,))
            cursor.execute("DELETE FROM workout_sessions WHERE session_id=?", (session_id,))
            print("\nSession and its exercises deleted successfully.")
        
        elif choice == "2":
            cursor.execute("SELECT * FROM workout_exercises")
            exercises = cursor.fetchall()
            if not exercises:
                print("\nNo exercises to delete!")
                return

            for exercise in exercises:
                print(f"Exercise ID: {exercise[0]} | Session ID: {exercise[1]} | Exercise: {exercise[2]} | "
                      f"Set: {exercise[3]} | Weight: {exercise[4]} KG | Reps: {exercise[5]}")
            
            exercise_id = input("Enter the Exercise ID to delete: ").strip()
            cursor.execute("DELETE FROM workout_exercises WHERE exercise_id=?", (exercise_id,))
            print("\nExercise deleted successfully.")
        
        else:
            print("Invalid choice.")
        
        # Reset AUTOINCREMENT if needed
        reset_autoincrement(conn)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def clear_all_logs(conn):
    """Clear all workout logs."""
    try:
        confirm = input("\nAre you sure you want to clear all logs? (y/n): ").strip().lower()
        if confirm == "y":
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workout_exercises")
            cursor.execute("DELETE FROM workout_sessions")
            reset_autoincrement(conn)
            conn.commit()
            print("\nAll logs have been cleared.")
        else:
            print("\nOperation canceled.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def main():
    conn = initialize_db()
    try:
        while True:
            print("\nWorkout Tracker")
            print("1. Log New Workout")
            print("2. View Workout Logs")
            print("3. Delete Log")
            print("4. Clear All Logs")
            print("5. Exit")

            choice = input("Enter your choice: ").strip()
            match choice:
                case '1': log_workout(conn)
                case '2': view_logs(conn)
                case '3': delete_log(conn)
                case '4': clear_all_logs(conn)
                case '5': break
                case _: print("Invalid choice! Please enter a valid option.")
    except Exception as e:
        print(f"Error encountered: {e}")
if __name__ == "__main__":
    main()