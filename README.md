<img src="2bff2a08-14e5-40a9-8d9f-e0d6f29e5a2d.webp" width="100" height="100" alt="Bot Logo">

# La Covardia Bot

Un bot de Telegram que permet enviar missatges anònims a un grup.

## Característiques

- Envia missatges anònims al grup
- Suporta text, fotos i documents
- Límit de 5 missatges per hora per usuari
- Interfície en català
- Missatges en negreta al grup

## Comandes

- `/start` - Inicia el bot i mostra l'ajuda
- `/ajuda` - Mostra el missatge d'ajuda
- `/codi` - Mostra l'enllaç al codi font
- `/quota` - Consulta els missatges que et queden en aquesta hora
- `/feedback` - Envia un suggeriment als administradors (el nom d'usuari serà visible)

## Privacitat

- Els missatges es publiquen de forma anònima
- No es guarda cap registre dels usuaris
- La comanda `/feedback` inclou el nom d'usuari per gestió

## Desenvolupament

Bot desenvolupat amb:
- Python
- python-telegram-bot
- Google Cloud Functions

## Llicència

[MIT License](LICENSE)

## Com utilitzar-lo

1. Inicia una conversa privada amb el bot
2. Envia el comandament `/start` per començar
3. Envia qualsevol missatge al bot i aquest el publicarà anònimament al grup
4. Rebràs una confirmació quan el missatge s'hagi enviat correctament

## Límits

- Màxim 5 missatges per hora per usuari
- El bot t'informarà dels missatges restants després de cada enviament
- Quan arribis al límit, el bot t'indicarà quant temps has d'esperar abans de poder tornar a enviar missatges

## Tipus de missatges suportats

- ✅ Text
- 📸 Fotos (amb o sense text)
- 📎 Documents

## Requisits tècnics (per a desenvolupadors)

- Python 3.9
- python-telegram-bot
- Google Cloud Functions
- Google Cloud SDK

## Desplegament

El bot està desplegat a Google Cloud Functions. Per a més informació sobre com desplegar la teva pròpia instància, consulta la documentació de Google Cloud. 
