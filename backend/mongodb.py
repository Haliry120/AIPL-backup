from pymongo import MongoClient  
from datetime import datetime  
import os  
from dotenv import load_dotenv  
  
load_dotenv()  
  
class MongoDB:  
    def __init__(self):  
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))  
        self.db = self.client['aipl_database']  
        self.users = self.db['users']  
        self.contents = self.db['learning_contents']  
        self.stats = self.db['learning_stats']  
      
    def get_or_create_user(self, user_id=None):  
        """获取或创建用户"""  
        if not user_id:  
            user_id = f"temp_{datetime.now().timestamp()}"  
          
        user = self.users.find_one({"user_id": user_id})  
        if not user:  
            user = {  
                "user_id": user_id,  
                "created_at": datetime.utcnow(),  
                "updated_at": datetime.utcnow(),  
                "is_temporary": True  
            }  
            self.users.insert_one(user)  
          
        return user  
    
    def save_content(self, user_id, topic, content_type, content_data, version=1):  
        """保存学习内容"""  
        # 检查是否已存在相同内容  
        existing = self.contents.find_one({  
            "user_id": user_id,  
            "topic": topic,  
            "content_type": content_type  
        })  
          
        content = {  
            "user_id": user_id,  
            "topic": topic,  
            "content_type": content_type,  
            "content_data": content_data,  
            "version": version,  
            "updated_at": datetime.utcnow()  
        }  
          
        if existing:  
            self.contents.update_one(  
                {"_id": existing["_id"]},  
                {"$set": content}  
            )  
        else:  
            content["created_at"] = datetime.utcnow()  
            self.contents.insert_one(content)  
      
    def get_content(self, user_id, topic, content_type):  
        """获取学习内容"""  
        return self.contents.find_one({  
            "user_id": user_id,  
            "topic": topic,  
            "content_type": content_type  
        })  
    
    def update_quiz_score(self, user_id, topic, score):  
        """更新测验成绩"""  
        stats = self.stats.find_one({"user_id": user_id, "topic": topic})  
        if stats:  
            self.stats.update_one(  
                {"_id": stats["_id"]},  
                {  
                    "$push": {"quiz_scores": score},  
                    "$set": {"last_activity": datetime.utcnow()}  
                }  
            )  
        else:  
            stats = {  
                "user_id": user_id,  
                "topic": topic,  
                "quiz_scores": [score],  
                "completion_rate": 0,  
                "last_activity": datetime.utcnow()  
            }  
            self.stats.insert_one(stats)  
  
# 全局实例  
mongodb = MongoDB()