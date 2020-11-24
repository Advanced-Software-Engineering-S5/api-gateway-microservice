from api_gateway.forms import RatingForm, RestaurantProfileEditForm, ReservationForm
from api_gateway.classes.restaurant import Restaurant, RestaurantTable, Review
from api_gateway.classes.reservations import Reservation
from logging import error
from api_gateway.classes.exceptions import FormValidationError, GoOutSafeError
from flask import Blueprint, redirect, render_template, request, flash
from api_gateway.auth import admin_required, current_user, login_required
from sqlalchemy import func
from datetime import datetime

restaurants = Blueprint('restaurants', __name__)

@restaurants.route('/restaurants/reserve/<restaurant_id>', methods=['GET', 'POST'])
@login_required
def _reserve(restaurant_id):
    form = ReservationForm()
    restaurant = Restaurant.get(restaurant_id)
    if (request.method == 'POST'):
        if ReservationForm(request.form).validate_on_submit():
            reservation_time = datetime.combine(
                ReservationForm(request.form).data['reservation_date'],
                ReservationForm(request.form).data['reservation_time'])

            if (reservation_time <= datetime.now()):
                flash ('Invalid Date Error. You cannot reserve a table in the past!', 'booking')
                return redirect(request.referrer)
                
            seats = ReservationForm(request.form).data['seats']
            mess = Reservation.new(int(current_user.id), int(restaurant_id), reservation_time, seats)
            print(mess)
            flash(mess, 'booking')
            return redirect('/restaurants')
    return render_template('reserve.html', name=restaurant.name, form=form)

@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = Restaurant.getAll()
    return render_template("restaurants.html",
                           message=message,
                           restaurants=allrestaurants,
                           base_url='restaurants')


@restaurants.route('/restaurants/<restaurant_id>',
                   methods=['GET', 'POST'])
def restaurant_sheet(restaurant_id):
    record = Restaurant.get(restaurant_id)
    if not record:
        return render_template("error.html", error_message="The page you're looking does not exists")
    if not current_user or not current_user.is_authenticated:
        return render_template("restaurantsheet.html", record=record)
    review = Review.get(restaurant_id, user_id=current_user.id)
    if review is not None:
        # show the user their updated view
        record.update_review(review.stars)
    if current_user.is_authenticated and not current_user.restaurant_id \
        and review is None:
        # the user is logged and hasn't already a review for this restaurant
        form = RatingForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    if form.review is not None:
                        Review.add(restaurant_id, current_user.id, int(request.form.get("stars_number")), text=str(form.review.data))                                       
                    else:
                        Review.add(restaurant_id, current_user.id, int(request.form.get("stars_number"))) 
                    # update review count immediately so user can see it
                    record.update_review(int(request.form.get("stars_number")))
                except GoOutSafeError as e:
                    return render_template("error.html", error_message=str(e))
        else:
            return render_template("restaurantsheet.html", form=form, record=record)

    return render_template("restaurantsheet.html", record=record)




@restaurants.route('/restaurants/edit/<restaurant_id>', methods=['GET', 'POST'])
@login_required
def _edit(restaurant_id):
    if (not current_user.restaurant_id) or current_user.restaurant_id != int(restaurant_id):
        return render_template("error.html", error_message="You haven't the permissions to access this page")
    r = Restaurant.get(restaurant_id)
    form = RestaurantProfileEditForm(obj=r)

    tables = RestaurantTable.get(r.id)
    
    if request.method == 'POST':
        try:
            if not form.validate_on_submit:
                raise FormValidationError("Can't validate the form")
            Restaurant.update(restaurant_id, request.form, phone=form.phone.data, extra_info=form.extra_info.data)
            return redirect('/restaurants/edit/' + restaurant_id)
        except GoOutSafeError as e:
            return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)

    return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)