from datetime import datetime, timedelta, timezone
import json
import os
import random
import time
from typing import List
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

API_KEY = os.environ.get("GEMINI_API_KEY", "ใส่_API_KEY_ของคุณที่นี่")
client = genai.Client(api_key=API_KEY)


class ChinesePostItem(BaseModel):
    flower_name_th: str = Field(description="ชื่อดอกไม้มงคลภาษาไทย")
    text_line_1_zh: str = Field(
        description="ข้อความบรรทัดบนภาษาจีนตัวเต็ม เช่น 早上好！"
    )
    text_line_2_zh: str = Field(
        description="ข้อความบรรทัดกลางภาษาจีนตัวเต็ม 4 ตัวอักษร เช่น 吉祥如意, 身體健康"
    )
    text_line_3_zh: str = Field(
        description="ข้อความบรรทัดล่างภาษาจีนตัวเต็ม 4 ตัวอักษร เช่น 笑口常開, 歲歲平安, 平安喜樂"
    )
    caption_zh: str = Field(
        description="แคปชั่นโพสต์ภาษาจีนตัวเต็ม 2-3 บรรทัด อ่านแล้วอบอุ่น เป็นสิริมงคล ใส่อีโมจิให้เหมาะสม"
    )
    translation_th: str = Field(
        description="คำแปลภาษาไทยของข้อความบนภาพและแคปชั่น"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษละเอียดๆ สไตล์ทิวทัศน์ขุนเขา เก๋งจีน น้ำตก ดอกไม้แสงเช้า มีตัวอักษรพู่กันจีนสีแดงขอบทอง 3 บรรทัดลอยบนท้องฟ้าด้านบน สัดส่วน 9:16"
    )


class ThaiPostItem(BaseModel):
    flower_name_th: str = Field(description="ชื่อดอกไม้มงคลภาษาไทย")
    text_line_1_th: str = Field(
        description="ข้อความบรรทัดบนภาษาไทยสั้นๆ 2-3 คำ เช่น สวัสดีวันพุธ, อรุณสวัสดิ์"
    )
    text_line_2_th: str = Field(
        description="ข้อความบรรทัดล่างภาษาไทยสั้นๆ 2-4 คำ เช่น สุขภาพแข็งแรง, ยิ้มรับความสุข, โชคดีมีชัย"
    )
    caption_th: str = Field(
        description="แคปชั่นโพสต์ภาษาไทย 2-3 บรรทัด อวยพรให้มีความสุข สุขภาพแข็งแรง ใส่อีโมจิให้เหมาะสม"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษละเอียดๆ สไตล์ทิวทัศน์ขุนเขา น้ำตก สะพานหิน ดอกไม้แสงเช้า มีตัวอักษรภาษาไทยสีแดงขอบทอง 2 บรรทัดลอยบนท้องฟ้าด้านบน สัดส่วน 9:16"
    )


class ChineseBatch(BaseModel):
    posts: List[ChinesePostItem]


class ThaiBatch(BaseModel):
    posts: List[ThaiPostItem]


def get_thai_now():
    tz_th = timezone(timedelta(hours=7))
    return datetime.now(tz_th)


def get_thai_day_info():
    days_map = {
        0: ("วันจันทร์", "星期一 / 週一", "สีเหลือง / สีทอง"),
        1: ("วันอังคาร", "星期二 / 週二", "สีชมพู"),
        2: ("วันพุธ", "星期三 / 週三", "สีเขียว / สีทอง"),
        3: ("วันพฤหัสบดี", "星期四 / 週四", "สีส้ม / สีแสด"),
        4: ("วันศุกร์", "星期五 / 週五", "สีฟ้า / สีน้ำเงิน"),
        5: ("วันเสาร์", "星期六 / 週六", "สีม่วง"),
        6: ("วันอาทิตย์", "星期日 / 週日", "สีแดง"),
    }
    return days_map[get_thai_now().weekday()]


