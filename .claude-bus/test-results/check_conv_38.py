#!/usr/bin/env python3
"""Check messages in conversation 38"""

import sqlite3
import sys

db_path = r'D:\gpt-oss\data\gpt_oss.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check conversation exists
cursor.execute("SELECT id, title, message_count, last_message_at FROM conversations WHERE id = 38")
conv = cursor.fetchone()

print("\n=== CONVERSATION 38 ===")
if conv:
    print(f"ID: {conv[0]}, Title: {conv[1]}, Message Count: {conv[2]}, Last Message: {conv[3]}")
else:
    print("Conversation 38 NOT FOUND in database!")
    sys.exit(1)

# Check messages
cursor.execute("""
    SELECT id, role, content, token_count, model_name, created_at
    FROM messages
    WHERE conversation_id = 38
    ORDER BY created_at
""")

messages = cursor.fetchall()

print(f"\n=== MESSAGES IN CONVERSATION 38 (Total: {len(messages)}) ===\n")

for msg in messages:
    msg_id, role, content, token_count, model_name, created_at = msg
    print(f"Message ID: {msg_id}")
    print(f"Role: {role}")
    print(f"Content: {repr(content[:200] if content else 'EMPTY/NULL')}")
    print(f"Token Count: {token_count}")
    print(f"Model: {model_name}")
    print(f"Created: {created_at}")
    print("-" * 80)

conn.close()
