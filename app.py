from flask import Flask, render_template, request, redirect, flash
from flask import render_template
from mysql import connector
from flask import request, redirect, url_for, session
from flask import flash
from datetime import datetime
import mysql.connector



app = Flask(__name__)


app.secret_key = 'kantin amikom'


db = connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='kantin3'
)

if db.is_connected():
    print('Koneksi berhasil dibuka')


# Page login


@app.route('/')
def home():
    if not session.get('loggedin'):
        return redirect('/login')
    else:
        return redirect('/order/')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute(
            'SELECT level FROM users WHERE username = %s AND password = %s',
            (username, password,)
        )
        user = cursor.fetchone()
        if user and user[0] == 'kasir':
            session['loggedin'] = True
            session['username'] = username
            message = 'Berhasil login!'
            return redirect('/order/')
        elif user and user[0] == 'user':
            session['loggedin'] = True
            session['username'] = username
            message = 'Berhasil login!'
            return redirect('/menu/')
        else:
            message = 'Silakan masukkan Username/kata sandi yang benar!'
    return render_template('login.html', message=message)

#page Register

@app.route('/register/', methods=['GET', 'POST'])
def register():
    message = None
    success = request.args.get('success')
    if success:
        message = "Registrasi berhasil"
    return render_template('register.html', message=message)

@app.route('/proses_register/', methods=['POST'])
def tambah_register():
    username = request.form['username']
    password = request.form['password']
    level = 'user'
    
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO users (username, password, level) VALUES (%s, %s, %s)", (username, password, level))
        db.commit()
        flash('Registrasi berhasil', 'success')
        return redirect(url_for('login', success='true'))
    except mysql.connector.IntegrityError as e:
        error_message = str(e)
        if "Duplicate entry" in error_message and "'username'" in error_message:
            flash('Username sudah digunakan, silakan gunakan username lain.', 'danger')
        else:
            flash('Terjadi kesalahan saat melakukan registrasi.', 'danger')
        return redirect(url_for('register'))

# Page Menu

@app.route('/edit_menu/')
def edit_menu():
    cursor = db.cursor()
    cursor.execute('select * from menu')
    result = cursor.fetchall()
    cursor.close()
    return render_template('kasir/edit_menu.html', hasil = result)

@app.route('/tambah_menu/')
def tambah_menu():
    return render_template('kasir/tambah_menu.html')

@app.route('/proses_tambah_menu/', methods = ['POST'])
def tambah_menu_baru():
    nama_menu = request.form['nama_menu']
    deskripsi = request.form['deskripsi']
    harga = request.form['harga2']
    kategori = request.form['kategori']
    cur = db.cursor()
    cur.execute("INSERT INTO menu (nama_item, deskripsi, harga, kategori) VALUES (%s, %s, %s, %s)", (nama_menu, deskripsi, harga, kategori))
    db.commit()
    return redirect(url_for('edit_menu'))
    
@app.route('/hapus_menu/<id>', methods = ['GET'])
def hapus_menu(id):
    cur = db.cursor()
    cur.execute('DELETE from menu where id=%s', (id,))
    db.commit()
    return redirect(url_for('edit_menu'))

@app.route('/ubah_menu/<id>', methods=['GET'])
def ubah_menu(id):
    cur = db.cursor()
    cur.execute('select * from menu where id=%s', (id,))
    res = cur.fetchall()
    cur.close()
    return render_template('kasir/edit_menu2.html', hasil = res)

@app.route('/proses/ubah_menu/', methods=['POST'])
def proses_ubah_menu():
    nama_menu = request.form['nama_menu']
    nama_menu2 = request.form['nama_menu2']
    deskripsi = request.form['deskripsi']
    harga2 = request.form['harga2']
    kategori = request.form['kategori']
    cur = db.cursor()
    sql = "UPDATE menu SET nama_item=%s, deskripsi=%s, harga=%s, kategori=%s WHERE nama_item=%s"
    values = (nama_menu2, deskripsi, harga2, kategori, nama_menu)
    cur.execute(sql, values)
    db.commit()
    return redirect(url_for('edit_menu'))

# Page order

@app.route('/order/')
def order():
    if not session.get('loggedin'):
        return redirect('/login')

    cursor = db.cursor()
    cursor.execute('SELECT * FROM pesanan ORDER BY nama')
    results = cursor.fetchall()

    orders_by_user = {}
    for row in results:
        username = row[1]
        if username not in orders_by_user:
            orders_by_user[username] = {'orders': [], 'total_price': 0.0}
        harga_barang = float(row[5])
        orders_by_user[username]['orders'].append(row)
        orders_by_user[username]['total_price'] += harga_barang * row[4]

    cursor.close()

    return render_template('kasir/order.html', orders_by_user=orders_by_user)

@app.route('/disable_order/<pesanan_id>', methods=['POST'])
def disable_order(pesanan_id):
    cursor = db.cursor()
    cursor.execute('SELECT status FROM pesanan WHERE id_pesanan = %s', (pesanan_id,))
    status = cursor.fetchone()[0]

    new_status = 'disabled' if status != 'disabled' else 'enabled'
    cursor.execute('UPDATE pesanan SET status = %s WHERE id_pesanan = %s', (new_status, pesanan_id))
    db.commit()

    return redirect(url_for('order'))

