# Rule-Based Restaurant Chatbot

This project is a restaurant chatbot that uses a rule-based intent system instead of a trained large language model. Its behavior is driven by keyword dictionaries, branching logic, and field extraction rules defined in `chatbot.py` and `response_database.py`.

It now also includes a lightweight self-learning layer. The chatbot stores successful interactions in `learned_interactions.jsonl` and can reuse similar past phrasing to recover an intent when the fixed keyword rules alone would otherwise fail.

## How The Chatbot Works

At a high level, each user message goes through this pipeline:

1. The message is cleaned and split into words.
2. Words are normalized with lemmatization.
3. The chatbot chooses a top-level intent such as `greeting`, `operation`, `contact`, or `service`.
4. If the top-level intent is `service`, it chooses a sub-intent such as `reservation`, `menu`, or `delivery`.
5. If needed, the chatbot extracts details from the message, such as reservation name, date, time, party size, or delivery address.
6. It returns a fixed response, a menu image, or a booking/delivery confirmation.

## Method 1: Lemmatization

Lemmatization is implemented with NLTK's `WordNetLemmatizer` in `chatbot.py`.

### What it does

Lemmatization reduces different forms of a word to a simpler base form so the chatbot can match more user inputs with fewer keywords.

Examples:

- `booking` can be reduced toward `book`
- `delivered` can be reduced toward `deliver`
- `drinks` can be reduced toward `drink`

### How it is implemented

The code defines:

- `lemmatize_word(word)` in `chatbot.py`
- `lemmatize_words(word_list)` in `chatbot.py`

The implementation lemmatizes each token twice:

- first as a noun
- then as a verb

This helps the chatbot normalize common restaurant-related words before intent matching.

### Where it is used

After the user message is parsed, `get_intent()` creates `normalized_words` by calling `lemmatize_words(...)` in `chatbot.py`. Those normalized words are then compared against normalized keyword lists inside:

- `top_level_intent()` in `chatbot.py`
- `second_level_intent()` in `chatbot.py`

### Why it matters

Without lemmatization, the chatbot would need many more keyword variants. With lemmatization, it can recognize related word forms using a smaller keyword dictionary.

## Method 2: Decision Tree Style Logic

This project does not use a trained machine learning decision tree classifier. Instead, it uses a hand-written decision flow that behaves like a small decision tree: the program checks a series of conditions and branches into the next step based on what it finds.

That branching flow is mainly implemented in:

- `generate_response()` in `chatbot.py`
- `get_intent()` in `chatbot.py`
- `top_level_intent()` in `chatbot.py`
- `second_level_intent()` in `chatbot.py`

### Decision flow

The chatbot follows this branching logic:

1. Parse the message into words.
2. Lemmatize the words.
3. Search for a top-level intent using `INTENT_KEYWORDS` from `response_database.py`.
4. If no direct top-level intent is found, check for reservation-specific signals using `has_reservation_signals()` in `chatbot.py`.
5. If the top-level intent is `service`, search for the matching sub-intent.
6. Based on the chosen intent, route the message to the correct response path:
   - reservation extraction
   - delivery extraction
   - menu image response
   - fixed business information response
   - fallback response

### Why this is like a decision tree

It is called "decision tree style" because the chatbot makes one decision after another:

- first `What broad category is this?`
- then `What specific service is it about?`
- then `Do we have enough details to complete the action?`

Each answer determines the next branch in the code.

### Reservation branch

If the service is a reservation, the chatbot tries to extract:

- customer name
- party size
- date
- time

This logic is handled by helper functions such as:

- `extract_name()` in `chatbot.py`
- `extract_party_size()` in `chatbot.py`
- `extract_time()` in `chatbot.py`
- `extract_date()` in `chatbot.py`

If all fields are found, the booking is saved. Otherwise, the chatbot returns the reservation help message from `BUSINESS_INFO`.

### Delivery branch

If the service is delivery, the chatbot tries to extract:

- customer name
- address
- ordered menu items

This is handled by:

- `extract_delivery_name()` in `chatbot.py`
- `extract_delivery_address()` in `chatbot.py`
- `extract_delivery_order()` in `chatbot.py`

If enough information is present, the delivery is saved and a confirmation message is returned.

## Keyword Database

The chatbot's rules are largely controlled by constants in `response_database.py`:

- `INTENT_KEYWORDS`: keywords used to recognize intents and sub-intents
- `RESERVATION_FIELD_KEYWORDS`: keywords that help detect reservation details
- `NUMBER_WORDS`: written numbers such as `one`, `two`, and `three`
- `MENU_ITEMS`: menu names and prices
- `BUSINESS_INFO`: fixed business responses and help text

This means most behavior changes can be made by editing the keyword lists and response dictionaries without changing the core chatbot flow.

## Important Clarification For Teammates

If you describe this system in a report or presentation, the most accurate wording is:

- `rule-based chatbot with lemmatization`
- `branching intent logic`
- `decision tree style flow`

The phrase `decision tree` is fine informally if you mean the branching logic, but this code does not train or use a formal machine learning decision tree model.

## Summary

This chatbot combines two main ideas:

- `Lemmatization` to normalize words before matching
- `Rule-based decision flow` to route the message and extract details
- `Lightweight self-learning memory` to reuse successful past phrasing

Together, these methods let the chatbot handle common restaurant questions and simple booking or delivery requests in a predictable way.

## Self-Learning Layer

The self-learning feature is implemented in `learning_store.py`.

What it does:

- stores successful interactions with their detected intent and cleaned tokens
- saves them to `learned_interactions.jsonl`
- checks that memory store when the main rule system does not find an intent
- reuses the closest learned match if the similarity score is high enough

What it does not do:

- it does not train a machine learning model
- it does not automatically invent brand new business knowledge
- it only learns from successful intent classifications that already happened in the chatbot

This makes the bot more adaptive while keeping the project safely inside the same rule-based architecture.
