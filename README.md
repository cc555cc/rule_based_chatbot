# Rule-Based Restaurant Chatbot

This project is a rule-based restaurant chatbot with a lightweight self-learning layer. It does not use a large language model. Instead, it generates replies by combining:

- keyword-based intent detection
- branching response logic
- reservation and delivery field extraction
- a small learned-memory system for previously seen words and phrasing

## Major Chatbot Functions

### How The Chatbot Generates A Response

The chatbot follows a decision-tree-like flow based on a top intent and, when needed, a sub-intent.

The flow is:

1. The UI sends the user message to `server.py`.
2. `server.py` calls `generate_response()` in `chatbot.py`.
3. `chatbot.py` breaks the sentence into tokens with `parse_phrase()`.
4. `text_normalization.py` lemmatizes the tokens so different word forms can match the same rule.
5. `chatbot.py` looks for a top intent by comparing the normalized words against predefined keyword groups in `learning_resource/response_database.py`.
6. If a matching keyword is found, the chatbot returns the category where that keyword belongs, such as `greeting`, `operation`, `contact`, or `service`.
7. If the top intent is `service`, the chatbot then looks for a service sub-intent such as `reservation`, `menu`, or `delivery`.
8. Based on the detected intent, the chatbot generates a response:

- fixed business response for greeting, contact, or operation questions
- menu response with text and `resource/menu.png`
- reservation extraction and confirmation
- delivery extraction and confirmation

For reservation and delivery queries, the chatbot tries to extract the required details from the sentence. If enough information is missing, it returns a generic help response instead of a confirmation.

If the rule system does not find an intent, the chatbot then checks the learned interaction store in `learning_resource/model_learning.py`. This is a more expensive fallback because it looks through previously learned unfamiliar words. If that still does not produce an intent, the chatbot returns the standard fallback response.

### How The Chatbot Learns New Words

The chatbot learns unfamiliar words when they appear together with words that already reveal a known intent.

The idea is:

- an unfamiliar word is stored with the intent it appeared with
- each future appearance adds more evidence for that intent
- over time, the chatbot estimates which intent that unfamiliar word most strongly belongs to

This logic is implemented mainly in `learning_resource/model_learning.py`.

#### Appending New Words

`appending_learning_entry()` is called with:

- the original phrase
- the detected top intent
- the detected sub-intent

It then:

1. Parses and normalizes the phrase.
2. Checks whether the phrase contains a known intent word.
3. Looks at each normalized word that is not already a known keyword.
4. If the word is already in `learned_interactions.jsonl`, it adds points to the matching top intent and sub-intent counts.
5. If the word is not already stored, it creates a new learned entry for that word.
6. It updates the observation count when the phrase also contains known intent words.

#### Promotion To The Main Rule Database

After a learned word has been observed enough times, the chatbot may promote it into the main keyword database for faster future matching.

The promotion conditions in the current code are:

- observation count is at least `5`
- one top intent has at least `70%` of the accumulated points for that word
- if the top intent is `service`, one sub-intent also has at least `70%` of the sub-intent points

When those conditions are met, the word is written into `learning_resource/response_database.py` so the main rule system can match it directly next time.

#### Guessing Intent From Learned Words

If the normal rule-based system fails to detect an intent, the chatbot tries to guess one from the learned interaction file.

It does this by:

1. Normalizing the current phrase.
2. Checking whether any of its words appear in `learned_interactions.jsonl`.
3. Adding up the stored top-intent and sub-intent points for matching learned words.
4. Choosing the intent with the highest total score.

The highest-scoring accumulated intent is treated as the most likely user intent, and the chatbot then generates a response from that guessed intent.

## Response And Learning Flow

When a user sends a message, the system works in this order:

1. `server.py` receives the API request from the UI.
2. `chatbot.py` parses the message and decides the intent.
3. `text_normalization.py` lemmatizes words so related terms map to the same base form.
4. `learning_resource/response_database.py` provides the rule dictionaries and business data used for matching.
5. `chatbot.py` generates a response, menu reply, reservation confirmation, or delivery confirmation.
6. `booking_store.py` saves bookings and deliveries to JSONL files when needed.
7. `learning_resource/model_learning.py` stores useful learned words and can reuse them later when the fixed rules miss an intent.

