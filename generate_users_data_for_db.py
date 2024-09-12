import json
import random

import requests

# List of popular hashtags
POPULAR_HASHTAGS = [
    "love",
    "instagood",
    "photooftheday",
    "fashion",
    "beautiful",
    "happy",
    "cute",
    "tbt",
    "like4like",
    "followme",
    "picoftheday",
    "follow",
    "me",
    "selfie",
    "summer",
    "art",
    "instadaily",
    "friends",
    "repost",
    "nature",
    "smile",
    "style",
    "food",
    "family",
    "travel",
    "fitness",
    "igers",
    "fun",
    "tagsforlikes",
    "instalike",
    "likeforlike",
    "ootd",
    "beauty",
    "amazing",
    "instamood",
    "instagram",
    "photography",
    "vscocam",
    "sun",
    "photo",
    "music",
    "party",
    "girls",
    "cool",
    "bestoftheday",
    "swag",
    "fitnessmotivation",
    "motivation",
    "healthy",
    "gym",
]


def generate_users_for_db() -> list:
    """Generate user data for database"""
    users_list = []
    # Lists of user data
    pks = [pk for pk in range(50, 1001)]
    country_pks = [pk for pk in range(1, 196)]
    user_first_name_list = [
        "John",
        "James",
        "Robert",
        "Michael",
        "William",
        "David",
        "Richard",
        "Joseph",
        "Thomas",
        "Charles",
        "Christopher",
        "Daniel",
        "Matthew",
        "Anthony",
        "Donald",
        "Mark",
        "Paul",
        "Steven",
        "Andrew",
        "Kenneth",
        "Joshua",
        "George",
        "Kevin",
        "Brian",
        "Edward",
        "Ronald",
        "Timothy",
        "Jason",
        "Jeffrey",
        "Ryan",
        "Gary",
        "Nicholas",
        "Eric",
        "Stephen",
        "Jonathan",
        "Larry",
        "Justin",
        "Scott",
        "Brandon",
        "Raymond",
        "Jeffery",
        "Frank",
        "Gregory",
        "Samuel",
        "Patrick",
        "Alexander",
        "Dennis",
        "Walter",
        "Peter",
        "Harold",
        "Douglas",
        "Henry",
        "Carl",
        "Arthur",
        "Roger",
        "Joe",
        "Juan",
        "Jack",
        "Albert",
        "Jonathan",
    ]
    user_last_name_list = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Miller",
        "Davis",
        "Wilson",
        "Moore",
        "Taylor",
        "Anderson",
        "Thomas",
        "Jackson",
        "White",
        "Harris",
        "Martin",
        "Thompson",
        "Garcia",
        "Martinez",
        "Robinson",
        "Clark",
        "Rodriguez",
        "Lewis",
        "Lee",
        "Walker",
        "Hall",
        "Allen",
        "Young",
        "Green",
        "Adams",
        "Baker",
        "Hill",
        "Moore",
        "Thompson",
        "Walker",
        "White",
        "Harris",
        "Martin",
        "Thompson",
        "Garcia",
        "Martinez",
        "Robinson",
        "Clark",
        "Rodriguez",
        "Lewis",
        "Lee",
        "Robinson",
        "Clark",
        "Rodriguez",
        "Lewis",
        "Lee",
        "Walker",
        "Hall",
    ]

    years_list = [year for year in range(1960, 2009)]
    months_list = [month for month in range(1, 13)]
    days_list = [day for day in range(1, 29)]

    def generate_people_list() -> list:
        """Generate list of people"""
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
        birth_date = (
            f"{random.choice(years_list)}-"
            f"{random.choice(months_list)}-"
            f"{random.choice(days_list)}"
        )
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
                "my_subscriptions": subscriptions,
            },
        }
        users_list.append(user)
    return users_list


def generate_hashtags_for_db() -> list:
    """
    Generate a list of hashtags for the database.

    Returns:
        list: A list of dictionaries representing each hashtag.
    """
    hashtag_list = []

    for tag in POPULAR_HASHTAGS:
        hashtag = {"model": "post.hashtag", "pk": tag, "fields": {"tag": tag}}
        hashtag_list.append(hashtag)
    return hashtag_list


def generate_comments_for_db() -> list:
    """
    Generates a list of comments for the database.

    Returns:
        list: A list of dictionaries representing each comment.
    """
    comments_list = []

    def generate_text_for_comment() -> str:
        """
        Generates a random text for a comment.

        Returns:
            str: The generated text.
        """
        # Generate a random number of paragraphs for the comment
        number_of_paragraphs = random.randint(1, 2)

        # Generate the comment text using the Bacon Ipsum API
        url = (
            f"https://baconipsum.com/api/?type=all-meat&paras="
            f"{number_of_paragraphs}&format=html"
        )
        response = requests.get(url).content.decode("utf-8")
        paragraphs = response.replace("<p>", "").replace("</p>", "")
        return paragraphs

    comment_id = 30

    for _ in range(50):
        print("generating comment")
        # Generate a random user ID for the comment
        user_id = random.randint(50, 960)
        comment = {
            "model": "post.comment",
            "pk": comment_id,
            "fields": {
                "text": generate_text_for_comment(),
                "owner": user_id,
                "created_date": "2022-01-01",
            },
        }
        comment_id += 1
        comments_list.append(comment)

    print("generated comments")

    return comments_list


