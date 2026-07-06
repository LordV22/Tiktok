import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler,
    ContextTypes, filters,
)
from telegram.constants import ChatAction

from config import settings, Security
from src.ai.chat_ai import ChatAI
from src.core.pipeline import Pipeline
from src.effects.cinematic import CinematicEffects
from src.effects.transitions import Transitions
from src.utils.files import FileManager

logger = logging.getLogger(__name__)

WAITING = 1


class VideoBot:
    def __init__(self):
        self.ai = ChatAI()
        self.pipeline = Pipeline()
        self.effects = CinematicEffects()
        self.transitions = Transitions()
        self.files = FileManager(settings.paths.temp, settings.paths.output)
        self.security = Security()

    def keyboard_main(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Chat com IA", callback_data="chat")],
            [
                InlineKeyboardButton("📸 Com Imagens", callback_data="images"),
                InlineKeyboardButton("🎬 Do Zero", callback_data="zero"),
            ],
            [
                InlineKeyboardButton("🎨 Templates", callback_data="templates"),
                InlineKeyboardButton("✨ Efeitos", callback_data="effects"),
            ],
            [InlineKeyboardButton("📚 Ajuda", callback_data="help")],
        ])

    def keyboard_back(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Voltar", callback_data="back")]
        ])

    async def start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(
            f"🎬 *Olá {user.first_name}!*\n\n"
            "Sou um bot de vídeos com *inteligência artificial*.\n\n"
            "💬 *Chat* - Descreva o vídeo em linguagem natural\n"
            "📸 *Imagens* - Envie fotos e crie um vídeo\n"
            "🎬 *Do Zero* - Gere um vídeo apenas com texto\n\n"
            "📝 *Exemplos:*\n"
            "• \"Quero um vídeo de 15s sobre segurança digital\"\n"
            "• \"Crie um vídeo para TikTok com efeito glitch\"\n"
            "• \"Faça um slideshow com minhas férias\"\n\n"
            "Escolha ou *me diga o que quer*:",
            reply_markup=self.keyboard_main(),
            parse_mode="Markdown",
        )
        return WAITING

    async def help_cmd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📚 *Como usar:*\n\n"
            "1. Clique em \"💬 Chat com IA\"\n"
            "2. Digite o que quer de forma natural\n"
            "3. A IA cria o vídeo automaticamente\n\n"
            "*Comandos:*\n"
            "/start - Iniciar\n"
            "/help - Ajuda\n"
            "/cancel - Cancelar\n"
            "/clear - Limpar conversa",
            parse_mode="Markdown",
        )

    async def button_handler(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "chat":
            await query.edit_message_text(
                "💬 *Modo Chat Ativado!*\n\n"
                "Descreva o vídeo que quer de forma natural.\n\n"
                "*Exemplos:*\n"
                "• \"Vídeo de 20s para minha loja\"\n"
                "• \"Slideshow com fotos de viagem\"\n"
                "• \"Vídeo para LinkedIn com efeito profissional\"\n\n"
                "📝 *Digite sua descrição:*",
                parse_mode="Markdown",
            )
            ctx.user_data["mode"] = "chat"

        elif query.data == "images":
            await query.edit_message_text(
                "📸 *Modo Imagens!*\n\n"
                "Envie suas fotos e depois digite o que quer.\n\n"
                "📷 *Envie a primeira imagem:*",
                parse_mode="Markdown",
            )
            ctx.user_data["mode"] = "images"
            ctx.user_data["images"] = []

        elif query.data == "zero":
            await query.edit_message_text(
                "🎬 *Criar do Zero!*\n\n"
                "Descreva detalhadamente o vídeo desejado.\n\n"
                "📝 *Descreva seu vídeo:*",
                parse_mode="Markdown",
            )
            ctx.user_data["mode"] = "zero"

        elif query.data == "templates":
            kb = [
                [
                    InlineKeyboardButton("🏢 Profissional", callback_data="tpl_professional"),
                    InlineKeyboardButton("✨ Moderno", callback_data="tpl_modern"),
                ],
                [
                    InlineKeyboardButton("🎨 Criativo", callback_data="tpl_creative"),
                    InlineKeyboardButton("🎬 Cinematográfico", callback_data="tpl_cinematic"),
                ],
                [
                    InlineKeyboardButton("📱 Social Media", callback_data="tpl_social"),
                    InlineKeyboardButton("🎮 Gaming", callback_data="tpl_gaming"),
                ],
                [InlineKeyboardButton("⬅️ Voltar", callback_data="back")],
            ]
            await query.edit_message_text(
                "🎨 *Templates:*",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="Markdown",
            )

        elif query.data.startswith("tpl_"):
            style = query.data.replace("tpl_", "")
            ctx.user_data["template"] = style
            await query.edit_message_text(
                f"🎨 Template: *{style}*\n\n"
                "Agora descreva o vídeo:",
                parse_mode="Markdown",
            )
            ctx.user_data["mode"] = "chat"

        elif query.data == "effects":
            effects_list = self.effects.list()
            kb = []
            for i in range(0, len(effects_list), 3):
                row = [
                    InlineKeyboardButton(f"✨ {e}", callback_data=f"fx_{e}")
                    for e in effects_list[i:i+3]
                ]
                kb.append(row)
            kb.append([InlineKeyboardButton("⬅️ Voltar", callback_data="back")])
            await query.edit_message_text(
                "✨ *Efeitos Disponíveis:*\n\nEscolha para testar:",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="Markdown",
            )

        elif query.data.startswith("fx_"):
            effect = query.data.replace("fx_", "")
            await query.edit_message_text(
                f"✨ Efeito: *{effect}*\n\n"
                "Para usar este efeito, descreva um vídeo e peça para incluir o efeito.",
                parse_mode="Markdown",
            )

        elif query.data == "help":
            await query.edit_message_text(
                "📚 *Ajuda*\n\n"
                "*Modo Chat:*\n"
                "1. Clique em \"💬 Chat\"\n"
                "2. Digite o que quer\n"
                "3. Confirme e aguarde\n\n"
                "*Dicas:*\n"
                "• Seja específico\n"
                "• Mencione a plataforma\n"
                "• Peça efeitos específicos\n\n"
                "/clear - Limpar conversa",
                parse_mode="Markdown",
            )

        elif query.data == "back":
            await query.edit_message_text(
                "🎬 *Menu Principal*",
                reply_markup=self.keyboard_main(),
                parse_mode="Markdown",
            )

        elif query.data == "confirm":
            await self._generate_video(update, ctx)

        elif query.data == "cancel":
            ctx.user_data.clear()
            await query.edit_message_text(
                "❌ Cancelado.",
                reply_markup=self.keyboard_main(),
            )

    async def receive_message(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = update.message.text
        mode = ctx.user_data.get("mode", "chat")

        if mode == "images" and update.message.photo:
            await self._receive_photo(update, ctx)
            return

        if len(text) > 3000:
            text = text[:3000]
            await update.message.reply_text(
                "📝 Texto muito longo! Usei apenas os primeiros 3000 caracteres.\n\n"
                "💡 *Dica:* Descreva o vídeo de forma mais resumida.",
                parse_mode="Markdown",
            )

        await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        result = self.ai.chat(text, user_id)

        if result["success"]:
            data = result["data"]
            ctx.user_data["video_data"] = data

            understanding = data.get('understanding', '')
            if len(understanding) > 500:
                understanding = understanding[:500] + "..."

            msg = (
                f"✅ *Entendi!*\n\n"
                f"📝 {understanding}\n\n"
                f"🎬 *Plano:*\n"
                f"• Duração: {data.get('duration', '?')}s\n"
                f"• Estilo: {data.get('style', '?')}\n"
                f"• Cenas: {len(data.get('scenes', []))}\n"
                f"• Efeitos: {', '.join(data.get('effects', [])[:3])}\n"
            )

            suggestions = data.get("suggestions", [])
            if suggestions:
                msg += "\n💡 *Sugestões:*\n"
                for s in suggestions[:3]:
                    msg += f"• {s}\n"

            if len(msg) > 4000:
                msg = msg[:4000] + "\n\n..."

            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Criar", callback_data="confirm"),
                    InlineKeyboardButton("✏️ Editar", callback_data="chat"),
                ],
                [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")],
            ])

            await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
        else:
            error_msg = result.get('error', 'Desconhecido')
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "..."
            await update.message.reply_text(
                f"❌ Erro: {error_msg}\n\nTente novamente."
            )

    async def _receive_photo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        file = await photo.get_file()

        images = ctx.user_data.get("images", [])
        img_path = self.files.temp_path(f"img_{len(images)}", "jpg")
        await file.download_to_drive(img_path)
        images.append(img_path)
        ctx.user_data["images"] = images

        count = len(images)
        await update.message.reply_text(
            f"✅ Imagem {count} recebida!\n\n"
            "Envie mais ou *descreva o vídeo*.",
            parse_mode="Markdown",
        )

        if count >= 2:
            ctx.user_data["mode"] = "chat"

    async def _generate_video(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = ctx.user_data.get("video_data")
        if not data:
            await query.edit_message_text("❌ Dados perdidos. Comece novamente.")
            return

        await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VIDEO)
        await query.edit_message_text("⏳ *Criando vídeo...*", parse_mode="Markdown")

        try:
            output = self.files.output_path(f"video_{query.from_user.id}")

            images = ctx.user_data.get("images", [])

            result = self.pipeline.create_from_ai(
                video_data=data,
                output_path=output,
                images=images if images else None,
            )

            if result["success"]:
                await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)
                with open(output, "rb") as f:
                    caption = (
                        f"✅ *Vídeo Criado!*\n\n"
                        f"🎬 Duração: {data.get('duration', '?')}s\n"
                        f"🎨 Estilo: {data.get('style', '?')}\n"
                        f"⏱️ {result.get('processing_time', 0):.1f}s"
                    )
                    await query.message.reply_video(
                        video=f,
                        caption=caption,
                        parse_mode="Markdown",
                    )
                self.files.safe_delete(output)
                self.ai.clear(query.from_user.id)
            else:
                await query.edit_message_text(f"❌ Erro: {result.get('error')}")

        except Exception as e:
            logger.error(f"Erro: {e}")
            await query.edit_message_text(f"❌ Erro interno: {str(e)}")

        ctx.user_data.clear()

    async def cancel(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        ctx.user_data.clear()
        await update.message.reply_text(
            "❌ Cancelado.",
            reply_markup=self.keyboard_main(),
        )
        return WAITING

    async def clear(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        self.ai.clear(update.effective_user.id)
        ctx.user_data.clear()
        await update.message.reply_text("🧹 Conversa limpa!")


def setup(app: Application):
    bot = VideoBot()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", bot.start),
            CommandHandler("help", bot.help_cmd),
        ],
        states={
            WAITING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.receive_message),
                MessageHandler(filters.PHOTO, bot.receive_message),
                CallbackQueryHandler(bot.button_handler),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", bot.cancel),
            CommandHandler("clear", bot.clear),
            CommandHandler("start", bot.start),
        ],
    )

    app.add_handler(conv)
