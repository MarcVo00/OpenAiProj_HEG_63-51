import openai
import fitz
import csv
from io import StringIO

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    doc.close()
    return text


#main
def main():
    pdf_path = "E:\HEG\Tech émergente\GPTProj3\marc.pdf"
    text = extract_text_from_pdf(pdf_path)
    
    #données openai pour que l'api marche
    openai.api_key = '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'
    openai.organization = 'org-5vnXArMLj6DdS0yJfEO7lk5I'
    
    #Variables de prompts
    requestUser = f'Peux-tu ajouter le nom des cours et quand ils auront lieux:\n {text} \n','Peux-tu ajouter ces autres activités, sachant que certaines activités peuvent prendre plus d''une heure. Á toi de juger combien de temps chaque activités va prendre: \n' ,input('que veux-tu ajouter de plus dans la semaine ?')
    requestInstructions = "Tu es un expert en gestion du temps qui ne répondra qu'en m'envoyant un text en format csv. Je souhaiterais créer un planning personnalisé à partir de mon emploi du temps actuel et de certaines activités que j'aimerai inclure dans ma semaine. Si des informations d'heure ne sont pas spécifiées, tu les rempliras de manière judicieuse. Les activités seront planifiées entre 8 heures et 22 heures."
    requestFormat = 'De plus, tu dois respecter le format que je te proposerai:\nLe planning sera formaté sous forme de fichier CSV avec les titres suivants : heure de début, heure de fin, date, jour, durée, et activité. Voici un exemple: "08.00,10.00,08.12.2023,Lundi,2,Cours: 63-51 - Technologies émergentes". En plus, le planning sera rempli avec les informations que je te fournirai. Le planning sera trié de manière croissante, d''abord par date, puis par heure. Il est impératif que tous les jours de la semaine soient représentés dans le planning en commançant par lundi et que le planning soit sur une semaine :'
    response = openai.completions.create(
        model="text-davinci-003",
        prompt = f"{requestInstructions}\n{requestFormat}\n{requestUser}", 
        #prompt=f"Tu es un expert en gestion du temps. Tu dois créer un fichier sous forme csv avec les informations que je fournirai. Je souhaiterais créer un planning personnalisé à partir de mon emploi du temps actuel et de certaines activités que j'aimerai inclure dans ma semaine. Le planning sera formaté sous forme de fichier CSV avec les colonnes suivantes : heure de début, heure de fin, date, jour, durée, et activité. Si aucune tâche n'est assignée à un créneau horaire, il sera indiqué ""temps libre"f". Si des informations d'heure ne sont pas spécifiées, tu les rempliras de manière judicieuse. Les activités seront planifiées entre 8 heures et 22 heures. Le planning sera trié de manière croissante, d'abord par date, puis par heure. Il est impératif que tous les jours de la semaine soient représentés dans le planning en commançant par un lundi: \n {requestUser}", 
        temperature=0.7,
        max_tokens= 3000
    )
    #print(prompt)
    
    print(response.choices[0].text.strip())
    data = response.choices[0].text.strip()
    lines = data.split('\n')

    # Créer un fichier CSV en utilisant StringIO
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)

    # Écrire les lignes dans le fichier CSV
    for line in lines:
        # Séparer les valeurs en utilisant la virgule et éliminer les espaces inutiles
        row = [value.strip() for value in line.split(',')]
        csv_writer.writerow(row)

    # Exporter le contenu dans un fichier CSV
    with open('emploi_du_temps.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(csv_data.getvalue())
    

if __name__ == "__main__":
    main()

