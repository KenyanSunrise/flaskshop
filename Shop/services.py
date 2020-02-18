from Shop.models import Product
from flask import current_app


def get_page_of_products(data):
    if data is None:
        manufacturer = None
        category = None
        page = 1
    else:
        manufacturer = data.get('manufacturer')
        category = data.get('category')
        page = data.get('page', 1)
    products = Product.query
    if manufacturer:
        products.filter_by(ManufacturerName=manufacturer)
    if category:
        products.filter_by(CategoryName=category)
    page_with_products = products.paginate(page=page, per_page=current_app.config['PRODUCTS_PER_PAGE'])
    return page, page_with_products
