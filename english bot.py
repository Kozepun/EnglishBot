import telebot
import random
from telebot import types
import os

words = [[]]
translation = [[]]

UID = {}
forbiddenSymbols = ["^", "*", "%"]

wordNumber = []
answerBut = []
correctAnswers = []
buttonText = [[]]

inputEnabled = []

with open("token.txt") as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)

wordLists = []
customWordLists = [[]]

with open("wordList.txt", encoding='utf-8', mode='r') as file:
    for line in file:
        if '#' in line:
            wordLists.append(line)

@bot.message_handler(commands=['start'])
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
        inputEnabled.append(False)

    MUID = UID[message.chat.id]

    customWordLists[MUID] = []
    buttons = []

    kb1 = types.InlineKeyboardMarkup(row_width=2)

    for wordlist in wordLists:
        buttons.append(types.InlineKeyboardButton(text=f"{wordlist.replace('#', '')}", callback_data=f"{wordlist}"))

    if (os.path.exists(f"{message.chat.id}.txt")):
        with open(f"{message.chat.id}.txt", encoding='utf-8', mode='r') as file:
            for line in file:
                if '#' in line:
                    customWordLists[MUID].append(line.replace("#", "").replace("\n", ""))
    else:
        f = open(f"{message.chat.id}.txt", "x")
        f.close()

    for wordlist in customWordLists[MUID]:
        buttons.append(types.InlineKeyboardButton(text=f"{wordlist}", callback_data=f"^{wordlist}"))

    kb1.add(*buttons)
    kb1.add(types.InlineKeyboardButton(text=f"Wordlist Editor", callback_data=f"*custom"))
    bot.send_message(message.chat.id, "choose words", reply_markup=kb1)


@bot.message_handler()
def input(message):
    MUID = UID[message.chat.id]
    if inputEnabled[MUID]:
        if "/" in message.text:
            inputEnabled[MUID] = False
        else:
            text = message.text
            textSplit = str(text).split("\n")
            textFile = open(f"{message.chat.id}.txt", encoding='utf-8', mode='a')
            error = False
            if "#" in textSplit[0]:
                i = 0
                while i < len(textSplit) - 1:
                    i += 1
                    b = textSplit[i].split("-")
                    if len(b) != 2 or "#" in textSplit[i]:
                        error = True
                        break
            else:
                error = True

            if error == False:
                for word in textSplit:
                    textFile.write(f"\n{word.replace('^', '').replace('%', '').replace('*', '')}")
                textFile.close()
                bot.send_message(message.chat.id, "List Created Successfully")
                inputEnabled[MUID] = False
            else:
                bot.send_message(message.chat.id,"Error occured try:\n#listName\nword-translation\nword-translation\nword-translation\nword-translation")


