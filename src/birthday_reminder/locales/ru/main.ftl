start =
    Привет, { $first_name }!

    Я могу помочь тебе не забывать дни рождения друзей.
    Прежде чем мы начнем, пожалуйста, выберите ваш язык:

stats =
    Статистика пользователей и напоминаний:

    Всего пользователей: { $total_users }
    Новые пользователи сегодня: { $new_users_today }
    Новые пользователи на этой неделе: { $new_users_week }
    Новые пользователи в этом месяце: { $new_users_month }

    Всего напоминаний: { $total_reminders }
    Новые напоминания сегодня: { $new_reminders_today }
    Новые напоминания на этой неделе: { $new_reminders_week }
    Новые напоминания в этом месяце: { $new_reminders_month }
    Среднее количество напоминаний на пользователя: { $avg_reminders_per_user }

create-remind-select-month =
    Давайте начнем создание напоминания о дне рождении друга.
    В каком месяце день рождения у твоего друга?

create-remind-select-day =
    В какой день у твоего друга день рождения?

create-remind-select-user =
    Введи имя своего друга:

create-remind-select-user-empty =
    Имя друга не может быть пустым

create-remind-select-user-too-long =
    Имя друга слишком длинное. Оно должно быть короче 100 символов.

create-remind-confirm =
    Ты хочешь создать напоминание о дне рождении { $name }?

create-remind-success =
    Поздравляю! Ты создал напоминание о дне рождении друга.
    Если ты хочешь создать еще одно напоминание или управлять существующими, используй кнопки ниже:

create-remind-button =
    Создать напоминание

create-remind-select-month-button =
    << Выбрать месяц

create-remind-select-day-button =
    << Выбрать день

create-remind-input-user-button =
    << Ввести имя друга

delete-remind-select-remind =
    Какое напоминание ты хочешь удалить?

delete-remind-confirm =
    Ты уверен, что хочешь удалить напоминание?

delete-remind-success =
    Напоминание удалено.
    Если ты хочешь создать новое напоминание или управлять существующими, используй кнопки ниже:

delete-remind-select-remind-button =
    << Вернуться

reminders-empty =
    У тебя пока нет напоминаний 🐨

main-menu =
    Что ты хочешь сделать?

main-menu-create-reminder = Создать напоминание

main-menu-delete-reminder = Удалить напоминание

main-menu-show-reminders = Показать напоминания

show-reminders =
    Твои напоминания:

    { $reminders }

show-reminders-text =
    { $name }, { $date } (через { $days } д.)

show-reminders-text-not-leap-year =
    { $name }, ~{ $date } (через ~{ $days } д., не високосный год)

main-menu-show-capybara = Показать капибару

show-capybara =
    Капибара следит за тобой

show-capybara-back =
    О нет, я боюсь!

back-to-main-menu-button =
    << Назад в главное меню

confirm-button =
    Подтвердить >>

birthday-coming-soon =
    Скоро день рождения { $name }!

birthday-today =
    Сегодня день рождения { $name }! 🎉

dialog-error =
    Что-то пошло не так. Пожалуйста, используйте новый диалог.

January = Январь
February = Февраль
March = Март
April = Апрель
May = Май
June = Июнь
July = Июль
August = Август
September = Сентябрь
October = Октябрь
November = Ноябрь
December = Декабрь
