# EcoFinds

**EcoFinds** is a modern, eco-friendly web platform for listing, discovering, and purchasing second-hand items. Built with Flask and MySQL, it features user authentication, product photo uploads, animated UI, and seamless shopping cart and purchase experiences.

---

## Features

- **User Authentication:** Sign up, log in, and manage your profile.
- **Product Listings:** Add, edit, and delete listings with photo uploads.
- **Product Feed:** Browse and filter products by keyword and category.
- **Animated, Responsive UI:** Stylish dashboard, product cards, and forms with live effects.
- **Shopping Cart:** Add products to your cart and purchase them.
- **Purchase History:** View your previously purchased items.
- **Access Control:** Users cannot buy or add their own listings to the cart.
- **Robust Database:** MySQL with foreign key constraints for data integrity.

---

## Screenshots

<img src="static/demo_feed.png" width="350"> <img src="static/demo_dashboard.png" width="350">

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ecofinds.git
cd ecofinds
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. MySQL Setup

- Create the database and tables:

```sql
CREATE DATABASE ecofinds_db;
USE ecofinds_db;

CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    image VARCHAR(200) DEFAULT 'default_user.png'
);

CREATE TABLE product (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    image VARCHAR(200) DEFAULT 'placeholder.png',
    owner_id INT,
    FOREIGN KEY(owner_id) REFERENCES user(id)
);

CREATE TABLE cart (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    product_id INT,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(product_id) REFERENCES product(id)
);

CREATE TABLE purchase (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    product_id INT,
    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(product_id) REFERENCES product(id) ON DELETE CASCADE
);
```

- (Optional) Insert some sample data (see [`sample_data.sql`](sample_data.sql) if provided).

### 4. Configure Flask

Edit `config.py` with your MySQL credentials and secret key:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'your_mysql_user'
MYSQL_PASSWORD = 'your_mysql_password'
MYSQL_DB = 'ecofinds_db'
SECRET_KEY = 'your_secret_key'
```

### 5. Run the App

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## Project Structure

```
ecofinds/
│
├── app.py
├── config.py
├── models.py
├── requirements.txt
│
├── static/
│   ├── style.css
│   ├── products/
│   ├── placeholder.png
│   └── default_user.png
│
└── templates/
    ├── base.html
    ├── login.html
    ├── signup.html
    ├── dashboard.html
    ├── feed.html
    ├── add_product.html
    ├── my_listings.html
    ├── product_detail.html
    ├── cart.html
    └── previous_purchase.html
```

---

## Customization

- Change categories by editing the `categories` list in `app.py`.
- Customize styles in `static/style.css`.
- Add more features: messaging, reviews, advanced search, etc.

---

## Security Notes

- Passwords are stored as hashes (never plaintext).
- Only the owner can edit/delete their products.
- Users cannot buy or add their own products to the cart.

---

## License

MIT License

---

## Contributing

Pull requests and feature suggestions are welcome!

---

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [MySQL](https://www.mysql.com/)
- [Font Awesome](https://fontawesome.com/)
- [Google Fonts](https://fonts.google.com/)

---

**EcoFinds — Give old things new life!**