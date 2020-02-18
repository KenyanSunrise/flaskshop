from webapp import db
from datetime import datetime


class UserFunctions():
    def to_dict(self):
        return {'id': self.id,
                'Name': self.Name,
                'Link': self.create_link()}


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(80), unique=True)
    Slug = db.Column(db.String(80), unique=True)
    Description = db.Column(db.String(80), nullable=True)
    Reference = db.Column(db.String(80), nullable=True)
    Stock = db.Column(db.Integer, nullable=False, default=0)
    Price = db.Column(db.String, nullable=False)
    Available = db.Column(db.Boolean, default=False)
    Created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    Updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(), onupdate=datetime.utcnow())
    CategoryName = db.Column(db.String(80), db.ForeignKey('category.Name'), nullable=False)
    ManufacturerName = db.Column(db.String(80), db.ForeignKey('manufacturer.Name'), nullable=False)

    def to_dict(self):
        return {'Slug': self.Slug,
                'Description': self.Description,
                'Reference': self.Reference,
                'Stock': self.Stock,
                'Price': self.Price,
                'Available': self.Available,
                'Updated': self.Updated.strftime("%d %B %Y"),
                'Category': {'Name': self.Category.Name,
                             'Slug': self.Category.Slug},
                'Manufacturer': {'Name': self.Manufacturer.Name,
                                 'Slug': self.Manufacturer.Slug}
                }

    def __repr__(self):
        return 'Product: {0} with id: {1}'.format(self.Name, self.id)


class Category(UserFunctions, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(80), unique=True)
    Slug = db.Column(db.String(80), unique=True)
    Products = db.relationship('Product', backref='Category')

    def __repr__(self):
        return 'Category: {0} with id: {1}'.format(self.Name, self.id)


class Manufacturer(UserFunctions, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(80), unique=True)
    Slug = db.Column(db.String(80), unique=True)
    Products = db.relationship('Product', backref='Manufacturer')

    def __repr__(self):
        return 'Manufacturer: {0} with id: {1}'.format(self.Name, self.id)


Order_products = db.Table('Order_products',
                          db.Column('Product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
                          db.Column('Order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True)
                          )


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Status = db.Column(db.String)
    Created = db.Column(db.DateTime, default=datetime.utcnow())
    Updated = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    Products = db.relationship('Product', secondary=Order_products, lazy='subquery',
                               backref=db.backref('Orders', lazy='subquery'))

