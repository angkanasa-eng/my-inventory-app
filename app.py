from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from functools import wraps
from datetime import datetime
import pandas as pd
import io
import math

app = Flask(__name__)
app.secret_key = 'kku_computing_secret_key'

# 1. ผู้ใช้งานและสิทธิ์ (Admin, Staff, Customer)
USERS = {
    "admin": {"password": "123", "role": "admin", "name": "ผู้ดูแลระบบ"},
    "staff": {"password": "123", "role": "staff", "name": "พนักงานคลัง"},
    "customer": {"password": "123", "role": "customer", "name": "ลูกค้าทั่วไป"}
}

# 2. ทะเบียนสินค้า 50 รายการ
products = [
    # --- หมวดอุปกรณ์สำนักงาน ---
    {"sku": "SKU-001", "name": "กระดาษ A4 80gsm (Double A)", "category": "อุปกรณ์สำนักงาน", "unit": "รีม", "cost_price": 105.00, "sell_price": 135.00, "qty": 8, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-002", "name": "กระดาษ A4 70gsm (Idea Work)", "category": "อุปกรณ์สำนักงาน", "unit": "รีม", "cost_price": 95.00, "sell_price": 120.00, "qty": 45, "reorder_point": 15, "warehouse": "คลัง A"},
    {"sku": "SKU-003", "name": "คลิปหนีบกระดาษ เบอร์ 110", "category": "อุปกรณ์สำนักงาน", "unit": "กล่อง", "cost_price": 18.00, "sell_price": 30.00, "qty": 60, "reorder_point": 20, "warehouse": "คลัง A"},
    {"sku": "SKU-004", "name": "ลวดเย็บกระดาษ เบอร์ 10", "category": "อุปกรณ์สำนักงาน", "unit": "กล่อง", "cost_price": 8.00, "sell_price": 15.00, "qty": 5, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-005", "name": "เครื่องเย็บกระดาษ HD-10", "category": "อุปกรณ์สำนักงาน", "unit": "อัน", "cost_price": 45.00, "sell_price": 75.00, "qty": 18, "reorder_point": 5, "warehouse": "คลัง A"},
    {"sku": "SKU-006", "name": "เทปกาวสองหน้า 24mm", "category": "อุปกรณ์สำนักงาน", "unit": "ม้วน", "cost_price": 22.00, "sell_price": 35.00, "qty": 30, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-007", "name": "เทปใส 3/4 นิ้ว", "category": "อุปกรณ์สำนักงาน", "unit": "ม้วน", "cost_price": 12.00, "sell_price": 20.00, "qty": 50, "reorder_point": 15, "warehouse": "คลัง A"},
    {"sku": "SKU-008", "name": "แท่นตัดเทปตั้งโต๊ะ", "category": "อุปกรณ์สำนักงาน", "unit": "อัน", "cost_price": 65.00, "sell_price": 99.00, "qty": 3, "reorder_point": 5, "warehouse": "คลัง A"},
    {"sku": "SKU-009", "name": "กาวลาเท็กซ์ 8 ออนซ์", "category": "อุปกรณ์สำนักงาน", "unit": "ขวด", "cost_price": 25.00, "sell_price": 40.00, "qty": 22, "reorder_point": 8, "warehouse": "คลัง A"},
    {"sku": "SKU-010", "name": "กาวแท่ง 22 กรัม", "category": "อุปกรณ์สำนักงาน", "unit": "แท่ง", "cost_price": 18.00, "sell_price": 30.00, "qty": 40, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-011", "name": "กรรไกร 7 นิ้ว (ตราช้าง)", "category": "อุปกรณ์สำนักงาน", "unit": "เล่ม", "cost_price": 35.00, "sell_price": 55.00, "qty": 12, "reorder_point": 5, "warehouse": "คลัง A"},
    {"sku": "SKU-012", "name": "คัตเตอร์ใหญ่ L-500", "category": "อุปกรณ์สำนักงาน", "unit": "อัน", "cost_price": 40.00, "sell_price": 65.00, "qty": 4, "reorder_point": 8, "warehouse": "คลัง A"},
    {"sku": "SKU-013", "name": "ใบคัตเตอร์ L-150 (แพ็ค 6 ใบ)", "category": "อุปกรณ์สำนักงาน", "unit": "แพ็ค", "cost_price": 20.00, "sell_price": 35.00, "qty": 25, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-014", "name": "แฟ้มสัมมนาตราช้าง A4", "category": "อุปกรณ์สำนักงาน", "unit": "เล่ม", "cost_price": 42.00, "sell_price": 65.00, "qty": 35, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-015", "name": "แฟ้มสันห่วง 2 นิ้ว A4", "category": "อุปกรณ์สำนักงาน", "unit": "เล่ม", "cost_price": 55.00, "sell_price": 85.00, "qty": 14, "reorder_point": 8, "warehouse": "คลัง A"},

    # --- หมวดเครื่องเขียน ---
    {"sku": "SKU-016", "name": "ปากกาลูกลื่น น้ำเงิน 0.5mm", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 5.00, "sell_price": 10.00, "qty": 155, "reorder_point": 30, "warehouse": "คลัง A"},
    {"sku": "SKU-017", "name": "ปากกาลูกลื่น แดง 0.5mm", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 5.00, "sell_price": 10.00, "qty": 80, "reorder_point": 20, "warehouse": "คลัง A"},
    {"sku": "SKU-018", "name": "ปากกาลูกลื่น ดำ 0.5mm", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 5.00, "sell_price": 10.00, "qty": 65, "reorder_point": 20, "warehouse": "คลัง A"},
    {"sku": "SKU-019", "name": "ปากกาเจล 0.7mm สีน้ำเงิน", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 12.00, "sell_price": 22.00, "qty": 40, "reorder_point": 15, "warehouse": "คลัง A"},
    {"sku": "SKU-020", "name": "ปากกาเน้นข้อความ สียางเหลือง", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 15.00, "sell_price": 25.00, "qty": 2, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-021", "name": "ปากกาเคมีไวท์บอร์ด ดำ", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 16.00, "sell_price": 28.00, "qty": 25, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-022", "name": "ปากกาเคมีไวท์บอร์ด น้ำเงิน", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 16.00, "sell_price": 28.00, "qty": 30, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-023", "name": "ดินสอดำ 2B (กล่อง 12 แท่ง)", "category": "เครื่องเขียน", "unit": "กล่อง", "cost_price": 36.00, "sell_price": 60.00, "qty": 15, "reorder_point": 5, "warehouse": "คลัง A"},
    {"sku": "SKU-024", "name": "ดินสอกด 0.5mm", "category": "เครื่องเขียน", "unit": "ด้าม", "cost_price": 25.00, "sell_price": 45.00, "qty": 28, "reorder_point": 8, "warehouse": "คลัง A"},
    {"sku": "SKU-025", "name": "ไส้ดินสอกด 2B 0.5mm", "category": "เครื่องเขียน", "unit": "หลอด", "cost_price": 10.00, "sell_price": 18.00, "qty": 50, "reorder_point": 15, "warehouse": "คลัง A"},
    {"sku": "SKU-026", "name": "ยางลบก้อนใหญ่ (Pentel)", "category": "เครื่องเขียน", "unit": "ก้อน", "cost_price": 8.00, "sell_price": 15.00, "qty": 70, "reorder_point": 20, "warehouse": "คลัง A"},
    {"sku": "SKU-027", "name": "เทปลบคำผิด 5mm x 6m", "category": "เครื่องเขียน", "unit": "อัน", "cost_price": 20.00, "sell_price": 35.00, "qty": 9, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-028", "name": "น้ำยาลบคำผิดแบบขวด", "category": "เครื่องเขียน", "unit": "ขวด", "cost_price": 28.00, "sell_price": 45.00, "qty": 18, "reorder_point": 5, "warehouse": "คลัง A"},
    {"sku": "SKU-029", "name": "ไม้บรรทัดเหล็ก 12 นิ้ว", "category": "เครื่องเขียน", "unit": "อัน", "cost_price": 12.00, "sell_price": 25.00, "qty": 40, "reorder_point": 10, "warehouse": "คลัง A"},
    {"sku": "SKU-030", "name": "โพสต์อิท 3x3 นิ้ว สีเหลือง", "category": "เครื่องเขียน", "unit": "เล่ม", "cost_price": 22.00, "sell_price": 38.00, "qty": 6, "reorder_point": 10, "warehouse": "คลัง A"},

    # --- หมวดอุปกรณ์ไอที / อิเล็กทรอนิกส์ ---
    {"sku": "SKU-031", "name": "เม้าส์ไร้สาย Logitech M185", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "ตัว", "cost_price": 260.00, "sell_price": 390.00, "qty": 12, "reorder_point": 5, "warehouse": "คลัง B"},
    {"sku": "SKU-032", "name": "คีย์บอร์ด USB Logitech K120", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "ตัว", "cost_price": 210.00, "sell_price": 320.00, "qty": 8, "reorder_point": 5, "warehouse": "คลัง B"},
    {"sku": "SKU-033", "name": "แผ่นรองเม้าส์ แบบมีหมอนรองข้อมือ", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "อัน", "cost_price": 45.00, "sell_price": 89.00, "qty": 20, "reorder_point": 8, "warehouse": "คลัง B"},
    {"sku": "SKU-034", "name": "แฟลชไดร์ฟ 32GB Kingston", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "อัน", "cost_price": 110.00, "sell_price": 179.00, "qty": 15, "reorder_point": 5, "warehouse": "คลัง B"},
    {"sku": "SKU-035", "name": "แฟลชไดร์ฟ 64GB SanDisk", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "อัน", "cost_price": 180.00, "sell_price": 269.00, "qty": 4, "reorder_point": 5, "warehouse": "คลัง B"},
    {"sku": "SKU-036", "name": "ปลั๊กไฟ 4 ช่อง 1 สวิตช์ 3 เมตร", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "อัน", "cost_price": 190.00, "sell_price": 299.00, "qty": 10, "reorder_point": 4, "warehouse": "คลัง B"},
    {"sku": "SKU-037", "name": "สาย HDMI 1.8 เมตร", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "เส้น", "cost_price": 60.00, "sell_price": 120.00, "qty": 25, "reorder_point": 5, "warehouse": "คลัง B"},
    {"sku": "SKU-038", "name": "สายชาร์จ Type-C 1 เมตร", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "เส้น", "cost_price": 40.00, "sell_price": 99.00, "qty": 30, "reorder_point": 10, "warehouse": "คลัง B"},
    {"sku": "SKU-039", "name": "ถ่าน AA Panasonic (แพ็ค 4 ก้อน)", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "แพ็ค", "cost_price": 38.00, "sell_price": 62.00, "qty": 45, "reorder_point": 15, "warehouse": "คลัง B"},
    {"sku": "SKU-040", "name": "ถ่าน AAA Panasonic (แพ็ค 4 ก้อน)", "category": "ไอทีและอิเล็กทรอนิกส์", "unit": "แพ็ค", "cost_price": 38.00, "sell_price": 62.00, "qty": 3, "reorder_point": 15, "warehouse": "คลัง B"},

    # --- หมวดเฟอร์นิเจอร์และทำความสะอาด ---
    {"sku": "SKU-041", "name": "เก้าอี้สำนักงาน พนักพิงพลาสติก", "category": "เฟอร์นิเจอร์", "unit": "ตัว", "cost_price": 850.00, "sell_price": 1290.00, "qty": 6, "reorder_point": 2, "warehouse": "คลัง B"},
    {"sku": "SKU-042", "name": "โคมไฟตั้งโต๊ะ LED", "category": "เฟอร์นิเจอร์", "unit": "เครื่อง", "cost_price": 220.00, "sell_price": 350.00, "qty": 11, "reorder_point": 3, "warehouse": "คลัง B"},
    {"sku": "SKU-043", "name": "ถังขยะพลาสติก 10 ลิตร", "category": "ของใช้ในสำนักงาน", "unit": "ใบ", "cost_price": 40.00, "sell_price": 75.00, "qty": 14, "reorder_point": 5, "warehouse": "คลัง B"},
    {"sku": "SKU-044", "name": "ถุงขยะดำ 24x30 นิ้ว (แพ็ค 1 กิโล)", "category": "ของใช้ในสำนักงาน", "unit": "แพ็ค", "cost_price": 45.00, "sell_price": 70.00, "qty": 22, "reorder_point": 8, "warehouse": "คลัง B"},
    {"sku": "SKU-045", "name": "สเปรย์แอลกอฮอล์ 500ml", "category": "ของใช้ในสำนักงาน", "unit": "ขวด", "cost_price": 50.00, "sell_price": 89.00, "qty": 2, "reorder_point": 10, "warehouse": "คลัง B"},
    {"sku": "SKU-046", "name": "ทิชชู่ม้วนยาว (แพ็ค 6 ม้วน)", "category": "ของใช้ในสำนักงาน", "unit": "แพ็ค", "cost_price": 35.00, "sell_price": 59.00, "qty": 18, "reorder_point": 8, "warehouse": "คลัง B"},
    {"sku": "SKU-047", "name": "ทิชชู่เช็ดหน้าแบบกล่อง", "category": "ของใช้ในสำนักงาน", "unit": "กล่อง", "cost_price": 20.00, "sell_price": 35.00, "qty": 30, "reorder_point": 10, "warehouse": "คลัง B"},
    {"sku": "SKU-048", "name": "น้ำยาล้างจาน 550ml", "category": "ของใช้ในสำนักงาน", "unit": "ถุง", "cost_price": 18.00, "sell_price": 28.00, "qty": 25, "reorder_point": 5, "warehouse": "คลัง B"},
    {"sku": "SKU-049", "name": "สก็อตไบรต์ ล้างจาน", "category": "ของใช้ในสำนักงาน", "unit": "แผ่น", "cost_price": 8.00, "sell_price": 15.00, "qty": 40, "reorder_point": 10, "warehouse": "คลัง B"},
    {"sku": "SKU-050", "name": "เครื่องคิดเลข 12 หลัก (Casio)", "category": "อุปกรณ์สำนักงาน", "unit": "เครื่อง", "cost_price": 280.00, "sell_price": 450.00, "qty": 7, "reorder_point": 3, "warehouse": "คลัง A"}
]

suppliers = [{"id": "SUP-01", "name": "บจก. ออฟฟิศเมท ซัพพลาย", "contact": "02-123-4567"}]
purchase_orders = [{"po_no": "PO-2026-001", "supplier_name": "บจก. ออฟฟิศเมท ซัพพลาย", "sku": "SKU-001", "qty": 50, "status": "รอรับของ"}]
stock_logs = []

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("กรุณาเข้าสู่ระบบก่อนใช้งาน", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("เข้าถึงไม่ได้: สิทธิ์เฉพาะ Admin เท่านั้น", "danger")
            return redirect(url_for('inventory'))
        return f(*args, **kwargs)
    return decorated_function

def staff_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['admin', 'staff']:
            flash("สิทธิ์ Customer สามารถดูสินค้าได้เท่านั้น ไม่สามารถทำรายการสต็อกได้", "danger")
            return redirect(url_for('inventory'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = USERS.get(username)
        if user and user['password'] == password:
            session['user'] = username
            session['role'] = user['role']
            session['name'] = user['name']
            flash(f"ยินดีต้อนรับคุณ {user['name']} (สิทธิ์: {user['role'].upper()})", "success")
            return redirect(url_for('inventory'))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()

        if not username or not password or not name:
            flash("กรุณากรอกข้อมูลให้ครบทุกช่อง", "danger")
            return redirect(url_for('register'))

        if username in USERS:
            flash("ชื่อผู้ใช้นี้มีในระบบแล้ว กรุณาใช้ชื่ออื่น", "warning")
            return redirect(url_for('register'))

        # สมัครสมาชิกใหม่จะได้รับสิทธิ์เป็น customer เสมอ
        USERS[username] = {"password": password, "role": "customer", "name": name}
        flash("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("ออกจากระบบเรียบร้อย", "info")
    return redirect(url_for('login'))

@app.route('/')
@app.route('/inventory')
@login_required
def inventory():
    search = request.args.get('search', '').strip().lower()
    page = int(request.args.get('page', 1))
    per_page = 10  # แบ่งหน้า หน้าละ 10 รายการ

    filtered_products = []
    for p in products:
        match_search = (search in p['sku'].lower()) or (search in p['name'].lower())
        if match_search:
            p['is_low_stock'] = (p['qty'] <= p['reorder_point'])
            filtered_products.append(p)

    total_items = len(filtered_products)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_products = filtered_products[start_idx:end_idx]

    return render_template('inventory.html', 
                           products=paginated_products, 
                           search=search, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items)

@app.route('/stock/transact', methods=['POST'])
@login_required
@staff_or_admin_required
def stock_transact():
    try:
        sku = request.form.get('sku', '').strip()
        trans_type = request.form.get('trans_type')
        qty = int(request.form.get('qty', 0))
        reason = request.form.get('reason', '').strip()

        if trans_type in ['IN', 'OUT'] and qty <= 0:
            flash("จำนวนสินค้าต้องมากกว่า 0 เท่านั้น", "danger")
            return redirect(url_for('inventory'))

        if trans_type == 'ADJUST' and qty < 0:
            flash("จำนวนสต็อกคงเหลือไม่สามารถติดลบได้", "danger")
            return redirect(url_for('inventory'))

        product = next((p for p in products if p['sku'] == sku), None)
        if not product:
            flash("ไม่พบรหัสสินค้านี้ในระบบ", "danger")
            return redirect(url_for('inventory'))

        if trans_type == 'OUT' and qty > product['qty']:
            flash(f"ไม่สามารถเบิกได้! สต็อกคงเหลือปัจจุบันมีเพียง {product['qty']} {product['unit']}", "danger")
            return redirect(url_for('inventory'))

        old_qty = product['qty']
        if trans_type == 'IN':
            product['qty'] += qty
            change_txt = f"+{qty}"
        elif trans_type == 'OUT':
            product['qty'] -= qty
            change_txt = f"-{qty}"
        elif trans_type == 'ADJUST':
            product['qty'] = qty
            change_txt = f"ปรับจาก {old_qty} เป็น {qty}"

        stock_logs.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sku": sku,
            "type": "รับเข้า" if trans_type == 'IN' else ("เบิกออก" if trans_type == 'OUT' else "ปรับยอด"),
            "change": change_txt,
            "balance": product['qty'],
            "reason": reason,
            "user": session.get('name')
        })

        flash(f"ทำรายการสำเร็จ! สินค้า {sku} ยอดคงเหลือใหม่คือ {product['qty']} {product['unit']}", "success")

    except ValueError:
        flash("กรุณากรอกตัวเลขจำนวนให้ถูกต้อง", "danger")

    return redirect(url_for('inventory'))

@app.route('/stock-card/<sku>')
@login_required
def stock_card(sku):
    product = next((p for p in products if p['sku'] == sku), None)
    logs = [log for log in stock_logs if log['sku'] == sku]
    return render_template('stock_card.html', product=product, logs=logs)

@app.route('/po')
@login_required
@staff_or_admin_required
def po_management():
    return render_template('po.html', suppliers=suppliers, pos=purchase_orders)

@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_skus = len(products)
    total_items = sum(p['qty'] for p in products)
    total_cost = sum(p['qty'] * p['cost_price'] for p in products)
    total_value = sum(p['qty'] * p['sell_price'] for p in products)
    low_stock_list = [p for p in products if p['qty'] <= p['reorder_point']]
    return render_template('dashboard.html', total_skus=total_skus, total_items=total_items, total_cost=total_cost, total_value=total_value, low_stock_list=low_stock_list)

@app.route('/export/excel')
@login_required
def export_excel():
    df = pd.DataFrame(products)[['sku', 'name', 'category', 'unit', 'cost_price', 'sell_price', 'qty', 'reorder_point', 'warehouse']]
    df.columns = ['รหัส SKU', 'ชื่อสินค้า', 'หมวดหมู่', 'หน่วยนับ', 'ราคาทุน', 'ราคาขาย', 'คงเหลือ', 'จุดสั่งซื้อ', 'คลัง']
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Stock_Report')
    output.seek(0)
    return send_file(output, download_name="inventory_report.xlsx", as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    app.run(debug=True)
