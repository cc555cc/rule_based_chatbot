#this script contains the logic of the chatbot for generating response based on extracted intentions, 
#unknown word that presents in the query with known word will be learned and stored in learned_interaction.py
#failure to extract intentions will result in the chatbot guessing intention with unfamiliar word based on learned interactions.
#Finally, if guessing fail, the chatbot return generic response, telling the user that it do not understand the query.
from learning_resource.response_database import BUSINESS_INFO, INTENT_KEYWORDS, MENU_ITEMS, RESERVATION_FIELD_KEYWORDS, NUMBER_WORDS
from booking_store import save_booking, save_delivery
from datetime import date, timedelta
from learning_resource.model_learning import appending_learning_entry, predict_intent_from_learned_entries
from text_normalization import lemmatize_word, lemmatize_words
import random


MONTH_NAMES = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
}
NAME_PREFIX_WORDS = {"the", "a", "an", "name"}


#called by UI
def generate_response(phrase):
    word_list = parse_phrase(phrase)
    intents = get_intent(phrase)

    return get_response(phrase, intents)

def parse_phrase(phrase):
    parse_list = []

    #split the phrase into individual words and store them in a list.
    for word in phrase.lower().split():
        cleaned_word = word.strip(".,!?;:").replace(".", "")
        if cleaned_word:
            parse_list.append(cleaned_word)

    return parse_list

#procedure to extract intent from the conversation
def get_intent(phrase):
    word_list = parse_phrase(phrase)
    normalized_words = lemmatize_words(word_list)

    #determine the top intention: operation info, contact, service ...
    top_intent = top_level_intent(normalized_words)

    if not top_intent and has_reservation_signals(word_list):
        top_intent = "service"
        return [top_intent, "reservation"]

    #determine sub-level intention
    sub_intent = second_level_intent(top_intent, normalized_words)

    return [top_intent, sub_intent]

def top_level_intent(word_list):
    greeting_detected = False
    
    #extract the categories / subcategories name where the keyword was found in, which then represents the intention of the query
    for word in word_list:
        for category_name, subcategories in INTENT_KEYWORDS.items():
            for keywords in subcategories.values():
                normalized_keywords = [lemmatize_word(k) for k in keywords]
                if word in normalized_keywords:
                    if category_name == "greeting":
                        greeting_detected = True
                        continue

                    return category_name

    if greeting_detected:
        return "greeting"

    return False
    
def second_level_intent(top_intent, word_list):
    if not top_intent:
        return False

    #if ask about operation/contact info --> just response with predefined restaurant info
    if top_intent in ["greeting", "operation", "contact"]:
        return top_intent

    #explore sub-intention if asking about services: delivery, menu, reservation
    if top_intent != "service":
        return False

    for word in word_list:
        for subcategory_name, keywords in INTENT_KEYWORDS[top_intent].items():
            normalized_keywords = [lemmatize_word(keyword) for keyword in keywords]
            if word in normalized_keywords:
                return subcategory_name

    return False

#check if the query contains a reservation signal, return a boolean value that indicating whether the user is asking for reservation
def has_reservation_signals(word_list):
    if not word_list:
        return False

    if any(word in RESERVATION_FIELD_KEYWORDS["date"]["exact"] for word in word_list):
        return True

    if "on" in word_list or "under" in word_list or "people" in word_list or "person" in word_list:
        return True

    for i, word in enumerate(word_list):
        if word in {"for", "at"} and i + 1 < len(word_list):
            next_word = word_list[i + 1]
            if next_word.isdigit() or next_word in NUMBER_WORDS:
                return True

    return False

#extract reservation / delivery detail helper function
def extract_name(word_list, i, word, name_keywords):
    candidate_index = None

    #if the keyword implies that the name is likely to be the next word, check the next word as candidate
    if word in name_keywords["before"] and i + 1 < len(word_list):
        candidate_index = i + 1
    #if the keyword implies that the name is likely to be the previous word, check the previous word as candidate
    elif word in name_keywords["after"] and i + 1 < len(word_list):
        candidate_index = i + 1

    #quit if no candidate index is identified
    if candidate_index is None:
        return ""

    #skip common words that are unlikely to be part of the name
    while candidate_index < len(word_list) and word_list[candidate_index] in NAME_PREFIX_WORDS:
        candidate_index += 1

    #quit if we have reached the end of the word list without finding a valid candidate
    if candidate_index >= len(word_list):
        return ""

    #check if the candidate word is a number or a number word, which are unlikely to be part of the name
    candidate = word_list[candidate_index]
    if candidate.isdigit() or candidate in NUMBER_WORDS:
        return ""

    return candidate.title()