def get_landscape_recipes(count: int = 5) -> str:
    flowers = [
        "vibrant pink Peony flowers and overhanging cherry blossom branches (ดอกโบตั๋นและซากุระ)",
        "blooming pink Lotus flowers in the pond and pink Plum Blossoms overhead (ดอกบัวชมพูและดอกเหมย)",
        "colorful pink and blue Hydrangeas with blooming roses along a stone balustrade (ดอกไฮเดรนเยียและกุหลาบ)",
        "radiant yellow Phalaenopsis Orchids and golden Osmanthus blossoms (ดอกกล้วยไม้เหลืองและหอมหมื่นลี้)",
        "lush red Camellia flowers and cascading wisteria blossoms (ดอกคามิเลียและวิสทีเรีย)",
        "golden Chrysanthemums and pink Magnolia branches in bloom (ดอกเบญจมาศทองและแมกโนเลีย)",
        "bright Sunflowers and vibrant Bougainvillea flowers along the riverbank (ดอกทานตะวันและเฟื่องฟ้า)",
    ]

    landscapes = [
        "majestic traditional Chinese palace pavilion perched on a cliff beside a cascading waterfall, stone staircase with glowing stone lanterns, misty mountains, and red-crowned cranes flying in the golden sunrise sky",
        "serene Jiangnan ancient water town with white-walled houses, red lanterns, weeping willow trees, traditional wooden boats on a golden river, and an arched stone bridge at sunrise",
        "tranquil classical Chinese garden with a wooden lakeside pavilion, stone arch bridge over turquoise water with swimming koi fish, misty mountain peaks, and flying white cranes",
        "panoramic misty mountain valley at dawn with tiered waterfalls, ancient temple roofs peeking through golden clouds, stone pathway lined with flowers, and warm sunbeams",
    ]

    selected_flowers = random.sample(flowers, count)
    recipes = []
    for i in range(count):
        f = selected_flowers[i]
        bg = random.choice(landscapes)
        recipes.append(f"ชุดที่ {i+1}: ดอกไม้={f} | ทิวทัศน์={bg}")
    return "\n".join(recipes)


def call_gemini_with_retry(prompt: str, schema_class):
    """ฟังก์ชันเรียก AI พร้อมระบบรอคิวและสลับโมเดลสำรองตระกูล Flash และ Flash-Lite"""
    candidate_models = [
        "gemini-3.8-flash",
        "gemini-3.8-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]

    for model_name in candidate_models:
        for attempt in range(1, 5):  # ลองสูงสุดโมเดลละ 4 รอบ
            try:
                print(
                    f"กำลังเรียกใช้โมเดล {model_name} (รอบที่ {attempt})..."
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema_class,
                        temperature=0.85,
                    ),
                )
                print(f"✅ สำเร็จด้วยโมเดล {model_name}!")
                return json.loads(response.text)

            except errors.ServerError as e:
                wait_sec = 15 * attempt  # รอ 15วิ, 30วิ, 45วิ, 60วิ
                print(
                    f"⚠️ เซิร์ฟเวอร์คิวเต็ม (503) รอ {wait_sec} วินาทีแล้วลองใหม่..."
                )
                time.sleep(wait_sec)
            except errors.ClientError as e:
                print(
                    f"⚠️ โมเดล {model_name} ไม่รองรับ ({e.code}) ข้ามไปใช้โมเดลถัดไป..."
                )
                break
            except Exception as e:
                print(f"⚠️ เกิดข้อผิดพลาดอื่น: {e} รอ 15 วินาที...")
                time.sleep(15)

    raise RuntimeError(
        "ไม่สามารถสร้างคอนเทนต์ได้ เนื่องจากเซิร์ฟเวอร์ Google คิวเต็มทุกโมเดล"
    )


