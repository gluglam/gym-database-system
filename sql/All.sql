-- S1. Dodanie członka (3 inserty w 1 transakcji) — już masz, tylko pokaz jako sekwencję

BEGIN;

INSERT INTO Osoba(imie, nazwisko, email, data_urodzenia, stworzone_dnia)
VALUES(?, ?, ?, ?, date('now'));

INSERT INTO Nr_telefonu(nr_tel, id_osoby)
VALUES(?, last_insert_rowid());

INSERT INTO Czlonek(id_osoby, data_dolaczenia, status)
VALUES(last_insert_rowid(), date('now'), 'Aktywny');

COMMIT;


-- S2. Sprzedaż karnetu + płatność (INSERT…SELECT + last_insert_rowid)

BEGIN;

INSERT INTO Zakup_karnetu(
  data_zakupu, data_rozpoczecia, data_zakonczenia, cena_koncowa, status, id_planu, id_osoby
)
SELECT
  date('now'),
  date('now'),
  date('now', '+' || pk.dlugosc_dni || ' day'),
  pk.cena_bazowa,
  'Aktywny',
  pk.id_planu,
  ?
FROM Plan_karnetu pk
WHERE pk.id_planu = ?;

INSERT INTO Platnosc(kwota, metoda, data_platnosci, status, id_zakupu)
VALUES(?, ?, date('now'), ?, last_insert_rowid());

COMMIT;


-- S3. Zapis na zajęcia “1 SQL z walidacją” — Twoje Q_SIGNUP_FANCY jest idealne na pkt 4 (warunki + EXISTS + NOT EXISTS)

-- parametry: (mid, sid, mid, mid, sid, mid, sid, sid, sid, sid)
INSERT INTO Zapis(data_zapisu, status, godzina_wejscia, id_osoby, id_sesji)
SELECT date('now'),'Potwierdziny', strftime('%H:%M','now'), ?, ?
WHERE
  EXISTS (SELECT 1 FROM Czlonek c WHERE c.id_osoby = ? AND c.status = 'Aktywny')
  AND EXISTS (
    SELECT 1 FROM Zakup_karnetu zk
    WHERE zk.id_osoby = ?
      AND zk.status IN ('Aktywny')
      AND date('now') BETWEEN zk.data_rozpoczecia AND zk.data_zakonczenia
  )
  AND EXISTS (
    SELECT 1 FROM Sesja_zajec sz
    WHERE sz.id_sesji = ?
      AND sz.status IN ('Zaplanowana', 'Otwarta')
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
  ) < (SELECT sz2.liczebnosc FROM Sesja_zajec sz2 WHERE sz2.id_sesji = ?);


-- S4. “Anuluj zakup” + automatyczne usunięcie płatności (CASCADE) — sekwencja modyfikująca/usuwająca

BEGIN;

UPDATE Zakup_karnetu
SET status = ''
WHERE id_zakupu = ?;

-- jeśli chcesz “twardo” usunąć (wtedy płatności lecą kaskadą):
DELETE FROM Zakup_karnetu WHERE id_zakupu = ?;

COMMIT;

-- Q1. Lista członków z telefonami + status aktywnego karnetu (skorelowane subquery)

SELECT
  c.id_osoby, o.imie, o.nazwisko, o.email,
  COALESCE(GROUP_CONCAT(t.nr_tel, ', '), '') AS telefony,
  c.data_dolaczenia, c.status AS status_czlonka,
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


-- Q2. Wyszukiwarka członków (LIKE + opcjonalny filtr statusu)

SELECT
  c.id_osoby, o.imie, o.nazwisko, o.email,
  COALESCE(GROUP_CONCAT(t.nr_tel, ', '), '') AS telefony,
  c.data_dolaczenia, c.status
FROM Czlonek c
JOIN Osoba o ON o.id_osoby = c.id_osoby
LEFT JOIN Nr_telefonu t ON t.id_osoby = o.id_osoby
WHERE (o.nazwisko LIKE ? OR o.email LIKE ?)
  AND (? = '' OR c.status = ?)
