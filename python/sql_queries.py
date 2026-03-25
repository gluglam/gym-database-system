# sql_queries.py
"""
Collection of queries used by the application.
Contains both:
- DML sequences (INSERT/UPDATE/DELETE) to demonstrate the full cycle,
- showcase SELECTs compliant with the requirements (JOIN, GROUP BY, HAVING, EXISTS/NOT EXISTS, subqueries, ANY/ALL equivalents).

Note: SQLite does not support the ANY/ALL syntax directly like PostgreSQL, for example,
but semantic equivalents can be shown (ALL -> MAX/MIN, ANY -> MIN/MAX).
"""

# =========================
# Members
# =========================

Q_MEMBERS_LIST = """
SELECT
  c.id_osoby,
  o.imie,
  o.nazwisko,
  o.email,
  COALESCE(GROUP_CONCAT(t.nr_tel, ', '), '') AS telefony,
  c.data_dolaczenia,
  c.status AS status_czlonka,
  (
    SELECT zk.status
    FROM Zakup_karnetu zk
    WHERE zk.id_osoby = c.id_osoby
      AND date('now') BETWEEN zk.data_rozpoczecia AND zk.data_zakonczenia
    ORDER BY zk.data_zakupu DESC
    LIMIT 1
  ) AS status_aktywny_karnet
FROM Czlonek c
JOIN Osoba o ON o.id_osoby = c.id_osoby
LEFT JOIN Nr_telefonu t ON t.id_osoby = o.id_osoby
GROUP BY c.id_osoby
ORDER BY o.nazwisko, o.imie;
"""

Q_MEMBERS_SEARCH = """
SELECT
  c.id_osoby, o.imie, o.nazwisko, o.email,
  COALESCE(GROUP_CONCAT(t.nr_tel, ', '), '') AS telefony,
  c.data_dolaczenia,
  c.status
FROM Czlonek c
JOIN Osoba o ON o.id_osoby = c.id_osoby
LEFT JOIN Nr_telefonu t ON t.id_osoby = o.id_osoby
WHERE (o.nazwisko LIKE ? OR o.email LIKE ?)
  AND (? = '' OR c.status = ?)
GROUP BY c.id_osoby
ORDER BY o.nazwisko;
"""

# Member addition sequence: 3 inserts (Osoba -> Nr_telefonu -> Czlonek)
Q_MEMBER_ADD_OSOBA = """
INSERT INTO Osoba(imie, nazwisko, email, data_urodzenia, stworzone_dnia)
VALUES(?, ?, ?, ?, date('now'));
"""
Q_MEMBER_ADD_PHONE = """
INSERT INTO Nr_telefonu(nr_tel, id_osoby)
VALUES(?, last_insert_rowid());
"""
Q_MEMBER_ADD_CZLONEK = """
INSERT INTO Czlonek(id_osoby, data_dolaczenia, status)
VALUES(last_insert_rowid(), date('now'), 'active');
"""
Q_MEMBER_DELETE = "DELETE FROM Osoba WHERE id_osoby = ?;"

# NOT EXISTS
Q_INACTIVE_90D = """
SELECT
  c.id_osoby, o.imie, o.nazwisko, c.status
FROM Czlonek c
JOIN Osoba o ON o.id_osoby = c.id_osoby
WHERE NOT EXISTS (
  SELECT 1
  FROM Zakup_karnetu zk
  WHERE zk.id_osoby = c.id_osoby
    AND date(zk.data_zakupu) >= date('now', '-90 day')
)
ORDER BY o.nazwisko, o.imie;
"""

