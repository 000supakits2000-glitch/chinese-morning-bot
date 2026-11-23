from datetime import datetime
import json
import os
import time
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

API_KEY = os.environ.get("GEMINI_API_KEY", "ใส่_API_KEY_ของคุณที่นี่")
client = genai.Client(api_key=API_KEY)


class DualGroupMorningContent(BaseModel):
    flower_name_th: str = Field(
        description="ชื่อดอกไม้มงคลภาษาไทย (เช่น ดอกโบตั๋น, ดอกบัว, ดอกกล้วยไม้)"
    )

    # ส่วนของกลุ่มจีน (早安吉祥如意花語圖)
    zh_text_on_image: str = Field(
        description="ข้อความอวยพรภาษาจีนตัวเต็ม (Traditional Chinese) สั้นๆ 4-8 ตัวอักษร สำหรับวางบนรูปภาพ (บังคับต้องมีตามกฎกลุ่มจีน)"
    )
    zh_caption: str = Field(
        description="แคปชั่นโพสต์ภาษาจีนตัวเต็ม 2-3 บรรทัด อ่านแล้วอบอุ่น เป็นสิริมงคล ใส่อีโมจิให้เหมาะสม"
    )
    zh_translation_th: str = Field(
        description="คำแปลภาษาไทยของข้อความบนภาพและแคปชั่นภาษาจีน"
    )

    # ส่วนของกลุ่มไทย (ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน)
    th_text_on_image: str = Field(
        description="ข้อความสวัสดีตามวันหรือคำคมข้อคิดดีๆ ภาษาไทย สั้นๆ อ่านง่าย ตัวใหญ่ สำหรับวางบนรูปภาพ"
    )
    th_caption: str = Field(
        description="แคปชั่นโพสต์ภาษาไทย 2-3 บรรทัด อวยพรให้มีความสุข สุขภาพแข็งแรง ใส่อีโมจิให้เหมาะสม"
    )

    # ส่วนที่ใช้ร่วมกัน
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษสำหรับเจนภาพนิ่งดอกไม้แสงเช้า สดใส คมชัด 4:5 (ห้ามมีภาพอาหาร ปฏิทิน หรือสัตว์ 12 นักษัตร และลงท้ายด้วย no text)"
    )


def get_thai_and_chinese_day():
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
    คุณคือผู้เชี่ยวชาญการทำคอนเทนต์สวัสดีตอนเช้าสำหรับกลุ่ม Facebook ขนาดใหญ่ 2 กลุ่ม:
    กลุ่มที่ 1: กลุ่มชาวจีน (早安吉祥如意花語圖) เน้นผู้ใหญ่ชาวไต้หวัน/ฮ่องกง
    กลุ่มที่ 2: กลุ่มคนไทย (ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน) เน้นมิตรภาพ คำอวยพรตามวัน และข้อคิดดีๆ
    
    จงคิดคอนเทนต์สำหรับวันนี้ ({day_th} / {day_zh}) ในธีม: "{theme}"
    
    กฎเหล็กที่ต้องปฏิบัติตามอย่างเคร่งครัด:
    1. **ส่วนภาษาจีน (กลุ่มที่ 1):**
       - ต้องใช้ **อักษรจีนตัวเต็ม (Traditional Chinese)** เท่านั้น
       - **ห้าม** กล่าวถึงหรือมีเนื้อหาเกี่ยวกับ: ดวงชะตา 12 นักษัตร (十二生肖), อาหาร/ของกิน (美食), ปฏิทิน (日历), การเมือง (政治) และศาสนา (宗教) เด็ดขาด
       - ข้อความบนภาพ (zh_text_on_image) ต้องสั้น กระชับ 4-8 ตัวอักษร (กฎกลุ่มห้ามโพสต์ภาพที่ไม่มีตัวหนังสือ)
    2. **ส่วนภาษาไทย (กลุ่มที่ 2):**
       - ข้อความบนภาพ (th_text_on_image) ต้องระบุวันให้ตรงกับวันนี้ ({day_th}) เช่น "สวัสดี{day_th} ขอให้สุขใจ..." อ่านง่าย สบายตา
       - แคปชั่น (th_caption) สุภาพ จริงใจ เน้นแบ่งปันความสุขและมิตรภาพ ไม่ขายของ ไม่แปะลิงก์
    3. **Image Prompt (image_prompt_en):**
       - เป็นภาพนิ่งของดอกไม้สวยงามรับแสงเช้า สีสันสดใส เพื่อให้ใช้เจนภาพเพียง 1 ครั้งแล้วนำไปใส่ตัวหนังสือแยกเป็น 2 ภาษาได้
       - ห้ามมีภาพอาหาร ปฏิทิน หรือสัตว์ 12 นักษัตรเด็ดขาด และต้องลงท้ายด้วย no text
    """

    candidate_models = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-pro"]

    for model_name in candidate_models:
        for attempt in range(1, 4):
            try:
                print(
                    f"กำลังเรียกใช้โมเดล {model_name} (รอบที่ {attempt})..."
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DualGroupMorningContent,
                        temperature=0.8,
                    ),
                )
                return json.loads(response.text)

            except errors.ServerError as e:
                print(
                    f"⚠️ เซิร์ฟเวอร์คิวเต็ม ({e}) รอ 10 วินาทีแล้วลองใหม่..."
                )
                time.sleep(10)
            except errors.ClientError as e:
                print(
                    f"⚠️ โมเดล {model_name} ไม่พร้อมใช้งาน ({e}) เปลี่ยนไปใช้โมเดลสำรอง..."
                )
                break

    raise RuntimeError(
        "ไม่สามารถสร้างคอนเทนต์ได้ เนื่องจากเซิร์ฟเวอร์ Google คิวเต็มทุกโมเดล"
    )


if __name__ == "__main__":
    print("กำลังสร้างคอนเทนต์สำหรับทั้ง 2 กลุ่ม...\n")

    result = generate_morning_content(
        theme="ดอกไม้มงคลสีสดใส อวยพรให้สุขภาพแข็งแรงและมีความสุข"
    )

    print("\n" + "=" * 60)
    print(f"🌸 ดอกไม้ประจำวัน: {result['flower_name_th']}")
    print("=" * 60)

    print("\n🇨🇳 [กลุ่มที่ 1: 早安吉祥如意花語圖]")
    print(f"🖼️ ข้อความบังคับวางบนรูป: {result['zh_text_on_image']}")
    print(f"📝 แคปชั่นโพสต์:\n{result['zh_caption']}")
    print(f"🇹🇭 คำแปลไทย: {result['zh_translation_th']}")

    print("\n" + "-" * 60)

    print("\n🇹🇭 [กลุ่มที่ 2: ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน]")
    print(f"🖼️ ข้อความวางบนรูป: {result['th_text_on_image']}")
    print(f"📝 แคปชั่นโพสต์:\n{result['th_caption']}")

    print("\n" + "=" * 60)
    print(f"🎨 Prompt สร้างรูปภาพ (ใช้รูปเดียวกันได้เลย):\n{result['image_prompt_en']}")
    print("=" * 60)