def generate_posts_for_db() -> list:
    """
    Generates a list of posts for database with titles, texts, owners,
    hashtags, likes, comments, and created date.
    """
    posts_list = []

    def generate_likes() -> list:
        """Generates a list of unique user IDs as likes for a post."""
        likes = []
        for _ in range(random.randint(0, 100)):
            user_id = random.randint(50, 960)
            if user_id not in likes:
                likes.append(user_id)
        return likes

    def generate_title_for_post() -> str:
        """Generates a title for a post using random words."""
        print("generating title for post")
        num_words = random.randint(1, 5)
        url = f"https://random-word-api.vercel.app/api?words={num_words}"
        response = requests.get(url).content.decode("utf-8")
        response = (
            response.replace("[", "")
            .replace("]", "")
            .replace('"', "")
            .split(",")
        )

        title = " ".join(response).capitalize()
        print("generated title for post")
        return title

    def generate_text_for_post() -> str:
        """Generates text for a post using random paragraphs."""
        print("generating text for post")
        number_of_paragraphs = random.randint(1, 5)

        url_1 = (
            f"https://baconipsum.com/api/?type=all-meat&paras="
            f"{number_of_paragraphs}&format=html"
        )
        url_2 = "https://baconipsum.com/api/?type=meat-and-filler&format=html"
        url_3 = (
            f"https://baconipsum.com/api/?type=meat-and-filler&paras="
            f"{number_of_paragraphs}&format=html"
        )

        url = random.choice([url_1, url_2, url_3])
        response = requests.get(url).content.decode("utf-8")

        paragraphs = response.replace("<p>", "").replace("</p>", "")
        print("generated text for post")
        return paragraphs

    post_id = 10

    for owner_id in range(50, 100):
        number_of_posts_for_owner = random.randint(0, 2)
        if number_of_posts_for_owner != 0:
            comment_ids = [random.randint(30, 79) for _ in range(3)]
            hashtags = [
                random.choice(POPULAR_HASHTAGS)
                for _ in range(random.randint(1, 5))
            ]
            for i in range(number_of_posts_for_owner):
                print("Generating posts for user", owner_id)
                post = {
                    "model": "post.post",
                    "pk": post_id,
                    "fields": {
                        "title": generate_title_for_post(),
                        "text": generate_text_for_post(),
                        "owner": owner_id,
                        "hashtags": hashtags,
                        "likes": generate_likes(),
                        "comments": comment_ids,
                        "created_date": "2022-01-01",
                    },
                }

                posts_list.append(post)
                post_id += 1
                print("Generated posts for user", owner_id)
                print("-" * 30)

    return posts_list


def save_users_data_to_json(users: list, file_name: str) -> None:
    """
    Save a list of user data to a JSON file.

    Args:
        users (list): A list of user data to be saved.
        file_name (str): The name of the JSON file to be created.

    Returns:
        None
    """
    with open(f"{file_name}.json", "w") as file:
        json.dump(users, file, indent=4)


def open_json_file(file_name: str) -> list:
    """
    Open a JSON file and return its contents as a list of dictionaries.
    """
    with open(file_name, "r") as file:
        data = json.load(file)
    return data


def combine_all_data() -> list:
    """
    Combine all data into a single list.
    """
    countrys_data = open_json_file("country_db_data.json")
    users_data = open_json_file("users_data_for_db.json")

    users_data = countrys_data + users_data
    save_users_data_to_json(users_data, "users_data_for_db")

    hashtags_data = open_json_file("hashtags_data_for_db.json")
    comments_data = open_json_file("comments_data_for_db.json")
    posts_data = open_json_file("posts_data_for_db.json")

    posts_data = hashtags_data + comments_data + posts_data
    save_users_data_to_json(posts_data, "posts_data_for_db")


if __name__ == "__main__":
    users_data = generate_users_for_db()
    save_users_data_to_json(users_data, "users_data_for_db")

    hashtags_data = generate_hashtags_for_db()
    save_users_data_to_json(hashtags_data, "hashtags_data_for_db")

    comments_data = generate_comments_for_db()
    save_users_data_to_json(comments_data, "comments_data_for_db")

    post_data = generate_posts_for_db()
    save_users_data_to_json(post_data, "posts_data_for_db")

    combine_all_data()
