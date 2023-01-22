import requests
import bs4
import colorama
from threading import ThreadError
import schedule
import telebot
import time


API_KEY = 'str API KEY'
CHAT_ID = 'int chat id'
bot = telebot.TeleBot(API_KEY)



class PriceTracker:
    def __init__(self, produit):
        liste_produits = self.rechercher_produit(produit)
        nb_bon_produit = self.afficher_liste_produits(liste_produits)
        prix_produit = self.afficher_produit(liste_produits[nb_bon_produit]['lien'])
        print(prix_produit)

    # -- Requête pour récupérer une page
    def info_site(self, url:str):
        """Retourne un site grace à l'url

        Args:
            url (str): URL du site

        Returns:
            BeautifulSoup: site
        """
        # Requête sur un url
        res = requests.get(url, timeout=(2, 5))
        # Si la requête n'aboutie pas on annule tout
        if not res.ok:
            print('Erreur')
            exit()
        # On met le site en bien pour pouvoir l'utiliser
        site = bs4.BeautifulSoup(res.text, 'lxml')
        
        return site



    def rechercher_produit(self, produit:str, uniquement_magasin:list=None, nombre_de_produits_a_afficher:int=5):
        """Retourne une liste de produits

        Args:
            produit (str): Nom du produit recherché
            uniquement_magasin (list, optional): Les magasins que l'on veut uniquement. Defaults to None.
            nombre_de_produits_a_afficher (int, optional): Assez clair quand même. Defaults to 5.

        Returns:
            list: Liste de dico contenant les noms et liens des produits
        """
        # On effectue une requête pour obtenir une liste des produits proche du souhait de l'utilisateur
        site = self.info_site(f'https://ledenicheur.fr/search?search={produit}')
        # On défini la liste contenant le nom et le lien des produits
        liste_noms_liens = []
        # Pour chaque enfant dans le tableau contenant la liste des produits
        for child in site.find('ul', class_ = 'ListUl-sc-xo0c91-0 fTCido').findChildren(recursive=False):
            try:
                # On récupère le lien et le nom
                lien = child.find('a', class_ = 'InternalLink-sc-t916l0-1 hYGtTZ ProductLink-sc-ezay95-0 cXuLZZ').get('href')
                nom = child.find('span', class_ = 'Text--d6brv6 cmPSrj titlesmalltext').get('title')
                # On ajoute tout à une liste de dico
                liste_noms_liens.append({"nom": nom, "lien": lien})
            except:
                pass
            
        return liste_noms_liens[0:5]
    


    def afficher_liste_produits(self, liste_produits:list):
        """Permet de choisir parmis une liste de produits

        Args:
            liste_produits (list): Liste des produits
        
        Returns:
            dict: Produit selectionné
        """
        for n_ieme_produit in range(len(liste_produits)):
            print(f"{n_ieme_produit+1} : {liste_produits[n_ieme_produit]['nom']}")
        
        bon_produit = int(input("Quel est le bon produit : "))
        
        return bon_produit - 1



    def afficher_produit(self, lien:str, uniquement_magasin:list=None):
        uniquement_magasin = ["Fnac", "Amazon"]
        # Requête pour avoir la page du produit selectionné
        site = self.info_site(f"https://ledenicheur.fr{lien}")

        # On affiche le titre du produit
        titre_produit = site.find('h1', class_ = 'Text--d6brv6 cUwXWZ h2text Title-sc-16x82tr-2 fDYedx')
        print(f"{colorama.Fore.YELLOW}{titre_produit.text} : {colorama.Fore.WHITE}")
        # On récupère le tableau contenant tout les prix et les magasins
        ul = site.find('ul', class_ = 'PriceList-sc-wkzg9v-0 fbrkVc')

        liste_magasin = []
        liste_tout = {}
        for child in ul.findChildren(recursive=False):
            prix = child.find('span', class_ = 'Text--d6brv6 iLMTVw bodysmalltext PriceLabel-sc-lboeq9-0 epoSmt StyledPriceLabel-sc-k40pbc-0 kQerWx')
            magasin = child.find('span', class_ = 'StoreInfoTitle-sc-bc2k22-1 idSYNT')
            # Si le prix et le magasin existe et si le magasin n'a pas encore été trouvé
            if prix and magasin and magasin.text not in liste_magasin:
                if True in [(text in magasin.text) for text in uniquement_magasin]:
                    liste_magasin.append(magasin.text)
                    liste_tout[magasin.text] = prix.text
                
        return liste_tout
    


produit = PriceTracker('splatoon 3')

exit()

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
