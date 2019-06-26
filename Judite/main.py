import telegram
import configparser
# import redis
import mysql.connector
#!/usr/bin/python
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
    try:
        """
            Shows an welcome message and help info about the available commands.
        """
        me = bot.get_me()
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        print( "start\n")
        msg = "Ola, eu sou Judite, a bibliotecaria.\n"
        
        
        result = BuscaSessao(bot, update)
        print( "len(result) == " + str(len(result)))

        if (len(result) == 0):
            print( "novo por aqui")
            cursor = db.cursor()
            nome = str(user.first_name) + " " + str(user.last_name)
            print( "nome = " + nome)
            query = " call biblioteca.inserePessoa( " + str(user.id) +", '" + str(user.username) +"', '" + nome.strip() + "'); "
            print( query)
            cursor.execute(query)

            db.commit()
            print( "inseri pessoa")
        else:
            print("result[0]")
            print(result[0])
            if str(result[0][2]) != None and str(result[0][3]) != "":
                msg += "Conectado a biblioteca: " + str(result[0][3]) + "\n\n"
            


        msg += "Esses comandos vao te ajudar:\n\n"
        msg += "/Bibliotecas - Exibe todas as bibliotecas\n"
        msg += "/Conectar [id] - Acessa uma biblioteca\n"
        msg += "/Livros - Exibe os livros disponiveis\n"
        msg += "/Areas - Exibe as areas dos livros presentes\n"
        msg += "/LivrosArea [id] - Exibe os livros disponiveis em uma area\n"
        msg += "/Pegar [id] - Marca um livro como estando com voce\n"
        msg += "/Emprestimos - Exibe os seus emprestimos\n"
        msg += "/Devolver [id] - devolve um livro que estava com voce\n"

        # Commands menu
        main_menu_keyboard = [[telegram.KeyboardButton('/Bibliotecas')]
                            ,[telegram.KeyboardButton('/Livros')]
                            ,[telegram.KeyboardButton('/Areas')]
                            ,[telegram.KeyboardButton('/Emprestimos')]
                            ,[telegram.KeyboardButton('/start')]]
        reply_kb_markup = telegram.ReplyKeyboardMarkup(main_menu_keyboard,
                                                    resize_keyboard=True,
                                                    one_time_keyboard=True)

        func = "START"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()
        # Send the message with menu
        bot.send_message(chat_id=update.message.chat_id,
                        text=msg,
                        reply_markup=reply_kb_markup)
    except Exception as e:
        print(e)
        print( "start - deu ruim")
        cursor = db.cursor()
        db.rollback()

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)




def support(bot, update):
    try:
        print( "Execute inicio")
        user = update.message.from_user
        text = update.message.text.replace("/execute", "")

        cursor = db.cursor()

        cursor.execute("insert into LIVROS (COD_OBRA) VALUES (2), (3), (3), (5)")
        print( "comando realizado")
        db.commit()
    except Exception as e:
        print(e)
        print( "pegar - deu ruim")
        cursor = db.cursor()
        db.rollback()

support_handler = CommandHandler('support', support)
dispatcher.add_handler(support_handler)





def livros(bot, update):
    try:
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        print( "livros - entrei")
        cursor = db.cursor()
        print( "livros - criei o cursor")
        
        # query =  " select ID_OBRA, NOM_OBRA, count(NOM_OBRA)  " 
        # query += " From LIVROS LIV "
        # query += " INNER JOIN OBRAS OBR ON OBR.ID_OBRA = LIV.COD_OBRA "
        # query += " left join EMPRESTIMOS EMP ON EMP.COD_LIVRO = LIV.ID_LIVRO AND DATA_DEVOLUCAO IS NULL "
        # query += " where ID_EMPRESTIMO IS NULL "
        # query += " GROUP BY ID_OBRA, NOM_OBRA "
        # query += " order by NOM_OBRA "

        result = BuscaSessao(bot, update)
        print( 4)
        print( "len(result) == " + str(len(result)))

        if (len(result) == 0):
            #novo por aqui
            start(bot, update)
            return 
        if (str(result[0][2]) == ""):
            Bibliotecas(bot, update)
            return 
        

        args = [result[0][1]]

        cursor.callproc( "biblioteca.buscaLivros", args)
        print( "livros - executei a consulta")
        for res in cursor.stored_results():
            print( 2)
            results = res.fetchall()

        print( " result[0] = " + str(result[0]))
            
        msg = "ID - LIVRO (QUANTIDADE) \n"
        if (len(results) == 0):
            msg = "tem nada nessa biblioteca nao parceiro"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return
        for row in results:
            msg += "/" + str(row[0]) + " - " + row[1] + " ("+str(row[2]) +")\n"

        
        func = "LIVROS"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()
        
        bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
        print( "livros - retornei a mensagem"        )
    except Exception as e:
        print(e)
        print( "livros - deu ruim")
        cursor = db.cursor()
        db.rollback()

    # finally:
    #     cursor.close()

