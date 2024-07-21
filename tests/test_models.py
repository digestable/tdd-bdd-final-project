# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    # Test to read a product and ensure that it passes
    def test_read_a_product(self):
        """It should read a product in the database"""
        product = ProductFactory()
        # logging.logger(product)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Get the single product from the database and assert correct product
        retrieved_product = Product.find(product.id)
        self.assertEqual(retrieved_product.id, product.id)
        self.assertEqual(retrieved_product.name, product.name)
        self.assertEqual(retrieved_product.description, product.description)
        self.assertEqual(retrieved_product.price, product.price)

    # Test to update a product and ensure that it passes
    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # UPdate and save description
        product.description = "test desc"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "test desc")
        # Retrieve the product and verify the id hasn't changed
        # AND desc is update version
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "test desc")

    # Test to update a product with invalid id EXTRA SAD
    def test_update_a_product_invaliid_update(self):
        """It should not Update a Product and return 404"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # UPdate and save description
        product.description = "test desc"
        original_id = product.id
        product.id= None
        self.assertRaises(DataValidationError, product.update)



    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Check product in database
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Delete product
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should List All Products"""
        # Assert no products in db
        products = Product.all()
        self.assertEqual(products, [])

        # Create 10 products
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        # Check 10 products in database
        products = Product.all()
        self.assertEqual(len(products), 10)

    def test_find_product_by_name(self):
        """It should List All Products"""
        # Create product in db
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)


    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)
            

    # Increase coverage >95% by adding four extra tests, increasing coverage from 93%
    def test_find_by_price(self):
        """It should Find Products by Price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)


    # Deserializes a Product - available not bool datavalidation error
    def test_deserialize_available_not_bool(self):
        """It should get DataValidation error when available not bool type"""
        product = ProductFactory()
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": "19.99",
            "available": "yes",  # Invalid type for testing
            "category": "ELECTRONICS"
        }
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertIn("Invalid type for boolean [available]", str(context.exception))

    # Deserializes a Product - invalid attribute raises datavalidation error
    def test_deserialize_invalid_category(self):
        """It should show invalid category raises datavalidation error"""
        product = ProductFactory()
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": "19.99",
            "available": True,  
            "category": "INVALID_CATEGORY"
        }
        
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertIn("Invalid attribute:", str(context.exception))

    # Deserializes a Product - invalid type raises datavalidation error
    def test_deserialize_invalid_data_type(self):
        """It should show invalid category raises datavalidation error"""
        product = ProductFactory()
        data = 'Not_dict'        
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertIn("Invalid product: body of request contained bad or no data", str(context.exception))

    # Strip function in find_by_price function
    def test_valid_price_function(self):
        """It should Strip function in find_by_price function"""
        price = "12.22"
        price_clean = Product.find_by_price(price)
        self.assertFalse(type(price_clean) is Decimal)
       

