# Project 1

Web Programming with Python and JavaScript
This website allows users to search for books, see others' reviews for a book, and submit their own reviews. application.py sets up Flask, the database, different routes, and handles interactions with the database. import.py inserts a list of 5000 books into the database, with the data from books.csv. layout.html is the template for the other html files. index.html is the main page, with a login and option to go to the signup. signup.html has a form for signing up, if the username is not taken. search.html is the page users are taken to once they have logged in, and allows them to search for a book by title, author, or ISBN author. The keyword is compared to the information in the database, and the page will display the results of the search or a message saying no results. Each search result will link out to a page about the book. book.html contains information about the book, Goodreads data about its ratings, reviews from other users, and an area for a particular user to submit a review. status.html displays the status after a search or review submission if it was unsuccessful and a message about why, and is also the page that users are taken to after successfully submitting a review. Each page other than the main login and signup have an option to return to the search page or to log out. When a user goes to api/<isbn>, the page will return a JSON response with information about the book with that ISBN, or an error message if no such book exists in the database.
=======
# claireqw
