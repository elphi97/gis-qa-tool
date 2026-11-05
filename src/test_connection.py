# src/test_connection.py

from db import get_connection        # LUKA 1: co importujemy z pliku db.py?
# (nazwa funkcji, którą tam zdefiniowałeś)

# LUKA 2: wywołanie tej funkcji (bez argumentów)
conn = get_connection()

# LUKA 3: jak nazywa się metoda otwierająca kursor na obiekcie conn?
cur = conn.cursor()

# LUKA 4: zapytanie SQL sprawdzające wersję PostgreSQL

cur.execute("SELECT version();")

# (robiliśmy je już w pgAdmin/DBeaver wcześniej - inna komenda niż PostGIS_Full_Version)

# LUKA 5: metoda pobierająca JEDEN wiersz wyniku z kursora
result = cur.fetchone()
# (podpowiedź: "fetch" + coś)

print(result)

cur.close()
conn.close()                   # LUKA 6: jak zamykamy połączenie z bazą?
