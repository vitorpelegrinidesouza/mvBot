import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# carrega as credenciais do arquivo .env
from dotenv import load_dotenv
load_dotenv()

# configura as credenciais do Google Drive
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), scope)
client = gspread.authorize(creds)

# configura o servidor Flask
app = Flask(__name__)

# rota para lidar com as solicitações do webhook do Twilio
@app.route('/webhook', methods=['POST'])
def webhook():
    # analisa a mensagem recebida
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()

    # verifica se a mensagem é sobre o evento
    if 'evento' in incoming_msg:
        resp.message('Ótimo! Qual é a data do evento? (DD/MM/AAAA)')
    elif '/' in incoming_msg:
        # verifica se a mensagem é sobre a data do evento
        try:
            datetime.strptime(incoming_msg, '%d/%m/%Y')
            resp.message('Entendido! Qual é o local do evento?')
        except ValueError:
            resp.message('Desculpe, não entendi a data. Por favor, digite a data no formato DD/MM/AAAA.')
    elif 'local' in incoming_msg:
        # verifica se a mensagem é sobre o local do evento
        resp.message('Perfeito! Quantas pessoas são esperadas?')
    elif incoming_msg.isdigit():
        # verifica se a mensagem é sobre o número de pessoas esperadas
        resp.message('Entendi! Vamos escolher o cardápio. Digite "entrada", "salada", "massa" ou "sobremesa".')
    elif incoming_msg in ['entrada', 'salada', 'massa', 'sobremesa']:
        # verifica se a mensagem é sobre a categoria de cardápio escolhida
        resp.message(f'Ótima escolha! Aqui estão as opções de {incoming_msg}: \n\n- Opção 1\n- Opção 2\n- Opção 3\n\nDigite o número da opção escolhida.')
    elif incoming_msg.isdigit() and int(incoming_msg) in range(1, 4):
        # verifica se a mensagem é sobre a opção de cardápio escolhida
        resp.message('Obrigado por escolher o cardápio!')
        
        # salva as informações na planilha
        sheet = client.open('Planilha de Eventos').sheet1
        row = [datetime.now().strftime('%d/%m/%Y %H:%M:%S'), request.values.get('From'), request.values.get('Body')]
        sheet.append_row(row)

    return str(resp)