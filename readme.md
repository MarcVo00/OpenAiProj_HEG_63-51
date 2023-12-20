# OpenAI Planning Assistant

## How to install
- installer python
- python -m venv venv (pour créer un environnement virtuel)
- .\venv\Scripts\activate (pour activer l'environnement virtuel)
- pip install -r requirements.txt (pour installer les librairies)

## How to write the file ".env"
- OPENAI_API_KEY="Your OpenAI api key"
- OPENAI_ORG_ID="Your Organisation ID"

## Libraries to install
- OpenAi
- python-dotenv

## How it works
1. le code va regarder si un fichier config.json existe.
    1.2 si oui, il va le lire et utiliser les informations dedans.
    1.3 si non, il va le créer avec les informations qu'on lui aura fourni.
2. L'utilisateur devra fournir son "user_id".
    2.1 Si l'utilisateur n'existe pas, il va être créé.
3. L'utilisateur devra fournir un fichier s'il en a.
4. L'utilisateur pourra fournir un prompt et il recevra une réponse.
