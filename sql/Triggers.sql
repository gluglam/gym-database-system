-- 1 Walidacja: data_rozpoczecia musi być <= data_zakonczenia (jeśli ktoś poda ręcznie)
CREATE TRIGGER IF NOT EXISTS trg_zakup_dates_validate_ins
BEFORE INSERT ON Zakup_karnetu
FOR EACH ROW
WHEN NEW.data_rozpoczecia IS NOT NULL
 AND NEW.data_zakonczenia IS NOT NULL
 AND date(NEW.data_zakonczenia) < date(NEW.data_rozpoczecia)
BEGIN
  SELECT RAISE(ABORT, 'Zakup_karnetu: data_zakonczenia nie może być wcześniejsza niż data_rozpoczecia');
END;

-- 2 Limit miejsc na sesję zajęć – blokada zapisu po przekroczeniu liczebności
CREATE TRIGGER IF NOT EXISTS trg_zapis_limit_miejsc
BEFORE INSERT ON Zapis
FOR EACH ROW
WHEN (
  (SELECT COUNT(*)
   FROM Zapis z
   WHERE z.id_sesji = NEW.id_sesji
     AND z.status IN ('Potwierdzony')
  ) >=
  (SELECT s.liczebnosc
   FROM Sesja_zajec s
   WHERE s.id_sesji = NEW.id_sesji
  )
BEGIN
  SELECT RAISE(ABORT, 'Brak wolnych miejsc na tę sesję zajęć');
END;
