#this script is responsible for storing unrecognized user input and corresponding extracted intents for future model traning and improvement
from datetime import datetime
import json
from pathlib import Path

from learning_resource.response_database import STOP_WORDS,INTENT_KEYWORDS

BASE_DIR = Path(__file__).resolve().parent

def load_learned_entries():
    learned_entries = []

    try:
        with open(LEARNED_INTERACTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                    entry.setdefault("observation", 0)
                    learned_entries.append(entry)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass

    return learned_entries

LEARNED_INTERACTIONS_FILE = BASE_DIR / "learned_interactions.jsonl"
LEARNING_LOG_FILE = BASE_DIR / "learning_log.txt"

KNOWN_INTENT_WORDS = {
    keyword
    for category in INTENT_KEYWORDS.values()
    for keyword_list in category.values()
    for keyword in keyword_list
}

KNOWN_INTENT_TOKENS = {
    token
    for keyword in KNOWN_INTENT_WORDS
    for token in keyword.lower().split()
}

def normalize_learning_tokens(words):
    
    normalize_tokens = []

    for word in words:
        word = word.lower().strip('.,!?()[]{}"\'')

        if word.isdigit():
            normalize_tokens.append("<number>")
            continue
        elif word in STOP_WORDS:
            continue
        else: 
            normalize_tokens.append(word)
    
    return normalize_tokens

def parse_learning_phrase(phrase):
    parse_list = []

    for word in phrase.lower().split():
        cleaned_word = word.strip(".,!?;:").replace(".", "")
        if cleaned_word:
            parse_list.append(cleaned_word)

    return parse_list

def write_learning_log(word, original_phrase, top_intent, sub_intent):
    log_message = (
        f"Learned word: {word} | phrase: {original_phrase} | "
        f"top_intent: {top_intent} | sub_intent: {sub_intent}"
    )

    with open(LEARNING_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

#called by chatbot.py to learn unrecognized word
def appending_learning_entry(original_phrase, top_intent, sub_intent):
    parsed_phrase = parse_learning_phrase(original_phrase)
    has_known_intent_word = any(word in KNOWN_INTENT_TOKENS for word in parsed_phrase)
    normalized_phrase = normalize_learning_tokens(parse_learning_phrase(original_phrase))
    learned_entries = load_learned_entries()

    if not top_intent:
        return

    if top_intent != "service":
        sub_intent = False

    for word in normalized_phrase:
        if word not in KNOWN_INTENT_WORDS and word != "<number>":
            #check if the word is registerd in the learned interaction file, where "word" equal to the current word
            unrecognized_word_entry = None
            for entry in learned_entries:
                if entry["word"] == word:
                    unrecognized_word_entry = entry
                    break
        else:
            continue
        
        #if this word is registered, then updates the points of the associated intents in the entry
        if unrecognized_word_entry is not None:
            if top_intent not in unrecognized_word_entry["top_intent"]:
                unrecognized_word_entry["top_intent"][top_intent] = 1
            else:
                unrecognized_word_entry["top_intent"][top_intent] += 1

            if sub_intent:
                if sub_intent not in unrecognized_word_entry["sub_intent"]:
                    unrecognized_word_entry["sub_intent"][sub_intent] = 1
                else:
                    unrecognized_word_entry["sub_intent"][sub_intent] += 1
            if has_known_intent_word:
                unrecognized_word_entry["observation"] += 1
            unrecognized_word_entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
            write_learning_log(word, original_phrase, top_intent, sub_intent)
        else:
            #returns a json entry of the new word
            unrecognized_word_entry = add_new_keyword(
                word,
                top_intent,
                sub_intent,
                observation=1 if has_known_intent_word else 0,
            )
            learned_entries.append(unrecognized_word_entry)
            write_learning_log(word, original_phrase, top_intent, sub_intent)

    with open(LEARNED_INTERACTIONS_FILE, "w", encoding="utf-8") as f:
        for entry in learned_entries:
            f.write(json.dumps(entry) + "\n")


def add_new_keyword(word, top_intent, sub_intent, observation=0):
    associated_top_intent = {}
    associated_sub_intent = {}

    associated_top_intent[top_intent] = 1

    if top_intent == "service" and sub_intent:
        associated_sub_intent[sub_intent] = 1
    
    json_entry = {
        "word": word,
        "top_intent": associated_top_intent,
        "sub_intent": associated_sub_intent,
        "observation": observation,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    return json_entry

def predict_intent_from_learned_entries(current_phrase):
    normalized_phrase = normalize_learning_tokens(parse_learning_phrase(current_phrase))
    associated_top_intent_points = {}
    associated_sub_intent_points = {}
    learned_entries = load_learned_entries()
    
    for word in normalized_phrase:
        for entry in learned_entries:
            if entry["word"] == word:
                for intent, points in entry["top_intent"].items():
                    if intent in associated_top_intent_points:
                        associated_top_intent_points[intent] += points
                    else:
                        associated_top_intent_points[intent] = points

                for intent, points in entry["sub_intent"].items():
                    if intent in associated_sub_intent_points:
                        associated_sub_intent_points[intent] += points
                    else:
                        associated_sub_intent_points[intent] = points

    if associated_top_intent_points:
        predicted_top_intent = max(associated_top_intent_points, key=associated_top_intent_points.get)

        if predicted_top_intent == "service" and associated_sub_intent_points:
            predicted_sub_intent = max(associated_sub_intent_points, key=associated_sub_intent_points.get)
        else:
            predicted_sub_intent = False

        return [predicted_top_intent, predicted_sub_intent]

    return False

def train(sentence, top_intent, sub_intent=False):
    if top_intent != "service":
        sub_intent = False

    appending_learning_entry(sentence, top_intent, sub_intent)

    return {
        "sentence": sentence,
        "top_intent": top_intent,
        "sub_intent": sub_intent,
        "status": "trained",
    }

def write_to_response_database(word, top_intent, sub_intent):
    return 0

if __name__ == "__main__":
    from chatbot import get_intent

    training_files = ("training_sentence.txt", "training_sentences.txt")
    trained_count = 0
    skipped_count = 0
    training_file = None

    for candidate in training_files:
        try:
            with open(candidate, "r", encoding="utf-8"):
                training_file = candidate
                break
        except FileNotFoundError:
            continue

    if training_file is None:
        print("No training file found. Expected training_sentence.txt or training_sentences.txt")
    else:
        with open(training_file, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                sentence = None
                top_intent = None
                sub_intent = False

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    entry = None

                if isinstance(entry, dict):
                    sentence = entry.get("sentence")
                    top_intent = entry.get("top_intent")
                    sub_intent = entry.get("sub_intent", False)
                else:
                    delimiter = "\t" if "\t" in line else "|" if "|" in line else None
                    if delimiter:
                        parts = [part.strip() for part in line.split(delimiter)]
                        if len(parts) >= 2:
                            sentence = parts[0]
                            top_intent = parts[1]
                            if len(parts) >= 3 and parts[2]:
                                sub_intent = parts[2]
                    else:
                        sentence = line
                        top_intent, sub_intent = get_intent(sentence)

                if sentence and top_intent:
                    train(sentence, top_intent, sub_intent)
                    trained_count += 1
                else:
                    skipped_count += 1

        print(f"Training complete from {training_file}: trained={trained_count}, skipped={skipped_count}")

