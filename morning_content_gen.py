from datetime import datetime
import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

API_KEY = os.environ.get("GEMINI_API_KEY", "ใส่_API_KEY_ของคุณที่นี่")
client = genai.Client(api_key=API_KEY)


class MorningPostContent(BaseModel):
    flower_name_th: str = Field(
        description="ชื่อดอกไม้มงคลภาษาไทย (เช่น ดอกโบตั๋น, ดอกบัว, ดอกกล้วยไม้)"
    )
    text_on_image_zh: str = Field(
        description="ข้อความอวยพรภาษาจีนตัวเต็ม (Traditional Chinese) สั้นๆ 4-8 ตัวอักษร สำหรับวางบนรูปภาพ (บังคับต้องมีตามกฎกลุ่ม)"
    )
    caption_zh: str = Field(
        description="แคปชั่นโพสต์ภาษาจีนตัวเต็ม 2-3 บรรทัด อ่านแล้วอบอุ่น เป็นสิริมงคล ใส่อีโมจิให้เหมาะสม"
    )
    translation_th: str = Field(
        description="คำแปลภาษาไทยของข้อความบนภาพและแคปชั่น"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษสำหรับเจนภาพนิ่งดอกไม้แสงเช้า สดใส คมชัด 4:5 (ห้ามมีภาพอาหารหรือปฏิทิน)"
    )


def get_thai_and_chinese_day():
    """ดึงข้อมูลวันปัจจุบันเพื่อนำไปใส่ในคำอวยพรให้ตรงวัน"""
    days_map = {
        0: ("วันจันทร์", "星期一 / 週一"),
        1: ("วันอังคาร", "星期二 / 週二"),
        2: ("วันพุธ", "星期三 / 週三"),
        3: ("วันพฤหัสบดี", "星期四 / 週四"),
        4: ("วันศุกร์", "星期五 / 週五"),
        5: ("วันเสาร์", "星期六 / 週六"),
        6: ("วันอาทิตย์", "星期日 / 週日"),
    }
    today_idx = datetime.now().weekday()
    return days_map[today_idx]


def generate_morning_content(theme: str = "ดอกไม้มงคลรับอรุณ"):
    day_th, day_zh = get_thai_and_chinese_day()

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการทำคอนเทนต์สำหรับกลุ่ม Facebook ชาวจีน (กลุ่ม 早安吉祥如意花語圖)
    จงคิดคอนเทนต์สวัสดีตอนเช้าสำหรับวันนี้ ({day_th} / {day_zh}) ในธีม: "{theme}"
    
    กฎเหล็กของกลุ่มที่ต้องปฏิบัติตามอย่างเคร่งครัด (ฝ่าฝืนจะถูกแบนทันที):
    1. ภาษาจีนทั้งหมดต้องใช้ **อักษรจีนตัวเต็ม (Traditional Chinese)** เท่านั้น
    2. **ห้าม** กล่าวถึงหรือมีเนื้อหาเกี่ยวกับ: ดวงชะตา 12 นักษัตร (十二生肖), อาหาร/ของกิน (美食), ปฏิทิน (日历), การเมือง (政治) และศาสนา (宗教) เด็ดขาด
    3. เน้นเฉพาะเรื่องดอกไม้ ความงดงามของธรรมชาติ สุขภาพแข็งแรง ความสุข ความโชคดี และมิตรภาพที่อบอุ่น
    4. ข้อความบนภาพ (text_on_image_zh) ต้องสั้น กระชับ อ่านง่าย 4-8 ตัวอักษร เพื่อนำไปวางบนรูปภาพ (กฎกลุ่มห้ามโพสต์ภาพที่ไม่มีตัวหนังสือ)
    5. ห้ามใส่ลิงก์ ห้ามขายของ และห้ามชักชวนแอดเพื่อน WhatsApp/Messenger
    6. Image Prompt ต้องเป็นภาพนิ่งของดอกไม้เท่านั้น ห้ามมีภาพอาหาร ปฏิทิน หรือสัตว์ 12 นักษัตร
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MorningPostContent,
            temperature=0.8,
        ),
    )

    return json.loads(response.text)


if __name__ == "__main__":
    print("กำลังสร้างคอนเทนต์ตามกฎระเบียบกลุ่ม...\n")

    result = generate_morning_content(
        theme="ดอกไม้มงคลสีสดใส อวยพรให้สุขภาพแข็งแรงและมีความสุข"
    )

    print(f"🌸 ดอกไม้: {result['flower_name_th']}")
    print(f"🖼️ ข้อความบังคับวางบนรูป: {result['text_on_image_zh']}")
    print("-" * 50)
    print(f"📝 แคปชั่นสำหรับก๊อปปี้โพสต์:\n{result['caption_zh']}")
    print("-" * 50)
    print(f"🇹🇭 คำแปลไทย:\n{result['translation_th']}")
    print("-" * 50)
    print(f"🎨 Prompt สร้างรูปภาพ:\n{result['image_prompt_en']}")
