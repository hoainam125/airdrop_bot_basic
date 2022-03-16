import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import mysql.connector

# set up database
mydb = mysql.connector.connect(
    host="localhost",
    user="AirdropUser",
    password="password@",
    database="telegramairdropbot"
)

bot = telebot.TeleBot("#token telegrambot")
wrong_format_message = "Wrong Format :) ???"
user_in4 = {
    "id_telegram": "",
    "username_telegram": "",
    "link_fb": "",
    "user_twitter": "",
    "wallet": "",
    "referral_count": 0
}
mycursor = mydb.cursor()

# Inline button for Continue and
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Continue", callback_data="continue"))
    return markup


# Inline button When done all
def done_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Statistics", callback_data="statistic"),
               InlineKeyboardButton("Referral", callback_data="referral"),
               InlineKeyboardButton("Wallet address", callback_data="wallet"))
    return markup
def check_wallet(address):
    if(address.startswith("0x") and len(address) == 42):
        return True
    else: return False
def check_referral(message,id_referral):
    if(len(message.text.split()) > 1):
        sql = "SELECT * FROM user_in4 WHERE id_telegram LIKE %s "
        val = (id_referral, )
        try:
            mycursor.execute(sql, val)
            myresult = mycursor.fetchone()
            if(mycursor.rowcount > 0):
                referral = myresult[1]
                referral_message = "You were invited by @" + str(referral)
                bot.send_message(message.chat.id, referral_message)
                return id_referral
        except mysql.Error as err:
            print(err)


# insert user_in4
def insert_in4():
    sql = "INSERT INTO user_in4 (id_telegram, username_telegram, link_fb, user_twitter, wallet, referral_count) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (list(user_in4.values()))
    try:
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
    except mysql.Error as err:
        print(err)

# print in4
def statistic(message, user_id):
    if(len(message.text.split()) > 1):
        sql = "SELECT * FROM user_in4 WHERE id_telegram LIKE %s "
        val = (user_id, )
        try:
            mycursor.execute(sql, val)
            myresult = mycursor.fetchone()
            if(mycursor.rowcount > 0):
                referral = myresult[1]
                referral_message = "You were invited by @" + str(referral)
                bot.send_message(message.chat.id, referral_message)
        except mysql.Error as err:
            print(err)

# Count referral
def add_referral(id_referral):
    sql ="UPDATE user_in4 SET referral_count = referral_count + 1 WHERE id_telegram = %s"
    val = (id_referral,)
    try:
        mycursor.execute(sql, val)
        mydb.commit()

    except mysql.Error as err:
        print(err)
# Start command function

@bot.message_handler(commands=['start'])
def Start(message):
    user_in4["id_telegram"] = message.chat.id
    user_in4["username_telegram"] = message.chat.username  # Get telegram Id vs telegram username #TODO : write function check deeplink and return NOne
    try:
        id_referral = str(message.text.split()[1]) #Get Deeplink
        check_referral(message,id_referral)
    bot.send_message(message.chat.id, "Press continue to continue", reply_markup=gen_markup())

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if call.data == "continue":
            twitter(message)


    # class Nhập thông tin người dùng.
    def twitter(pm):
        sent_msg = bot.send_message(pm.chat.id, "Type your twitter ID with @")
        bot.register_next_step_handler(sent_msg, fb)  # Next message will call the name_handler function

    def fb(twitter):
        if ("@" in twitter.text):
            user_in4["user_twitter"] = twitter.text
        else:
            bot.send_message(twitter.chat.id, wrong_format_message,reply_markup= gen_markup())
            return twitter



        sent_msg = bot.send_message(twitter.chat.id, "Type your link FB: https://www.facebook.com/user_name")
        bot.register_next_step_handler(sent_msg, wallet)  # Next message will call the name_handler function

    def wallet(pm):
        fb = pm.text
        if( "https://www.facebook.com" not in fb):
            bot.send_message(pm.chat.id, wrong_format_message, reply_markup= gen_markup())
            return fb
        else:
            user_in4["link_fb"] = fb
        sent_msg = bot.send_message(pm.chat.id, "PLease type your wallet address")
        bot.register_next_step_handler(sent_msg, done_task)
    def done_task(addr):
        wallet= addr.text
        if(check_wallet(wallet)):
            user_in4["wallet"] =  wallet
            congrat_message = "Successful, You invite link is: {}".format("https://t.me/huy2111_bot?start="+str(user_in4["id_telegram"]))
            bot.send_message(addr.chat.id, congrat_message, reply_markup= done_markup())
            insert_in4()
            add_referral(id_referral)
        else:
            bot.send_message(addr.chat.id, wrong_format_message, reply_markup= gen_markup())
        # insert vào database




bot.polling()