livros_handler = CommandHandler('livros', livros)
dispatcher.add_handler(livros_handler)




def areas(bot, update):
    try:
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        print( "areas - entrei")
        cursor = db.cursor()
        print( "areas - criei o cursor")
        
        # query =  " select ID_OBRA, NOM_OBRA, count(NOM_OBRA)  " 
        # query += " From LIVROS LIV "
        # query += " INNER JOIN OBRAS OBR ON OBR.ID_OBRA = LIV.COD_OBRA "
        # query += " left join EMPRESTIMOS EMP ON EMP.COD_LIVRO = LIV.ID_LIVRO AND DATA_DEVOLUCAO IS NULL "
        # query += " where ID_EMPRESTIMO IS NULL "
        # query += " GROUP BY ID_OBRA, NOM_OBRA "
        # query += " order by NOM_OBRA "

        result = BuscaSessao(bot, update)
        print( 4)
        print( "len(result) == " + str(len(result)))

        if (len(result) == 0):
            #novo por aqui
            start(bot, update)
            return 
        if (str(result[0][2]) == ""):
            Bibliotecas(bot, update)
            return 
        

        args = [result[0][2]]

        cursor.callproc( "biblioteca.buscaAreas", args)
        print( "areas - executei a consulta")
        for res in cursor.stored_results():
            print( 2)
            results = res.fetchall()

        print( " result[0] = " + str(result[0]))
            
        msg = "ID - AREA \n"
        if (len(results) == 0):
            msg = "tem nada nessa biblioteca nao parceiro"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return
        for row in results:
            msg += "/" + str(row[0]) + " - " + row[1] +"\n"

        
        func = "AREAS"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()
        
        bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
        print( "areas - retornei a mensagem"        )
    except Exception as e:
        print(e)
        print( "areas - deu ruim")
        cursor = db.cursor()
        db.rollback()

    # finally:
    #     cursor.close()

areas_handler = CommandHandler('areas', areas)
dispatcher.add_handler(areas_handler)



def livrosArea(bot, update):
    try:
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        print( "livrosArea - entrei")

        text = update.message.text.lower().replace("/livrosarea", "")
        text = text.replace("/", "").replace(" ", "")
        text = text.strip()

        if (text == ""):
            msg = "Escolha uma area\nex: /LivrosArea 1"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return

        cursor = db.cursor()
        print( "livrosArea - criei o cursor")
        
        # query =  " select ID_OBRA, NOM_OBRA, count(NOM_OBRA)  " 
        # query += " From LIVROS LIV "
        # query += " INNER JOIN OBRAS OBR ON OBR.ID_OBRA = LIV.COD_OBRA "
        # query += " left join EMPRESTIMOS EMP ON EMP.COD_LIVRO = LIV.ID_LIVRO AND DATA_DEVOLUCAO IS NULL "
        # query += " where ID_EMPRESTIMO IS NULL "
        # query += " GROUP BY ID_OBRA, NOM_OBRA "
        # query += " order by NOM_OBRA "

        result = BuscaSessao(bot, update)
        print( 4)
        print( "len(result) == " + str(len(result)))

        if (len(result) == 0):
            #novo por aqui
            start(bot, update)
            return 
        if (str(result[0][2]) == ""):
            Bibliotecas(bot, update)
            return 
        

        args = [result[0][2], int(text)]

        cursor.callproc( "biblioteca.buscaLivrosArea", args)
        print( "livrosArea - executei a consulta")
        for res in cursor.stored_results():
            print( 2)
            results = res.fetchall()

        print( " result[0] = " + str(result[0]))
            
        msg = "ID - LIVRO (QUANTIDADE) \n"
        if (len(results) == 0):
            msg = "tem nada nessa biblioteca nao parceiro"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return
        for row in results:
            msg += "/" + str(row[0]) + " - " + row[1] + " ("+str(row[2]) +")\n"

        
        func = "LIVROS_AREA"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()
        
        bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
        print( "livrosArea - retornei a mensagem"        )
    except Exception as e:
        print(e)
        print( "livrosArea - deu ruim")
        cursor = db.cursor()
        db.rollback()

    # finally:
    #     cursor.close()

