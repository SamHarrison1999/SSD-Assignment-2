from flask_Captchaify import Captchaify
from flask_testing import TestCase

from main import db, app
from main.models import Customer, load_user


# noinspection PyPep8Naming
class test(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def dictionary_attack(self):
        return self.client.get('/attacker/dictionary-attack', follow_redirects=True)

    def register(self, username, email, password, confirm_password):
        return self.client.post('/register', data=dict(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        ), follow_redirects=True)

    def change_password(self, customer_id, current_password, new_password, confirm_password):
        return self.client.post(f'/change_password/{customer_id}', data=dict(
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password
        ), follow_redirects=True)

    def profile(self, customer_id):
        return self.client.get(f'/profile/{customer_id}', follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def page_not_found(self):
        return self.client.get('/path_that_does_not_exist', follow_redirects=True)

    def search(self, search):
        return self.client.post('/search', data=dict(search=search), follow_redirects=True)

    def create_product(self, product_name, quantity, price, description, product_image):
        with open(product_image, "rb") as your_file:
            return self.client.post("/create_product", data={
                'product_name': product_name,
                'quantity': quantity,
                'price': price,
                'description': description,
                "product_image": your_file
            }, follow_redirects=True)

    def update_product(self, product_id, product_name, quantity, price, description, product_image):
        with open(product_image, "rb") as your_file:
            return self.client.post(f"/update-item/{product_id}", data={
                'product_name': product_name,
                'quantity': quantity,
                'price': price,
                'description': description,
                "product_image": your_file
            }, follow_redirects=True)

    def update_order(self, order_id, status):
        return self.client.post(f'/update-order/{order_id}', data={
            'order_status': status,
        }, follow_redirects=True)

    def get_image(self, file_name):
        with open(file_name, "rb") as your_file:
            return self.client.get(f'/media/{your_file}', follow_redirects=True)

    def view_products(self):
        return self.client.get('/view-shop-items', follow_redirects=True)

    def delete_item(self, product_id):
        return self.client.delete(f"/delete-item/{product_id}", follow_redirects=True)

    def add_to_cart(self, product_id):
        return self.client.post(f'/add-to-cart/{product_id}')

    def increase_cart_quantity(self, cart_id):
        return self.client.get(f"/increase-quantity?cart_id={cart_id}", follow_redirects=True)

    def decrease_cart_quantity(self, cart_id):
        return self.client.get(f"/decrease-quantity?cart_id={cart_id}", follow_redirects=True)

    def remove_from_cart(self, cart_id):
        return self.client.get(f"/remove-from-cart?cart_id={cart_id}", follow_redirects=True)

    def view_cart(self):
        return self.client.get('/cart', follow_redirects=True)

    def manage_customers(self):
        return self.client.get("/customers", follow_redirects=True)

    def delete_customer(self, customer_id):
        return self.client.delete(f"/customers/{customer_id}", follow_redirects=True)

    def place_order(self):
        return self.client.get('/place-order', follow_redirects=True)

    def viewer_my_orders(self):
        return self.client.get('/orders', follow_redirects=True)

    def view_orders(self):
        return self.client.get('/view-orders', follow_redirects=True)

    def test_register(self):
        rv = self.register("admin", "admin@admin.com", "123456", "123456")
        assert 'Account created successfully!' in rv.data.decode('utf-8')
        self.assertEqual(rv.request.path, '/home')

    def test_username_already_exists(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        rv = self.register("admin", "admin2@admin.com", "123456", "123456")
        assert ("There was an error with creating a user" and
                "Please try a different username" in rv.data.decode('utf-8'))

    def test_email_already_exists(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        rv = self.register("admin2", "admin@admin.com", "123456", "123456")
        assert "There was an error with creating a user" and "Please try a different email" in rv.data.decode('utf-8')

    def test_login(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        rv = self.login("admin@admin.com", "123456")
        assert 'You are now logged in as: admin' in rv.data.decode('utf-8')

    def test_failed_login(self):
        rv = self.login("test1@gmail.com", "123456")
        assert "Email and password don&#39;t match a valid user" in rv.data.decode('utf-8')

    def test_logout(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.logout()
        assert "You are now logged out" in rv.data.decode('utf-8')
        self.assertEqual(rv.request.path, '/home')

    def test_error_raised_if_try_to_read_password(self):
        customer = Customer()
        customer.id = 1
        customer.username = 'Test'
        customer.email = 'test1@gmail.com'
        customer.password = '123456'
        customer.confirm_password = '123456'
        with self.assertRaises(AttributeError):
            customer.password()

    def test_load_user(self):
        with app.app_context():
            self.register("admin", "admin@admin.com", "123456", "123456")
            customer = load_user(1)
            with self.subTest():
                self.assertEqual(customer.email, "admin@admin.com")
                self.assertEqual(customer.username, "admin")
                self.assertTrue(customer.verify_password('123456'))

    def test_profile_page(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.profile(1)
        assert 'Welcome <span class="text-capitalize">admin</span>' in rv.data.decode('utf-8')

    def test_access_denied_when_attempt_to_access_another_customers_profile(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.profile(2)
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_page_not_found_error(self):
        rv = self.page_not_found()
        assert 'Page not found' in rv.data.decode('utf-8')

    def test_change_password(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.change_password(1, "123456", "12345678", "12345678")
        assert 'Password updated' in rv.data.decode('utf-8')
        self.assertEqual(rv.request.path, '/profile/1')

    def test_error_when_attempt_to_change_password_when_current_password_is_incorrect(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.change_password(1, "1234567", "12345678", "12345678")
        assert 'Current password is incorrect' in rv.data.decode('utf-8')

    def test_error_when_passwords_do_not_match(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.change_password(1, "123456", "12345678", "123456")
        assert 'New passwords do not match' in rv.data.decode('utf-8')

    def test_access_denied_if_attempt_to_change_another_customers_password(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.register("admin2", "admin2@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.change_password(2, "123456", "12345678", "123456")
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_create_product(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        assert 'Apple Watch Ultra Added Successfully' in rv.data.decode('utf-8')

    def test_error_when_creating_product(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.create_product("Apple Watch Ultra", 10000, None, "Apple Smart Watch", 'AppleWatch.jpg')
        assert 'There was an error with adding a product' in rv.data.decode('utf-8')

    def test_access_denied_if_none_admin_attempts_to_create_a_product(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.login("test@test.com", "123456")
        rv = self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_manage_products(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.view_products()
        assert 'Apple Watch Ultra' in rv.data.decode('utf-8')

    def test_access_denied_if_none_admin_attempts_to_manage_products_list(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.login("test@test.com", "123456")
        rv = self.view_products()
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_update_product(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.update_product(1, "Apple Watch", 10, 600, "Smart Watch", 'AppleWatch.jpg')
        assert 'Apple Watch Updated Successfully' in rv.data.decode('utf-8')
        assert rv.request.path == '/view-shop-items'

    def test_error_raised_if_validation_fails_when_updating_a_product(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.update_product(1, "", 10, 600, "", 'AppleWatch.jpg')
        assert 'There was an error with updating a product' in rv.data.decode('utf-8')

    def test_access_denied_if_none_admin_attempts_to_update_a_product(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.login("test@test.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.update_product(1, "Apple Watch", 10, 600, "Smart Watch", 'AppleWatch.jpg')
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_delete_product_from_list_of_products(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.delete_item(1)
        assert 'Item Deleted Successfully' in rv.data.decode('utf-8')

    def test_access_denied_if_non_admin_attempts_to_delete_a_product(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.login("test@test.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.delete_item(1)
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_add_to_cart(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        rv = self.view_cart()
        assert 'Apple Watch Ultra' in rv.data.decode('utf-8')

    def test_add_to_cart_if_item_is_already_in_cart(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.add_to_cart(1)
        rv = self.view_cart()
        assert '<span id="quantity">2</span>' in rv.data.decode('utf-8')

    def test_increase_quantity(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.view_cart()
        self.increase_cart_quantity(1)
        rv = self.view_cart()
        assert '<span id="quantity">2</span>' in rv.data.decode('utf-8')

    def test_decrease_quantity(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.add_to_cart(1)
        self.view_cart()
        self.decrease_cart_quantity(1)
        rv = self.view_cart()
        assert '<span id="quantity">1</span>' in rv.data.decode('utf-8')

    def test_remove_from_cart(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.view_cart()
        self.remove_from_cart(1)
        rv = self.view_cart()
        assert 'Your Cart is Empty' in rv.data.decode('utf-8')

    def test_remove_from_cart_with_multiple_items_in_cart(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.create_product("Xbox Series X", 20000, 500, "Microsoft Game Console", 'AppleWatch.jpg')
        self.add_to_cart(2)
        self.view_cart()
        self.remove_from_cart(1)
        rv = self.view_cart()
        assert 'Xbox Series X' in rv.data.decode('utf-8')

    def test_delete_customer(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.delete_customer(1)
        assert "The account" and "has been deleted" in rv.data.decode('utf-8')

    def test__access_denied_when_non_admin_attempts_to_delete_customer(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("test@test.com", "123456")
        rv = self.delete_customer(2)
        assert "Access Denied" in rv.data.decode('utf-8')

    def test_view_customers(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        rv = self.manage_customers()
        assert 'admin@admin.com' in rv.data.decode('utf-8')

    def test_access_denied_error_if_customer_attempts_to_access_manage_customers_page(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.login("test@test.com", "123456")
        rv = self.manage_customers()
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_place_order(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.add_to_cart(1)
        self.view_cart()
        rv = self.place_order()
        assert 'Order Placed Successfully' in rv.data.decode('utf-8')

    def test_error_raised_when_placing_order(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 1, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.add_to_cart(1)
        self.view_cart()
        rv = self.place_order()
        assert 'Order not placed' in rv.data.decode('utf-8')

    def test_view_my_orders(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.view_cart()
        self.place_order()
        rv = self.viewer_my_orders()
        assert '<p>Order Status: Pending</p>' in rv.data.decode('utf-8')

    def test_update_order_status(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.view_cart()
        self.place_order()
        rv = self.update_order(1, "Delivered")
        assert 'Order 1 Updated successfully' in rv.data.decode('utf-8')

    def test_update_order_status_with_no_status(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.add_to_cart(1)
        self.view_cart()
        self.place_order()
        rv = self.update_order(1, None)
        assert 'Order 1 not updated' in rv.data.decode('utf-8')

    def test_access_denied_when_non_admin_tries_to_view_all_orders(self):
        self.register("test", "test@test.com", "123456", "123456")
        self.login("test@test.com", "123456")
        rv = self.view_orders()
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_access_denied_when_non_admin_tried_to_update_an_order(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        self.logout()
        self.register("test", "test@test.com", "123456", "123456")
        self.login("test@test.com", "123456")
        self.add_to_cart(1)
        self.view_cart()
        self.place_order()
        rv = self.update_order(1, "Delivered")
        assert 'Access Denied' in rv.data.decode('utf-8')

    def test_search_when_found_matching_product(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.search("Apple Watch")
        assert 'Apple Watch Ultra' in rv.data.decode('utf-8')

    def test_search_when_found_no_matching_product(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        self.login("admin@admin.com", "123456")
        self.create_product("Apple Watch Ultra", 10000, 799.99, "Apple Smart Watch", 'AppleWatch.jpg')
        rv = self.search("Xbox")
        assert 'No Items Match your Search query' in rv.data.decode('utf-8')

    def test_search_route(self):
        rv = self.client.get("/search", follow_redirects=True)
        assert 'Search Page' in rv.data.decode('utf-8')
        assert rv.request.path == '/search'

    def test_dictionary_attack(self):
        self.register("admin", "admin@admin.com", "123456", "123456")
        rv = self.dictionary_attack()
        assert 'Password is 123456' in rv.data.decode('utf-8')

    def test_get_image(self):
        self.get_image('AppleWatch.jpg')