def extract_party_size(word_list, i, word, party_size_keywords):
    if not (word.isdigit() or word in NUMBER_WORDS):
        return ""

    #check if the word is likely to be the party size based on the presence of keywords that typically appear before or after the party size in a reservation query
    if i + 1 < len(word_list) and word_list[i + 1] in party_size_keywords["before"]:
        return word

    #check if the word is likely to be the party size based on the presence of keywords that typically appear before or after the party size in a reservation query
    if i > 0 and word_list[i - 1] in party_size_keywords["after"]:
        return word

    return ""


def extract_time(word_list, i, word, time_keywords):
    #check if the word is likely to be the time based on the presence of keywords that typically appear before or after the time in a reservation query
    if word in time_keywords["before"]:
        return is_time_value(word_list[i - 1]) if i > 0 else ""

    #check if the word is likely to be the time based on the presence of keywords that typically appear before or after the time in a reservation query
    if word in time_keywords["after"]:
        if i + 1 < len(word_list):
            next_word = is_time_value(word_list[i + 1])
            if next_word:
                return next_word

            return is_time_value(word_list[i + 1:i + 3])
        else:
            return ""

    #handle special cases where the time is expressed in a more casual way, such as "noon" or "midnight"
    if word in time_keywords["noon"]:
        return word

    #handle special cases where the time is expressed in a more casual way, such as "evening" or "tonight", which are often used to refer to an unclear time in the evening
    if word in time_keywords["unclear"]:
        return "unclear"

    return ""


def extract_date(word_list, i, word, date_keywords):
    #check if the word is likely to be the date based on the presence of keywords that typically appear before or after the date in a reservation query
    if word in date_keywords["exact"]:
        return str(get_next_weekday_date(word))

    #check if the word is likely to be the date based on the presence of keywords that typically appear before or after the date in a reservation query
    if word in date_keywords["after"] and i + 1 < len(word_list):
        max_end = min(len(word_list), i + 5)
        #if the keyword is "on", then check wether the next few words forms validate date expression
        for end in range(max_end, i + 1, -1):
            parsed_date = is_date_value(word_list[i + 1:end])
            if parsed_date:
                return parsed_date

    return ""


def extract_delivery_name(word_list, i, word):
    #check if the word is likely to be the name based on the presence of keywords that typically appear before or after the name in a delivery query
    if word not in {"for", "name", "under"} or i + 1 >= len(word_list):
        return ""

    return word_list[i + 1]


def extract_delivery_address(word_list, i, word):
    #check if the word is likely to be the address based on the presence of keywords that typically appear before or after the address in a delivery query
    if word not in {"to", "address", "at"} or i + 1 >= len(word_list):
        return ""

    address_words = []
    stop_words = {
        "at", "for", "on", "with",
        "today", "tomorrow", "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday",
    }

    #check the next few words after the keyword to see if they form a valid address
    for next_word in word_list[i + 1:]:
        #stop if the word match the ones in stop_words, which are unlikely to be part of the address and often indicate the end of the address in a delivery query
        if next_word in stop_words:
            break
        address_words.append(next_word)

    return " ".join(address_words)

#extract delivery time from query, handle both explicit time expression and more casual expression such as "tonight"
def extract_delivery_phone(word):
    cleaned_word = word.replace("-", "").replace("(", "").replace(")", "")
    return word if cleaned_word.isdigit() and len(cleaned_word) >= 7 else ""


def extract_delivery_time(word_list, i, word):
    if word == "at":
        return is_time_value(word_list[i + 1:])

    return extract_time(word_list, i, word, RESERVATION_FIELD_KEYWORDS["time"])

