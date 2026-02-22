import os
import random
from highrise import BaseBot, User, Position, SessionMetadata
from flask import Flask
from threading import Thread

# --- سيرفر لضمان العمل 24 ساعة ---
app = Flask('')
@app.route('/')
def home(): return "Bot Leveling System Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات المالك والبيانات ---
OWNER_USER = "___7k"
VIP_USERS = [] 
user_stats = {} # لتخزين الرسائل واللفلات {username: {'messages': 0, 'level': 1}}

ALL_EMOTES = ["emote-tired", "emoji-celebrate", "dance-sexy", "dance-blackpink", "emote-model", "dance-tiktok8", "dance-papakapa", "emote-hello"]

class MyBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("Bot Started with Leveling System")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()
        username = user.username.lower()

        # --- نظام اللفلات ---
        if username not in user_stats:
            user_stats[username] = {'messages': 0, 'level': 1}
        
        user_stats[username]['messages'] += 1
        
        # كل 20 رسالة يزيد لفل
        new_level = (user_stats[username]['messages'] // 20) + 1
        if new_level > user_stats[username]['level']:
            user_stats[username]['level'] = new_level
            await self.highrise.chat(f"مبروك يا @{username}! ارتفع مستواك إلى {new_level} 🆙")
            
            # لو وصل لفل 100 ياخذ VIP تلقائي
            if new_level == 100 and username not in VIP_USERS:
                VIP_USERS.append(username)
                await self.highrise.chat(f"🎉 تهانينا! وصلت لفل 100 وتم منحك صلاحية VIP تلقائياً!")

        # --- أمر !me (عرض مستواك ورسائلك) ---
        if msg == "!me":
            stats = user_stats[username]
            await self.highrise.chat(f"👤 الـمـسـتـخدم: {user.username}\n📊 الـلـفـل: {stats['level']}\n✉️ الـرسـائـل: {stats['messages']}\n⭐ الحالة: {'VIP' if username in VIP_USERS or username == OWNER_USER else 'عضو'}")

        # --- أمر !list (أفضل 20 في الروم) ---
        elif msg == "!list":
            sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['messages'], reverse=True)[:20]
            leaderboard = "🏆 قـائـمـة الـمـتـصـدرين (TOP 20):\n"
            for i, (name, data) in enumerate(sorted_users, 1):
                leaderboard += f"{i}. {name} - LVL: {data['level']} ({data['messages']} msg)\n"
            await self.highrise.chat(leaderboard)

        # --- الأوامر السابقة (بدون تغيير) ---
        elif msg.startswith("هات ") and (username == OWNER_USER or username in VIP_USERS):
            target = msg.split("@")[-1].strip()
            await self.highrise.chat(f"جاري جلب @{target}...")

        elif msg == "stop":
            await self.highrise.chat(f"تم الإيقاف لـ {user.username}")

        elif msg == "فوق":
            await self.highrise.teleport(user.user_id, Position(15, 10, 15))
        
        elif msg == "نزلني":
            await self.highrise.teleport(user.user_id, Position(15, 0, 15))

        elif msg == "vip":
            if username == OWNER_USER or username in VIP_USERS:
                await self.highrise.teleport(user.user_id, Position(5, 5, 5))
            else:
                await self.highrise.chat("عذراً، هذا الأمر للـ VIP فقط ❌")

        elif msg.startswith("اضف vip ") and username == OWNER_USER:
            new_vip = msg.split("@")[-1].strip().lower()
            if new_vip not in VIP_USERS:
                VIP_USERS.append(new_vip)
                await self.highrise.chat(f"تم إضافة @{new_vip} للـ VIP بواسطة المالك ✅")

    async def on_user_join(self, user: User, position: Position) -> None:
        # رقصة عشوائية عند الدخول
        random_emote = random.choice(ALL_EMOTES)
        await self.highrise.send_emote(random_emote, user.user_id)
        await self.highrise.chat(f"يا هلا {user.username}! نورت الروم ✨\nاكتب !me لمعرفة مستواك.")

keep_alive()

if __name__ == "__main__":
    from highrise.__main__ import main
    main()
