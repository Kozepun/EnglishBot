import telebot
import random
from telebot import types
import ollama
from pymongo import MongoClient
from deep_translator import GoogleTranslator

client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users = db["users"]
groupsdb = db["groups"]


groups = []
teachers = []
admins = []

path = ""

words = [[]]
translation = [[]]

UID = {}
forbiddenSymbols = ["^", "*", "%"]

wordNumber = []
answerBut = []
correctAnswers = []
buttonText = [[]]

inputEnabled = []

wordLists = []
customWordLists = [[]]

localizedMessage =[["обери категорію","выбери категорию","choose category"],
                   ["потрібно додати мінімум п\'ять слів","нужно добавить минимум пять слов","you need to add minimum 5 words"],
                   ["категорія успішно створена","категория успешно создана","succesfully created category"],
                   ["помилка спробуйте:\n#ім\'я категорії\nслово-переклад\nслово-переклад\nслово-переклад\nслово-переклад\nслово-переклад","ошибка попробуйте:\n#имя категории\nслово-перевод\nслово-перевод\nслово-перевод\nслово-перевод\nслово-перевод","error try:\nword-translation\nword-translation\nword-translation\nword-translation\nword-translation"],
                   ["редактор категорій","редактор категорий","category editor"],
                   ["напишіть наприклад:\n#ім\'я категорії\nслово-переклад\nслово-переклад\nслово-переклад\nслово-переклад\nслово-переклад","напишите например:\n#имя категории\nслово-перевод\nслово-перевод\nслово-перевод\nслово-перевод\nслово-перевод","write for example:\nword-translation\nword-translation\nword-translation\nword-translation\nword-translation"],
                   ["обери категорію для видалення","выбери категорию для удаления","choose category for deletion"],
                   ["ти точно хочеш видалити категорію","ты точно хочешь удалить категорию","are you sure you want to delete"],
                   ["неможливо знайти","невозможно найти","can\'t find"],
                   ["видалено","удалено","deleted"],
                   ["вітаю","поздравляю","congratulations"],
                   ["перегляд слів категорії","предпросмостр слов категории","preview of category"],
                   ["підтвердити вибір","подтвердить выбор","confirm choice"],
                   ["не правильно","не правильно","incorrect"],
                   ["правильно","правильно","correct"],
                   ["обери мову","выбери язык","choose language"],
                   ["помилка спробуйте /gen ім'я категорії","ошибка попробуйте /gen имя категории","error try /gen category name"],
                   ["ви приєднались до групи", "вы присоединились к групе", "you joined group"],
                   ["ця група не існує","эта група не существует","this group doesn't exist"],
                   ["обери завдання","выбери задание","choose task"],
                   ["помилка спробуйте /hw назва групи","ошибка попробуйте /hw название групы","error try /hw group name"],
                   ["у вас є нове завдання","у вас есть новое задание","you have a new task"],
                   ["завдання надіслано","задание отослано","the task has been sent"],
                   ["у вас немає доступу","у вас нет доступа","you don't have access"]]

localizedButtons = [["редактор категорій","редактор категорий","category editor"],
                    ["додати","добавить","add"],
                    ["видалити","удалить","remove"],
                    ["так","да","yes"],
                    ["ні","нет","no"],
                    ["повторити","повторить","retry"],
                    ["вийти","выйти","exit"]]

lang = []

with open(f"{path}token.txt") as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)

with open(f"{path}wordList.txt", encoding='utf-8', mode='r') as file:
    for line in file:
        if '#' in line:
            wordLists.append(line)

for user in users.find():
    level = user["level"]
    id = user["_id"]
    lang.append(user["lang"])

    UID.update({id: len(UID)})
    words.append([])
    translation.append([])
    wordNumber.append(-1)
    answerBut.append(0)
    correctAnswers.append(0)
    buttonText.append([])
    customWordLists.append([])

    inputEnabled.append(False)
    if level > 0:
        teachers.append(id)
        if level > 1:
            admins.append(id)

for group in groupsdb.find({}):
    groups.append(group["group"])
