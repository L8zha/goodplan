from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler, filters
)
from handlers import (
    start, exit_handler,
    to_add_menu, add_category, add_food_type,
    add_food_place_name, add_food_place_map,
    add_fun_place_name, add_fun_place_map,
    add_hotel_name, add_hotel_address, add_hotel_map,
    add_address_name, add_address_adr, add_address_map,
    to_view_menu, view_category, view_food_type, view_address_people,
    to_edit_menu, edit_category, edit_food_type, edit_choose_item, edit_input,
    START, MAIN_MENU, ADD_CATEGORY, ADD_FOOD_TYPE,
    ADD_PLACE_NAME, ADD_PLACE_MAP, ADD_FUN_PLACE_NAME, ADD_FUN_PLACE_MAP,
    ADD_HOTEL_NAME, ADD_HOTEL_ADDRESS, ADD_HOTEL_MAP,
    ADD_ADDRESS_NAME, ADD_ADDRESS_ADR, ADD_ADDRESS_MAP,
    VIEW_CATEGORY, VIEW_FOOD_TYPE, VIEW_ADDRESS_PEOPLE, VIEW_ADDRESS_PERSON,
    EDIT_CATEGORY, EDIT_FOOD_TYPE, EDIT_CHOOSE_ITEM, EDIT_INPUT
)

def main():
    app = Application.builder().token("7178929219:AAFXr4KOlPUUHBYxXTnTzF5iNG7t2s4AIM0").build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Выход$"), exit_handler),
        ],
        states={
            START: [
                MessageHandler(filters.Regex("^Старт$"), on_start_button),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            MAIN_MENU: [
                MessageHandler(filters.Regex("^Добавление$"), to_add_menu),
                MessageHandler(filters.Regex("^Просмотр$"), to_view_menu),
                MessageHandler(filters.Regex("^Редактирование$"), to_edit_menu),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_CATEGORY: [
                MessageHandler(filters.Regex("^(Еда|Развлечения|Отели|Адреса)$"), add_category),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_FOOD_TYPE: [
                MessageHandler(filters.Regex("^(Завтраки|Обеды|Ужины|Перекусить)$"), add_food_type),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_PLACE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_food_place_name),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_PLACE_MAP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_food_place_map),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_FUN_PLACE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_fun_place_name),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_FUN_PLACE_MAP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_fun_place_map),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_HOTEL_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_hotel_name),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_HOTEL_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_hotel_address),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_HOTEL_MAP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_hotel_map),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_ADDRESS_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_address_name),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_ADDRESS_ADR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_address_adr),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            ADD_ADDRESS_MAP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_address_map),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            VIEW_CATEGORY: [
                MessageHandler(filters.Regex("^(Еда|Развлечения|Отели|Адреса)$"), view_category),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            VIEW_FOOD_TYPE: [
                MessageHandler(filters.Regex("^(Завтраки|Обеды|Ужины|Перекусить)$"), view_food_type),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            VIEW_ADDRESS_PEOPLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, view_address_people),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            VIEW_ADDRESS_PERSON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, to_view_menu),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            EDIT_CATEGORY: [
                MessageHandler(filters.Regex("^(Еда|Развлечения|Отели|Адреса)$"), edit_category),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            EDIT_FOOD_TYPE: [
                MessageHandler(filters.Regex("^(Завтраки|Обеды|Ужины|Перекусить)$"), edit_food_type),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            EDIT_CHOOSE_ITEM: [
                MessageHandler(filters.Regex(r"^\d+$"), edit_choose_item),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
            EDIT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_input),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Выход$"), exit_handler)],
        allow_reentry=True
    )

    app.add_handler(conv)
    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()