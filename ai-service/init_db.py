import pymysql
import os
import re

# Database Configuration
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "root"
SCHEMA_FILE = "../database/schema.sql"

def get_connection(db_name=None):
    kwargs = dict(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True,
    )
    if db_name:
        kwargs['database'] = db_name
    return pymysql.connect(**kwargs)

def execute_script(filename):
    print(f"Reading schema from {filename}...")
    with open(filename, 'r') as f:
        content = f.read()

    # Split by DELIMITER statements to handle procedures/triggers
    # This is a basic parser for the specific format in schema.sql
    
    # Normalize line endings
    content = content.replace('\r\n', '\n')
    
    # Remove comments (basic)
    # content = re.sub(r'--.*', '', content) # Don't remove -- inside strings/code
    
    commands = []
    current_command = []
    delimiter = ";"
    
    lines = content.split('\n')
    
    for line in lines:
        line_clean = line.strip()
        
        # skip empty lines and comments (if start of line)
        if not line_clean or line_clean.startswith('--'):
            continue
            
        if line_clean.startswith('DELIMITER'):
            delimiter = line_clean.split()[1]
            continue
            
        current_command.append(line)
        
        if line_clean.endswith(delimiter):
            # End of command
            # Remove delimiter from the end of the last line
            cmd_str = '\n'.join(current_command)
            
            # For standard semicolon, standard split
            # For custom delimiter like $$, remove it
            if delimiter != ';':
                if cmd_str.endswith(delimiter):
                    cmd_str = cmd_str[:-len(delimiter)]
            else:
                if cmd_str.endswith(';'):
                    cmd_str = cmd_str[:-1]
            
            commands.append(cmd_str.strip())
            current_command = []
            
    print(f"Parsed {len(commands)} commands.")
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for i, cmd in enumerate(commands):
                if not cmd:
                    continue
                try:
                    # Special handling for create database usage
                    if "CREATE DATABASE" in cmd:
                        print(f"Creating database...")
                    elif "USE" in cmd:
                        print(f"Switching database...")
                        
                    cursor.execute(cmd)
                except Exception as e:
                    print(f"Error executing command #{i+1}:\n{cmd[:50]}...\nError: {e}")
                    # Don't stop on errors (some drops might fail)
                    # allow failure for DROP DATABASE or existing tables
        conn.commit()
        print("Schema execution completed successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    execute_script(SCHEMA_FILE)