livrosArea_handler = CommandHandler('livrosArea', livrosArea)
dispatcher.add_handler(livrosArea_handler)



def pegar(bot, update):
    try:
        
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        text = update.message.text.lower().replace("/pegar", "")
        text = text.replace("/", "").replace(" ", "")
        text = text.strip()

        print( "id usuario: " + str(user.id))
        print( "usuario: " + user.first_name + ' ' + user.last_name)
        print( "mensagem: " + text )
        print( "PEGAR - entrei")

        if (text == ""):
            msg = "Escolha um livro\nex: /Pegar 1"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return

        cursor = db.cursor()
        print( "PEGAR - criei o cursor")

        result = BuscaSessao(bot, update)
        print( "len(result) == " + str(len(result)))

        if (len(result) == 0):
            #novo por aqui
            start(bot, update)
            return 
        if (str(result[0][2]) == ""):
            Bibliotecas(bot, update)
            return 

        sessao = str(result[0][1])
        biblioteca = str(result[0][2])
        IdObra = text

        query =  ' select MIN(LIV.ID_LIVRO)'
        query += ' From LIVROS LIV'
        query += ' INNER JOIN OBRAS OBR ON OBR.ID_OBRA = LIV.COD_OBRA '
        query += ' left join EMPRESTIMOS EMP ON ( EMP.COD_LIVRO = LIV.ID_LIVRO AND EMP.DT_DEVOLUCAO IS NULL ) '
        query += ' where ID_EMPRESTIMO IS NULL'
        query += ' AND ID_OBRA = ' + text
        query += ' AND LIV.COD_BIBLIOTECA = ' + biblioteca 

        cursor.execute(query)
        print( "busquei o livro ")
        results = cursor.fetchall()
        print( "len(results) = " + str(len(results)))
        if (len(results) == 0):
            msg = "livro nao disponivel"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)            
            return
        

        query = " call biblioteca.pegaLivro( " + str(sessao) + ", " + str(IdObra)  + " ); "
        print (query)
        cursor.execute(query)
        print( "Inseri o emprestimo. ")

        msg = "Ok, bons estudos.\n\n"        
        
        func = "PEGAR"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()
        
        print( "commit")
        bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
        print( "pegar - retornei a mensagem"    )    
    except Exception as e:
        print(e)
        print( "pegar - deu ruim")
        cursor = db.cursor()
        db.rollback()
    finally:
        # cursor.commit()
        # cursor.close()
         print( "")
pegar_handler = CommandHandler('pegar', pegar)
dispatcher.add_handler(pegar_handler)




def execute(bot, update):
    try:
        print( "Execute inicio")
        user = update.message.from_user
        text = update.message.text.replace("/execute", "")

        cursor = db.cursor()
        print( "comando realizado")
        cursor.execute(text)
        db.commit()
        msg = "FIM"
        bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
    except Exception as e:
        print(e)
        print( "pegar - deu ruim")
        db.rollback()

execute_handler = CommandHandler('execute', execute)
dispatcher.add_handler(execute_handler)


