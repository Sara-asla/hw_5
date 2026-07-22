import sys
import json
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
            raise InvalidIdException("Customer ID must be a non-negative integer.")
        self.id = id
        self.name = name
        self.city = city
        self.address = address

    def __repr__(self):
        return f"Customer(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"

class Supplier:
    """
    Represents a supplier in the Matamazon system.
    """
    def __init__(self, id, name, city, address):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Supplier ID must be a non-negative integer.")
        self.id = id
        self.name = name
        self.city = city
        self.address = address

    def __repr__(self):
        return f"Supplier(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"


class Product:
    """
    Represents a product sold on the Matamazon website.
    """
    def __init__(self, id, name, price, supplier_id, quantity):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Product ID must be a non-negative integer.")
        if not isinstance(supplier_id, int) or supplier_id < 0:
            raise InvalidIdException("Supplier ID must be a non-negative integer.")
        if not isinstance(quantity, int) or quantity < 0:
            raise InvalidIdException("Quantity must be a non-negative integer.")
        if not isinstance(price, (int, float)) or price < 0:
            raise InvalidPriceException("Price must be a non-negative number.")
        
        self.id = id
        self.name = name
        self.price = float(price)
        self.supplier_id = supplier_id
        self.quantity = quantity

    def __lt__(self, other):
        return self.price < other.price

    def __repr__(self):
        return f"Product(id={self.id}, name='{self.name}', price={self.price}, supplier_id={self.supplier_id}, quantity={self.quantity})"


class Order:
    """
    Represents a placed order.
    """
    def __init__(self, id, customer_id, product_id, quantity, total_price):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("Order ID must be a non-negative integer.")
        if not isinstance(customer_id, int) or customer_id < 0:
            raise InvalidIdException("Customer ID must be a non-negative integer.")
        if not isinstance(product_id, int) or product_id < 0:
            raise InvalidIdException("Product ID must be a non-negative integer.")
        if not isinstance(quantity, int) or quantity < 0:
            raise InvalidIdException("Quantity must be a non-negative integer.")
        if not isinstance(total_price, (int, float)) or total_price < 0:
            raise InvalidPriceException("Total price must be a non-negative number.")
        
        self.id = id
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = float(total_price)

    def __repr__(self):
        return f"Order(id={self.id}, customer_id={self.customer_id}, product_id={self.product_id}, quantity={self.quantity}, total_price={self.total_price})"


class MatamazonSystem:
    def __init__(self):
        self.customers = {}
        self.suppliers = {}
        self.products = {}
        self.orders = {}
        self.next_order_id = 1

    def register_entity(self, entity, is_customer):
        if is_customer:
            if entity.id in self.customers:
                raise InvalidIdException(f"Customer with ID {entity.id} already exists.")
            self.customers[entity.id] = entity
        else:
            if entity.id in self.suppliers:
                raise InvalidIdException(f"Supplier with ID {entity.id} already exists.")
            self.suppliers[entity.id] = entity

    def add_or_update_product(self, product):
        if product.supplier_id not in self.suppliers:
            raise InvalidIdException(f"Supplier ID {product.supplier_id} does not exist.")
        
        if product.id in self.products:
            existing_product = self.products[product.id]
            if existing_product.supplier_id != product.supplier_id:
                raise InvalidIdException("Product exists but belongs to a different supplier.")
            self.products[product.id] = product
        else:
            self.products[product.id] = product

    def place_order(self, customer_id, product_id, quantity=1):
        if customer_id not in self.customers:
            raise InvalidIdException("Customer does not exist.")
        if product_id not in self.products:
            return "The product does not exist in the system"
        
        product = self.products[product_id]
        if product.quantity < quantity:
            return "The quantity requested for this product is greater than the quantity in stock"
        
        product.quantity -= quantity
        total_price = product.price * quantity
        order = Order(self.next_order_id, customer_id, product_id, quantity, total_price)
        self.orders[self.next_order_id] = order
        self.next_order_id += 1
        
        return "The order has been accepted in the system"

    def remove_object(self, _id, class_type):
        if not isinstance(_id, int) or _id < 0:
            raise InvalidIdException("Invalid ID provided.")
            
        class_type = class_type.strip().lower()
        
        if class_type == "order":
            if _id not in self.orders:
                raise InvalidIdException("Order does not exist.")
            order = self.orders[_id]
            if order.product_id in self.products:
                self.products[order.product_id].quantity += order.quantity
            del self.orders[_id]
            return order.quantity

        for order in self.orders.values():
            if class_type == "customer" and order.customer_id == _id:
                raise InvalidIdException("Cannot remove Customer with existing orders.")
            if class_type == "product" and order.product_id == _id:
                raise InvalidIdException("Cannot remove Product with existing orders.")
            if class_type == "supplier":
                if order.product_id in self.products and self.products[order.product_id].supplier_id == _id:
                    raise InvalidIdException("Cannot remove Supplier with existing product orders.")

        if class_type == "customer":
            if _id not in self.customers:
                raise InvalidIdException("Customer does not exist.")
            del self.customers[_id]
        elif class_type == "supplier":
            if _id not in self.suppliers:
                raise InvalidIdException("Supplier does not exist.")
            del self.suppliers[_id]
        elif class_type == "product":
            if _id not in self.products:
                raise InvalidIdException("Product does not exist.")
            del self.products[_id]
        else:
            raise ValueError(f"Unknown class type: {class_type}")

    def search_products(self, query, max_price=None):
        results = []
        for p in self.products.values():
            if query in p.name and p.quantity > 0:
                if max_price is None or p.price <= max_price:
                    results.append(p)
        return sorted(results)

    def export_system_to_file(self, path):
        with open(path, 'w') as f:
            for c in self.customers.values():
                f.write(f"{c}\n")
            for s in self.suppliers.values():
                f.write(f"{s}\n")
            for p in self.products.values():
                f.write(f"{p}\n")

    def export_orders(self, out_file):
        output_dict = {}
        for order in self.orders.values():
            if order.product_id in self.products:
                sup_id = self.products[order.product_id].supplier_id
                if sup_id in self.suppliers:
                    city = self.suppliers[sup_id].city
                    if city not in output_dict:
                        output_dict[city] = []
                    output_dict[city].append(str(order))
        
        json.dump(output_dict, out_file)


