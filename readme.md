# OpenAI Planning Assistant

## But du projet
Le projet OpenAi Planning Assistant sert à avoir un assistant personnel qui premettra à une étudiant de lui fournir un ou plusieurs plannings en format PDF et de créer un planning.
Il pourra aussi demander à l'assistant d'ajouter des heures pour réaliser ses hobbys.
Le planning que l'assistant proposera, sera sous forme CSV. L'étudiant pourra reprendre le texte et le mettre dans un fichier CSV pour pouvoir avoir son tableau d'horaire.

## Librairies à installer
- OpenAi
- python-dotenv

## Comment installer
- installer python
- python -m venv venv (pour créer un environnement virtuel)
- .\venv\Scripts\activate (pour activer l'environnement virtuel)    Pour Windows
- pip install -r requirements.txt (pour installer les librairies)

## Créer un fichier ".env" avec les informations suivantes
- OPENAI_API_KEY="Your OpenAI api key"
- OPENAI_ORG_ID="Your Organisation ID"

## Comment ça marche
1. le code va regarder si un fichier config.json existe.  
    1.2 si oui, il va le lire et utiliser les informations dedans.  
    1.3 si non, il va le créer avec les informations qu'on lui aura fourni.  
2. L'utilisateur devra fournir son "user_id".  
    2.1 Si l'utilisateur n'existe pas, il va être créé.
3. L'utilisateur devra fournir un fichier, s'il en a.
4. L'utilisateur pourra fournir un prompt et il recevra une réponse.