## Project Structure By Importance

### 1. `chatbot.py`

This is the core chatbot engine.

It is responsible for:

- parsing user text
- detecting top-level and sub-level intents
- extracting reservation and delivery details
- generating the final response
- asking the learning layer for help when normal rules fail

This is the most important file for response generation.

### 2. `text_normalization.py`

This file normalizes words before intent matching.

It provides:

- `lemmatize_word()`
- `lemmatize_words()`

This helps the chatbot treat related words like `booking`, `booked`, and `book` more consistently.

### 3. `learning_resource/`

This folder contains the rule database and the self-learning system.

#### `learning_resource/response_database.py`

This is the main rule database used by the chatbot.

It stores:

- `INTENT_KEYWORDS`
- `RESERVATION_FIELD_KEYWORDS`
- `NUMBER_WORDS`
- `MENU_ITEMS`
- `BUSINESS_INFO`
- stop words used by the learning layer

This file is critical because it defines most of the chatbot's vocabulary and fixed responses.

#### `learning_resource/model_learning.py`

This is the lightweight learning layer.

It is responsible for:

- storing learned unknown words
- updating observation counts
- predicting intents from learned entries when rule matching fails
- writing promoted keywords back into the response database
- logging learning activity

This is the most important file for learning new words.

#### `learning_resource/learned_interactions.jsonl`

This stores learned words and their observed intent associations.

The chatbot reads this file when it tries to recover an intent that the fixed rules did not catch.

#### `learning_resource/learning_log.txt`

This is a plain-text log of learning activity such as:

- new learned words
- updated learned words
- promoted learned words

It is useful for debugging the learning system.

#### `learning_resource/response_database_minimal.py`

This appears to be a smaller or alternate database variant. It is not part of the main runtime path used by `chatbot.py`.

#### `learning_resource/__init__.py`

This makes `learning_resource` importable as a Python package.

#### `learning_resource/__pycache__/`

This contains generated Python cache files and is not part of the chatbot logic.

### 4. `server.py`

This is the backend HTTP server for the chatbot.

It:

- listens on `127.0.0.1:8000`
- accepts `POST /api/chat`
- passes the message to `chatbot.py`
- returns the chatbot reply as JSON

Without this file, the UI cannot talk to the chatbot engine.

### 5. `booking_store.py`

This file saves successful reservation and delivery data.

It provides:

- `save_booking()`
- `save_delivery()`

These functions write structured JSON lines into the service database files.

### 6. `service_database/`

This folder stores service records created by chatbot actions.

#### `service_database/bookings.jsonl`

Stores saved reservation records.

#### `service_database/deliveries.jsonl`

Stores saved delivery records.

### 7. `training_sentences.txt`

This file is used to seed or reinforce the learning layer.

`learning_resource/model_learning.py` can read it and train the memory system from example sentences.

It supports the learning system, but it is not required for normal live response generation.

### 8. `resource/`

This folder stores static assets used in responses.

#### `resource/menu.png`

This image is returned when the chatbot responds with the menu.

### 9. `chatbot-ui/`

This is the React frontend for the chatbot.

It:

- shows the chat interface
- sends user messages to `/api/chat`
- displays text replies and menu images

It is important for user interaction, but it does not decide the chatbot logic itself.

### 10. `restore.ps1`

This is a support script rather than part of normal chatbot response generation.

It is not in the main response or learning path.

## Runtime Summary

If you only want to understand the main chatbot path, focus on these files first:

1. `chatbot.py`
2. `text_normalization.py`
3. `learning_resource/response_database.py`
4. `learning_resource/model_learning.py`
5. `server.py`
6. `booking_store.py`

## Important Clarification

The most accurate way to describe this project is:

- `rule-based chatbot with lemmatization`
- `branching intent logic`
- `lightweight self-learning memory`

It is fine to describe the branching flow as `decision tree style`, but this project does not train or use a formal machine learning decision tree model.
