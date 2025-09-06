def calculate_bmi(weight, height):
    """calculate BMI"""
    bmi = 0
    if height > 0:
        height_m = height / 100
        bmi = weight / height_m**2
    
    return round(bmi, 2)

def get_bmi_category(bmi):
    """categories of BMI"""
    if bmi < 18.5:
        return "น้ำหนักน้อย"
    elif bmi < 25:
        return "น้ำหนักปกติ"
    elif bmi < 30:
        return "น้ำหนักเกิน"
    else:
        return "อ้วน"
        
def calculate_bmr(weight, height, age, gender='male'):
    """calculate BMR"""
    if gender == 'male':
        bmr = 88.362 + 13.397*weight + 4.799*height - 5.677*age
    else:
        bmr = 447.593 + 9.247*weight + 3.098*height - 4.330*age
        
    return round(bmr,2)

def calculate_tdee(bmr, activity_level='sedentary'):
    """calculate TDEE"""
    multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extremely_active': 1.9
    }
    
    tdee = bmr * multipliers[activity_level]
    
    return round(tdee,2)

def calculate_daily_calories_for_goal(tdee, goal='maintain', rate=0.5):
    """calculate daily calories for goal"""
    
    calories_per_kg = 7700
    
    if goal == 'lose':
        daily_deficit = (rate * calories_per_kg) / 7
        return round(tdee - daily_deficit, 2)
    elif goal == 'gain':
        daily_surplus = (rate * calories_per_kg) / 7
        return round(tdee + daily_surplus, 2)
    else:  # maintain
        return tdee
    
def estimate_calories_burned(activity_type, duration_minutes, weight):
    """estimate calories burned"""
    met_values = {
        'walking_slow': 2.0,
        'walking_moderate': 5.0,
        'walking_fast': 6.5,
        'jogging': 8.0,
        'running': 10.0,
        'cycling_leisure': 3.5,
        'cycling_moderate':  5.5,
        'cycling_fast':  8.0,
        'swimming': 7.0,
        'weight_training':6.0,
        'yoga': 2.5,
        'aerobics': 6.5,
        'bassketball': 8.0,
        'soccer': 8.0,
        'tennis': 4.0,
        'badminton': 4.5,
        'dancing': 6.0
    }
    
    calories = (met_values[activity_type] * 3.5 * weight * duration_minutes)/200
    
    return round(calories,2)

def calculate_ideal_weight_range(height):
    """calculate proper weight range"""
    height_m =  height / 100
    
    min_weight = 18.5 * (height_m**2)
    max_weight = 24.9 * (height_m**2)
    
    return {
        'min': round(min_weight, 1),
        'max': round(max_weight, 1)
    }
    
def calculate_body_fat_percentage(bmi, age, gender='male'):
    """estimate body fat percentage"""
    
    if gender == 'male':
        body_fat = 1.2 * bmi + 0.23*age - 16.2
    else:
        body_fat = 1.2 * bmi + 0.23*age - 5.4
    
    return max(0, round(body_fat,1))

def get_weight_status(current_weight, target_weight, initial_weight):
    """ประเมินสถานะการลดน้ำหนัก"""
    if initial_weight == target_weight:
        return "เป้าหมายคงที่"
   
    total_goal = abs(initial_weight - target_weight)
    current_progress = abs(initial_weight - current_weight)
       
    if target_weight < initial_weight:  # ลดน้ำหนัก
        if current_weight <= target_weight:
            return "บรรลุเป้าหมายแล้ว"
        elif current_progress > 0:
            return f"กำลังลดน้ำหนัก ({current_progress:.1f}/{total_goal:.1f} กก.)"
        else:
            return "ยังไม่เริ่มลดน้ำหนัก"
    else:  # เพิ่มน้ำหนัก
        if current_weight >= target_weight:
            return "บรรลุเป้าหมายแล้ว"
        elif current_progress > 0:
            return f"กำลังเพิ่มน้ำหนัก ({current_progress:.1f}/{total_goal:.1f} กก.)"
        else:
            return "ยังไม่เริ่มเพิ่มน้ำหนัก"
        

def get_activity_recommendations(bmi_category, goal):
    """แนะนำกิจกรรมตาม BMI และเป้าหมาย"""
    recommendations = {
        'น้ำหนักน้อย': {
            'gain': ['ยกน้ำหนัก', 'กิจกรรมเพิ่มกล้ามเนื้อ', 'เดินเร็ว'],
            'maintain': ['โยคะ', 'เดินเบาๆ', 'แอโรบิคเบาๆ']
        },
        'น้ำหนักปกติ': {
            'maintain': ['เดิน', 'ปั่นจักรยาน', 'ว่ายน้ำ', 'เต้นรำ'],
            'lose': ['วิ่งจ๊อกกิ้ง', 'แอโรบิค', 'ฟุตบอล'],
            'gain': ['ยกน้ำหนัก', 'กิจกรรมเพิ่มกล้ามเนื้อ']
        },
        'น้ำหนักเกิน': {
            'lose': ['เดินเร็ว', 'ว่ายน้ำ', 'ปั่นจักรยาน', 'แอโรบิค'],
            'maintain': ['เดิน', 'โยคะ', 'เต้นรำ']
        },
        'อ้วน': {
            'lose': ['เดิน', 'ว่ายน้ำ', 'ปั่นจักรยานเบาๆ', 'แอโรบิคน้ำ'],
            'maintain': ['เดินเบาๆ', 'โยคะ', 'กิจกรรมในน้ำ']
        }
    }
    
    return recommendations[bmi_category][goal]