# HAVING
Q_VIP_MEMBERS_BY_YEAR = """
SELECT
  o.id_osoby,
  o.nazwisko || ' ' || o.imie AS czlonek,
  COUNT(*) AS liczba_zakupow,
  ROUND(SUM(zk.cena_koncowa), 2) AS suma
FROM Zakup_karnetu zk
JOIN Osoba o ON o.id_osoby = zk.id_osoby
WHERE strftime('%Y', zk.data_zakupu) = ?
  AND zk.status IN ('Aktywny','Opłacony','Wygasły')
GROUP BY o.id_osoby
HAVING COUNT(*) >= ?
ORDER BY suma DESC, liczba_zakupow DESC;
"""

# Dates
Q_EXPIRING_PASSES_14D = """
SELECT
  o.nazwisko, o.imie,
  zk.data_zakonczenia,
  pk.nazwa AS plan,
  zk.status
FROM Zakup_karnetu zk
JOIN Czlonek c ON c.id_osoby = zk.id_osoby
JOIN Osoba o ON o.id_osoby = c.id_osoby
JOIN Plan_karnetu pk ON pk.id_planu = zk.id_planu
WHERE zk.status IN ('Aktywny', 'Opłacony')
  AND date(zk.data_zakonczenia) BETWEEN date('now') AND date('now', '+14 day')
ORDER BY zk.data_zakonczenia ASC, o.nazwisko ASC;
"""

# =========================
# Passes + payments
# =========================

# INSERT...SELECT + last_insert_rowid()
Q_PURCHASE_INSERT = """
INSERT INTO Zakup_karnetu(
  data_zakupu, data_rozpoczecia, data_zakonczenia, cena_koncowa, status, id_planu, id_osoby
)
SELECT
  date('now'),
  date('now'),
  date('now', '+' || pk.dlugosc_dni || ' day'),
  pk.cena_bazowa,
  'active',
  pk.id_planu,
  ?
FROM Plan_karnetu pk
WHERE pk.id_planu = ?;
"""

Q_PAYMENT_INSERT_LAST = """
INSERT INTO Platnosc(kwota, metoda, data_platnosci, status, id_zakupu)
VALUES(?, ?, date('now'), ?, last_insert_rowid());
"""

# UPDATE + DELETE sequence (point 4b + 4c)
Q_PURCHASE_CANCEL = "UPDATE Zakup_karnetu SET status='cancelled' WHERE id_zakupu=?;"
Q_PURCHASE_DELETE = "DELETE FROM Zakup_karnetu WHERE id_zakupu=?;"

# GROUP BY + HAVING
Q_REVENUE_REPORT = """
SELECT
  strftime('%Y-%m', p.data_platnosci) AS miesiac,
  p.metoda,
  COUNT(*) AS liczba_platnosci,
  SUM(p.kwota) AS suma
FROM Platnosc p
WHERE strftime('%Y', p.data_platnosci) = ?
  AND p.status = 'Opłacona'
GROUP BY miesiac, p.metoda
HAVING SUM(p.kwota) > ?
ORDER BY miesiac, p.metoda;
"""

# HAVING
Q_TOP_PLANS = """
SELECT
  pk.nazwa,
  COUNT(*) AS liczba_zakupow,
  ROUND(AVG(zk.cena_koncowa), 2) AS srednia_cena
FROM Zakup_karnetu zk
JOIN Plan_karnetu pk ON pk.id_planu = zk.id_planu
WHERE strftime('%Y', zk.data_zakupu) = ?
GROUP BY pk.id_planu
HAVING COUNT(*) >= ?
ORDER BY liczba_zakupow DESC, pk.nazwa ASC;
"""

# JOIN + condition
Q_SUSPICIOUS_PAYMENTS = """
SELECT
  p.id_platnosci,
  p.data_platnosci,
  p.kwota,
  pk.nazwa AS plan,
  pk.cena_bazowa,
  o.nazwisko || ' ' || o.imie AS czlonek
FROM Platnosc p
JOIN Zakup_karnetu zk ON zk.id_zakupu = p.id_zakupu
JOIN Plan_karnetu pk ON pk.id_planu = zk.id_planu
JOIN Osoba o ON o.id_osoby = zk.id_osoby
WHERE p.status = 'Opłacona'
  AND p.kwota < pk.cena_bazowa
ORDER BY p.data_platnosci DESC;
"""

