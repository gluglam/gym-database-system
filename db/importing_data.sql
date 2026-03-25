BEGIN TRANSACTION;

-- =============================================
-- 1. SŁOWNIKI I KATALOGI
-- =============================================

-- Tabela: Plan_karnetu (Bez zmian w datach, bo ich tu nie ma)
INSERT INTO Plan_karnetu (id_planu, nazwa, dlugosc_dni, cena_bazowa) VALUES
(1, 'Open Miesięczny', 30, 139.00),
(2, 'Open Student', 30, 99.00),
(3, 'Open Senior', 30, 89.00),
(4, 'Poranny Ptaszek (do 14:00)', 30, 79.00),
(5, 'Weekendowy', 30, 69.00),
(6, '3 Miesiące Standard', 90, 350.00),
(7, '6 Miesięcy Standard', 180, 650.00),
(8, 'Roczny VIP', 365, 1200.00),
(9, 'Karnet 10 wejść', 60, 250.00),
(10, 'Jednorazowe wejście', 1, 35.00),
(11, 'Karnet Korporacyjny', 30, 110.00),
(12, 'Trening Personalny Pakiet 5', 45, 600.00),
(13, 'Trening Personalny Pakiet 10', 90, 1100.00),
(14, 'Karnet "Dla Pary"', 30, 240.00),
(15, 'Karnet Online (App)', 30, 49.00);

-- Tabela: Typ_zajec
INSERT INTO Typ_zajec (id_typu, nazwa, poziom_trudnosci, czas_trwania, opis) VALUES
(1, 'Hatha Yoga', 'Początkujący', 60, 'Klasyczna joga dla równowagi.'),
(2, 'Power Yoga', 'Zaawansowany', 60, 'Dynamiczna odmiana jogi.'),
(3, 'Pilates', 'Średni', 55, 'Wzmacnianie mięśni głębokich.'),
(4, 'Zdrowy Kręgosłup', 'Początkujący', 45, 'Ćwiczenia rehabilitacyjne.'),
(5, 'Zumba', 'Średni', 60, 'Taniec latynoamerykański cardio.'),
(6, 'Body Pump', 'Średni', 60, 'Trening ze sztangami.'),
(7, 'CrossFit WOD', 'Ekspert', 45, 'Trening dnia o wysokiej intensywności.'),
(8, 'Tabata', 'Zaawansowany', 30, 'Interwały o wysokiej intensywności.'),
(9, 'Boks - Technika', 'Średni', 90, 'Nauka ciosów i uników.'),
(10, 'Kickboxing', 'Zaawansowany', 90, 'Boks z elementami kopnięć.'),
(11, 'Spinning / Rowerki', 'Średni', 50, 'Jazda na rowerach stacjonarnych.'),
(12, 'Stretching', 'Początkujący', 30, 'Rozciąganie po treningu.'),
(13, 'TRX', 'Średni', 45, 'Ćwiczenia z taśmami podwieszanymi.'),
(14, 'Kalistenika', 'Zaawansowany', 60, 'Trening z masą własnego ciała.'),
(15, 'Aqua Aerobik', 'Początkujący', 45, 'Ćwiczenia w basenie.');

-- Tabela: Sprzet (Daty zakupu +2 lata: 2022->2024, 2023->2025)
INSERT INTO Sprzet (id_sprzetu, nazwa, kategoria, nr_seryjny, data_zakupu, status) VALUES
(1, 'Bieżnia Matrix T5', 'Cardio', 'CARD-001', '2024-01-10', 'Sprawny'),
(2, 'Bieżnia Matrix T5', 'Cardio', 'CARD-002', '2024-01-10', 'W naprawie'),
(3, 'Bieżnia Matrix T5', 'Cardio', 'CARD-003', '2024-01-10', 'Sprawny'),
(4, 'Orbitrek LifeFitness', 'Cardio', 'CARD-004', '2024-02-15', 'Sprawny'),
(5, 'Wioślarz Concept2', 'Cardio', 'CARD-005', '2024-03-01', 'Do serwisu'),
(6, 'Rower stacjonarny', 'Cardio', 'CARD-006', '2024-03-01', 'Sprawny'),
(7, 'Brama wielofunkcyjna', 'Siłowy', 'STR-001', '2023-11-20', 'Sprawny'),
(8, 'Suwnica Smitha', 'Siłowy', 'STR-002', '2023-11-20', 'Sprawny'),
(9, 'Ławka regulowana', 'Wolne ciężary', 'FREE-001', '2025-01-05', 'Sprawny'),
(10, 'Ławka regulowana', 'Wolne ciężary', 'FREE-002', '2025-01-05', 'Tapicerka uszkodzona'),
(11, 'Zestaw hantli 2-50kg', 'Wolne ciężary', 'FREE-003', '2025-01-05', 'Sprawny'),
(12, 'Sztanga olimpijska 20kg', 'Wolne ciężary', 'FREE-004', '2025-02-10', 'Sprawny'),
(13, 'Sztanga olimpijska 20kg', 'Wolne ciężary', 'FREE-005', '2025-02-10', 'Wygięta'),
(14, 'Maszyna do nóg (Leg Press)', 'Siłowy', 'STR-003', '2023-12-12', 'Sprawny'),
(15, 'Wyciąg górny', 'Siłowy', 'STR-004', '2023-12-12', 'Sprawny'),
(16, 'Mata do jogi Premium', 'Akcesoria', 'ACC-001', '2025-05-01', 'Sprawny');

