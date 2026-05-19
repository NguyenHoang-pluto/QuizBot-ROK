import sqlite3

conn = sqlite3.connect('data/rok_quiz.db')
cur = conn.cursor()

# Tìm các câu hỏi chứa chữ "August" hoặc có "elmantaokuro"
cur.execute("SELECT id, question_text, answer_text FROM questions WHERE question_text LIKE '%elmantaokuro%' OR question_text LIKE '%Dee%' OR question_text LIKE '%Dax%'")
rows = cur.fetchall()

print(f"Tìm thấy {len(rows)} hàng khớp:")
for r in rows[:10]:
    print(f"ID: {r[0]}")
    print(f"  Q: {repr(r[1])}")
    print(f"  A: {repr(r[2])}")
