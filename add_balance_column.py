import sqlite3

def add_balance_column():
    # Connect to the database
    conn = sqlite3.connect('instance/aveum.db')
    cursor = conn.cursor()
    
    try:
        # Add balance column if it doesn't exist
        cursor.execute('''
            ALTER TABLE user 
            ADD COLUMN balance FLOAT DEFAULT 0.0
        ''')
        conn.commit()
        print("Balance column added successfully!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Balance column already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_balance_column()