GROUP BY c.id_osoby
ORDER BY o.nazwisko;

-- Q3. Członkowie bez zakupów od 90 dni (NOT EXISTS)

SELECT c.id_osoby, o.imie, o.nazwisko, c.status
FROM Czlonek c
JOIN Osoba o ON o.id_osoby = c.id_osoby
WHERE NOT EXISTS (
  SELECT 1
  FROM Zakup_karnetu zk
  WHERE zk.id_osoby = c.id_osoby
    AND date(zk.data_zakupu) >= date('now', '-90 day')
)
ORDER BY o.nazwisko, o.imie;

-- Q4. “VIP”: członkowie z ≥ X zakupami w roku (GROUP BY + HAVING)

SELECT
  o.id_osoby,
  o.nazwisko || ' ' || o.imie AS czlonek,
  COUNT(*) AS liczba_zakupow,
  ROUND(SUM(zk.cena_koncowa), 2) AS suma
FROM Zakup_karnetu zk
JOIN Osoba o ON o.id_osoby = zk.id_osoby
WHERE strftime('%Y', zk.data_zakupu) = ?
  AND zk.status IN ('active','paid','expired')
GROUP BY o.id_osoby
HAVING COUNT(*) >= ?
ORDER BY suma DESC, liczba_zakupow DESC;

-- Q5. Karnety wygasające w 14 dni (daty)

SELECT
  o.nazwisko, o.imie,
  zk.data_zakonczenia,
  pk.nazwa AS plan,
  zk.status
FROM Zakup_karnetu zk
JOIN Czlonek c ON c.id_osoby = zk.id_osoby
JOIN Osoba o ON o.id_osoby = c.id_osoby
JOIN Plan_karnetu pk ON pk.id_planu = zk.id_planu
WHERE zk.status IN ('active', 'paid')
  AND date(zk.data_zakonczenia) BETWEEN date('now') AND date('now', '+14 day')
ORDER BY zk.data_zakonczenia ASC, o.nazwisko ASC;

-- Q6. Raport przychodów: miesiąc + metoda (GROUP BY + HAVING)

SELECT
  strftime('%Y-%m', p.data_platnosci) AS miesiac,
  p.metoda,
  COUNT(*) AS liczba_platnosci,
  SUM(p.kwota) AS suma
FROM Platnosc p
WHERE strftime('%Y', p.data_platnosci) = ?
  AND p.status = 'paid'
GROUP BY miesiac, p.metoda
HAVING SUM(p.kwota) > ?
ORDER BY miesiac, p.metoda;

-- Q7. Najpopularniejsze plany w roku (GROUP BY + HAVING)

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

-- Q8. “Podejrzane płatności”: paid, ale kwota < minimalnej ceny planu (JOIN + warunek porównawczy)

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
WHERE p.status = 'paid'
  AND p.kwota < pk.cena_bazowa
ORDER BY p.data_platnosci DESC;

-- Q9. Ekwiwalent > ALL(...): zakupy droższe niż wszystkie ceny bazowe planów (czyli > MAX)

SELECT
  zk.id_zakupu, zk.cena_koncowa, pk.nazwa, o.nazwisko || ' ' || o.imie AS czlonek
FROM Zakup_karnetu zk
JOIN Plan_karnetu pk ON pk.id_planu = zk.id_planu
JOIN Osoba o ON o.id_osoby = zk.id_osoby
WHERE zk.cena_koncowa > (SELECT MAX(cena_bazowa) FROM Plan_karnetu)
ORDER BY zk.cena_koncowa DESC;

-- Q10. Lista sesji z liczbą zapisanych i wolnymi miejscami (LEFT JOIN + GROUP BY)

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
 AND z.status IN ('Potwierdzony')
