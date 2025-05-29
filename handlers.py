import sqlite3
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

(
    START, MAIN_MENU, ADD_CATEGORY, ADD_FOOD_TYPE,
    ADD_PLACE_NAME, ADD_PLACE_MAP, ADD_FUN_PLACE_NAME, ADD_FUN_PLACE_MAP,
    ADD_HOTEL_NAME, ADD_HOTEL_ADDRESS, ADD_HOTEL_MAP,
    ADD_ADDRESS_NAME, ADD_ADDRESS_ADR, ADD_ADDRESS_MAP,
    VIEW_CATEGORY, VIEW_FOOD_TYPE, VIEW_ADDRESS_PEOPLE, VIEW_ADDRESS_PERSON,
    EDIT_CATEGORY, EDIT_FOOD_TYPE, EDIT_CHOOSE_ITEM, EDIT_INPUT,
) = range(22)

FOOD_TYPES = ["Завтраки", "Обеды", "Ужины", "Перекусить"]
CATEGORIES = ["Еда", "Развлечения", "Отели", "Адреса"]

def get_db():
    conn = sqlite3.connect("places.sqlite")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            subcategory TEXT,
            name TEXT,
            address TEXT,
            map_url TEXT,
            person TEXT
        )
    ''')
    conn.commit()
    return conn

def save_place(category, subcategory, name, address, map_url, person=None):
    conn = get_db()
    conn.execute("INSERT INTO places (category, subcategory, name, address, map_url, person) VALUES (?, ?, ?, ?, ?, ?)",
                 (category, subcategory, name, address, map_url, person))
    conn.commit()
    conn.close()

def get_places(category, subcategory=None):
    conn = get_db()
    if subcategory:
        rows = conn.execute("SELECT id, name, address, map_url, person FROM places WHERE category=? AND subcategory=?",
                            (category, subcategory)).fetchall()
    else:
        rows = conn.execute("SELECT id, name, address, map_url, person FROM places WHERE category=?", (category,)).fetchall()
    conn.close()
    return rows

def get_place_by_id(place_id):
    conn = get_db()
    row = conn.execute("SELECT id, category, subcategory, name, address, map_url, person FROM places WHERE id=?", (place_id,)).fetchone()
    conn.close()
    return row

def update_place(place_id, name, address, map_url, person):
    conn = get_db()
    conn.execute("UPDATE places SET name=?, address=?, map_url=?, person=? WHERE id=?", (name, address, map_url, person, place_id))
    conn.commit()
    conn.close()

def get_people_with_addresses():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT person FROM places WHERE category='Адреса' AND person IS NOT NULL").fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

def get_address_by_person(person):
    conn = get_db()
    row = conn.execute("SELECT name, address, map_url FROM places WHERE category='Адреса' AND person=?", (person,)).fetchone()
    conn.close()
    return row

def clear_all():
    conn = get_db()
    conn.execute("DELETE FROM places")
    conn.commit()
    conn.close()

EXIT_BUTTON = [["Выход"]]

def with_exit(keyboard):
    return keyboard + EXIT_BUTTON

async def send_and_track(update, context, *args, **kwargs):
    # Отправляет сообщение и сохраняет его message_id для последующего удаления
    sent = await update.message.reply_text(*args, **kwargs)
    bot_msgs = context.user_data.setdefault("bot_messages", [])
    bot_msgs.append(sent.message_id)
    return sent

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Нажмите 'Старт' для начала",
        reply_markup=ReplyKeyboardMarkup([["Старт"], ["Выход"]], resize_keyboard=True)
    )
    return START

async def exit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_msgs = context.user_data.get("bot_messages", [])
    for msg_id in bot_msgs:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
        except Exception:
            pass  # уже удалено или нет прав
    context.user_data["bot_messages"] = []
    await send_and_track(
        update, context,
        "Вы вышли из режима. Для возврата используйте /start.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def on_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(with_exit([["Просмотр", "Добавление", "Редактирование"]]), resize_keyboard=True)
    )
    return MAIN_MENU

async def to_add_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что добавить?",
        reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return ADD_CATEGORY

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text
    context.user_data["add_category"] = cat
    if cat == "Еда":
        await send_and_track(
            update, context,
            "Тип еды:",
            reply_markup=ReplyKeyboardMarkup(with_exit([FOOD_TYPES]), resize_keyboard=True)
        )
        return ADD_FOOD_TYPE
    elif cat == "Развлечения":
        context.user_data["add_subcat"] = None
        await send_and_track(
            update, context, "Название заведения и/или адрес:"
        )
        return ADD_FUN_PLACE_NAME
    elif cat == "Отели":
        await send_and_track(
            update, context, "Название отеля:"
        )
        return ADD_HOTEL_NAME
    elif cat == "Адреса":
        await send_and_track(
            update, context, "Имя:"
        )
        return ADD_ADDRESS_NAME
    else:
        return ADD_CATEGORY

async def add_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    typ = update.message.text
    context.user_data["add_subcat"] = typ
    await send_and_track(
        update, context, "Название заведения и/или адрес:"
    )
    return ADD_PLACE_NAME

async def add_food_place_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_name"] = update.message.text
    context.user_data["add_address"] = ""
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):", reply_markup=ReplyKeyboardMarkup(with_exit([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_PLACE_MAP

async def add_food_place_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    cat = context.user_data["add_category"]
    subcat = context.user_data["add_subcat"]
    name = context.user_data["add_name"]
    address = ""  # адреса нет отдельно
    save_place(cat, subcat, name, address, map_url)
    await send_and_track(
        update, context, "Добавлено!", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return ADD_CATEGORY

async def add_fun_place_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_name"] = update.message.text
    context.user_data["add_address"] = ""
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):", reply_markup=ReplyKeyboardMarkup(with_exit([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_FUN_PLACE_MAP

async def add_fun_place_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    save_place("Развлечения", None, context.user_data["add_name"], "", map_url)
    await send_and_track(
        update, context, "Добавлено!", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return ADD_CATEGORY

async def add_hotel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_name"] = update.message.text
    await send_and_track(
        update, context, "Адрес:"
    )
    return ADD_HOTEL_ADDRESS

async def add_hotel_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_address"] = update.message.text
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):", reply_markup=ReplyKeyboardMarkup(with_exit([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_HOTEL_MAP

async def add_hotel_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    save_place("Отели", None, context.user_data["add_name"], context.user_data["add_address"], map_url)
    await send_and_track(
        update, context, "Добавлено!", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return ADD_CATEGORY

async def add_address_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["person"] = update.message.text
    await send_and_track(
        update, context, "Адрес:"
    )
    return ADD_ADDRESS_ADR

async def add_address_adr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_address"] = update.message.text
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):", reply_markup=ReplyKeyboardMarkup(with_exit([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_ADDRESS_MAP

async def add_address_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    save_place("Адреса", None, "", context.user_data["add_address"], map_url, context.user_data["person"])
    await send_and_track(
        update, context, "Добавлено!", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return ADD_CATEGORY

async def to_view_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что посмотреть?",
        reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return VIEW_CATEGORY

async def view_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text
    context.user_data["view_category"] = cat
    if cat == "Еда":
        await send_and_track(
            update, context, "Тип еды:", reply_markup=ReplyKeyboardMarkup(with_exit([FOOD_TYPES]), resize_keyboard=True)
        )
        return VIEW_FOOD_TYPE
    elif cat == "Развлечения":
        rows = get_places("Развлечения")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
            )
            return VIEW_CATEGORY
        txt = "\n".join([f"{r[1]}{'' if not r[2] else ' ('+r[2]+')'}{'' if not r[3] else ' — '+r[3]}" for r in rows])
        await send_and_track(
            update, context, txt, reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
        )
        return VIEW_CATEGORY
    elif cat == "Отели":
        rows = get_places("Отели")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
            )
            return VIEW_CATEGORY
        txt = "\n".join([f"{r[1]}{'' if not r[2] else ' ('+r[2]+')'}{'' if not r[3] else ' — '+r[3]}" for r in rows])
        await send_and_track(
            update, context, txt, reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
        )
        return VIEW_CATEGORY
    elif cat == "Адреса":
        people = get_people_with_addresses()
        if not people:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
            )
            return VIEW_CATEGORY
        await send_and_track(
            update, context, "Кто?", reply_markup=ReplyKeyboardMarkup(with_exit([[p] for p in people]), resize_keyboard=True)
        )
        return VIEW_ADDRESS_PEOPLE

async def view_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subcat = update.message.text
    rows = get_places("Еда", subcat)
    if not rows:
        await send_and_track(
            update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([FOOD_TYPES]), resize_keyboard=True)
        )
        return VIEW_FOOD_TYPE
    txt = "\n".join([f"{r[1]}{'' if not r[2] else ' ('+r[2]+')'}{'' if not r[3] else ' — '+r[3]}" for r in rows])
    await send_and_track(
        update, context, txt, reply_markup=ReplyKeyboardMarkup(with_exit([FOOD_TYPES]), resize_keyboard=True)
    )
    return VIEW_FOOD_TYPE

async def view_address_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    person = update.message.text
    info = get_address_by_person(person)
    if not info:
        await send_and_track(
            update, context, "Нет информации.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
        )
        return VIEW_CATEGORY
    txt = f"{person}:\nАдрес: {info[1]}\n{'Ссылка: '+info[2] if info[2] else ''}"
    await send_and_track(
        update, context, txt, reply_markup=ReplyKeyboardMarkup(with_exit([[person]]), resize_keyboard=True)
    )
    return VIEW_ADDRESS_PERSON

async def to_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что редактировать?",
        reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return EDIT_CATEGORY

async def edit_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text
    context.user_data["edit_category"] = cat
    if cat == "Еда":
        await send_and_track(
            update, context, "Тип еды:", reply_markup=ReplyKeyboardMarkup(with_exit([FOOD_TYPES]), resize_keyboard=True)
        )
        return EDIT_FOOD_TYPE
    elif cat == "Развлечения":
        rows = get_places("Развлечения")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
            )
            return EDIT_CATEGORY
        context.user_data["edit_rows"] = rows
        txt = "\n".join([f"{i+1}. {r[1]}" for i, r in enumerate(rows)])
        await send_and_track(
            update, context, txt + "\nВведите номер для редактирования:", reply_markup=ReplyKeyboardMarkup(with_exit([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
        )
        return EDIT_CHOOSE_ITEM
    elif cat == "Отели":
        rows = get_places("Отели")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
            )
            return EDIT_CATEGORY
        context.user_data["edit_rows"] = rows
        txt = "\n".join([f"{i+1}. {r[1]}" for i, r in enumerate(rows)])
        await send_and_track(
            update, context, txt + "\nВведите номер для редактирования:", reply_markup=ReplyKeyboardMarkup(with_exit([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
        )
        return EDIT_CHOOSE_ITEM
    elif cat == "Адреса":
        rows = get_places("Адреса")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
            )
            return EDIT_CATEGORY
        context.user_data["edit_rows"] = rows
        txt = "\n".join([f"{i+1}. {r[4]}" for i, r in enumerate(rows)])
        await send_and_track(
            update, context, txt + "\nВведите номер для редактирования:", reply_markup=ReplyKeyboardMarkup(with_exit([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
        )
        return EDIT_CHOOSE_ITEM

async def edit_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subcat = update.message.text
    rows = get_places("Еда", subcat)
    if not rows:
        await send_and_track(
            update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_exit([FOOD_TYPES]), resize_keyboard=True)
        )
        return EDIT_FOOD_TYPE
    context.user_data["edit_rows"] = rows
    txt = "\n".join([f"{i+1}. {r[1]}" for i, r in enumerate(rows)])
    await send_and_track(
        update, context, txt + "\nВведите номер для редактирования:", reply_markup=ReplyKeyboardMarkup(with_exit([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
    )
    return EDIT_CHOOSE_ITEM

async def edit_choose_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = int(update.message.text) - 1
        row = context.user_data["edit_rows"][num]
    except (ValueError, IndexError):
        await send_and_track(
            update, context, "Некорректный номер. Попробуйте ещё раз."
        )
        return EDIT_CHOOSE_ITEM
    place_id = row[0]
    context.user_data["edit_place_id"] = place_id
    place = get_place_by_id(place_id)
    if place[1] == "Адреса":
        await send_and_track(
            update, context,
            f"Редактируйте (имя::адрес::ссылка):\n{place[6]}::{place[3]}::{place[5]}",
            reply_markup=ReplyKeyboardMarkup(with_exit([["Сохранить"]]), resize_keyboard=True)
        )
    else:
        await send_and_track(
            update, context,
            f"Редактируйте (название::адрес::ссылка):\n{place[3]}::{place[4]}::{place[5]}",
            reply_markup=ReplyKeyboardMarkup(with_exit([["Сохранить"]]), resize_keyboard=True)
        )
    return EDIT_INPUT

async def edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    place_id = context.user_data.get("edit_place_id")
    if not place_id:
        await send_and_track(
            update, context, "Ошибка. Попробуйте заново.", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
        )
        return EDIT_CATEGORY
    if text == "Сохранить":
        await send_and_track(
            update, context, "Сначала отредактируйте данные и отправьте их."
        )
        return EDIT_INPUT
    place = get_place_by_id(place_id)
    if place[1] == "Адреса":
        parts = text.split("::")
        if len(parts) < 2:
            await send_and_track(
                update, context, "Введите в формате: имя::адрес::ссылка"
            )
            return EDIT_INPUT
        name, address = parts[0], parts[1]
        map_url = parts[2] if len(parts) > 2 else ""
        person = name
        update_place(place_id, name, address, map_url, person)
    else:
        parts = text.split("::")
        if len(parts) < 1:
            await send_and_track(
                update, context, "Введите в формате: название::адрес::ссылка"
            )
            return EDIT_INPUT
        name = parts[0]
        address = parts[1] if len(parts) > 1 else ""
        map_url = parts[2] if len(parts) > 2 else ""
        update_place(place_id, name, address, map_url, None)
    await send_and_track(
        update, context, "Сохранено!", reply_markup=ReplyKeyboardMarkup(with_exit([CATEGORIES]), resize_keyboard=True)
    )
    return EDIT_CATEGORY