from datetime import datetime
import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. ตั้งค่า API Key (แนะนำให้ตั้งใน Environment Variable ชื่อ GEMINI_API_KEY หรือใส่ตรงนี้ชั่วคราว)
API_KEY = os.environ.get("GEMINI_API_KEY", "ใส่_API_KEY_ของคุณที่นี่")
client = genai.Client(api_key=API_KEY)


# 2. กำหนดโครงสร้างข้อมูลผลลัพธ์ (JSON Schema)
class MorningPostContent(BaseModel):
    flower_name_th: str = Field(
        description="ชื่อดอกไม้มงคลภาษาไทย (เช่น ดอกโบตั๋น, ดอกบัว, ดอกกล้วยไม้)"
    )
    text_on_image_zh: str = Field(
        description="ข้อความอวยพรภาษาจีนตัวเต็ม (Traditional Chinese) สั้นๆ 4-8 ตัวอักษร สำหรับวางบนรูปภาพ"
    )
    caption_zh: str = Field(
        description="แคปชั่นโพสต์ภาษาจีนตัวเต็ม 2-3 บรรทัด อ่านแล้วอบอุ่น เป็นสิริมงคล ใส่อีโมจิให้เหมาะสม"
    )
    translation_th: str = Field(
        description="คำแปลภาษาไทยของข้อความบนภาพและแคปชั่น"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษสำหรับเจนภาพดอกไม้แสงเช้า สดใส คมชัด 4:5 และระบุ no text ท้ายสุด"
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
    กลุ่มเป้าหมายคือผู้ใหญ่และผู้สูงอายุชาวไต้หวัน ฮ่องกง และชาวจีนโพ้นทะเล
    
    จงคิดคอนเทนต์สวัสดีตอนเช้าสำหรับวันนี้ ({day_th} / {day_zh}) 
    ในธีม: "{theme}"
    
    ข้อกำหนดสำคัญ:
    1. ภาษาจีนทั้งหมดต้องใช้ **อักษรจีนตัวเต็ม (Traditional Chinese)** เท่านั้น ห้ามใช้ตัวย่อ
    2. ข้อความบนภาพ (text_on_image_zh) ต้องสั้น กระชับ อ่านง่าย ความหมายมงคล (เช่น สุขภาพแข็งแรง โชคลาภ ราบรื่น)
    3. แคปชั่น (caption_zh) ต้องสุภาพ อบอุ่น ไม่ขายของ ไม่ใส่ลิงก์
    4. Image Prompt ต้องเน้นดอกไม้สวยๆ แสงแดดยามเช้า หยดน้ำค้าง สีสันสดใส สไตล์ภาพถ่ายสมจริง
    """

    # ใช้ gemini-2.5-flash ซึ่งรวดเร็วและฟรีใน Free Tier
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MorningPostContent,
            temperature=0.8,  # เพิ่มความหลากหลายไม่ให้ซ้ำซาก
        ),
    )

    return json.loads(response.text)


if __name__ == "__main__":
    print("กำลังสร้างคอนเทนต์สวัสดีตอนเช้า...\n")

    # สามารถเปลี่ยนธีมได้ตามต้องการ เช่น "ดอกบัวกับธรรมะ", "ดอกโบตั๋นเรียกทรัพย์", "ชาจีนยามเช้า"
    result = generate_morning_content(
        theme="ดอกไม้มงคลสีสดใส อวยพรให้สุขภาพแข็งแรงและโชคดี"
    )

    print(f"🌸 ดอกไม้: {result['flower_name_th']}")
    print(f"🖼️ ข้อความวางบนรูป: {result['text_on_image_zh']}")
    print("-" * 50)
    print(f"📝 แคปชั่นสำหรับก๊อปปี้โพสต์:\n{result['caption_zh']}")
    print("-" * 50)
    print(f"🇹🇭 คำแปลไทย:\n{result['translation_th']}")
    print("-" * 50)
    print(f"🎨 Prompt สร้างรูปภาพ:\n{result['image_prompt_en']}")
