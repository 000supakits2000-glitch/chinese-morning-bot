from datetime import datetime, timedelta, timezone
import json
import os
import time
from typing import List
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

API_KEY = os.environ.get("GEMINI_API_KEY", "ใส่_API_KEY_ของคุณที่นี่")
client = genai.Client(api_key=API_KEY)


# โครงสร้างคอนเทนต์ 1 ชุด สำหรับกลุ่มจีน
class ChinesePostItem(BaseModel):
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
        description="Prompt ภาษาอังกฤษสำหรับเจนภาพนิ่งดอกไม้มงคลแสงเช้า สดใส คมชัด 4:5 (ห้ามมีภาพอาหาร ปฏิทิน สัตว์ 12 นักษัตร และลงท้ายด้วย no text)"
    )


# โครงสร้างคอนเทนต์ 1 ชุด สำหรับกลุ่มไทย
class ThaiPostItem(BaseModel):
    flower_name_th: str = Field(
        description="ชื่อดอกไม้ภาษาไทยที่สีเข้ากับวันหรือมีความหมายดีๆ"
    )
    text_on_image_th: str = Field(
        description="ข้อความสวัสดีตามวันหรือคำคมข้อคิดดีๆ ภาษาไทย สั้นๆ อ่านง่าย ตัวใหญ่ สำหรับวางบนรูปภาพ"
    )
    caption_th: str = Field(
        description="แคปชั่นโพสต์ภาษาไทย 2-3 บรรทัด อวยพรให้มีความสุข สุขภาพแข็งแรง ใส่อีโมจิให้เหมาะสม"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษสำหรับเจนภาพนิ่งดอกไม้สวยงามรับแสงเช้า สีสันสดใส คมชัด 4:5 ลงท้ายด้วย no text"
    )


# โครงสร้างผลลัพธ์รวม (กลุ่มละ 5 ชุด)
class DailyDualGroupBatch(BaseModel):
    chinese_posts: List[ChinesePostItem] = Field(
        description="รายการคอนเทนต์และ Prompt สำหรับกลุ่มจีน จำนวน 5 ชุด (ดอกไม้และข้อความต้องไม่ซ้ำกันในแต่ละชุด)"
    )
    thai_posts: List[ThaiPostItem] = Field(
        description="รายการคอนเทนต์และ Prompt สำหรับกลุ่มไทย จำนวน 5 ชุด (ดอกไม้และข้อความต้องไม่ซ้ำกันในแต่ละชุด)"
    )


def get_thai_now():
    """ดึงเวลาปัจจุบันตามเวลาประเทศไทย (UTC+7)"""
    tz_th = timezone(timedelta(hours=7))
    return datetime.now(tz_th)


def get_thai_day_info():
    """คืนค่าข้อมูลวันภาษาไทย, ภาษาจีน และสีประจำวัน"""
    days_map = {
        0: ("วันจันทร์", "星期一 / 週一", "สีเหลือง / สีขาวครีม"),
        1: ("วันอังคาร", "星期二 / 週二", "สีชมพู"),
        2: ("วันพุธ", "星期三 / 週三", "สีเขียว"),
        3: ("วันพฤหัสบดี", "星期四 / 週四", "สีส้ม / สีแสด"),
        4: ("วันศุกร์", "星期五 / 週五", "สีฟ้า / สีน้ำเงิน"),
        5: ("วันเสาร์", "星期六 / 週六", "สีม่วง"),
        6: ("วันอาทิตย์", "星期日 / 週日", "สีแดง"),
    }
    today_idx = get_thai_now().weekday()
    return days_map[today_idx]


