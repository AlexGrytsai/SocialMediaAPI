import json
import random


def generate_users_for_db() -> list:
    users_list = []

    pks = [pk for pk in range(50, 1001)]
    country_pks = [pk for pk in range(1, 196)]
    user_first_name_list = [
        "John", "James", "Robert", "Michael", "William", "David", "Richard",
        "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
        "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth",
        "Joshua", "George", "Kevin", "Brian", "Edward", "Ronald", "Timothy",
        "Jason", "Jeffrey", "Ryan", "Gary", "Nicholas", "Eric", "Stephen",
        "Jonathan", "Larry", "Justin", "Scott", "Brandon", "Raymond",
        "Jeffery", "Frank", "Gregory", "Samuel", "Patrick", "Alexander",
        "Dennis", "Walter", "Peter", "Harold", "Douglas", "Henry", "Carl",
        "Arthur", "Roger", "Joe", "Juan", "Jack", "Albert", "Jonathan",
    ]
    user_last_name_list = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
        "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White",
        "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
        "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen",
        "Young", "Green", "Adams", "Baker", "Hill", "Moore", "Thompson",
        "Walker", "White", "Harris", "Martin", "Thompson", "Garcia",
        "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
        "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall",
    ]

    years_list = [year for year in range(1960, 2009)]
    months_list = [month for month in range(1, 13)]
    days_list = [day for day in range(1, 29)]

    def generate_people_list() -> list:
        people_list = []
        for i in range(random.randint(0, 100)):
            people = random.choice(pks)
            if people != pk and people not in people_list:
                people_list.append(people)
        return people_list

    for pk in pks:
        followers = generate_people_list()
        subscriptions = generate_people_list()
        first_name = random.choice(user_first_name_list)
        last_name = random.choice(user_last_name_list)
        email = f"{last_name.lower()}{pk}@example.com"
        birth_date = (f"{random.choice(years_list)}-"
                      f"{random.choice(months_list)}-"
                      f"{random.choice(days_list)}")
        user = {
            "model": "users.user",
            "pk": pk,
            "fields": {
                "username": f"{last_name.lower()}{pk}",
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "residence_place": random.choice(country_pks),
                "birth_date": birth_date,
                "followers": followers,
                "my_subscriptions": subscriptions
            }
        }
        users_list.append(user)
    return users_list


def save_users_data_to_json(users: list) -> None:
    with open("users_data_for_db.json", "w") as file:
        json.dump(users, file, indent=4)


if __name__ == "__main__":
    users_data = generate_users_for_db()
    save_users_data_to_json(users_data)
