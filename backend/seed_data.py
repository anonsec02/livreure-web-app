#!/usr/bin/env python3
"""
Seed data script for Livreure platform
Creates sample data for testing and development
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.user import db
from src.models.customer import Customer, CustomerAddress
from src.models.restaurant import Restaurant, MenuItem
from src.models.delivery_agent import DeliveryAgent
from src.models.admin import Admin
from werkzeug.security import generate_password_hash

def create_sample_data():
    """Create sample data for the platform"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create sample customers
        print("Creating sample customers...")
        customers = [
            {
                'name': 'أحمد محمد',
                'email': 'ahmed@customer.mr',
                'password_hash': generate_password_hash('customer123'),
                'phone': '+22241234567'
            },
            {
                'name': 'فاطمة أحمد',
                'email': 'fatima@customer.mr',
                'password_hash': generate_password_hash('customer123'),
                'phone': '+22241234568'
            },
            {
                'name': 'محمد عبد الله',
                'email': 'mohamed@customer.mr',
                'password_hash': generate_password_hash('customer123'),
                'phone': '+22241234569'
            }
        ]
        
        for customer_data in customers:
            customer = Customer(**customer_data)
            db.session.add(customer)
        
        # Create sample restaurants
        print("Creating sample restaurants...")
        restaurants = [
            {
                'name': 'مطعم الصحراء',
                'email': 'sahara@restaurant.mr',
                'password_hash': generate_password_hash('restaurant123'),
                'phone': '+22241234570',
                'address': 'نواكشوط، الرياض',
                'description': 'مطعم متخصص في الأكلات الموريتانية التقليدية',
                'category': 'traditional',
                'is_open': True
            },
            {
                'name': 'برجر هاوس',
                'email': 'burger@restaurant.mr',
                'password_hash': generate_password_hash('restaurant123'),
                'phone': '+22241234571',
                'address': 'نواكشوط، تفرغ زينة',
                'description': 'أفضل البرجر والوجبات السريعة في نواكشوط',
                'category': 'fast_food',
                'is_open': True
            },
            {
                'name': 'بيتزا بالاس',
                'email': 'pizza@restaurant.mr',
                'password_hash': generate_password_hash('restaurant123'),
                'phone': '+22241234572',
                'address': 'نواكشوط، كرفور',
                'description': 'بيتزا إيطالية أصيلة بنكهة موريتانية',
                'category': 'pizza',
                'is_open': True
            },
            {
                'name': 'حلويات الأمل',
                'email': 'sweets@restaurant.mr',
                'password_hash': generate_password_hash('restaurant123'),
                'phone': '+22241234573',
                'address': 'نواكشوط، السوق المركزي',
                'description': 'أشهى الحلويات الشرقية والغربية',
                'category': 'desserts',
                'is_open': True
            },
            {
                'name': 'مقهى النخيل',
                'email': 'cafe@restaurant.mr',
                'password_hash': generate_password_hash('restaurant123'),
                'phone': '+22241234574',
                'address': 'نواكشوط، تيارت',
                'description': 'أفضل القهوة والمشروبات الساخنة والباردة',
                'category': 'drinks',
                'is_open': True
            }
        ]
        
        for restaurant_data in restaurants:
            restaurant = Restaurant(**restaurant_data)
            db.session.add(restaurant)
        
        db.session.commit()
        
        # Create sample menu items
        print("Creating sample menu items...")
        
        # Get restaurant IDs
        sahara = Restaurant.query.filter_by(email='sahara@restaurant.mr').first()
        burger_house = Restaurant.query.filter_by(email='burger@restaurant.mr').first()
        pizza_palace = Restaurant.query.filter_by(email='pizza@restaurant.mr').first()
        sweets = Restaurant.query.filter_by(email='sweets@restaurant.mr').first()
        cafe = Restaurant.query.filter_by(email='cafe@restaurant.mr').first()
        
        menu_items = [
            # Sahara Restaurant (Traditional)
            {
                'restaurant_id': sahara.id,
                'name': 'لحم مشوي مع الأرز',
                'description': 'لحم مشوي طازج مع الأرز الأبيض والخضار',
                'price': 1500.0,
                'category': 'main_dish',
                'is_available': True
            },
            {
                'restaurant_id': sahara.id,
                'name': 'كسكس باللحم',
                'description': 'كسكس تقليدي باللحم والخضار الطازجة',
                'price': 1200.0,
                'category': 'main_dish',
                'is_available': True
            },
            {
                'restaurant_id': sahara.id,
                'name': 'سمك مشوي',
                'description': 'سمك طازج مشوي مع الأرز والسلطة',
                'price': 1800.0,
                'category': 'main_dish',
                'is_available': True
            },
            
            # Burger House (Fast Food)
            {
                'restaurant_id': burger_house.id,
                'name': 'برجر كلاسيك',
                'description': 'برجر لحم بقري مع الخس والطماطم والجبن',
                'price': 800.0,
                'category': 'burger',
                'is_available': True
            },
            {
                'restaurant_id': burger_house.id,
                'name': 'برجر دجاج',
                'description': 'برجر دجاج مقرمش مع الصوص الخاص',
                'price': 700.0,
                'category': 'burger',
                'is_available': True
            },
            {
                'restaurant_id': burger_house.id,
                'name': 'بطاطس مقلية',
                'description': 'بطاطس مقلية ذهبية مقرمشة',
                'price': 300.0,
                'category': 'side',
                'is_available': True
            },
            
            # Pizza Palace
            {
                'restaurant_id': pizza_palace.id,
                'name': 'بيتزا مارجريتا',
                'description': 'بيتزا كلاسيكية بالطماطم والجبن والريحان',
                'price': 1000.0,
                'category': 'pizza',
                'is_available': True
            },
            {
                'restaurant_id': pizza_palace.id,
                'name': 'بيتزا بيبروني',
                'description': 'بيتزا بالبيبروني والجبن الموتزاريلا',
                'price': 1200.0,
                'category': 'pizza',
                'is_available': True
            },
            {
                'restaurant_id': pizza_palace.id,
                'name': 'بيتزا الخضار',
                'description': 'بيتزا بالخضار المشكلة والجبن',
                'price': 900.0,
                'category': 'pizza',
                'is_available': True
            },
            
            # Sweets
            {
                'restaurant_id': sweets.id,
                'name': 'كنافة بالجبن',
                'description': 'كنافة طازجة بالجبن والقطر',
                'price': 500.0,
                'category': 'dessert',
                'is_available': True
            },
            {
                'restaurant_id': sweets.id,
                'name': 'بقلاوة',
                'description': 'بقلاوة محشوة بالمكسرات والعسل',
                'price': 400.0,
                'category': 'dessert',
                'is_available': True
            },
            {
                'restaurant_id': sweets.id,
                'name': 'مهلبية',
                'description': 'مهلبية كريمية بالفستق',
                'price': 300.0,
                'category': 'dessert',
                'is_available': True
            },
            
            # Cafe
            {
                'restaurant_id': cafe.id,
                'name': 'قهوة عربية',
                'description': 'قهوة عربية أصيلة بالهيل',
                'price': 200.0,
                'category': 'hot_drink',
                'is_available': True
            },
            {
                'restaurant_id': cafe.id,
                'name': 'شاي أتاي',
                'description': 'شاي موريتاني تقليدي بالنعناع',
                'price': 150.0,
                'category': 'hot_drink',
                'is_available': True
            },
            {
                'restaurant_id': cafe.id,
                'name': 'عصير برتقال طازج',
                'description': 'عصير برتقال طبيعي 100%',
                'price': 250.0,
                'category': 'cold_drink',
                'is_available': True
            }
        ]
        
        for item_data in menu_items:
            menu_item = MenuItem(**item_data)
            db.session.add(menu_item)
        
        # Create sample delivery agents
        print("Creating sample delivery agents...")
        delivery_agents = [
            {
                'name': 'عبد الله أحمد',
                'email': 'abdullah@delivery.mr',
                'password_hash': generate_password_hash('delivery123'),
                'phone': '+22241234575',
                'vehicle_type': 'motorcycle',
                'license_number': 'DL001',
                'is_available': True
            },
            {
                'name': 'محمد ولد أحمد',
                'email': 'mohamed@delivery.mr',
                'password_hash': generate_password_hash('delivery123'),
                'phone': '+22241234576',
                'vehicle_type': 'bicycle',
                'license_number': 'DL002',
                'is_available': True
            },
            {
                'name': 'أحمد ولد محمد',
                'email': 'ahmed@delivery.mr',
                'password_hash': generate_password_hash('delivery123'),
                'phone': '+22241234577',
                'vehicle_type': 'car',
                'license_number': 'DL003',
                'is_available': False
            }
        ]
        
        for agent_data in delivery_agents:
            agent = DeliveryAgent(**agent_data)
            db.session.add(agent)
        
        # Create admin user
        print("Creating admin user...")
        admin = Admin(
            username='admin',
            full_name='مدير النظام',
            email='admin@livreure.mr',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        
        # Commit all changes
        db.session.commit()
        
        print("\n✅ Sample data created successfully!")
        print("\n📋 Test Accounts:")
        print("=" * 50)
        print("👤 Customer:")
        print("   Email: ahmed@customer.mr")
        print("   Password: customer123")
        print("\n🏪 Restaurant:")
        print("   Email: sahara@restaurant.mr")
        print("   Password: restaurant123")
        print("\n🏍️ Delivery Agent:")
        print("   Email: abdullah@delivery.mr")
        print("   Password: delivery123")
        print("\n👨‍💼 Admin:")
        print("   Email: admin@livreure.mr")
        print("   Password: admin123")
        print("=" * 50)

if __name__ == '__main__':
    create_sample_data()

