from datetime import datetime
from controllers.database import db

# CUSTOMER_DETAILS Table
class CustomerDetails(db.Model):
    __tablename__ = 'customer_details'
    dl_number = db.Column(db.String(8), primary_key=True, nullable=False)
    fname = db.Column(db.String(25), nullable=False)
    mname = db.Column(db.String(15))
    lname = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), nullable=False)
    phone_number = db.Column(db.String(25), nullable=False)
    email_id = db.Column(db.String(30), nullable=False)
    street = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state_name = db.Column(db.String(20), nullable=False)
    zipcode = db.Column(db.String(5), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)

# CAR_CATEGORY Table
class CarCategory(db.Model):
    __tablename__ = 'car_category'
    category_name = db.Column(db.String(25), primary_key=True, nullable=False)
    no_of_luggage = db.Column(db.Integer, nullable=False)
    no_of_person = db.Column(db.Integer, nullable=False)
    cost_per_day = db.Column(db.Numeric(5, 2), nullable=False)
    late_fee_per_hour = db.Column(db.Numeric(5, 2), nullable=False)

# LOCATION_DETAILS Table
class LocationDetails(db.Model):
    __tablename__ = 'location_details'
    location_id = db.Column(db.String(4), primary_key=True, nullable=False)
    location_name = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state_name = db.Column(db.String(20), nullable=False)
    zipcode = db.Column(db.String(5), nullable=False)

# CAR Table
class Car(db.Model):
    __tablename__ = 'car'
    registration_number = db.Column(db.String(7), primary_key=True, nullable=False)
    model_name = db.Column(db.String(25), nullable=False)
    make = db.Column(db.String(25), nullable=False)
    model_year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    car_category_name = db.Column(db.String(25), db.ForeignKey('car_category.category_name'), nullable=False)
    loc_id = db.Column(db.String(4), db.ForeignKey('location_details.location_id'), nullable=False)
    availability_flag = db.Column(db.String(1), nullable=False)

# DISCOUNT_DETAILS Table
class DiscountDetails(db.Model):
    __tablename__ = 'discount_details'
    discount_code = db.Column(db.String(4), primary_key=True, nullable=False)
    discount_name = db.Column(db.String(25), unique=True, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    discount_percentage = db.Column(db.Numeric(4, 2), nullable=False)

# RENTAL_CAR_INSURANCE Table
class RentalCarInsurance(db.Model):
    __tablename__ = 'rental_car_insurance'
    insurance_code = db.Column(db.String(4), primary_key=True, nullable=False)
    insurance_name = db.Column(db.String(50), unique=True, nullable=False)
    coverage_type = db.Column(db.String(200), nullable=False)
    cost_per_day = db.Column(db.Numeric(4, 2), nullable=False)

# BOOKING_DETAILS Table
class BookingDetails(db.Model):
    __tablename__ = 'booking_details'
    booking_id = db.Column(db.String(5), primary_key=True, nullable=False)
    from_dt_time = db.Column(db.DateTime, nullable=False)
    ret_dt_time = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    booking_status = db.Column(db.String(1), nullable=False)
    pickup_loc = db.Column(db.String(4), db.ForeignKey('location_details.location_id'), nullable=False)
    drop_loc = db.Column(db.String(4), db.ForeignKey('location_details.location_id'), nullable=False)
    reg_num = db.Column(db.String(7), db.ForeignKey('car.registration_number'), nullable=False)
    dl_num = db.Column(db.String(8), db.ForeignKey('customer_details.dl_number'), nullable=False)
    ins_code = db.Column(db.String(4), db.ForeignKey('rental_car_insurance.insurance_code'))
    act_ret_dt_time = db.Column(db.DateTime)
    discount_code = db.Column(db.String(4), db.ForeignKey('discount_details.discount_code'))

# BILLING_DETAILS Table
class BillingDetails(db.Model):
    __tablename__ = 'billing_details'
    bill_id = db.Column(db.String(6), primary_key=True, nullable=False)
    bill_date = db.Column(db.Date, nullable=False)
    bill_status = db.Column(db.String(1), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False)
    booking_id = db.Column(db.String(5), db.ForeignKey('booking_details.booking_id'), nullable=False)
    total_late_fee = db.Column(db.Numeric(10, 2), nullable=False)
    
# ADMIN table
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)