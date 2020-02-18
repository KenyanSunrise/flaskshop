import unittest
from webapp import create_app, db
from Shop.models import Product, Category, Manufacturer, Order
from config import Config
from slugify import slugify
from auth.models import User, OAuth, Permission, AnonymousUser, Role
from Shop.routes import get_available_manufacturers, get_available_categories


class TestingConfig(Config):
    TEST = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None


class UserModelCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_category_fields(self):
        category1 = Category(Name='Фары', Slug=slugify('Фары'))
        db.session.add(category1)
        db.session.commit()
        self.assertEqual(Category.query.filter_by(Name='Фары').first().id, 1)
        self.assertEqual(Category.query.filter_by(Slug=slugify('Фары')).first().id, 1)
        self.assertEqual(Category.query.count(), 1)

    def test_manufacturer_fields(self):
        manufacturer1 = Manufacturer(Name='Лада', Slug=slugify('Лада'))
        db.session.add(manufacturer1)
        db.session.commit()
        self.assertEqual(Manufacturer.query.filter_by(Name='Лада').first().id, 1)
        self.assertEqual(Manufacturer.query.filter_by(Slug=slugify('Лада')).first().id, 1)
        self.assertEqual(Manufacturer.query.count(), 1)

    def test_product_fields(self):
        product1 = Product(Name='Ступица',
                           Slug=slugify('Ступица'),
                           Price='123.3',
                           Stock=1,
                           Available=True,
                           ManufacturerName='Vas',
                           CategoryName='Что-то')
        db.session.add(product1)
        db.session.commit()
        self.assertEqual(float(product1.Price), 123.3)

    def test_manufacturer_and_category_foreign_key(self):
        category1 = Category(Name='Фары', Slug=slugify('Фары'))
        manufacturer1 = Manufacturer(Name='Лада', Slug=slugify('Лада'))
        product1 = Product(Name='Ступица',
                           Slug=slugify('Ступица'),
                           Price='123.3',
                           Stock=1,
                           Available=True)
        category1.Products.append(product1)
        manufacturer1.Products.append(product1)
        db.session.add_all([category1, product1, manufacturer1])
        db.session.commit()
        self.assertEqual(product1.Manufacturer.Name, manufacturer1.Name)
        self.assertEqual(product1.Category.Name, category1.Name)
        self.assertEqual(len(category1.Products), 1)
        self.assertEqual(len(manufacturer1.Products), 1)
        product2 = Product(Name='Ступица2',
                           Slug=slugify('Ступица2'),
                           Price='1255.3',
                           Stock=1,
                           Available=True)
        category1.Products.append(product2)
        manufacturer1.Products.append(product2)
        db.session.add_all([category1, product2, manufacturer1])
        db.session.commit()
        self.assertEqual(len(category1.Products), 2)
        self.assertEqual(len(manufacturer1.Products), 2)

    def test_OAuth_and_User(self):
        oa = OAuth(Provider='Github', Provider_user_id='123', Token='456token')
        u1 = User(Name='Pavel', Email='pepega@gmail.com', Address='adr')
        oa.User = u1
        db.session.add_all([oa, u1])
        db.session.commit()
        query = OAuth.query.filter_by(
            Provider='Github',
            Provider_user_id='123',
        )
        oauth = query.one()
        self.assertEqual(oauth.User, u1)

    def test_availabele_manufacturers(self):
        manufacturer1 = Manufacturer(Name='Лада', Slug=slugify('Лада'))
        manufacturer2 = Manufacturer(Name='Приора', Slug=slugify('Приора'))
        db.session.add_all([manufacturer1, manufacturer2])
        db.session.commit()
        self.assertEqual(get_available_manufacturers(), {'available manufacturers': ['Лада', 'Приора']})

    def test_available_categories(self):
        cat1 = Category(Name='Фары', Slug=slugify('Фары'))
        cat2 = Category(Name='Двери', Slug=slugify('Двери'))
        db.session.add_all([cat1, cat2])
        db.session.commit()
        self.assertEqual(get_available_categories(), {'available categories': ['Фары', 'Двери']})

    def test_orders(self):
        category1 = Category(Name='Фары', Slug=slugify('Фары'))
        manufacturer1 = Manufacturer(Name='Лада', Slug=slugify('Лада'))
        product1 = Product(Name='Ступица',
                           Slug=slugify('Ступица'),
                           Price='123.3',
                           Stock=1,
                           Available=True)
        category1.Products.append(product1)
        manufacturer1.Products.append(product1)
        db.session.add_all([category1, product1, manufacturer1])
        db.session.commit()
        oa = OAuth(Provider='Github', Provider_user_id='123', Token='456token')
        u1 = User(Name='Pavel', Email='pepega@gmail.com', Address='adr')
        oa.User = u1
        db.session.add_all([oa, u1])
        db.session.commit()
        order = Order(Status='Testing')
        order.Products.append(product1)
        order.User = u1
        db.session.add_all([u1, order])
        db.session.commit()
        self.assertEqual(u1.orders.first().Status, 'Testing')
        self.assertEqual(order.User, u1)

    def test_user_role(self):
        Role.insert_roles()
        oa = OAuth(Provider='Github', Provider_user_id='123', Token='456token')
        u = User(Name='Pavel', Email='pepega@gmail.com', Address='adr')
        oa.User = u
        db.session.add_all([oa, u])
        db.session.commit()

        self.assertTrue(u.can(Permission.STAFF))
        self.assertTrue(u.can(Permission.UPDATE))
        self.assertTrue(u.can(Permission.REMOVE))
        self.assertTrue(u.can(Permission.ADMIN))
        u.role = Role.query.filter_by(name='Moderator').first()
        print(u.role.name)
        self.assertTrue(u.can(Permission.STAFF))
        self.assertTrue(u.can(Permission.UPDATE))
        self.assertTrue(u.can(Permission.REMOVE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        Role.insert_roles()
        self.assertFalse(u.can(Permission.STAFF))
        self.assertFalse(u.can(Permission.UPDATE))
        self.assertFalse(u.can(Permission.REMOVE))
        self.assertFalse(u.can(Permission.ADMIN))



if __name__ == '__main__':
    unittest.main(verbosity=2)