-- =============================================
-- 2. OSOBY I TELEFONY
-- =============================================

-- Tabela: Osoba (Daty urodzenia i stworzenia +2 lata)
INSERT INTO Osoba (id_osoby, imie, nazwisko, email, data_urodzenia, stworzone_dnia) VALUES
-- Pracownicy (Zarząd i Recepcja)
(1, 'Adam', 'Szefowski', 'adam.boss@gym.pl', '1977-05-12', '2022-01-01'),
(2, 'Beata', 'Kierowniczka', 'beata.k@gym.pl', '1982-08-20', '2022-01-02'),
(3, 'Celina', 'Recepcja', 'celina.r@gym.pl', '1997-02-14', '2023-03-10'),
(4, 'Dariusz', 'Serwisant', 'darek.s@gym.pl', '1984-11-30', '2022-06-01'),
(5, 'Eliza', 'Sprzedaz', 'eliza.s@gym.pl', '1992-07-07', '2023-09-01'),
-- Pracownicy (Trenerzy)
(6, 'Filip', 'Mocny', 'filip.m@gym.pl', '1990-01-10', '2023-01-15'),
(7, 'Grażyna', 'Fit', 'grazyna.f@gym.pl', '1994-04-22', '2023-02-01'),
(8, 'Hubert', 'Sztanga', 'hubert.sz@gym.pl', '1987-12-12', '2022-05-05'),
(9, 'Iga', 'Joga', 'iga.j@gym.pl', '1992-03-30', '2024-01-10'),
(10, 'Janusz', 'Boks', 'janusz.b@gym.pl', '1980-09-09', '2023-11-11'),
(11, 'Karolina', 'Zumba', 'karo.z@gym.pl', '1998-06-06', '2024-03-03'),
(12, 'Leon', 'Cross', 'leon.c@gym.pl', '1993-08-18', '2023-07-20'),
(13, 'Monika', 'Pilates', 'monika.p@gym.pl', '1985-05-25', '2022-10-10'),
(14, 'Norbert', 'Kalistenik', 'norbert.k@gym.pl', '1996-02-28', '2024-05-15'),
(15, 'Oliwia', 'Rowerowa', 'oliwia.r@gym.pl', '1995-11-15', '2024-06-01'),
(16, 'Paweł', 'Trener', 'pawel.t@gym.pl', '1991-10-01', '2024-08-01'),
(17, 'Robert', 'Trener', 'robert.t@gym.pl', '1992-12-12', '2024-09-01'),
(18, 'Sylwia', 'Trener', 'sylwia.t@gym.pl', '1997-01-05', '2025-01-01'),
(19, 'Tomasz', 'Trener', 'tomasz.t@gym.pl', '1989-07-07', '2025-02-01'),
(20, 'Urszula', 'Trener', 'ula.t@gym.pl', '1993-03-03', '2025-03-01'),
-- Członkowie (Klienci)
(21, 'Wojciech', 'Kowalski', 'wojtek.k@gmail.com', '1992-01-01', '2025-01-02'),
(22, 'Zofia', 'Nowak', 'zosia.n@onet.pl', '2002-05-05', '2025-01-05'),
(23, 'Andrzej', 'Wiśniewski', 'andrzej.w@wp.pl', '1987-08-08', '2025-01-10'),
(24, 'Barbara', 'Wójcik', 'basia.w@gmail.com', '1972-12-12', '2025-02-01'),
(25, 'Cezary', 'Kowalczyk', 'czarek.k@o2.pl', '1997-03-03', '2025-02-15'),
(26, 'Dominika', 'Kamińska', 'domi.k@edu.pl', '2004-07-20', '2025-03-01'),
(27, 'Edward', 'Lewandowski', 'ed.lew@gmail.com', '1967-09-30', '2025-03-10'),
(28, 'Felicja', 'Zielińska', 'fela.z@wp.pl', '1993-11-11', '2025-04-01'),
(29, 'Grzegorz', 'Szymański', 'grzes.sz@onet.pl', '1990-02-02', '2025-04-05'),
(30, 'Hanna', 'Woźniak', 'hania.w@gmail.com', '2001-06-15', '2025-05-01'),
(31, 'Ireneusz', 'Dąbrowski', 'irek.d@firmowa.pl', '1981-04-10', '2025-05-20'),
(32, 'Joanna', 'Kozłowska', 'asia.k@gmail.com', '1995-08-25', '2025-06-01'),
(33, 'Krzysztof', 'Jankowski', 'kris.j@wp.pl', '1983-10-31', '2025-06-15'),
(34, 'Lidia', 'Mazur', 'lidka.m@o2.pl', '1998-01-20', '2025-07-01'),
(35, 'Michał', 'Kwiatkowski', 'michal.k@gmail.com', '1992-05-05', '2025-07-10'),
(36, 'Natalia', 'Krawczyk', 'nati.k@edu.pl', '2003-09-01', '2025-08-01'),
(37, 'Olgierd', 'Piotrowski', 'olgierd.p@gmail.com', '1986-11-15', '2025-08-20'),
(38, 'Patrycja', 'Grabowska', 'pati.g@wp.pl', '2000-03-08', '2025-09-01'),
(39, 'Rafał', 'Pawłowski', 'rafal.p@onet.pl', '1989-07-22', '2025-09-15'),
(40, 'Sandra', 'Michalska', 'sandra.m@gmail.com', '1994-12-24', '2025-10-01');

