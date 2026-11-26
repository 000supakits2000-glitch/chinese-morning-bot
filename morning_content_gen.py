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
        description="ข้อความบรรทัดบนภาษาจีนตัวเต็ม ห้ามระบุวัน เช่น 早上好！, 早安吉祥！ หรือ 傍晚好！, 晚安吉祥！"
    )
    text_line_2_zh: str = Field(
        description="ข้อความบรรทัดกลางภาษาจีนตัวเต็ม 4 ตัวอักษร ห้ามระบุวัน เช่น 吉祥如意, 身體健康, 花開富貴, 平安喜樂"
    )
    text_line_3_zh: str = Field(
        description="ข้อความบรรทัดล่างภาษาจีนตัวเต็ม 4 ตัวอักษร ห้ามระบุวัน เช่น 笑口常開, 歲歲平安, 順心如意, 幸福安康"
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
        description="ข้อความสวัสดีตามวัน/ช่วงเวลา หรือคำอวยพรภาษาไทยสั้นๆ อ่านง่าย (สำหรับให้ผู้ใช้ไปพิมพ์แปะลงภาพเอง)"
    )
    caption_th: str = Field(
        description="แคปชั่นโพสต์ภาษาไทย 2-3 บรรทัด อวยพรให้มีความสุข สุขภาพแข็งแรง ใส่อีโมจิให้เหมาะสม"
    )
    image_prompt_en: str = Field(
        description="Prompt ภาษาอังกฤษละเอียดๆ สไตล์ทิวทัศน์ไทยแท้ๆ สีสันสดใสจัดจ้าน สัดส่วน 9:16 และลงท้ายด้วย clean open sky space at the top, no text"
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


def get_chinese_landscape_recipes(count: int = 5, time_of_day: str = "morning") -> str:
    flowers = [
        "jewel-toned hot pink and gold Peony flowers with overhanging bright cherry blossom branches (ดอกโบตั๋นและซากุระสีสด)",
        "vivid magenta-pink Lotus flowers in crystal water and bright pink Plum Blossoms overhead (ดอกบัวชมพูสดและดอกเหมย)",
        "vibrant royal blue, violet, and pink Hydrangeas with lush crimson roses along a stone balustrade (ดอกไฮเดรนเยียและกุหลาบสีสด)",
        "brilliant golden-yellow Phalaenopsis Orchids and radiant Osmanthus blossoms (ดอกกล้วยไม้เหลืองทองและหอมหมื่นลี้)",
        "lush scarlet-red Camellia flowers and cascading vivid purple wisteria blossoms (ดอกคามิเลียแดงและวิสทีเรียม่วง)",
        "radiant golden Chrysanthemums and vibrant pink Magnolia branches in full bloom (ดอกเบญจมาศทองและแมกโนเลียชมพู)",
    ]

    if time_of_day == "evening":
        landscapes = [
            "majestic traditional Chinese palace pavilion perched on a cliff beside a glowing waterfall at golden sunset, warm lit red-gold lanterns, misty purple-gold mountains, and red-crowned cranes flying across a radiant amber twilight sky",
            "serene Jiangnan ancient water town at dusk with warm glowing red lanterns reflecting on the shimmering golden-orange canal, willow trees, traditional wooden boats, and an arched stone bridge under a breathtaking sunset sky",
            "tranquil classical Chinese garden at golden hour with a red-and-gold lakeside pavilion lit by warm lanterns, stone arch bridge over sunset-reflecting water with bright koi fish, and glowing orange-pink clouds",
        ]
    else:
        landscapes = [
            "majestic traditional Chinese palace pavilion perched on a cliff beside a sparkling turquoise cascading waterfall, stone staircase with glowing red-gold lanterns, misty emerald mountains, and red-crowned cranes flying in the radiant golden sunrise sky",
            "serene Jiangnan ancient water town with white-walled houses, glowing red lanterns, lush green weeping willow trees, traditional wooden boats on a shimmering golden-blue river, and an arched stone bridge at sunrise",
            "tranquil classical Chinese garden with a bright red-and-gold wooden lakeside pavilion, stone arch bridge over crystal-clear turquoise water with bright orange-and-white koi fish, misty mountain peaks, and flying white cranes",
            "panoramic misty mountain valley at dawn with tiered crystal waterfalls, ornate temple roofs peeking through sunlit golden clouds, stone pathway lined with vivid flowers, and brilliant sunbeams",
        ]

    selected_flowers = random.sample(flowers, min(count, len(flowers)))
    return "\n".join(
        [
            f"ชุดที่ {i+1}: ดอกไม้={selected_flowers[i]} | ทิวทัศน์={random.choice(landscapes)}"
            for i in range(count)
        ]
    )


def get_thai_landscape_recipes(count: int = 5, time_of_day: str = "morning") -> str:
    thai_flowers = [
        "vibrant jewel-toned pink and white Thai sacred Lotus flowers with sparkling dew drops (ดอกบัวหลวงสีชมพูขาวสดใส)",
        "cascading brilliant golden-yellow Ratchaphruek (Golden Shower) blossoms glowing in sunlight (ดอกราชพฤกษ์สีเหลืองทองอร่าม)",
        "lush white, golden-yellow, and bright pink Plumeria (Leelawadee) flowers beside a carved stone basin (ดอกลีลาวดีสีสด)",
        "richly saturated purple, magenta, and blue Thai Vanda Orchids blooming in lush emerald greenery (ดอกกล้วยไม้แวนด้าไทยสีสด)",
        "delicate white Thai Jasmine garlands and bright orange-gold Champaka flowers in a gleaming silver bowl (ดอกมะลิและดอกจำปา)",
        "hyper-vibrant magenta Bougainvillea and brilliant orange-gold Marigold flowers along a wooden garden fence (ดอกเฟื่องฟ้าและดอกดาวเรืองสีสด)",
    ]

    if time_of_day == "evening":
        thai_landscapes = [
            "traditional Thai teakwood house (Ruen Thai) beside a tranquil canal at golden sunset, warm glowing amber light reflecting on calm water, wooden pier, and a breathtaking orange-pink twilight sky",
            "serene traditional Thai wooden pavilion (Sala Thai) overlooking a peaceful lotus pond at sunset, warm golden hour rays illuminating tropical flowers, and glowing amber-violet clouds in the distance",
            "scenic Thai riverside countryside at dusk, traditional wooden rowboat floating on shimmering golden-orange water, warm sunset glow behind a distant golden temple spire (chedi)",
        ]
    else:
        thai_landscapes = [
            "traditional Thai teakwood house (Ruen Thai) with ornate golden-trimmed gabled roofs beside a sparkling canal at sunrise, wooden pier, glowing morning mist over turquoise-gold water, and radiant sunbeams",
            "serene traditional Thai wooden pavilion (Sala Thai) overlooking a crystal-clear lotus pond in a lush vibrant tropical garden, misty emerald mountains in the distance, and brilliant golden morning sunlight",
            "scenic Thai riverside countryside at dawn, traditional wooden rowboat floating on shimmering golden-blue water, lush vivid green trees, distant gleaming golden temple spire (chedi) amidst sunlit mist",
            "peaceful northern Thai Lanna-style wooden garden bridge over a crystal-clear forest stream, lush emerald ferns, brilliant golden sun rays filtering through trees, and vibrant morning glow",
            "tranquil Thai botanical water garden at sunrise, carved stone water fountain, blooming lotus pond with colorful swimming fish, and radiant golden light illuminating a crisp blue-and-gold sky",
        ]

    selected_flowers = random.sample(thai_flowers, min(count, len(thai_flowers)))
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
    zh_recipes = get_chinese_landscape_recipes(5, time_of_day="morning")

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
    th_recipes = get_thai_landscape_recipes(5, time_of_day="morning")

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


def generate_chinese_evening_posts(count: int = 2):
    zh_recipes = get_chinese_landscape_recipes(count, time_of_day="evening")

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการสร้าง Prompt ภาพโปสการ์ดอวยพร **สวัสดีตอนเย็น (傍晚好 / 晚安吉祥)** สไตล์ทิวทัศน์จีนมงคลยามอาทิตย์อัสดง
    จงคิดคอนเทนต์สวัสดีตอนเย็นสำหรับกลุ่มชาวจีน (早安吉祥如意花語圖) จำนวน **{count} ชุด** ไม่ซ้ำกัน
    
    อ้างอิงตามโจทย์ภาพยามเย็นด้านล่างนี้ทีละชุด:
    {zh_recipes}
    
    โครงสร้าง Prompt ภาพ (image_prompt_en) ทุกชุด (โทนแสงอาทิตย์ตกยามเย็น Golden Hour สวยอบอุ่น):
- สัดส่วนแนวตั้ง `9:16 vertical aspect ratio` ภาพวาดดิจิทัลอาร์ต 3D กึ่งภาพถ่ายสมจริง **เน้นแสงอาทิตย์ตกสีทองส้มอมชมพูอบอุ่น คมชัดระดับ HDR**: `Hyper-vibrant warm sunset colors, rich golden-orange and amber twilight palette, HDR quality, breathtaking crystal-clear 8k digital painting and 3D photorealistic scenery, glowing warm lanterns, peaceful evening atmosphere`
- กิ่งดอกไม้มงคลสีสดยื่นลงมาจากมุมบนซ้าย และพุ่มดอกไม้สีสดใสบานสะพรั่งเต็มพื้นที่ด้านล่างตามโจทย์
- **ข้อความลอยเด่นบนท้องฟ้ายามเย็นด้านบน (ไม่มีป้ายแดง):** `In the upper glowing sunset sky, large bold glossy crimson-red Chinese calligraphy text with gleaming gold outlines and small golden auspicious cloud motifs, reading Line 1: "[text_line_1_zh]", Line 2: "[text_line_2_zh]", Line 3: "[text_line_3_zh]"`
    
    กฎเหล็กของกลุ่มจีนที่ห้ามละเมิดเด็ดขาด:
1. ภาษาจีนทั้งหมดต้องใช้ **อักษรจีนตัวเต็ม (Traditional Chinese)** เท่านั้น (บรรทัดบนให้ใช้คำทักทายตอนเย็น เช่น 傍晚好！, 晚安吉祥！)
2. **ห้ามระบุวันในสัปดาห์โดยเด็ดขาด** (ห้ามมีคำว่า 週一 ถึง 週日 หรือ 星期 ทั้งในภาพและในแคปชั่น)
3. **ห้าม** กล่าวถึงหรือมีภาพเกี่ยวกับ: ดวงชะตา 12 นักษัตร (十二生肖), อาหาร/ของกิน/มื้อเย็น (美食/晚餐), ปฏิทิน (日历), การเมือง (政治) และศาสนา (宗教) เด็ดขาด (ให้อวยพรเรื่องการพักผ่อน ความสบายใจ และสุขภาพแทน)
    """
    return call_gemini_with_retry(prompt, ChineseBatch)["posts"]


def generate_thai_evening_posts(count: int = 2):
    day_th, _ = get_thai_day_info()
    th_recipes = get_thai_landscape_recipes(count, time_of_day="evening")

    prompt = f"""
    คุณคือผู้เชี่ยวชาญการสร้าง Prompt ภาพทิวทัศน์และดอกไม้สไตล์ไทยแท้ๆ สำหรับโพสต์ **สวัสดีตอนเย็น** ในกลุ่มคนไทย (ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน)
    จงคิดคอนเทนต์สวัสดีตอนเย็นสำหรับเย็น{day_th}นี้ จำนวน **{count} ชุด** ไม่ซ้ำกัน
    
    อ้างอิงตามโจทย์ภาพยามเย็นด้านล่างนี้ทีละชุด:
    {th_recipes}
    
    ข้อกำหนดสำคัญสำหรับกลุ่มไทย (ตอนเย็น):
1. **text_for_manual_overlay_th:** คิดข้อความสวัสดีตอนเย็นภาษาไทยสั้นๆ อบอุ่น อ่านง่าย (เช่น "สวัสดีตอนเย็นครับ พักผ่อนให้สบายใจ...") เพื่อแยกออกมาให้ผู้ใช้เอาไปพิมพ์แปะลงภาพเองทีหลัง
2. **caption_th:** แคปชั่นโพสต์สวัสดีตอนเย็น 2-3 บรรทัด อวยพรให้เดินทางกลับบ้านปลอดภัย พักผ่อนให้หายเหนื่อย ใส่อีโมจิอบอุ่นๆ
3. **image_prompt_en (ห้ามใส่ตัวหนังสือในภาพเด็ดขาด และเน้นแสงเย็นอบอุ่น):**
  - เขียน Prompt ภาษาอังกฤษบรรยายภาพทิวทัศน์ไทยและดอกไม้ไทยยามเย็นตามโจทย์ สัดส่วนแนวตั้ง `9:16 vertical aspect ratio`
  - **เน้นแสงอาทิตย์ตกยามเย็น (Golden Hour Sunset) สีทองส้มอบอุ่น คมชัดระดับ HDR:** `Hyper-vibrant warm sunset colors, rich golden-orange and soft amber twilight palette, HDR quality, luminous 8k digital painting and photorealistic Thai scenery, peaceful evening glow, calm water reflections`
  - **ห้าม** มีสถาปัตยกรรมจีนในภาพนี้ ให้เป็นบรรยากาศไทยแท้ๆ เท่านั้น
  - **ต้องเว้นพื้นที่ท้องฟ้าด้านบนให้โล่งสะอาดตา และลงท้าย Prompt ทุกชุดด้วย:** `clean open sunset sky space at the top, no text, no letters, no watermark`
    """
    return call_gemini_with_retry(prompt, ThaiBatch)["posts"]


if __name__ == "__main__":
    print("=== ส่วนที่ 1: กลุ่มจีน ตอนเช้า (5 ชุด) ===")
    zh_posts = generate_chinese_posts()

    print("\n=== ส่วนที่ 2: กลุ่มไทย ตอนเช้า (5 ชุด) ===")
    th_posts = generate_thai_posts()

    print("\n=== ส่วนที่ 3: กลุ่มจีน ตอนเย็น (2 ชุด) ===")
    zh_evening_posts = generate_chinese_evening_posts(2)

    print("\n=== ส่วนที่ 4: กลุ่มไทย ตอนเย็น (2 ชุด) ===")
    th_evening_posts = generate_thai_evening_posts(2)

    now_str = get_thai_now().strftime("%d/%m/%Y เวลา %H:%M น.")
    day_th, day_color = get_thai_day_info()

    lines = []
    lines.append("=" * 65)
    lines.append(f"📅 อัปเดตล่าสุด: {day_th}ที่ {now_str} (เวลาไทย)")
    lines.append(
        f"🎨 โทนสีประจำวัน (กลุ่มไทย): {day_color} | โหมด: เช้า + เย็น (Hyper-Vibrant HDR)"
    )
    lines.append("=" * 65)

    # ส่วนที่ 1: จีนตอนเช้า
    lines.append(
        "\n🇨🇳 [ส่วนที่ 1: กลุ่มจีน ตอนเช้า 早安吉祥如意花語圖 - 5 ชุด]"
    )
    lines.append(
        "⚠️ กฎกลุ่ม: โพสต์ได้สูงสุดไม่เกิน 5 โพสต์/วัน | ใช้จีนตัวเต็มทั้งหมด"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(zh_posts, start=1):
        lines.append(f"\n--- 🇨🇳 เช้า ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(
            f"🖼️ ข้อความบนท้องฟ้า: {item['text_line_1_zh']} / {item['text_line_2_zh']} / {item['text_line_3_zh']}"
        )
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_zh']}")
        lines.append(f"🇹🇭 คำแปลไทย: {item['translation_th']}")
        lines.append(
            f"🎨 Image Prompt:\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    # ส่วนที่ 2: ไทยตอนเช้า
    lines.append(
        "\n\n🇹🇭 [ส่วนที่ 2: กลุ่มไทย ตอนเช้า ภาพสวย ดอกไม้งาม สวัสดีกันทุกวัน - 5 ชุด]"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(th_posts, start=1):
        lines.append(f"\n--- 🇹🇭 เช้า ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(
            f"✍️ ข้อความแนะนำสำหรับนำไปพิมพ์แปะบนรูปเอง:\n{item['text_for_manual_overlay_th']}"
        )
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_th']}")
        lines.append(
            f"🎨 Image Prompt (เว้นที่ด้านบนไว้ใส่ข้อความ):\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    # ส่วนที่ 3: จีนตอนเย็น
    lines.append(
        "\n\n🌅 🇨🇳 [ส่วนที่ 3: กลุ่มจีน สวัสดีตอนเย็น 傍晚好 - 2 ชุด]"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(zh_evening_posts, start=1):
        lines.append(f"\n--- 🌅 🇨🇳 เย็น ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(
            f"🖼️ ข้อความบนท้องฟ้า: {item['text_line_1_zh']} / {item['text_line_2_zh']} / {item['text_line_3_zh']}"
        )
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_zh']}")
        lines.append(f"🇹🇭 คำแปลไทย: {item['translation_th']}")
        lines.append(
            f"🎨 Image Prompt (แสงเย็น):\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    # ส่วนที่ 4: ไทยตอนเย็น
    lines.append(
        "\n\n🌅 🇹🇭 [ส่วนที่ 4: กลุ่มไทย สวัสดีตอนเย็น - 2 ชุด]"
    )
    lines.append("=" * 65)

    for idx, item in enumerate(th_evening_posts, start=1):
        lines.append(f"\n--- 🌅 🇹🇭 เย็น ชุดที่ {idx} ({item['flower_name_th']}) ---")
        lines.append(
            f"✍️ ข้อความแนะนำสำหรับนำไปพิมพ์แปะบนรูปเอง:\n{item['text_for_manual_overlay_th']}"
        )
        lines.append(f"📝 แคปชั่นโพสต์:\n{item['caption_th']}")
        lines.append(
            f"🎨 Image Prompt (แสงเย็น เว้นที่ด้านบนไว้ใส่ข้อความ):\n{item['image_prompt_en']}"
        )
        lines.append("-" * 50)

    output_text = "\n".join(lines)

    with open("today_post.txt", "w", encoding="utf-8") as f:
        f.write(output_text)

    print("\n✅ บันทึกคอนเทนต์ครบทั้ง เช้า (10 ชุด) + เย็น (4 ชุด) ลงไฟล์ today_post.txt สำเร็จเรียบร้อย!")
