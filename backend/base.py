from flask import Flask, request
import roadmap
import quiz
import generativeResources
from flask_cors import CORS
import bilibili_search
import translate

api = Flask(__name__)
CORS(api)


@api.route("/api/roadmap", methods=["POST"])
def get_roadmap():
    req = request.get_json()

    response_body = roadmap.create_roadmap(
        topic=req.get("topic", "Machine Learning"),
        time=req.get("time", "4 weeks"),
        knowledge_level=req.get("knowledge_level", "Absoulte Beginner"),
    )

    return response_body


@api.route("/api/quiz", methods=["POST"])
def get_quiz():
    req = request.get_json()

    course = req.get("course")
    topic = req.get("topic")
    subtopic = req.get("subtopic")
    description = req.get("description")

    if not (course and topic and subtopic and description):
        return "Required Fields not provided", 400

    print("getting quiz...")
    response_body = quiz.get_quiz(course, topic, subtopic, description)
    return response_body


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
    req_data = {
        "course": False,
        "knowledge_level": False,
        "description": False,
        "time": False,
    }
    for key in req_data.keys():
        req_data[key] = req.get(key)
        if not req_data[key]:
            return "Required Fields not provided", 400
    print(f"generative resources for {req_data['course']}")
    resources = generativeResources.generate_resources(**req_data)
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