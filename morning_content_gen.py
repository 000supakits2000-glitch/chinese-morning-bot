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
        description="Prompt ภาษาอังกฤษละเอียดๆ สไตล์ทิวทัศน์จีนมงคลสีสันสดใสจัดจ้าน มีตัวอักษรพู่กันจีนสีแดงขอบทอง 3 บรรทัดลอยบนท้องฟ้าด้านบน สัดส่วน 9:16"
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
        description="Prompt ภาษาอังกฤษละเอียดๆ สไตล์ทิวทัศน์ไทยแท้ๆ สีสันสดใสจัดจ้าน แสงเช้าเจิดจ้า สัดส่วน 9:16 และลงท้ายด้วย clean open sky space at the top, no text"
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
        0: ("วันจันทร์", "สีเหลือง / สีทอง (Bright Yellow & Gold)"),
        1: ("วันอังคาร", "สีชมพูสดใส (Vibrant Pink & Magenta)"),
        2: ("วันพุธ", "สีเขียวมรกตและทอง (Emerald Green & Gold)"),
        3: ("วันพฤหัสบดี", "สีส้มแสดและทอง (Vibrant Orange & Amber)"),
        4: ("วันศุกร์", "สีฟ้าครามและน้ำเงินสด (Vivid Sky Blue & Turquoise)"),
        5: ("วันเสาร์", "สีม่วงสดใส (Rich Royal Purple & Violet)"),
        6: ("วันอาทิตย์", "สีแดงทับทิมและทอง (Brilliant Ruby Red & Gold)"),
    }
    return days_map[get_thai_now().weekday()]


def get_chinese_landscape_recipes(count: int = 5) -> str:
    flowers = [
        "jewel-toned hot pink and gold Peony flowers with overhanging bright cherry blossom branches (ดอกโบตั๋นและซากุระสีสด)",
        "vivid magenta-pink Lotus flowers in crystal water and bright pink Plum Blossoms overhead (ดอกบัวชมพูสดและดอกเหมย)",
        "vibrant royal blue, violet, and pink Hydrangeas with lush crimson roses along a stone balustrade (ดอกไฮเดรนเยียและกุหลาบสีสด)",
        "brilliant golden-yellow Phalaenopsis Orchids and radiant Osmanthus blossoms (ดอกกล้วยไม้เหลืองทองและหอมหมื่นลี้)",
        "lush scarlet-red Camellia flowers and cascading vivid purple wisteria blossoms (ดอกคามิเลียแดงและวิสทีเรียม่วง)",
        "radiant golden Chrysanthemums and vibrant pink Magnolia branches in full bloom (ดอกเบญจมาศทองและแมกโนเลียชมพู)",
    ]

    landscapes = [
        "majestic traditional Chinese palace pavilion perched on a cliff beside a sparkling turquoise cascading waterfall, stone staircase with glowing red-gold lanterns, misty emerald mountains, and red-crowned cranes flying in the radiant golden sunrise sky",
        "serene Jiangnan ancient water town with white-walled houses, glowing red lanterns, lush green weeping willow trees, traditional wooden boats on a shimmering golden-blue river, and an arched stone bridge at sunrise",
        "tranquil classical Chinese garden with a bright red-and-gold wooden lakeside pavilion, stone arch bridge over crystal-clear turquoise water with bright orange-and-white koi fish, misty mountain peaks, and flying white cranes",
        "panoramic misty mountain valley at dawn with tiered crystal waterfalls, ornate temple roofs peeking through sunlit golden clouds, stone pathway lined with vivid flowers, and brilliant sunbeams",
    ]

    selected_flowers = random.sample(flowers, count)
    return "\n".join(
        [
            f"ชุดที่ {i+1}: ดอกไม้={selected_flowers[i]} | ทิวทัศน์={random.choice(landscapes)}"
            for i in range(count)
        ]
    )


