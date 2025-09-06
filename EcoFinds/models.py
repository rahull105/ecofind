from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, username, password, image):
        self.id = id
        self.email = email
        self.username = username
        self.password = password
        self.image = image

class Product:
    def __init__(self, id, title, description, category, price, image, owner_id):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.image = image
        self.owner_id = owner_id