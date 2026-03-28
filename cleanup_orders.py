# cleanup_orders.py - Run this to fix corrupted orders.json
import json
import os

ORDERS_FILE = 'orders.json'


def cleanup_orders():
    """Clean up corrupted orders.json file"""

    # Check if file exists
    if not os.path.exists(ORDERS_FILE):
        print("orders.json does not exist. Creating empty file...")
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        return

    try:
        # Try to load existing file
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print("orders.json is empty. Creating empty list...")
                with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
                return

            orders = json.loads(content)

            # Check if orders is a list
            if not isinstance(orders, list):
                print(f"orders.json contains {type(orders)} instead of list. Resetting...")
                orders = []

            # Clean each order
            cleaned_orders = []
            for i, order in enumerate(orders):
                if not isinstance(order, dict):
                    print(f"Order {i} is not a dictionary. Skipping...")
                    continue

                # Clean items
                if 'items' in order:
                    if not isinstance(order['items'], list):
                        print(f"Order {order.get('id', i)}: items is {type(order['items'])}, converting to list...")
                        order['items'] = []
                    else:
                        # Clean each item
                        cleaned_items = []
                        for item in order['items']:
                            if isinstance(item, dict):
                                # Ensure each item has required fields
                                cleaned_item = {
                                    'id': item.get('id', 0),
                                    'name': item.get('name', 'Unknown Product'),
                                    'price': item.get('price', 0),
                                    'quantity': item.get('quantity', 1),
                                    'image': item.get('image', '/static/images/default.jpg')
                                }
                                cleaned_items.append(cleaned_item)
                            else:
                                print(f"Order {order.get('id', i)}: item {item} is not a dict, skipping...")
                        order['items'] = cleaned_items
                else:
                    order['items'] = []

                # Ensure customer info exists
                if 'customer' not in order or not isinstance(order['customer'], dict):
                    order['customer'] = {
                        'name': 'Unknown',
                        'email': 'unknown@example.com',
                        'phone': '0000000000',
                        'address': 'No address provided'
                    }

                # Ensure required fields exist
                if 'id' not in order:
                    order['id'] = i + 1
                if 'order_date' not in order:
                    order['order_date'] = '2024-01-01 00:00:00'
                if 'total' not in order:
                    order['total'] = 0
                if 'status' not in order:
                    order['status'] = 'Pending'
                if 'payment_method' not in order:
                    order['payment_method'] = 'cash on delivery'

                cleaned_orders.append(order)

            # Save cleaned orders
            with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(cleaned_orders, f, indent=2, ensure_ascii=False)

            print(f"✅ Cleaned {len(cleaned_orders)} orders successfully!")

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print("Creating backup and resetting orders.json...")

        # Backup corrupted file
        backup_file = f"{ORDERS_FILE}.corrupted_backup"
        import shutil
        if os.path.exists(ORDERS_FILE):
            shutil.copy(ORDERS_FILE, backup_file)
            print(f"Backed up corrupted file to {backup_file}")

        # Create new empty orders file
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)

        print("✅ Created new empty orders.json")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Creating new empty orders.json...")
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)


if __name__ == '__main__':
    cleanup_orders()
    print("\nRun 'python app.py' to start the application")