def get_thai_landscape_recipes(count: int = 5) -> str:
    thai_flowers = [
        "vibrant jewel-toned pink and white Thai sacred Lotus flowers with sparkling morning dew drops (ดอกบัวหลวงสีชมพูขาวสดใส)",
        "cascading brilliant golden-yellow Ratchaphruek (Golden Shower) blossoms glowing in sunlight (ดอกราชพฤกษ์สีเหลืองทองอร่าม)",
        "lush white, golden-yellow, and bright pink Plumeria (Leelawadee) flowers beside a carved stone basin (ดอกลีลาวดีสีสด)",
        "richly saturated purple, magenta, and blue Thai Vanda Orchids blooming in lush emerald greenery (ดอกกล้วยไม้แวนด้าไทยสีสด)",
        "delicate white Thai Jasmine garlands and bright orange-gold Champaka flowers in a gleaming silver bowl (ดอกมะลิและดอกจำปา)",
        "hyper-vibrant magenta Bougainvillea and brilliant orange-gold Marigold flowers along a wooden garden fence (ดอกเฟื่องฟ้าและดอกดาวเรืองสีสด)",
    ]

    thai_landscapes = [
        "traditional Thai teakwood house (Ruen Thai) with ornate golden-trimmed gabled roofs beside a sparkling canal at sunrise, wooden pier, glowing morning mist over turquoise-gold water, and radiant sunbeams",
        "serene traditional Thai wooden pavilion (Sala Thai) overlooking a crystal-clear lotus pond in a lush vibrant tropical garden, misty emerald mountains in the distance, and brilliant golden morning sunlight",
        "scenic Thai riverside countryside at dawn, traditional wooden rowboat floating on shimmering golden-blue water, lush vivid green trees, distant gleaming golden temple spire (chedi) amidst sunlit mist",
        "peaceful northern Thai Lanna-style wooden garden bridge over a crystal-clear forest stream, lush emerald ferns, brilliant golden sun rays filtering through trees, and vibrant morning glow",
        "tranquil Thai botanical water garden at sunrise, carved stone water fountain, blooming lotus pond with colorful swimming fish, and radiant golden light illuminating a crisp blue-and-gold sky",
    ]

    selected_flowers = random.sample(thai_flowers, count)
    return "\n".join(
        [
            f"ชุดที่ {i+1}: ดอกไม้ไทย={selected_flowers[i]} | บรรยากาศแบบไทย={random.choice(thai_landscapes)}"
            for i in range(count)
        ]
    )