GROUP BY sz.id_sesji
ORDER BY sz.czas_rozpoczecia DESC;

-- Q11. “Prawie pełne” (HAVING + obliczenie procentu)

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

-- Q12. Ranking typów zajęć wg frekwencji w ostatnich 30 dniach (CTE + GROUP BY + ORDER BY)

WITH zapisy30 AS (
  SELECT z.id_sesji
  FROM Zapis z
  WHERE date(z.data_zapisu) >= date('now', '-30 day')
    AND z.status IN ('Potwierdzony')
)
SELECT
  tz.nazwa,
  COUNT(*) AS liczba_zapisow
FROM zapisy30 x
JOIN Sesja_zajec sz ON sz.id_sesji = x.id_sesji
JOIN Typ_zajec tz ON tz.id_typu = sz.id_typu
GROUP BY tz.id_typu
ORDER BY liczba_zapisow DESC, tz.nazwa ASC;

-- Q13. “Popis” okienkowy: 5 najbliższych sesji i miejsce w kolejce po czasie (window function)

SELECT *
FROM (
  SELECT
    sz.id_sesji,
    tz.nazwa AS typ,
    sz.czas_rozpoczecia,
    sz.sala,
    ROW_NUMBER() OVER (ORDER BY sz.czas_rozpoczecia ASC) AS rn
  FROM Sesja_zajec sz
  JOIN Typ_zajec tz ON tz.id_typu = sz.id_typu
  WHERE datetime(sz.czas_rozpoczecia) >= datetime('now')
    AND sz.status IN ('Zaplanowana','Otwarta')
)
WHERE rn <= 5
ORDER BY czas_rozpoczecia ASC;

-- Q14. Sprzęt z otwartymi zgłoszeniami (HAVING)

SELECT
  s.id_sprzetu,
  s.nazwa,
  s.kategoria,
  s.status AS status_sprzetu,
  COUNT(zs.id_zgloszenia) AS otwartych_zgloszen
FROM Sprzet s
LEFT JOIN Zgloszenia_serwisowe zs
  ON zs.id_sprzetu = s.id_sprzetu
 AND zs.status IN ('W toku', 'W naprawie', 'Zgłoszone')
GROUP BY s.id_sprzetu
HAVING otwartych_zgloszen > 0
ORDER BY otwartych_zgloszen DESC, s.kategoria, s.nazwa;

-- Q15. Zgłoszenia w toku, ale tylko dla ról serwis/manager (IN + CASE sortowanie)

SELECT
  zs.id_zgloszenia,
  zs.data_zgloszenia,
  zs.priorytet,
  zs.status,
  s.nazwa AS sprzet,
  s.nr_seryjny,
FROM Zgloszenia_serwisowe zs
JOIN Sprzet s ON s.id_sprzetu = zs.id_sprzetu
LEFT JOIN Pracownik p ON p.id_osoby = zs.id_osoby
LEFT JOIN Osoba o ON o.id_osoby = p.id_osoby
WHERE zs.status IN ('Zgłoszony','W toku', 'W naprawie')
ORDER BY
  CASE zs.priorytet
    WHEN 'Wysoki' THEN 1
    WHEN 'Średni' THEN 2
    ELSE 3
  END,
  zs.data_zgloszenia DESC;

-- Q16. “Serwisowe KPI”: liczba zgłoszeń per pracownik w miesiącu (GROUP BY + HAVING)

SELECT
  p.id_osoby,
  o.nazwisko || ' ' || o.imie AS pracownik,
  COUNT(*) AS liczba_zgloszen
FROM Zgloszenia_serwisowe zs
JOIN Pracownik p ON p.id_osoby = zs.id_osoby
JOIN Osoba o ON o.id_osoby = p.id_osoby
WHERE strftime('%Y-%m', zs.data_zgloszenia) = ?
GROUP BY p.id_osoby
HAVING COUNT(*) >= ?
ORDER BY liczba_zgloszen DESC;