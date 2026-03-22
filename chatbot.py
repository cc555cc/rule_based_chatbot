from response_database import BUSINESS_INFO, INTENT_KEYWORDS, MENU_ITEMS, RESERVATION_FIELD_KEYWORDS, NUMBER_WORDS
from booking_store import save_booking, save_delivery
from datetime import date, timedelta
import random


#called by UI
def generate_response(phrase):
    word_list = parse_phrase(phrase)
    intents = get_intent(phrase)
    if "reservation" in intents:
        return extract_reserve_detail(word_list)
    elif "menu" in intents:
        return "resource/menu.png"
    elif "delivery" in intents:
        return extract_delivery_detail(word_list)

    return get_response(intents)

def parse_phrase(phrase):
    parse_list = []

    #split the phrase into individual words and store them in a list.
    for word in phrase.lower().split():
        cleaned_word = word.strip(".,!?;:")
        if cleaned_word:
            parse_list.append(cleaned_word)

    return parse_list

def get_intent(phrase):
    word_list = parse_phrase(phrase)

    top_intent = top_level_intent(word_list)

    sub_intent = second_level_intent(top_intent, word_list)

    return [top_intent, sub_intent]

def top_level_intent(word_list):
    top_intent = ""

    for word in word_list:
        for category_name, subcategories in INTENT_KEYWORDS.items():
            for keywords in subcategories.values():
                if word in keywords:
                    top_intent = category_name
                    return top_intent

    return False
    
def second_level_intent(top_intent,word_list):
    if not top_intent:
        return False

    #if ask about operation/contact info --> just response with predefined restaurant info
    if top_intent in ["greeting", "operation", "contact"]:
        return top_intent

    #explore sub-intent if asking about services: delivery, menu, reservation
    if top_intent != "service":
        return False

    for word in word_list:
        for subcategory_name, keywords in INTENT_KEYWORDS[top_intent].items():
            if word in keywords:
                return subcategory_name

    return False

def extract_name(word_list, i, word, name_keywords):
    if i + 1 >= len(word_list) or word in NUMBER_WORDS:
        return ""

    if word in name_keywords["before"]:
        return word_list[i + 1]

    if word in name_keywords["after"] and i + 2 < len(word_list) and word_list[i + 1] in name_keywords["after"]:
        return word_list[i + 2]

    if word in name_keywords["after"]:
        return word_list[i + 1]

    return ""


def extract_party_size(word_list, i, word, party_size_keywords):
    if not (word.isdigit() or word in NUMBER_WORDS):
        return ""

    if i + 1 < len(word_list) and word_list[i + 1] in party_size_keywords["before"]:
        return word

    if i > 0 and word_list[i - 1] in party_size_keywords["after"]:
        return word

    return ""


def extract_time(word_list, i, word, time_keywords):
    if word in time_keywords["before"]:
        return is_time_value(word_list[i - 1]) if i > 0 else ""

    if word in time_keywords["after"]:
        return is_time_value(word_list[i + 1]) if i + 1 < len(word_list) else ""

    if word in time_keywords["noon"]:
        return word

    if word in time_keywords["unclear"]:
        return "unclear"

    return ""


def extract_date(word_list, i, word, date_keywords):
    if word in date_keywords["exact"]:
        return str(get_next_weekday_date(word))

    if word in date_keywords["after"] and i + 1 < len(word_list):
        return is_date_value(word_list[i + 1:])

    return ""


def extract_delivery_name(word_list, i, word):
    if word not in {"for", "name", "under"} or i + 1 >= len(word_list):
        return ""

    return word_list[i + 1]


def extract_delivery_address(word_list, i, word):
    if word not in {"to", "address", "at"} or i + 1 >= len(word_list):
        return ""

    address_words = []
    stop_words = {
        "at", "for", "on", "with",
        "today", "tomorrow", "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday",
    }

    for next_word in word_list[i + 1:]:
        if next_word in stop_words:
            break
        address_words.append(next_word)

    return " ".join(address_words)


def extract_delivery_phone(word):
    cleaned_word = word.replace("-", "").replace("(", "").replace(")", "")
    return word if cleaned_word.isdigit() and len(cleaned_word) >= 7 else ""


def extract_delivery_time(word_list, i, word):
    if word == "at":
        return is_time_value(word_list[i + 1:])

    return extract_time(word_list, i, word, RESERVATION_FIELD_KEYWORDS["time"])


