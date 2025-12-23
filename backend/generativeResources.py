import siliconflow_client

    
def generate_resources(course, knowledge_level, description, time):
    """使用硅基流动API生成学习资源"""
    
    # 系统指令
    system_instruction = "您是一位AI学习助手。请使用适合学习的平实冷静的语言，根据用户设定的时间提供相应的学习内容。"
        
    # 用户提示
    user_prompt = f"我现在正在学习{course}。我在这方面的知识水平是{knowledge_level}我想学习{description}。我希望在{time}内掌握。请指导我。"

    # 使用客户端生成文本响应
    client = siliconflow_client.get_client()
    return client.generate_text(
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        temperature=1,
        top_p=0.95,
        max_tokens=8192
    )