-- Tabela: Nr_telefonu
INSERT INTO Nr_telefonu (nr_tel, id_osoby) VALUES
-- Pracownicy i Recepcja
('500-111-111', 1), ('500-222-222', 2), ('500-333-333', 3), ('500-444-444', 4), ('500-555-555', 5),

-- Trenerzy
('600-101-101', 6), ('600-102-102', 7), ('600-103-103', 8), ('600-104-104', 9), ('600-105-105', 10),
('600-106-106', 11), ('600-107-107', 12), ('600-108-108', 13), ('600-109-109', 14), ('600-110-110', 15),
('600-111-111', 16), ('600-112-112', 17), ('600-113-113', 18), ('600-114-114', 19), ('600-115-115', 20),

-- Członkowie (Klienci)
('700-201-201', 21), ('700-202-202', 22), ('700-203-203', 23), ('700-204-204', 24), ('700-205-205', 25),
('700-206-206', 26), ('700-207-207', 27), ('700-208-208', 28), ('700-209-209', 29), ('700-210-210', 30),
('700-211-211', 31), ('700-212-212', 32), ('700-213-213', 33), ('700-214-214', 34), ('700-215-215', 35),
('700-216-216', 36), ('700-217-217', 37), ('700-218-218', 38), ('700-219-219', 39), ('700-220-220', 40);

-- =============================================
-- 3. PRACOWNICY I TRENERZY
-- =============================================

