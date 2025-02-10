![Bot Logo](2bff2a08-14e5-40a9-8d9f-e0d6f29e5a2d.webp)

# Bot Anònim de Telegram

Un bot de Telegram que permet als usuaris enviar missatges anònims a un grup específic.

## Característiques

- 🔒 Anonimat complet dels missatges
- 📝 Suport per a text, fotos i documents
- ⏰ Sistema de límit de missatges (5 missatges per hora)
- 🗣️ Interfície completament en català

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

## Privacitat

- Els missatges són completament anònims
- No es guarda cap registre dels missatges enviats
- La identitat dels usuaris mai es comparteix amb el grup

## Requisits tècnics (per a desenvolupadors)

- Python 3.9
- python-telegram-bot
- Google Cloud Functions
- Google Cloud SDK

## Desplegament

El bot està desplegat a Google Cloud Functions. Per a més informació sobre com desplegar la teva pròpia instància, consulta la documentació de Google Cloud.

## Llicència

Aquest projecte està sota la llicència MIT. Consulta el fitxer `LICENSE` per a més detalls. 