def generate_chinese_posts():
    day_th, day_zh, _ = get_thai_day_info()
    zh_recipes = get_landscape_recipes(5)

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการสร้าง Prompt ภาพโปสการ์ดอวยพรสวัสดีตอนเช้าสไตล์ทิวทัศน์จีนมงคล (Chinese Auspicious Morning Landscape Greeting Card Art)
    จงคิดคอนเทนต์สำหรับกลุ่มชาวจีน (早安吉祥如意花語圖) วันนี้ ({day_th} / {day_zh}) จำนวน **5 ชุด** ไม่ซ้ำกัน
    
    อ้างอิงตามโจทย์ภาพด้านล่างนี้ทีละชุด:
    {zh_recipes}
    
    โครงสร้าง Prompt ภาพ (image_prompt_en) ทุกชุด:
    - สัดส่วนแนวตั้ง `9:16 vertical aspect ratio` ภาพวาดดิจิทัลอาร์ต 3D กึ่งภาพถ่ายสมจริง สีสันสดใสเจิดจ้า แสงอาทิตย์ยามเช้าส่องประกายอบอุ่น
    - กิ่งดอกไม้มงคลยื่นลงมาจากมุมบนซ้าย และพุ่มดอกไม้บานสะพรั่งเต็มพื้นที่ด้านล่างตามโจทย์
    - ทิวทัศน์ตรงกลางและฉากหลังตามโจทย์ มีนกกระเรียนมงคล (red-crowned cranes) บินบนท้องฟ้าสีทองอ่อนๆ
    - **ข้อความลอยเด่นบนท้องฟ้าด้านบน (ไม่มีป้ายแดง):** `In the upper bright sunrise sky, large bold glossy crimson-red Chinese calligraphy text with gleaming gold outlines and small golden auspicious cloud motifs, reading Line 1: "[text_line_1_zh]", Line 2: "[text_line_2_zh]", Line 3: "[text_line_3_zh]"`
    
    กฎเหล็กของกลุ่มจีน:
    1. ภาษาจีนทั้งหมดต้องใช้ **อักษรจีนตัวเต็ม (Traditional Chinese)** เท่านั้น (เช่น 笑口常開, 歲歲平安, 吉祥如意, 身體健康)
    2. **ห้าม** กล่าวถึงหรือมีภาพเกี่ยวกับ: ดวงชะตา 12 นักษัตร (十二生肖), อาหาร/ของกิน (美食), ปฏิทิน (日历), การเมือง (政治) และศาสนา (宗教) เด็ดขาด
    """
    return call_gemini_with_retry(prompt, ChineseBatch)["posts"]


def generate_thai_posts():
    day_th, _, day_color = get_thai_day_info()
    th_recipes = get_landscape_recipes(5)

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการสร้าง Prompt ภาพโปสการ์ดอวยพรสวัสดีตอนเช้าสไตล์ทิวทัศน์มงคล
    จงคิดคอนเทนต์สำหรับกลุ่มคนไทย (ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน) วันนี้ ({day_th} โทนสี{day_color}) จำนวน **5 ชุด** ไม่ซ้ำกัน
    
    อ้างอิงตามโจทย์ภาพด้านล่างนี้ทีละชุด (ปรับโทนสีดอกไม้หรือแสงให้เข้ากับ{day_th} {day_color}):
    {th_recipes}
    
    โครงสร้าง Prompt ภาพ (image_prompt_en) ทุกชุด:
    - สัดส่วนแนวตั้ง `9:16 vertical aspect ratio` ภาพวาดดิจิทัลอาร์ต 3D กึ่งภาพถ่ายสมจริง สีสันสดใสเจิดจ้า แสงอาทิตย์ยามเช้าส่องประกายอบอุ่น
    - กิ่งดอกไม้มงคลยื่นลงมาจากมุมบนซ้าย และพุ่มดอกไม้บานสะพรั่งเต็มพื้นที่ด้านล่างตามโจทย์
    - ทิวทัศน์ตรงกลางและฉากหลังตามโจทย์
    - **ข้อความลอยเด่นบนท้องฟ้าด้านบน:** `In the upper bright sunrise sky, large bold glossy crimson-red Thai typography text with gleaming gold outlines and subtle golden light glow, reading Line 1: "[text_line_1_th]" and Line 2: "[text_line_2_th]"`
    """
    return call_gemini_with_retry(prompt, ThaiBatch)["posts"]


if __name__ == "__main__":
    print("=== เริ่มสร้างคอนเทนต์ส่วนที่ 1: กลุ่มจีน (5 ชุด) ===")
    zh_posts = generate_chinese_posts()

    print("\n=== เริ่มสร้างคอนเทนต์ส่วนที่ 2: กลุ่มไทย (5 ชุด) ===")
    th_posts = generate_thai_posts()

    now_str = get_thai_now().strftime("%d/%m/%Y เวลา %H:%M น.")
    day_th, _, day_color = get_thai_day_info()

    lines = []
    lines.append("=" * 65)
    lines.append(f"📅 อัปเดตล่าสุด: {day_th}ที่ {now_str} (เวลาไทย)")
    lines.append(
        f"🎨 สไตล์ภาพ: ทิวทัศน์ขุนเขา-เก๋งจีน-น้ำตก + ดอกไม้แสงเช้า (สัดส่วน 9:16)"
    )
    lines.append("=" * 65)

    lines.append(
        "\n🇨🇳 [ส่วนที่ 1: กลุ่มจีน 早安吉祥如意花語圖 - 5 ชุด]"
    )
    lines.append(
        "⚠️ กฎกลุ่ม: โพสต์ได้สูงสุดไม่เกิน 5 โพสต์/วัน | ใช้จีนตัวเต็มทั้งหมด"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(zh_posts, start=1):
        lines.append(f"\n--- 🇨🇳 ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(
            f"🖼️ ข้อความบนท้องฟ้า: {item['text_line_1_zh']} / {item['text_line_2_zh']} / {item['text_line_3_zh']}"
        )
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_zh']}")
        lines.append(f"🇹🇭 คำแปลไทย: {item['translation_th']}")
        lines.append(
            f"🎨 Image Prompt (ก๊อปปี้ไปเจนภาพได้เลย):\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    lines.append(
        "\n\n🇹🇭 [ส่วนที่ 2: กลุ่มไทย ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน - 5 ชุด]"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(th_posts, start=1):
        lines.append(f"\n--- 🇹🇭 ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(
            f"🖼️ ข้อความบนท้องฟ้า: {item['text_line_1_th']} / {item['text_line_2_th']}"
        )
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_th']}")
        lines.append(
            f"🎨 Image Prompt (ก๊อปปี้ไปเจนภาพได้เลย):\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    output_text = "\n".join(lines)

    with open("today_post.txt", "w", encoding="utf-8") as f:
        f.write(output_text)

    print("\n✅ บันทึกคอนเทนต์ทั้ง 10 ชุด ลงไฟล์ today_post.txt สำเร็จเรียบร้อย!")
