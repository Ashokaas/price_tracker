from requests import get
from bs4 import BeautifulSoup
from colorama import Fore
from threading import ThreadError
import schedule
import telebot
import time


API_KEY = # Votre clef api (str)
CHAT_ID = # Votre CHAT_ID (int)
bot = telebot.TeleBot(API_KEY)




# -- Requête pour récupérer une page
def info_site(url):
    # Requête sur un url
    res = get(url)
    # Si la requête n'aboutie pas on annule tout
    if not res.ok:
        print('Erreur')
        exit()
    # On met le site en bien pour pouvoir l'utiliser
    site = BeautifulSoup(res.text, 'lxml')
    
    return site


def rechercher_produit(produit:str, uniquement_magasin:list=None, nombre_de_produits_a_afficher:int=5):
    # On effectue une requête pour obtenir une liste des produits proche du souhait de l'utilisateur
    site = info_site(f'https://ledenicheur.fr/search?search={produit}')
    # On défini les listes contenants le nom et le lien des produits
    liste_nom = []
    liste_lien = []
    # Pour chaque enfant dans le tableau contenant la liste des produits
    for child in site.find('ul', class_ = 'ListUl-sc-xo0c91-0 fTCido').findChildren():
        # On récupère le lien et le nom
        lien = child.find('a', class_ = 'InternalLink-sc-t916l0-1 hYGtTZ ProductLink-sc-ezay95-0 cXuLZZ')
        nom = child.find('span', class_ = 'Text--bzqghn kBBoFI titlesmalltext')
        print(nom)
        # Si le nom existe et qu'il n'a jamais été trouvé
        if nom and nom.text not in liste_nom:
            liste_nom.append(nom.text)
        # Si le lien existe et qu'il n'a jamais été trouvé
        if lien and lien['href'] not in liste_lien:
            liste_lien.append(lien['href'])
    # On affiche la liste à l'utilisateur
    propostiion = ''
    print(liste_nom)
    for i in range(nombre_de_produits_a_afficher):
        propostiion += (f'{i+1} : {liste_nom[i]}\n')
    
    return propostiion, liste_lien
    


def afficher_produit(nb, liste_lien, uniquement_magasin):

    # Requête pour avoir la page du produit selectionné
    lien = f"https://ledenicheur.fr{liste_lien[nb-1]}"
    site = info_site(lien)

    # On affiche le titre du produit
    titre_produit = site.find('h1', class_ = 'Text--bzqghn bhbQJh h2text Title-sc-16x82tr-2 daHeSK')
    print(f'\n{Fore.YELLOW}{titre_produit.text} : {Fore.WHITE}')
    # On récupère le tableau contenant tout les prix et les magasins
    ul = site.find('ul', class_ = 'PriceList-sc-wkzg9v-0 fbrkVc')

    liste_magasin = []
    liste_tout = {}
    for child in ul.findChildren():
        prix = child.find('span', class_ = 'Text--bzqghn ddqBq bodysmalltext PriceLabel-sc-lboeq9-0 jCcYnj StyledPriceLabel-sc-k40pbc-0 kQerWx')
        magasin = child.find('span', class_ = 'StoreInfoTitle-sc-bc2k22-1 idSYNT')
        # Si le prix et le magasin existe et si le magasin n'a pas encore été trouvé
        if prix and magasin and magasin.text not in liste_magasin:
            if True in [(text in magasin.text) for text in uniquement_magasin]:
                liste_magasin.append(magasin.text)
                liste_tout[magasin.text] = prix.text
            
    return liste_tout
    

    

   



# 1er argument : (str)(obligatoire) Le produit ou l'id du produit que vous voulez
# 2ème argument : (list)(facultatif) Pour avoir le meilleur prix dans les enseignes que vous voulez
#rechercher_produit(produit='splatoon 3', uniquement_magasin=['Amazon', 'Fnac', 'Leclerc', 'Cultura', 'Auchan'], nombre_de_produits_a_afficher=5)



@bot.message_handler(commands=['isactive'])
def is_active(message):
    is_active_msg = bot.send_message(chat_id=CHAT_ID, text="Yes\n\n(Suppression dans 3 secondes)")
    time.sleep(3)
    bot.delete_message(chat_id=CHAT_ID, message_id=is_active_msg.id)
    
    
    
@bot.message_handler(commands=['prix'])
def prix(message):
    print(message.text)
    produit = message.text[6:]
    print(produit)

    proposition, liste_lien = rechercher_produit(produit)
    print(proposition)
    
    bot.send_message(chat_id=CHAT_ID, text=proposition)
    
    @bot.message_handler()
    def prix2(message):
        liste_finale = afficher_produit(int(message.text), liste_lien, ['Amazon', 'Fnac', 'Leclerc', 'Cultura', 'Auchan'])
        print(liste_finale)
        message_a_envoyer = ''
        for magasin, prix in zip(list(liste_finale.keys()), list(liste_finale.values())):
            message_a_envoyer += f'{magasin} : {prix}\n'
        
        print(message_a_envoyer)
        bot.send_message(chat_id=CHAT_ID, text=str(message_a_envoyer))
        
        @bot.message_handler(commands=['follow'])
        def follow(message):
            while True:
                if liste_finale != afficher_produit(int(message.text), liste_lien, ['Amazon', 'Fnac', 'Leclerc', 'Cultura', 'Auchan']):
                    bot.send_message(chat_id=CHAT_ID, text='Le prix a changé')
                
        
    
    
    
    
bot.infinity_polling()