-- Tabela: Pracownik (Daty zatrudnienia +2 lata)
INSERT INTO Pracownik (id_osoby, data_zatrudnienia, rola, wynagrodzenie, nadzoruje) VALUES
(1, '2022-01-01', 'Właściciel', 15000.00, NULL),
(2, '2022-01-02', 'Manager Klubu', 9000.00, 1),
(3, '2023-03-10', 'Recepcjonista', 4200.00, 2),
(4, '2022-06-01', 'Konserwator', 4500.00, 2),
(5, '2023-09-01', 'Specjalista ds. Sprzedaży', 4800.00, 2),
(6, '2023-01-15', 'Trener Personalny', 5000.00, 2),
(7, '2023-02-01', 'Instruktor Fitness', 4600.00, 2),
(8, '2022-05-05', 'Trener Siłowy', 5200.00, 2),
(9, '2024-01-10', 'Instruktor Jogi', 4800.00, 2),
(10, '2023-11-11', 'Trener Sztuk Walki', 5000.00, 2),
(11, '2024-03-03', 'Instruktor Tańca', 4500.00, 2),
(12, '2023-07-20', 'Trener CrossFit', 5500.00, 2),
(13, '2022-10-10', 'Instruktor Pilates', 4700.00, 2),
(14, '2024-05-15', 'Trener Kalisteniki', 4600.00, 2),
(15, '2024-06-01', 'Instruktor Spinning', 4400.00, 2),
(16, '2024-08-01', 'Trener Dyżurny', 4100.00, 2),
(17, '2024-09-01', 'Trener Dyżurny', 4100.00, 2),
(18, '2025-01-01', 'Trener Personalny', 4900.00, 2),
(19, '2025-02-01', 'Trener Personalny', 4900.00, 2),
(20, '2025-03-01', 'Trener Personalny', 4900.00, 2);

-- Tabela: Trener
INSERT INTO Trener (id_osoby, specjalizacja, poziom) VALUES
(6, 'Budowanie masy', 'Ekspert'),
(7, 'Spalanie tłuszczu', 'Zaawansowany'),
(8, 'Trójbój siłowy', 'Ekspert'),
(9, 'Vinyasa Yoga', 'Zaawansowany'),
(10, 'Boks i Kickboxing', 'Mistrzowski'),
(11, 'Zumba i Salsation', 'Zaawansowany'),
(12, 'Przygotowanie motoryczne', 'Ekspert'),
(13, 'Rehabilitacja', 'Zaawansowany'),
(14, 'Street Workout', 'Średniozaawansowany'),
(15, 'Wytrzymałość', 'Średniozaawansowany'),
(16, 'Ogólnorozwojowy', 'Początkujący'),
(17, 'Ogólnorozwojowy', 'Początkujący'),
(18, 'Dietetyka', 'Zaawansowany'),
(19, 'Kettlebells', 'Średniozaawansowany'),
(20, 'CrossFit', 'Początkujący');

-- =============================================
-- 4. CZŁONKOWIE I ZAKUPY
-- =============================================

-- Tabela: Czlonek (Daty dołączenia +2 lata)
INSERT INTO Czlonek (id_osoby, data_dolaczenia, status) VALUES
(21, '2025-01-02', 'Aktywny'), (22, '2025-01-05', 'Aktywny'),
(23, '2025-01-10', 'Aktywny'), (24, '2025-02-01', 'Zawieszony'),
(25, '2025-02-15', 'Aktywny'), (26, '2025-03-01', 'Aktywny'),
(27, '2025-03-10', 'Aktywny'), (28, '2025-04-01', 'Nieaktywny'),
(29, '2025-04-05', 'Aktywny'), (30, '2025-05-01', 'Aktywny'),
(31, '2025-05-20', 'Aktywny'), (32, '2025-06-01', 'Aktywny'),
(33, '2025-06-15', 'Windykacja'), (34, '2025-07-01', 'Aktywny'),
(35, '2025-07-10', 'Aktywny'), (36, '2025-08-01', 'Aktywny'),
(37, '2025-08-20', 'Aktywny'), (38, '2025-09-01', 'Aktywny'),
(39, '2025-09-15', 'Aktywny'), (40, '2025-10-01', 'Aktywny');