# ALL equivalent: > ALL(SELECT cena_bazowa FROM Plan_karnetu) === > MAX(cena_bazowa)
Q_PURCHASES_OVER_ALL_PLAN_PRICES = """
SELECT
  zk.id_zakupu,
  zk.cena_koncowa,
  pk.nazwa AS plan,
  o.nazwisko || ' ' || o.imie AS czlonek
FROM Zakup_karnetu zk
JOIN Plan_karnetu pk ON pk.id_planu = zk.id_planu
JOIN Osoba o ON o.id_osoby = zk.id_osoby
WHERE zk.cena_koncowa > (SELECT MAX(cena_bazowa) FROM Plan_karnetu)
ORDER BY zk.cena_koncowa DESC;
"""

# ANY equivalent: > ANY(S) === > MIN(S) (a more sensible example: payments greater than the minimum plan price)
Q_PAYMENTS_OVER_ANY_PLAN_PRICE = """
SELECT
  p.id_platnosci,
  p.kwota,
  p.data_platnosci,
  o.nazwisko || ' ' || o.imie AS czlonek
FROM Platnosc p
JOIN Zakup_karnetu zk ON zk.id_zakupu = p.id_zakupu
JOIN Osoba o ON o.id_osoby = zk.id_osoby
WHERE p.status='Opłacona'
  AND p.kwota > (SELECT MIN(cena_bazowa) FROM Plan_karnetu)
ORDER BY p.kwota DESC, p.data_platnosci DESC;
"""

# =========================
# Classes
# =========================

Q_SCHEDULE_LIST = """
SELECT
  sz.id_sesji,
  tz.nazwa AS typ_zajec,
  COALESCE(o.nazwisko || ' ' || o.imie, 'Brak') AS trener,
  sz.czas_rozpoczecia,
  sz.sala,
  sz.liczebnosc AS limit_miejsc,
  COUNT(z.id_osoby) AS zapisanych,
  (sz.liczebnosc - COUNT(z.id_osoby)) AS wolnych
FROM Sesja_zajec sz
JOIN Typ_zajec tz ON tz.id_typu = sz.id_typu
LEFT JOIN Trener t ON t.id_osoby = sz.id_osoby
LEFT JOIN Osoba o ON o.id_osoby = t.id_osoby
LEFT JOIN Zapis z
  ON z.id_sesji = sz.id_sesji
 AND z.status IN ('confirmed', 'present')
GROUP BY sz.id_sesji
ORDER BY sz.czas_rozpoczecia DESC;
"""

Q_NEARLY_FULL = """
SELECT
  sz.id_sesji,
  tz.nazwa,
  sz.czas_rozpoczecia,
  sz.liczebnosc,
  COUNT(z.id_osoby) AS zapisanych,
  ROUND(100.0 * COUNT(z.id_osoby) / sz.liczebnosc, 1) AS procent
FROM Sesja_zajec sz
JOIN Typ_zajec tz ON tz.id_typu = sz.id_typu
LEFT JOIN Zapis z
  ON z.id_sesji = sz.id_sesji
 AND z.status IN ('Potwierdzony')
GROUP BY sz.id_sesji
HAVING (1.0 * COUNT(z.id_osoby) / sz.liczebnosc) >= 0.80
ORDER BY procent DESC, sz.czas_rozpoczecia DESC;
"""

