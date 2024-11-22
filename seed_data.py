from flask import Flask
from datetime import date
from controllers.model import *
from controllers.database import db
from controllers.routes import main as main_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbms_se.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(main_routes)
app.secret_key = 'achutha2704'
db.init_app(app)

with app.app_context():
    db.create_all()
    
    #Admin
    #admin= model.Admin(username='AchuAdmin',password = generate_password_hash("AchuAdmin"))

    # Car data
    """   
    cars = [
        ('ABX1234', 'CIVIC', 'HONDA', 2014, 10000, 'ECONOMY', 'L101', 'A'),
        ('SDF4567', 'FIESTA', 'FORD', 2015, 15000, 'ECONOMY', 'L102', 'N'),
        ('WER3245', 'ACCENT', 'HYUNDAI', 2014, 12356, 'ECONOMY', 'L103', 'A'),
        ('GLZ2376', 'COROLLA', 'TOYOTA', 2016, 5000, 'ECONOMY', 'L104', 'A'),
        ('HJK1234', 'CIVIC', 'HONDA', 2015, 20145, 'ECONOMY', 'L102', 'N'),
        ('GLS7625', 'FOCUS', 'FORD', 2014, 12000, 'COMPACT', 'L107', 'A'),
        ('FKD8202', 'GOLF', 'VOLKSWAGAN', 2016, 9000, 'COMPACT', 'L106', 'A'),
        ('HNX1890', 'PRIUS', 'TOYOTA', 2015, 15690, 'COMPACT', 'L105', 'N'),
        ('KJS1983', 'PRIUS', 'TOYOTA', 2014, 20900, 'COMPACT', 'L104', 'A'),
        ('SDL9356', 'FOCUS', 'FORD', 2016, 10009, 'COMPACT', 'L103', 'A'),
        ('OTY7293', 'CRUZE', 'CHEVROLET', 2016, 17800, 'MID SIZE', 'L102', 'A'),
        ('QWE4562', 'LEGACY', 'SUBARU', 2012, 13420, 'MID SIZE', 'L101', 'A'),
        ('CXZ2356', 'AVENGER', 'DODGE', 2015, 5000, 'MID SIZE', 'L102', 'A'),
        ('ASD9090', 'ACCORD', 'HONDA', 2016, 200, 'MID SIZE', 'L103', 'A'),
        ('UYT3981', 'LEGACY', 'SUBARU', 2013, 16750, 'MID SIZE', 'L104', 'A'),
        ('TRE9726', '200', 'CHRYSTLER', 2012, 14320, 'STANDARD', 'L105', 'A'),
        ('HGF5628', 'TAURUS', 'FORD', 2013, 15540, 'STANDARD', 'L106', 'A'),
        ('LKJ7253', '200', 'CHRYSTLER', 2014, 16300, 'STANDARD', 'L107', 'A'),
        ('VBN6283', 'TAURUS', 'FORD', 2015, 17500, 'STANDARD', 'L101', 'A'),
        ('POI7281', '200', 'CHRYSTLER', 2016, 18830, 'STANDARD', 'L102', 'N'),
        ('MNB8654', 'FALCON', 'FORD', 2012, 10900, 'FULL SIZE', 'L103', 'A'),
        ('UHV9786', 'IMPALA', 'CHEVROLET', 2013, 11500, 'FULL SIZE', 'L104', 'A'),
        ('EFB5427', 'WAYFARER', 'FORD', 2014, 14350, 'FULL SIZE', 'L105', 'A'),
        ('PLM9873', 'IMPALA', 'CHEVROLET', 2015, 18900, 'FULL SIZE', 'L106', 'A'),
        ('WDV2458', 'FALCON', 'FORD', 2016, 5600, 'FULL SIZE', 'L107', 'A'),
        ('QSC8709', 'MKZ', 'LINCOLN', 2012, 18700, 'LUXURY CAR', 'L101', 'A'),
        ('TGB8961', 'GENESIS', 'HYUNDAI', 2013, 17620, 'LUXURY CAR', 'L102', 'A'),
        ('MKU0172', 'TLX', 'ACURA', 2014, 12345, 'LUXURY CAR', 'L103', 'A'),
        ('CFT1908', '328I', 'BMW', 2015, 10800, 'LUXURY CAR', 'L104', 'A'),
        ('WHM7619', 'AVALON', 'TOYOTA', 2016, 7800, 'LUXURY CAR', 'L105', 'A'),
        ('WLZ8955', 'ESCAPE', 'FORD', 2012, 19800, 'MID SIZE SUV', 'L106', 'A'),
        ('QIO7621', 'EQUINOX', 'CHEVROLET', 2013, 17560, 'MID SIZE SUV', 'L107', 'A'),
        ('YSN1927', 'PATHFINDER', 'NISSAN', 2014, 14390, 'MID SIZE SUV', 'L101', 'A'),
        ('EDM8610', 'GLA', 'MERCEDEZ BENZ', 2015, 12900, 'MID SIZE SUV', 'L102', 'A'),
        ('AHK7325', 'RAV4', 'TOYOTA', 2016, 3400, 'MID SIZE SUV', 'L103', 'A'),
        ('OHZ0976', 'EDGE', 'FORD', 2012, 27890, 'STANDARD SUV', 'L104', 'A'),
        ('RKS9862', 'TAHOE', 'CHEVROLET', 2013, 20390, 'STANDARD SUV', 'L105', 'A'),
        ('WIJ6190', 'EDGE', 'FORD', 2014, 18700, 'STANDARD SUV', 'L106', 'A'),
        ('ZDT8612', 'TAHOE', 'CHEVROLET', 2015, 14300, 'STANDARD SUV', 'L107', 'A'),
        ('LDJ7719', 'EDGE', 'FORD', 2016, 5690, 'STANDARD SUV', 'L101', 'A'),
        ('UIA8709', 'EXPEDITION', 'FORD', 2012, 19870, 'FULL SIZE SUV', 'L102', 'A'),
        ('WKJ7972', 'SEQUOIA', 'TOYOTA', 2013, 14500, 'FULL SIZE SUV', 'L103', 'A'),
        ('JLS1097', 'SUBURBAN', 'CHEVROLET', 2014, 13290, 'FULL SIZE SUV', 'L104', 'A'),
        ('UHJ6782', 'EXPEDITION', 'FORD', 2015, 11750, 'FULL SIZE SUV', 'L105', 'A'),
        ('XBM6822', 'SUBURBAN', 'CHEVROLET', 2016, 3400, 'FULL SIZE SUV', 'L106', 'A'),
        ('SHK7767', 'QUEST', 'NISSAN', 2012, 23478, 'MINI VAN', 'L107', 'A'),
        ('JSL7920', 'ODYSSEY', 'HONDA', 2013, 19320, 'MINI VAN', 'L106', 'A'),
        ('PAJ5289', 'GRAND CARAVAN', 'DODGE', 2014, 23478, 'MINI VAN', 'L105', 'A'),
        ('TSJ6290', 'QUEST', 'NISSAN', 2015, 13200, 'MINI VAN', 'L104', 'A'),
        ('MWO9296', 'ODYSSEY', 'HONDA', 2016, 2300, 'MINI VAN', 'L103', 'A')
    ]
    
    # Insert car data into the database
    for car in cars:
        new_car = model.Car(
            registration_number=car[0],
            model_name=car[1],
            make=car[2],
            model_year=car[3],
            mileage=car[4],
            car_category_name=car[5],
            loc_id=car[6],
            availability_flag=car[7]
        )
        db.session.add(new_car)
    """
    #car categories
    '''
    car_categories = [
        ('ECONOMY', 2, 5, 30, 0.9),
        ('COMPACT', 3, 5, 32, 0.96),
        ('MID SIZE', 3, 5, 35, 1.05),
        ('STANDARD', 3, 5, 38, 1.14),
        ('FULL SIZE', 4, 5, 40, 1.2),
        ('LUXURY CAR', 5, 5, 75, 2.25),
        ('MID SIZE SUV', 2, 5, 36, 1.08),
        ('STANDARD SUV', 3, 5, 40, 1.2),
        ('FULL SIZE SUV', 2, 8, 60, 1.8),
        ('MINI VAN', 5, 7, 70, 2.1)
    ]


    # Inserting data into the CarCategory table
    for category_name, no_of_luggage, no_of_person, cost_per_day, late_fee_per_hour in car_categories:
        car_category = CarCategory(
            category_name=category_name,
            no_of_luggage=no_of_luggage,
            no_of_person=no_of_person,
            cost_per_day=cost_per_day,
            late_fee_per_hour=late_fee_per_hour
        )
        db.session.add(car_category)

    # Commit the transaction
    db.session.commit()
    print("Car data inserted successfully.")
'''

    # Insert data into DiscountDetails table
    discount_details_data = [
        DiscountDetails(discount_code='D678', discount_name='IBM CORPORATE', expiry_date=date(2025, 1, 25), discount_percentage=25),
        DiscountDetails(discount_code='D234', discount_name='CTS CORPORATE', expiry_date=date(2025, 9, 2), discount_percentage=20),
        DiscountDetails(discount_code='D756', discount_name='HOLIDAY SPECIAL', expiry_date=date(2025, 10, 29), discount_percentage=10),
        DiscountDetails(discount_code='D109', discount_name='WEEKLY RENTALS', expiry_date=date(2025, 11, 9), discount_percentage=25),
        DiscountDetails(discount_code='D972', discount_name='ONE WAY SPECIAL', expiry_date=date(2024, 12, 15), discount_percentage=20),
        DiscountDetails(discount_code='D297', discount_name='UPGRADE SPECIAL', expiry_date=date(2025, 2, 18), discount_percentage=20)
    ]

    # Insert data into RentalCarInsurance table
    rental_car_insurance_data = [
        RentalCarInsurance(insurance_code='I201', insurance_name='COLLISION DAMAGE WAIVER', coverage_type='Covers theft and total damage to the rental car', cost_per_day=15),
        RentalCarInsurance(insurance_code='I202', insurance_name='SUPPLEMENTAL LIABILITY PROTECTION', coverage_type='Covers damage done to others', cost_per_day=12),
        RentalCarInsurance(insurance_code='I203', insurance_name='PERSONAL ACCIDENT INSURANCE', coverage_type='Covers medical costs for driver and passengers', cost_per_day=10),
        RentalCarInsurance(insurance_code='I204', insurance_name='PERSONAL EFFECTS COVERAGE', coverage_type='Covers theft of personal belongings', cost_per_day=5)
    ]

    # Add and commit data to the database
    try:
        db.session.add_all(discount_details_data)
        db.session.add_all(rental_car_insurance_data)
        db.session.commit()
        print("Data inserted successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")