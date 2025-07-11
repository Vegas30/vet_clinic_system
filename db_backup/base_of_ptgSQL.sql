-- CREATE TABLE Филиалы (
--     id SERIAL PRIMARY KEY,
--     name TEXT NOT NULL,
--     address TEXT NOT NULL,
--     phone TEXT NOT NULL
-- );

-- CREATE TABLE Сотрудники (
--     id SERIAL PRIMARY KEY,
--     full_name TEXT NOT NULL,
--     login TEXT UNIQUE NOT NULL,
--     password_hash TEXT NOT NULL,
--     role TEXT NOT NULL,
--     branch_id INTEGER NOT NULL REFERENCES Филиалы(id) ON DELETE RESTRICT
-- );

-- CREATE TABLE Услуги (
--     id SERIAL PRIMARY KEY,
--     title TEXT NOT NULL,
--     description TEXT,
--     price NUMERIC(10, 2) NOT NULL CHECK (price >= 0)
-- );

-- CREATE TABLE Приёмы (
--     id SERIAL PRIMARY KEY,
--     animal_id TEXT NOT NULL,
--     vet_id INTEGER NOT NULL REFERENCES Сотрудники(id) ON DELETE RESTRICT,
--     date DATE NOT NULL,
--     time TIME NOT NULL,
--     service_id INTEGER NOT NULL REFERENCES Услуги(id) ON DELETE RESTRICT,
--     status TEXT NOT NULL CHECK (status IN ('запланирован', 'завершен', 'отменен')),
--     CONSTRAINT unique_appointment UNIQUE (vet_id, date, time)
-- );

-- CREATE TABLE Журнал_входа (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER NOT NULL REFERENCES Сотрудники(id) ON DELETE CASCADE,
--     datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     event_type TEXT NOT NULL CHECK (event_type IN ('вход', 'выход'))
-- );

-- - Филиалы
-- INSERT INTO Филиалы (name, address, phone) VALUES
-- ('Центральный', 'ул. Центральная, 1', '+79990001111'),
-- ('Северный', 'ул. Северная, 5', '+79990002222'),
-- ('Западный', 'ул. Западная, 10', '+79990003333'),
-- ('Восточный', 'ул. Восточная, 15', '+79990004444');

-- -- Сотрудники
-- INSERT INTO Сотрудники (full_name, login, password_hash, role, branch_id) VALUES
-- -- Администраторы
-- ('Иванов Сергей Петрович', 'admin1', 'a1', 'Администратор', 1),
-- ('Смирнова Анна Владимировна', 'admin2', 'a2', 'Администратор', 2),

--  -- Врачи
-- ('Петров Дмитрий Игоревич', 'vet1', 'v1', 'Врач', 1),
-- ('Козлова Елена Александровна', 'vet2', 'v2', 'Врач', 1),
-- ('Сидоров Алексей Николаевич', 'vet3', 'v3', 'Врач', 2),

-- -- Регистраторы
-- ('Федорова Мария Олеговна', 'reg1', 'r1', 'Регистратор', 1),
-- ('Николаев Иван Сергеевич', 'reg2', 'r2', 'Регистратор', 3),

-- -- Менеджеры
-- ('Волкова Ольга Дмитриевна', 'manager1', 'm1', 'Менеджер', 1),
-- ('Григорьев Павел Андреевич', 'manager2', 'm2', 'Менеджер', 4);

-- -- Услуги
-- INSERT INTO Услуги (title, description, price) VALUES
-- ('Консультация', 'Первичный осмотр животного', 1500.00),
-- ('Вакцинация', 'Комплексная прививка', 2500.00),
-- ('Чипирование', 'Установка идентификационного чипа', 3500.00),
-- ('Стерилизация', 'Хирургическая операция', 8000.00),
-- ('Анализы', 'Лабораторные исследования', 3000.00);

-- -- Приемы
-- INSERT INTO Приёмы (animal_id, vet_id, date, time, service_id, status) VALUES
-- ('Барсик (кот, 2 года)', 3, '2025-07-10', '10:00', 1, 'запланирован'),
-- ('Шарик (собака, лабрадор)', 3, '2025-07-10', '11:30', 2, 'завершен'),
-- ('Мурка (кот, 1 год)', 4, '2025-07-10', '09:00', 4, 'запланирован'),
-- ('Рекс (овчарка, 5 лет)', 5, '2025-07-11', '14:00', 3, 'запланирован'),
-- ('Зефир (кролик, 6 мес.)', 4, '2025-07-12', '12:00', 5, 'отменен');

-- --Журнал входа
-- INSERT INTO Журнал_входа (user_id, datetime, event_type) VALUES
-- (1, '2025-07-09 08:05:12', 'вход'),
-- (3, '2025-07-09 08:10:23', 'вход'),
-- (6, '2025-07-09 08:15:44', 'вход'),
-- (1, '2025-07-09 18:01:55', 'выход'),
-- (3, '2025-07-09 17:45:31', 'выход'),
-- (7, '2025-07-09 09:30:10', 'вход');


