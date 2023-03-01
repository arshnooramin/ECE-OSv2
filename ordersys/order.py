import re
from flask import *
from ordersys.emailer import *
from ordersys.db import get_db
from flask_login import login_required, current_user
from ordersys.enums import *
from ordersys.project import update_cost as project_update_cost
from ordersys.user import User

bp = Blueprint('order', __name__, url_prefix='/order')

@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new_order():
    db = get_db()
    cur = db.cursor()
    
    item_costs = 0

    if request.method == 'POST':
        if request.form['vendor'] == 'Other':
            vendor = request.form['vendor-other-name']
            vendor_url = request.form['vendor-other-url']
            if '//' in vendor_url:
                vendor_url = vendor_url.split('//')[1]
        else:
            vendor = request.form['vendor']
            vendor_url = vendors[vendor]
        
        order_data = (
            current_user.project_id,
            vendor,
            vendor_url,
            request.form['order-date'],
            request.form['order-speed'],
        )
        
        cur.execute('INSERT INTO eorder (project_id, vendor, vendor_url, order_time, shipping_speed) VALUES (?, ?, ?, ?, ?)', order_data)
        order_id = cur.lastrowid

        db.commit()

        item_nums = set()
        for f_re in request.form:
            c_item_num = f_re.split('-')[-1]
            if c_item_num.isnumeric() and c_item_num not in item_nums:
                item_nums.add(c_item_num)
        
        for item_num in item_nums:
            item_costs += float(request.form['item-price-' + item_num])*float(request.form['item-quantity-' + item_num])
            item_data = (
                order_id,
                request.form['item-description-' + item_num],
                request.form['item-number-' + item_num],
                request.form['item-price-' + item_num],
                request.form['item-quantity-' + item_num],
                request.form['item-justification-' + item_num]
            )

            db.execute('INSERT INTO item (order_id, description, item_number, price, quantity, justification) VALUES (?, ?, ?, ?, ?, ?)', item_data)
            db.commit()
        
        db.execute('UPDATE eorder SET item_costs = ? WHERE id = ?', (item_costs, order_id,))
        db.commit()

        project_update_cost(current_user.project_id, item_costs)
        send_order_email(order_id, vendor, url_for('project.index_admin', project_id=current_user.project_id), current_user)
        flash('Order successfully created.', 'success')
        return redirect(url_for('project.index'))

    return render_template('order/new.html', vendors=vendors)

@bp.route('/edit/<int:order_id>', methods=('GET', 'POST'))
@login_required
def edit_order(order_id):
    db = get_db()

    order = db.execute(
        "SELECT * FROM eorder WHERE id = ?", (order_id,)
    ).fetchone()
    user = db.execute(
        "SELECT user_id FROM project WHERE id = ?", (order["project_id"],)
    ).fetchone()

    if request.method == 'POST':
        track_url = request.form['order-track-url']
        if '//' in track_url:
            track_url = track_url.split('//')[1]
        order_data = (
            request.form['order-date'],
            request.form['order-speed'],
            request.form['order-status'],
            track_url,
            request.form['order-shipping-costs'],
            None if int(request.form['order-courier']) < 0 else request.form['order-courier'],
            order_id
        )

        db.execute('UPDATE eorder SET order_time = ?, shipping_speed = ?, status = ?, track_url = ?, shipping_costs = ?, courier = ? WHERE id = ?', order_data)
        db.commit()

        project_update_cost(order['project_id'], -1*order['shipping_costs'])
        project_update_cost(order['project_id'], request.form['order-shipping-costs'])

        if status_enum[order['status']] != status_enum[int(request.form['order-status'])]:
            send_status_email(order_id, order['vendor'], status_enum[int(request.form['order-status'])], url_for('project.index'), User.get(user['user_id']))

        flash('Order successfully modified.', 'success')
        return redirect(session['prev_project'])
    
    return render_template('order/edit.html', order=order, vendors=vendors, status_enum=status_enum, order_speed_enum=order_speed_enum, order_date_enum=order_date_enum, courier_enum=courier_enum)

@bp.route('/delete/<int:order_id>/')
@login_required
def delete_order(order_id):
    db = get_db()
    
    order = db.execute(
        "SELECT * FROM eorder WHERE id = ?", (order_id,)
    ).fetchone()

    db.execute('DELETE FROM eorder WHERE id = ?', (order_id,))
    db.commit()

    project_update_cost(order['project_id'], -1*(order['item_costs'] + order['shipping_costs']))
    
    flash('Order successfully deleted.', 'success')
    return redirect(session['prev_project']) if current_user.is_admin() else redirect(url_for('project.index'))