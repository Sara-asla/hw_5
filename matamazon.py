import sys
import json
import os


class InvalidIdException(Exception):
    pass


class InvalidPriceException(Exception):
    pass


class Customer:
    def __init__(self, id, name, city, address):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Invalid Customer ID. Must be a non-negative integer.")
        self.id = id
        self.name = name
        self.city = city
        self.address = address

    def __str__(self):
        return f"Customer(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"

    def __repr__(self):
        return self.__str__()


class Supplier:
    def __init__(self, id, name, city, address):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Invalid Supplier ID. Must be a non-negative integer.")
        self.id = id
        self.name = name
        self.city = city
        self.address = address

    def __str__(self):
        return f"Supplier(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"

    def __repr__(self):
        return self.__str__()


class Product:
    def __init__(self, id, name, price, supplier_id, quantity):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Invalid Product ID.")
        if not isinstance(supplier_id, int) or supplier_id < 0:
            raise InvalidIdException("Invalid Supplier ID.")
        if not isinstance(quantity, int) or quantity < 0:
            raise InvalidIdException("Invalid Quantity.")
        if not isinstance(price, (int, float)) or price < 0:
            raise InvalidPriceException("Invalid Price. Must be non-negative.")

        self.id = id
        self.name = name
        self.price = price
        self.supplier_id = supplier_id
        self.quantity = quantity

    def __str__(self):
        return f"Product(id={self.id}, name='{self.name}', price={self.price}, supplier_id={self.supplier_id}, quantity={self.quantity})"
    
    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.price < other.price


class Order:
    def __init__(self, id, customer_id, product_id, quantity, total_price):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Invalid Order ID.")
        if not isinstance(customer_id, int) or customer_id < 0:
            raise InvalidIdException("Invalid Customer ID.")
        if not isinstance(product_id, int) or product_id < 0:
            raise InvalidIdException("Invalid Product ID.")
        if not isinstance(quantity, int) or quantity < 0:
            raise InvalidIdException("Invalid Quantity.")
        if not isinstance(total_price, (int, float)) or total_price < 0:
            raise InvalidPriceException("Invalid Total Price.")

        self.id = id
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price

    def __str__(self):
        return f"Order(id={self.id}, customer_id={self.customer_id}, product_id={self.product_id}, quantity={self.quantity}, total_price={self.total_price})"

    def __repr__(self):
        return self.__str__()


class MatamazonSystem:
    def __init__(self):
        self.customers = {}
        self.suppliers = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1

    def register_entity(self, entity, is_customer):
        if entity.id in self.customers or entity.id in self.suppliers:
            raise InvalidIdException(f"ID {entity.id} already exists in the system.")
        
        if is_customer:
            self.customers[entity.id] = entity
        else:
            self.suppliers[entity.id] = entity

    def add_or_update_product(self, product):
        if product.supplier_id not in self.suppliers:
            raise InvalidIdException(f"Supplier ID {product.supplier_id} does not exist.")
        
        if product.id in self.products:
            if self.products[product.id].supplier_id != product.supplier_id:
                raise InvalidIdException(f"Product ID {product.id} belongs to a different supplier.")
            
        self.products[product.id] = product

    def place_order(self, customer_id, product_id, quantity=1):
        if customer_id not in self.customers:
            raise InvalidIdException(f"Customer ID {customer_id} does not exist.")
        if product_id not in self.products:
            return "The product does not exist in the system"
            
        product = self.products[product_id]
        
        if quantity > product.quantity:
            return "The product does not exist in the system. The quantity requested for this product is greater than the quantity in stock"
            
        product.quantity -= quantity
        total_price = product.price * quantity
        new_order = Order(self.next_order_id, customer_id, product_id, quantity, total_price)
        
        self.orders[self.next_order_id] = new_order
        self.next_order_id += 1
        
        return "The order has been accepted in the system"

    def remove_object(self, _id, class_type):
        if not isinstance(_id, int) or _id < 0:
            raise InvalidIdException("Invalid ID.")

        class_type = class_type.strip().lower()

        if class_type == "order":
            if _id not in self.orders:
                raise InvalidIdException(f"Order ID {_id} not found.")
            order = self.orders.pop(_id)
            if order.product_id in self.products:
                self.products[order.product_id].quantity += order.quantity
            return order.quantity

        elif class_type == "customer":
            if _id not in self.customers:
                raise InvalidIdException(f"Customer ID {_id} not found.")
            for order in self.orders.values():
                if order.customer_id == _id:
                    raise InvalidIdException(f"Cannot remove Customer {_id}. Dependent orders exist.")
            self.customers.pop(_id
