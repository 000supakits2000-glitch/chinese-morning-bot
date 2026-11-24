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
        description="ข้อความบรรทัดบนภาษาจีนตัวเต็ม ห้ามระบุวัน เช่น 早上好！, 早安吉祥！"
    )
    text_line_2_zh: str = Field(
        description="ข้อความบรรทัดกลางภาษาจีนตัวเต็ม 4 ตัวอักษร ห้ามระบุวัน เช่น 吉祥如意, 身體健康, 花開富貴"
    )
    text_line_3_zh: str = Field(
        description="ข้อความบรรทัดล่างภาษาจีนตัวเต็ม 4 ตัวอักษร ห้ามระบุวัน เช่น 笑口常開, 歲歲平安, 平安喜樂"
    )
    caption_zh: str = Field(
        description="แคปชั่นโพสต์ภาษาจีนตัวเต็ม 2-3 บรรทัด อ่านแล้วอบอุ่น เป็นสิริมงคล ห้ามระบุวันในสัปดาห์ ใส่อีโมจิให้เหมาะสม"
    )
    translation_th: str = Field(
        description="คำแปลภาษาไทยของข้อความบนภาพและแคปชั่น"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษละเอียดๆ สไตล์ทิวทัศน์จีนมงคล มีตัวอักษรพู่กันจีนสีแดงขอบทอง 3 บรรทัดลอยบนท้องฟ้าด้านบน สัดส่วน 9:16"
    )


class ThaiPostItem(BaseModel):
    flower_name_th: str = Field(description="ชื่อดอกไม้ไทยภาษาไทย")
    text_for_manual_overlay_th: str = Field(
        description="ข้อความสวัสดีตามวันหรือคำอวยพรภาษาไทยสั้นๆ อ่านง่าย (สำหรับให้ผู้ใช้ไปพิมพ์แปะลงภาพเอง)"
    )
    caption_th: str = Field(
        description="แคปชั่นโพสต์ภาษาไทย 2-3 บรรทัด อวยพรให้มีความสุข สุขภาพแข็งแรง ใส่อีโมจิให้เหมาะสม"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษละเอียดๆ สไตล์ทิวทัศน์ไทยแท้ๆ (เรือนไทย ศาลาไทย ริมน้ำ ดอกไม้ไทย) แสงเช้าสดใส สัดส่วน 9:16 และต้องลงท้ายด้วย clean sky space, no text"
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
        0: ("วันจันทร์", "สีเหลือง / สีทอง"),
        1: ("วันอังคาร", "สีชมพู"),
        2: ("วันพุธ", "สีเขียว / สีทอง"),
        3: ("วันพฤหัสบดี", "สีส้ม / สีแสด"),
        4: ("วันศุกร์", "สีฟ้า / สีน้ำเงิน"),
        5: ("วันเสาร์", "สีม่วง"),
        6: ("วันอาทิตย์", "สีแดง"),
    }
    return days_map[get_thai_now().weekday()]


def get_chinese_landscape_recipes(count: int = 5) -> str:
    """สุ่มโจทย์ภาพทิวทัศน์จีนมงคล 5 ชุด"""
    flowers = [
        "vibrant pink Peony flowers and overhanging cherry blossom branches (ดอกโบตั๋นและซากุระ)",
        "blooming pink Lotus flowers in the pond and pink Plum Blossoms overhead (ดอกบัวชมพูและดอกเหมย)",
        "colorful pink and blue Hydrangeas with blooming roses along a stone balustrade (ดอกไฮเดรนเยียและกุหลาบ)",
        "radiant yellow Phalaenopsis Orchids and golden Osmanthus blossoms (ดอกกล้วยไม้เหลืองและหอมหมื่นลี้)",
        "lush red Camellia flowers and cascading wisteria blossoms (ดอกคามิเลียและวิสทีเรีย)",
        "golden Chrysanthemums and pink Magnolia branches in bloom (ดอกเบญจมาศทองและแมกโนเลีย)",
    ]

    landscapes = [
        "majestic traditional Chinese palace pavilion perched on a cliff beside a cascading waterfall, stone staircase with glowing stone lanterns, misty mountains, and red-crowned cranes flying in the golden sunrise sky",
        "serene Jiangnan ancient water town with white-walled houses, red lanterns, weeping willow trees, traditional wooden boats on a golden river, and an arched stone bridge at sunrise",
        "tranquil classical Chinese garden with a wooden lakeside pavilion, stone arch bridge over turquoise water with swimming koi fish, misty mountain peaks, and flying white cranes",
        "panoramic misty mountain valley at dawn with tiered waterfalls, ancient temple roofs peeking through golden clouds, stone pathway lined with flowers, and warm sunbeams",
    ]

    selected_flowers = random.sample(flowers, count)
    return "\n".join(
        [
            f"ชุดที่ {i+1}: ดอกไม้={selected_flowers[i]} | ทิวทัศน์={random.choice(landscapes)}"
            for i in range(count)
        ]
    )


