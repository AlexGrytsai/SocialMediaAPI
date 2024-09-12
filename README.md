
## Social Media API  
  
## Overview  

This project is a Django REST Framework-based API for managing users and posts. It includes features such as user registration, user profile management, posting, commenting, liking posts, and user subscription.   

## Features  
  
**User Management**: 
 - Custom User model using email as the username. 
 - User registration, profile update, and password change. 
 - Follow and unfollow other users. 
 - View posts by users they follow. 
 - Custom image upload path for user photos. 

**Post Management**: 
 - Create, update, and delete posts. 
 - Add comments to posts. 
 - Like and unlike posts.
 - Filter posts by hashtags and author.
 - Custom image upload path for posts images.

**JSON Web Tokens**: JSON Web Tokens are used to authenticate users. 

**Asynchronous Tasks with Celery and Flower**: The API includes a feature to schedule posts using Celery.

## Project Structure

- **UserManager**: Custom manager for the User model.
- **User**: Custom user model with fields such as `email`, `birth_date`, `photo`, `residence_place`, `followers`, and `my_subscriptions`.
- **ResidencePlace**: Model to store the user's country of residence.
- **Post**: Model representing a post with fields such as `title`, `text`, `image`, `owner`, `hashtags`, `likes`, and `comments`.
- **Hashtag**: Model representing hashtags used in posts.
- **Comment**: Model representing comments on posts.
  

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/AlexGrytsai/SocialMediaAPI
    cd https://github.com/AlexGrytsai/SocialMediaAPI
    ```
2. **Environment Variables:**
		Ensure you have a `.env` file in the root directory with the following variables:
		
	```env
	WEATHER_KEY=<WEATHERAPI_API_KEY>
	POSTGRES_PASSWORD=social
	POSTGRES_USER=social
	POSTGRES_DB=social
	POSTGRES_HOST=db
	POSTGRES_PORT=5432
	```
		
3. **Build and start the application using Docker:**
    ```sh
    docker-compose up
    ```
4. **Loading data into a database (examples):**
	Open a new terminal and enter the command:
	```sh
    docker exec -it social_media_api-app-1 /bin/sh
    python manage.py users_data_for_db.json
    python manage.py posts_data_for_db.json
    ```
5. **Create a superuser:**
	```sh
    python manage.py createsuperuser
    ```
    After created Super User, exit from container using the following command:
    ```sh
    exit
    ```
    
6. **Access the application:**
    
    Open your web browser and navigate to [http://localhost:8000](http://localhost:8000) or [http://127.0.0.1:8000](http://127.0.0.1:8000).
	You need to get access token for use app - [get token](http://127.0.0.1:8000/api/v1/token/).
	For use an access token, you can use [ModHeader - Modify HTTP headers](https://chromewebstore.google.com/detail/modheader-modify-http-hea/idgpnmonknjnojddfkpgkljpfnnfcklj?pli=1) for Chrome. After installing it, you need added Authorization with "Bearer <your_access_token>".
	Now, you can use all application's feathers.
	Use Flower to monitor the status of scheduled tasks and other Celery workers - [http://localhost:5555](http://localhost:5555).
	
7. **Access the application's documentation:**
    
    You can familiarize yourself with all the documentation and methods of using the Airport API System by clicking on the link: [swagger](http://localhost:8000/api/v1/doc/swagger/).
