## E-COMMERCE

Overview

This is a Django-based E-Commerce website designed to showcase and sell products, with a focus on socks. The site allows users to browse products, view details, add reviews with ratings, and download invoices for orders. The project is hosted on GitHub at https://github.com/Aryannegi14/E-Commerce.
Features

Product Listings: Display socks with details and average ratings.
Reviews and Ratings: Users can add reviews and rate products.
Order Management: Generate and download PDF invoices for orders.
Search Functionality: Search for products by name.
Email Notifications: Send order details via email (Gmail integration).

Installation
Prerequisites

Python 3.x
Django
Other dependencies listed in requirements.txt

Setup

Clone the repository:git clone https://github.com/Aryannegi14/E-Commerce.git
cd E-Commerce


Install dependencies:pip install -r requirements.txt


Set up environment variables:
Create a .env file or use Replit’s “Secrets” tab.
Add your Gmail credentials (e.g., EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) for email functionality.


Apply migrations:python manage.py migrate


Run the development server:python manage.py runserver


Or, for Replit, use the default run command configured in .replit.



Usage

Visit the homepage to browse socks.
Click a product to see details and add reviews.
Place an order to generate and download an invoice via email.
Use the search bar to find specific products.

Project Structure

e_commerce/: Main Django app folder containing views, templates, and models.
views.py: Handles product listings, reviews, and invoice generation.
templates/: HTML templates for the frontend.
models.py: Defines the database schema (e.g., Product, Review, Order).


manage.py: Django management script.
requirements.txt: Lists project dependencies.

Contributing
Feel free to fork the repository, make improvements, and submit pull requests. Ensure you follow the existing code style and update the README if adding features.
License
This project is licensed under the Apache-2.0 License. See the LICENSE file for details.
Troubleshooting

Contact
For questions or support, reach out to the repository owner at aryannegiofficial@gmail.com.
