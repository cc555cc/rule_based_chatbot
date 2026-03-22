"""
Predefined response database for the rule-based chatbot.

Each item represents one intent category:
- intent: the name of the user intent
- patterns: words or phrases to look for in the user's message
- responses: possible replies the chatbot can return
"""

INTENT_KEYWORDS = {
    "operation": {
        "address": [
            "where",
            "address",
            "location",
            "located",
            "directions",
            "find",
            "map",
            "nearby",
        ],
        "time": [
            "holiday",
            "open",
            "opening",
            "close",
            "closing",
            "hours",
            "time",
            "today",
            "tomorrow",
            "weekend",
        ],
    },
    "contact": {
        "number": [
            "number",
            "phone",
            "call",
            "contact",
            "telephone",
            "mobile",
        ],
        "email": [
            "email",
            "mail",
            "message",
            "contact form",
        ],
    },
    "service": {
        "reservation": [
            "reservation",
            "booking",
            "book",
            "reserve",
            "table",
            "seat",
            "seating",
            "party",
        ],
        "menu": [
            "menu",
            "eat",
            "food",
            "meal",
            "dish",
            "dishes",
            "drink",
            "drinks",
            "special",
            "specials",
        ],
        "delivery": [
            "delivery",
            "deliver",
            "delivered",
            "takeout",
            "take-out",
            "pickup",
            "pick-up",
            "carryout",
            "carry-out",
            "to go",
            "order online",
            "drop off",
        ],
    },
}

RESERVATION_FIELD_KEYWORDS = {
    "name": {
        "before": [
            "for",
            "name",
        ],
        "after": [
            "under",
            "mr",
            "mrs",
            "ms",
            "miss",
        ],
    },
    "time": {
        "before": [
            "pm",
            "am",
            "o'clock",
        ],
        "after": [
            "at",
        ],
        "noon": [
            "noon",
        ],
        "unclear": [
            "midnight",
            "evening",
            "morning",
            "afternoon",
            "tonight",
        ],
    },
    "party_size": {
        "before": [
            "people",
            "person",
            "guest",
            "guests",
            "seat",
            "seats",
        ],
        "after": [
            "for",
        ],
    },
    "date": {
        "exact": [
            "today",
            "tomorrow",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
        "after": [
            "on",
        ],
    },
}

NUMBER_WORDS = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
]

BUSINESS_INFO = {
    "operation": {
        "response": "We are open from 9 AM to 9 PM every day, and our restaurant is located at 123 Main Street.",
        "details": {
            "address": "Our restaurant is located at 123 Main Street.",
            "time": "We are open from 9 AM to 9 PM every day.",
        },
    },
    "contact": {
        "response": "You can reach us by phone at (555) 123-4567 or by email at hello@restaurant.com.",
        "details": {
            "number": "You can call us at (555) 123-4567.",
            "email": "You can email us at hello@restaurant.com.",
        },
    },
    "service": {
        "details": {
            "reservation": "We accept reservations for lunch and dinner. Please clearly provide your name, party size, booking date and time.",
            "menu": "We offer appetizers, main dishes, desserts, and drinks. Ask if you want recommendations.",
            "delivery": "We offer delivery, takeout, and pickup during business hours. Please cleary provide your name and address.",
        },
    },
}

RESPONSE_DATABASE = [
    {
        "intent": "greeting",
        "patterns": ["hello", "hi", "hey", "good morning", "good afternoon"],
        "responses": [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
        ],
    },
    {
        "intent": "goodbye",
        "patterns": ["bye", "goodbye", "see you", "talk to you later"],
        "responses": [
            "Goodbye! Have a great day.",
            "See you later!",
        ],
    },
    {
        "intent": "hours",
        "patterns": ["hours", "opening hours", "when are you open", "what time do you open"],
        "responses": [
            "We are open from 9 AM to 5 PM, Monday to Friday.",
        ],
    },
    {
        "intent": "pricing",
        "patterns": ["price", "cost", "how much", "fees"],
        "responses": [
            "Prices depend on the service or item. Please tell me what you are asking about.",
        ],
    },
    {
        "intent": "help",
        "patterns": ["help", "support", "can you help me", "i need help"],
        "responses": [
            "Of course. Please describe your question and I will try to help.",
        ],
    },
]

FALLBACK_RESPONSES = [
    "Sorry, I do not understand that yet.",
    "I am not sure how to respond to that right now.",
]
