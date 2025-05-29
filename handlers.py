import sqlite3
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
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
BACK_BUTTON = [["Назад"]]

def with_exit(keyboard):
    return keyboard + EXIT_BUTTON

def with_back(keyboard):
    return keyboard + BACK_BUTTON

async def send_and_track(update, context, *args, **kwargs):
    sent = await update.message.reply_text(*args, **kwargs)
    bot_msgs = context.user_data.setdefault("bot_messages", [])
    bot_msgs.append(sent.message_id)
    return sent

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup([["Просмотр", "Добавление", "Редактирование"], ["Выход"]], resize_keyboard=True)
    )
    return MAIN_MENU

async def exit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_msgs = context.user_data.get("bot_messages", [])
    for msg_id in bot_msgs:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
        except Exception:
            pass
    context.user_data["bot_messages"] = []
    await send_and_track(
        update, context,
        "Вы вышли из режима. Для возврата используйте /start.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ----------- BACK HANDLERS ------------

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start(update, context)

async def back_to_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что добавить?",
        reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
    )
    return ADD_CATEGORY

async def back_to_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что посмотреть?",
        reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
    )
    return VIEW_CATEGORY

async def back_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что редактировать?",
        reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
    )
    return EDIT_CATEGORY

# ------------- ADD -------------------

async def to_add_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что добавить?",
        reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
    )
    return ADD_CATEGORY

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text
    if cat == "Назад":
        return await back_to_main(update, context)
    context.user_data["add_category"] = cat
    if cat == "Еда":
        await send_and_track(
            update, context,
            "Тип еды:",
            reply_markup=ReplyKeyboardMarkup(with_back([FOOD_TYPES]), resize_keyboard=True)
        )
        return ADD_FOOD_TYPE
    elif cat == "Развлечения":
        context.user_data["add_subcat"] = None
        await send_and_track(
            update, context, "Название заведения и/или адрес:",
            reply_markup=ReplyKeyboardMarkup(with_back([]), resize_keyboard=True)
        )
        return ADD_FUN_PLACE_NAME
    elif cat == "Отели":
        await send_and_track(
            update, context, "Название отеля:",
            reply_markup=ReplyKeyboardMarkup(with_back([]), resize_keyboard=True)
        )
        return ADD_HOTEL_NAME
    elif cat == "Адреса":
        await send_and_track(
            update, context, "Имя:",
            reply_markup=ReplyKeyboardMarkup(with_back([]), resize_keyboard=True)
        )
        return ADD_ADDRESS_NAME
    else:
        return ADD_CATEGORY

async def add_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    typ = update.message.text
    if typ == "Назад":
        return await to_add_menu(update, context)
    context.user_data["add_subcat"] = typ
    await send_and_track(
        update, context, "Название заведения и/или адрес:",
        reply_markup=ReplyKeyboardMarkup(with_back([]), resize_keyboard=True)
    )
    return ADD_PLACE_NAME

