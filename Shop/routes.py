from flask import Blueprint, jsonify
from Shop.models import Category, Manufacturer
from flask import url_for, request
from Shop.services import get_page_of_products
import json

shop = Blueprint('shop', __name__)


@shop.route('/', methods=["GET"])
def main_links():
    response = {'links': {
        'auth': {'Github': url_for('github.login', _external=True),
                 'Google': url_for('google.login', _external=True),
                 'Yandex': url_for('yandex.login', _external=True)},
        'account': {'info': url_for('account.account_page', _external=True),
                    'logout': url_for('account.logout', _external=True)},
        'get_data': {'available_manufacturers': url_for('shop.get_available_manufacturers'),
                     'available_categories': url_for('shop.get_available_categories'),
                     'get_page_of_items': url_for('shop.products_page')}}
    }
    return jsonify(response), 200


@shop.route('/get_available_manufacturers', methods=['GET'])
def get_available_manufacturers():
    manufacturers = Manufacturer.query.all()
    manufacturers_name = [x.Name for x in manufacturers]
    result = {
        'available manufacturers': manufacturers_name
    }
    return result


@shop.route('/get_available_categories', methods=['GET'])
def get_available_categories():
    categories = Category.query.all()
    categories_name = [x.Name for x in categories]
    result = {
        'available categories': categories_name
    }
    return result


@shop.route('/products')
def products_page():
    data = request.json
    page, page_of_products = get_page_of_products(data)
    result = {'items': {x.Name: x.to_dict() for x in page_of_products.items},
              'page': page,
              'pages': page_of_products.pages,
              'item_per_page': page_of_products.per_page,
              'total_items': page_of_products.total}
    return result