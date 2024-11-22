import uuid
import math
from decimal import Decimal
from datetime import datetime
from controllers import model
from sqlalchemy import func, or_, case, extract
from controllers.database import db
from decimal import Decimal, ROUND_HALF_UP
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

#################################
#           Procedure           #
#################################

def calculate_bill_details(booking, actual_return_datetime):
    """
    Calculate comprehensive bill details for a booking
    
    Args:
        booking (BookingDetails): The booking object
        actual_return_datetime (datetime): Actual return time
    
    Returns:
        dict: Calculated bill details
    """
    # Normalize datetime objects to have consistent timezone
    if booking.from_dt_time.tzinfo is not None:
        # If booking from time is timezone-aware, make actual return time timezone-aware
        if actual_return_datetime.tzinfo is None:
            actual_return_datetime = actual_return_datetime.replace(tzinfo=booking.from_dt_time.tzinfo)
    else:
        # If booking from time is timezone-naive, remove timezone from actual return time
        if actual_return_datetime.tzinfo is not None:
            actual_return_datetime = actual_return_datetime.replace(tzinfo=None)
    
    # Get car details
    car = model.Car.query.filter_by(registration_number=booking.reg_num).first()
    car_category = model.CarCategory.query.filter_by(category_name=car.car_category_name).first()
    
    # Calculate rental duration
    rental_duration = (actual_return_datetime - booking.from_dt_time).total_seconds() / (24 * 3600)
    rental_duration = max(1, math.ceil(rental_duration))  # Minimum 1 day
    
    # Base amount calculation (ensure it matches original booking logic)
    base_amount = Decimal(car_category.cost_per_day * rental_duration)
    
    # Late fee calculation
    late_fee = Decimal('0.00')
    if actual_return_datetime > booking.ret_dt_time:
        # Normalize ret_dt_time for comparison
        ret_dt_time = booking.ret_dt_time
        if ret_dt_time.tzinfo is not None and actual_return_datetime.tzinfo is None:
            ret_dt_time = ret_dt_time.replace(tzinfo=None)
        
        hours_late = (actual_return_datetime - ret_dt_time).total_seconds() / 3600
        late_fee = Decimal(hours_late * float(car_category.late_fee_per_hour)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    
    # Insurance cost calculation
    insurance_cost = Decimal('0.00')
    insurance_details = None
    if booking.ins_code:
        insurance = model.RentalCarInsurance.query.get(booking.ins_code)
        insurance_cost = Decimal(insurance.cost_per_day * rental_duration)
        insurance_details = {
            'name': insurance.insurance_name,
            'cost_per_day': float(insurance.cost_per_day),
            'total_cost': float(insurance_cost)
        }
    
    # Discount calculation
    discount_amount = Decimal('0.00')
    discount_details = None
    if booking.discount_code:
        discount = model.DiscountDetails.query.get(booking.discount_code)
        if discount.expiry_date >= datetime.now().date():
            discount_amount = (base_amount * Decimal(discount.discount_percentage / 100)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            discount_details = {
                'name': discount.discount_name,
                'percentage': float(discount.discount_percentage),
                'amount': float(discount_amount)
            }
    
    # Tax calculation (10%)
    subtotal = base_amount + insurance_cost
    tax_amount = (subtotal * Decimal('0.1')).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    
    # Total amount calculation
    total_amount = subtotal + tax_amount + late_fee - discount_amount
    
    return {
        'booking_id': booking.booking_id,
        'base_amount': float(base_amount),
        'rental_duration': rental_duration,
        'late_fee': float(late_fee),
        'insurance_cost': float(insurance_cost),
        'discount_amount': float(discount_amount),
        'tax_amount': float(tax_amount),
        'total_amount': float(total_amount),
        'car_details': {
            'model': car.model_name,
            'make': car.make,
            'registration': car.registration_number,
            'category': car.car_category_name
        },
        'booking_dates': {
            'pickup': booking.from_dt_time,
            'expected_return': booking.ret_dt_time,
            'actual_return': actual_return_datetime
        },
        'insurance': insurance_details,
        'discount': discount_details
    }

#################################
#       Admin functions         #
#################################

# admin loign
@main.route('/admin/',methods=["POST","GET"])
def adminIndex():
    # chect the request is post or not
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if username == "" and password == "":
            flash('Please fill all the field','danger')
            return redirect('/admin/')
        else:
            # login admin by username 
            admins = model.Admin().query.filter_by(username=username).first()
            if admins and check_password_hash(admins.password,password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('Login Successfully','success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Email and Password','danger')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html',title="Admin Login")
    
@main.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    # User Statistics
    totalUser = model.CustomerDetails.query.count()
    totalApprove = model.CustomerDetails.query.filter_by(status=1).count()
    notTotalApprove = model.CustomerDetails.query.filter_by(status=0).count()
    
    # Financial Aggregations
    # Total Revenue Analysis
    total_revenue = db.session.query(func.sum(model.BillingDetails.total_amount)).scalar() or 0
    
    # Monthly Revenue Breakdown
    monthly_revenue = db.session.query(
        extract('month', model.BillingDetails.bill_date).label('month'),
        func.sum(model.BillingDetails.total_amount).label('monthly_total')
    ).group_by(extract('month', model.BillingDetails.bill_date)).all()
    
    # Car Category Revenue
    car_category_revenue = db.session.query(
        model.Car.car_category_name,
        func.sum(model.BillingDetails.total_amount).label('category_total')
    ).join(model.BookingDetails, model.Car.registration_number == model.BookingDetails.reg_num)\
     .join(model.BillingDetails, model.BookingDetails.booking_id == model.BillingDetails.booking_id)\
     .group_by(model.Car.car_category_name).all()
    
    # Booking Status Analysis
    booking_status_analysis = db.session.query(
        model.BookingDetails.booking_status,
        func.count(model.BookingDetails.booking_id).label('status_count')
    ).group_by(model.BookingDetails.booking_status).all()
    
    # Late Fees Analysis
    late_fees_analysis = db.session.query(
        func.sum(model.BillingDetails.total_late_fee).label('total_late_fees')
    ).scalar() or 0
    
    # Insurance Revenue
    insurance_revenue = db.session.query(
        model.RentalCarInsurance.insurance_name,
        func.sum(model.BillingDetails.total_amount).label('insurance_total')
    ).join(model.BookingDetails, model.RentalCarInsurance.insurance_code == model.BookingDetails.ins_code)\
     .join(model.BillingDetails, model.BookingDetails.booking_id == model.BillingDetails.booking_id)\
     .group_by(model.RentalCarInsurance.insurance_name).all()
    
    # Most Popular Car Categories
    popular_car_categories = db.session.query(
        model.Car.car_category_name,
        func.count(model.BookingDetails.booking_id).label('booking_count')
    ).join(model.BookingDetails, model.Car.registration_number == model.BookingDetails.reg_num)\
     .group_by(model.Car.car_category_name)\
     .order_by(func.count(model.BookingDetails.booking_id).desc()).all()
    
    return render_template('admin/dashboard.html', 
        title="Admin Dashboard",
        totalUser=totalUser,
        totalApprove=totalApprove,
        notTotalApprove=notTotalApprove,
        total_revenue=total_revenue,
        monthly_revenue=monthly_revenue,
        car_category_revenue=car_category_revenue,
        booking_status_analysis=booking_status_analysis,
        late_fees_analysis=late_fees_analysis,
        insurance_revenue=insurance_revenue,
        popular_car_categories=popular_car_categories
    )
    
# admin get all user 
@main.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method == "POST":
        search = request.form.get('search')
        users = model.CustomerDetails.query.filter_by(model.CustomerDetails.username.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    else:
        users = model.CustomerDetails.query.all()
        return render_template('admin/all-user.html',title='Approve User',users=users)

# Aproove users
@main.route('/admin/approve-user/<string:dl_number>')
def adminApprove(dl_number):
    if not session.get('admin_id'):
        return redirect('/admin/')
    model.CustomerDetails.query.filter_by(dl_number=dl_number).update(dict(status=1))
    db.session.commit()
    flash('Approved Successfully', 'success')
    return redirect('/admin/get-all-user')

# change admin password
@main.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin = model.Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please fill the field','danger')
            return redirect('/admin/change-admin-password')
        else:
            model.Admin().query.filter_by(username=username).update(dict(password = generate_password_hash(password,10)))
            db.session.commit()
            flash('Admin Password update successfully','success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)
    
# Join query for viewing all the booking details
@main.route('/admin/bookings')
def adminBookings():
    if not session.get('admin_id'):
        return redirect('/admin/')

    bookings = db.session.query(
        model.BookingDetails.booking_id,
        model.CustomerDetails.fname,
        model.CustomerDetails.lname,
        model.CustomerDetails.phone_number,
        model.BookingDetails.from_dt_time,
        model.BookingDetails.ret_dt_time
    ).join(
        model.CustomerDetails,
        model.BookingDetails.dl_num == model.CustomerDetails.dl_number
    ).filter(
        model.BookingDetails.booking_status == 'P'
    ).all()

    return render_template('admin/bookings.html', title='Active Bookings', bookings=bookings)

# admin logout
@main.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')

@main.route('/admin/returns', methods=['GET'])
def viewPendingReturns():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.adminLogin'))
    
    pending_returns = (
        db.session.query(
            model.BookingDetails,
            model.BillingDetails,
            model.CustomerDetails,
            model.Car
        )
        .join(model.BillingDetails, model.BookingDetails.booking_id == model.BillingDetails.booking_id)
        .join(model.CustomerDetails, model.BookingDetails.dl_num == model.CustomerDetails.dl_number)
        .join(model.Car, model.BookingDetails.reg_num == model.Car.registration_number)
        .filter(model.BookingDetails.booking_status == 'A')
        .all()
    )
    
    return render_template('admin/pending_returns.html',
                         returns=pending_returns)

@main.route('/admin/returns/approve/<string:booking_id>', methods=['POST'])
def approveReturn(booking_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.adminLogin'))
    
    try:
        booking = model.BookingDetails.query.get_or_404(booking_id)
        bill = model.BillingDetails.query.filter_by(booking_id=booking_id).first()
        
        # Update booking status
        booking.booking_status = 'R'  # R: Returned
        
        # Update billing status
        bill.bill_status = 'C'  # C: Completed
        
        # Make car available again
        car = model.Car.query.get(booking.reg_num)
        car.availability_flag = 'A'
        
        db.session.commit()
        flash('Return approved successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving return: {str(e)}', 'error')
    
    return redirect(url_for('main.viewPendingReturns'))

#################################
#       User functions          #
#################################
    
# User Login
@main.route('/user/', methods=["POST", "GET"])
def userIndex():
    if session.get('dl_number'):
        return redirect('/user/dashboard')
    
    if request.method == "POST":
        # Get input fields
        email_id = request.form.get('email_id')
        password = request.form.get('password')
        
        # Check if the user exists by email_id
        user = model.CustomerDetails.query.filter_by(email_id=email_id).first()
        
        if user and check_password_hash(user.password, password):
            # Check if the account is approved
            if user.status == 0:
                flash('Your account is not approved by Admin', 'danger')
                return redirect('/user/')
            else:
                # Set session data
                session['dl_number'] = user.dl_number
                flash('Login successfully', 'success')
                return redirect('/user/dashboard')
        else:
            flash('Invalid email or password', 'danger')
            return redirect('/user/')
    
    return render_template('user/index.html', title="User Login")

# User Register
@main.route('/user/signup', methods=['POST', 'GET'])
def userSignup():
    if session.get('dl_number'):
        return redirect('/user/dashboard')
    
    if request.method == 'POST':
        # Get all input fields
        dl_number = request.form.get('dl_number')
        fname = request.form.get('fname')
        mname = request.form.get('mname')
        lname = request.form.get('lname')
        phone_number = request.form.get('phone_number')
        email_id = request.form.get('email_id')
        username = request.form.get('username')
        password = request.form.get('password')
        street = request.form.get('street')
        city = request.form.get('city')
        state_name = request.form.get('state_name')
        zipcode = request.form.get('zipcode')

        # Check all required fields are filled
        if not all([dl_number, fname, lname, phone_number, email_id, username, password, street, city, state_name, zipcode]):
            flash('Please fill all required fields', 'danger')
            return redirect('/user/signup')
        
        # Check if email already exists
        is_email = model.CustomerDetails.query.filter_by(email_id=email_id).first()
        if is_email:
            flash('Email already exists', 'danger')
            return redirect('/user/signup')
        
        # Hash the password
        hash_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=10)

        # Create new user
        user = model.CustomerDetails(
            dl_number=dl_number,
            fname=fname,
            mname=mname,
            lname=lname,
            phone_number=phone_number,
            email_id=email_id,
            username = username,
            street=street,
            city=city,
            state_name=state_name,
            zipcode=zipcode,
            password=hash_password,
            status=0  # Default status to 0 (unapproved)
        )

        # Add user to the database
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Admin will approve your account shortly.', 'success')
        return redirect('/user/')
    
    return render_template('user/signup.html', title="User Signup")

# User Dashboard
@main.route('/user/dashboard')
def userDashboard():
    if not session.get('dl_number'):
        return redirect('/user/')
    return render_template('user/dashboard.html',title="User Dashboard", show_sidebar=True)

# User Profile
@main.route('/user/profile')
def userProfile():
    if not session.get('dl_number'):
        return redirect('/user/')
    
    dl_number = session.get('dl_number')
    user = model.CustomerDetails.query.filter_by(dl_number=dl_number).first()
    return render_template('user/profile.html', title="User Profile", user=user, show_sidebar=True)

# User Logout
@main.route('/user/logout')
def userLogout():
    if not session.get('dl_number'):
        return redirect('/user/')
    
    session.pop('dl_number', None)
    flash('Logged out successfully', 'success')
    return redirect('/')

# Change Password
@main.route('/user/change-password', methods=["POST", "GET"])
def userChangePassword():
    if not session.get('dl_number'):
        return redirect('/user/')
    
    if request.method == 'POST':
        email_id = request.form.get('email_id')
        password = request.form.get('password')
        
        if not email_id or not password:
            flash('Please fill all fields', 'danger')
            return redirect('/user/change-password')
        
        # Check if user with the provided email exists
        user = model.CustomerDetails.query.filter_by(email_id = email_id).first()
        if user:
            hash_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=10)
            user.password = hash_password
            db.session.commit()
            flash('Password changed successfully', 'success')
            return redirect('/user/profile')
        else:
            flash('Invalid email', 'danger')
            return redirect('/user/change-password')
    
    return render_template('user/change-password.html', title = "Change Password")

# Update Profile
@main.route('/user/update-profile', methods=["POST", "GET"])
def userUpdateProfile():
    if not session.get('dl_number'):
        return redirect('/user/')
    
    dl_number = session.get('dl_number')
    user = model.CustomerDetails.query.get(dl_number)
    
    if request.method == 'POST':
        # Get input fields
        fname = request.form.get('fname')
        mname = request.form.get('mname')
        lname = request.form.get('lname')
        phone_number = request.form.get('phone_number')
        email_id = request.form.get('email_id')
        username = request.form.get('username')
        street = request.form.get('street')
        city = request.form.get('city')
        state_name = request.form.get('state_name')
        zipcode = request.form.get('zipcode')
        
        # Check all required fields are filled
        if not all([fname, lname, phone_number, email_id, username, street, city, state_name, zipcode]):
            flash('Please fill all required fields', 'danger')
            return redirect('/user/update-profile')
        
        # Update user profile
        user.fname = fname
        user.mname = mname
        user.lname = lname
        user.phone_number = phone_number
        user.email_id = email_id
        user.username = username
        user.street = street
        user.city = city
        user.state_name = state_name
        user.zipcode = zipcode
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect('/user/profile')
    
    return render_template('user/update-profile.html', title="Update Profile", user=user, show_sidebar=True)

# Display the nerest pickup locations to user -> TBD  convert this to a stored procedure
@main.route('/user/pickup_locations')
def userPickupLocations():
    if not session.get('dl_number'):
        return redirect('/user/dashboard')

    dl_number = session.get('dl_number')
    user_details = model.CustomerDetails.query.filter_by(dl_number=dl_number).first()

    if user_details:
        proximity_score = case(
            (model.LocationDetails.street == user_details.street, 4),
            (model.LocationDetails.zipcode == user_details.zipcode, 3),
            (model.LocationDetails.city == user_details.city, 2),
            (model.LocationDetails.state_name == user_details.state_name, 1),
            else_=0
        )

        nearest_locations = (model.LocationDetails.query
                             .filter(
                                 or_(
                                     model.LocationDetails.street == user_details.street,
                                     model.LocationDetails.zipcode == user_details.zipcode,
                                     model.LocationDetails.city == user_details.city,
                                     model.LocationDetails.state_name == user_details.state_name
                                 )
                             )
                             .order_by(proximity_score.desc())
                             .all())

        if not nearest_locations:
            nearest_locations = model.LocationDetails.query.all()

    return render_template('user/pickup_locations.html', 
                           title="Select Pickup Location", 
                           show_sidebar=True, 
                           locations=nearest_locations)

# Display all dropoff locations to the user
@main.route('/user/locations/dropoff/<string:pickup_location_id>')
def userDropoffLoc(pickup_location_id):
    if not session.get('dl_number'):
        return redirect('/user/dashboard')

    # Get all locations except the pickup location
    dropoff_locations = model.LocationDetails.query.filter(
        model.LocationDetails.location_id != pickup_location_id
    ).all()

    return render_template('user/dropoff_locations.html', 
                           title="Select Drop-off Location", 
                           show_sidebar=True, 
                           pickup_location_id=pickup_location_id,
                           locations=dropoff_locations)

# Booking the car
@main.route('/user/cars/<string:pickup_location_id>/<string:dropoff_location_id>', methods=['GET', 'POST'])
def viewCars(pickup_location_id, dropoff_location_id):
    customer_dl = session.get('dl_number')
    if request.method == 'POST':
        # Prepare booking details
        registration_number = request.form['registration_number']
        customer_dl = request.form['dl_number']
        pickup_datetime = datetime.fromisoformat(request.form['pickup_datetime'])
        return_datetime = datetime.fromisoformat(request.form['return_datetime'])
        
        # Get optional insurance and discount codes
        insurance_code = request.form.get('insurance_code') or None
        discount_code = request.form.get('discount_code') or None
        
        # Create booking
        new_booking = model.BookingDetails(
            booking_id=str(uuid.uuid4())[:5],
            from_dt_time=pickup_datetime,
            ret_dt_time=return_datetime,
            amount=0,  # Will be calculated by trigger
            booking_status='P',
            pickup_loc=pickup_location_id,
            drop_loc=dropoff_location_id,
            reg_num=registration_number,
            dl_num=customer_dl,
            ins_code=insurance_code,
            discount_code=discount_code
        )
        db.session.add(new_booking)
        db.session.commit()

        # Additional calculations after initial booking
        booking = model.BookingDetails.query.get(new_booking.booking_id)
        
        # Calculate rental days
        rental_days = (booking.ret_dt_time.date() - booking.from_dt_time.date()).days + 1
        
        # Apply insurance if selected
        if insurance_code:
            insurance = model.RentalCarInsurance.query.get(insurance_code)
            insurance_amount = float(insurance.cost_per_day) * rental_days
            booking.amount += Decimal(insurance_amount) 
        
        # Apply discount if valid
        if discount_code:
            discount = model.DiscountDetails.query.filter_by(
                discount_code=discount_code
            ).filter(model.DiscountDetails.expiry_date >= datetime.now().date()).first()
            
            if discount:
                # Calculate base amount before discount
                car = model.Car.query.get(registration_number)
                car_category = model.CarCategory.query.filter_by(category_name=car.car_category_name).first()
                base_amount = float(car_category.cost_per_day) * rental_days
                
                # Apply discount
                discount_amount = base_amount * (float(discount.discount_percentage) / 100)
                booking.amount -= Decimal(discount_amount)
        
        db.session.commit()

        return redirect(url_for('main.userDropoffLoc', pickup_location_id=pickup_location_id))

    # GET Request
    selected_category = request.args.get('category')
    
    # Filter cars by pickup location and availability
    query = model.Car.query.filter_by(loc_id=pickup_location_id, availability_flag='A')
    if selected_category and selected_category != "all":
        query = query.filter_by(car_category_name=selected_category)
    available_cars = query.all()

    pickup_location = model.LocationDetails.query.get(pickup_location_id)
    dropoff_location = model.LocationDetails.query.get(dropoff_location_id)
    categories = model.CarCategory.query.all()
    cat_map = {category.category_name: float(category.cost_per_day) for category in categories}
    
    # Fetch available insurance policies and discounts
    insurance_policies = model.RentalCarInsurance.query.all()
    
    # Fetch valid discounts (not expired)
    current_date = datetime.now().date()
    valid_discounts = model.DiscountDetails.query.filter(
        model.DiscountDetails.expiry_date >= current_date
    ).all()

    return render_template('user/cars.html', 
                           title="Available Cars", 
                           show_sidebar=False, 
                           pickup_location=pickup_location,
                           dropoff_location=dropoff_location, 
                           cars=available_cars, 
                           cat_map=cat_map,
                           categories=categories,
                           insurance_policies=insurance_policies,
                           valid_discounts=valid_discounts,
                           selected_category=selected_category,
                           customer_dl=customer_dl)
    
# Returning the vehicle   
@main.route('/user/return', methods=['GET', 'POST'])
def returnCar():
    customer_dl = session.get('dl_number')
    if not customer_dl:
        flash('Please login to access this page', 'danger')
        return redirect(url_for('main.login'))

    # Get active bookings for the customer with car details
    active_bookings = db.session.query(
        model.BookingDetails, 
        model.Car
    ).join(
        model.Car, 
        model.BookingDetails.reg_num == model.Car.registration_number
    ).filter(
        model.BookingDetails.dl_num == customer_dl, 
        model.BookingDetails.booking_status == 'P'
    ).all()

    if request.method == 'POST':
        booking_id = request.form['booking_id']
        actual_return_datetime = datetime.now()
        
        # Find the booking
        booking = model.BookingDetails.query.get(booking_id)
        
        if not booking:
            flash('Invalid booking', 'danger')
            return redirect(url_for('main.returnCar'))

        # Store essential booking details in session for payment route
        session['return_details'] = {
            'booking_id': booking_id,
            'actual_return_datetime': actual_return_datetime
        }

        return redirect(url_for('main.paymentPage'))

    return render_template('user/return.html', 
                           title="Return Car", 
                           show_sidebar=True, 
                           active_bookings=active_bookings)

@main.route('/user/payment', methods=['GET', 'POST'])
def paymentPage():
    # Retrieve return details from session
    return_details = session.get('return_details')

    if not return_details:
        flash('No pending return found', 'danger')
        return redirect(url_for('main.returnCar'))

    # Find the booking
    booking = model.BookingDetails.query.get(return_details['booking_id'])

    if not booking:
        flash('Invalid booking', 'danger')
        return redirect(url_for('main.returnCar'))

    # Fetch car details
    car = model.Car.query.get(booking.reg_num)

    # Fetch discount details if applicable
    discount = None
    if booking.discount_code:
        discount = model.DiscountDetails.query.get(booking.discount_code)

    # Fetch insurance details if applicable
    insurance = None
    if booking.ins_code:
        insurance = model.RentalCarInsurance.query.get(booking.ins_code)

    # Calculate bill details
    bill_details = calculate_bill_details(
        booking, 
        return_details['actual_return_datetime']
    )

    # Update bill details with queried data
    bill_details.update({
        'car_details': {
            'make': car.make,
            'model': car.model_name,
            'registration': car.registration_number,
            'category': car.car_category_name
        },
        'discount_details': {
            'name': discount.discount_name if discount else None,
            'percentage': float(discount.discount_percentage) if discount else 0
        } if discount else None,
        'insurance_details': {
            'name': insurance.insurance_name if insurance else None,
            'cost': float(insurance.cost_per_day) * bill_details['rental_duration'] if insurance else 0
        } if insurance else None
    })

    if request.method == 'POST':
        # Generate bill
        bill = model.BillingDetails(
            bill_id=str(uuid.uuid4())[:6],
            bill_date=datetime.now().date(),
            bill_status='P',
            discount_amount = Decimal(
            (bill_details['discount_details']['percentage'] / 100 * bill_details['base_amount']) 
            if bill_details.get('discount_details') 
            else 0),
            total_amount=Decimal(bill_details['total_amount']),
            tax_amount=Decimal(bill_details['tax_amount']),
            booking_id=booking.booking_id,
            total_late_fee=Decimal(bill_details['late_fee'])
        )

        # Update booking status and set car availability
        booking.booking_status = 'R'
        booking.act_ret_dt_time = return_details['actual_return_datetime']
        car.availability_flag = 'A'

        db.session.add(bill)
        db.session.commit()

        # Clear session details
        session.pop('return_details', None)

        flash(f'Payment successful. Total paid: ${bill_details["total_amount"]:.2f}', 'success')
        return redirect(url_for('main.userDashboard'))

    return render_template('user/payment.html', 
                           title="Payment", 
                           show_sidebar=True, 
                           bill_details=bill_details)