async def add_food_place_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_category(update, context)
    context.user_data["add_name"] = update.message.text
    context.user_data["add_address"] = ""
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):",
        reply_markup=ReplyKeyboardMarkup(with_back([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_PLACE_MAP

async def add_food_place_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_food_place_name(update, context)
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    cat = context.user_data["add_category"]
    subcat = context.user_data["add_subcat"]
    name = context.user_data["add_name"]
    address = ""
    save_place(cat, subcat, name, address, map_url)
    await send_and_track(
        update, context, "Добавлено!",
        reply_markup=ReplyKeyboardMarkup([["Просмотр", "Добавление", "Редактирование"], ["Выход"]], resize_keyboard=True)
    )
    return MAIN_MENU

async def add_fun_place_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_category(update, context)
    context.user_data["add_name"] = update.message.text
    context.user_data["add_address"] = ""
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):",
        reply_markup=ReplyKeyboardMarkup(with_back([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_FUN_PLACE_MAP

async def add_fun_place_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_fun_place_name(update, context)
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    save_place("Развлечения", None, context.user_data["add_name"], "", map_url)
    await send_and_track(
        update, context, "Добавлено!",
        reply_markup=ReplyKeyboardMarkup([["Просмотр", "Добавление", "Редактирование"], ["Выход"]], resize_keyboard=True)
    )
    return MAIN_MENU

async def add_hotel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_category(update, context)
    context.user_data["add_name"] = update.message.text
    await send_and_track(
        update, context, "Адрес:",
        reply_markup=ReplyKeyboardMarkup(with_back([]), resize_keyboard=True)
    )
    return ADD_HOTEL_ADDRESS

async def add_hotel_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_hotel_name(update, context)
    context.user_data["add_address"] = update.message.text
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):",
        reply_markup=ReplyKeyboardMarkup(with_back([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_HOTEL_MAP

async def add_hotel_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_hotel_address(update, context)
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    save_place("Отели", None, context.user_data["add_name"], context.user_data["add_address"], map_url)
    await send_and_track(
        update, context, "Добавлено!",
        reply_markup=ReplyKeyboardMarkup([["Просмотр", "Добавление", "Редактирование"], ["Выход"]], resize_keyboard=True)
    )
    return MAIN_MENU

async def add_address_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_category(update, context)
    context.user_data["person"] = update.message.text
    await send_and_track(
        update, context, "Адрес:",
        reply_markup=ReplyKeyboardMarkup(with_back([]), resize_keyboard=True)
    )
    return ADD_ADDRESS_ADR

async def add_address_adr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_address_name(update, context)
    context.user_data["add_address"] = update.message.text
    await send_and_track(
        update, context, "Ссылка на карты (или 'Пропустить'):",
        reply_markup=ReplyKeyboardMarkup(with_back([["Пропустить"]]), resize_keyboard=True)
    )
    return ADD_ADDRESS_MAP

async def add_address_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        return await add_address_adr(update, context)
    if update.message.text == "Пропустить":
        map_url = ""
    else:
        map_url = update.message.text
    save_place("Адреса", None, "", context.user_data["add_address"], map_url, context.user_data["person"])
    await send_and_track(
        update, context, "Добавлено!",
        reply_markup=ReplyKeyboardMarkup([["Просмотр", "Добавление", "Редактирование"], ["Выход"]], resize_keyboard=True)
    )
    return MAIN_MENU

# --------------------- VIEW ------------------------------

async def to_view_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что посмотреть?",
        reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
    )
    return VIEW_CATEGORY

async def view_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text
    if cat == "Назад":
        return await back_to_main(update, context)
    context.user_data["view_category"] = cat
    if cat == "Еда":
        await send_and_track(
            update, context, "Тип еды:", reply_markup=ReplyKeyboardMarkup(with_back([FOOD_TYPES]), resize_keyboard=True)
        )
        return VIEW_FOOD_TYPE
    elif cat == "Развлечения":
        rows = get_places("Развлечения")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
            return VIEW_CATEGORY
        for r in rows:
            fields = []
            if r[1]:
                fields.append(f"(!)Адрес или название: {r[1]}")
            if r[3]:
                fields.append(f"(!)Ссылка на карты: {r[3]}")
            await send_and_track(
                update, context, "\n".join(fields), reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
        return VIEW_CATEGORY
    elif cat == "Отели":
        rows = get_places("Отели")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
            return VIEW_CATEGORY
        for r in rows:
            fields = []
            if r[1]:
                fields.append(f"(!)Адрес или название: {r[1]}")
            if r[3]:
                fields.append(f"(!)Ссылка на карты: {r[3]}")
            await send_and_track(
                update, context, "\n".join(fields), reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
        return VIEW_CATEGORY
    elif cat == "Адреса":
        people = get_people_with_addresses()
        if not people:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
            return VIEW_CATEGORY
        await send_and_track(
            update, context, "Кто?", reply_markup=ReplyKeyboardMarkup(with_back([[p] for p in people]), resize_keyboard=True)
        )
        return VIEW_ADDRESS_PEOPLE

async def view_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subcat = update.message.text
    if subcat == "Назад":
        return await view_category(update, context)
    rows = get_places("Еда", subcat)
    if not rows:
        await send_and_track(
            update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([FOOD_TYPES]), resize_keyboard=True)
        )
        return VIEW_FOOD_TYPE
    for r in rows:
        fields = []
        if r[1]:
            fields.append(f"(!)Адрес или название: {r[1]}")
        if r[3]:
            fields.append(f"(!)Ссылка на карты: {r[3]}")
        await send_and_track(
            update, context, "\n".join(fields), reply_markup=ReplyKeyboardMarkup(with_back([FOOD_TYPES]), resize_keyboard=True)
        )
    return VIEW_FOOD_TYPE

async def view_address_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    person = update.message.text
    if person == "Назад":
        return await view_category(update, context)
    info = get_address_by_person(person)
    if not info:
        await send_and_track(
            update, context, "Нет информации.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
        )
        return VIEW_CATEGORY
    fields = []
    if info[0]:
        fields.append(f"(!)Адрес или название: {info[0]}")
    if info[2]:
        fields.append(f"(!)Ссылка на карты: {info[2]}")
    await send_and_track(
        update, context, "\n".join(fields), reply_markup=ReplyKeyboardMarkup(with_back([[person]]), resize_keyboard=True)
    )
    return VIEW_ADDRESS_PERSON

# ------------------------ EDIT -----------------------------

async def to_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_track(
        update, context,
        "Что редактировать?",
        reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
    )
    return EDIT_CATEGORY

async def edit_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text
    if cat == "Назад":
        return await back_to_main(update, context)
    context.user_data["edit_category"] = cat
    if cat == "Еда":
        await send_and_track(
            update, context, "Тип еды:", reply_markup=ReplyKeyboardMarkup(with_back([FOOD_TYPES]), resize_keyboard=True)
        )
        return EDIT_FOOD_TYPE
    elif cat == "Развлечения":
        rows = get_places("Развлечения")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
            return EDIT_CATEGORY
        context.user_data["edit_rows"] = rows
        txt = "\n".join([f"{i+1}. {r[1]}" for i, r in enumerate(rows)])
        await send_and_track(
            update, context, txt + "\nВведите номер для редактирования:",
            reply_markup=ReplyKeyboardMarkup(with_back([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
        )
        return EDIT_CHOOSE_ITEM
    elif cat == "Отели":
        rows = get_places("Отели")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
            return EDIT_CATEGORY
        context.user_data["edit_rows"] = rows
        txt = "\n".join([f"{i+1}. {r[1]}" for i, r in enumerate(rows)])
        await send_and_track(
            update, context, txt + "\nВведите номер для редактирования:",
            reply_markup=ReplyKeyboardMarkup(with_back([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
        )
        return EDIT_CHOOSE_ITEM
    elif cat == "Адреса":
        rows = get_places("Адреса")
        if not rows:
            await send_and_track(
                update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
            )
            return EDIT_CATEGORY
        context.user_data["edit_rows"] = rows
        txt = "\n".join([f"{i+1}. {r[4]}" for i, r in enumerate(rows)])
        await send_and_track(
            update, context, txt + "\nВведите номер для редактирования:",
            reply_markup=ReplyKeyboardMarkup(with_back([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
        )
        return EDIT_CHOOSE_ITEM

async def edit_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subcat = update.message.text
    if subcat == "Назад":
        return await edit_category(update, context)
    rows = get_places("Еда", subcat)
    if not rows:
        await send_and_track(
            update, context, "Ничего не найдено.", reply_markup=ReplyKeyboardMarkup(with_back([FOOD_TYPES]), resize_keyboard=True)
        )
        return EDIT_FOOD_TYPE
    context.user_data["edit_rows"] = rows
    txt = "\n".join([f"{i+1}. {r[1]}" for i, r in enumerate(rows)])
    await send_and_track(
        update, context, txt + "\nВведите номер для редактирования:",
        reply_markup=ReplyKeyboardMarkup(with_back([[str(i+1)] for i in range(len(rows))]), resize_keyboard=True)
    )
    return EDIT_CHOOSE_ITEM

async def edit_choose_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Назад":
        return await edit_category(update, context)
    try:
        num = int(text) - 1
        row = context.user_data["edit_rows"][num]
    except (ValueError, IndexError):
        await send_and_track(
            update, context, "Некорректный номер. Попробуйте ещё раз.",
            reply_markup=ReplyKeyboardMarkup(with_back([[str(i+1)] for i in range(len(context.user_data['edit_rows']))]), resize_keyboard=True)
        )
        return EDIT_CHOOSE_ITEM
    place_id = row[0]
    context.user_data["edit_place_id"] = place_id
    place = get_place_by_id(place_id)
    # Формируем строку для редактирования
    if place[1] == "Адреса":
        edit_str = f"{place[6] or ''}::{place[3] or ''}::{place[5] or ''}"
        await update.message.reply_text(
            f"Измените данные (имя::адрес::ссылка):\n{edit_str}",
            reply_markup=ForceReply(selective=False)
        )
    else:
        edit_str = f"{place[3] or ''}::{place[4] or ''}::{place[5] or ''}"
        await update.message.reply_text(
            f"Измените данные (название::адрес::ссылка):\n{edit_str}",
            reply_markup=ForceReply(selective=False)
        )
    context.user_data["edit_prev"] = edit_str
    return EDIT_INPUT

async def edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Назад":
        # Назад возвращает к выбору номера
        return await edit_category(update, context)
    place_id = context.user_data.get("edit_place_id")
    if not place_id:
        await send_and_track(
            update, context, "Ошибка. Попробуйте заново.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
        )
        return EDIT_CATEGORY
    prev = context.user_data.get("edit_prev", "")
    if text == prev:
        # ничего не изменилось
        await send_and_track(
            update, context, "Данные не изменены.", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
        )
        return EDIT_CATEGORY
    place = get_place_by_id(place_id)
    if place[1] == "Адреса":
        parts = text.split("::")
        if len(parts) < 2:
            await update.message.reply_text(
                "Введите в формате: имя::адрес::ссылка",
                reply_markup=ForceReply(selective=False)
            )
            return EDIT_INPUT
        name, address = parts[0], parts[1]
        map_url = parts[2] if len(parts) > 2 else ""
        person = name
        update_place(place_id, name, address, map_url, person)
    else:
        parts = text.split("::")
        if len(parts) < 1:
            await update.message.reply_text(
                "Введите в формате: название::адрес::ссылка",
                reply_markup=ForceReply(selective=False)
            )
            return EDIT_INPUT
        name = parts[0]
        address = parts[1] if len(parts) > 1 else ""
        map_url = parts[2] if len(parts) > 2 else ""
        update_place(place_id, name, address, map_url, None)
    await send_and_track(
        update, context, "Сохранено!", reply_markup=ReplyKeyboardMarkup(with_back([CATEGORIES]), resize_keyboard=True)
    )
    return EDIT_CATEGORY