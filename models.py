from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



# ---------------- FARMER MODEL ---------------- #

class Farmer(db.Model):
    __tablename__ = "farmers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    village = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    land = db.Column(db.Float, nullable=False)

    crops = db.relationship(
        "Crop",
        backref="farmer",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Farmer {self.name}>"


# ---------------- CROP MODEL ---------------- #

class Crop(db.Model):
    __tablename__ = "crops"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    crop_name = db.Column(db.String(100), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    area = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Crop {self.crop_name}>"


# ---------------- ADMIN MODEL ---------------- #

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Admin {self.username}>"


# ---------------- CONTACT MODEL ---------------- #

class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Contact {self.name}>"
    
    
    