def generate_batch_content():
    day_th, day_zh, day_color = get_thai_day_info()

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการทำคอนเทนต์สวัสดีตอนเช้าสำหรับกลุ่ม Facebook ขนาดใหญ่ 2 กลุ่ม:
    กลุ่มที่ 1: กลุ่มชาวจีน (早安吉祥如意花語圖) เน้นผู้ใหญ่ชาวไต้หวัน/ฮ่องกง
    กลุ่มที่ 2: กลุ่มคนไทย (ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน) เน้นมิตรภาพ คำอวยพรตามวัน และข้อคิดดีๆ
    
    จงคิดคอนเทนต์สำหรับวันนี้ ({day_th} / {day_zh}) แบ่งเป็น **กลุ่มละ 5 ชุด (รวม 10 ชุด)** โดยทั้ง 5 ชุดในแต่ละกลุ่มต้องใช้ชนิดดอกไม้ มุมกล้อง และคำอวยพรที่แตกต่างกันไม่ซ้ำเลย
    
    กฎเหล็กที่ต้องปฏิบัติตามอย่างเคร่งครัด:
    1. **ส่วนกลุ่มจีน (chinese_posts จำนวน 5 ชุด):**
       - ใช้ **อักษรจีนตัวเต็ม (Traditional Chinese)** เท่านั้น
       - **ห้าม** กล่าวถึงหรือมีเนื้อหาเกี่ยวกับ: ดวงชะตา 12 นักษัตร (十二生肖), อาหาร/ของกิน (美食), ปฏิทิน (日历), การเมือง (政治) และศาสนา (宗教) เด็ดขาด
       - ข้อความบนภาพ (text_on_image_zh) ต้องสั้น กระชับ 4-8 ตัวอักษร (กฎกลุ่มห้ามโพสต์ภาพที่ไม่มีตัวหนังสือ)
       - Image Prompt ต้องเป็นภาพนิ่งของดอกไม้มงคล (เช่น โบตั๋น, บัว, กล้วยไม้, เหมย, เบญจมาศ, ทานตะวัน) รับแสงเช้า ห้ามมีอาหาร ปฏิทิน หรือสัตว์ 12 นักษัตร และลงท้ายด้วย no text
       
    2. **ส่วนกลุ่มไทย (thai_posts จำนวน 5 ชุด):**
       - วันนี้คือ{day_th} ({day_color}) ให้เน้นดอกไม้โทน{day_color} หรือดอกไม้สีสันสดใสสวยงาม
       - ข้อความบนภาพ (text_on_image_th) มีทั้งแบบระบุวัน ("สวัสดี{day_th}...") และแบบคำคมข้อคิดดีๆ อ่านง่าย สบายตา
       - แคปชั่น (caption_th) สุภาพ จริงใจ เน้นแบ่งปันความสุข ไม่ขายของ ไม่แปะลิงก์
       - Image Prompt เป็นภาพนิ่งดอกไม้สวยงามแสงเช้า สีสันสดใส คมชัด ลงท้ายด้วย no text
    """

    candidate_models = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-pro"]

    for model_name in candidate_models:
        for attempt in range(1, 4):
            try:
                print(
                    f"กำลังเรียกใช้โมเดล {model_name} เพื่อสร้างคอนเทนต์ 10 ชุด (รอบที่ {attempt})..."
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DailyDualGroupBatch,
                        temperature=0.85,  # เพิ่มความหลากหลายให้ทั้ง 5 ชุดไม่ซ้ำกัน
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
    print("กำลังสร้างคอนเทนต์กลุ่มละ 5 ชุด (รวม 10 ชุด)...\n")

    data = generate_batch_content()
    now_str = get_thai_now().strftime("%d/%m/%Y เวลา %H:%M น.")
    day_th, _, day_color = get_thai_day_info()

    lines = []
    lines.append("=" * 65)
    lines.append(f"📅 อัปเดตล่าสุด: {day_th}ที่ {now_str} (เวลาไทย)")
    lines.append(
        f"🎨 ธีมสีประจำวัน (สำหรับกลุ่มไทย): {day_color} | จำนวน: กลุ่มละ 5 ชุด"
    )
    lines.append("=" * 65)

    # จัดรูปแบบส่วนที่ 1: กลุ่มจีน 5 ชุด
    lines.append(
        "\n🇨🇳 [ส่วนที่ 1: กลุ่มจีน 早安吉祥如意花語圖 - 5 ชุด]"
    )
    lines.append(
        "⚠️ กฎกลุ่ม: โพสต์ได้สูงสุดไม่เกิน 5 โพสต์/วัน | บังคับใส่ตัวหนังสือลงบนภาพทุกใบ"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(data["chinese_posts"], start=1):
        lines.append(f"\n--- 🇨🇳 ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(f"🖼️ ข้อความวางบนรูป: {item['text_on_image_zh']}")
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_zh']}")
        lines.append(f"🇹🇭 คำแปลไทย: {item['translation_th']}")
        lines.append(f"🎨 Image Prompt:\n{item['image_prompt_en']}")
        lines.append("-" * 50)

    # จัดรูปแบบส่วนที่ 2: กลุ่มไทย 5 ชุด
    lines.append(
        "\n\n🇹🇭 [ส่วนที่ 2: กลุ่มไทย ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน - 5 ชุด]"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(data["thai_posts"], start=1):
        lines.append(f"\n--- 🇹🇭 ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(f"🖼️ ข้อความวางบนรูป: {item['text_on_image_th']}")
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_th']}")
        lines.append(f"🎨 Image Prompt:\n{item['image_prompt_en']}")
        lines.append("-" * 50)

    output_text = "\n".join(lines)

    with open("today_post.txt", "w", encoding="utf-8") as f:
        f.write(output_text)

    print(
        "✅ บันทึกคอนเทนต์ทั้ง 10 ชุด (กลุ่มละ 5 ชุด) ลงไฟล์ today_post.txt เรียบร้อยแล้ว!"
    )