# Page Transaksi

@app.route('/transaksi/')
def transaksi():
    cursor = db.cursor()
    cursor.execute('select * from transaksi')
    result = cursor.fetchall()
    cursor.close()
    return render_template('kasir/transaksi.html', hasil = result)

# Page User

@app.route('/menu/')
def menu():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM menu')
    result = cursor.fetchall()
    cursor.close()
    return render_template('user/menu.html', hasil=result)


@app.route('/makanan/')
def makanan():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM menu WHERE kategori = %s', ('makanan',))
    result = cursor.fetchall()
    cursor.close()
    return render_template('user/makanan.html', hasil = result)

@app.route('/minuman/')
def minuman():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM menu WHERE kategori = %s', ('minuman',))
    result = cursor.fetchall()
    cursor.close()
    return render_template('user/minuman.html',hasil = result)

@app.route('/add_to_cart/', methods=['POST'])
def add_to_cart():
    item_id = request.form.get('item_id')
    if 'cart' not in session:
        session['cart'] = []
    if item_id not in session['cart']:
        session['cart'].append(item_id)
        session.modified = True
    return redirect(url_for('menu'))

@app.route('/add_to_cart2/', methods=['POST'])
def add_to_cart2():
    item_id = request.form.get('item_id')
    if 'cart' not in session:
        session['cart'] = []
    if item_id not in session['cart']:
        session['cart'].append(item_id)
        session.modified = True
    return redirect(url_for('makanan'))

@app.route('/add_to_cart3/', methods=['POST'])
def add_to_cart3():
    item_id = request.form.get('item_id')
    if 'cart' not in session:
        session['cart'] = []
    if item_id not in session['cart']:
        session['cart'].append(item_id)
        session.modified = True
    return redirect(url_for('minuman'))

@app.route('/cart/')
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('user/cart2.html')
    
    cursor = db.cursor()
    placeholders = ','.join(['%s'] * len(session['cart']))
    query = 'SELECT id, nama_item, harga FROM menu WHERE id IN ({})'.format(placeholders)
    cursor.execute(query, session['cart'])
    items = cursor.fetchall()
    cursor.close()
    
    return render_template('user/cart.html', items=items)

@app.route('/checkout/', methods=['POST'])
def checkout():
    if 'username' not in session:
        flash("Anda perlu login untuk melakukan tindakan ini.", "error")
        return redirect(url_for('login'))

    if 'cart' not in session or not session['cart']:
        flash("Keranjang Anda kosong.", "error")
        return redirect(url_for('cart'))

    cursor = db.cursor()
    total_harga = 0.0
    pesanan_ids = []
    nama = session['username']
    meja = request.form['meja']
    
    try:
        cursor.execute('SELECT username FROM users WHERE username = %s AND level = %s', (nama, 'user'))
        user_exists = cursor.fetchone()

        if user_exists:
            for item_id in session['cart']:
                jumlah = float(request.form.get('jumlah_' + str(item_id), 0))
                catatan = request.form.get('catatan_' + str(item_id), '')
                
                cursor.execute('SELECT nama_item, harga FROM menu WHERE id = %s', (item_id,))
                menu_item = cursor.fetchone()

                if menu_item:
                    harga_per_item = float(menu_item[1])
                    harga_total_item = harga_per_item * jumlah
                    total_harga += harga_total_item

                    query = 'INSERT INTO pesanan (nama, meja, nama_menu, harga, catatan, quantity) VALUES (%s, %s, %s, %s, %s, %s)'
                    total_harga_formatted = '{:,.3f}'.format(harga_total_item).replace(',', '.')
                    cursor.execute(query, (nama, meja, menu_item[0], total_harga_formatted, catatan, jumlah))

                    pesanan_id = cursor.lastrowid
                    pesanan_ids.append(pesanan_id)

            for pesanan_id in pesanan_ids:
                query = 'INSERT INTO transaksi (username, id_pesanan, quantity, pesanan, time) VALUES (%s, %s, %s, %s, %s)'
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Mendapatkan timestamp saat ini
                cursor.execute(query, (nama, pesanan_id, jumlah, menu_item[0], current_time))

            db.commit()
            session.pop('cart', None)

            total_harga_formatted = '{:,.3f}'.format(total_harga).replace(',', '.')
            return render_template('user/checkout_success.html', total_harga=total_harga_formatted)
        else:
            flash("Username tidak valid", "error")
            return redirect(url_for('cart'))

    except Exception as e:
        db.rollback()
        flash(f"Terjadi kesalahan saat checkout: {str(e)}", "error")
        return redirect(url_for('cart'))

    finally:
        cursor.close()


@app.route('/hapus_item/<item_id>', methods=['GET'])
def hapus_item(item_id):
    if 'cart' in session and item_id in session['cart']:
        session['cart'].remove(item_id)
        flash(f'Item berhasil dihapus dari keranjang.', 'success')
    return redirect(url_for('cart'))


# General


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__== '__main__':
    app.run()    