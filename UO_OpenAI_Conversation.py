import clr
import System
import json
import re
from time import sleep, time
from System.Net.Http import HttpClient, StringContent
from System.Net.Http.Headers import AuthenticationHeaderValue

clr.AddReference('System.Net.Http')

# Constants and Configuration
OPENAI_API_KEY = "OpenAIKeyHere" 
RESPONSE_DELAY = 7  # Time in seconds to wait before processing the next message - to make sure the bot has time to respond before responding again
MESSAGE_WAIT_TIME = 5  # Time in seconds to wait for additional message parts - to make sure to listen for the complete conversation when the other player is speaking
CONVERSATION_HISTORY_SIZE = 4
CONVERSATION_TIMEOUT = 60  # Time in seconds before the keyword conversation is considered to be over

# Global variables to track the active conversation state
player_conversation_history = []
conversation_initiator = None
conversation_start_time = 0
conversation_history = []  # Initialize the conversation history
last_processed_time = 0

Journal.Clear() # clear the journal to avoid responding to old conversations
# Global variables for specific player or keyword activation
listen_for_player = "OtherPlayerNameToListenFor"  # Replace with the specific player name you want to respond to at all times
keywords = ["PlayerName", "playernickname"]  # It will respond to these words and then start a conversation with specific player. Add more as needed - Capitalization matters

# Set up the initial OpenAI api prompt and behavior
BRAIN_SECTION = [
    {"role": "system", "content": "Your name is PlayerName. Keep responses short. "
    "You are an avatar inside of the game Ultima Online. You are one of many players."
    "Do not respond with your name like a chatbot. Do not use YourName:"
    "You are talking to another character who you are friends with but constantly argue and disagree."
    "You are on the side of Lord British and they are on the side of Lord Blackthorn."
    "You are a grandmaster warrior who has seen many battles. You yearn for the old times before the discovery of the lost lands"
    "Do not break character or mention you are a language model, be inquisitive, keep responses to one sentence."
    "Do not add any line breaks or odd characters. Keep things brief and short like you are using text to speech."
    "Only response with short sentences. You want to keep the conversation going."}
]


def send_to_openai(prompt):
    endpoint = "https://api.openai.com/v1/chat/completions"

    # Add the user's message to the conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Use the global CONTENT_SECTION variable
    messages = BRAIN_SECTION.copy()

    messages.extend(conversation_history[-6:])  # Add the last few conversation history entries

    # Create a dictionary for the JSON data
    data_dict = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }

    # Convert the dictionary to a JSON string
    data_json = json.dumps(data_dict)
    print(f"JSON Data: {data_json}", 33)
    content = StringContent(data_json, System.Text.Encoding.UTF8, "application/json")

    # Setup the HTTP client and headers
    http = HttpClient()
    http.DefaultRequestHeaders.Authorization = AuthenticationHeaderValue("Bearer", OPENAI_API_KEY)

    # Make the POST request
    response = http.PostAsync(endpoint, content).Result
    response_content = response.Content.ReadAsStringAsync().Result
    print(response_content)
    if response.IsSuccessStatusCode:
        # Manually extract the desired text from the response string
        assistant_idx = response_content.find('"role": "assistant"')
        if assistant_idx != -1:
            start_idx = response_content.find('"content": "', assistant_idx) + 12
            end_idx = response_content.find('"', start_idx)
            assistant_response = response_content[start_idx:end_idx].strip()

            # Remove newlines
            assistant_response = assistant_response.replace('\\n\\n', ' ').replace('\\n', ' ')

            # Add the assistant's message to the conversation history
            conversation_history.append({"role": "assistant", "content": assistant_response})

            # Manage the size of the conversation history if it becomes too long
            while len(conversation_history) > 20:  # 10 pairs x 2
                conversation_history.pop(0)  # Remove the oldest message

            return assistant_response
    else:
        # Return the entire response content for debugging
        return "API Error: " + response_content


def split_into_segments(text, max_length=92):
    """
    Splits a long string into segments of max_length, without splitting words.
    """
    words = text.split()
    segments = []
    current_segment = ""

    for word in words:
        if len(current_segment) + len(word) <= max_length:
            if current_segment:
                current_segment += " " + word
            else:
                current_segment = word
        else:
            segments.append(current_segment)
            current_segment = word

    if current_segment:
        segments.append(current_segment)

    return segments

