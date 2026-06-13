# -*- coding: utf-8 -*-
"""示例题库 - 首次启动自带"""
from database import Database, QuestionRepository, CategoryRepository
import config

SAMPLE_QUESTIONS = [
    {
        "content": "在道路上驾驶机动车，应当遵守什么原则？",
        "options": {"A": "左侧通行", "B": "右侧通行", "C": "中间通行", "D": "随意通行"},
        "answer": "B",
        "explanation": "根据道路交通安全法，机动车应当右侧通行。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "机动车驾驶人初次申领驾驶证后的实习期是多少个月？",
        "options": {"A": "6个月", "B": "12个月", "C": "18个月", "D": "24个月"},
        "answer": "B",
        "explanation": "驾驶证初次申领实习期为12个月。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "车辆在高速公路行驶，遇有雾、雨、雪、沙尘、冰雹等低能见度气象条件，能见度小于100米时，最高车速不得超过每小时多少公里？",
        "options": {"A": "40公里", "B": "60公里", "C": "80公里", "D": "100公里"},
        "answer": "A",
        "explanation": "能见度小于100米时，车速不得超过40公里/小时，并与同车道前车保持50米以上距离。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "机动车驾驶证的有效期分为几种？",
        "options": {"A": "6年", "B": "10年", "C": "长期", "D": "以上都对"},
        "answer": "D",
        "explanation": "机动车驾驶证分为6年、10年和长期三种。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "驾驶机动车在道路上违反交通安全法律、法规的规定发生交通事故，尚不构成犯罪的，一次记多少分？",
        "options": {"A": "6分", "B": "9分", "C": "12分", "D": "不记分"},
        "answer": "C",
        "explanation": "发生重大交通事故尚不构成犯罪的一次记12分。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "机动车通过铁路道口时，最高时速不得超过多少？",
        "options": {"A": "15公里", "B": "20公里", "C": "30公里", "D": "40公里"},
        "answer": "C",
        "explanation": "机动车通过铁路道口时最高车速不得超过30公里/小时。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "驾驶机动车遇到前方车辆停车排队时，可以从两侧穿插行驶。",
        "options": {"对": "正确", "错": "错误"},
        "answer": "错",
        "explanation": "不得从前方车辆两侧穿插行驶。",
        "question_type": "judgment",
        "category_id": 1,
    },
    {
        "content": "在高速公路上行驶，不得有以下哪些行为？",
        "options": {"A": "倒车", "B": "逆行", "C": "穿越中央分隔带掉头", "D": "以上都是"},
        "answer": "D",
        "explanation": "在高速公路上禁止倒车、逆行、穿越中央分隔带掉头或者在车道内停车。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "车辆在普通道路上发生故障时，应当在车后多少米设置警告标志？",
        "options": {"A": "50-100米", "B": "100-150米", "C": "150-200米", "D": "200米以上"},
        "answer": "A",
        "explanation": "普通道路应在车后50-100米设置警告标志。",
        "question_type": "single",
        "category_id": 1,
    },
    {
        "content": "饮酒后驾驶机动车的，一次记多少分？",
        "options": {"A": "3分", "B": "6分", "C": "9分", "D": "12分"},
        "answer": "D",
        "explanation": "饮酒后驾驶机动车的一次记12分。",
        "question_type": "single",
        "category_id": 1,
    },
]


def load_samples_if_empty():
    """如果数据库为空，加载示例题库"""
    db = Database()
    repo = QuestionRepository(db)
    cat_repo = CategoryRepository(db)
    total = repo.count_all()
    if total > 0:
        return total
    # 插入示例
    repo.add_batch(SAMPLE_QUESTIONS)
    return repo.count_all()
