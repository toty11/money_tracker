
from bs4 import BeautifulSoup
from decimal import Decimal
import os,subprocess

os.chdir("./money_tracker")

charges = [['ECHEANCE PRET PERSONNEL',13.33,'-'],["TOTAL OPTION SYSTEM' EPARGNE",4.99,'-'],
['PRLV SEPA HANDICAP INTERNATIONA',15,'-'],['CB  NETFLIX.COM',10.99,'-'],
['PRLV SEPA AXA',82.55,'-'],['PRLV SEPA FITBERGEVIN',29.95,'-'],['PRLV SEPA ORANGE CARAIBE',19.99,'-'],
['CB  E D F',66.86,'-']]

def getMontant(li):
    li = li.find('a')
    montant = ""
    montant = li.find('span','montantMvt').string
    signe = montant[0]
    montant = montant.replace('+','')
    montant = montant.replace('-','')
    montant = montant.replace(",",".")
    montant = montant.replace(u'\xa0', u' ')
    montant = montant.replace(' ','')

    return float(montant),signe

def getDate(li):
    li = li.find('a')
    return li.find('span','dateMvt').string

def getLibelle(li):
    li = li.find('a')
    return li.find('span','libelleMvt').string

def getTotal(items):
    total = 0
    for item in items:
        if(item[2] == '-'):
            total -= item[1]
        else:
            total += item[1] 
    return total

def create_liste(li):
    ecriture = []
    date = getDate(li)
    returnMontant = getMontant(li)
    montant = returnMontant[0]
    signe = returnMontant[1]
    libelle = getLibelle(li)
    ecriture.append(date)
    ecriture.append(montant)
    ecriture.append(signe)
    ecriture.append(libelle)
    return ecriture

#Retourne la liste des charges déjà payé
#et la liste des charges qu'ils restent à payé
def create_liste_charge(items):
    charges_liste = []
    
    for item in items:
        for charge in charges:
            if(charge[0] in item[3] and item[1] == charge[1]):
                charges_liste.append(item)  
    return charges_liste

def create_liste_charges_restantes(charges_liste):
    charges_restantes_liste = []
    charge_impayé = 0
    for charge in charges:
        for charge_payee in charges_liste:
            if(charge[0] in charge_payee[3]):
                charge_impayé = 1
                break
        if(charge_impayé == 0):
            charges_restantes_liste.append(charge)  
        charge_impayé = 0
    return charges_restantes_liste

def create_html_output(items,solde_reel,signe_solde_reel):
    economie_theorique = 'Economie théorique : {:.2f}'.format(getTotal(items)*(2/3))
    economie_reel = 'Economie réel : {:.2f}'.format(solde_reel*(2/3))
    solde = 'Solde théorique : {:.2f}€'.format(getTotal(items))
    solde_reel = 'Solde réel : {}{:.2f}€'.format(signe_solde_reel,solde_reel)
    
    liste_charges = create_liste_charge(items)
    liste_charges_restantes = create_liste_charges_restantes(liste_charges)
    html_charges_restantes = output_html_charges_restantes(liste_charges_restantes)
    html_charges_payee = output_html_charges(liste_charges)

    with open("output.html", "r") as f:
        html = f.read()
    soup = BeautifulSoup(html,features="html.parser")
    soup.find(id='solde').string = solde
    soup.find(id='solde_reel').string = solde_reel
    soup.find(id='budget_reel').string = economie_reel
    soup.find(id='budget_theorique').string = economie_theorique
    soup.find(id='charges_payee').extend(html_charges_payee)
    soup.find(id='charges_restantes').extend(html_charges_restantes)
    html = soup.prettify("utf-8")
    with open('index.html','wb') as f:
        f.write(html)

def output_html_charges(charges_liste):
    output = []
    for charge in charges_liste:
        div_tag = soup.new_tag("div",attrs={'class':'row text-left'})
        libelle_tag = soup.new_tag("p",attrs={'class':'col-10'})
        libelle_tag.string = '{}'.format(charge[3])
        div_tag.append(libelle_tag)
        montant_tag = soup.new_tag("p",attrs={'class':'col-2'})
        montant_tag.string = '{}{:.2f}€'.format(charge[2],charge[1])
        div_tag.append(montant_tag)
        #date_tag = soup.new_tag("p",attr={'class':'col_8'}).string = '{} {}{:.2f}€'.format(charge[3],charge[2],charge[1])
        
        #new_tag.string = '{} {}{:.2f}€'.format(charge[3],charge[2],charge[1])
        output.append(div_tag)
    new_tag = soup.new_tag("p")
    new_tag.string = 'Total charges payées {:.2f}€'.format(getTotal(charges_liste))
    output.append(new_tag)
    return output

def output_html_charges_restantes(charges_liste):
    output = []
    for charge in charges_liste:
        div_tag = soup.new_tag("div",attrs={'class':'row text-left'})
        libelle_tag = soup.new_tag("p",attrs={'class':'col-10'})
        libelle_tag.string = '{}'.format(charge[0])
        div_tag.append(libelle_tag)
        montant_tag = soup.new_tag("p",attrs={'class':'col-2'})
        montant_tag.string = '{}{:.2f}€'.format(charge[2],charge[1])
        div_tag.append(montant_tag)
        output.append(div_tag)

    new_tag = soup.new_tag("p")
    new_tag.string = 'Total charges restantes {:.2f}€'.format(getTotal(charges_liste))
    output.append(new_tag)
    return output

path = 'test.txt'

with open(path,'r') as f:
    html = f.read()
soup = BeautifulSoup(html,features="html.parser")

items = soup.find(id='homeAccDetail').find('ul').find_all('li')
items_formated = []

for item in items:
    items_formated.append(create_liste(item))
    if(getLibelle(item) == 'VIREMENT ALL MOL TECHNOLOGY'):
        break

solde_reel = soup.find(id='largeSolde').string
solde_reel = solde_reel[0:len(solde_reel)-4]
signe_solde_reel = solde_reel[0]
solde_reel = solde_reel.replace('+','')
solde_reel = solde_reel.replace('-','')
solde_reel = solde_reel.replace(",",".")
solde_reel = solde_reel.replace(u'\xa0', u' ')
solde_reel = solde_reel.replace(' ','')
solde_reel = float(solde_reel)

create_html_output(items_formated,solde_reel,signe_solde_reel)
subprocess.run(['open', 'index.html'], check=True)