def get_thai_landscape_recipes(count: int = 5) -> str:
    """สุ่มโจทย์ภาพทิวทัศน์สไตล์ไทยแท้ๆ 5 ชุด"""
    thai_flowers = [
        "blooming pink and white Thai sacred Lotus flowers with morning dew drops (ดอกบัวหลวงสีชมพูขาว)",
        "cascading golden yellow Ratchaphruek (Golden Shower) blossoms hanging gracefully (ดอกราชพฤกษ์/ดอกคูนสีเหลืองทอง)",
        "fragrant white and yellow Plumeria (Leelawadee) flowers beside a carved stone basin (ดอกลีลาวดี)",
        "vibrant purple and pink Thai Vanda Orchids blooming in lush tropical greenery (ดอกกล้วยไม้แวนด้าไทย)",
        "delicate white Thai Jasmine garlands and blooming Champaka flowers in a traditional silver bowl (ดอกมะลิและดอกจำปา)",
        "colorful Bougainvillea and bright Marigold flowers along a wooden garden fence (ดอกเฟื่องฟ้าและดอกดาวเรือง)",
    ]

    thai_landscapes = [
        "traditional Thai teakwood house (Ruen Thai) with high gabled roofs beside a peaceful canal at sunrise, wooden pier, gentle morning mist over water, and warm golden sunbeams",
        "serene traditional Thai wooden pavilion (Sala Thai) overlooking a tranquil lotus pond in a lush tropical garden, misty mountains in the distance, and radiant morning sunlight",
        "scenic Thai riverside countryside at dawn, traditional wooden rowboat floating on calm golden-lit water, lush green trees, distant gleaming golden temple spire (chedi) amidst morning mist",
        "peaceful northern Thai Lanna-style wooden garden bridge over a clear forest stream, tropical ferns, glowing morning sun rays filtering through trees, and soft golden mist",
        "tranquil Thai botanical water garden at sunrise, carved stone water fountain, blooming lotus pond with swimming colorful fish, and warm golden light illuminating the misty sky",
    ]

    selected_flowers = random.sample(thai_flowers, count)
    return "\n".join(
        [
            f"ชุดที่ {i+1}: ดอกไม้ไทย={selected_flowers[i]} | บรรยากาศแบบไทย={random.choice(thai_landscapes)}"
            for i in range(count)
        ]
    )


