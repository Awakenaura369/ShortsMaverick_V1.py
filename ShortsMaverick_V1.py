import streamlit as st
import asyncio
import random
import os
from playwright.async_api import async_playwright
from groq import Groq

# --- Configuration ---
st.set_page_config(page_title="Maverick Multi-Sniper", page_icon="🏴‍☠️", layout="wide")

if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ_API_KEY missing in secrets!")
    st.stop()

USER_DATA_DIR = "./user_data"
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Tabs System ---
tab1, tab2 = st.tabs(["📺 YouTube Sniper", "🎯 Facebook Sniper"])

# --- Tab 1: YouTube Sniper ---
with tab1:
    st.header("YouTube Shorts Automation")
    count = st.number_input("Target Videos", 1, 1000, 50, key="yt_count")
    delay = st.slider("Base Delay (Seconds)", 10, 120, 30, key="yt_delay")

    async def start_yt_beast(target_count, wait_time):
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                USER_DATA_DIR, headless=False,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.pages[0]
            await page.goto("https://www.youtube.com/shorts")
            st.warning("⚠️ عندك 20 ثانية للتأكد من تسجيل الدخول...")
            await asyncio.sleep(20)

            for i in range(target_count):
                try:
                    video_title = await page.title()
                    # تحليل العنوان لضمان استهداف المحتوى العربي
                    prompt = f"Video Title: '{video_title}'. Write a viral Moroccan Darija comment for this. Make it mysterious to drive bio clicks."
                    completion = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": prompt}])
                    ai_comment = completion.choices[0].message.content

                    await page.click("#comments-button")
                    await asyncio.sleep(2)
                    await page.locator("#placeholder-area").click()
                    await page.keyboard.type(ai_comment, delay=100)
                    await page.keyboard.press("Control+Enter")
                    st.success(f"✅ Posted: {ai_comment}")

                    await page.keyboard.press("Escape")
                    await asyncio.sleep(1)
                    await page.keyboard.press("ArrowDown")
                    await asyncio.sleep(random.randint(wait_time, wait_time+15))
                except Exception as e:
                    await page.keyboard.press("ArrowDown")
                    await asyncio.sleep(5)
            await context.close()

    if st.button("LAUNCH YOUTUBE BEAST 🔥"):
        asyncio.run(start_yt_beast(count, delay))

# --- Tab 2: Facebook Sniper ---
with tab2:
    st.header("Social Media Hook Generator (Facebook)") #
    st.write("صاوب 'خطاف' (Hook) كيهز بناند بالفضول للفيسبوك.")
    
    fb_topic = st.text_area("علاش غايهضر المنشور ديالك؟")
    if st.button("Generate FB Hook 🚀"):
        hook_prompt = f"You are a viral marketing expert. Generate 3 powerful hooks in Moroccan Darija (Arabic script) for a Facebook post about: {fb_topic}. Focus on controversy and curiosity."
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": hook_prompt}]
        )
        st.subheader("إليك المقترحات:")
        st.write(response.choices[0].message.content)
