from api_gateway.forms import RatingForm, ReservationForm, RestaurantProfileEditForm
from api_gateway.classes.restaurant import Restaurant, RestaurantTable, Review
from logging import error
from api_gateway.classes.exceptions import GoOutSafeError
from flask import Blueprint, redirect, render_template, request, flash
from api_gateway.auth import admin_required, current_user, login_required
from sqlalchemy import func
from datetime import datetime

restaurants = Blueprint('restaurants', __name__)


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
    review = Review.get(restaurant_id, current_user.id)
    if review is not None:
        # show the user their updated view
        record.update_review(review.stars)
    if current_user.is_authenticated and not current_user.restaurant_id \
        and review is None:
        # the user is logged and hasn't already a review for this restaurant
        form = RatingForm()
        if(request.method == 'POST'):
            if form.validate_on_submit():
                if form.review is not None:
                    Review.add(restaurant_id, current_user.id, int(request.form.get("stars_number")), text=str(form.review.data))                                       
                else:
                    Review.add(restaurant_id, current_user.id, int(request.form.get("stars_number"))) 
                # update review count immediately so user can see it
                record.update_review(int(request.form.get("stars_number")))
        else:
            return render_template("restaurantsheet.html", form=form, record=record)

    return render_template("restaurantsheet.html", record=record)


@restaurants.route('/restaurants/reserve/<restaurant_id>',
                   methods=['GET', 'POST'])
# @login_required
def _reserve(restaurant_id):
    pass
    """form = ReservationForm()
    record = Restaurant.get(restaurant_id)

    if (request.method == 'POST'):
        if ReservationForm(request.form).validate_on_submit():
            reservation_time = datetime.combine(
                ReservationForm(request.form).data['reservation_date'],
                ReservationForm(request.form).data['reservation_time'])
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=record.id,
                reservation_time=reservation_time,
                reservation_seats=ReservationForm(request.form).data['seats'],
                avg_stay_time=record.avg_stay_time)
            if (cr.is_overbooked(restaurant_id=record.id,
                                 reservation_seats=ReservationForm(
                                     request.form).data['seats'],
                                 overlapping_tables=overlapping_tables)):
                flash('Overbooking Notification: no tables with the wanted seats on the requested date and time. Please, try another one.', 'booking')
                return redirect('/restaurants')
            else:
                assigned_table = cr.assign_table_to_reservation(
                    overlapping_tables=overlapping_tables,
                    restaurant_id=record.id,
                    reservation_seats=ReservationForm(
                        request.form).data['seats'])
                reservation = Reservation(user_id=current_user.id,
                                          restaurant_id=record.id,
                                          reservation_time=reservation_time,
                                          seats=ReservationForm(
                                              request.form).data['seats'],
                                          table_no=assigned_table.table_id)
                cr.add_reservation(reservation)
                flash('Booking confirmed', 'booking')
                return redirect('/restaurants')

    return render_template('reserve.html', name=record.name, form=form)"""


@restaurants.route('/restaurants/edit/<restaurant_id>', methods=['GET', 'POST'])
@login_required
def _edit(restaurant_id):
    if (not current_user.restaurant_id) or current_user.restaurant_id != int(restaurant_id):
        return render_template("error.html", error_message="You haven't the permissions to access this page")
    r = Restaurant.query.get(restaurant_id)
    form = RestaurantProfileEditForm(obj=r)

    tables = RestaurantTable.get(r.id)
    
    if request.method == 'POST':
        try:
            Restaurant.update(restaurant_id, request.form, phone=form.phone, extra_info=form.extra_info)
            return redirect('/restaurants/edit/' + restaurant_id)
        except GoOutSafeError as e:
            return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)

    return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)