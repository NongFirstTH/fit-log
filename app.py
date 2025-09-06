from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import FitLogDB
from utils.calculations import *
import matplotlib
matplotlib.use('Agg')  # ใช้ backend ที่ไม่ต้องการ GUI
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['DejaVu Sans']  # ตั้งค่าฟอนต์
import io
import base64
import pandas as pd
from datetime import date
import matplotlib.dates as mdates

app = Flask(__name__)
app.secret_key = 'secret-key'  # เปลี่ยนเป็น secret key ของคุณ

# สร้าง instance ของ database
db = FitLogDB()

@app.route('/test')
def test():
    users = db.get_all_users()
    return users.to_dict(orient='records')

@app.route('/')
def index():
    """หน้าแรก"""
    users = db.get_all_users()
    current_user_id = session.get('current_user_id')
    
    stats = None
    if current_user_id:
        stats = db.get_user_stats(current_user_id)
    
    return render_template('index.html', users=users, current_user=current_user_id, stats=stats)

@app.route('/set_current_user/<int:user_id>')
def set_current_user(user_id):
    """ตั้งค่าผู้ใช้ปัจจุบัน"""
    session['current_user_id'] = user_id
    session['current_user_name'] = db.get_user_by_id(user_id)['name']
    flash('เปลี่ยนผู้ใช้สำเร็จ!', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    """จัดการ Profile User"""
    users = db.get_all_users()
    current_user_id = session.get('current_user_id')
    current_user = None
    
    if current_user_id:
        current_user = db.get_user_by_id(current_user_id)
    
    return render_template('profile.html', users=users, current_user=current_user)

@app.route('/add_user', methods=['POST'])
def add_user():
    """เพิ่มผู้ใช้ใหม่"""
    name = str(request.form.get('name'))
    weight = float(request.form.get('weight'))
    height = float(request.form.get('height'))
    age = int(request.form.get('age'))
    target_weight = float(request.form.get('target_weight'))
    
    if db.add_user(name, weight, height, age, target_weight):
        # เพิ่มน้ำหนักเริ่มต้นลงในประวัติ
        users = db.get_all_users()
        new_user_id = users['user_id'].max()
        db.add_weight_record(new_user_id, date.today().strftime('%Y-%m-%d'), weight, 'น้ำหนักเริ่มต้น')
        
        flash('เพิ่มผู้ใช้สำเร็จ!', 'success')
    else:
        flash('เกิดข้อผิดพลาดในการเพิ่มผู้ใช้', 'error')
    
    return redirect(url_for('profile'))

@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    """อัพเดตข้อมูลผู้ใช้"""
    name = request.form.get('name')
    weight = float(request.form.get('weight')) if request.form.get('weight') else None
    height = float(request.form.get('height')) if request.form.get('height') else None
    age = int(request.form.get('age')) if request.form.get('age') else None
    target_weight = float(request.form.get('target_weight')) if request.form.get('target_weight') else None
    
    if db.update_user(user_id, name, weight, height, age, target_weight) is not None:
        flash('อัพเดตข้อมูลผู้ใช้สำเร็จ!', 'success')
    else:
        flash('เกิดข้อผิดพลาดในการอัพเดตข้อมูล', 'error')
    
    return redirect(url_for('profile'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    """ลบผู้ใช้"""
    if db.delete_user(user_id):
        # ลบผู้ใช้ออกจาก session หากเป็นผู้ใช้ปัจจุบัน
        if session.get('current_user_id') == user_id:
            session.pop('current_user_id', None)
        flash('ลบผู้ใช้สำเร็จ!', 'success')
    else:
        flash('เกิดข้อผิดพลาดในการลบผู้ใช้', 'error')
    
    return redirect(url_for('profile'))

@app.route('/activity')
def activity():
    """หน้าบันทึกกิจกรรม"""
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash('กรุณาเลือกผู้ใช้ก่อน', 'warning')
        return redirect(url_for('profile'))
    
    # ดึงกิจกรรมล่าสุด
    activities = db.get_user_activities(current_user_id)
    user = db.get_user_by_id(current_user_id)
    
    return render_template('activity.html', activities=activities, user=user, today = date.today().strftime('%Y-%m-%d'))

@app.route('/add_activity', methods=['POST'])
def add_activity():
    """เพิ่มกิจกรรม"""
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash('กรุณาเลือกผู้ใช้ก่อน', 'warning')
        return redirect(url_for('profile'))
    
    activity_date = request.form.get('date')
    activity_name = request.form.get('activity_name')
    details = request.form.get('details', '')
    duration = int(request.form.get('duration', 0))
    
    # คำนวณแคลลอรี่โดยอัตโนมัติหรือใช้ค่าที่กรอกมา
    calories_input = request.form.get('calories')
    if calories_input:
        calories = float(calories_input)
    else:
        user = db.get_user_by_id(current_user_id)
        current_weight = db.get_latest_weight(current_user_id) or user['weight']
        calories = estimate_calories_burned(activity_name.lower().replace(' ', '_'), duration, current_weight)
    
    if db.add_activity(current_user_id, activity_date, activity_name, details, calories, duration):
        flash('บันทึกกิจกรรมสำเร็จ!', 'success')
    else:
        flash('เกิดข้อผิดพลาดในการบันทึกกิจกรรม', 'error')
    
    return redirect(url_for('activity'))

@app.route('/delete_activity/<int:activity_id>')
def delete_activity(activity_id):
    """ลบกิจกรรม"""
    if db.delete_activity(activity_id):
        flash('ลบกิจกรรมสำเร็จ!', 'success')
    else:
        flash('เกิดข้อผิดพลาดในการลบกิจกรรม', 'error')
    
    return redirect(url_for('activity'))

@app.route('/status')
def status():
    """แสดงผลสถานะ"""
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash('กรุณาเลือกผู้ใช้ก่อน', 'warning')
        return redirect(url_for('profile'))
    
    stats = db.get_user_stats(current_user_id)
    activities = db.get_user_activities(current_user_id)
    
    # สร้างกราฟแคลลอรี่รายวัน
    activity_chart = create_activity_chart(activities)
    
    return render_template('status.html', stats=stats, chart=activity_chart)

@app.route('/weight')
def weight():
    """หน้าจัดการน้ำหนัก"""
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash('กรุณาเลือกผู้ใช้ก่อน', 'warning')
        return redirect(url_for('profile'))
    
    weight_history = db.get_weight_history(current_user_id)

    user = db.get_user_by_id(current_user_id)
    
    # สร้างกราฟน้ำหนัก
    if user is not None:
        weight_chart = create_weight_chart(current_user_id, weight_history, user['target_weight'])
        return render_template('weight.html', weight_history=weight_history, user=user, chart=weight_chart)
    
    return render_template('weight.html', weight_history=weight_history, user=user)

@app.route('/add_weight', methods=['POST'])
def add_weight():
    """เพิ่มบันทึกน้ำหนัก"""
    current_user_id = session.get('current_user_id')
    if not current_user_id:
        flash('กรุณาเลือกผู้ใช้ก่อน', 'warning')
        return redirect(url_for('profile'))
    
    weight_date = request.form.get('date')
    weight_value = float(request.form.get('weight'))
    notes = request.form.get('notes', '')
    
    if db.add_weight_record(current_user_id, weight_date, weight_value, notes):
        # อัพเดตน้ำหนักปัจจุบันในโปรไฟล์
        db.update_user(current_user_id, weight=weight_value)
        flash('บันทึกน้ำหนักสำเร็จ!', 'success')
    else:
        flash('เกิดข้อผิดพลาดในการบันทึกน้ำหนัก', 'error')
    
    return redirect(url_for('weight'))

@app.route('/calculator')
def calculator():
    """หน้าคำนวณ BMI, TDEE, แคลลอรี่"""
    current_user_id = session.get('current_user_id')
    user = db.get_user_by_id(current_user_id)
    calculations = {}
    
    if user is not None:
        current_weight = user['weight']
        
        # คำนวณค่าต่างๆ
        bmi = calculate_bmi(current_weight, user['height'])
        bmi_category = get_bmi_category(bmi)
        bmr_male = calculate_bmr(current_weight, user['height'], user['age'], 'male')
        bmr_female = calculate_bmr(current_weight, user['height'], user['age'], 'female')
        
        calculations = {
            'current_weight': current_weight,
            'bmi': bmi,
            'bmi_category': bmi_category,
            'bmr_male': bmr_male,
            'bmr_female': bmr_female,
            'tdee_sedentary': calculate_tdee(bmr_male, 'sedentary'),
            'tdee_light': calculate_tdee(bmr_male, 'lightly_active'),
            'tdee_moderate': calculate_tdee(bmr_male, 'moderately_active'),
            'tdee_very': calculate_tdee(bmr_male, 'very_active'),
            'tdee_extreme': calculate_tdee(bmr_male, 'extremely_active'),
            'ideal_weight': calculate_ideal_weight_range(user['height']),
            'body_fat_male': calculate_body_fat_percentage(bmi, user['age'], 'male'),
            'body_fat_female': calculate_body_fat_percentage(bmi, user['age'], 'female')
        }
    
    return render_template('calculator.html', user=user, calculations=calculations)

@app.route('/calculate_custom', methods=['POST'])
def calculate_custom():
    """คำนวณด้วยค่าที่กำหนดเอง"""
    weight = float(request.form.get('weight'))
    height = float(request.form.get('height'))
    age = int(request.form.get('age'))
    gender = request.form.get('gender', 'male')
    activity_level = request.form.get('activity_level', 'sedentary')
    
    bmi = calculate_bmi(weight, height)
    bmi_category = get_bmi_category(bmi)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    ideal_weight = calculate_ideal_weight_range(height, gender)
    body_fat = calculate_body_fat_percentage(bmi, age, gender)
    
    calculations = {
        'weight': weight,
        'height': height,
        'age': age,
        'gender': gender,
        'activity_level': activity_level,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'bmr': bmr,
        'tdee': tdee,
        'ideal_weight': ideal_weight,
        'body_fat': body_fat
    }
    
    return jsonify(calculations)

def create_activity_chart(activities):
    """สร้างกราฟแสดงแคลลอรี่ที่เผาผลาญรายวัน"""
    if activities.empty:
        return None
    
    # จัดกลุ่มตามวันที่
    activities['date'] = pd.to_datetime(activities['date'])
    daily_calories = activities.groupby('date')['calories_burned'].sum()
    
    # สร้างกราฟ
    plt.figure(figsize=(12, 6))
    plt.plot(daily_calories.index, daily_calories.values, marker='o', linewidth=2, markersize=6)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Calories (kcal)', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    if activities.size !=7:
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # รูปแบบวันที่
        ax.xaxis.set_major_locator(mdates.DayLocator())  # บังคับให้แสดงทุกวัน
        plt.xticks(rotation=45)
    else:
        plt.xticks(ticks=[daily_calories.index[0].strftime('%Y-%m-%d')], rotation=45)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # แปลงเป็น base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    chart_url = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return chart_url

import matplotlib.dates as mdates

def create_weight_chart(current_user_id, weight_history, target_weight):
    if weight_history.empty:
        return None

    weight_history['date'] = pd.to_datetime(weight_history['date'])

    plt.figure(figsize=(12, 6))
    plt.plot(weight_history['date'], weight_history['weight'], marker='o', linewidth=2, markersize=6, label='current weight')

    if target_weight:
        plt.axhline(y=target_weight, color='r', linestyle='--', linewidth=2, label=f'target ({target_weight} kg)')

    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Weight (kg)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Check have weight history 1 record and check date in not same data
    if weight_history.size != 5 and weight_history['date'].nunique() != 1:
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # รูปแบบวันที่
        ax.xaxis.set_major_locator(mdates.DayLocator())  # บังคับให้แสดงทุกวัน
        plt.xticks(rotation=45)
    else:
        plt.xticks(ticks=[weight_history['date'][current_user_id-1].strftime('%Y-%m-%d')], rotation=45)
        
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    chart_url = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    return chart_url


if __name__ == '__main__':
    app.run(host='127.0.0.12', debug=True)