-- Tabela: Zakup_karnetu (Wszystkie daty +2 lata)
INSERT INTO Zakup_karnetu (id_zakupu, data_zakupu, data_rozpoczecia, data_zakonczenia, cena_koncowa, status, id_planu, id_osoby) VALUES
(1, '2025-01-02', '2025-01-02', '2025-02-01', 139.00, 'Zakończony', 1, 21),
(2, '2025-02-01', '2025-02-01', '2025-03-01', 139.00, 'Zakończony', 1, 21),
(3, '2025-03-01', '2025-03-01', '2025-04-01', 139.00, 'Zakończony', 1, 21),
(4, '2025-01-05', '2025-01-05', '2025-02-04', 99.00, 'Zakończony', 2, 22),
(5, '2025-02-05', '2025-02-05', '2025-03-07', 99.00, 'Zakończony', 2, 22),
(6, '2025-01-10', '2025-01-10', '2026-01-10', 1100.00, 'Aktywny', 8, 23),
(7, '2025-02-15', '2025-02-15', '2025-05-15', 350.00, 'Zakończony', 6, 25),
(8, '2025-03-01', '2025-03-01', '2025-04-01', 99.00, 'Aktywny', 2, 26),
(9, '2025-03-10', '2025-03-10', '2025-04-09', 89.00, 'Aktywny', 3, 27),
(10, '2025-05-01', '2025-05-01', '2025-05-31', 69.00, 'Aktywny', 5, 30),
(11, '2025-05-20', '2025-05-20', '2025-06-19', 110.00, 'Aktywny', 11, 31),
(12, '2025-06-01', '2025-06-01', '2025-07-01', 139.00, 'Aktywny', 1, 32),
(13, '2025-06-15', '2025-06-15', '2025-07-15', 139.00, 'Wygasły', 1, 33),
(14, '2025-07-01', '2025-07-01', '2025-07-02', 35.00, 'Zakończony', 10, 34),
(15, '2025-07-10', '2025-07-10', '2026-07-10', 1200.00, 'Aktywny', 8, 35),
(16, '2025-09-01', '2025-09-01', '2025-10-01', 240.00, 'Aktywny', 14, 38);

-- Tabela: Platnosc (Daty płatności +2 lata)
INSERT INTO Platnosc (id_platnosci, kwota, metoda, data_platnosci, status, id_zakupu) VALUES
(1, 139.00, 'Karta', '2025-01-02', 'Zaksięgowana', 1),
(2, 139.00, 'Karta', '2025-02-01', 'Zaksięgowana', 2),
(3, 139.00, 'Karta', '2025-03-01', 'Zaksięgowana', 3),
(4, 99.00, 'BLIK', '2025-01-05', 'Zaksięgowana', 4),
(5, 99.00, 'BLIK', '2025-02-05', 'Zaksięgowana', 5),
(6, 1100.00, 'Przelew', '2025-01-10', 'Zaksięgowana', 6),
(7, 350.00, 'Gotówka', '2025-02-15', 'Zaksięgowana', 7),
(8, 99.00, 'Karta', '2025-03-01', 'Zaksięgowana', 8),
(9, 89.00, 'Gotówka', '2025-03-10', 'Zaksięgowana', 9),
(10, 69.00, 'Karta', '2025-05-01', 'Zaksięgowana', 10),
(11, 110.00, 'Przelew', '2025-05-20', 'Zaksięgowana', 11),
(12, 139.00, 'Karta', '2025-06-01', 'Zaksięgowana', 12),
(13, 0.00, 'Brak', '2025-06-15', 'Odrzucona', 13),
(14, 35.00, 'Gotówka', '2025-07-01', 'Zaksięgowana', 14),
(15, 1200.00, 'Przelew', '2025-07-10', 'Zaksięgowana', 15),
(16, 240.00, 'Karta', '2025-09-01', 'Zaksięgowana', 16);

-- =============================================
-- 5. HARMONOGRAM (Sesje i Zapisy - PAŹDZIERNIK 2025)
-- =============================================

-- Tabela: Sesja_zajec (2023 -> 2025)
INSERT INTO Sesja_zajec (id_sesji, czas_rozpoczecia, sala, liczebnosc, status, id_typu, id_osoby) VALUES
(1, '2025-10-20 08:00', 'Sala Jogi', 15, 'Zaplanowana', 1, 9),
(2, '2025-10-20 17:00', 'Sala Fitness', 20, 'Zaplanowana', 5, 11),
(3, '2025-10-20 18:00', 'Sala Siłowa', 10, 'Zaplanowana', 7, 12),
(4, '2025-10-20 19:00', 'Ring', 8, 'Zaplanowana', 9, 10),
(5, '2025-10-21 09:00', 'Sala Jogi', 12, 'Otwarta', 3, 13),
(6, '2025-10-21 10:00', 'Sala Rowerowa', 20, 'Otwarta', 11, 15),
(7, '2025-10-21 16:00', 'Plener', 15, 'Otwarta', 14, 14),
(8, '2025-10-21 18:00', 'Sala Fitness', 25, 'Pełna', 6, 7),
(9, '2025-10-22 10:00', 'Sala Jogi', 15, 'Zaplanowana', 4, 13),
(10, '2025-10-22 11:00', 'Basen', 15, 'Zaplanowana', 15, 7),
(11, '2025-10-23 07:00', 'Sala Fitness', 10, 'Zaplanowana', 8, 12),
(12, '2025-10-23 18:00', 'Strefa TRX', 8, 'Zaplanowana', 13, 16),
(13, '2025-10-24 17:00', 'Ring', 8, 'Zaplanowana', 10, 10),
(14, '2025-10-24 19:00', 'Sala Jogi', 15, 'Zaplanowana', 2, 9),
(15, '2025-10-25 18:00', 'Sala Fitness', 10, 'Odwołana', 12, 17);

