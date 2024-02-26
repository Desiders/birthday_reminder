start =
    Hello, { $first_name }!

    I can help you remember your friends' birthdays.
    Before we start, please select your language:

stats =
    Stats of users and reminders:

    Total users: { $total_users }
    New users today: { $new_users_today }
    New users this week: { $new_users_week }
    New users this month: { $new_users_month }

    Total birthday reminders: { $total_reminders }
    New reminders today: { $new_reminders_today }
    New reminders this week: { $new_reminders_week }
    New reminders this month: { $new_reminders_month }
    Average reminders per user: { $avg_reminders_per_user }

create-remind-select-month =
    Let's start creating a birthday reminder for your friend.
    What month is your friend's birthday?

create-remind-select-day =
    What day is your friend's birthday?

create-remind-select-user =
    Input your friend's name:

create-remind-select-user-empty =
    A friend's name cannot be empty

create-remind-select-user-too-long =
    A friend's name is too long. It should be shorter than 100 characters.

create-remind-confirm =
    You are about to create a reminder for { $name }'s birthday?

create-remind-success =
    Congratulations! You have created a reminder of a friend's birthday.
    If you want to create another reminder or manage existing ones, use buttons below:

create-remind-button =
    Create reminder

create-remind-select-month-button =
    << Select month

create-remind-select-day-button =
    << Select day

create-remind-input-user-button =
    << Input user's name

delete-remind-select-remind =
    Which reminder would you like to delete?

delete-remind-confirm =
    You are about to delete the reminder?

delete-remind-success =
    The reminder has been deleted.
    If you want to create reminder or manage existing ones, use buttons below:

delete-remind-select-remind-button =
    << Go back

reminders-empty =
    You don't have any reminders yet 🐨

main-menu =
    What would you like to do?

main-menu-create-reminder = Create reminder

main-menu-delete-reminder = Delete reminder

main-menu-show-reminders = Show reminders

show-reminders =
    Here are your reminders:

    { $reminders }

show-reminders-text =
    { $name }, { $date } (in { $days } days)

show-reminders-text-not-leap-year =
    { $name }, ~{ $date } (in ~{ $days } days, not leap year)

main-menu-show-capybara = Show capybara

show-capybara =
    Capybara see you

show-capybara-back =
    Oh no, I'm scared!

back-to-main-menu-button =
    << Back to main menu

confirm-button =
    Confirm >>

January = January
February = February
March = March
April = April
May = May
June = June
July = July
August = August
September = September
October = October
November = November
December = December
