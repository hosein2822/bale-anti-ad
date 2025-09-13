from bale import Bot, Message, CallbackQuery  
from bale import InlineKeyboardMarkup, InlineKeyboardButton, MenuKeyboardMarkup, MenuKeyboardButton  
from gradio_client import Client  
import csv  
import json  
import os  
import time
  
# ====== تنظیمات اولیه ======  
TOKEN = "504972366:kVoUjPjPUrnv2U1LVfn4DDJ1FdZUVnpxEVpeY8u9"  

client = Bot(token=TOKEN)  

client2 = Client("Hosein28/no-ads-api")  
botid = '504972366'  
  
# فایل‌های ذخیره‌سازی  

STATS_FILE = "stats.json"
DATA_CSV = "dataads.csv"  
GROUP_SETTINGS_FILE = "group_settings.json"  
WARNS_FILE = "warns.json"  
DELETED_CACHE_FILE = "deleted_cache.json"


# ساخت فایل‌ها در صورت نبودن  
if not os.path.exists(DELETED_CACHE_FILE):
    with open(DELETED_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
if not os.path.exists(DATA_CSV):  
    with open(DATA_CSV, mode="w", newline="", encoding="utf-8") as f:  
        writer = csv.writer(f)  
        writer.writerow(["text", "label"])  
if not os.path.exists(GROUP_SETTINGS_FILE):  
    with open(GROUP_SETTINGS_FILE, "w", encoding="utf-8") as f:  
        json.dump({}, f, ensure_ascii=False, indent=2)  
if not os.path.exists(WARNS_FILE):  
    with open(WARNS_FILE, "w", encoding="utf-8") as f:  
        json.dump({}, f, ensure_ascii=False, indent=2)  
if not os.path.exists(DELETED_CACHE_FILE):  
    with open(DELETED_CACHE_FILE, "w", encoding="utf-8") as f:  
        json.dump({}, f, ensure_ascii=False, indent=2)
  
# دیتاست موقتی برای تست دکمه‌ها  
saved_messages = {}  
  
# ====== توابع کمکی برای تنظیمات و اخطارها ======  
def load_deleted_cache():
    try:
        with open(DELETED_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_deleted_cache(cache):
    try:
        with open(DELETED_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("save_deleted_cache error:", e)

def add_deleted_entry(group_id, user_id, text,username):
    cache = load_deleted_cache()
    key = f"{group_id}:{user_id}:{int(time.time())}"
    cache[key] = {"text": text, "group_id": str(group_id), "user_id": str(user_id),"username":str(username)}
    save_deleted_cache(cache)
    return key

def pop_deleted_entry(key):
    cache = load_deleted_cache()
    entry = cache.pop(key, None)
    save_deleted_cache(cache)
    return entry

def load_stats(default=None):
    if default is None:
        default = {}
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_stats(data):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("save_stats error:", e)

def ensure_group_stats(group_id):
    stats = load_stats({})
    gid = str(group_id)
    if gid not in stats:
        stats[gid] = {
            "deleted_ads": 0,
            "deleted_forward": 0,
            "deleted_link": 0,
            "deleted_id": 0,
            "total_deleted": 0,
            "kicked": 0
        }
        save_stats(stats)
    return stats

def inc_stat(group_id, key, n=1):
    stats = load_stats({})
    gid = str(group_id)
    if gid not in stats:
        ensure_group_stats(gid)
        stats = load_stats({})
    stats[gid].setdefault(key, 0)
    stats[gid][key] = int(stats[gid].get(key, 0)) + int(n)
    # update total_deleted if a deletion-type key incremented
    if key in ("deleted_ads", "deleted_forward", "deleted_link", "deleted_id"):
        stats[gid].setdefault("total_deleted", 0)
        stats[gid]["total_deleted"] = int(stats[gid].get("total_deleted", 0)) + int(n)
    save_stats(stats)

def get_stats(group_id):
    stats = load_stats({})
    return stats.get(str(group_id), {
        "deleted_ads": 0,
        "deleted_forward": 0,
        "deleted_link": 0,
        "deleted_id": 0,
        "total_deleted": 0,
        "kicked": 0
    })

def load_json(path, default):  
    try:  
        with open(path, "r", encoding="utf-8") as f:  
            return json.load(f)  
    except Exception:  
        return default  
  
def save_json(path, data):  
    try:  
        with open(path, "w", encoding="utf-8") as f:  
            json.dump(data, f, ensure_ascii=False, indent=2)  
    except Exception as e:  
        print("save_json error:", e)  
  
def get_group_settings(group_id):  
    cfg = load_json(GROUP_SETTINGS_FILE, {})  
    return cfg.get(str(group_id), {  
        "no_ads": True,  
        "no_link": False,  
        "no_id": False,  
        "no_forward": False,  
        "warns_enabled": True,  
        "max_warns": 3  
    })  
  
def set_group_setting(group_id, key, value):  
    cfg = load_json(GROUP_SETTINGS_FILE, {})  
    cfg.setdefault(str(group_id), {  
        "no_ads": True,  
        "no_link": False,  
        "no_id": False,  
        "no_forward": False,  
        "warns_enabled": True,  
        "max_warns": 3  
    })  
    cfg[str(group_id)][key] = value  
    save_json(GROUP_SETTINGS_FILE, cfg)  
  
def add_warn(group_id, user_id):  
    warns = load_json(WARNS_FILE, {})  
    warns.setdefault(str(group_id), {})  
    warns[str(group_id)].setdefault(str(user_id), 0)  
    warns[str(group_id)][str(user_id)] += 1  
    save_json(WARNS_FILE, warns)  
    return warns[str(group_id)][str(user_id)]  
  
def reset_warns(group_id, user_id):  
    warns = load_json(WARNS_FILE, {})  
    if str(group_id) in warns and str(user_id) in warns[str(group_id)]:  
        warns[str(group_id)][str(user_id)] = 0  
        save_json(WARNS_FILE, warns)  
  
def get_warns(group_id, user_id):  
    warns = load_json(WARNS_FILE, {})  
    return int(warns.get(str(group_id), {}).get(str(user_id), 0))  

def remove_warn(group_id, user_id):
    warns = load_json(WARNS_FILE, {})
    if str(group_id) in warns and str(user_id) in warns[str(group_id)]:
        warns[str(group_id)][str(user_id)] = max(0, warns[str(group_id)][str(user_id)] - 1)
        save_json(WARNS_FILE, warns)
        return warns[str(group_id)][str(user_id)]
    return 0


# ====== تابع تشخیص (تو از client2.predict استفاده کردی) ======  
def is_ads(msg):  
    try:  
        result = client2.predict(  
            text=msg,  
            api_name="/predict"  
        )  
        # انتظار داریم result شامل 'label' باشه مانند کد اولیه شما  
        return str(result.get('label', "0"))  
    except Exception as e:  
        print("is_ads predict error:", e)  
        return "0"  
    
def is_link(pm):
    domains = ['.ir','.net','.com','.org','.ai','.me','.ru','.run','.app','.info','.blog']
    for domain in domains :
        if domain in str(pm):
            return True
            break
        else :
            return False

  
# ====== کمکی برای گرفتن لیست admin ids ======  
async def get_admin_ids(chat_id):  
    
    admins = await client.get_chat_administrators(chat_id)  
      
    return str(admins)
  
# ====== رویدادها ======  
@client.event  
async def on_ready():  
    print(f"ربات {client.user.username} روشن شد ✅")  
  
@client.event  
async def on_message(message: Message):  
    
    try:  
        # ignore bot's own messages  
        try:  
            myid = str(getattr(client.user, "id", None))  
            sender_id = str(getattr(message.author, "id", getattr(message, "from_user", None)))  
            if myid and sender_id and myid == sender_id:  
                return  
        except:  
            pass  
  
        # فقط گروه‌ها را اینجا پردازش می‌کنیم برای بخش admin  
        if message.chat.is_group_chat:  
            # لیست ادمین ها  
            admin_ids = await get_admin_ids(message.chat_id)  
  
            # اگر دستور start فرستاده شده  
            if message.content in ["/start"]:  
                # چک کن ربات ادمین گروه باشه تا بتونه پیام‌ها رو حذف کنه  
                if botid in admin_ids:  
                    await message.reply('سلام! من ربات ضد تبلیغ هستم . دیگه لازم نیست وقتتو صرف پاک کردن تبلیغ ها بکنی چون من اینجام . قابلیت ها : حذف تبلیغات باستفاده از هوش مصنوعی , ثبت اخطار , قابلیت تنظیم اخطار دستی , برای ادمین ها , قابلیت تنظیم تعداد اخطار ها و یا غیر فعالسازی اخطار . برای مشاهده دستورات /help رو ارسال کن ')  
                else:  
                    await message.reply("سلام! جهت استفاده از ربات ضد تبلیغ ربات را با دسترسی مشاهد اعضا و حذف اعضا و حذف و ارسال پیام مدیر گروه کنید")  
                return  
  
            # کمک: دستور help برای ادمین‌ها در گروه  
            if message.content == "/help":  
                 
                  
                await message.reply(  
                    '📜👤دستورات (ویژه ادمین ها):\n\n'  
                    'فعالسازی حذف تبلیغ : /OnNoAds\n'  
                    'غیر فعالسازی حذف تبلیغات : /OffNoAds\n'  
                    'فعالسازی حذف لینک : /OnNoLink\n'  
                    'غیر فعالسازی حذف لینک : /OffNoLink\n'  
                    'فعالسازی حذف آیدی : /OnNoID\n'  
                    'غیر فعالسازی حذف آیدی : /OffNoID\n'  
                    'فعالسازی حذف  فوروارد : /OnNoFor\n'  
                    'غیر فعالسازی حذف فوروارد: /OffNoFor\n\n'  
                    '⚠️👤دستورات مربوط به اخطار :\n\n'  
                    'فعالسازی اخطار خودکار : /OnWarn\n'  
                    'غیر فعالسازی اخطار خودکار : /OffWarn\n'  
                    'تنظیم تعداد اخطار مجاز : /SetWarn X  (مثال: /SetWarn 3)\n'  
                    'اخطار دادن دستی به کاربر (ریپلای روی پیام): /Warn\n\n'  
                    'اگر پیام تبلیغی فرستاد اما حذف نشد، روی پیام ریپلای کن و /ad را بزن.\n\n'  
                    '📜👥دستورات عمومی :\n'
                    'اطلاعات و آمار گروه : /info\n'
                    'اطلاعات مشاهده تعداد اخطار ها : /MyWarns\n\n'
                    '(بقیه دستورات و قابلیت ها به مرور اضافه خواهد شد...)'
                )  
                return  
  
            if message.content == "/MyWarns":
                try:
                    uid = getattr(message.author, "id", getattr(message.author, "user_id", None))
                    n = get_warns(message.chat_id, uid)
                    await message.reply(f"⚠️ شما {n} اخطار دارید در این گروه.")
                except Exception as e:
                    print("MyWarns error:", e)
                    await message.reply("خطا در خواندن تعداد اخطارها.")
                return
            

            # عمومی: هر کاربری در گروه می‌تواند /info را بزند
            if message.content == "/info":
                try:
                    gid = message.chat_id
                    # آیدی عددی گروه
                    gid_str = str(gid)
                    # لینک گروه (اگر موجود باشد)
                    invite = getattr(message.chat, "invite_link", None) or "ندارد یا خصوصی"
                    # آمار از فایل
                    s = get_stats(gid)
                    # تعداد اخراج شده و حذف‌های تفکیکی
                    kicked = s.get("kicked", 0)
                    deleted_ads = s.get("deleted_ads", 0)
                    deleted_forward = s.get("deleted_forward", 0)
                    deleted_link = s.get("deleted_link", 0)
                    deleted_id = s.get("deleted_id", 0)
                    total_deleted = s.get("total_deleted", 0)
                    # ساخت پیام پاسخ
                    info_text = (
                        f"ℹ️ اطلاعات گروه:\n"
                        f"- آیدی گروه: `{gid_str}`\n"
                        f"- لینک گروه: {invite}\n\n"
                        f"📊 آمار حذف‌ها توسط ربات:\n"
                        f"- مجموع حذف‌ها: {total_deleted}\n"
                        f"- تبلیغی: {deleted_ads}\n"
                        f"- فوروارد: {deleted_forward}\n"
                        f"- لینک: {deleted_link}\n"
                        f"- آیدی: {deleted_id}\n\n"
                        f"👢 تعداد کاربرانی که توسط ربات اخراج شدند: {kicked}\n"
                    )
                    await message.reply(info_text)
                except Exception as e:
                    print("info command error:", e)
                    await message.reply("خطا در دریافت اطلاعات گروه.")
                return


            # دستورهای مدیریتی (همگی فقط برای ادمین‌ها)  
            # ابتدا چک کن فرستنده ادمین هست  
            if str(message.author.id) not in admin_ids:  
                # اگر پیام از ادمین نبود، به سراغ تشخیص عادی پیام (ربات حذف خودکار) برو  
                # توجه: اگر می‌خواهی ربات فقط بر پیام‌های غیرادمین نظارت کند، اینجا کارش انجام می‌شود  
                # ابتدا تنظیمات گروه رو بگیر  
                settings = get_group_settings(message.chat_id)  
                text = getattr(message, "content", "") or ""  
                if not text:  
                    return  
  
                # اگر حذف تبلیغ فعال باشد و مدل تشخیص دهد  
                try:  
                    if settings.get("no_ads", True) and '1' in is_ads(text):  
                        deleted_text = text
                        deleted_key = add_deleted_entry(message.chat_id, message.author.id, deleted_text,message.author.username)
                        kb = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(text="تبلیغ نبود ❌", callback_data=f"undo_ad:{deleted_key}")
    )

                        # حذف پیام  
                        try:  
                            await message.delete()  
                        except Exception as e:  
                            print("delete error:", e)  
                        else:
                            inc_stat(message.chat_id,"deleted_ads",1)
                        # ثبت اخطار در صورت فعال بودن اخطارها  
                        if settings.get("warns_enabled", True):  
                            new = add_warn(message.chat_id, message.author.id)  
                            maxw = settings.get("max_warns", 3)  
                            try:  
                                await client.send_message(message.chat_id,  
                                    f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) عزیز!\nپیام تبلیغی حذف شد. شما اخطار {new} اخطار /{maxw}  گرفتید.  ''\n( در صورتی که پیام این کاربر تبلیغی نبود یک از ادمین ها روی دکمه زیر ضربه بزند )'
                                ,components=kb)  
                            except Exception:  
                                pass  
                            if new >= maxw:  
                                # اخراج کاربر  
                                try:  
                                    await message.chat.ban_chat_member(message.author.id)  
                                except Exception:  
                                    try:  
                                        await client.ban_chat_member(message.chat_id, message.author.id)  
                                    except Exception as e:  
                                        print("kick error:", e)  
                                    else:
                                        inc_stat(message.chat_id, "kicked",1)
                                else:
                                    inc_stat(message.chat_id, "kicked",1)
                                # ریست اخطارها  
                                reset_warns(message.chat_id, message.author.id)  
                        else:  
                            # اگر اخطار غیر فعال است، فقط پیام حذف شود  
                            try:  
                                await client.send_message(message.chat_id,  
                                    f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) : فرستنده \nپیام تبلیغی حذف شد.'  
                                ,components=kb)  
                            except:  
                                pass  
                        return  
                    

                 


                    elif settings.get('no_forward', True) and message.forward_from_chat != None:
                        # حذف پیام  
                                try:  
                                    await message.delete()  
                                except Exception as e:  
                                    print("delete error:", e)
                                else:
                                    inc_stat(message.chat_id,"deleted_forward",1)
                                      
                                # ثبت اخطار در صورت فعال بودن اخطارها  
                                if settings.get("warns_enabled", True):  
                                    new = add_warn(message.chat_id, message.author.id)  
                                    maxw = settings.get("max_warns", 3)  
                                    try:  
                                        await client.send_message(message.chat_id,  
                                            f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) عزیز!\nپیام فوروارد حذف شد. شما اخطار {new} اخطار / {maxw} گرفتید.'  
                                        ,delete_after=10)  
                                    except Exception:  
                                        pass
                                    if new >= maxw:  
                                # اخراج کاربر  
                                        try:  
                                            await message.chat.ban_chat_member(message.author.id)  
                                        except Exception:  
                                            try:  
                                                await client.ban_chat_member(message.chat_id, message.author.id)  
                                            except Exception as e:  
                                                print("kick error:", e)  
                                            else:
                                                inc_stat(message.chat_id, "kicked",1)
                                        else:
                                            inc_stat(message.chat_id, "kicked",1)
                                        # ریست اخطارها  
                                        reset_warns(message.chat_id, message.author.id)
                                else:  
                                    # اگر اخطار غیر فعال است، فقط پیام حذف شود  
                                    try:  
                                        await client.send_message(message.chat_id,  
                                            f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) : فرستنده  \n پیام فوروارد حذف شد.'  
                                        ,delete_after=10)  
                                    except:  
                                        pass  
                                return               

                    elif settings.get('no_link',True) and is_link(message.content):
                        # حذف پیام  
                                try:  
                                    await message.delete()  
                                except Exception as e:  
                                    print("delete error:", e) 
                                else:
                                    inc_stat(message.chat_id,"deleted_link",1) 
                                
                                # ثبت اخطار در صورت فعال بودن اخطارها  
                                if settings.get("warns_enabled", True):  
                                    new = add_warn(message.chat_id, message.author.id)  
                                    maxw = settings.get("max_warns", 3)  
                                    try:  
                                        await client.send_message(message.chat_id,  
                                            f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) عزیز!\nپیام حاوی حذف شد. شما اخطار {new} اخطار / {maxw} گرفتید.'  
                                        ,delete_after=10)  
                                    except Exception:  
                                        pass
                                    if new >= maxw:  
                                # اخراج کاربر  
                                        try:  
                                            await message.chat.ban_chat_member(message.author.id)  
                                        except Exception:  
                                            try:  
                                                await client.ban_chat_member(message.chat_id, message.author.id)  
                                            except Exception as e:  
                                                print("kick error:", e)  
                                            else:
                                                inc_stat(message.chat_id, "kicked",1)
                                        else:
                                            inc_stat(message.chat_id, "kicked",1)
                                        # ریست اخطارها  
                                        reset_warns(message.chat_id, message.author.id)
                                else:  
                                    # اگر اخطار غیر فعال است، فقط پیام حذف شود  
                                    try:  
                                        await client.send_message(message.chat_id,  
                                            f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) : فرستنده  \n پیام حاوی لینک حذف شد.'  
                                        ,delete_after=10)  
                                    except:  
                                        pass  
                                return               

                    
                    elif settings.get('no_id',True)and '@' in message.content:
                        # حذف پیام  
                                try:  
                                    await message.delete()  
                                except Exception as e:  
                                    print("delete error:", e)  
                                else:
                                    inc_stat(message.chat_id,"deleted_id",1)
                                # ثبت اخطار در صورت فعال بودن اخطارها  
                                if settings.get("warns_enabled", True):  
                                    new = add_warn(message.chat_id, message.author.id)  
                                    maxw = settings.get("max_warns", 3)  
                                    try:  
                                        await client.send_message(message.chat_id,  
                                            f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) عزیز!\nپیام حاوی آیدی  حذف شد. شما اخطار {new} اخطار / {maxw} گرفتید.'  
                                        ,delete_after=10)  
                                    except Exception:  
                                        pass
                                    if new >= maxw:  
                                # اخراج کاربر  
                                        try:  
                                            await message.chat.ban_chat_member(message.author.id)  
                                        except Exception:  
                                            try:  
                                                await client.ban_chat_member(message.chat_id, message.author.id)  
                                            except Exception as e:  
                                                print("kick error:", e)  
                                            else:
                                                inc_stat(message.chat_id, "kicked",1)
                                        else:
                                            inc_stat(message.chat_id, "kicked",1)
                                        # ریست اخطارها  
                                        reset_warns(message.chat_id, message.author.id)
                                else:  
                                    # اگر اخطار غیر فعال است، فقط پیام حذف شود  
                                    try:  
                                        await client.send_message(message.chat_id,  
                                            f'[{message.author.first_name}](ble.ir/{getattr(message.author, "username", "")}) : فرستنده  \n پیام حاوی آیدی حذف شد.'  
                                        ,delete_after=10)  
                                    except:  
                                        pass  
                                return               

                except Exception as e:  
                    print("is_ads check error:", e)  
                return  # غیر ادمین‌ها پردازش کامل شد؛ ادمین‌ها در بخش بعدی بررسی می‌شوند     
                
        



            # اگر فرستنده ادمین است، پردازش دستورات مدیریتی زیر را انجام بده:  
            # فعال/غیرفعال کردن قوانین  
            cmd = message.content.strip().split()  
            cmd0 = cmd[0] if len(cmd)>0 else ""  
            # On/Off toggles  
            if cmd0 == "/OnNoAds":  
                set_group_setting(message.chat_id, "no_ads", True)  
                await message.reply("✅ حذف تبلیغ فعال شد.")  
                return  
            if cmd0 == "/OffNoAds":  
                set_group_setting(message.chat_id, "no_ads", False)  
                await message.reply("✅ حذف تبلیغ غیرفعال شد.")  
                return  
            if cmd0 == "/OnNoLink":  
                set_group_setting(message.chat_id, "no_link", True)  
                await message.reply("✅ حذف لینک فعال شد.")  
                return  
            if cmd0 == "/OffNoLink":  
                set_group_setting(message.chat_id, "no_link", False)  
                await message.reply("✅ حذف لینک غیرفعال شد.")  
                return  
            if cmd0 == "/OnNoID":  
                set_group_setting(message.chat_id, "no_id", True)  
                await message.reply("✅ حذف آیدی فعال شد.")  
                return  
            if cmd0 == "/OffNoID":  
                set_group_setting(message.chat_id, "no_id", False)  
                await message.reply("✅ حذف آیدی غیرفعال شد.")  
                return  
            if cmd0 == "/OnNoFor":  
                set_group_setting(message.chat_id, "no_forward", True)  
                await message.reply("✅ حذف فوروارد فعال شد.")  
                return  
            if cmd0 == "/OffNoFor":  
                set_group_setting(message.chat_id, "no_forward", False)  
                await message.reply("✅ حذف فوروارد غیرفعال شد.")  
                return  
  
            # Warn toggles  
            if cmd0 == "/OnWarn":  
                set_group_setting(message.chat_id, "warns_enabled", True)  
                await message.reply("✅ اخطار خودکار فعال شد.")  
                return  
            if cmd0 == "/OffWarn":  
                set_group_setting(message.chat_id, "warns_enabled", False)  
                await message.reply("✅ اخطار خودکار غیرفعال شد.")  
                return  
  
            # SetWarn X  
            if cmd0 == "/SetWarn":  
                if len(cmd) >= 2:  
                    try:  
                        n = int(cmd[1])  
                        set_group_setting(message.chat_id, "max_warns", n)  
                        await message.reply(f"✅ حد اخطار روی {n} تنظیم شد.")  
                    except:  
                        await message.reply("⚠️ مقدار نامعتبر است. مثال: /SetWarn 3")  
                else:  
                    await message.reply("ℹ️ مثال: /SetWarn 3")  
                return  
  
            # Warn (manual) - by reply  
            if cmd0 == "/Warn":  
                replied = getattr(message, "reply_to_message", None) or getattr(message, "reply_to", None)  
                if not replied:  
                    await message.reply("ℹ️ برای اخطار دستی ریپلای کنید روی پیام کاربر و /Warn را بفرستید.")  
                    return  
                target = getattr(replied, "author", None) or getattr(replied, "from_user", None)  
                if not target:  
                    await message.reply("⚠️ نتوانستم کاربر را شناسایی کنم.")  
                    return  
                tid = getattr(target, "id", getattr(target, "user_id", None))  
                new = add_warn(message.chat_id, tid)  
                maxw = get_group_settings(message.chat_id).get("max_warns", 3)  
                await message.reply(f"⚠️ کاربر <{tid}> اخطار گرفت: {new}/{maxw}")  
                if new >= maxw:  
                    try:  
                        await message.chat.ban_chat_member(tid)  
                        await message.reply(f"❌ کاربر <{tid}> حذف شد (رسید به حد اخطار).")  
                        reset_warns(message.chat_id, tid)  
                    except Exception as e:  
                        await message.reply("خطا در حذف کاربر: " + str(e))  
                return  
  
            # /ad : ریپلای + /ad -> ذخیره پیام تبلیغی دستی و اخطار  
            if cmd0 == "/ad":  
                replied = getattr(message, "reply_to_message", None) or getattr(message, "reply_to", None)  
                if not replied:  
                    await message.reply("ℹ️ برای علامت‌گذاری ریپلای کنید و /ad را بزنید.")  
                    return  
                ttext = getattr(replied, "content", "") or getattr(replied, "text", "")  
                # ذخیره در CSV با label=1  
                try:  
                    with open(DATA_CSV, mode="a", newline="", encoding="utf-8") as file:  
                        writer = csv.writer(file)  
                        writer.writerow([ttext, 1])  
                except Exception as e:  
                    print("csv write error:", e)  
                # اخطار به کاربر  
                target = getattr(replied, "author", None) or getattr(replied, "from_user", None)  
                if target:  
                    tid = getattr(target, "id", getattr(target, "user_id", None))  
                    new = add_warn(message.chat_id, tid)  
                    maxw = get_group_settings(message.chat_id).get("max_warns", 3)  
                    try:  
                        await message.reply(f"💾 پیام به‌عنوان تبلیغ ذخیره شد — کاربر <{tid}> اخطار {new}/{maxw}.")  
                    except:  
                        pass  
                    if new >= maxw:  
                        try:  
                            await message.chat.ban_chat_member(tid)  
                            await message.reply(f"❌ کاربر <{tid}> حذف شد (رسید به حد اخطار).")  
                            reset_warns(message.chat_id, tid)  
                        except Exception as e:  
                            await message.reply("خطا در حذف کاربر: " + str(e))  
                else:  
                    await message.reply("⚠️ نتوانستم کاربر را شناسایی کنم.")  
                return  
  
            # اگر هیچکدام از دستورات مدیریتی نبودند و فرستنده ادمین است،  
            # به اینجا برسد و می‌توان دستورات دیگر را اضافه کرد.  
            return  
  
        # اگر پیام توی چت خصوصی است، همان منو پیوی را اجرا کن  
        else:  
            if message.content == "/start":  
                # دکمه‌های اینلاین  
                inline_kb = InlineKeyboardMarkup()  
                inline_kb.add(InlineKeyboardButton(text="➕ افزودن بازو به گروه ", callback_data="add"),1)  
                inline_kb.add(InlineKeyboardButton(text="🧪 تست تشخیص تبلیغ", callback_data="test"),2)  
  
                # کیبورد منو  
                  
                inline_kb.add(InlineKeyboardButton("📊 آمار گروه",callback_data='i'),3)  
                inline_kb.add(InlineKeyboardButton("⚙️ تنظیمات",callback_data='s'),3)  
                inline_kb.add(InlineKeyboardButton("گزارش خرابی",callback_data='m'),4)
                inline_kb.add(InlineKeyboardButton("پیشنهادات و انتقادات",callback_data='m2'),4)


  
                # پیام خوشامدگویی  
                await message.reply(  
                    f"سلام {message.author.first_name} 👋\n"  
                    "به ربات ضد تبلیغ خوش اومدی! 🚀\n"  
                    "از منوی زیر میتونی امکانات ربات رو ببینی 👇",  
                    components=inline_kb
                )  
                return  
  
            

                


    except Exception as e:  
        print("on_message general error:", e)  
  
