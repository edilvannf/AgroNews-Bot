#import asyncio
import requests
from bs4 import BeautifulSoup

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from telegram.helpers import escape_markdown

TOKEN = '7571180435:AAHkH8imAm8u0RT2COUy7o4FDua4OgpVQNM'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Sites de notícias", callback_data='noticias')],
        [InlineKeyboardButton("❓ Ajuda", callback_data='ajuda')],
        [InlineKeyboardButton("ℹ️ Sobre", callback_data='sobre')],
        [InlineKeyboardButton("❌ Sair", callback_data='sair_bot')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("👋 Escolha uma opção:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("👋 Escolha uma opção:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    back_to_menu_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data='menu')]])

    if query.data == 'noticias':
        keyboard = [
            [InlineKeyboardButton("🌾 Globo Rural", callback_data='globorural_select_count')],
            [InlineKeyboardButton("🚜 Canal Rural", callback_data='canalrural_select_count')],
            [InlineKeyboardButton("🌱 AgroLink", callback_data='agrolink_select_count')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='menu')]
        ]
        await query.edit_message_text("Escolha um site para ver as últimas notícias:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'ajuda':
        help_message = (
            "ℹ️ *Guia de Ajuda do Bot de Notícias Agrícolas*\n\n"
            "Este bot foi desenvolvido para te manter atualizado com as últimas notícias do agronegócio, coletando informações dos principais portais\\.\n\n"
            "*Funcionalidades Principais:*\n"
            "1\\.  *Sites de Notícias:* Selecione esta opção para escolher entre os sites disponíveis \\(Globo Rural, Canal Rural, AgroLink\\) e ver as notícias mais recentes\\.\n"
            "2\\.  *Quantidade de Notícias:* Após escolher um site, você poderá selecionar se deseja visualizar 5, 10 ou 15 notícias\\.\n"
            "3\\.  *Voltar ao Menu Principal:* Após visualizar as notícias, um botão aparecerá para retornar ao menu inicial e explorar outras opções\\.\n"
            "4\\.  *Sobre:* Conheça mais sobre os criadores e o propósito deste projeto\\.\n"
            "5\\.  *Sair:* Encerra a sessão do bot\\. Você pode reiniciá\\-lo a qualquer momento com o comando /start\\.\n\n"
            "*Comandos Rápidos:*\n"
            "•  `/start`: Inicia o bot e exibe o menu principal\\.\n"
            "•  `/sair`: Desliga o bot\\.\n\n"
            "Se tiver alguma dúvida ou sugestão, sinta\\-se à vontade para explorar as opções do menu\\!"
        )
        await query.edit_message_text(help_message, parse_mode='MarkdownV2', reply_markup=back_to_menu_keyboard)

    elif query.data == 'sobre':
        await query.edit_message_text(
            "🤖 Bot criado por Edilvan, Ketlhin e Ana Paula. Este projeto foi desenvolvido como parte da disciplina Projeto Integrador à Programação, no curso de Big Data no Agronegócio da UNICENTRO, com o objetivo de aplicar conhecimentos de web scraping, automação e manipulação de dados com Python.\n\nFontes: Globo Rural, Canal Rural e AgroLink.",
            reply_markup=back_to_menu_keyboard
        )

    elif query.data == 'menu':
        await start(update, context)

    elif query.data == 'sair_bot':
        await sair(update, context)

    elif query.data.endswith('_select_count'):
        site_name_prefix = query.data.replace('_select_count', '')
        keyboard = [
            [InlineKeyboardButton("5 Notícias", callback_data=f'{site_name_prefix}_5')],
            [InlineKeyboardButton("10 Notícias", callback_data=f'{site_name_prefix}_10')],
            [InlineKeyboardButton("15 Notícias", callback_data=f'{site_name_prefix}_15')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='noticias')]
        ]
        await query.edit_message_text("Quantas notícias você gostaria de ver?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('globorural_'):
        num_articles = int(query.data.split('_')[1])
        await enviar_globorural(query, context, num_articles)
    elif query.data.startswith('canalrural_'):
        num_articles = int(query.data.split('_')[1])
        await enviar_canalrural(query, context, num_articles)
    elif query.data.startswith('agrolink_'):
        num_articles = int(query.data.split('_')[1])
        await enviar_agrolink(query, context, num_articles)

async def enviar_globorural(query, context, num_articles):
    try:
        pagina = requests.get('https://globorural.globo.com/ultimas-noticias/')
        pagina.raise_for_status()
        soup = BeautifulSoup(pagina.text, 'html.parser')
        noticias = soup.find_all('div', class_='feed-post-body')

        mensagens = []
        for i, div in enumerate(noticias[:num_articles]):
            h2 = div.find('h2', class_='feed-post-link gui-color-primary gui-color-hover')
            if h2:
                a_tag = h2.find('a')
                if a_tag:
                    texto = escape_markdown(a_tag.text.strip(), version=2)
                    link = escape_markdown(a_tag['href'], version=2)
                    mensagens.append(f'👉 *{texto}*\n🔗 {link}')

        if mensagens:
            keyboard = [[InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data='menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f'📰 *Últimas {num_articles} notícias do Globo Rural:*\n\n' + '\n\n'.join(mensagens),
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("Não foi possível encontrar notícias do Globo Rural no momento.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar Globo Rural: {e}")
        await query.edit_message_text("Ocorreu um erro ao buscar notícias do Globo Rural. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Erro inesperado em enviar_globorural: {e}")
        await query.edit_message_text("Ocorreu um erro inesperado ao processar as notícias do Globo Rural.")

async def enviar_canalrural(query, context, num_articles):
    try:
        pagina = requests.get('https://www.canalrural.com.br/ultimas-noticias/')
        pagina.raise_for_status()
        soup = BeautifulSoup(pagina.text, 'html.parser')
        artigos = soup.find_all('article')

        mensagens = []
        for artigo in artigos[:num_articles]:
            link_tag = artigo.find('a', href=True)
            if link_tag and link_tag.text.strip():
                texto = escape_markdown(link_tag.text.strip(), version=2)
                link = escape_markdown(link_tag['href'], version=2)
                mensagens.append(f'👉 *{texto}*\n🔗 {link}')

        if mensagens:
            keyboard = [[InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data='menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f'📰 *Últimas {num_articles} notícias do Canal Rural:*\n\n' + '\n\n'.join(mensagens),
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("Não foi possível encontrar notícias do Canal Rural no momento.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar Canal Rural: {e}")
        await query.edit_message_text("Ocorreu um erro ao buscar notícias do Canal Rural. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Erro inesperado em enviar_canalrural: {e}")
        await query.edit_message_text("Ocorreu um erro inesperado ao processar as notícias do Canal Rural.")

async def enviar_agrolink(query, context, num_articles):
    try:
        pagina = requests.get('https://www.agrolink.com.br/noticias/')
        pagina.raise_for_status()
        soup = BeautifulSoup(pagina.text, 'html.parser')
        noticias_agrolink = soup.select('a.block-news-main-general-title')

        if not noticias_agrolink:
            print("Nenhum elemento 'a.block-news-main-general-title' encontrado no AgroLink.")
            await query.edit_message_text("Não foi possível encontrar notícias do AgroLink com o seletor atual. O site pode ter mudado ou não há notícias disponíveis.")
            return

        mensagens = []
        for link_noticia in noticias_agrolink[:num_articles]:
            texto = escape_markdown(link_noticia.get_text(strip=True), version=2)
            link = link_noticia['href']
            if link.startswith('/'):
                link = f'https://www.agrolink.com.br{link}'
            link = escape_markdown(link, version=2)
            mensagens.append(f'👉 *{texto}*\n🔗 {link}')

        if mensagens:
            keyboard = [[InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data='menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f'📰 *Últimas {num_articles} notícias do AgroLink:*\n\n' + '\n\n'.join(mensagens),
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        else:
            print("A lista de mensagens do AgroLink ficou vazia após o processamento dos elementos encontrados.")
            await query.edit_message_text("Não foi possível processar as notícias do AgroLink. Tente novamente mais tarde.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar AgroLink: {e}")
        await query.edit_message_text("Ocorreu um erro ao buscar notícias do AgroLink. Verifique sua conexão ou tente novamente mais tarde.")
    except Exception as e:
        print(f"Erro inesperado em enviar_agrolink: {e}")
        await query.edit_message_text("Ocorreu um erro inesperado ao processar as notícias do AgroLink.")

async def sair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text("👋 Até logo! O bot será desligado.")
    else:
        await update.message.reply_text("👋 Até logo! O bot será desligado.")
    await context.application.stop()

async def configurar_comandos(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Inicia o bot"),
        BotCommand("sair", "Fecha o bot"),
    ])

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.post_init = configurar_comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sair", sair))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot está rodando...")
    app.run_polling()
