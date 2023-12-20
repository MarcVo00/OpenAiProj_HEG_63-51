import json
import os
import sys
import time
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.beta.threads.thread_message import ThreadMessage
from pydantic import parse_obj_as
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder

load_dotenv()
CONFIG_FILE = "config.json"
client = OpenAI()

@dataclass
class UploadedFile:
    openai_id: str
    file_name: str

@dataclass
class Assistant:
    name: str
    prompt: str
    files: list[str]
    model: str = "gpt-4-1106-preview"

# La config sera composé d'un utilisateur et d'un id assistant. De plus, il y aura la listes des fichiers dans la config.
@dataclass
class Config:
    assistants: dict
    files: list[UploadedFile]

    @classmethod
    def read(cls) -> "Config":
        if not os.path.exists(CONFIG_FILE):
            print(f"Config file {CONFIG_FILE} does not exist, loading an empty config.", file=sys.stderr)
            return cls(assistants={}, files=[])
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return parse_obj_as(cls, config)

    def write(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self, f, indent=2, default=pydantic_encoder)

    def get_file_name(self, openai_id: str) -> str:
        """Get the file name for the given OpenAI file id."""
        for file in self.files:
            if file.openai_id == openai_id:
                return file.file_name
        raise ValueError(f"File with id {openai_id} not found in config.")

    def try_adding_file(self, file_name: str, openai_id: str) -> None:
        """Try adding a file to the config. If it already exists, do nothing."""
        # File already exists, do nothing.
        for file in self.files:
            if file.file_name == file_name:
                return

        # Check that the file exists on OpenAI.
        try:
            openai_file = client.files.retrieve(openai_id)
            # Simple check that it has the same name.
            if openai_file.filename != file_name:
                raise ValueError(f"OpenAI file {openai_id} has name {openai_file.filename}, expected {file_name}")
            self.files.append(UploadedFile(openai_id=openai_id, file_name=file_name))
            self.write()
        except Exception as e:
            print(f"Could not add file {file_name} with id {openai_id}: {e}", file=sys.stderr)

    def get_or_create_file(self, file_name: str) -> UploadedFile:
        """Get the file with the given name, or upload it if it doesn't exist."""
        for file in self.files:
            if file.file_name == file_name:
                return file

        print(f"File {file_name} not found in config. Uploading to OpenAI.", file=sys.stderr)
        with open(file_name, "rb") as f:
            openai_file = client.files.create(file=f, purpose="assistants")
            uploaded_file = UploadedFile(openai_id=openai_file.id, file_name=file_name)
            self.files.append(uploaded_file)
            self.write()


            return uploaded_file

    def get_or_create_assistant(self, user_id: str, assistant: Assistant, force_recreate: bool = False) -> str:
        """Get the assistant with the given name, or create it if it doesn't exist."""
        assistant_id = self.assistants.get(user_id)
        if assistant_id is not None and not force_recreate:
            return assistant_id
        else:
            print(f"Creating new Assistant for user {user_id}.", file=sys.stderr)
            assistant_id = client.beta.assistants.create(
                name=assistant.name,
                instructions=assistant.prompt,
                model=assistant.model,
                file_ids=[self.get_or_create_file(file_name).openai_id for file_name in assistant.files],
                tools=[{"type": "retrieval"}],
            ).id
            self.assistants[user_id] = assistant_id
            print(self.assistants)
            self.write()
            return assistant_id

def print_message(message: ThreadMessage):
    text_message = message.content[0]
    assert text_message.type == "text"
    text = text_message.text
    print("Message: ")
    print(text.value)

    sources = []
    for annotation in text.annotations:
        if annotation.type != "file_citation":
            continue
        source = annotation.file_citation
        file_name = config.get_file_name(source.file_id)
        quote_start = source.quote[:50].replace("\n", " ") + "..."
        sources.append(f'{annotation.text}: dans {file_name}, "{quote_start}"')

    if sources:
        print()
        print("Sources:")
        print("\n".join(sources))

if __name__ == "__main__":
    files_names = []
    config = Config.read()

    #Permet à l'utilisateur d'uploader ses fichiers sur OpenAi
    user_id: str = input("Le nom de l'utilisateur: ").lower()
    user_response: str = input('''Veux-tu ajouter des fichiers ?("non" pour arrêter d'ajouter)''')
    while user_response != "non":
        files_names.append(user_response)
        user_response: str = input('''Veux-tu ajouter des fichiers ?("non" pour arrêter d'ajouter)''')
        print(files_names)
    assistant = Assistant(
    name="PlanningAssistant",

    #L'instructions que l'assistant va recevoir avant que l'utilisateur ne lui demande quoique se soit.
    prompt="""Tu es un expert en gestion du temps.
    Tu dois me fournir un planning de la semaine avec les informations que je te fournis. Par contre, s'il n'y plus de temps disponible, tu répondras que ce n'est pas possible d'ajouter plus d'activités.
    La forme du planning doit être sous forme CSV mais tu dois me fournir du texte et pas un lien.
    Je veux qu'il y ait les titres suivants:
    Date, Jour, Heure de début, Heure de fin, Durée, Nom d'activité
    """.replace(
        "\n    ", " "
    ),
    files= files_names
)
    assistant_id = config.get_or_create_assistant(user_id, assistant)
    print(f"Assistant id for user {user_id}: {assistant_id}")
    user_prompt = input("Que veux-tu me demander ?")
    # Création du thread et d'un premier message
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_prompt
    )

    # Lance l'assistant sur le thread
    run = client.beta.threads.runs.create(assistant_id=assistant_id, thread_id=thread.id)
    print(f"Started assistant on run id: {run.id}")

    # On attend que l'assistant ait fini de répondre. Tant que l'utilisateur n'a plus "rien" à demander, les demandes continueront
    remaining_tries = 20
    while remaining_tries > 0:
        remaining_tries = 20
        print(f"Assistant run status: {run.status}. Waiting 5 seconds.")
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        remaining_tries -= 1
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            last_message = messages.data[0]
            print_message(last_message)
            user_prompt = input("""Que veux-tu me demander ? ("rien" pour arrêter)""")
            if user_prompt.lower() != "rien":
                message = client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=user_prompt
                )
            else:
                break
            
            # Lance l'assistant sur le thread
            run = client.beta.threads.runs.create(assistant_id=assistant_id, thread_id=thread.id)
            


    if run.status != "completed":
        print(f"Assistant run did not answer. Status: {run.status}", file=sys.stderr)
        sys.exit(1)

