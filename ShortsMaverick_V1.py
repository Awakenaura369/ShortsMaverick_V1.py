import streamlit as st
import asyncio
import random
from playwright.async_api import async_playwright
from groq import Groq

# --- إعدادات الصفحة ---
st.set_page_config(page_title="YouTube Shorts Maverick", page_icon="📺", layout="wide")

# --- جلب الـ API من Secrets ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ مالقيتش GROQ_API_KEY فـ Streamlit Secrets!")
    st.stop()

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --- عقل الوحش (الذكاء الاصطناعي) ---
def generate_viral_comment(video_title):
    prompt = f"""
    Video Title: "{video_title}"
    Platform: YouTube Shorts
    Language: Moroccan Darija (Arabic script)
    Task: Write a viral, curiosity-driven comment. 
    Style: Mysterious, "missing info" style.
    Goal: Make people visit my channel bio for a link.
    Example: 'هادشي لي وقع فهاد الفيديو صدمة! كملتو ف الرابط لي عندي ف لبروفايل ديالي، دخلوا شوفوا قبل ما يتمسح'
    Constraint: Max 12 words. No hashtags.
    """
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )
        return completion.choices[0].message.content
    except Exception:
        return "والله هادشي خطير! التكملة والحقيقة كاملة حطيتها ف الرابط لي عندي ف لبروفايل 😱"

# --- محرك الأتمتة (قناص يوتيوب) ---
async def start_yt_sniper(target_count, wait_time):
    async with async_playwright() as p:
        # تشغيل المتصفح (خلوه باين لمراقبة العملية)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        st.info("🚀 جاري فتح يوتيوب شورتس...")
        await page.goto("https://www.youtube.com/shorts", wait_until="networkidle")
        
        st.warning("⚠️ عندك 30 ثانية باش تسجل الدخول (Login) يدوياً!")
        await asyncio.sleep(30)

        for i in range(target_count):
            try:
                # 1. جلب عنوان الفيديو
                video_title = await page.title()
                video_title = video_title.replace(" - YouTube", "")
                st.write(f"🧐 فيديو {i+1}: {video_title}")

                # 2. توليد التعليق
                ai_comment = generate_viral_comment(video_title)
                
                # 3. فتح خانة التعليقات
                await page.wait_for_selector("#comments-button", timeout=10000)
                await page.click("#comments-button")
                await asyncio.sleep(2)

                # 4. كتابة ونشر التعليق
                # يوتيوب كيستخدم div قابلة للتعديل
                comment_input = page.locator("#placeholder-area")
                await comment_input.click()
                await page.keyboard.type(ai_comment, delay=100) # كتابة كأنها بشرية
                await asyncio.sleep(1)
                await page.keyboard.press("Control+Enter")
                
                st.success(f"✅ تم النشر: {ai_comment}")

                # 5. غلق نافذة التعليقات (اختياري) وسكرول للفيديو التالي
                await page.keyboard.press("Escape")
                await asyncio.sleep(1)
                await page.keyboard.press("ArrowDown")
                
                # انتظار عشوائي لتجنب الحظر
                jitter = random.randint(wait_time, wait_time + 15)
                st.write(f"😴 انتظار {jitter} ثانية...")
                await asyncio.sleep(jitter)

            except Exception as e:
                st.error(f"❌ مشكل فالفيديو {i+1}: {str(e)}")
                await page.keyboard.press("ArrowDown")
                await asyncio.sleep(5)

        await browser.close()

# --- واجهة التحكم Streamlit ---
st.title("🏴‍☠️ YouTube Shorts Sniper V1")
st.markdown("### وحش جلب الكليكات أوتوماتيكياً عبر Groq AI")

col1, col2 = st.columns(2)
with col1:
    count = st.number_input("عدد الفيديوهات", 1, 500, 20)
with col2:
    delay = st.slider("الانتظار (ثانية)", 10, 120, 30)

if st.button("إطلاق الوحش 🔥"):
    asyncio.run(start_yt_sniper(count, delay))
