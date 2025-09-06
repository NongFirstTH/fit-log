import pandas as pd
from datetime import datetime

class FitLogDB:
    def __init__(self, db_path='data/fit_log_data.xlsx'):
        self.db_path = db_path

    def read_sheet(self, sheet_name):
        """อ่านข้อมูลจาก sheet"""
        try:
            return pd.read_excel(self.db_path, sheet_name=sheet_name)
        except Exception as e:
            print(f"Error reading {sheet_name}: {e}")
            return pd.DataFrame()

    def write_sheet(self, sheet_name, data):
        """เขียนข้อมูลลง sheet"""
        try:
            with pd.ExcelWriter(self.db_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        except Exception as e:
            print(f"Error writing to {sheet_name}: {e}")
            return False

    # User Management
    def get_all_users(self):
        """ดึงข้อมูลผู้ใช้ทั้งหมด"""
        return self.read_sheet('Users')

    def get_user_by_id(self, user_id):
        """ดึงข้อมูลผู้ใช้โดย ID"""
        users = self.read_sheet('Users')
        user_data = users[users['user_id'] == user_id]
        
        if user_data.empty :
            return None
        else:
            return user_data.iloc[0]

    def add_user(self, name, weight, height, age, target_weight):
        """เพิ่มผู้ใช้ใหม่"""
        users = self.read_sheet('Users')
        
        # สร้าง user_id ใหม่
        user_id = 1
        if not users.empty :   
            user_id = users['user_id'].max() + 1
        
        new_user = {
            'user_id': user_id,
            'name': name,
            'weight': weight,
            'height': height,
            'age': age,
            'target_weight': target_weight,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
        return self.write_sheet('Users', users)

    def update_user(self, user_id, name=None, weight=None, height=None, age=None, target_weight=None):
        """อัพเดตข้อมูลผู้ใช้"""
        users = self.read_sheet('Users')
        user = users['user_id'] == user_id
        if user.empty:
            return None

        update = {
            'name': name,
            'weight': weight,
            'height': height,
            'age': age,
            'target_weight': target_weight
        }
        for key, value in update.items():
            if value is not None:
                users.loc[user, key] = value
        users.loc[user, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(users)
        return self.write_sheet('Users', users)

    def delete_user(self, user_id):
        """ลบผู้ใช้"""
        users = self.read_sheet('Users')
        users = users[users['user_id'] != user_id]
        
        self.delete_weight_history(user_id)
        return self.write_sheet('Users', users)

    # Activity Management
    def add_activity(self, user_id, date, activity_name, details, calories_burned, duration_minutes=0):
        """เพิ่มกิจกรรม"""
        activities = self.read_sheet('Activities')
        activity_id = 1  
        if not activities.empty :
            activity_id = activities['activity_id'].max() + 1
        
        new_activity = {
            'activity_id': activity_id,
            'user_id': user_id,
            'date': date,
            'activity_name': activity_name,
            'details': details,
            'calories_burned': calories_burned,
            'duration_minutes': duration_minutes
        }
        
        activities = pd.concat([activities, pd.DataFrame([new_activity])], ignore_index=True)
        return self.write_sheet('Activities', activities)

    def get_user_activities(self, user_id):
        """ดึงกิจกรรมของผู้ใช้"""
        activities = self.read_sheet('Activities')
        user_activities = activities[activities['user_id'] == user_id]
        
        return user_activities.sort_values('date', ascending=False)

    def delete_activity(self, activity_id):
        """ลบกิจกรรม"""
        activities = self.read_sheet('Activities')
        activities = activities[activities['activity_id'] != activity_id]
        return self.write_sheet('Activities', activities)

    # Weight History Management
    def add_weight_record(self, user_id, date, weight, notes=''):
        """เพิ่มบันทึกน้ำหนัก"""
        weight_history = self.read_sheet('Weight_History')
        
        record_id = 1 
        if not weight_history.empty:
            record_id = weight_history['record_id'].max() + 1
        
        new_record = {
            'record_id': record_id,
            'user_id': user_id,
            'date': date,
            'weight': weight,
            'notes': notes
        }
        
        weight_history = pd.concat([weight_history, pd.DataFrame([new_record])], ignore_index=True)
        return self.write_sheet('Weight_History', weight_history)

    def get_weight_history(self, user_id):
        """ดึงประวัติน้ำหนัก"""
        weight_history = self.read_sheet('Weight_History')
        user_weights = weight_history[weight_history['user_id'] == user_id]
        return user_weights.sort_values('date', ascending=True)

    def get_latest_weight(self, user_id):
        """ดึงน้ำหนักล่าสุด"""
        weight_history = self.get_weight_history(user_id)
        if weight_history.empty:
           return None 
        else:
            return weight_history.iloc[-1]['weight']

    def delete_weight_history(self, user_id):
        """ลบประวัติน้ำหนัก"""
        weight_history = self.read_sheet('Weight_History')
        user_weights = weight_history[weight_history['user_id'] != user_id]
        return self.write_sheet('Weight_History', user_weights)
    
    # Statistics and Analytics
    def get_user_stats(self, user_id):
        """ดึงสถิติของผู้ใช้"""
        user = self.get_user_by_id(user_id)
        if user is None:
            return None
        
        activities = self.get_user_activities(user_id)
        weight_history = self.get_weight_history(user_id)
        
        stats = {
            'user': user,
            'total_activities': len(activities),
            'total_calories_burned': activities['calories_burned'].sum() if not activities.empty else 0,
            'avg_daily_calories': activities['calories_burned'].mean() if not activities.empty else 0,
            'initial_weight': float(weight_history['weight'].iloc[0]) if not weight_history.empty else float(user['weight']),
            'current_weight': float(user['weight']),
            'target_weight': float(user['target_weight']),
            'weight_progress': 0
        }
        
        # คำนวณความคืบหน้าน้ำหนัก
        if stats['current_weight'] and stats['target_weight']:
            initial_weight = stats['initial_weight']
            current_weight = stats['current_weight']
            target_weight = stats['target_weight']
            
            if initial_weight != target_weight:
                progress =  abs(current_weight - initial_weight) / abs(target_weight - initial_weight) * 100
                stats['weight_progress'] = round(max(0, min(100, progress)), 2)
        
        return stats