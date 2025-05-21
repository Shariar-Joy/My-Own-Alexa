import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import re
import time


class VoiceAssistant:
    def __init__(self, name="assistant"):
        self.name = name
        self.listener = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.setup_voice()

    def setup_voice(self):
        """Configure voice settings"""
        voices = self.engine.getProperty('voices')
        # Set female voice if available
        if voices:
            self.engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
        # Adjust rate and volume
        self.engine.setProperty('rate', 180)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume level

    def talk(self, text):
        """Make the assistant speak"""
        print(f"{self.name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen for user input"""
        command = ""
        try:
            with sr.Microphone() as source:
                print("\nListening...")
                # Adjust for ambient noise
                self.listener.adjust_for_ambient_noise(source, duration=0.5)
                # Set timeout and phrase time limit for better responsiveness
                voice = self.listener.listen(source, timeout=5, phrase_time_limit=5)
                print("Processing...")
                command = self.listener.recognize_google(voice)
                command = command.lower()
                print(f"You said: {command}")
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error occurred during listening: {e}")
        return command

    def process_command(self, command):
        """Process and respond to user command"""
        if not command:
            return False

        # Check if the assistant name is in the command
        wake_word_present = self.name.lower() in command
        # Remove assistant name from command if present
        if wake_word_present:
            command = command.replace(self.name.lower(), "").strip()

        # Process different types of commands
        if 'play' in command:
            song = command.replace('play', '').strip()
            self.talk(f"Playing {song}")
            try:
                pywhatkit.playonyt(song)
                return True
            except Exception as e:
                self.talk("Sorry, I couldn't play that. Please check your internet connection.")
                print(f"Error: {e}")
                return False

        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            self.talk(f"Current time is {time}")
            return True

        elif 'date' in command or 'today' in command:
            date = datetime.datetime.now().strftime('%A, %B %d, %Y')
            self.talk(f"Today is {date}")
            return True

        elif re.search(r'who (is|was|are)', command):
            try:
                # Extract the search query after "who is/was/are"
                search_pattern = r'who (is|was|are) (.*)'
                matches = re.search(search_pattern, command)
                if matches:
                    query = matches.group(2).strip()
                    if query:
                        info = wikipedia.summary(query, sentences=2)
                        self.talk(info)
                        return True
                    else:
                        self.talk("I didn't catch who you wanted to know about")
                        return False
                else:
                    self.talk("Could you rephrase your question?")
                    return False
            except wikipedia.exceptions.DisambiguationError as e:
                options = ", ".join(e.options[:3])
                self.talk(f"There are multiple results. Did you mean one of these: {options}?")
                return False
            except wikipedia.exceptions.PageError:
                self.talk("I couldn't find information about that subject")
                return False
            except Exception as e:
                self.talk("Sorry, I encountered an error while searching")
                print(f"Error: {e}")
                return False

        elif 'what is' in command or 'what are' in command or 'tell me about' in command:
            try:
                # Extract search query
                search_terms = ['what is', 'what are', 'tell me about']
                for term in search_terms:
                    if term in command:
                        query = command.replace(term, '').strip()
                        break

                if query:
                    info = wikipedia.summary(query, sentences=2)
                    self.talk(info)
                    return True
                else:
                    self.talk("I didn't understand what you want to know about")
                    return False
            except Exception as e:
                self.talk("I couldn't find that information")
                print(f"Error: {e}")
                return False

        elif 'joke' in command:
            try:
                joke = pyjokes.get_joke()
                self.talk(joke)
                return True
            except:
                self.talk("I'm having trouble thinking of a joke right now")
                return False

        elif 'hello' in command or 'hi' in command:
            self.talk(f"Hello there! How can I help you today?")
            return True

        elif 'your name' in command or 'who are you' in command:
            self.talk(f"I'm {self.name}, your voice assistant")
            return True

        elif 'exit' in command or 'stop' in command or 'goodbye' in command or 'bye' in command:
            self.talk("Goodbye! Have a great day!")
            return "exit"

        elif 'thank you' in command or 'thanks' in command:
            self.talk("You're welcome! Is there anything else I can help with?")
            return True

        # If no specific command was detected but the wake word was used
        elif wake_word_present:
            self.talk("How can I help you?")
            return True

        # If no wake word and no recognized command
        else:
            if wake_word_present:  # Only respond if wake word was present
                self.talk("I'm not sure how to help with that. Could you try another question?")
            return False

    def run(self):
        """Main assistant loop"""
        self.talk(f"Hello! I'm {self.name}, your voice assistant. How can I help you?")

        try:
            running = True
            while running:
                command = self.listen()
                result = self.process_command(command)

                # Check if we should exit
                if result == "exit":
                    running = False

                # Small pause to prevent CPU overuse
                time.sleep(0.5)

        except KeyboardInterrupt:
            self.talk("Goodbye!")
            print("Voice assistant terminated.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.talk("I encountered a problem and need to restart.")


if __name__ == "__main__":
    # Create and run the assistant with your preferred name
    assistant = VoiceAssistant(name="alexa")
    assistant.run()
