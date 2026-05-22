import os
import sys
import random
import datetime
from decimal import Decimal
from faker import Faker
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clothing_erp.settings')
django.setup()

# Now import Django models
from apps.core.models import Currency
from apps.inventory.models import (
    Category, Size, Color, Brand, Season, Product,
    ProductVariant, Warehouse, InventoryMovement
)
from apps.sales.models import Customer, Order, OrderItem
from apps.purchase.models import Supplier, PurchaseOrder, PurchaseOrderItem
from apps.finance.models import Invoice, Payment, Expense
from apps.hr.models import Department, Position, Employee, Attendance, Salary
from apps.settings.models import CompanyInfo, SystemSetting
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django_countries import countries
from django.db import transaction

fake = Faker('uz_UZ')  # Using Uzbek locale
Faker.seed(2025)  # For reproducible results

# Sample data
COLORS = [
    ('Qora', '#000000'),
    ('Oq', '#FFFFFF'),
    ('Qizil', '#FF0000'),
    ('Ko\'k', '#0000FF'),
    ('Yashil', '#00FF00'),
    ('Sariq', '#FFFF00'),
    ('Pushti', '#FFC0CB'),
    ('Jigarrang', '#A52A2A'),
    ('Kulrang', '#808080'),
    ('To\'q ko\'k', '#000080'),
]

SIZES = [
    ('XS', 'XS'),
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('XXL', 'XXL'),
    ('36', '36'),
    ('38', '38'),
    ('40', '40'),
    ('42', '42'),
    ('44', '44'),
    ('46', '46'),
]

CATEGORIES = [
    'Ko\'ylaklar',
    'Shimlar',
    'Futbolkalar',
    'Kurtka & Palto',
    'Kostyumlar',
    'Jinslar',
    'Sport kiyimlari',
    'Ichki kiyimlar',
    'Pijamalar',
    'Aksessuarlar',
    'Bosh kiyimlar',
    'Oyoq kiyimlar',
]

SUBCATEGORIES = {
    'Ko\'ylaklar': ['Klassik', 'Casual', 'Biznes', 'Chiziqli'],
    'Shimlar': ['Klassik', 'Casual', 'Sport', 'Jins'],
    'Futbolkalar': ['Polo', 'Yozgi', 'Uzun yengli', 'Sport'],
    'Kurtka & Palto': ['Qishki', 'Kuzgi', 'Yengil', 'Yomg\'irga'],
    'Sport kiyimlari': ['Tolstovka', 'Sport shimlar', 'Sport kostyumlar'],
}

BRANDS = [
    ('UzTextile', 'O\'zbekistonda ishlab chiqarilgan yuqori sifatli matolar'),
    ('SilkRoad', 'Ipak yo\'lidan ilhomlangan dizaynlar'),
    ('TashkentStyle', 'Zamonaviy shaharlarga mos kiyimlar'),
    ('SamarkandFashion', 'Sharqona dizaynlar'),
    ('BukharaCraft', 'An\'anaviy naqshlardan ilhomlangan'),
    ('UzDenim', 'O\'zbekistonda ishlab chiqarilgan jins mahsulotlar'),
    ('CottonWay', 'Yuqori sifatli paxta mahsulotlari'),
    ('NamStyle', 'Zamonaviy milliy kiyimlar'),
    ('AndijanFashion', 'Vodiycha uslubdagi kiyimlar'),
    ('FerganaTextile', 'Vodiyning eng yaxshi matolaridan'),
]

SEASONS = ['Bahor', 'Yoz', 'Kuz', 'Qish', 'Yil bo\'yi']

DEPARTMENTS = [
    'Sotuvlar',
    'Marketing',
    'Ishlab chiqarish',
    'Ombor',
    'Moliya',
    'HR',
    'IT'
]

POSITIONS = {
    'Sotuvlar': ['Sotuv menejeri', 'Sotuv vakili', 'Mijozlar xizmati'],
    'Marketing': ['Marketing menejeri', 'Ijtimoiy media mutaxassisi', 'Dizayner'],
    'Ishlab chiqarish': ['Ishlab chiqarish menejeri', 'Tikuvchi', 'Sifat nazorati'],
    'Ombor': ['Ombor menejeri', 'Ombor xodimi', 'Logistika mutaxassisi'],
    'Moliya': ['Moliya menejeri', 'Hisobchi', 'Kassir'],
    'HR': ['HR menejeri', 'Xodimlar bo\'yicha mutaxassis', 'Trener'],
    'IT': ['IT menejeri', 'Dasturchi', 'Tizim administratori']
}