def call_gemini_with_retry(prompt: str, schema_class):
    """สลับไปใช้โมเดลสำรองอย่างรวดเร็ว หากตัวหลักคิวเต็ม (503)"""
    candidate_models = [
        "gemini-3.8-flash",
        "gemini-3.8-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
    ]

    for model_name in candidate_models:
        for attempt in range(1, 3):
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
                print(
                    f"⚠️ โมเดล {model_name} คิวเต็ม (503) รอ 5 วินาที..."
                )
                time.sleep(5)
            except errors.ClientError as e:
                print(
                    f"⚠️ โมเดล {model_name} ไม่รองรับ ({e.code}) ข้ามทันที..."
                )
                break
            except Exception as e:
                print(f"⚠️ ข้อผิดพลาด: {e} รอ 5 วินาที...")
                time.sleep(5)

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
    
    โครงสร้าง Prompt ภาพ (image_prompt_en) ทุกชุด (ต้องเน้นสีสันสดใสเจิดจ้า HDR):
    - สัดส่วนแนวตั้ง `9:16 vertical aspect ratio` ภาพวาดดิจิทัลอาร์ต 3D กึ่งภาพถ่ายสมจริง **เน้นสีสันสดใสอิ่มตัวสูง แสงแดดยามเช้าเจิดจ้า คมชัดระดับ HDR**: `Hyper-vibrant saturated colors, rich vivid color palette, HDR quality, breathtaking crystal-clear 8k digital painting and 3D photorealistic scenery, radiant golden sunrise sunbeams, luminous morning glow`
    - กิ่งดอกไม้มงคลสีสดยื่นลงมาจากมุมบนซ้าย และพุ่มดอกไม้สีสดใสบานสะพรั่งเต็มพื้นที่ด้านล่างตามโจทย์
    - ทิวทัศน์ตรงกลางและฉากหลังตามโจทย์ มีนกกระเรียนมงคล (red-crowned cranes) บินบนท้องฟ้าสีฟ้าครามตัดแสงทองยามเช้า
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
    
    อ้างอิงตามโจทย์ภาพด้านล่างนี้ทีละชุด (ปรับโทนสีดอกไม้หรือแสงยามเช้าให้เข้ากับ{day_th} {day_color} แบบสีสดใสจัดจ้าน):
    {th_recipes}
    
    ข้อกำหนดสำคัญสำหรับกลุ่มไทย:
    1. **text_for_manual_overlay_th:** คิดข้อความสวัสดีตามวัน (เช่น "สวัสดี{day_th} ขอให้สุขใจ...") หรือคำคมข้อคิดดีๆ ภาษาไทยสั้นๆ อ่านง่าย เพื่อแยกออกมาให้ผู้ใช้เอาไปพิมพ์แปะลงภาพเองทีหลัง
    2. **image_prompt_en (ห้ามใส่ตัวหนังสือในภาพเด็ดขาด และต้องเน้นสีสดใสจัดจ้า):**
       - เขียน Prompt ภาษาอังกฤษบรรยายภาพทิวทัศน์ไทยและดอกไม้ไทยตามโจทย์ สัดส่วนแนวตั้ง `9:16 vertical aspect ratio`
       - **ต้องเน้นสีสันสดใสอิ่มตัวสูง แสงแดดยามเช้าเจิดจ้า คมชัดระดับ HDR:** `Hyper-vibrant saturated colors, rich vivid color palette, HDR quality, luminous 8k digital painting and photorealistic Thai scenery, radiant golden sunrise rays, crystal-clear water reflections, high contrast`
       - **ห้าม** มีสถาปัตยกรรมจีนในภาพนี้ ให้เป็นบรรยากาศไทยแท้ๆ เท่านั้น
       - **ต้องเว้นพื้นที่ท้องฟ้าด้านบนให้โล่งสะอาดตา และลงท้าย Prompt ทุกชุดด้วย:** `clean open bright sky space at the top, no text, no letters, no watermark`
    """
    return call_gemini_with_retry(prompt, ThaiBatch)["posts"]


if __name__ == "__main__":
    print("=== เริ่มสร้างคอนเทนต์ส่วนที่ 1: กลุ่มจีน (สีสดใส + มีอักษรจีนในภาพ - 5 ชุด) ===")
    zh_posts = generate_chinese_posts()

    print("\n=== เริ่มสร้างคอนเทนต์ส่วนที่ 2: กลุ่มไทย (สีสดใส + ภาพสไตล์ไทย ไม่มีตัวหนังสือ - 5 ชุด) ===")
    th_posts = generate_thai_posts()

    now_str = get_thai_now().strftime("%d/%m/%Y เวลา %H:%M น.")
    day_th, day_color = get_thai_day_info()

    lines = []
    lines.append("=" * 65)
    lines.append(f"📅 อัปเดตล่าสุด: {day_th}ที่ {now_str} (เวลาไทย)")
    lines.append(
        f"🎨 โทนสีประจำวัน (กลุ่มไทย): {day_color} | โหมด: สีสดใสเจิดจ้า (Hyper-Vibrant HDR)"
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

    print("\n✅ บันทึกคอนเทนต์โหมดสีสดใสทั้ง 10 ชุด ลงไฟล์ today_post.txt สำเร็จเรียบร้อย!")