def Emprestimos(bot, update):
    try:
        print( "emprestimos - inicio")
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        #text = update.message.text.replace("/execute", "")

        # query =  " SELECT OBR.ID_OBRA, OBR.NOM_OBRA, COUNT(OBR.ID_OBRA) "
        # query += " FROM EMPRESTIMOS"
        # query += " LEFT JOIN LIVROS ON LIVROS.ID_LIVRO = EMPRESTIMOS.COD_LIVRO "
        # query += " LEFT JOIN OBRAS OBR ON LIVROS.COD_OBRA = OBR.ID_OBRA"
        # query += " LEFT JOIN PESSOAS ON PESSOAS.ID_PESSOA = EMPRESTIMOS.COD_PESSOA"
        # query += " WHERE EMPRESTIMOS.DT_DEVOLUCAO IS NULL "
        # query += " AND PESSOAS.COD_PESSOA_TELEGRAM = " + str(user.id)
        # query += " GROUP BY OBR.ID_OBRA, OBR.NOM_OBRA"

        res = BuscaSessao(bot, update)
        if (len(res) == 0):
            #novo por aqui
            start(bot, update)
            return 
        if (str(res[0][2]) == ""):
            Bibliotecas(bot, update)
            return 
     
        query = " call biblioteca.buscaEmprestimos( "+ str(ID_PESSOA_TELEGRAM) +" ); "
        print( query)
        cursor = db.cursor(buffered=True)
        #cursor.execute(query)
        cursor.callproc( "biblioteca.buscaEmprestimos", [str(ID_PESSOA_TELEGRAM),])
        print( "emprestimos - comando realizado")
        for res in cursor.stored_results():
            results = res.fetchall()

        print("results")
        print(results)
        if (len(results) == 0):
            msg = "emprestimos - nenhum livro encontrado"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
            return

        msg = "Empréstimos em todas as bibliotecas:\nID - LIVRO [BIBLIOTECA]\n"
        for row in results:
            msg += "/" + str(row[0]) + " - " +  row[1] + " ["+ row[2] +"]\n"

        func = "EMPRESTIMOS"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()
        bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
    except Exception as e:
        print(e)
        print( "emprestimos - deu ruim")
        cursor = db.cursor()
        dc.rollback()

Emprestimos_handler = CommandHandler('emprestimos', Emprestimos)
dispatcher.add_handler(Emprestimos_handler)



def Devolver(bot, update):
    try:
        print( "Devolver - inicio")
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id        
        text = update.message.text.lower().replace("/devolver", "")
        text = text.replace("/", "").replace(" ", "").strip()

        if (text == ""):
            msg = "Escolha um livro\nex: /Devolver 1"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return

        result = BuscaSessao(bot, update)
        if (len(result) == 0):
            #novo por aqui
            start(bot, update)
            return 
        if (str(result[0][2]) == ""):
            Bibliotecas(bot, update)
            return 
        print( "Criei o cursor")
        cursor = db.cursor()
        cursor.callproc( "biblioteca.buscaEmprestimos", [str(ID_PESSOA_TELEGRAM),])
        print( "DEVOLVER - comando realizado")
        for res in cursor.stored_results():
            results = res.fetchall()
        ids = [row[0] for row in results]
        print ("ids")
        print (ids)
        if (not int(text) in ids):
            msg = "DEVOLVER - emprestimo nao encontrado"
            print(msg)
            bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
            return
        
        query = " call biblioteca.devolveLivro("+ text + "); "

        print( query)
        
        cursor.execute(query)
        print( "executei ")
        for res in cursor.stored_results():
            results = cursor.fetchall()

        func = "DEVOLVER"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()
        print( "Devolver - commit")
        msg = "Devolvido \n"
        
        bot.send_message(chat_id=update.message.chat_id,
                     text=msg)

    except Exception as e:
        print(e)
        print( "Devolver - deu ruim")
        cursor = db.cursor() 
        db.rollback()

Devolver_handler = CommandHandler('devolver', Devolver)
dispatcher.add_handler(Devolver_handler)



def Bibliotecas(bot, update):
    try:
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        query = " call biblioteca.buscaBibliotecas(); "

        cursor = db.cursor()
        print( "Criei o cursor")
        cursor.callproc( "biblioteca.buscaBibliotecas")
        print( "Bibliotecas - comando realizado")

        for res in cursor.stored_results():
            results = res.fetchall()


        if (len(results) == 0):
            msg = "Bibliotecas - nenhuma Biblioteca encontrada"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
            return
        print( results[0][0])
        msg = "Conecte-se a uma biblioteca:\n"
        msg += "ID - Biblioteca \n"
        for row in results:
            msg += "/" + str(row[0]) + " - " +  row[1] + "\n"

        func = "BIBLIOTECAS"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()

        bot.send_message(chat_id=update.message.chat_id,
                        text=msg)
    except Exception as e:
        print(e)
        print( "Bibliotecas - deu ruim")
        cursor = db.cursor()
        db.rollback()

