from flask import Flask, request
import roadmap
import quiz
import generativeResources
from flask_cors import CORS
import bilibili_search
import translate
from database import get_or_create_user, save_content, get_content
import uuid

api = Flask(__name__)
CORS(api)

def get_user_id():  
    """从请求中获取或创建用户ID"""  
    user_id = request.headers.get('X-User-ID')  
    if not user_id:  
        # 从 localStorage 或创建新的临时ID  
        user_id = request.json.get('user_id') if request.json else None  
      
    user = get_or_create_user(user_id)  
    return user['user_id'] 

@api.route("/api/roadmap", methods=["POST"])
def get_roadmap():
    req = request.get_json()

    # 检查是否需要重新生成
    regenerate = req.get("regenerate", False)
    topic = req.get("topic", "Machine Learning")

    # 如果不是重新生成，尝试从数据库获取
    if not regenerate:
        try:
            from database import get_content
            user_id = request.headers.get('X-User-ID')
            if user_id:
                existing = get_content(user_id, topic, "roadmap")
                if existing:
                    return existing["content_data"]
        except:
            pass  # 如果数据库出错，继续生成新的

    # 生成新的路线图
    response_body = roadmap.create_roadmap(
        topic=topic,
        time=req.get("time", "4 weeks"),
        knowledge_level=req.get("knowledge_level", "Absolute Beginner"),
    )

    # 保存到数据库
    try:
        from database import save_content
        user_id = request.headers.get('X-User-ID')
        if user_id:
            save_content(user_id, topic, "roadmap", response_body)
    except:
        pass  # 如果数据库出错，仍然返回结果

    return response_body


@api.route("/api/quiz", methods=["POST"])
def get_quiz():
    req = request.get_json()
    user_id = get_user_id()

    course = req.get("course")
    topic = req.get("topic")
    subtopic = req.get("subtopic")
    description = req.get("description")

    if not (course and topic and subtopic and description):
        return "Required Fields not provided", 400

    # 生成测验（测验通常不需要缓存，每次都是新的）
    response_body = quiz.get_quiz(course, topic, subtopic, description)
    return response_body

@api.route("/api/quiz-score", methods=["POST"])  
def save_quiz_score():  
    """保存测验成绩"""  
    req = request.get_json()  
    user_id = get_user_id()  
      
    topic = req.get("topic")  
    score = req.get("score")  
      
    if not topic or score is None:  
        return "Required Fields not provided", 400  
      
    from database import update_quiz_score  
    update_quiz_score(user_id, topic, score)  
      
    return {"success": True}  

@api.route("/api/user-data", methods=["GET"])  
def get_user_data():  
    """获取用户的所有学习数据"""  
    user_id = get_user_id()  
      
    # 获取用户的所有内容  
    from database import get_user_contents  
    contents = get_user_contents(user_id)  
      
    return {  
        "user_id": user_id,  
        "contents": contents  
    }

@api.route("/api/translate", methods=["POST"])
def get_translations():
    req = request.get_json()

    text = req.get("textArr")
    toLang = req.get("toLang")

    print(f"Translating to {toLang}: { text}")
    translated_text = translate.translate_text_arr(text_arr=text, target=toLang)
    return translated_text


@api.route("/api/generate-resource", methods=["POST"])
def generative_resource():
    req = request.get_json()
    user_id = get_user_id()

    # 检查是否需要重新生成
    regenerate = req.get("regenerate", False)
    course = req.get("course")

    if not regenerate:
        # 尝试从数据库获取现有资源
        existing = get_content(user_id, course, "resource")
        if existing:
            return existing["content_data"]

    # 验证必需字段
    req_data = {
        "course": req.get("course"),
        "knowledge_level": req.get("knowledge_level"),
        "description": req.get("description"),
        "time": req.get("time"),
    }

    for key, value in req_data.items():
        if not value:
            return "Required Fields not provided", 400
    
    # 生成新的资源
    resources = generativeResources.generate_resources(**req_data)

    # 保存到数据库
    save_content(user_id, course, "resource", resources)

    return resources


@api.route("/api/search-bilibili", methods=["POST"])
def search_bilibili():
    req = request.get_json()

    subtopic = req.get("subtopic", "")
    course = req.get("course", "")

    # 将英文关键词翻译成中文
    try:
        subtopic_cn = translate.translate_text_arr([subtopic], target="zh-CN")[0] if subtopic else ""
        course_cn = translate.translate_text_arr([course], target="zh-CN")[0] if course else ""
        print(f"Translated: {subtopic} -> {subtopic_cn}, {course} -> {course_cn}")
    except Exception as e:
        print(f"Translation error: {e}, using original keywords")
        subtopic_cn = subtopic
        course_cn = course

        # 使用翻译后的中文关键词搜索
    keyword = f"{subtopic_cn} 教程"

    print(f"Searching Bilibili for: {keyword}")
    courses = bilibili_search.search_bilibili_courses(keyword)

    # 如果第一次搜索无结果,尝试其他组合
    if not courses:
        print(f"No results for '{keyword}', trying with course name")
        keyword = f"{course_cn} {subtopic_cn}"
        courses = bilibili_search.search_bilibili_courses(keyword)

    if not courses:
        print(f"No results for '{keyword}', trying with course only")
        keyword = f"{course_cn}"
        courses = bilibili_search.search_bilibili_courses(keyword)

    return {"courses": courses, "keyword": keyword}