-- Tabela: Zapis (2023 -> 2025)
INSERT INTO Zapis (data_zapisu, status, godzina_wejscia, id_osoby, id_sesji) VALUES
('2025-10-18', 'Potwierdzony', '07:50', 22, 1),
('2025-10-18', 'Potwierdzony', '07:55', 26, 1),
('2025-10-19', 'Potwierdzony', '-', 30, 2),
('2025-10-19', 'Potwierdzony', '-', 32, 2),
('2025-10-19', 'Rezerwowy', '-', 21, 2),
('2025-10-20', 'Potwierdzony', '17:50', 25, 3),
('2025-10-20', 'Potwierdzony', '17:55', 23, 3),
('2025-10-20', 'Potwierdzony', '-', 35, 4),
('2025-10-20', 'Anulowany', '-', 38, 4),
('2025-10-21', 'Potwierdzony', '08:55', 27, 5),
('2025-10-21', 'Potwierdzony', '-', 22, 6),
('2025-10-21', 'Potwierdzony', '-', 24, 6),
('2025-10-21', 'Potwierdzony', '-', 29, 7),
('2025-10-21', 'Potwierdzony', '-', 31, 8),
('2025-10-22', 'Potwierdzony', '-', 40, 9),
('2025-10-22', 'Potwierdzony', '-', 36, 10);

-- =============================================
-- 6. ZGŁOSZENIA SERWISOWE
-- =============================================

-- Tabela: Zgloszenia_serwisowe (Wszystkie zgłoszenia +2 lata)
INSERT INTO Zgloszenia_serwisowe (id_zgloszenia, opis_problemu, priorytet, data_zgloszenia, status, id_sprzetu, id_osoby) VALUES
(1, 'Pas bieżni się zacina', 'Wysoki', '2025-01-20', 'Naprawione', 2, 4),
(2, 'Skrzypienie przy wiosłowaniu', 'Średni', '2025-03-05', 'W toku', 5, 4),
(3, 'Pęknięta tapicerka', 'Niski', '2025-04-10', 'Zgłoszone', 10, 3),
(4, 'Wygięta sztanga po upadku', 'Wysoki', '2025-05-15', 'Do wymiany', 13, 2),
(5, 'Brak zawleczki w atlasie', 'Wysoki', '2025-06-01', 'Naprawione', 7, 4),
(6, 'Monitor nie działa', 'Średni', '2025-06-10', 'Naprawione', 1, 4),
(7, 'Luźne śruby w ławce', 'Wysoki', '2025-07-01', 'Naprawione', 9, 4),
(8, 'Wymiana linki wyciągu', 'Średni', '2025-07-20', 'W toku', 15, 4),
(9, 'Suwnica ciężko chodzi', 'Średni', '2025-08-05', 'Zgłoszone', 8, 3),
(10, 'Mata do jogi porwana', 'Niski', '2025-09-01', 'Do wymiany', 16, 3),
(11, 'Orbitrek hałasuje', 'Średni', '2025-09-10', 'Naprawione', 4, 4),
(12, 'Hantel 10kg uszkodzony gwint', 'Niski', '2025-09-15', 'Zgłoszone', 11, 2),
(13, 'Bieżnia błąd E1', 'Wysoki', '2025-10-01', 'Zgłoszone', 3, 3),
(14, 'Zabrudzona tapicerka', 'Niski', '2025-10-05', 'Wyczyszczone', 14, 4),
(15, 'Rower - urwany pedał', 'Wysoki', '2025-10-10', 'W naprawie', 6, 4);

COMMIT;