@bot.message_handler(commands=['start', 'lang', 'gen', 'joingroup', 'hw', 'newgroup', 'req', 'promote', ])
def start(message):
    global customWordLists

    if message.chat.id not in UID:
        UID.update({message.chat.id: len(UID)})
        words.append([])
        translation.append([])
        wordNumber.append(-1)
        answerBut.append(0)
        correctAnswers.append(0)
        buttonText.append([])
        customWordLists.append([])
        lang.append(0)
        inputEnabled.append(False)

        users.insert_one({"_id": message.chat.id, "level": 0, "lang": 0, "group": "", "wordlists": [], "words": [], "translations": []})

    MUID = UID[message.chat.id]
    inputEnabled[MUID] = False

    if message.text == "/lang":
        kb1 = types.InlineKeyboardMarkup(row_width=3)
        kb1.add(types.InlineKeyboardButton(text=f"UKR", callback_data="//lang0"),
                types.InlineKeyboardButton(text=f"RUS", callback_data="//lang1"),
                types.InlineKeyboardButton(text=f"ENG", callback_data="//lang2"))
        bot.send_message(message.chat.id, f"{localizedMessage[15][lang[MUID]]}", reply_markup=kb1)
    elif '/req' in message.text:
        for user in users.find({"level" : 2}):
            bot.send_message(user["_id"], f"/promote {message.chat.id} 1")
    elif '/promote' in message.text:
        for user in users.find({"_id" : message.chat.id}):
            if user["level"] == 2:
                textSplit = message.text.split(" ")
                print(textSplit[1])
                myQuery = {"_id" : int(textSplit[1])}
                newvalues = {"$set": {"level" : int(textSplit[2])}}
                users.update_one(myQuery, newvalues)

    elif '/gen' in message.text:
        if len(message.text.split(" ")) > 1:
            theme = message.text.replace('/gen ', '')

            myquery = {"_id": message.chat.id}

            dwords = []
            dtrans = []

            response = ollama.generate(model='qwen3:4b',prompt=f'10 english words NO NUMERATION no other text each from new line theme {theme}',think=False)

            english_words = response["response"].replace("\n", ",")

            ukrainian_words = GoogleTranslator(source='en', target='uk').translate(english_words).split(",")

            for en, uk in zip(english_words.split(","), ukrainian_words):
                dwords.append(en.strip())
                dtrans.append(uk.strip())

            newvalues = {"$push": {"words": dwords, "translations": dtrans, "wordlists": theme}}

            users.update_one(myquery, newvalues)

            bot.send_message(message.chat.id, f"{localizedMessage[2][lang[MUID]]}")



        else:
            bot.send_message(message.chat.id, localizedMessage[16][lang[MUID]])
    elif '/joingroup' in message.text:
        splitText = message.text.split(" ")
        if len(splitText) == 2:
            if(splitText[1] in groups):
                bot.send_message(message.chat.id, f"{localizedMessage[17][lang[MUID]]} {splitText[1]}")
                myquery = {"_id": message.chat.id}
                newvalues = {"$set": {"group": splitText[1]}}

                users.update_one(myquery, newvalues)
            else:
                bot.send_message(message.chat.id, localizedMessage[18][lang[MUID]])
    elif '/hw' in message.text:
        if message.chat.id in teachers:
            spl = message.text.split(" ")

            buttons = []
            kb1 = types.InlineKeyboardMarkup(row_width=2)

            if len(spl) == 2:
                if spl[1] in groups:
                    for user in users.find({"_id": message.chat.id}):
                        for wl in user["wordlists"]:
                            buttons.append(types.InlineKeyboardButton(text=wl, callback_data=f'?||?add-{wl}-{spl[1]}'))

                    kb1.add(*buttons)
                    bot.send_message(message.chat.id, localizedMessage[19][lang[MUID]], reply_markup=kb1)
                else:
                    bot.send_message(message.chat.id, localizedMessage[18][lang[MUID]])
            else:
                bot.send_message(message.chat.id, localizedMessage[20][lang[MUID]])
        else:
            bot.send_message(message.chat.id, localizedMessage[23][lang[MUID]])
    elif "/newgroup" in message.text:
        for user in users.find({"_id": message.chat.id}):
            if user["level"] == 2:
                splitText = message.text.split(" ")
                groupsdb.insert_one({"group": splitText[1]})
                groups.append(splitText[1])

                bot.send_message(message.chat.id, f"ok")
    else:
        customWordLists[MUID] = []
        buttons = []

        kb1 = types.InlineKeyboardMarkup(row_width=2)

        for wordlist in wordLists:
            buttons.append(types.InlineKeyboardButton(text=f"{wordlist.replace('#', '')}", callback_data=f"{wordlist}"))

        for user in users.find({"_id":message.chat.id}):
            customWordLists[MUID] = user["wordlists"]
            for wordlist in customWordLists[MUID]:
                buttons.append(types.InlineKeyboardButton(text=f"{wordlist}", callback_data=f"^{wordlist}"))

        kb1.add(*buttons)
        kb1.add(types.InlineKeyboardButton(text=f"{localizedButtons[0][lang[MUID]]}", callback_data=f"*custom"))
        bot.send_message(message.chat.id, f"{localizedMessage[0][lang[MUID]]}", reply_markup=kb1)


