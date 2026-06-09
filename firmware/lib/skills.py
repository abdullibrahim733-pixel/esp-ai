SKILLS = [
    {
        "id": "general",
        "name": "General",
        "desc": "Open-ended conversation",
        "icon": "💬",
        "prompt": "You are a helpful, concise AI assistant. Keep responses brief and to the point.",
    },
    {
        "id": "code",
        "name": "Code Expert",
        "desc": "Write & explain code",
        "icon": "&lt;/&gt;",
        "prompt": "You are a senior software engineer. Write clean, well-structured code. Explain your reasoning when relevant.",
    },
    {
        "id": "summarize",
        "name": "Summarizer",
        "desc": "Condense long text",
        "icon": "📄",
        "prompt": "You are a summarization engine. Extract key points and present them concisely. Use bullet points when helpful.",
    },
    {
        "id": "translate",
        "name": "Translator",
        "desc": "Translate between languages",
        "icon": "🌐",
        "prompt": "You are a professional translator. Translate text accurately while preserving meaning, tone, and style. Identify source and target languages.",
    },
    {
        "id": "explain",
        "name": "Explainer",
        "desc": "Break down complex topics",
        "icon": "🔍",
        "prompt": "You are a patient teacher. Explain complex topics in simple terms using analogies and examples. Assume no prior knowledge.",
    },
    {
        "id": "debug",
        "name": "Debugger",
        "desc": "Find & fix issues",
        "icon": "🐛",
        "prompt": "You are an expert debugger. Analyze problems systematically, identify root causes, and propose tested solutions.",
    },
]


def get_skill(skill_id):
    for s in SKILLS:
        if s["id"] == skill_id:
            return s
    return SKILLS[0]


def get_system_prompt(skill_id):
    return get_skill(skill_id)["prompt"]


def get_skills_list():
    return [{"id": s["id"], "name": s["name"], "desc": s["desc"], "icon": s["icon"], "prompt": s["prompt"]} for s in SKILLS]
