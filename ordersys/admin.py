from flask import *
import os
from sqlite3 import IntegrityError
from string import ascii_uppercase
from datetime import datetime
from ordersys.enums import *
import xlsxwriter
from ordersys.db import get_db, init_db, populate_db
from flask_login import login_required
from ordersys.auth import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=('GET', 'POST'))
@login_required
@admin_required
def index():
    db = get_db()
    projects = db.execute(
        'SELECT p.id AS project_id, p.name AS project_name, p.total AS project_total, u.name AS user_name, u.id AS user_id, u.email AS user_email, p.name AS project_name, p.total AS total FROM project p LEFT JOIN user u ON p.id = u.project_id'
    ).fetchall()
    admins = db.execute(
        'SELECT * FROM user WHERE auth_level = 0'
    ).fetchall()
    
    if request.method == 'POST':
        if request.form['type'] == 'csv':
            csv_proj = list()
            all = list()
            for project in projects:
                all.append(project)
                if request.form.get(f"{project['project_id']}-project-check"):
                    csv_proj.append(project)
            if request.form.get('all-project-check'):
                fname = xlsx_gen(all)
            else:
                fname = xlsx_gen(csv_proj)
            return send_file(fname, as_attachment=True)

        elif request.form['type'] == 'project':
            project_name = request.form['project-name']
            db.execute('INSERT INTO project (name) VALUES (?)', (project_name,))
            db.commit()
            flash('New project successfully added.', 'success')
            return redirect(url_for("admin.index"))
        elif request.form['type'] == 'user':
            if '@' in request.form['email']:
                flash('Only include username when adding a PM (exclude @bucknell.edu)', 'error')
                return redirect(url_for('admin.index'))
            cur = db.cursor()
            user_data = (
                str(request.form['project-id']), 
                request.form['user-name'],
                request.form['email'] + '@bucknell.edu', 1
            )

            project = db.execute(
                "SELECT * FROM project WHERE id = ?", (request.form['project-id'],)
            ).fetchone()
            if project['user_id'] != None:
                flash('Project already has an assigned PM.', 'error')
            else:
                try:
                    cur.execute(
                        'INSERT INTO user (project_id, name, email, auth_level) VALUES (?, ?, ?, ?);', user_data
                    )
                except IntegrityError as err:
                    if 'UNIQUE' in err.args[0]:
                        flash('User already exists. You can not add or reassign existing users.', 'error')
                    else:
                        flash('Database integrity error.', 'error')
                    return redirect(url_for("admin.index"))
                user_id = cur.lastrowid
                db.execute('UPDATE project SET user_id = ? WHERE id = ?', (user_id, request.form['project-id'],))
                db.commit()
                flash('New PM successfully added.', 'success')
            return redirect(url_for("admin.index"))
        elif request.form['type'] == 'admin':
            if '@' in request.form['email']:
                flash('Only include username when adding a PM (exclude @bucknell.edu)', 'error')
                return redirect(url_for('admin.index'))
            cur = db.cursor()
            user_data = (
                0, 
                request.form['user-name'],
                request.form['email'] + '@bucknell.edu', 0
            )
            try:
                cur.execute(
                    'INSERT INTO user (project_id, name, email, auth_level) VALUES (?, ?, ?, ?);', user_data
                )
            except IntegrityError as err:
                if 'UNIQUE' in err.args[0]:
                    flash('User already exists. You can not add or reassign existing users.', 'error')
                else:
                    flash('Database integrity error.', 'error')
                return redirect(url_for("admin.index"))
            db.commit()
            flash('New Admin successfully added.', 'success')
            return redirect(url_for("admin.index"))

    return render_template('admin/index.html', projects=projects, admins=admins)

@bp.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    db = get_db()
    
    db.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.execute('UPDATE project SET user_id = ? WHERE user_id = ?', (None, user_id,))
    db.commit()
    flash('User successfully deleted.', 'success')

    return redirect(url_for('admin.index'))

@bp.route('/reset_db')
@login_required
@admin_required
def reset_db():
    db = get_db()
    
    db.execute('DROP TABLE eorder')
    db.execute('DROP TABLE item')
    db.execute('DROP TABLE project')
    db.execute('DROP TABLE user')

    init_db()
    populate_db()
    
    db.commit()
    flash('Database successfully resetted.', 'success')

    return redirect(url_for('auth.logout'))

def xlsx_gen(csv_proj):
    db = get_db()
    headers = [
        'Timestamp',
        'Vendor',
        'Vendor URL',
        'Item Description',
        'Item Number',
        'Item Price',
        'Item Quantity',
        'Item Justification',
        'Order Date',
        'Shipping Speed',
        'Order Subtotal',
        'Shipping Costs',
        'Order Total',
        'Order Status',
        'Tracking',
        'Courier'
    ]

    fname = os.path.join(current_app.root_path, 'outputs', datetime.now().strftime('eceordering-%Y-%m-%d-%H-%M.xlsx'))
    xfile = xlsxwriter.Workbook(fname)
    fbold = xfile.add_format({'bold': 1})
    fdollar = xfile.add_format({'num_format': '$ #,##0.00'})
    fdt = xfile.add_format({'num_format': 'mm/dd/yyyy hh:mm:ss'})
    
    for project in csv_proj:
        row = 1
        
        csheet = xfile.add_worksheet(project['project_name'])
        
        csheet.set_column(0, 15, 20)

        for idx, header in enumerate(headers):
            csheet.write(ascii_uppercase[idx] + '1', header, fbold)

        orders = db.execute(
            'SELECT * FROM eorder WHERE project_id = ?', (project['project_id'],)
        ).fetchall()
        for order in orders:
            items = db.execute(
                'SELECT * FROM item WHERE order_id = ?', (order['id'],)
            ).fetchall()
            
            merge_cols = [0, 1, 2, 8, 9, 10, 11, 12, 13, 14, 15]
            for c in merge_cols:
                csheet.merge_range(row, c, row + len(items) - 1, c, "")

            for item in items:
                col = 0
                csheet.write_datetime(row, col, order['created'], fdt); col += 1
                csheet.write_string(row, col, order['vendor']); col += 1
                csheet.write_url(row, col, order['vendor_url']); col += 1
                csheet.write_string(row, col, item['description']); col += 1
                csheet.write_string(row, col, item['item_number']); col += 1
                csheet.write_number(row, col, item['price'], fdollar); col += 1
                csheet.write_number(row, col, item['quantity']); col += 1
                csheet.write_string(row, col, item['justification']); col += 1
                csheet.write_string(row, col, order_date_enum[order['order_time']]); col += 1
                csheet.write_string(row, col, order_speed_enum[order['shipping_speed']]); col += 1
                csheet.write_number(row, col, order['item_costs'], fdollar); col += 1
                csheet.write_number(row, col, order['shipping_costs'], fdollar); col += 1
                csheet.write_number(row, col, order['item_costs'] + order['shipping_costs'], fdollar); col += 1
                csheet.write_string(row, col, status_enum[order['status']]); col += 1
                csheet.write_url(row, col, 'None' if not  order['track_url'] else order['track_url']); col += 1
                csheet.write_string(row, col, 'None' if not order['courier'] else courier_enum[order['courier']]); col += 1
                row += 1

    xfile.close()

    return fname