@bot.message_handler()
def input(message):
    MUID = UID[message.chat.id]
    if inputEnabled[MUID] == True:
            text = message.text
            textSplit = str(text).split("\n")
            error = ""
            if "#" in textSplit[0]:
                i = 0
                while i < len(textSplit) - 1:
                    i += 1
                    b = textSplit[i].split("-")
                    if len(b) != 2 or "#" in textSplit[i]:
                        error = "default"
                        break
                if len(textSplit) < 6 and error == "":
                    bot.send_message(message.chat.id,f"{localizedMessage[1][lang[MUID]]}")
                    error = "length"
            else:
                error = "default"

            if error == "":
                myquery = {"_id": message.chat.id}

                awords = []
                atrans = []

                for w in textSplit:
                    if "#" in w:
                        newvalues = {"$push": {"wordlists": w.replace("#","")}}
                        users.update_one(myquery, newvalues)
                    else:
                        awords.append(w.split("-")[0])
                        atrans.append(w.split("-")[1])


                newvalues = {"$push": {"words": awords, "translations": atrans}}

                users.update_one(myquery, newvalues)

                bot.send_message(message.chat.id, f"{localizedMessage[2][lang[MUID]]}")


            elif error == "default":
                bot.send_message(message.chat.id,f"{localizedMessage[3][lang[MUID]]}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global answerBut
    global wordNumber
    global correctAnswers
    global words
    global translation
    global inputEnabled

    CUID = UID[call.message.chat.id]

    inputEnabled[CUID] = False

    if "*" in call.data:
        calldata = call.data.replace("*", "")

        if calldata == "custom":
            kb3 = types.InlineKeyboardMarkup(row_width=2)
            #buttons = [types.InlineKeyboardButton(text=f"{localizedButtons[1][lang[CUID]]}", callback_data=f"*add"), types.InlineKeyboardButton(text=f"{localizedButtons[2][lang[CUID]]}", callback_data=f"*remove"), types.InlineKeyboardButton(text=f"edit", callback_data=f"*edit")]
            buttons = [types.InlineKeyboardButton(text=f"{localizedButtons[1][lang[CUID]]}", callback_data=f"*add"),
                       types.InlineKeyboardButton(text=f"{localizedButtons[2][lang[CUID]]}", callback_data=f"*remove"),]
            kb3.add(*buttons)

            bot.send_message(call.message.chat.id, f"{localizedMessage[4][lang[CUID]]}", reply_markup=kb3)
        elif calldata == "add":
            bot.send_message(call.message.chat.id, f"{localizedMessage[5][lang[CUID]]}")
            inputEnabled[CUID] = True
        elif calldata == "remove" or calldata == "edit":
            kb4 = types.InlineKeyboardMarkup(row_width=2)
            buttons = []
            for wordlist in customWordLists[CUID]:
                if calldata == "remove":
                    buttons.append(types.InlineKeyboardButton(text=f"{wordlist}", callback_data=f"*{wordlist}"))
                else:
                    buttons.append(types.InlineKeyboardButton(text=f"{wordlist}", callback_data=f"e*{wordlist}"))
            kb4.add(*buttons)
            if calldata == "remove":
                bot.send_message(call.message.chat.id, f"{localizedMessage[6][lang[CUID]]}", reply_markup=kb4)
            else:
                bot.send_message(call.message.chat.id, f"choose to edit", reply_markup=kb4)
        elif call.data.replace("e*", "") in customWordLists[CUID] or calldata in customWordLists[CUID]:
            if calldata in customWordLists[CUID]:
                kb5 = types.InlineKeyboardMarkup(row_width=2)
                kb5.add(types.InlineKeyboardButton(text=f"{localizedButtons[3][lang[CUID]]}", callback_data=f"*%{calldata}"))
                kb5.add(types.InlineKeyboardButton(text=f"{localizedButtons[4][lang[CUID]]}", callback_data=f"*N"))

                bot.send_message(call.message.chat.id, f"{localizedMessage[7][lang[CUID]]} {calldata}?", reply_markup=kb5)
            else:
                isFound = False
                with open(f"{path}{call.message.chat.id}.txt", encoding='utf-8', mode='r') as file:
                    for line in file:
                        if '#' in line:
                            if call.data.replace("e*", "") == line.strip().replace("#", ""):
                                isFound = True
                            elif isFound == True:
                                break
                        elif isFound:
                            p = line.strip().split("-")
                            words[CUID].append(p[0])
                            translation[CUID].append(p[1])

                buttons = []
                for word in words[CUID]:
                    i = words[CUID].index(word)
                    buttons.append(types.InlineKeyboardButton(text=f"{word}-{translation[CUID][i]}", callback_data=f"*{word}"))
                kb6 = types.InlineKeyboardMarkup(row_width=2)
                kb6.add(*buttons)
                bot.send_message(call.message.chat.id, f"what word do you want to edit",reply_markup=kb6)
        elif calldata in words[CUID]:
            kb7 = types.InlineKeyboardMarkup(row_width=2)
            kb7.add(types.InlineKeyboardButton(text=f"add", callback_data="52"))
            kb7.add(types.InlineKeyboardButton(text=f"remove", callback_data="52"))
            kb7.add(types.InlineKeyboardButton(text=f"edt", callback_data="52"))
            bot.send_message(call.message.chat.id, f"what word do you want to edit", reply_markup=kb7)
        elif "%" in call.data:
            calldata1 = calldata.replace("%", "")

            for user in users.find({"_id": call.message.chat.id}):
                if calldata1 in user["wordlists"]:


                    newLists = []
                    newWords = []
                    newTrans = []

                    i = 0
                    while i < len(user["wordlists"]):
                        if user["wordlists"][i] != calldata1:
                            newLists.append(user["wordlists"][i])
                            newWords.append(user["words"][i])
                            newTrans.append(user["translations"][i])
                        i += 1


                    myquery = {"_id": call.message.chat.id}
                    newvalues = {"$set": {"words": newWords, "translations": newTrans, "wordlists": newLists}}
                    users.update_one(myquery, newvalues)
                    bot.send_message(call.message.chat.id, f"{localizedMessage[9][lang[CUID]]} {calldata1}")
                else:
                    bot.send_message(call.message.chat.id, f"{localizedMessage[8][lang[CUID]]} {calldata1}")
    elif "?||?" in call.data:
        for user in users.find({"_id": call.message.chat.id}):
            shareListName = call.data.split("-")[1]

            i = user["wordlists"].index(shareListName)

            shareListWords = user["words"][i]
            shareListTrans = user["translations"][i]

            myquery = {"group": call.data.split("-")[2]}

            newvalues = {"$push": {"words": shareListWords, "translations": shareListTrans, "wordlists" : shareListName}}

            users.update_many(myquery, newvalues)

            for user1 in users.find(myquery):
                bot.send_message(user1["_id"], localizedMessage[21][lang[CUID]])

        bot.send_message(call.message.chat.id, localizedMessage[22][lang[CUID]])

    elif "//lang" in call.data:
        lang[CUID] = int(call.data.replace("//lang", ""))

        myquery = {"_id": call.message.chat.id}
        newvalues = {"$set": {"lang": lang[CUID]}}

        users.update_many(myquery, newvalues)

        start(call.message)
    else:
        if call.data in wordLists or call.data.replace("^", "") in customWordLists[CUID]:
            correctAnswers[CUID] = 0
            wordNumber[CUID] = -1
            translation[CUID] = list()
            words[CUID] = list()

            isFound = False
            if "^" not in call.data:
                with open(f"{path}wordList.txt", encoding='utf-8', mode='r') as file:
                    for line in file:
                        if '#' in line:
                            if call.data == line:
                                isFound = True
                            elif isFound == True:
                                break
                        elif isFound:
                            p = line.strip().split("-")
                            words[CUID].append(p[0])
                            translation[CUID].append(p[1])

            else:

                for user in users.find({"_id": call.message.chat.id}):
                    Listindex = user["wordlists"].index(call.data.replace("^", ""))
                    words[CUID] = user["words"][Listindex]
                    translation[CUID] = user["translations"][Listindex]

            timedtranslation = tuple(translation[CUID])
            timedwords = tuple(words[CUID])

            shufleList = list(zip(timedtranslation, timedwords))
            random.shuffle(shufleList)
            translation[CUID], words[CUID] = zip(*shufleList)

            kb6 = types.InlineKeyboardMarkup(row_width=2)
            kb6.add(types.InlineKeyboardButton(text=f"{localizedButtons[3][lang[CUID]]}", callback_data=f'restart'), types.InlineKeyboardButton(text=f"{localizedButtons[4][lang[CUID]]}", callback_data='exit'))
            msg = f"{localizedMessage[11][lang[CUID]]} {call.data.replace('#', '').replace('^', '')}".replace("\n", "")
            msg += "\n"
            for word in words[CUID]:
                i = words[CUID].index(word)
                msg += f"{word}-{translation[CUID][i]}\n"
            msg += f"\n{localizedMessage[12][lang[CUID]]}?"
            bot.send_message(call.message.chat.id, msg, reply_markup=kb6)

        elif call.data == "exit":
            start(call.message)
        else:
            if call.data != "restart" and call.data != str(answerBut[CUID]):
                bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id,text=f"{localizedMessage[13][lang[CUID]]}, {words[CUID][wordNumber[CUID]]} - {translation[CUID][wordNumber[CUID]]}")
            if call.data == str(answerBut[CUID]):
                bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text=f"{localizedMessage[14][lang[CUID]]}")
                correctAnswers[CUID] += 1
            if wordNumber[CUID] == len(words[CUID]) - 1:
                kb2 = types.InlineKeyboardMarkup(row_width=2)
                kb2.add(types.InlineKeyboardButton(text=f"{localizedButtons[5][lang[CUID]]}", callback_data=f"restart"))
                kb2.add(types.InlineKeyboardButton(text=f"{localizedButtons[6][lang[CUID]]}", callback_data=f"exit"))
                bot.send_message(call.message.chat.id, f"{localizedMessage[10][lang[CUID]]} {correctAnswers[CUID]}/{len(translation[CUID])}",reply_markup=kb2)
                correctAnswers[CUID] = 0
                wordNumber[CUID] = -1
            else:
                wordNumber[CUID] += 1
                answerBut[CUID] = random.randint(0, 3)

                r = list(range(0, wordNumber[CUID])) + list(range(wordNumber[CUID] + 1, len(translation[CUID])))
                b = random.sample(r, 4)

                buttonText[CUID] = [translation[CUID][b[0]], translation[CUID][b[1]], translation[CUID][b[2]],translation[CUID][b[3]]]
                buttonText[CUID][answerBut[CUID]] = translation[CUID][wordNumber[CUID]]

                kb = types.InlineKeyboardMarkup(row_width=2)
                btn_types = types.InlineKeyboardButton(text=buttonText[CUID][0], callback_data='0')
                btn_types2 = types.InlineKeyboardButton(text=buttonText[CUID][1], callback_data='1')
                btn_types3 = types.InlineKeyboardButton(text=buttonText[CUID][2], callback_data='2')
                btn_types4 = types.InlineKeyboardButton(text=buttonText[CUID][3], callback_data='3')
                kb.add(btn_types, btn_types2, btn_types3, btn_types4)
                bot.send_message(call.message.chat.id, words[CUID][wordNumber[CUID]], reply_markup=kb)
    bot.answer_callback_query(call.id)


bot.infinity_polling()