def load_system_from_file(path):
    sys = MatamazonSystem()
    if not os.path.exists(path):
        return sys
        
    with open(path, 'r') as f:
        lines = f.readlines()
        
    parsed_objects = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = eval(line)
            parsed_objects.append(obj)
        except (SyntaxError, NameError):
            continue
            
    for obj in parsed_objects:
        if isinstance(obj, Customer):
            sys.register_entity(obj, True)
        elif isinstance(obj, Supplier):
            sys.register_entity(obj, False)
            
    for obj in parsed_objects:
        if isinstance(obj, Product):
            sys.add_or_update_product(obj)
            
    for obj in parsed_objects:
        if isinstance(obj, Order):
            sys.orders[obj.id] = obj
            if obj.id >= sys.next_order_id:
                sys.next_order_id = obj.id + 1
                
    return sys


def print_usage_and_exit():
    sys.stderr.write("Usage: python3 matamazon.py -l < matamazon_log > -s < matamazon_system > -o <output_file> -os <out_matamazon_system>\n")
    sys.exit(1)

def print_error_and_exit():
    print("The matamazon script has encountered an error")
    sys.exit(0)

def parse_args():
    args = {'-l': None, '-s': None, '-o': None, '-os': None}
    
    i = 1
    while i < len(sys.argv):
        flag = sys.argv[i]
        
        if flag == '-1': 
            flag = '-l'
        if flag == '-0': 
            flag = '-o'
            
        if flag in args:
            if i + 1 < len(sys.argv) and not sys.argv[i+1].startswith('-'):
                args[flag] = sys.argv[i+1]
                i += 2
            else:
                print_usage_and_exit()
        else:
            print_usage_and_exit()
            
    if not args['-l']:
        print_usage_and_exit()
        
    return args

def main():
    try:
        args = parse_args()
        
        if args['-s']:
            system = load_system_from_file(args['-s'])
        else:
            system = MatamazonSystem()

        with open(args['-l'], 'r') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if not line:
                    continue
                
                parts = line.split()
                cmd = parts[0]

                if cmd == 'register':
                    entity_type = parts[1].lower()
                    _id = int(parts[2])
                    name = parts[3].replace('_', ' ')
                    city = parts[4].replace('_', ' ')
                    address = parts[5].replace('_', ' ')
                    
                    if entity_type == 'customer':
                        system.register_entity(Customer(_id, name, city, address), True)
                    elif entity_type == 'supplier':
                        system.register_entity(Supplier(_id, name, city, address), False)
                        
                elif cmd == 'add' or cmd == 'update':
                    _id = int(parts[1])
                    name = parts[2].replace('_', ' ')
                    price = float(parts[3])
                    supplier_id = int(parts[4])
                    quantity = int(parts[5])
                    system.add_or_update_product(Product(_id, name, price, supplier_id, quantity))
                    
                elif cmd == 'order':
                    customer_id = int(parts[1])
                    product_id = int(parts[2])
                    quantity = int(parts[3]) if len(parts) > 3 else 1
                    system.place_order(customer_id, product_id, quantity)
                    
                elif cmd == 'remove':
                    class_type = parts[1]
                    _id = int(parts[2])
                    system.remove_object(_id, class_type)
                    
                elif cmd == 'search':
                    query = parts[1].replace('_', ' ')
                    max_price = float(parts[2]) if len(parts) > 2 else None
                    results = system.search_products(query, max_price)
                    print(results)

        if args['-o']:
            with open(args['-o'], 'w') as out_f:
                system.export_orders(out_f)
        else:
            system.export_orders(sys.stdout)
            print() 
            
        if args['-os']:
            system.export_system_to_file(args['-os'])

    except SystemExit:
        raise
    except Exception:
        print_error_and_exit()

if __name__ == "__main__":
    main()
