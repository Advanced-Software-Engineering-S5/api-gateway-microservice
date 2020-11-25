from flask import Blueprint, redirect, render_template, request, url_for, flash
from api_gateway.auth import current_user, login_required, operator_required
from api_gateway.classes.reservations import Reservation, ReservationState
from api_gateway.classes.user import User
from datetime import datetime, time
import logging

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')


@reservations.add_app_template_filter
def prettytime(value: datetime):
    """
    Pretty printing of date and time.
    """
    return value.strftime("%A %d %B - %H:%M")


@reservations.add_app_template_filter
def prettyhour(value: datetime):
    """
    Pretty printing of time only.
    """
    return value.strftime("%H:%M")


@reservations.add_app_template_test
def modifiable_reservation(reservation: Reservation):
    """
    Returns true iff the reservation is still modifiable, i.e. if the reservation time is not yet due.
    """
    return reservation.reservation_time > datetime.now()


@reservations.add_app_template_test
def accepted_reservation(reservation: Reservation):
    """
    Returns true iff the reservation has been accepted.
    """
    return reservation.status is ReservationState.ACCEPTED


@reservations.add_app_template_test
def declined_reservation(reservation: Reservation):
    """
    Returns true iff the reservation has been declined.
    """
    return reservation.status is ReservationState.DECLINED


@reservations.add_app_template_test
def show_mark_buttons(reservation: Reservation):
    """
    Returns true iff the mark buttons have to be shown, i.e. if the reservation is atleast accepted and it is past due.
    """
    logging.info(datetime.now())
    return reservation.status.value > ReservationState.PENDING and reservation.reservation_time <= datetime.now()


@reservations.add_app_template_test
def entrance_marked(reservation: Reservation):
    """
    Returns true if the entrance has been marked.
    """
    return reservation.status.value >= ReservationState.SEATED.value


@reservations.add_app_template_test
def exit_marked(reservation: Reservation):
    """
    Returns true if the exit has been marked.
    """
    return reservation.status is ReservationState.DONE

def update_status(reservation_id: int, status: int, time: datetime = None):
    res = Reservation.get_reservation(reservation_id = int(reservation_id))
    if (res is not None and res.restaurant_id == current_user.restaurant_id):
         mess = Reservation.update_reservation_status(reservation_id=int(reservation_id), status=status, time=time)
         return mess
    return None


@reservations.route('/', defaults={'page': 1})
@reservations.route('/page/<int:page>', methods=('GET', ))
@operator_required
def home(page: int):
    reservations, more = Reservation.get_paged_reservations(restaurant_id=current_user.restaurant_id, page=page)
    users = []
    for reservation in reservations:
        user = User.get(id=reservation.user_id)
        users.append(user)
    res = zip(reservations, users)
    if not reservations and page > 1:
        return "", 404
    else:
        return render_template("reservations.html",
                               reservations=res,
                               current_page=page,
                               morepages=more,
                               customers=Reservation.get_seated_customers(restaurant_id=current_user.restaurant_id),
                               today=False)


@reservations.route('/today', defaults={'page': 1})
@reservations.route('/today/page/<int:page>', methods=('GET', ))
@operator_required
def today(page: int):
    reservations, more = Reservation.get_paged_reservation_of_today(restaurant_id=current_user.restaurant_id, page=page)
    users = []
    for reservation in reservations:
        user = User.get(id=reservation.user_id)
        logging.info(user)
        users.append(user)
    
    res = zip(reservations, users)
    if not reservations and page > 1:
        return "", 404
    else:
        return render_template("reservations.html",
                               reservations=res,
                               current_page=page,
                               morepages=more,
                               customers=Reservation.get_seated_customers(restaurant_id=current_user.restaurant_id),
                               today=False)


@reservations.route('/<reservation_id>/decline', methods=('POST', ))
@operator_required
def decline(reservation_id: int):
    mess = update_status(reservation_id=reservation_id, status=0)
    if mess:
         flash(mess, 'status_update')
         return redirect(request.referrer)
    flash('You are not allowed to do that', 'status_update')
    return redirect(request.referrer)


@reservations.route('/<reservation_id>/accept', methods=('POST', ))
@operator_required
def accept(reservation_id: int):
    mess = update_status(reservation_id=reservation_id, status=2)
    print(mess)
    if mess:
        flash(mess, 'status_update')
        return redirect(request.referrer)
    flash('You are not allowed to do that', 'status_update')
    return redirect(request.referrer)



@reservations.route('/<reservation_id>/markentrance', methods=('POST', ))
@operator_required
def mark_entrance(reservation_id: int):
    mess = update_status(reservation_id=reservation_id, status=3, time=datetime.now())
    if mess:
        flash(mess, 'status_update')
        return redirect(request.referrer)
    flash('You are not allowed to do that', 'status_update')
    return redirect(request.referrer)



@reservations.route('/<reservation_id>/markexit', methods=('POST', ))
@operator_required
def mark_exit(reservation_id: int):
    mess = update_status(reservation_id=reservation_id, status=4, time=datetime.now())
    if mess:
        flash(mess, 'status_update')
        return redirect(request.referrer)
    flash('You are not allowed to do that', 'status_update')
    return redirect(request.referrer)

