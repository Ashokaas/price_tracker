import requests
from bs4 import BeautifulSoup
from colorama import Fore

NOMBRE_DE_PRODUIT_A_AFFICHER = 5

# -- Requête pour récupérer une page
def info_site(url):
    # Requête sur un url
    res = requests.get(url)
    # Si la requête n'aboutie pas on annule tout
    if not res.ok:
        print('Erreur')
        exit()
    # On met le site en bien pour pouvoir l'utiliser
    site = BeautifulSoup(res.text, 'lxml')
    
    return site


def rechercher_produit(produit):
    # Si l'utilisateur met directement le lien
    try:
        # On met l'id du produit en int
        int(produit)
        # On effectue une requête pour récupérer la page du produit
        site = info_site(f"https://ledenicheur.fr/product.php?p={produit}")
    # Sinon
    except:
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
            # Si le nom existe et qu'il n'a jamais été trouvé
            if nom and nom.text not in liste_nom:
                liste_nom.append(nom.text)
            # Si le lien existe et qu'il n'a jamais été trouvé
            if lien and lien['href'] not in liste_lien:
                liste_lien.append(lien['href'])
        # On affiche la liste à l'utilisateur
        for i in range(NOMBRE_DE_PRODUIT_A_AFFICHER):
            print(f'{i+1} : {liste_nom[i]}')
        # L'utilisateur choisi le produit
        selectionner_produit = int(input('Selectionnez le bon produit : '))
        # Requête pour avoir la page du produit selectionné
        site = info_site(f"https://ledenicheur.fr{liste_lien[selectionner_produit-1]}")

    # On affiche le titre du produit
    titre_produit = site.find('h1', class_ = 'Text--bzqghn bhbQJh h2text Title-sc-16x82tr-2 daHeSK')
    print(f'\n{Fore.YELLOW}{titre_produit.text} : {Fore.WHITE}')
    # On récupère le tableau contenant tout les prix et les magasins
    ul = site.find('ul', class_ = 'PriceList-sc-wkzg9v-0 fbrkVc')

    liste_magasin = []
    for child in ul.findChildren():
        prix = child.find('span', class_ = 'Text--bzqghn ddqBq bodysmalltext PriceLabel-sc-lboeq9-0 jCcYnj StyledPriceLabel-sc-k40pbc-0 kQerWx')
        magasin = child.find('span', class_ = 'StoreInfoTitle-sc-bc2k22-1 idSYNT')
        # Si le prix et le magasin existe et si le magasin n'a pas encore été trouvé
        if prix and magasin and magasin.text not in liste_magasin:
            liste_magasin.append(magasin.text)
            print(f'{magasin.text} : {prix.text}')


produit = input(f'\n{Fore.YELLOW}Quel produit recherchez vous ? : {Fore.WHITE}')
rechercher_produit(produit)

