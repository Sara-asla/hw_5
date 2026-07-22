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
            self.customers.pop(_id)

        elif class_type == "supplier":
            if _id not in self.suppliers:
                raise InvalidIdException(f"Supplier ID {_id} not found.")
            for product in self.products.values():
                if product.supplier_id == _id:
                    for order in self.orders.values():
                        if order.product_id == product.id:
                            raise InvalidIdException(f"Cannot remove Supplier {_id}. Dependent orders exist.")
            self.suppliers.pop(_id)

        elif class_type == "product":
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
            
        customers = []
        suppliers = []
        products = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith(("Customer(", "Supplier(", "Product(", "Order(")):
                try:
                    obj = eval(line) 
                    if isinstance(obj, Customer):
                        customers.append(obj)
                    elif isinstance(obj, Supplier):
                        suppliers.append(obj)
                    elif isinstance(obj, Product):
                        products.append(obj)
                except Exception:
                    pass
                    
        for c in customers:
            system.register_entity(c, True)
        for s in suppliers:
            system.register_entity(s, False)
        for p in products:
            system.add_or_update_product(p)
                
        return system
    except Exception as e:
        raise e


if __name__ == '__main__':
    args = {
        'matamazon_log': None,
        'matamazon_system': None,
        'output_file': None,
        'out_matamazon_system': None
    }
    
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        flag = argv[i]
        val = argv[i+1] if i + 1 < len(argv) else None
        
        if flag == '-l' and val:
            args['matamazon_log'] = val
        elif flag == '-s' and val:
            args['matamazon_system'] = val
        elif flag == '-o' and val:
            args['output_file'] = val
        elif flag == '-os' and val:
            args['out_matamazon_system'] = val
        
        i += 2
        
    if args['matamazon_system'] and os.path.exists(args['matamazon_system']):
        system = load_system_from_file(args['matamazon_system'])
    else:
        system = MatamazonSystem()

    if args['matamazon_log'] and os.path.exists(args['matamazon_log']):
        with open(args['matamazon_log'], 'r') as log_file:
            for line in log_file:
                line = line.split('#')[0].strip()
                if not line:
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                command = parts[0].strip().lower()

                if command == 'register':
                    c_type = parts[1].strip().lower()
                    _id = int(parts[2])
                    name = parts[3].replace('_', ' ')
                    city = parts[4].replace('_', ' ')
                    address = parts[5].replace('_', ' ')
                    if c_type == 'customer':
                        system.register_entity(Customer(_id, name, city, address), True)
                    elif c_type == 'supplier':
                        system.register_entity(Supplier(_id, name, city, address), False)

                elif command == 'add' or command == 'update':
                    _id = int(parts[1])
                    name = parts[2].replace('_', ' ')
                    price = float(parts[3])
                    supplier_id = int(parts[4])
                    qty = int(parts[5])
                    system.add_or_update_product(Product(_id, name, price, supplier_id, qty))

                elif command == 'order':
                    customer_id = int(parts[1])
                    product_id = int(parts[2])
                    qty = int(parts[3]) if len(parts) > 3 else 1
                    system.place_order(customer_id, product_id, qty)

                elif command == 'remove':
                    class_type = parts[1].strip()
                    _id = int(parts[2])
                    system.remove_object(_id, class_type)

                elif command == 'search':
                    query = parts[1].replace('_', ' ')
                    max_price = float(parts[2]) if len(parts) > 2 else None
                    results = system.search_products(query, max_price)
                    print(f
