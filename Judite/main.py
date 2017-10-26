import telegram
import configparser
# import redis
import mysql.connector

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Configuring bot
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Connecting to Telegram API
# Updater retrieves information and dispatcher connects commands
updater = Updater(token=config['DEFAULT']['token'])
dispatcher = updater.dispatcher

# Connecting to Redis db
db = mysql.connector.connect(user=config['DB']['user'], 
                            password=config['DB']['password'],
                            host=config['DB']['host'],
                            port=config['DB']['port'],
                            database=config['DB']['db'])


def start(bot, update):
    """
        Shows an welcome message and help info about the available commands.
    """
    me = bot.get_me()

    # Welcome message
    # msg = "Hello!\n"
    # msg += "I'm {0} and I came here to help you.\n".format(me.first_name)
    # msg += "What would you like to do?\n\n"
    # msg += "/support - Opens a new support ticket\n"
    # msg += "/settings - Settings of your account\n\n"
    msg = "Ola, eu sou Judite, a bibliotecaria.\n Esses comandos vao te ajudar:\n\n"
    msg += "/livros - Exibe os livros disponiveis\n"
    msg += "/pegar [id] - Marca um livro como estando com voce\n"
    msg += "/emprestimos - Exibe os seus emprestimos\n"
    msg += "/devolver [id] - devolve um livro que estava com voce\n"

    # Commands menu
    main_menu_keyboard = [[telegram.KeyboardButton('/livros')]#,
                          #,telegram.KeyboardButton('/start')],
                          ,[telegram.KeyboardButton('/emprestimos')]]
    reply_kb_markup = telegram.ReplyKeyboardMarkup(main_menu_keyboard,
                                                   resize_keyboard=True,
                                                   one_time_keyboard=True)

    # Send the message with menu
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg,
                     reply_markup=reply_kb_markup)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)




def support(bot, update):
    try:
        print "Execute inicio"
        user = update.message.from_user
        text = update.message.text.replace("/execute", "")

        cursor = db.cursor()

        cursor.execute("insert into LIVROS (COD_OBRA) VALUES (2), (3), (3), (5)")
        print "comando realizado"
        db.commit()
    except Exception as e:
        print(e)
        print "pegar - deu ruim"
        cursor.rollback()

support_handler = CommandHandler('support', support)
dispatcher.add_handler(support_handler)





def livros(bot, update):
    try:
        
        print "livros - entrei"
        cursor = db.cursor()
        print "livros - criei o cursor"
        
        query =  " select ID_OBRA, NOM_OBRA, count(NOM_OBRA)  " 
        query += " From LIVROS LIV "
        query += " INNER JOIN OBRAS OBR ON OBR.ID_OBRA = LIV.COD_OBRA "
        query += " left join EMPRESTIMOS EMP ON EMP.COD_LIVRO = LIV.ID_LIVRO AND DATA_DEVOLUCAO IS NULL "
        query += " where ID_EMPRESTIMO IS NULL "
        query += " GROUP BY ID_OBRA, NOM_OBRA "
        query += " order by NOM_OBRA "


        cursor.execute(query)
        print "livros - executei a consulta"
        
        msg = "ID - LIVRO (QUANTIDADE) \n"
        results = cursor.fetchall()
        if (len(results) == 0):
            msg = "tem nada nessa biblioteca nao parceiro"
            print msg
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return
        for row in results:
            msg += str(row[0]) + " - " + row[1] + " ("+str(row[2]) +")\n"

        # msg = "Livros disponiveis: \n\n"
        # msg+= "1 - Calculo 1 - James Stewart\n"
        # msg+= "2 - O Torcicologista, Excelencia - Goncalo M. Tavares\n"
        # msg+= "3 - Apostila de Fis Exp 3\n\n"
        
        
        
        bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
        print "livros - retornei a mensagem"        
    except Exception as e:
        print(e)
        print "livros - deu ruim"

    # finally:
    #     cursor.close()

livros_handler = CommandHandler('livros', livros)
dispatcher.add_handler(livros_handler)




def pegar(bot, update):
    try:
        
        user = update.message.from_user
        text = update.message.text.replace("/pegar", "")
        text = text.strip()

        print "id usuario: " + str(user.id)
        print "usuario: " + user.first_name + ' ' + user.last_name
        print "mensagem: " + text 
        print "PEGAR - entrei"
        cursor = db.cursor()
        print "PEGAR - criei o cursor"

        query =  ' select ID_PESSOA'
        query += ' FROM PESSOAS'
        query += ' WHERE COD_PESSOA_TELEGRAM = ' + str(user.id)

        cursor.execute(query)
        print "busquei a pessoa"
        results = cursor.fetchall()

        if (len(results) == 0):
            print "novo por aqui"
            #query =  " start transaction; "
            query = " insert into PESSOAS"
            query += " (NOM_PESSOA, COD_PESSOA_TELEGRAM, USR_PESSOA)"
            query += " VALUES ( '" + user.first_name + " " + user.last_name + "'"
            query += " , "+ str(user.id)
            query += " , '"+ user.username +"')"
            print "/ " + query + " /"
            cursor.execute(query)
            print "inseri pessoa"

            query =  ' select ID_PESSOA'
            query += ' FROM PESSOAS'
            query += ' WHERE COD_PESSOA_TELEGRAM = ' + str(user.id)

            cursor.execute(query)
            print "busquei a pessoa dnv"
            results = cursor.fetchall()

        for row in results:
            ID_PESSOA = row[0] 
            print "ID_PESSOA: " + str(ID_PESSOA)
        
        query =  ' select MIN(LIV.ID_LIVRO)'
        query += ' From LIVROS LIV'
        query += ' INNER JOIN OBRAS OBR ON OBR.ID_OBRA = LIV.COD_OBRA'
        query += ' left join EMPRESTIMOS EMP ON EMP.COD_LIVRO = LIV.ID_LIVRO AND DATA_DEVOLUCAO IS NULL'
        query += ' where ID_EMPRESTIMO IS NULL'
        query += ' AND ID_OBRA = ' + text
        query += ' '

        cursor.execute(query)
        print "busquei o livro "
        results = cursor.fetchall()
        print "len(results) = " + str(len(results))
        print "str(results[0][0]) = " + str(results[0][0])
        print "bool = " + str(results[0][0] == None)
        if (results[0][0] == None):
            msg = "livro nao disponivel"
            print msg
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)            
            return
        
        for row in results:
            ID_LIVRO = row[0] 
            print "ID_LIVRO: " + str(ID_LIVRO)

        query =  " "
        query += " INSERT INTO EMPRESTIMOS"
        query += " (COD_LIVRO, COD_PESSOA, DATA_EMPRESTIMO, SIT_EMPRESTIMO)"
        query += " VALUES"
        query += " (" + str(ID_LIVRO) + ", " + str(ID_PESSOA) + ", NOW(), '01')"

        cursor.execute(query)
        print "Inseri o emprestimo. "

        msg = "Ok, bons estudos.\n\n"        
        
        db.commit()
        
        print "commit"
        bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
        print "pegar - retornei a mensagem"        
    except Exception as e:
        print(e)
        print "pegar - deu ruim"
        cursor.rollback()
    finally:
        # cursor.commit()
        # cursor.close()
         print ""