Emprestimos_handler = CommandHandler('bibliotecas', Bibliotecas)
dispatcher.add_handler(Emprestimos_handler)


def Conectar(bot, update):
    try:
        user = update.message.from_user
        ID_PESSOA_TELEGRAM = user.id
        text = update.message.text.lower().replace("/conectar", "")
        text = text.replace("/", "")
        text = text.strip()

        if (text == "" or (not text.isnumeric()) ):
            msg = "Escolha um livro\nex: /Conectar 1"
            print( msg)
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return

        query = " call biblioteca.criaSessao(" + str(text) + ", " + str(ID_PESSOA_TELEGRAM) + " ); "

        print( "query = " + query)
        cursor = db.cursor()
        print( "Criei o cursor")
        cursor.execute(query)
        print( "Conectar - comando realizado")


        func = "CONECTAR"
        InsereLog(func, ID_PESSOA_TELEGRAM)
        db.commit()

        start(bot, update)
    except Exception as e:
        print(e)
        print( "Conectar - deu ruim")
        cursor = db.cursor()
        db.rollback()

Emprestimos_handler = CommandHandler('conectar', Conectar)
dispatcher.add_handler(Emprestimos_handler)






def unknown(bot, update):
    try:
        """
            Placeholder command when the user sends an unknown command.
        """
        msg = "Sorry, I don't know what you're asking for."
        log = BuscaLog(update)
        text = update.message.text.replace("/", "")
        text = text.replace(" ","")
        if ( (log == "") or (not text.isnumeric()) ):
            bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
            return
        

        if (log == "BIBLIOTECAS"):
            txt = "/conectar " + text
            update.message.text = txt
            Conectar(bot,update)
            return
        
        if (log == "LIVROS" or log == "LIVROS_AREA"):
            txt = "/pegar " + text
            update.message.text = txt
            pegar(bot,update)
            return

        if (log == "EMPRESTIMOS"):
            txt = "/devolver " + text
            update.message.text = txt
            Devolver(bot,update)
            return


        if (log == "AREAS"):
            txt = "/livrosArea " + text
            update.message.text = txt
            livrosArea(bot,update)
            return


        #se nao:
        bot.send_message(chat_id=update.message.chat_id,
                            text=msg)
        return
    except Exception as e:
        print(e)
        print( "Unknow - deu ruim")
        cursor = db.cursor()
        db.rollback()
unknown_handler = MessageHandler([Filters.command], unknown)
dispatcher.add_handler(unknown_handler)

##################################################################################


def BuscaSessao(bot, update):
    user = update.message.from_user
    ID_PESSOA_TELEGRAM = user.id
    cursor = db.cursor()

    #query = " call biblioteca.buscaSessao( " + str(ID_PESSOA_TELEGRAM) + " ); "
    args = [ID_PESSOA_TELEGRAM]
    cursor.callproc( "biblioteca.buscaSessao", args)
    #cursor.execute(query)
    #print( '1')
    for res in cursor.stored_results():
        #print( 2)
        #print( "res = " + str(res))
        return res.fetchall()
        

    return results



def InsereLog(funcao, ID_PESSOA_TELEGRAM):
    
    cursor = db.cursor()

    query = " call biblioteca.insereLog( " + str(ID_PESSOA_TELEGRAM) +", '"+ str(funcao) + "' ); "

    cursor.execute(query)
    
    return 

def BuscaLog(update):

    user = update.message.from_user
    ID_PESSOA_TELEGRAM = user.id
    cursor = db.cursor()

    args = [ID_PESSOA_TELEGRAM]
    cursor.callproc( "biblioteca.buscaComando", args)

    for res in cursor.stored_results():
        print( 2)
        BIBLIO = str(res.fetchall()[0][1])
        print( "str(res.fetchall()[0][1]) = " + BIBLIO)
        return BIBLIO
        
    return ""