class DataGenerator:
    def __init__(self):
        self.current_date = timezone.now().date()

        # Track created objects for relationship creation
        self.categories = {}
        self.sizes = {}
        self.colors = {}
        self.brands = {}
        self.seasons = {}
        self.products = []
        self.product_variants = []
        self.warehouses = []
        self.customers = []
        self.suppliers = []
        self.employees = {}
        self.departments = {}
        self.positions = {}
        self.orders = []
        self.purchase_orders = []

    @transaction.atomic
    def generate_all(self):
        self.generate_users(3)
        self.generate_company_info()
        self.generate_system_settings()
        self.generate_currencies()
        self.generate_categories()
        self.generate_sizes()
        self.generate_colors()
        self.generate_brands()
        self.generate_seasons()
        self.generate_warehouses(3)
        self.generate_departments()
        self.generate_positions()
        self.generate_employees(30)
        self.generate_products(50)
        self.generate_product_variants()
        self.generate_customers(20)
        self.generate_suppliers(10)
        self.generate_orders(30)
        self.generate_purchase_orders(15)
        self.generate_inventory_movements()
        self.generate_invoices()
        self.generate_payments()
        self.generate_expenses(20)
        self.generate_attendance()
        self.generate_salaries()

        print("All data has been successfully generated!")

    def generate_users(self, count):
        print("Generating users...")

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
            print("Superuser 'admin' created with password 'admin12345'")

        # Create regular users
        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{i + 1}"

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="password123",
                    first_name=first_name,
                    last_name=last_name
                )
                print(f"User '{username}' created with password 'password123'")

    def generate_company_info(self):
        print("Generating company info...")

        if not CompanyInfo.objects.exists():
            CompanyInfo.objects.create(
                name="Kiyim-Kechak Ulgurji Savdo",
                legal_name="'Kiyim-Kechak Ulgurji Savdo' MChJ",
                tax_number="123456789",
                registration_number="UZ987654321",
                address=fake.address(),
                city="Toshkent",
                zip_code="100000",
                country="O'zbekiston",
                phone=fake.phone_number(),
                email="info@kiyimulgurji.uz",
                website="https://kiyimulgurji.uz",
                bank_name="O'zsanoatqurilishbank",
                bank_account="12345678901234567890",
                bank_code="00987"
            )

    def generate_system_settings(self):
        print("Generating system settings...")

        settings_data = [
            {
                'key': 'company_currency',
                'name': 'Asosiy valyuta',
                'description': 'Tizimda ishlatiladigan asosiy valyuta',
                'value_type': 'text',
                'value_text': 'UZS',
            },
            {
                'key': 'tax_rate',
                'name': 'QQS stavkasi',
                'description': 'Standart qo\'shilgan qiymat solig\'i stavkasi',
                'value_type': 'number',
                'value_number': 15.0,
            },
            {
                'key': 'low_stock_threshold',
                'name': 'Kam zaxira chegarasi',
                'description': 'Mahsulot kam qolgan deb hisoblanadigan miqdor',
                'value_type': 'number',
                'value_number': 10,
            },
            {
                'key': 'enable_customer_notifications',
                'name': 'Mijoz bildirishnomalari',
                'description': 'Mijozlarga bildirishnomalar yuborish',
                'value_type': 'boolean',
                'value_boolean': True,
            },
        ]

        for setting_data in settings_data:
            if not SystemSetting.objects.filter(key=setting_data['key']).exists():
                setting = SystemSetting(
                    key=setting_data['key'],
                    name=setting_data['name'],
                    description=setting_data['description'],
                    value_type=setting_data['value_type']
                )

                if setting_data['value_type'] == 'text':
                    setting.value_text = setting_data['value_text']
                elif setting_data['value_type'] == 'number':
                    setting.value_number = setting_data['value_number']
                elif setting_data['value_type'] == 'boolean':
                    setting.value_boolean = setting_data['value_boolean']

                setting.save()

    def generate_currencies(self):
        print("Generating currencies...")

        currencies_data = [
            {
                'code': 'UZS',
                'name': "O'zbek so'mi",
                'symbol': "so'm",
                'is_default': True
            },
            {
                'code': 'USD',
                'name': "AQSh dollari",
                'symbol': "$",
                'is_default': False
            },
            {
                'code': 'EUR',
                'name': "Yevro",
                'symbol': "€",
                'is_default': False
            }
        ]

        for currency_data in currencies_data:
            Currency.objects.get_or_create(
                code=currency_data['code'],
                defaults={
                    'name': currency_data['name'],
                    'symbol': currency_data['symbol'],
                    'is_default': currency_data['is_default']
                }
            )

    def generate_categories(self):
        print("Generating categories...")

        # Main categories
        main_categories = {}
        for category_name in CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': fake.sentence()}
            )
            main_categories[category_name] = category
            self.categories[category_name] = category

        # Subcategories
        for main_cat, subcats in SUBCATEGORIES.items():
            main_category = main_categories.get(main_cat)
            if main_category:
                for subcat_name in subcats:
                    full_name = f"{main_cat} - {subcat_name}"
                    subcat, created = Category.objects.get_or_create(
                        name=subcat_name,
                        parent=main_category,
                        defaults={'description': fake.sentence()}
                    )
                    self.categories[full_name] = subcat

    def generate_sizes(self):
        print("Generating sizes...")

        for code, name in SIZES:
            size, created = Size.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            self.sizes[code] = size

    def generate_colors(self):
        print("Generating colors...")

        for name, code in COLORS:
            color, created = Color.objects.get_or_create(
                name=name,
                defaults={'color_code': code}
            )
            self.colors[name] = color

    def generate_brands(self):
        print("Generating brands...")

        for name, description in BRANDS:
            brand, created = Brand.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            self.brands[name] = brand

    def generate_seasons(self):
        print("Generating seasons...")

        for name in SEASONS:
            season, created = Season.objects.get_or_create(name=name)
            self.seasons[name] = season

    def generate_warehouses(self, count):
        print("Generating warehouses...")

        # Main warehouse
        main_warehouse, created = Warehouse.objects.get_or_create(
            name="Markaziy ombor",
            defaults={
                'address': fake.address(),
                'is_main': True
            }
        )
        self.warehouses.append(main_warehouse)

        # Additional warehouses
        for i in range(1, count):
            warehouse, created = Warehouse.objects.get_or_create(
                name=f"Ombor {i}",
                defaults={
                    'address': fake.address(),
                    'is_main': False
                }
            )
            self.warehouses.append(warehouse)

    def generate_departments(self):
        print("Generating departments...")

        for dept_name in DEPARTMENTS:
            dept, created = Department.objects.get_or_create(
                name=dept_name,
                defaults={'description': fake.sentence()}
            )
            self.departments[dept_name] = dept

    def generate_positions(self):
        print("Generating positions...")

        for dept_name, positions in POSITIONS.items():
            department = self.departments.get(dept_name)
            if department:
                for pos_name in positions:
                    position, created = Position.objects.get_or_create(
                        name=pos_name,
                        department=department,
                        defaults={'description': fake.sentence()}
                    )
                    key = f"{dept_name} - {pos_name}"
                    self.positions[key] = position

    def generate_employees(self, count):
        print(f"Generating {count} employees...")

        for i in range(count):
            dept_name = random.choice(list(DEPARTMENTS))
            department = self.departments.get(dept_name)

            if department:
                # Get a random position for this department
                available_positions = [p for p in self.positions.values()
                                       if p.department == department]

                if available_positions:
                    position = random.choice(available_positions)

                    gender = random.choice(['male', 'female'])
                    first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female()
                    last_name = fake.last_name_male() if gender == 'male' else fake.last_name_female()

                    # Generate a hire date from 5 years ago to now
                    hire_date = fake.date_between(start_date='-5y', end_date='today')

                    # Generate a birth date (25-55 years old)
                    birth_date = fake.date_of_birth(minimum_age=25, maximum_age=55)

                    # Base salary for the position
                    base_salary = Decimal(random.randint(300, 1000) * 10000)

                    employee = Employee.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        middle_name=fake.first_name(),
                        position=position,
                        department=department,
                        hire_date=hire_date,
                        birth_date=birth_date,
                        gender=gender,
                        email=fake.email(),
                        phone=fake.phone_number(),
                        address=fake.address(),
                        city=fake.city(),
                        country=random.choice(list(dict(countries).keys())),
                        passport_number=fake.bothify(text='??#######'),
                        tax_id=fake.bothify(text='##########'),
                        base_salary=base_salary,
                        is_active=True,
                        notes=fake.paragraph(nb_sentences=3)
                    )

                    key = f"{dept_name} - {i}"
                    self.employees[key] = employee

                    # Set department manager for some departments
                    if i < len(DEPARTMENTS) and not department.manager:
                        department.manager = employee
                        department.save()

    def generate_products(self, count):
        print(f"Generating {count} products...")

        for i in range(count):
            # Get a random main category and subcategory if available
            main_cat_name = random.choice(list(CATEGORIES))
            main_category = self.categories.get(main_cat_name)

            # Choose subcategory if available, otherwise use main category
            category = main_category
            if main_cat_name in SUBCATEGORIES and SUBCATEGORIES[main_cat_name]:
                subcat_name = random.choice(SUBCATEGORIES[main_cat_name])
                full_name = f"{main_cat_name} - {subcat_name}"
                if full_name in self.categories:
                    category = self.categories[full_name]

            # Get a random brand
            brand = random.choice(list(self.brands.values()))

            # Get a random season
            season = random.choice(list(self.seasons.values()))

            # Generate cost and wholesale prices
            cost_price = Decimal(random.randint(5000, 100000))
            markup = Decimal(random.uniform(1.3, 2.5))
            wholesale_price = (cost_price * markup).quantize(Decimal('0.01'))

            # Create product code: category prefix + random number
            code = f"{main_cat_name[:3].upper()}-{random.randint(1000, 9999)}"

            # Create the product name
            adjectives = ["Klassik", "Zamonaviy", "Premium", "Comfort", "Sport", "Urban"]
            product_name = f"{random.choice(adjectives)} {main_cat_name}"

            product = Product.objects.create(
                code=code,
                name=product_name,
                description=fake.paragraph(),
                category=category,
                brand=brand,
                season=season,
                cost_price=cost_price,
                wholesale_price=wholesale_price,
                is_active=True
            )

            self.products.append(product)

    def generate_product_variants(self):
        print("Generating product variants...")

        # Track used SKUs to avoid duplicates
        used_skus = set()

        for product in self.products:
            # Determine how many variants to create for this product
            num_variants = random.randint(3, 8)

            # Get some random colors and sizes
            variant_colors = random.sample(list(self.colors.values()), min(3, len(self.colors)))
            variant_sizes = random.sample(list(self.sizes.values()), min(4, len(self.sizes)))

            # Generate variants
            for color in variant_colors:
                for size in variant_sizes:
                    # Not all combinations will be created
                    if random.random() > 0.7:
                        continue

                    # Create SKU: product code + color + size + random number to ensure uniqueness
                    base_sku = f"{product.code}-{color.name[:1]}-{size.code}"
                    sku = base_sku

                    # If the SKU already exists, add a random number to make it unique
                    count = 1
                    while sku in used_skus:
                        sku = f"{base_sku}-{count}"
                        count += 1

                    used_skus.add(sku)

                    # Generate random stock quantity
                    stock_quantity = random.randint(0, 100)

                    variant = ProductVariant.objects.create(
                        product=product,
                        color=color,
                        size=size,
                        sku=sku,
                        stock_quantity=stock_quantity
                    )

                    self.product_variants.append(variant)

    def generate_customers(self, count):
        print(f"Generating {count} customers...")

        for i in range(count):
            # Mix of individual and company customers
            is_company = random.choice([True, False])

            if is_company:
                name = fake.company()
                contact_person = f"{fake.first_name()} {fake.last_name()}"
            else:
                name = f"{fake.first_name()} {fake.last_name()}"
                contact_person = ""

            customer = Customer.objects.create(
                name=name,
                contact_person=contact_person,
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address(),
                city=fake.city(),
                country=random.choice(list(dict(countries).keys())),
                tax_number=fake.bothify(text='##########') if is_company else "",
                is_active=True,
                notes=fake.paragraph(nb_sentences=2) if random.random() > 0.7 else ""
            )

            self.customers.append(customer)

    def generate_suppliers(self, count):
        print(f"Generating {count} suppliers...")

        for i in range(count):
            supplier = Supplier.objects.create(
                name=fake.company(),
                contact_person=f"{fake.first_name()} {fake.last_name()}",
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address(),
                city=fake.city(),
                country=random.choice(list(dict(countries).keys())),
                tax_number=fake.bothify(text='##########'),
                is_active=True,
                notes=fake.paragraph(nb_sentences=2) if random.random() > 0.7 else ""
            )

            self.suppliers.append(supplier)

    def generate_orders(self, count):
        print(f"Generating {count} orders...")

        status_options = ['draft', 'confirmed', 'processing', 'ready', 'shipped', 'delivered', 'cancelled']
        status_weights = [0.05, 0.15, 0.2, 0.15, 0.2, 0.2, 0.05]

        # Generate orders for the past year
        start_date = self.current_date - datetime.timedelta(days=365)

        for i in range(count):
            # Generate order data
            customer = random.choice(self.customers)
            warehouse = random.choice(self.warehouses)

            # Generate a random date from the past year to now
            order_date = fake.date_between(start_date=start_date, end_date=self.current_date)

            # Generate a random status based on weighted distribution
            status = random.choices(status_options, weights=status_weights)[0]

            # Calculate estimated delivery based on order date and status
            if status in ['draft', 'confirmed']:
                estimate_days = random.randint(5, 15)
                estimated_delivery = order_date + datetime.timedelta(days=estimate_days)
            elif status in ['processing', 'ready']:
                estimate_days = random.randint(1, 7)
                estimated_delivery = order_date + datetime.timedelta(days=estimate_days)
            elif status in ['shipped', 'delivered']:
                estimate_days = random.randint(1, 5)
                estimated_delivery = order_date + datetime.timedelta(days=estimate_days)
            else:
                estimated_delivery = None

            # Create order number
            order_number = f"OR-{order_date.strftime('%y%m')}-{i + 1:04d}"

            order = Order.objects.create(
                number=order_number,
                customer=customer,
                order_date=order_date,
                status=status,
                warehouse=warehouse,
                shipping_address=customer.address,
                notes=fake.paragraph(nb_sentences=1) if random.random() > 0.7 else "",
                estimated_delivery=estimated_delivery,
                subtotal=Decimal('0'),
                discount=Decimal(random.randint(0, 15)),
                tax=Decimal(random.randint(0, 15)),
                shipping_cost=Decimal(random.randint(0, 50000)),
                total=Decimal('0')
            )

            # Add order items
            num_items = random.randint(1, 5)
            order_variants = random.sample(self.product_variants, min(num_items, len(self.product_variants)))

            subtotal = Decimal('0')
            for variant in order_variants:
                # Random quantity between 1 and 10
                quantity = random.randint(1, 10)

                # Use the product's wholesale price with some variation
                price_variation = Decimal(random.uniform(0.95, 1.15))
                unit_price = (variant.product.wholesale_price * price_variation).quantize(Decimal('0.01'))

                # Random discount percentage
                discount_percent = Decimal(random.randint(0, 10))

                # Calculate total price
                total_price = ((unit_price * (1 - discount_percent / 100)) * quantity).quantize(Decimal('0.01'))

                OrderItem.objects.create(
                    order=order,
                    product_variant=variant,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_percent=discount_percent,
                    total_price=total_price
                )

                subtotal += total_price

            # Update order totals
            order.subtotal = subtotal
            order.total = (subtotal - (subtotal * order.discount / 100) + (
                        subtotal * order.tax / 100) + order.shipping_cost).quantize(Decimal('0.01'))
            order.save()

            self.orders.append(order)

    def generate_purchase_orders(self, count):
        print(f"Generating {count} purchase orders...")

        status_options = ['draft', 'sent', 'confirmed', 'partially_received', 'received', 'cancelled']
        status_weights = [0.1, 0.1, 0.2, 0.2, 0.3, 0.1]

        # Generate purchase orders for the past year
        start_date = self.current_date - datetime.timedelta(days=365)

        for i in range(count):
            # Generate purchase order data
            supplier = random.choice(self.suppliers)
            warehouse = random.choice(self.warehouses)

            # Generate a random date from the past year to now
            order_date = fake.date_between(start_date=start_date, end_date=self.current_date)

            # Generate a random status based on weighted distribution
            status = random.choices(status_options, weights=status_weights)[0]

            # Calculate expected delivery date
            expected_date = order_date + datetime.timedelta(days=random.randint(7, 30))

            # Create purchase order number
            po_number = f"PO-{order_date.strftime('%y%m')}-{i + 1:04d}"

            purchase_order = PurchaseOrder.objects.create(
                number=po_number,
                supplier=supplier,
                order_date=order_date,
                status=status,
                warehouse=warehouse,
                expected_date=expected_date,
                notes=fake.paragraph(nb_sentences=1) if random.random() > 0.7 else "",
                subtotal=Decimal('0'),
                discount=Decimal(random.randint(0, 10)),
                tax=Decimal(random.randint(0, 15)),
                shipping_cost=Decimal(random.randint(0, 50000)),
                total=Decimal('0')
            )

            # Add purchase order items
            num_items = random.randint(1, 8)
            order_products = random.sample(self.products, min(num_items, len(self.products)))

            subtotal = Decimal('0')
            for product in order_products:
                # Find a variant of this product
                product_variants = ProductVariant.objects.filter(product=product)
                if product_variants.exists():
                    variant = random.choice(product_variants)

                    # Random quantity between 10 and 100
                    quantity = random.randint(10, 100)

                    # Use the product's cost price with some variation
                    price_variation = Decimal(random.uniform(0.9, 1.05))
                    unit_price = (product.cost_price * price_variation).quantize(Decimal('0.01'))

                    # Calculate total price
                    total_price = (unit_price * quantity).quantize(Decimal('0.01'))

                    # For received or partially received orders, set received quantity
                    if status == 'received':
                        received_quantity = quantity
                    elif status == 'partially_received':
                        received_quantity = random.randint(0, quantity)
                    else:
                        received_quantity = 0

                    PurchaseOrderItem.objects.create(
                        purchase_order=purchase_order,
                        product_variant=variant,
                        quantity=quantity,
                        unit_price=unit_price,
                        received_quantity=received_quantity,
                        total_price=total_price
                    )

                    subtotal += total_price

            # Update purchase order totals
            purchase_order.subtotal = subtotal
            purchase_order.total = (subtotal - (subtotal * purchase_order.discount / 100) + (
                        subtotal * purchase_order.tax / 100) + purchase_order.shipping_cost).quantize(Decimal('0.01'))
            purchase_order.save()

            self.purchase_orders.append(purchase_order)

    def generate_inventory_movements(self):
        print("Generating inventory movements...")

        # Generate movements based on orders
        for order in self.orders:
            # Only create movements for orders past confirmed status
            if order.status not in ['draft', 'confirmed']:
                # Get all order items
                order_items = OrderItem.objects.filter(order=order)

                for item in order_items:
                    # Create movement for confirmed orders
                    movement_type = 'out'
                    reference = f"Order #{order.number}"

                    InventoryMovement.objects.create(
                        product_variant=item.product_variant,
                        warehouse=order.warehouse,
                        movement_type=movement_type,
                        quantity=item.quantity,
                        reference=reference,
                        notes=f"Outgoing stock for order {order.number}"
                    )

        # Generate movements based on purchase orders
        for po in self.purchase_orders:
            # Only create movements for received or partially received orders
            if po.status in ['received', 'partially_received']:
                # Get all purchase order items
                po_items = PurchaseOrderItem.objects.filter(purchase_order=po)

                for item in po_items:
                    # Only create movement if there are received items
                    if item.received_quantity > 0:
                        movement_type = 'in'
                        reference = f"PO #{po.number}"

                        InventoryMovement.objects.create(
                            product_variant=item.product_variant,
                            warehouse=po.warehouse,
                            movement_type=movement_type,
                            quantity=item.received_quantity,
                            reference=reference,
                            notes=f"Incoming stock from purchase order {po.number}"
                        )

        # Generate some random inventory adjustments
        for i in range(20):
            variant = random.choice(self.product_variants)
            warehouse = random.choice(self.warehouses)
            movement_type = random.choice(['adjustment', 'transfer'])
            quantity = random.randint(1, 10)

            if movement_type == 'adjustment':
                reference = "Inventory audit"
                notes = "Inventory adjustment after physical count"
            else:
                reference = f"Transfer to {random.choice(self.warehouses).name}"
                notes = "Stock transfer between warehouses"

            InventoryMovement.objects.create(
                product_variant=variant,
                warehouse=warehouse,
                movement_type=movement_type,
                quantity=quantity,
                reference=reference,
                notes=notes
            )

    def generate_invoices(self):
        print("Generating invoices...")

        # Default currency
        uzs_currency = Currency.objects.get(code='UZS')

        # Generate sales invoices from orders
        for order in self.orders:
            # Skip draft orders
            if order.status == 'draft':
                continue

            # Create invoice status based on order status
            if order.status in ['confirmed', 'processing']:
                invoice_status = 'sent'
            elif order.status in ['ready', 'shipped']:
                invoice_status = 'partially_paid'
            elif order.status == 'delivered':
                invoice_status = 'paid'
            elif order.status == 'cancelled':
                invoice_status = 'cancelled'
            else:
                invoice_status = 'draft'

            # Create invoice number
            invoice_number = f"INV-{order.number[3:]}"

            # Set issue date as order date
            issue_date = order.order_date

            # Set due date as 15 days after issue date
            due_date = issue_date + datetime.timedelta(days=15)

            # Create invoice
            Invoice.objects.create(
                number=invoice_number,
                invoice_type='sales',
                status=invoice_status,
                order=order,
                customer=order.customer,
                issue_date=issue_date,
                due_date=due_date,
                subtotal=order.subtotal,
                tax=order.subtotal * (order.tax / 100),
                discount=order.subtotal * (order.discount / 100),
                total=order.total,
                currency=uzs_currency,
                paid_amount=order.total if invoice_status == 'paid' else (
                    order.total * Decimal(0.5) if invoice_status == 'partially_paid' else Decimal('0')),
                notes=f"Invoice for order {order.number}"
            )

        # Generate purchase invoices from purchase orders
        for po in self.purchase_orders:
            # Skip draft orders
            if po.status == 'draft':
                continue

            # Create invoice status based on order status
            if po.status in ['sent', 'confirmed']:
                invoice_status = 'sent'
            elif po.status == 'partially_received':
                invoice_status = 'partially_paid'
            elif po.status == 'received':
                invoice_status = 'paid'
            elif po.status == 'cancelled':
                invoice_status = 'cancelled'
            else:
                invoice_status = 'draft'

            # Create invoice number
            invoice_number = f"PINV-{po.number[3:]}"

            # Set issue date as order date
            issue_date = po.order_date

            # Set due date as 30 days after issue date
            due_date = issue_date + datetime.timedelta(days=30)

            # Create invoice
            Invoice.objects.create(
                number=invoice_number,
                invoice_type='purchase',
                status=invoice_status,
                purchase_order=po,
                supplier=po.supplier,
                issue_date=issue_date,
                due_date=due_date,
                subtotal=po.subtotal,
                tax=po.subtotal * (po.tax / 100),
                discount=po.subtotal * (po.discount / 100),
                total=po.total,
                currency=uzs_currency,
                paid_amount=po.total if invoice_status == 'paid' else (
                    po.total * Decimal(0.5) if invoice_status == 'partially_paid' else Decimal('0')),
                notes=f"Invoice for purchase order {po.number}"
            )

    def generate_payments(self):
        print("Generating payments...")

        # Default currency
        uzs_currency = Currency.objects.get(code='UZS')

        # Payment methods
        payment_methods = ['cash', 'bank_transfer', 'credit_card', 'debit_card', 'online']

        # Generate payments for sales invoices
        sales_invoices = Invoice.objects.filter(invoice_type='sales')
        for invoice in sales_invoices:
            # Skip cancelled invoices
            if invoice.status == 'cancelled':
                continue

            # Create payment if invoice is paid or partially paid
            if invoice.status in ['paid', 'partially_paid']:
                amount = invoice.total if invoice.status == 'paid' else (invoice.total * Decimal(0.5)).quantize(
                    Decimal('0.01'))

                payment_number = f"PAY-{invoice.number[4:]}"
                payment_date = invoice.issue_date + datetime.timedelta(days=random.randint(1, 15))

                Payment.objects.create(
                    number=payment_number,
                    payment_type='in',
                    payment_method=random.choice(payment_methods),
                    amount=amount,
                    invoice=invoice,
                    customer=invoice.customer,
                    payment_date=payment_date,
                    reference=f"Payment for invoice {invoice.number}",
                    currency=uzs_currency,
                    notes=f"Customer payment for invoice {invoice.number}"
                )

        # Generate payments for purchase invoices
        purchase_invoices = Invoice.objects.filter(invoice_type='purchase')
        for invoice in purchase_invoices:
            # Skip cancelled invoices
            if invoice.status == 'cancelled':
                continue

            # Create payment if invoice is paid or partially paid
            if invoice.status in ['paid', 'partially_paid']:
                amount = invoice.total if invoice.status == 'paid' else (invoice.total * Decimal(0.5)).quantize(
                    Decimal('0.01'))

                payment_number = f"POUT-{invoice.number[5:]}"
                payment_date = invoice.issue_date + datetime.timedelta(days=random.randint(1, 30))

                Payment.objects.create(
                    number=payment_number,
                    payment_type='out',
                    payment_method=random.choice(payment_methods),
                    amount=amount,
                    invoice=invoice,
                    supplier=invoice.supplier,
                    payment_date=payment_date,
                    reference=f"Payment for supplier invoice {invoice.number}",
                    currency=uzs_currency,
                    notes=f"Supplier payment for invoice {invoice.number}"
                )

    def generate_expenses(self, count):
        print(f"Generating {count} expenses...")

        # Default currency
        uzs_currency = Currency.objects.get(code='UZS')

        # Expense categories
        categories = ['rent', 'utilities', 'salaries', 'marketing', 'transportation',
                      'maintenance', 'insurance', 'office_supplies', 'taxes', 'other']

        # Generate expenses for the past year
        start_date = self.current_date - datetime.timedelta(days=365)

        for i in range(count):
            # Generate expense date
            expense_date = fake.date_between(start_date=start_date, end_date=self.current_date)

            # Generate expense number
            expense_number = f"EXP-{expense_date.strftime('%y%m')}-{i + 1:03d}"

            # Get random category
            category = random.choice(categories)

            # Generate amount based on category
            if category in ['rent', 'salaries']:
                amount = Decimal(random.randint(200, 500) * 10000)
            elif category in ['utilities', 'marketing', 'transportation']:
                amount = Decimal(random.randint(50, 200) * 10000)
            else:
                amount = Decimal(random.randint(10, 100) * 10000)

            # Create expense
            Expense.objects.create(
                number=expense_number,
                date=expense_date,
                category=category,
                amount=amount,
                description=f"{category.capitalize()} expense for {expense_date.strftime('%B %Y')}",
                reference=fake.bothify(text="REF-####-??"),
                currency=uzs_currency
            )

    def generate_attendance(self):
        print("Generating attendance records...")

        # Generate attendance for all employees for the past 30 days
        for i in range(30):
            date = self.current_date - datetime.timedelta(days=i)

            # Skip weekends
            if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue

            for employee in Employee.objects.filter(is_active=True):
                # Determine status
                if random.random() < 0.05:  # 5% chance of absence
                    status = 'absent'
                    time_in = None
                    time_out = None
                elif random.random() < 0.1:  # 10% chance of late
                    status = 'late'
                    time_in = datetime.time(hour=9 + random.randint(1, 2), minute=random.randint(0, 59))
                    time_out = datetime.time(hour=17 + random.randint(0, 2), minute=random.randint(0, 59))
                elif random.random() < 0.05:  # 5% chance of half day
                    status = 'half_day'
                    time_in = datetime.time(hour=9, minute=random.randint(0, 30))
                    time_out = datetime.time(hour=13, minute=random.randint(0, 59))
                elif random.random() < 0.03:  # 3% chance of leave
                    status = 'leave'
                    time_in = None
                    time_out = None
                else:  # Regular attendance
                    status = 'present'
                    time_in = datetime.time(hour=8, minute=random.randint(0, 59))
                    time_out = datetime.time(hour=17, minute=random.randint(0, 59))

                Attendance.objects.create(
                    employee=employee,
                    date=date,
                    time_in=time_in,
                    time_out=time_out,
                    status=status,
                    notes="" if status == 'present' else fake.sentence()
                )

    def generate_salaries(self):
        print("Generating salary records...")

        # Get current month and year
        current_month = self.current_date.month
        current_year = self.current_date.year

        # Generate salaries for the past 3 months
        for i in range(3):
            # Calculate month and year
            month = current_month - i
            year = current_year

            if month <= 0:
                month = 12 + month
                year -= 1

            for employee in Employee.objects.filter(is_active=True):
                # Calculate base amount (use employee's base salary)
                base_amount = employee.base_salary

                # Calculate bonus (0-15% of base)
                bonus_percent = random.uniform(0, 15)
                bonus = (base_amount * Decimal(bonus_percent) / 100).quantize(Decimal('0.01'))

                # Calculate deductions (5-15% of base)
                deduction_percent = random.uniform(5, 15)
                deductions = (base_amount * Decimal(deduction_percent) / 100).quantize(Decimal('0.01'))

                # Calculate tax (12% standard)
                tax = (base_amount * Decimal(12) / 100).quantize(Decimal('0.01'))

                # Calculate net amount
                net_amount = base_amount + bonus - deductions - tax

                # Determine status based on month
                if month == current_month:
                    status = 'draft'
                    payment_date = None
                else:
                    status = 'paid'
                    # Payment date is typically the 5th of next month
                    next_month = month + 1
                    next_year = year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    payment_date = datetime.date(next_year, next_month, 5)

                Salary.objects.create(
                    employee=employee,
                    month=month,
                    year=year,
                    base_amount=base_amount,
                    bonus=bonus,
                    deductions=deductions,
                    tax=tax,
                    net_amount=net_amount,
                    payment_date=payment_date,
                    status=status,
                    notes=""
                )


if __name__ == '__main__':
    generator = DataGenerator()
    generator.generate_all()