def call_gemini_with_retry(prompt: str, schema_class):
    candidate_models = [
        "gemini-3.8-flash",
        "gemini-3.8-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]

    for model_name in candidate_models:
        for attempt in range(1, 5):
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

            except errors.ServerError:
                wait_sec = 15 * attempt
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
    zh_recipes = get_chinese_landscape_recipes(5)

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการสร้าง Prompt ภาพโปสการ์ดอวยพรสวัสดีตอนเช้าสไตล์ทิวทัศน์จีนมงคล (Chinese Auspicious Morning Landscape Greeting Card Art)
    จงคิดคอนเทนต์สำหรับกลุ่มชาวจีน (早安吉祥如意花語圖) จำนวน **5 ชุด** ไม่ซ้ำกัน
    
    อ้างอิงตามโจทย์ภาพด้านล่างนี้ทีละชุด:
    {zh_recipes}
    
    โครงสร้าง Prompt ภาพ (image_prompt_en) ทุกชุด:
    - สัดส่วนแนวตั้ง `9:16 vertical aspect ratio` ภาพวาดดิจิทัลอาร์ต 3D กึ่งภาพถ่ายสมจริง สีสันสดใสเจิดจ้า แสงอาทิตย์ยามเช้าส่องประกายอบอุ่น
    - กิ่งดอกไม้มงคลยื่นลงมาจากมุมบนซ้าย และพุ่มดอกไม้บานสะพรั่งเต็มพื้นที่ด้านล่างตามโจทย์
    - ทิวทัศน์ตรงกลางและฉากหลังตามโจทย์ มีนกกระเรียนมงคล (red-crowned cranes) บินบนท้องฟ้าสีทองอ่อนๆ
    - **ข้อความลอยเด่นบนท้องฟ้าด้านบน (ไม่มีป้ายแดง):** `In the upper bright sunrise sky, large bold glossy crimson-red Chinese calligraphy text with gleaming gold outlines and small golden auspicious cloud motifs, reading Line 1: "[text_line_1_zh]", Line 2: "[text_line_2_zh]", Line 3: "[text_line_3_zh]"`
    
    กฎเหล็กของกลุ่มจีนที่ห้ามละเมิดเด็ดขาด:
    1. ภาษาจีนทั้งหมดต้องใช้ **อักษรจีนตัวเต็ม (Traditional Chinese)** เท่านั้น (เช่น 笑口常開, 歲歲平安, 吉祥如意, 身體健康)
    2. **ห้ามระบุวันในสัปดาห์โดยเด็ดขาด** (ห้ามมีคำว่า 週一 ถึง 週日 หรือ 星期 ทั้งในภาพและในแคปชั่น)
    3. **ห้าม** กล่าวถึงหรือมีภาพเกี่ยวกับ: ดวงชะตา 12 นักษัตร (十二生肖), อาหาร/ของกิน (美食), ปฏิทิน (日历), การเมือง (政治) และศาสนา (宗教) เด็ดขาด
    """
    return call_gemini_with_retry(prompt, ChineseBatch)["posts"]


def generate_thai_posts():
    day_th, day_color = get_thai_day_info()
    th_recipes = get_thai_landscape_recipes(5)

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการสร้าง Prompt ภาพทิวทัศน์และดอกไม้สไตล์ไทยแท้ๆ สำหรับโพสต์สวัสดีตอนเช้าในกลุ่มคนไทย (ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน)
    จงคิดคอนเทนต์สำหรับวันนี้ ({day_th} โทนสี{day_color}) จำนวน **5 ชุด** ไม่ซ้ำกัน
    
    อ้างอิงตามโจทย์ภาพด้านล่างนี้ทีละชุด (ปรับโทนสีดอกไม้หรือแสงยามเช้าให้เข้ากับ{day_th} {day_color}):
    {th_recipes}
    
    ข้อกำหนดสำคัญสำหรับกลุ่มไทย:
    1. **text_for_manual_overlay_th:** คิดข้อความสวัสดีตามวัน (เช่น "สวัสดี{day_th} ขอให้สุขใจ...") หรือคำคมข้อคิดดีๆ ภาษาไทยสั้นๆ อ่านง่าย เพื่อแยกออกมาให้ผู้ใช้เอาไปพิมพ์แปะลงภาพเองทีหลัง
    2. **image_prompt_en (ห้ามใส่ตัวหนังสือในภาพเด็ดขาด):**
       - เขียน Prompt ภาษาอังกฤษบรรยายภาพทิวทัศน์ไทยและดอกไม้ไทยตามโจทย์ สัดส่วนแนวตั้ง `9:16 vertical aspect ratio`
       - เน้นสไตล์ภาพวาดดิจิทัลอาร์ตเสมือนจริง แสงแดดยามเช้าอบอุ่นสีทอง (Vibrant luminous digital painting and photorealistic Thai scenery, warm golden sunrise rays, peaceful morning mist, ultra-detailed)
       - **ห้าม** มีสถาปัตยกรรมจีนในภาพนี้ ให้เป็นบรรยากาศไทยแท้ๆ เท่านั้น
       - **ต้องเว้นพื้นที่ท้องฟ้าด้านบนให้โล่งสะอาดตา และลงท้าย Prompt ทุกชุดด้วย:** `clean open sky space at the top, no text, no letters, no watermark`
    """
    return call_gemini_with_retry(prompt, ThaiBatch)["posts"]


if __name__ == "__main__":
    print("=== เริ่มสร้างคอนเทนต์ส่วนที่ 1: กลุ่มจีน (มีตัวอักษรจีนในภาพ - 5 ชุด) ===")
    zh_posts = generate_chinese_posts()

    print("\n=== เริ่มสร้างคอนเทนต์ส่วนที่ 2: กลุ่มไทย (ภาพสไตล์ไทย ไม่มีตัวหนังสือในภาพ - 5 ชุด) ===")
    th_posts = generate_thai_posts()

    now_str = get_thai_now().strftime("%d/%m/%Y เวลา %H:%M น.")
    day_th, day_color = get_thai_day_info()

    lines = []
    lines.append("=" * 65)
    lines.append(f"📅 อัปเดตล่าสุด: {day_th}ที่ {now_str} (เวลาไทย)")
    lines.append(
        f"🎨 โทนสีประจำวัน (กลุ่มไทย): {day_color} | จำนวน: กลุ่มละ 5 ชุด"
    )
    lines.append("=" * 65)

    lines.append(
        "\n🇨🇳 [ส่วนที่ 1: กลุ่มจีน 早安吉祥如意花語圖 - 5 ชุด (ไม่ระบุวัน + มีอักษรจีนในภาพ)]"
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
            f"🎨 Image Prompt (ก๊อปปี้ไปเจนภาพพร้อมอักษรจีนได้เลย):\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    lines.append(
        "\n\n🇹🇭 [ส่วนที่ 2: กลุ่มไทย ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน - 5 ชุด (ภาพสไตล์ไทย ไม่ฝังตัวหนังสือ)]"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(th_posts, start=1):
        lines.append(f"\n--- 🇹🇭 ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(
            f"✍️ ข้อความแนะนำสำหรับนำไปพิมพ์แปะบนรูปเอง:\n{item['text_for_manual_overlay_th']}"
        )
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_th']}")
        lines.append(
            f"🎨 Image Prompt (ภาพเปล่าสไตล์ไทย เว้นที่ด้านบนไว้ใส่ข้อความ):\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    output_text = "\n".join(lines)

    with open("today_post.txt", "w", encoding="utf-8") as f:
        f.write(output_text)

    print("\n✅ บันทึกคอนเทนต์ทั้ง 10 ชุด ลงไฟล์ today_post.txt สำเร็จเรียบร้อย!")