@bot.message_handler(commands=['delete'])
def delete(message):
    isFound = False
    wasFound = False
    allLines = []
    with open(f"{message.chat.id}.txt", encoding='utf-8', mode='r+') as file:
        for lineA in file:
            line = lineA.replace("\n", "")
            if '#' in line:
                if str(message.text).replace("/delete ", "") == line:
                    isFound = True
                    wasFound = True
                elif isFound == True:
                    isFound = False
                    bot.send_message(message.chat.id,f"successfully deleted {str(message.text).replace('/delete ', '')}")
            if isFound == False:
                allLines.append(lineA)
        if wasFound == False:
            bot.send_message(message.chat.id, f"can't find {str(message.text).replace('/delete ', '')}")
        file.seek(0)
        file.truncate()
        file.writelines(allLines)


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
            buttons = [types.InlineKeyboardButton(text=f"add", callback_data=f"*add"), types.InlineKeyboardButton(text=f"remove", callback_data=f"*remove")]
            kb3.add(*buttons)

            bot.send_message(call.message.chat.id, "choose", reply_markup=kb3)
        elif calldata == "add":
            bot.send_message(call.message.chat.id, "example:\n#listName\nword-translation\nword-translation\nword-translation\nword-translation")
            inputEnabled[CUID] = True
        elif calldata == "remove":
            kb4 = types.InlineKeyboardMarkup(row_width=2)
            buttons = []
            for wordlist in customWordLists[CUID]:
                buttons.append(types.InlineKeyboardButton(text=f"{wordlist}", callback_data=f"*{wordlist}"))
            kb4.add(*buttons)

            bot.send_message(call.message.chat.id, "choose", reply_markup=kb4)
        elif calldata in customWordLists[CUID]:
            kb5 = types.InlineKeyboardMarkup(row_width=2)
            kb5.add(types.InlineKeyboardButton(text=f"Yes", callback_data=f"*%{calldata}"))
            kb5.add(types.InlineKeyboardButton(text=f"No", callback_data=f"*N"))

            bot.send_message(call.message.chat.id, f"are you sure you want to delete {calldata}", reply_markup=kb5)
        elif "%" in call.data:
            isFound = False
            wasFound = False
            allLines = []

            calldata1 = calldata.replace("%", "")

            with open(f"{call.message.chat.id}.txt", encoding='utf-8', mode='r+') as file:
                for lineA in file:
                    line = lineA.replace("\n", "")
                    if '#' in line:
                        if calldata1 == line.replace("#", ""):
                            isFound = True
                            wasFound = True
                        elif isFound == True:
                            isFound = False
                            bot.send_message(call.message.chat.id,f"successfully deleted {calldata1}")
                    if isFound == False:
                        allLines.append(lineA)
                if wasFound == False:
                    bot.send_message(call.message.chat.id, f"can't find {calldata1}")
                file.seek(0)
                file.truncate()
                file.writelines(allLines)

    else:
        if call.data in wordLists or call.data.replace("^", "") in customWordLists[CUID]:
            correctAnswers[CUID] = 0
            wordNumber[CUID] = -1
            translation[CUID] = list()
            words[CUID] = list()

            isFound = False
            if "^" not in call.data:
                with open("wordList.txt", encoding='utf-8', mode='r') as file:
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
                with open(f"{call.message.chat.id}.txt", encoding='utf-8', mode='r') as file:
                    for line in file:
                        if '#' in line:
                            if call.data.replace("^", "") == line.strip().replace("#", ""):
                                isFound = True
                            elif isFound == True:
                                break
                        elif isFound:
                            p = line.strip().split("-")
                            words[CUID].append(p[0])
                            translation[CUID].append(p[1])

            timedtranslation = tuple(translation[CUID])
            timedwords = tuple(words[CUID])

            shufleList = list(zip(timedtranslation, timedwords))
            random.shuffle(shufleList)
            translation[CUID], words[CUID] = zip(*shufleList)

            kb6 = types.InlineKeyboardMarkup(row_width=2)
            btn_types = types.InlineKeyboardButton(text='Yes', callback_data=f'restart')
            btn_types2 = types.InlineKeyboardButton(text='No', callback_data='exit')
            kb6.add(btn_types, btn_types2)
            msg = f"{call.data.replace('#', '').replace('^', '')}".replace("\n", "")
            msg += "\n"
            for word in words[CUID]:
                msg += f"{word}\n"
            msg += "Confirm?"
            bot.send_message(call.message.chat.id, msg, reply_markup=kb6)

        elif call.data == "exit":
            start(call.message)
        else:
            if call.data != "restart" and call.data != str(answerBut[CUID]):
                print(f"{call.data}-{answerBut[CUID]}")
                bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id,text=f"incorrect, {words[CUID][wordNumber[CUID]]} - {translation[CUID][wordNumber[CUID]]}")
            if wordNumber[CUID] == len(words[CUID]) - 1:
                kb2 = types.InlineKeyboardMarkup(row_width=2)
                kb2.add(types.InlineKeyboardButton(text=f"restart", callback_data=f"restart"))
                kb2.add(types.InlineKeyboardButton(text=f"exit", callback_data=f"exit"))
                bot.send_message(call.message.chat.id, f"congratulations {correctAnswers[CUID]}/{len(translation[CUID])}",reply_markup=kb2)
                correctAnswers[CUID] = 0
                wordNumber[CUID] = -1
            else:

                if call.data == str(answerBut[CUID]):
                    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text="correct")
                    correctAnswers[CUID] += 1

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