# ====== callback handler (همان منطق قبلی تست) ======  
@client.event  
async def on_callback(callback: CallbackQuery):  
    try:  
        print(callback.data)
        if callback.data == "add":  
            await callback.message.edit(  
                "🟢 جهت افزودن بازو به گروه خود مراحل زیر را دنبال کنید : \n"
                " 1⃣ وارد گروه خود شوید\n" 
                " 2⃣ روی اسم گروه خود ضربه بزنید\n"
                " 3⃣روی افزودن عضو ضربه بزنید\n"
                " 4⃣روی علامت 🔍 ضربه بزنید (بالا سمت راست )\n"
                " 5⃣آیدی ربات را بدون @ وارد کنید (AntiAdsBot)\n"
                " ⏺ربات در گروه شما عضو شد\n"
                " 6⃣ربات را در گروه با دسترسی های لازم  ادمین کنید (ترجیحا همه دسترسی هارا فعال کنید تا درصورتی که قابلیت جدید به ربات اضافه شد با مشکل مواجه نشوید )"  
            )  
            return  
        elif callback.data == 'i':  
                await callback.message.edit("جهت مشاهده امار گروه کافی است در گروه مورد نظر دستور /info را ارسال کنید")  
                return  
        

        elif callback.data == 's':  
                await callback.message.edit("جهت تنظیم کردن تنظیمات گروه دستور /help را درون گروه خود ارسال کنید ")  
                return



        elif callback.data == 'm':
                await callback.message.edit('پیغام خود را ارسال کنید :')


                def answer_checker(m: Message):  
                # در پیوی، بررسی می‌کنیم پیام از همان یوزر باشد  
                    return m.author == m.author and bool(m.text)  
  
            # منتظر پیام کاربر  
                answer_obj: Message = await client.wait_for('message', check=answer_checker)

                await client.send_message(1912298798,f'text:{answer_obj.content}\n username :{answer_obj.author}') 
                answer_obj.reply('ممنون از بازخورد شما !')


        elif callback.data == "test":  
            await callback.message.edit("پیام خود را ارسال کنید تا ربات تبلیغی بودن یا نبودن آن را تشخیص دهد:")  
  
            def answer_checker(m: Message):  
                # در پیوی، بررسی می‌کنیم پیام از همان یوزر باشد  
                return m.author == m.author and bool(m.text)  
  
            # منتظر پیام کاربر  
            answer_obj: Message = await client.wait_for('message', check=answer_checker)  
            text = getattr(answer_obj, "content", "") or getattr(answer_obj, "text", "")  
  
            # ذخیره متن پیام با شناسه پیام  
            saved_messages[answer_obj.message_id] = text  
  
            # پیش‌بینی اولیه (ساده)  
            if 'https' in text or '1' in is_ads(text):  
                reply_text = "این پیام تبلیغی است"  
            elif '0' in is_ads(text):  
                reply_text = "این پیام تبلیغی نیست"  
            else:  
                reply_text = "⚠️ ERROR: نمی‌توان تشخیص داد"  
  
            # دکمه‌ها با callback_data شامل label و message_id  
            inline_kb = InlineKeyboardMarkup()  
            inline_kb.add(InlineKeyboardButton(  
                "پیام تبلیغی بود ✅", callback_data=f"1:{answer_obj.message_id}"  
            ))  
            inline_kb.add(InlineKeyboardButton(  
                "پیام تبلیغی نبود ❌", callback_data=f"0:{answer_obj.message_id}"  
            ))  
  
            await answer_obj.reply(reply_text, components=inline_kb)  
            return  
        


        elif callback.data and callback.data.startswith("undo_ad:"):
            try:
                _, deleted_key = callback.data.split(":", 1)
                clicker = getattr(callback, "from_user", None) or getattr(callback, "user", None)
                clicker_id = str(getattr(clicker, "id", getattr(clicker, "user_id", None)))

                # مطمئن شو clicker ادمین گروه است
                chat = getattr(callback.message, "chat", None)
                chat_id = getattr(chat, "id", getattr(chat, "chat_id", None))
                admin_ids = await get_admin_ids(chat_id)
                if clicker_id not in admin_ids:
                    await callback.message.reply("⚠️ فقط ادمین‌ها می‌توانند این عمل را انجام دهند.",delete_after=20)
                    return

                entry = pop_deleted_entry(deleted_key)
                if not entry:
                    await callback.message.reply("⚠️ متن پیام پیدا نشد یا قبلاً پردازش شده است.")
                    return

                orig_text = entry.get("text", "")
                orig_user_id = entry.get("user_id")
                orig_username = entry.get('username')
                # 1) حذف یک اخطار
                new_warn = remove_warn(entry.get("group_id"), orig_user_id,)
                # 2) ذخیره پیام با لیبل 0
                with open(DATA_CSV, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow([orig_text, 0])
                # 3) ارسال مجدد پیام
                await client.send_message(chat_id, f"🔄 پیام بازیابی شد توسط ادمین — ارسال‌کننده: @{orig_username}\n\n{orig_text}")
                # 4) اطلاع کلیک‌کننده
                await callback.message.reply(f"✅ پیام بازبازی شد — اخطار کاهش یافت: جدید = {new_warn}")
            except Exception as e:
                print("undo_ad callback error:", e)
                await callback.message.reply("⚠️ خطا در پردازش بازبینی پیام.")
            return





        elif ":" in callback.data:  
            # استخراج label و msg_id  
            label_str, msg_id_str = callback.data.split(":")  
            try:  
                label = int(label_str)  
            except:  
                label = 0  
            try:  
                msg_id = int(msg_id_str)  
            except:  
                msg_id = None  
  
            # گرفتن متن از دیکشنری  
            textcsv = saved_messages.get(msg_id, "متن پیدا نشد")  
  
            # ذخیره در CSV  
            try:  
                with open(DATA_CSV, mode="a", newline="", encoding="utf-8") as file:  
                    writer = csv.writer(file)  
                    writer.writerow([textcsv, label])  
            except Exception as e:  
                print("csv write error callback:", e)  
  
            await callback.message.edit(f"✅ پیام ذخیره شد: {label}\n ممنون از بازخوزد شما ")  
            return  



        




    except Exception as e:  
        print("on_callback error:", e)  
  
# ====== run ======  
client.run() 