# Processes a response from the listen_for_player variable
def process_specific_player_response(listen_for_player):
    global player_conversation_history  # Reference the global variable
    global last_processed_time

    # Using Razor Enhanced's Journal function to get the latest entries, with the addname parameter set to True
    journal_entries = Journal.GetTextByType('Regular', True)

    # Filter the entries related to the specific player
    player_entries = [entry.split(f'{listen_for_player}:', 1)[-1].strip() for entry in journal_entries if listen_for_player in entry]

    # Check if there are new entries from the player
    if not player_entries:
        return

    # Check if the RESPONSE_DELAY has passed since the last processed message
    current_time = time()
    if current_time - last_processed_time < RESPONSE_DELAY:
        return

    # Wait for MESSAGE_WAIT_TIME seconds to collect all parts of the message
    sleep(MESSAGE_WAIT_TIME)

    # Get the latest entries again to include any additional parts
    journal_entries_after_wait = Journal.GetTextByType('Regular', True)
    player_entries_after_wait = [entry.split(f'{listen_for_player}:', 1)[-1].strip() for entry in journal_entries_after_wait if listen_for_player in entry]

    # Concatenate the last CONVERSATION_HISTORY_SIZE entries to form the complete message
    complete_message = ' '.join(player_entries_after_wait[-CONVERSATION_HISTORY_SIZE:])

    # Update the conversation history for the player
    player_conversation_history.append(complete_message)
    player_conversation_history = player_conversation_history[-CONVERSATION_HISTORY_SIZE:]  # Keep only the last few entries

    # Form the prompt using the conversation history
    conversation_history_prompt = ' '.join(player_conversation_history)
    prompt = send_to_openai(conversation_history_prompt)

    segments = split_into_segments(prompt)
    for segment in segments:
        Player.ChatSay(1153, segment)  # Sending message in-game
        Misc.Pause(2000)  # Adjust as needed between segments
    player_conversation_history = []
    Journal.Clear()  # Clearing the journal

    # Update the time when the last message was processed
    last_processed_time = current_time

# Processes the response when someone mentions the keywords
def process_journal():
    global conversation_initiator
    global conversation_start_time
    global keywords
    # Using Razor Enhanced's Journal function
    journal_entries = Journal.GetTextByType('Regular')

    # If there's no journal entries, return
    if not journal_entries or len(journal_entries) == 0:
        return

    # If there's a conversation initiator, process their messages
    if conversation_initiator:
        # Check if the initiator is the player's name
        if conversation_initiator == Player.Name:
            return

        # Check for conversation timeout
        if time() - conversation_start_time > CONVERSATION_TIMEOUT:
            conversation_initiator = None
            return

        # Check for goodbye or farewell
        last_entry = journal_entries[len(journal_entries) - 1].lower()  # Get the last entry using positive indexing
        if "goodbye" in last_entry or "farewell" in last_entry:
            conversation_initiator = None
            return

        # Process the last entry from the initiator
        prompt = send_to_openai(last_entry)
        segments = split_into_segments(prompt)
        for segment in segments:
            Player.ChatSay(1153, segment)  # Sending message in-game using Razor Enhanced's Player function
            Misc.Pause(2000)  # Adjust as needed between segments

    # Otherwise, look for the bot's name to initiate a new conversation
    else:
        for entry in journal_entries:
            # Extract the name of the player who initiated the conversation
            conversation_initiator_candidate = entry.split(':')[0].strip()

            # Check if the initiator is the player's name, skip if it is
            if conversation_initiator_candidate == Player.Name:
                continue

            for keyword in keywords:
                if keyword in entry:
                    conversation_initiator = conversation_initiator_candidate
                    conversation_start_time = time()
                    prompt = send_to_openai(entry)
                    segments = split_into_segments(prompt)
                    for segment in segments:
                        Player.ChatSay(1153, segment)  # Sending message in-game using Razor Enhanced's Player function
                        Misc.Pause(3000)  # Adjust as needed between segments
                    break  # Breaks out of inner for loop
    Journal.Clear()  # Clearing the journal
# Main Loop
while True:
    process_specific_player_response(listen_for_player)
    process_journal()
    Misc.Pause(1000)
