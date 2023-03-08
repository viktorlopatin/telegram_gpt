ff = {
    'en': {
        "hello": "Hello, {name}! I am GptMagicianBot. A language model of artificial intelligence, designed to help and discuss with people. There is no physical form in management, but I am able to process and generate folk answers to various questions and tasks. How can I help you today?\n\nAlso, you can now use inline mode in chats",
        "wait": "Wait a second...",
        "answer_error": "An error occurred ((",
        "create_account_text": "Please activate the bot to use its functions",
        "create_account_button": "Go to the bot",
    },
    'uk': {
        "hello": "Привіт, {name}! Я — GptMagicianBot. Мовна модель штучного інтелекту, розроблена для допомоги людям і спілкування з ними. У мене немає фізичної форми, але я здатний обробляти та генерувати людські відповіді на різні запити та завдання. Як я можу вам допомогти сьогодні?\n\nТакож ви тепер можете використовувати inline режим в чатах.",
        "wait": "Зачекайте хвилинку...",
        "answer_error": "Сталася помилка ((",
        "create_account_text": "Будьласка активуйте бота щоб використовувати його функції",
        "create_account_button": "Перейти в бота",
    },
}


def f(lang, text_param, **kwargs):
    if lang == "ru":
        lang_func = "uk"
    else:
        lang_func = lang if lang in ff else 'en'
    tt = ff[lang_func][text_param]
    for k, v in kwargs.items():
        tt = tt.replace(f"{{{k}}}", v)
    return tt


