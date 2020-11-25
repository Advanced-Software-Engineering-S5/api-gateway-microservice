from flask import Blueprint, redirect, render_template, request, url_for, flash
from api_gateway.auth import admin_required, current_user, login_required
from api_gateway.classes.reservations import Reservation, ReservationState
# from api_gateway.views.reservations import prettytime
from api_gateway.forms import ReservationForm

from datetime import datetime


customer_reservations = Blueprint('customer_reservations',
                                  __name__,
                                  url_prefix='/my_reservations')

@customer_reservations.add_app_template_filter
def prettytime(value: datetime):
    """
    Pretty printing of date and time.
    """
    return value.strftime("%A %d %B - %H:%M")

@customer_reservations.add_app_template_test
def declined_reservation(reservation: Reservation):
    """
    Returns true iff the reservation has been declined.
    """
    return reservation.status is ReservationState.DECLINED


@customer_reservations.route('/', methods=('GET', ))
@login_required
def get_reservations():
    form = ReservationForm()
    reservations = Reservation.get_customer_reservations(current_user.id)
    return render_template("customer_reservations.html",
                           reservations=reservations, form=form)


@customer_reservations.route('/<reservation_id>/update',
                             methods=(
                                 'GET',
                                 'POST',
                             ))
@login_required
def update_user_reservation(reservation_id: int):
    form = ReservationForm()
    if request.method == 'POST':
        new_date = new_date = datetime.combine(form.data['reservation_date'],
                            form.data['reservation_time'])
        if (new_date <= datetime.now()):
            flash(
                'Invalid Date Error. You cannot reserve a table in the past!',
                'reservation_mod')
            return redirect('/my_reservations/')
        if form.validate_on_submit():
            new_seats = form.data['seats']
            mess = Reservation.update_customer_reservation(int(reservation_id), new_date, new_seats)
            flash(mess, 'reservation_mod')
            return redirect('/my_reservations/')
    


@customer_reservations.route('/<reservation_id>/delete',
                             methods=(
                                 'GET',
                                 'DELETE',
                             ))
@login_required
def delete_user_reservation(reservation_id: int):
    mess = Reservation.delete_customer_reservation(int(reservation_id))
    flash(mess, 'reservation_mod')
    return redirect(request.referrer)