#extract dishes name from query and their price
def extract_delivery_order(word_list):
    menu_items = []

    #flatten the menu items into a single list and sort them by the number of words in their name in descending order to ensure that we match longer dish names before shorter ones
    for section_items in MENU_ITEMS.values():
        menu_items.extend(section_items)

    menu_items.sort(key=lambda item: len(item["name"].split()), reverse=True)

    order = []
    total = 0
    i = 0
    while i < len(word_list):
        matched_item = None

        #loop through menu item list to match with the words in query
        for item in menu_items:
            item_words = item["name"].lower().split()
            item_length = len(item_words)

            #if the current position in the word list matches the words of a menu item
            if word_list[i:i + item_length] == item_words:
                #add the item to the matched_item list
                matched_item = item
                break
        
        #if the list is not empty
        if matched_item:
            #add the items to the order list, add up their prices and move the index 
            #forward by the number of words in the matched item to continue searching for the next item in the query
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

    #loop through the words in query, extract the reservation details based on keywords read
    for i, word in enumerate(word_list):
        #extract name from the list, and set the name detail if extract_name returns a value
        if details["name"] == "":
            details["name"] = extract_name(word_list, i, word, name_keywords)

        #extract party size from the list, and set the party size detail if extract_party_size returns a value
        if details["party_size"] == "":
            details["party_size"] = extract_party_size(word_list, i, word, party_size_keywords)

        #extract time from the list, and set the time detail if extract_time returns a value
        if details["time"] == "":
            details["time"] = extract_time(word_list, i, word, time_keywords)
            #if the time is expressed in a more casual way such as "evening" or "tonight"
            if details["time"] == "unclear":
                return "unclear"

        #extract date from the list, and set the date detail if extract_date returns a value
        if details["date"] == "":
            extracted_date = extract_date(word_list, i, word, date_keywords)
            if extracted_date:
                details["date"] = extracted_date

    #if all fields of details are filled, save the booking and return confirmation message
    if all(details.values()):
        save_booking(details["name"], details["party_size"], details["time"], details["date"])
        message = (
            f"We have reserved a table of {details['party_size']} under "
            f"{details['name']} on {details['date']} at {details['time']}."
        )
        return message

    #otherwise, return generic response
    return BUSINESS_INFO["service"]["details"]["reservation"]


def extract_delivery_detail(word_list):
    details = {
        "name": "",
        "address": "",
        "order": [],
        "total": 0,
    }

    #loop through the words in query, extract the delivery details based on keywords read
    for i, word in enumerate(word_list):
        if details["name"] == "":
            details["name"] = extract_delivery_name(word_list, i, word)

        if details["address"] == "":
            details["address"] = extract_delivery_address(word_list, i, word)

    details["order"], details["total"] = extract_delivery_order(word_list)

    #if both name and address are extracted
    if details["name"] and details["address"]:
        save_delivery(details["name"], details["address"], details["order"], details["total"])

        #print the delivery details
        if details["order"]:
            order_text = ", ".join(details["order"])
            return (
                f"We have scheduled a delivery for {details['name']} to "
                f"{details['address']} with {order_text}. Total: ${details['total']:.2f}."
            )
        #print confirm message
        return f"We have scheduled a delivery for {details['name']} to {details['address']}."

    return BUSINESS_INFO["service"]["details"]["delivery"]

def is_time_value(text):
    #if time value is expressed in a list of words
    if isinstance(text, list):
        filtered_parts = [part for part in text if part not in {"the", "a", "an"}]
        #filter out common words that are not likely to form a time expression
        if not filtered_parts:
            return False
        text = " ".join(filtered_parts)

    #convert text to lowercase and strip leading/tailing for easier processing
    text = text.lower().strip()

    #case when time is expressed in a simple digit format
    if text.isdigit():
        return text

    #case when time is expressed with am/pm directly attached to the number
    if text.endswith("am") or text.endswith("pm"):
        #only check the part before am/pm
        number_part = text[:-2]
        if number_part.isdigit():
            return text

    #case when time is expressed in a more standard format with ":" separating hour and minute
    parts = text.split()
    #special case when time is expressed with am/pm without space
    if len(parts) == 2 and parts[0].isdigit() and parts[1] in {"am", "pm"}:
        return f"{parts[0]}{parts[1]}"

    #case when time is expressed in a more standard format with ":" 
    parts = text.split(":")
    #check if the time is expressed in valid formats
    if len(parts) == 2:
        hour, minute = parts
        #confirm that both hour and minute part are digits, or the minute part ends with am/pm and the rest are digits
        if hour.isdigit() and minute.isdigit():
            return text
        #case when minute part ends with am/pm
        if minute.endswith("am") or minute.endswith("pm"):
            minute_part = minute[:-2]
            if hour.isdigit() and minute_part.isdigit():
                return text

    return False

