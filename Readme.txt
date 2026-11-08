Little Lemon - Back-end developer capstone project
Django, Django REST Framework, MySQL, Djoser token authentication.

API PATHS TO TEST
-----------------
/api/menu/
/api/menu/<id>/
/api/bookings/
/api/bookings/<id>/
/auth/users/
/auth/token/login/
/auth/token/logout/

The home page (static HTML and CSS) is at /
The Django admin is at /admin/


SETUP
-----
1. Create the database in MySQL:
       CREATE DATABASE littlelemon CHARACTER SET utf8mb4;

2. Install the dependencies:
       python3 -m venv .venv
       source .venv/bin/activate        (Windows: .venv\Scripts\activate)
       pip install -r requirements.txt

3. If your MySQL user is not root with an empty password, copy .env.example
   to .env and fill in your own values.

4. Create the tables, load sample menu items and start the server:
       python manage.py migrate
       python manage.py loaddata menu
       python manage.py runserver

5. Run the unit tests:
       python manage.py test


TESTING WITH INSOMNIA
---------------------
The base URL is http://127.0.0.1:8000
Send the bodies below as JSON.

1. Register a user
   POST /auth/users/
   {"username": "reviewer", "email": "reviewer@example.com", "password": "S3cure-pass-42"}

2. Get a token
   POST /auth/token/login/
   {"username": "reviewer", "password": "S3cure-pass-42"}
   The response looks like {"auth_token": "<token>"}

3. For requests that need authentication, add this header:
   Authorization: Token <token>

4. Menu
   GET    /api/menu/          public
   GET    /api/menu/1/        public
   POST   /api/menu/          token required
   PUT    /api/menu/1/        token required
   DELETE /api/menu/1/        token required
   Body for POST and PUT:
   {"title": "Moussaka", "price": "16.50", "inventory": 12}

5. Bookings (all requests need a token)
   GET    /api/bookings/
   GET    /api/bookings/1/
   POST   /api/bookings/
   PUT    /api/bookings/1/
   DELETE /api/bookings/1/
   Body for POST and PUT:
   {"name": "Mario", "no_of_guests": 2, "booking_date": "2030-02-01T18:30:00Z"}

6. Log out (invalidates the token)
   POST /auth/token/logout/