pegar_handler = CommandHandler('pegar', pegar)
dispatcher.add_handler(pegar_handler)




def execute(bot, update):
    try:
        print "Execute inicio"
        user = update.message.from_user
        text = update.message.text.replace("/execute", "")

        cursor = db.cursor()
        print "comando realizado"
        cursor.execute(text)
        db.commit()
        msg = "FIM"
        bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
    except Exception as e:
        print(e)
        print "pegar - deu ruim"
        cursor.rollback()

execute_handler = CommandHandler('execute', execute)
dispatcher.add_handler(execute_handler)


def Emprestimos(bot, update):
    try:
        print "emprestimos - inicio"
        user = update.message.from_user
        #text = update.message.text.replace("/execute", "")

        query =  " SELECT OBR.ID_OBRA, OBR.NOM_OBRA, COUNT(OBR.ID_OBRA) "
        query += " FROM EMPRESTIMOS"
        query += " LEFT JOIN LIVROS ON LIVROS.ID_LIVRO = EMPRESTIMOS.COD_LIVRO "
        query += " LEFT JOIN OBRAS OBR ON LIVROS.COD_OBRA = OBR.ID_OBRA"
        query += " LEFT JOIN PESSOAS ON PESSOAS.ID_PESSOA = EMPRESTIMOS.COD_PESSOA"
        query += " WHERE EMPRESTIMOS.DATA_DEVOLUCAO IS NULL "
        query += " AND PESSOAS.COD_PESSOA_TELEGRAM = " + str(user.id)
        query += " GROUP BY OBR.ID_OBRA, OBR.NOM_OBRA"

        cursor = db.cursor()
        cursor.execute(query)
        print "emprestimos - comando realizado"

        results = cursor.fetchall()
        if (results[0][0] == None):
            msg = "emprestimos - nenhum livro encontrado"
            print msg
            bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
            return

        msg = "ID - LIVRO (QUANTIDADE) \n"
        for row in results:
            msg += str(row[0]) + " - " +  row[1] +" (" +str(row[2]) + ")\n"


        bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
    except Exception as e:
        print(e)
        print "emprestimos - deu ruim"
        cursor.rollback()

Emprestimos_handler = CommandHandler('emprestimos', Emprestimos)
dispatcher.add_handler(Emprestimos_handler)



def Devolver(bot, update):
    try:
        print "Devolver - inicio"
        user = update.message.from_user
        text = update.message.text.replace("/devolver", "")



        query = " SELECT MIN(ID_EMPRESTIMO)"
        query += " FROM EMPRESTIMOS"
        query += " inner JOIN LIVROS ON ID_LIVRO = COD_LIVRO AND DATA_DEVOLUCAO IS NULL"
        query += " INNER JOIN OBRAS ON ID_OBRA = COD_OBRA"
        query += " INNER join PESSOAS ON ID_PESSOA = COD_PESSOA"
        query += " WHERE COD_PESSOA_TELEGRAM = " + str(user.id)
        query += " AND ID_OBRA = " + str(text)

        cursor = db.cursor()
        print "Criei o cursor"
        cursor.execute(query)
        print "executei a busca"

        results = cursor.fetchall()
        print "atribui ao cursor"

        if (results[0][0] == None):
            msg = "emprestimos - emprestimo nao encontrado"
            print msg
            bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
            return
        print " passei da validacao"
        for row in results:
            ID_EMPRESTIMO = row[0]


        query =  " update EMPRESTIMOS"
        query += " set DATA_DEVOLUCAO = now()"
        query += " WHERE ID_EMPRESTIMO = " + str(ID_EMPRESTIMO)


        cursor.execute(query)
        print "Devolver - comando realizado"
        
        msg = "Devolvido \n"
        
        bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
                     
    except Exception as e:
        print(e)
        print "Devolver - deu ruim"
        cursor = db.cursor() 
        cursor.rollback()

Devolver_handler = CommandHandler('devolver', Devolver)
dispatcher.add_handler(Devolver_handler)






def unknown(bot, update):
    """
        Placeholder command when the user sends an unknown command.
    """
    msg = "Sorry, I don't know what you're asking for."
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg)

unknown_handler = MessageHandler([Filters.command], unknown)
dispatcher.add_handler(unknown_handler)