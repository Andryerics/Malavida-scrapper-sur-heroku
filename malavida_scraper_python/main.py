from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI()

# Première route pour le premier code
class ScrapeRequest(BaseModel):
    scrape_link: str

@app.post("/search")
def scrape_website(request: ScrapeRequest):
    url = request.scrape_link
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; DIG-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.content, 'html.parser')

    extracted_data = []

    for section in soup.find_all('section', class_='app-download'):
        image_src = section.find('img')['src']
        link_href = section.find('a')['href']
        link_text = section.find('a').text.strip()
        version = section.find('span', class_='ver').text.strip()
        description = section.find('p').text.strip()
        download_size = section.find('span', class_='mvicon-download size').text.strip()
        release_date = section.find('span', class_='mvicon-calendar date').text.strip()

        extracted_data.append({
            "Image link": image_src,
            "App Link": link_href,
            "Titre": link_text,
            "Version": version,
            "Description": description,
            "Taille": download_size,
            "Date de publication": release_date
        })

    return extracted_data

# Deuxième route pour le deuxième code
class DownloadRequest(BaseModel):
    scraping_link: str

@app.post("/download")
def scrape_website(request: DownloadRequest):
    scraping_link = request.scraping_link

    if not scraping_link:
        raise HTTPException(status_code=400, detail="Lien de scraping manquant dans la requête.")

    # Header avec le User-Agent spécifié
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; DIG-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36'
    }

    # Obtenir le contenu HTML de la page avec le header personnalisé
    response = requests.get(scraping_link, headers=headers)

    result = {}

    # Vérifier si la requête a abouti avec succès (code 200)
    if response.status_code == 200:
        # Utiliser BeautifulSoup pour analyser le contenu HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Trouver la balise <a> avec la classe 'download button green-low'
        first_link = soup.find('a', {'class': 'download button green-low'})

        # Vérifier si la balise <a> a été trouvée et extraire le texte de l'attribut href
        if first_link:
            first_href = first_link.get('href')
            result['App_link'] = first_href

            # Suivre le premier lien extrait
            second_response = requests.get(first_href, headers=headers)

            # Vérifier si la requête a abouti avec succès (code 200)
            if second_response.status_code == 200:
                # Analyser le contenu HTML de la deuxième page
                second_soup = BeautifulSoup(second_response.text, 'html.parser')

                # Trouver la balise <a> avec la classe 'button green mvicon-download'
                second_link = second_soup.find('a', {'class': 'button green mvicon-download'})

                # Vérifier si la balise <a> a été trouvée et extraire le texte de l'attribut href
                if second_link:
                    second_href = second_link.get('href')
                    result['Download_link'] = second_href
                else:
                    result['second_href'] = 'Balise <a> du deuxième lien non trouvée.'
            else:
                result['second_href'] = f'La deuxième requête a échoué : {second_response.status_code}'
        else:
            result['first_href'] = 'Balise <a> du premier lien non trouvée.'
    else:
        result['first_href'] = f'La première requête a échoué : {response.status_code}'

    return result

# Healthcheck
@app.get("/ping")
async def healthcheck():
    return {"status": "Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8299)
    
