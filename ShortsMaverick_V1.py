import streamlit as st
import asyncio
import random
import os
import subprocess
from playwright.async_api import async_playwright
from groq import Groq

# --- إعدادات السيرفر (Playwright Cloud Fix) ---
def install_playwright():
    try:
        # تأكد من تنصيب محرك المتصفح في السحاب
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except:
        pass

install_playwright()

# --- الإعدادات الأساسية ---
st.set_page_config(page_title="Maverick Multi-Sniper V1", page_icon="🏴‍☠️", layout="wide")

# التأكد من وجود مفتاح Groq
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ_API_KEY مفقود في Streamlit Secrets!")
    st.stop()

USER_DATA_DIR = "./user_data"
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- واجهة المستخدم (Tabs) ---
tab1, tab2 = st.tabs(["📺 YouTube Sniper", "🎯 Facebook Sniper"])

# --- TAB 1: YOUTUBE SNIPER ---
with tab1:
    st.header("YouTube Shorts Automation")
    yt_count = st.number_input("عدد الفيديوهات المستهدفة", 1, 1000, 30)
    yt_delay = st.slider("الانتظار بين التعليقات (ثانية)", 10, 120, 40)

    async def start_yt_beast(target_count, wait_time):
        async with async_playwright() as p:
            # headless=True للعمل على السحاب
            context = await p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = context.pages[0]
            st.info("🚀 جاري الدخول إلى YouTube Shorts...")
            await page.goto("https://www.youtube.com/shorts")
            await asyncio.sleep(5) # انتظار بسيط لتحميل الصفحة

            for i in range(target_count):
                try:
                    video_title = await page.title()
                    st.write(f"🧐 قنص الفيديو {i+1}: **{video_title}**")

                    # توليد تعليق ذكي بالدارجة باستخدام Groq
                    prompt = f"Video Title: '{video_title}'. Write a viral Moroccan Darija comment (Arabic script). Make it mysterious to drive profile clicks. Max 12 words."
                    completion = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": prompt}])
                    ai_comment = completion.choices[0].message.content

                    # فتح التعليقات ونشر التعليق
                    await page.wait_for_selector("#comments-button", timeout=10000)
                    await page.click("#comments-button")
                    await asyncio.sleep(2)
                    
                    await page.locator("#placeholder-area").click()
                    await page.keyboard.type(ai_comment, delay=random.randint(50, 150))
                    await page.keyboard.press("Control+Enter")
                    
                    st.success(f"✅ تم النشر: {ai_comment}")

                    # الانتقال للفيديو التالي
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(1)
                    await page.keyboard.press("ArrowDown")
                    
                    jitter = random.randint(wait_time, wait_time + 15)
                    st.write(f"😴 انتظار {jitter} ثانية...")
                    await asyncio.sleep(jitter)

                except Exception as e:
                    st.warning(f"⚠️ مشكل بسيط، جاري التخطي: {str(e)}")
                    await page.keyboard.press("ArrowDown")
                    await asyncio.sleep(5)
            await context.close()

    if st.button("LAUNCH YOUTUBE BEAST 🔥"):
        asyncio.run(start_yt_beast(yt_count, yt_delay))

# --- TAB 2: FACEBOOK SNIPER ---
with tab2:
    st.header("Facebook Sniper 🎯")
    st.subheader("Social Media Hook Generator") #
    
    topic = st.text_area("علاش غايهضر البوست ديالك؟")
    
    col1, col2 = st.columns(2)
    hook_text = ""
    
    with col1:
        if st.button("Generate FB Hook 🚀"):
            fb_prompt = f"Generate 3 viral Moroccan Darija hooks for a Facebook post about: {topic}. Target curiosity and controversy."
            res = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": fb_prompt}])
            st.session_state['fb_hook'] = res.choices[0].message.content

    if 'fb_hook' in st.session_state:
        st.info(st.session_state['fb_hook'])
        final_post = st.text_area("عدل البوست النهائي هنا:", value=st.session_state['fb_hook'], height=150)
        
        if st.button("نشر أوتوماتيكي على فيسبوك 🔥"):
            async def auto_post_fb(content):
                async with async_playwright() as p:
                    context = await p.chromium.launch_persistent_context(USER_DATA_DIR, headless=True)
                    page = context.pages[0]
                    try:
                        await page.goto("https://www.facebook.com/")
                        st.write("🔄 جاري محاولة النشر...")
                        # ملاحظة:Selectors فيسبوك تتغير، هذا الكود يعتمد على وجود الـ Session
                        await page.click('text="What\'s on your mind?"')
                        await asyncio.sleep(2)
                        await page.keyboard.type(content, delay=100)
                        await page.keyboard.press("Control+Enter")
                        st.success("✅ تم النشر بنجاح!")
                    except Exception as e:
                        st.error(f"❌ خطأ: تأكد من أنك مسجل الدخول في ملف user_data")
                    await context.close()
            
            asyncio.run(auto_post_fb(final_post))