def extract_delivery_order(word_list):
    menu_items = []

    for section_items in MENU_ITEMS.values():
        menu_items.extend(section_items)

    menu_items.sort(key=lambda item: len(item["name"].split()), reverse=True)

    order = []
    total = 0
    i = 0
    while i < len(word_list):
        matched_item = None

        for item in menu_items:
            item_words = item["name"].lower().split()
            item_length = len(item_words)

            if word_list[i:i + item_length] == item_words:
                matched_item = item
                break

        if matched_item:
            order.append(matched_item["name"])
            total += matched_item["price"]
            i += len(matched_item["name"].split())
            continue

        i += 1

    return order, total


def extract_reserve_detail(word_list):
    details = {
        "name": "",
        "time": "",
        "party_size": "",
        "date": "",
    }

    name_keywords = RESERVATION_FIELD_KEYWORDS["name"]
    party_size_keywords = RESERVATION_FIELD_KEYWORDS["party_size"]
    time_keywords = RESERVATION_FIELD_KEYWORDS["time"]
    date_keywords = RESERVATION_FIELD_KEYWORDS["date"]

    for i, word in enumerate(word_list):
        if details["name"] == "":
            details["name"] = extract_name(word_list, i, word, name_keywords)

        if details["party_size"] == "":
            details["party_size"] = extract_party_size(word_list, i, word, party_size_keywords)

        if details["time"] == "":
            details["time"] = extract_time(word_list, i, word, time_keywords)
            if details["time"] == "unclear":
                return "unclear"

        if details["date"] == "":
            details["date"] = extract_date(word_list, i, word, date_keywords)

    if "" not in details.values():
        save_booking(details["name"], details["party_size"], details["time"], details["date"])
        message = (
            f"We have reserved a table of {details['party_size']} under "
            f"{details['name']} on {details['date']} at {details['time']}."
        )
        return message

    return BUSINESS_INFO["service"]["details"]["reservation"]


def extract_delivery_detail(word_list):
    details = {
        "name": "",
        "address": "",
        "order": [],
        "total": 0,
    }

    for i, word in enumerate(word_list):
        if details["name"] == "":
            details["name"] = extract_delivery_name(word_list, i, word)

        if details["address"] == "":
            details["address"] = extract_delivery_address(word_list, i, word)

    details["order"], details["total"] = extract_delivery_order(word_list)

    if details["name"] and details["address"]:
        save_delivery(details["name"], details["address"], details["order"], details["total"])

        if details["order"]:
            order_text = ", ".join(details["order"])
            return (
                f"We have scheduled a delivery for {details['name']} to "
                f"{details['address']} with {order_text}. Total: ${details['total']:.2f}."
            )

        return f"We have scheduled a delivery for {details['name']} to {details['address']}."

    return BUSINESS_INFO["service"]["details"]["delivery"]

def is_time_value(text):
    if isinstance(text, list):
        text = " ".join(text)

    text = text.lower().strip()

    if text.isdigit():
        return text

    if text.endswith("am") or text.endswith("pm"):
        number_part = text[:-2]
        if number_part.isdigit():
            return text

    parts = text.split(":")
    if len(parts) == 2:
        hour, minute = parts

        if hour.isdigit() and minute.isdigit():
            return text

        if minute.endswith("am") or minute.endswith("pm"):
            minute_part = minute[:-2]
            if hour.isdigit() and minute_part.isdigit():
                return text

    return False

def is_date_value(text):
    if isinstance(text, list):
        text = " ".join(text)

    text = text.lower().strip(" ,.")

    valid_words = {
        "today", "tomorrow", "tonight", "weekend",
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    }

    if text in valid_words:
        return text

    parts = text.replace(",", "").split()
    month_names = {
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
    }

    if len(parts) == 2 and parts[0] in month_names:
        day = parts[1]
        if day.isdigit() and 1 <= int(day) <= 31:
            return text

    if len(parts) == 3 and parts[0] in month_names:
        day, year = parts[1], parts[2]
        if day.isdigit() and year.isdigit() and 1 <= int(day) <= 31:
            return text

    if "/" in text or "-" in text:
        separator = "/" if "/" in text else "-"
        parts = text.split(separator)
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            return text

    return False

def get_next_weekday_date(day_name):
    weekdays = {
        "tomorrow": -2,
        "today": -1,
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    today = date.today()
    if weekdays[day_name.lower()] == -1:
        return today
    elif weekdays[day_name.lower()] == -2:
        return today + timedelta(1)
    else:
        target_day = weekdays[day_name.lower()]
        days_ahead = (target_day - today.weekday()) % 7

        return today + timedelta(days=days_ahead)
def get_response(intents):
    top_intent, sub_intent = intents

    if top_intent == "greeting":
        return random.choice(BUSINESS_INFO["greeting"]["responses"])
    elif top_intent == "operation":
        return BUSINESS_INFO["operation"]["response"]
    elif top_intent == "contact":
        return BUSINESS_INFO["contact"]["response"]

    return "Sorry, I do not understand that yet."