#check if a given text can be interpreted as a date value
def is_date_value(text):
    #check if the date value is expressed in a list of words
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

    #if the text is not one of the expected date expression, check if it contains month names and day numbers
    parts = text.replace(",", "").split()
    month_names = {
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
    }

    #check if the date is expressed in formats like "March 5" or "March 5, 2024"
    if len(parts) == 2 and parts[0] in month_names:
        day = parts[1]
        if day.isdigit() and 1 <= int(day) <= 31:
            return text

    #check if the date is expressed in formats like "5 March 2024"
    if len(parts) == 3 and parts[0] in month_names:
        day, year = parts[1], parts[2]
        if day.isdigit() and year.isdigit() and 1 <= int(day) <= 31:
            return text

    #check if the date is expressed in formats like "March 5" or "March 5, 2024" but with the month and day part switched, which is a common mistake people make when expressing date
    if len(parts) == 2 and parts[1] in month_names:
        day = parts[0]
        if day.isdigit() and 1 <= int(day) <= 31:
            return f"{parts[1]} {day}"

    #check if the date is expressed in formats like "5 March 2024" but with the month and day part switched, which is a common mistake people make when expressing date
    if len(parts) == 3 and parts[1] in month_names:
        day, year = parts[0], parts[2]
        if day.isdigit() and year.isdigit() and 1 <= int(day) <= 31:
            return f"{parts[1]} {day} {year}"
    
    #check if the date is expressed in formats like "2024-03-05" or "2024/03/05"
    if "/" in text or "-" in text:
        separator = "/" if "/" in text else "-"
        parts = text.split(separator)
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            return text

    return False

#return a date object based on the given day name
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
    #the phrase is today
    if weekdays[day_name.lower()] == -1:
        return today
    #the phrase is tomorrow
    elif weekdays[day_name.lower()] == -2:
        return today + timedelta(1)
    else:
        #add the number of days needed to reach the target weekday to today's date
        target_day = weekdays[day_name.lower()]
        days_ahead = (target_day - today.weekday()) % 7

        return today + timedelta(days=days_ahead)

def build_guess_message(top_intent, sub_intent):
    if top_intent == "service":
        if sub_intent == "reservation":
            return "I am guessing you are asking for a reservation."
        if sub_intent == "menu":
            return "I am guessing you want the restaurant menu."
        if sub_intent == "delivery":
            return "I am guessing you want restaurant delivery."

    if top_intent == "contact":
        return "I am guessing you want the restaurant contact information."
    if top_intent == "operation":
        if sub_intent == "address":
            return "I am guessing you want the restaurant address."
        if sub_intent == "time":
            return "I am guessing you are asking about the restaurant hours."
        return "I am guessing you want restaurant information."
    if top_intent == "greeting":
        return "I am guessing you are greeting the restaurant."

    return "I am guessing what you want based on what I learned before."

def format_guessed_response(response, top_intent, sub_intent):
    guess_message = build_guess_message(top_intent, sub_intent)

    if isinstance(response, list) and response:
        return [f"{guess_message}\n{response[0]}"] + response[1:]

    if isinstance(response, str):
        return f"{guess_message}\n{response}"

    return response

#generate response based on the extracted intent for
def get_response(original_phrase, intents, guessed_from_learning=False):
    top_intent, sub_intent = intents
    word_list = parse_phrase(original_phrase)

    #query is asking about service, extract detail
    if "reservation" in intents: 
        response = extract_reserve_detail(word_list)
        appending_learning_entry(original_phrase, top_intent, sub_intent)
        return format_guessed_response(response, top_intent, sub_intent) if guessed_from_learning else response
    elif "menu" in intents:
        response = ["Please check out our menu.", "resource/menu.png"]
        appending_learning_entry(original_phrase, top_intent, sub_intent)
        return format_guessed_response(response, top_intent, sub_intent) if guessed_from_learning else response
    elif "delivery" in intents:
        response = extract_delivery_detail(word_list)
        appending_learning_entry(original_phrase, top_intent, sub_intent)
        return format_guessed_response(response, top_intent, sub_intent) if guessed_from_learning else response
    else:
        if top_intent == "greeting":
            response = random.choice(BUSINESS_INFO["greeting"]["responses"])
            appending_learning_entry(original_phrase, top_intent, sub_intent)
            return format_guessed_response(response, top_intent, sub_intent) if guessed_from_learning else response
        elif top_intent == "operation":
            response = BUSINESS_INFO["operation"]["response"]
            appending_learning_entry(original_phrase, top_intent, sub_intent)
            return format_guessed_response(response, top_intent, sub_intent) if guessed_from_learning else response
        elif top_intent == "contact":
            response = BUSINESS_INFO["contact"]["response"]
            appending_learning_entry(original_phrase, top_intent, sub_intent)
            return format_guessed_response(response, top_intent, sub_intent) if guessed_from_learning else response
        else:
            predicted_intents = predict_intent_from_learned_entries(original_phrase)
            if predicted_intents:
                return get_response(original_phrase, predicted_intents, guessed_from_learning=True)

    return "Sorry, I do not understand that yet."
