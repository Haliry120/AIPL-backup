import siliconflow_client  
    

def get_quiz(course, topic, subtopic, description):  
    """使用硅基流动API生成测验题目"""  
        
    # 系统指令  
    system_instruction = """您是一位AI代理，负责根据主题、子主题及具体学习要点的描述来提供测验题目。所有题目必须采用多项选择题形式，必要时可包含计算题。请根据子主题描述的详细程度决定题目数量，尽可能多地生成包含深度思考的题目。输出格式如下：{questions:[ {question: "...", options:[...], answerIndex:"...", reason:"..."} ]}"""
    # 用户提示  
    user_prompt = f'用户正在学习{course}课程，当前学习主题为“{topic}”。请根据子主题“{subtopic}”创建测验，该子主题的具体描述为“{description}”。'  
        
    # 使用客户端生成 JSON 响应  
    client = siliconflow_client.get_client()  
    return client.generate_json(  
        system_instruction=system_instruction,  
        user_prompt=user_prompt,  
        temperature=1,  
        top_p=0.95,  
        max_tokens=20000  
    )