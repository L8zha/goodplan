from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from handlers import (
    start, exit_handler,
    to_add_menu, add_category, add_food_type, add_food_place_name, add_food_place_map,
    add_fun_place_name, add_fun_place_map, add_hotel_name, add_hotel_address, add_hotel_map,
    add_address_name, add_address_adr, add_address_map,
    to_view_menu, view_category, view_food_type, view_address_people,
    to_edit_menu, edit_category, edit_food_type, edit_choose_item, edit_input,
    back_to_main, to_add_menu, add_category, add_food_type, add_food_place_name, add_fun_place_name, add_hotel_name, add_address_name,
)

(
    START, MAIN_MENU, ADD_CATEGORY, ADD_FOOD_TYPE,
    ADD_PLACE_NAME, ADD_PLACE_MAP, ADD_FUN_PLACE_NAME, ADD_FUN_PLACE_MAP,
    ADD_HOTEL_NAME, ADD_HOTEL_ADDRESS, ADD_HOTEL_MAP,
    ADD_ADDRESS_NAME, ADD_ADDRESS_ADR, ADD_ADDRESS_MAP,
    VIEW_CATEGORY, VIEW_FOOD_TYPE, VIEW_ADDRESS_PEOPLE, VIEW_ADDRESS_PERSON,
    EDIT_CATEGORY, EDIT_FOOD_TYPE, EDIT_CHOOSE_ITEM, EDIT_INPUT,
) = range(22)

def main():
    application = ApplicationBuilder().token("7178929219:AAFXr4KOlPUUHBYxXTnTzF5iNG7t2s4AIM0").build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Regex("^Просмотр$"), to_view_menu),
                MessageHandler(filters.Regex("^Добавление$"), to_add_menu),
                MessageHandler(filters.Regex("^Редактирование$"), to_edit_menu),
                MessageHandler(filters.Regex("^Выход$"), exit_handler),
            ],

            # ADD section
            ADD_CATEGORY: [
                MessageHandler(filters.Regex("^Назад$"), back_to_main),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_category),
            ],
            ADD_FOOD_TYPE: [
                MessageHandler(filters.Regex("^Назад$"), to_add_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_food_type),
            ],
            ADD_PLACE_NAME: [
                MessageHandler(filters.Regex("^Назад$"), add_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_food_place_name),
            ],
            ADD_PLACE_MAP: [
                MessageHandler(filters.Regex("^Назад$"), add_food_place_name),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_food_place_map),
            ],
            ADD_FUN_PLACE_NAME: [
                MessageHandler(filters.Regex("^Назад$"), add_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_fun_place_name),
            ],
            ADD_FUN_PLACE_MAP: [
                MessageHandler(filters.Regex("^Назад$"), add_fun_place_name),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_fun_place_map),
            ],
            ADD_HOTEL_NAME: [
                MessageHandler(filters.Regex("^Назад$"), add_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_hotel_name),
            ],
            ADD_HOTEL_ADDRESS: [
                MessageHandler(filters.Regex("^Назад$"), add_hotel_name),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_hotel_address),
            ],
            ADD_HOTEL_MAP: [
                MessageHandler(filters.Regex("^Назад$"), add_hotel_address),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_hotel_map),
            ],
            ADD_ADDRESS_NAME: [
                MessageHandler(filters.Regex("^Назад$"), add_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_address_name),
            ],
            ADD_ADDRESS_ADR: [
                MessageHandler(filters.Regex("^Назад$"), add_address_name),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_address_adr),
            ],
            ADD_ADDRESS_MAP: [
                MessageHandler(filters.Regex("^Назад$"), add_address_adr),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_address_map),
            ],

            # VIEW section
            VIEW_CATEGORY: [
                MessageHandler(filters.Regex("^Назад$"), back_to_main),
                MessageHandler(filters.TEXT & ~filters.COMMAND, view_category),
            ],
            VIEW_FOOD_TYPE: [
                MessageHandler(filters.Regex("^Назад$"), view_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, view_food_type),
            ],
            VIEW_ADDRESS_PEOPLE: [
                MessageHandler(filters.Regex("^Назад$"), view_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, view_address_people),
            ],
            VIEW_ADDRESS_PERSON: [
                MessageHandler(filters.Regex("^Назад$"), view_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, view_address_people),  # или другой обработчик
            ],

            # EDIT section
            EDIT_CATEGORY: [
                MessageHandler(filters.Regex("^Назад$"), back_to_main),
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_category),
            ],
            EDIT_FOOD_TYPE: [
                MessageHandler(filters.Regex("^Назад$"), edit_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_food_type),
            ],
            EDIT_CHOOSE_ITEM: [
                MessageHandler(filters.Regex("^Назад$"), edit_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_choose_item),
            ],
            EDIT_INPUT: [
                MessageHandler(filters.Regex("^Назад$"), edit_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_input),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Выход$"), exit_handler),
        ],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()