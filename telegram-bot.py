from telegram.ext import *
from telegram import KeyboardButton, ReplyKeyboardMarkup
from mss import mss
import tempfile
import os
import psutil
import ctypes
import webbrowser
import pyperclip
import subprocess
import json
import platform


class TelegramBot:

    def __init__(self):
        f = open('auth.json')
        auth = json.load(f)
        self.TOKEN = auth["TOKEN"]
        self.CHAT_ID = auth["CHAT_ID"]


    def start_command(self, update, context):
        buttons = [[KeyboardButton("⚠ Screen status")], [KeyboardButton("🔒 Lock screen")], [KeyboardButton("📸 Take screenshot")],
                   [KeyboardButton("✂️ Paste clipboard")], [KeyboardButton("📚 List process")], [KeyboardButton("💤 Sleep")],
                   [KeyboardButton("*️⃣ More commands")],[KeyboardButton("📂 ls")], [KeyboardButton("🧮 cmd")]]
        computer_name = platform.node().split(".")
        context.bot.MESSAGEENTITY_CODE.send_message(
            chat_id=self.CHAT_ID, text= f"[☢️] BOT live!\n\nYou're now controlling {computer_name[0]}", reply_markup=ReplyKeyboardMarkup(buttons))

# ? return errors
    def error(self, update, context):
        print(f"Update {update} caused error {context.error}")

# ? take screenshot
    def take_screenshot(self):
        TEMPDIR = tempfile.gettempdir()
        os.chdir(TEMPDIR)
        with mss() as sct:
            sct.shot(mon=-1)
        return os.path.join(TEMPDIR, 'monitor-0.png')

# ? message handler
    def handle_message(self, update, input_text):
        usr_msg = input_text.split()

# ? more commands
        if input_text == "more commands":
            return """url <link>: open a link on the browser\nkill <proc>: terminate process\ncmd <command>: execute shell command\n
            ls or dir: show elements in the current directory\ncd <dir>: change directory\ndownload <file>: download a file"""

# ? return actual pc's screen status
        if input_text == "screen status":
            for proc in psutil.process_iter():
                if (proc.name() == "LogonUI.exe"):
                    return 'Screen is Locked'
            return 'Screen is Unlocked'

# ? look pc screen
        if input_text == "lock screen":
            try:
                if platform.system() == "Darwin":
                    subprocess.call('pmset sleepnow', shell=True)
                elif platform.system() == "Windows":
                    ctypes.windll.user32.LockWorkStation()
                elif platform.system() == "Linux":
                    os.popen('gnome-screensaver-command --lock')
                return "Screen locked successfully"
            except:
                return "Error while locking screen"

# ? take a screenshot of the pc's screen
        if input_text == "take screenshot":
            update.message.bot.send_photo(
                chat_id=self.CHAT_ID, photo=open(self.take_screenshot(), 'rb'))
            return None

# ? paste che copied text of the pc
        if input_text == "paste clipboard":
            return pyperclip.paste()

# ? put the pc asleep
        if input_text == "sleep":
            try:
                if platform.system() == "Windows":
                    os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
                elif platform.system() == "Darwin":
                    subprocess.Popen('caffeinate')
                return "Your PC was put to sleep"
            except:
                return "Cannot put your PC to sleep"

# ? list of all the processes
        if input_text == "list process":
            try:
                proc_list = []
                for proc in psutil.process_iter():
                    if proc.name() not in proc_list:
                        proc_list.append(proc.name())
                processes = "\n".join(proc_list)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            return processes

# ? kill a process
        if usr_msg[0] == "kill":
            proc_list = []
            for proc in psutil.process_iter():
                p = proc_list.append([proc.name(), str(proc.pid)])
            try:
                for p in proc_list:
                    if p[0] == usr_msg[1]:
                        psutil.Process(int(p[1])).terminate()
                return 'Process terminated successfully'
            except:
                return 'Error occured while killing the process'

# ? url search
        if usr_msg[0] == "url":
            try:
                webbrowser.open(usr_msg[1])
                return 'Link opened successfully'
            except:
                return 'Error occured while opening link'

# ? ls or dir
        if usr_msg[0].lower() == 'ls' or usr_msg[0] == 'dir':
            try:
                os.listdir()
            except:
                return 'No elements in the current directory'
            filenames = "\n".join(os.listdir())
            if filenames:
                return filenames

# ? cd
        if usr_msg[0].lower() == "cd":
            if usr_msg[1]:
                try:
                    os.chdir(usr_msg[1])
                except:
                    return "Directory not found !"
                res = os.getcwd()
                if res:
                    return res

# ? download
# TODO: check for bugs
        if usr_msg[0] == 'download':
            if usr_msg[1]:
                if os.path.exists(usr_msg[1]):
                    try:
                        document = open(usr_msg[1], 'rb')
                        update.message.bot.send_document(
                            self.CHAT_ID, document)
                    except:
                        return "Something went wrong!"

# ? use console
        if usr_msg[0] == "cmd":
            res = subprocess.Popen(
                usr_msg[1:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
            stdout = res.stdout.read().decode("utf-8", 'ignore').strip()
            stderr = res.stderr.read().decode("utf-8", 'ignore').strip()
            if stdout:
                return (stdout)
            elif stderr:
                return (stderr)
            else:
                return ''

# ? send response
# ! change the username if you want to be the only one to use the bot!
    def send_response(self, update, context):
        user_message = update.message.text
        #! Please modify this
        if update.message.chat["username"] != "nickname":
            print("[!] " + update.message.chat["username"] + ' tried to use this bot')
            context.bot.send_message(
                chat_id=self.CHAT_ID, text="Nothing to see here.")
        else:
            user_message = user_message.encode(
                'ascii', 'ignore').decode('ascii').strip(' ')
            user_message = user_message[0].lower() + user_message[1:]
            response = self.handle_message(update, user_message)
            if response:
                if (len(response) > 4096):
                    for i in range(0, len(response), 4096):
                        context.bot.send_message(
                            chat_id=self.CHAT_ID, text=response[i:4096+i])
                else:
                    context.bot.send_message(
                        chat_id=self.CHAT_ID, text=response)

# ! print in console everytime the bot /start on Telegram
# TODO: PRINT "BOT ONLINE" IN CHAT EVERYTIME THE FILE IS RUN
    def start_bot(self):
        updater = Updater(self.TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start_command))
        dp.add_handler(MessageHandler(Filters.text, self.send_response))
        dp.add_error_handler(self.error)
        updater.start_polling()
        print("[=] BOT now live!")
        updater.idle()


bot = TelegramBot()
bot.start_bot()
