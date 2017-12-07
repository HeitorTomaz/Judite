# encoding: utf-8
# encoding: iso-8859-1
# encoding: win-1252
import csv
import configparser
import redis
import mysql.connector

def processar_arquivo(f):
    try:
        reader = csv.reader(f,delimiter=',')
        for linha in reader:
            nome,autor,quantidade,link = linha
            print (nome + "," + autor + "," + quantidade + "," + link)
            #TODO: INSERT na tabela livos
    except Exception as e:
        print(e)
        print("Deu ruim na importação")

config = configparser.ConfigParser()
config.read_file(open('config.ini'))
# Connecting to Redis db
db = mysql.connector.connect(user=config['DB']['user'], 
                            password=config['DB']['password'],
                            host=config['DB']['host'],
                            port=config['DB']['port'],
                            database=config['DB']['db'])

path = input("Digite o caminho do arquivo que deseja importar: \n")
try:
   with open(path, 'r', encoding='utf-8') as f:
       processar_arquivo(f)
except IOError:
    print (u'Arquivo não encontrado!')



