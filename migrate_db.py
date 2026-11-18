import sqlite3
conn = sqlite3.connect('wanderwise.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(chat_sessions)")
cols = [row[1] for row in cursor.fetchall()]
print('chat_sessions columns:', cols)

# Add context_state if missing
if 'context_state' not in cols:
    cursor.execute("ALTER TABLE chat_sessions ADD COLUMN context_state TEXT DEFAULT '{}'")
    conn.commit()
    print('Added context_state column!')
else:
    print('context_state column already exists.')

cursor.execute("PRAGMA table_info(chat_messages)")
msg_cols = [row[1] for row in cursor.fetchall()]
print('chat_messages columns:', msg_cols)

conn.close()
print('DB migration complete.')

