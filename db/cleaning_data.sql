-- Wyłączenie sprawdzania kluczy obcych, aby usunąć dane w dowolnej kolejności
PRAGMA foreign_keys = OFF;

-- Usuwanie danych z tabel zależnych (operacyjnych)
DELETE FROM Zapis;
DELETE FROM Platnosc;
DELETE FROM Zgloszenia_serwisowe;

-- Usuwanie danych z tabel pośrednich
DELETE FROM Zakup_karnetu;
DELETE FROM Sesja_zajec;
DELETE FROM Nr_telefonu;

-- Usuwanie danych z tabel specjalizacji (podtypy Osoby)
DELETE FROM Trener;
DELETE FROM Pracownik;
DELETE FROM Czlonek;

-- Usuwanie danych z tabel głównych (słowników i encji nadrzędnych)
DELETE FROM Osoba;
DELETE FROM Sprzet;
DELETE FROM Typ_zajec;
DELETE FROM Plan_karnetu;

COMMIT;

-- Ponowne włączenie sprawdzania kluczy obcych
PRAGMA foreign_keys = ON;

-- Opcjonalnie: Odzyskanie miejsca na dysku po usuniętych rekordach
VACUUM;