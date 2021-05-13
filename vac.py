import logging
import os, pickle
import secret_token

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


if os.path.isfile('obj/pcs.pkl'):
    pcs = load_obj('pcs')
else:
    pcs = dict()

if os.path.isfile('obj/users.pkl'):
    users = load_obj('users')
else:
    users = dict()

if os.path.isfile('obj/lastmsg.pkl'):
    lastmsg = load_obj('lastmsg')
else:
    lastmsg = dict()


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Hoi, ik ben Bill, de onofficiële Telegram bot voor prullenbakvaccin.nl! Ik kan notificaties sturen als er mogelijk vaccins beschikbaar komen in je buurt.")
    update.message.reply_text("Er zitten geen garanties aan het gebruik van mij en de website. Lees de website vooral even goed door zodat je weet waar je aan toe bent.")
    update.message.reply_text("Ik ben niet ontwikkeld door of enigszins verbonden aan prullenbakvaccin.nl. Ik ben gemaakt door @WTFloris omdat hij op een brakke middag niets te doen had. Ik kijk slechts iedere 5 minuten op de website of er nieuwe vaccins beschikbaar zijn gekomen.")
    update.message.reply_text("Wil je een bericht ontvangen als dat zo is? Geef mij dan even je postcode :)")


def postcode(update: Update, context: CallbackContext) -> None:
    pc = update.message.text.lower()
    cid = update.message.chat.id

    # Strip the space if needed
    if ' ' in pc:
        pc = pc[0:4] + pc[5:7]

    # Create a new postcode and new file if they don't exist, or append the chat id to the existing postcode
    if pc not in pcs.keys():
        pcs[pc] = [cid]
        os.mknod("data/" + pc)
    else:
        pcs[pc].append(cid)

    # If a user already exists, remove the chat id from their old postcode, possibly remove everything if they are the only user
    if cid in users.keys():
        pcs[users[cid]].remove(cid)
        if pcs[users[cid]] == []:
            os.remove('data/' + pcs[users[cid]])
            pcs.pop(users[cid], None)

    users[cid] = pc

    save_obj(pcs, 'pcs')
    save_obj(users, 'users')
    update.message.reply_text(f"Je postcode staat nu ingesteld op {pc.upper()}. Als je deze wilt wijzigen stuur je gewoon een andere postcode.")
    if pc in lastmsg.keys():
        update.message.reply_text(lastmsg[pc])


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help!')


def check_for_update(context: CallbackContext) -> None:
# def check_for_update(update: Update, context: CallbackContext) -> None:
    for pc in pcs.keys():
        with open('data/' + pc, 'r') as f:
            content = f.read()

            # If there is information available and there is no previous message
            if content != '' and pc not in lastmsg.keys():
                for chatid in pcs[pc]:
                    context.bot.send_message(chat_id=chatid, text=content)
                    context.bot.send_message(chat_id=chatid, text=f"Kijk op www.prullenbakvaccin.nl/{pc} voor meer informatie.")
                lastmsg[pc] = content

            # Or if there is information available but it does not match the previous message
            elif content != '':
                if lastmsg[pc] != content:
                    for chatid in pcs[pc]:
                        context.bot.send_message(chat_id=chatid, text=content)
                        context.bot.send_message(chat_id=chatid, text=f"Kijk op www.prullenbakvaccin.nl/{pc} voor meer informatie.")
                    lastmsg[pc] = content

            # Or if there are no vaccines but there was a previous message
            elif content == '' and pc in lastmsg.keys():
                for chatid in pcs[pc]:
                    context.bot.send_message(chat_id=chatid, text="De vaccins uit het vorige bericht zijn volgens de website helaas niet meer beschikbaar.")
                lastmsg.pop(pc, None)
    save_obj(lastmsg, 'lastmsg')


# def instruct(update: Update, _: CallbackContext) -> None:
#     update.message.reply_text("Als je je postcode wilt wijzigen, stuur die dan door. Verder kan ik niet zo veel voor je doen.")


def save_obj(obj, name):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def main() -> None:
    updater = Updater(secret_token.TOKEN, persistence=PicklePersistence(filename='vacbot_persist'), use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.regex('^[1-9][0-9]{3} ?(?!sa|sd|ss|SA|SD|SS)[A-z]{2}$'), postcode))

    check_for_update_job = updater.job_queue.run_repeating(check_for_update, interval=300, first=0)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()