# 1 SQL with validation (EXISTS / NOT EXISTS / limit)
# parameters: (mid, sid, mid, mid, sid, mid, sid, sid, sid, sid)
Q_SIGNUP_FANCY = """
INSERT INTO Zapis(data_zapisu, status, godzina_wejscia, id_osoby, id_sesji)
SELECT
  date('now'),
  'confirmed',
  strftime('%H:%M', 'now'),
  ?,
  ?
WHERE
  EXISTS (SELECT 1 FROM Czlonek c WHERE c.id_osoby = ? AND c.status = 'active')
  AND EXISTS (
    SELECT 1 FROM Zakup_karnetu zk
    WHERE zk.id_osoby = ?
      AND zk.status IN ('Aktywny','Zakończony')
      AND date('now') BETWEEN zk.data_rozpoczecia AND zk.data_zakonczenia
  )
  AND EXISTS (
    SELECT 1 FROM Sesja_zajec sz
    WHERE sz.id_sesji = ?
      AND sz.status IN ('scheduled', 'open')
  )
  AND NOT EXISTS (
    SELECT 1 FROM Zapis z
    WHERE z.id_osoby = ? AND z.id_sesji = ? AND z.data_zapisu = date('now')
  )
  AND (
    SELECT COUNT(*)
    FROM Zapis z2
    WHERE z2.id_sesji = ?
      AND z2.status IN ('Potwierdzony')
  ) < (
    SELECT sz2.liczebnosc FROM Sesja_zajec sz2 WHERE sz2.id_sesji = ?
  );
"""

# =========================
# Equipment
# =========================

Q_EQUIPMENT_OPEN_TICKETS = """
SELECT
  s.id_sprzetu,
  s.nazwa,
  s.kategoria,
  s.status AS status_sprzetu,
  COUNT(zs.id_zgloszenia) AS otwartych_zgloszen
FROM Sprzet s
LEFT JOIN Zgloszenia_serwisowe zs
  ON zs.id_sprzetu = s.id_sprzetu
 AND zs.status IN ('Zgłoszone', 'W toku', 'Do wymiany')
GROUP BY s.id_sprzetu
HAVING otwartych_zgloszen > 0
ORDER BY otwartych_zgloszen DESC, s.kategoria, s.nazwa;
"""

# =========================
# Employees / service
# =========================

Q_EMPLOYEES_LIST = """
SELECT
  p1.id_osoby,
  o1.imie,
  o1.nazwisko,
  p1.rola,
  p1.wynagrodzenie,
  p1.data_zatrudnienia,
  COALESCE(o2.nazwisko || ' ' || o2.imie, 'Brak') AS przelozony,
  COALESCE(GROUP_CONCAT(t.nr_tel, ', '), '') AS telefony
FROM Pracownik p1
JOIN Osoba o1 ON o1.id_osoby = p1.id_osoby
LEFT JOIN Pracownik p2 ON p2.id_osoby = p1.nadzoruje
LEFT JOIN Osoba o2 ON o2.id_osoby = p2.id_osoby
LEFT JOIN Nr_telefonu t ON t.id_osoby = o1.id_osoby
GROUP BY p1.id_osoby
ORDER BY p1.rola, o1.nazwisko;
"""

Q_SERVICE_IN_PROGRESS = """
SELECT
  zs.id_zgloszenia,
  zs.data_zgloszenia,
  zs.priorytet,
  zs.status,
  s.nazwa AS sprzet,
  s.nr_seryjny,
  COALESCE(o.nazwisko || ' ' || o.imie, 'Nieprzypisane') AS pracownik
FROM Zgloszenia_serwisowe zs
JOIN Sprzet s ON s.id_sprzetu = zs.id_sprzetu
LEFT JOIN Pracownik p ON p.id_osoby = zs.id_osoby
LEFT JOIN Osoba o ON o.id_osoby = p.id_osoby
WHERE zs.status IN ('open','in_progress')
  AND (zs.id_osoby IS NULL OR zs.id_osoby IN (
        SELECT id_osoby
        FROM Pracownik
        WHERE rola IN ('service', 'manager')
      ))
ORDER BY
  CASE zs.priorytet
    WHEN 'high' THEN 1
    WHEN 'medium' THEN 2
    ELSE 3
  END,
  zs.data_zgloszenia DESC;
"""