from datetime import datetime  
from mongodb import mongodb  
  
def save_content(user_id, topic, content_type, content_data):  
    """保存内容到 MongoDB"""  
    return mongodb.save_content(user_id, topic, content_type, content_data)  
  
def get_content(user_id, topic, content_type):  
    """从 MongoDB 获取内容"""  
    return mongodb.get_content(user_id, topic, content_type)  
  
def get_or_create_user(user_id=None):  
    """获取或创建用户"""  
    return mongodb.get_or_create_user(user_id)  
  
def update_quiz_score(user_id, topic, score):  
    """更新测验成绩"""  
    return mongodb.update_quiz_score(user_id, topic, score)  
  
def get_user_contents(user_id):  
    """获取用户的所有内容"""  
    return mongodb.get_user_contents(user_id)