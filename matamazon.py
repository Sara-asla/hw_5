import sys
import json
import argparse
import os


class InvalidIdException(Exception):
    pass


class InvalidPriceException(Exception):
    pass


class Customer:
    """
    Represents a customer in the Matamazon system.
    """

    def __init__(self, id, name, city, address):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Invalid Customer ID. Must be a non-negative integer.")
        self.id = id
        self.name = name
        self.city = city
        self.address = address

    def __str__(self):
        return f"Customer(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"


class Supplier:
    """
    Represents a supplier in the Matamazon system.
    """

    def __init__(self, id, name, city, address):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Invalid Supplier ID. Must be a non-negative integer.")
        self.id = id
        self.name = name
        self.city = city
        self.address = address

    def __str__(self):
        return f"Supplier(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"


class Product:
    """
    Represents a product sold on the Matamazon website.
    """

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
    
    def __lt__(self, other):
        return self.price < other.price


class Order:
    """
    Represents a placed order.
    """

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


class MatamazonSystem:
    """
    Main system class that stores and manages customers, suppliers, products and orders.
    """

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

        if class_type == "Order":
            if _id not in self.orders:
                raise InvalidIdException(f"Order ID {_id} not found.")
            order = self.orders.pop(_id)
            if order.product_id in self.products:
                self.products[order.product_id].quantity += order.quantity
            return order.quantity

        elif class_type == "Customer":
            if _id not in self.customers:
                raise InvalidIdException(f"Customer ID {_id} not found.")
            for order in self.orders.values():
                if order.customer_id == _id:
                    raise InvalidIdException(f"Cannot remove Customer {_id}. Dependent orders exist.")
            self.customers.pop(_id)

        elif class_type == "Supplier":
            if _id not in self.suppliers:
                raise InvalidIdException(f"Supplier ID {_id} not found.")
            for product in self.products.values():
                if product.supplier_id == _id:
                    for order in self.orders.values():
                        if order.product_id == product.id:
                            raise InvalidIdException(f"Cannot remove Supplier {_id}. Dependent orders exist.")
            self.suppliers.pop(_id)

        elif class_type == "Product":
            if _id not in self.products:
                raise InvalidIdException(f"Product ID {_id} not found.")
            for order in self.orders.values():
                if order.product_id == _id:
                    raise InvalidIdException(f"Cannot remove Product {_id}. Dependent orders exist.")
            self.products.pop(_id)

        else:
            raise ValueError(f"Invalid class type: {class_type}")

    def search_products(self, query, max_price=None):
        results = []
        for product in self.products.values():
            if product.quantity > 0 and query in product.name:
                if max_price is None or product.price <= max_price:
                    results.append(product)
        return sorted(results)

    def export_system_to_file(self, path):
        with open(path, 'w') as f:
            for customer in self.customers.values():
                f.write(str(customer) + "\n")
            for supplier in self.suppliers.values():
                f.write(str(supplier) + "\n")
            for product in self.products.values():
                f.write(str(product) + "\n")

    def export_orders(self, out_file):
        city_orders = {}
        for order in self.orders.values():
            if order.product_id in self.products:
                supplier_id = self.products[order.product_id].supplier_id
                city = self.suppliers[supplier_id].city
                
                if city not in city_orders:
                    city_orders[city] = []
                city_orders[city].append(str(order))
                
        json.dump(city_orders, out_file)


def load_system_from_file(path):
    system = MatamazonSystem()
    if not path or not os.path.exists(path):
        return system
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                obj = eval(line) 
                if isinstance(obj, Customer):
                    system.register_entity(obj, True)
                elif isinstance(obj, Supplier):
                    system.register_entity(obj, False)
                elif isinstance(obj, Product):
                    system.add_or_update_product(obj)
            except Exception:
                pass
                
        return system
    except Exception as e:
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Matamazon System Script")
    parser.add_argument('-l', required=True, dest='matamazon_log', help="Log file with actions")
    parser.add_argument('-s', required=False, dest='matamazon_system', help="System file to load")
    parser.add_argument('-o', required=False, dest='output_file', help="Output JSON file for orders")
    parser.add_argument('-os', required=False, dest='out_matamazon_system', help="Output text file for system state")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)

    try:
        # Load System Safely
        if args.matamazon_system and os.path.exists(args.matamazon_system):
            system = load_system_from_file(args.matamazon_system)
        else:
            system = MatamazonSystem()

        # Parse and execute log
        if args.matamazon_log and os.path.exists(args.matamazon_log):
            with open(args.matamazon_log, 'r') as log_file:
                for line in log_file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    command = parts[0]

                    if command == 'register':
                        c_type, _id, name, city, address = parts[1], int(parts[2]), parts[3].replace('_', ' '), parts[4].replace('_', ' '), parts[5].replace('_', ' ')
                        if c_type == 'customer':
                            system.register_entity(Customer(_id, name, city, address), True)
                        elif c_type == 'supplier':
                            system.register_entity(Supplier(_id, name, city, address), False)

                    elif command == 'add' or command == 'update':
                        _id, name, price, supplier_id, qty = int(parts[1]), parts[2].replace('_', ' '), float(parts[3]), int(parts[4]), int(parts[5])
                        system.add_or_update_product(Product(_id, name, price, supplier_id, qty))

                    elif command == 'order':
                        customer_id, product_id = int(parts[1]), int(parts[2])
                        qty = int(parts[3]) if len(parts) > 3 else 1
                        system.place_order(customer_id, product_id, qty)

                    elif command == 'remove':
                        class_type, _id = parts[1], int(parts[2])
                        system.remove_object(_id, class_type)

                    elif command == 'search':
                        query = parts[1].replace('_', ' ')
                        max_price = float(parts[2]) if len(parts) > 2 else None
                        results = system.search_products(query, max_price)
                        print(f"[{', '.join(str(p) for p in results)}]")

        # Export Orders Output
        if args.output_file:
            with open(args.output_file, 'w') as out_f:
                system.export_orders(out_f)
        else:
            system.export_orders(sys.stdout)

        # Export System Output
        if args.out_matamazon_system:
            system.export_system_to_file(args.out_matamazon_system)

    except Exception:
        print("The matamazon script has encountered an error", file=sys.stderr)
        sys.exit(1)
