# Social Media API

A Django-based RESTful API for a social media application with user authentication, profile management, post creation/retrieval, likes, comments, and follow/unfollow functionality.

## Prerequisites
- Python 3 must be already installed
- Docker and Docker Compose installed on your system
- Postgres DB

## Installation

```shell
git clone https://github.com/GeorgePavlej/social-media-api.git
```

```shell
cd social-media-api
```

```shell
python -m venv venv
```
```shell
venv\Scripts\activate (Windows)
```
```shell
source venv/bin/activate (Linux or macOS)
```

```shell
copy .env.sample -> .env and populate with all required data
```

```shell
pip install -r requirements.txt
```

```shell
python manage.py migrate
```

```shell
python manage.py runserver
```

## Run docker to start the development server and other required services:

```shell
docker-compose up --build
```
## API documentation

The API documentation is available at:
- api/doc/swagger/

## Getting access
<hr>

- Create user via /api/user/register/
- Get access token via /api/user/token/

## Features
<hr>

- JWT authenticated;
- Users authentication & registration

## API Endpoints

### Users Service

- `POST: /users/` : Register a new user.

- `POST: /users/token/` : Obtain JWT tokens.

- `POST: /users/token/refresh/` : Refresh JWT token.

- `GET: /users/me/` : Get profile information of the authenticated user.

- `POST: /users/me/` : Logout and invalidate token

- `PUT/PATCH: /users/me/` : Update profile information of the authenticated user.

### Profiles Service

- `GET: /profiles/`: List all profiles.
- `POST: /profiles/`: Create a new profile.
- `GET: /profiles/<id>/`: Retrieve a specific profile.
- `PUT/PATCH: /profiles/<id>/`: Update a specific profile.
- `DELETE: /profiles/<id>/`: Delete a specific profile.

### Follows Service

- `GET /follow/`: List all follows.
- `POST /follow/`: Create a new follow (follow a user).
- `DELETE /follow/<id>/`: Unfollow a user.

### Posts Service

- `GET: /posts/`: List all posts.
- `POST: /posts/`: Create a new post.
- `GET: /posts/<id>/`: Retrieve a specific post.
- `PUT/PATCH: /posts/<id>/`: Update a specific post.
- `DELETE: /posts/<id>/`: Delete a specific post.

### Likes Service

- `GET: /likes/`: List all likes.
- `POS: /likes/`: Create a new like (like a post).
- `DELETE: /likes/<id>/`: Unlike a post.

### Comments Service

- `GET: /comments/`: List all comments.
- `POST: /comments/`: Create a new comment.
- `GET: /comments/<id>/`: Retrieve a specific comment.
- `PUT/PATCH: /comments/<id>/`: Update a specific comment.
- `DELETE: /comments/<id>/`: Delete a specific comment.
