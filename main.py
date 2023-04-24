
from bs4 import BeautifulSoup
from decimal import Decimal
import os,subprocess,datetime,csv

#os.chdir("./money_tracker")

charges = [['ECHEANCE PRET PERSONNEL',13.33,'-',18],['PRLV SEPA HANDICAP INTERNATIONA',15,'-',10],['CB  NETFLIX.COM',10.99,'-',20],
['PRLV SEPA AXA',83.84,'-',5],['PRLV SEPA FITBERGEVIN',29.95,'-',26],['PRLV SEPA ORANGE CARAIBE',19.99,'-',24],
['CB  E D F',66.86,'-','Bimensuel'],['PRLV SEPA ALAN SA by Stripe via',52,'-',8],
['PRLV SEPA WORLD SATELLITE GUADE',39.99,'-',5],['CB BRUTX',4.99,'-',17],['CB  TIPI SIAEAG',0,'-','Bimensuel'],
['SPOTIFY',5,'-',17]]

def getMontant(li):
    

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
        total += item[1] 
    return total

def create_liste(row):
    ecriture = []
    
    ecriture.append(row[0])
    ecriture.append(float(row[1].replace(',', '.')))
    ecriture.append('')
    ecriture.append(row[4])
    return ecriture

#Retourne la liste des charges déjà payé
#et la liste des charges qu'ils restent à payé
def create_liste_charge(items):
    charges_liste = []
    
    for item in items:
        for charge in charges:
            if(charge[0] in item[3]):
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

def create_html_output(items,solde_reel):
    economie_theorique = 'Economie théorique : {:.2f}'.format(getTotal(items)*(2/3))
    economie_reel = 'Economie réel : {:.2f}'.format(solde_reel*(2/3))
    solde = 'Solde théorique : {:.2f}€'.format(getTotal(items))
    solde_reel = 'Solde réel : {:.2f}€'.format(solde_reel)
    
    liste_charges = create_liste_charge(items)
    print(liste_charges)
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

        date_tag = soup.new_tag("p",attrs={'class':'col-2'})
        date_tag.string = '{}'.format(charge[0])
        div_tag.append(date_tag)

        libelle_tag = soup.new_tag("p",attrs={'class':'col-8'})
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
        div_tag = soup.new_tag("div",attrs={'class':'row no-gutters text-left'})

        dt = datetime.datetime.today()
        date_tag = soup.new_tag("p",attrs={'class':'col-2'})
        if(type(charge[3]) is int):
            date = charge[3]-dt.day 
            date_tag.string = 'Dans {} jours'.format(date)
        else:
            date_tag.string = '{}'.format(charge[3])
        div_tag.append(date_tag)

        libelle_tag = soup.new_tag("p",attrs={'class':'col-8'})
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
items_formated = []
soup = BeautifulSoup('',features="html.parser")
with open('T_cpte_06174_001269U_du_01-04-2023_au_23-04-2023.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    for row in spamreader:
        if(row[3] == '06174 001269U'):
            solde_reel = float(row[1].replace(',', '.'))
        else:
            items_formated.append(create_liste(row))

create_html_output(items_formated,solde_reel)
#subprocess.run(['open', 'index.html'], check=True)