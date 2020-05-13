# Client meeting April 21th 2020
Louis is weer aanwezig bij de meeting.

## FA-discussie
Genormaliseerde tekst is een txt met:
 - getallen uitgeschreven
 - interpuncties weg (geen ,.'! etc)
 
Kan bron van problemen zijn, maar hoeft in onze studentenvoorbeelden niet per se. We vragen Wieke na hoe er meestal wordt omgegaan met het normaliseren van teksts

Er zijn twee voorname FA's:
- Emre's FA: de core
  - in: genormaliseerde tekst + wav
  - uit: ctm (word level)
- Mario's FA: FA++, de core, maar dan meer!
- Functionaliteit over 1 à 2 weken:
  - Input: platte genormaliseerde tekst files 
  - Input: (optioneel) woorden toevoegen aan lexicon (niet vervangen), .oov.dict
  - Output: geeft (mogelijk lege) oov-lijst
  - Output: phoneem-woord-segmentatie in tg
  - Input: tg, komt later, maar wel nog in dit project. Zijn veel conventies voor nodig. Wel wenselijk, zodat output tg weer terug door de tool gelust kan worden.
- Functionaliteit later, na ons project:
  - time stamps in the middle of text
  - pSIL, pSPN (audio kwaliteit waarschijnlijkheid meegeven, voor zacht uitgesproken woorden)
  - Uitspraakvarianten
  
We gebruiken nu de Emre variant, maar die kan alles wat we willen. De Mario-variant wordt de komende twee weken door Louis gebouwd, genaamd de FA2. Hij brengt hem in 2-daagse sprints online en hij zal uiteindelijk de huidige FA volledig vervangen. De source code bestaat al, maar werkt in Python 2.7. Nu moet alles doorlopen worden om hem te forceren Python 2.7 te gebruiken.

De pipeline verandert in wezen niet bij Mario's versie, dus onze kant is eigenlijk al redelijk af, we kunnen alleen niet testen. Volgende week linken met nieuwe FA2-server.

## Situatie in de tool
Op dit moment worden input templates opgehaald. Beste matchende template wordt gekozen en de input parameters worden aangeboden aan de user. Het later toevoegen van een tg-upload template is dus altijd mogelijk.

Wat als er een fout in de phoneem namen zit?

Wij laten steeds de debug log zien aan de user, maar ook de error.log is te downloaden. Alle fouten door aannames kunnen daarin gezet worden.

We komen tot de conclusie dat het niet handig of noodzakelijk is dat gebruikers g2p output aan kunnen passen. Wel houden we g2p als aparte stap in de pipeline, ter educatieve demonstratie.

## Product review result sprint 2
Klant is tevreden over de gang van zaken afgelopen sprint. Er onstond onzekerheid aan de kant van de klant, want er waren twee versies van de FA.

Het vragen van proefpersonen stond op het schema, maar zijn we uiteindelijk niet aan toegekomen. Tool werkt nog niet volledig, dus user testing kan nog niet echt, want de FA mist. Wel is Wieke een keer door de visuele non-functionele frontend gelopen.

Een kritiek bij de vorige sprint was dat we beslissingen namen zonder met jullie door te spreken. Nu waren er minder beslissingen. De klant had niet het gevoel achter de feiten aan te lopen.

Inlog zit er nu in. Deze zat in de MVP en die is nu af.
Eventueel kunnen we inloggen via science accounts, maar dat doen we niet want de meeste letterenstudenten hebben geen science account.

Hoe ervaarde de klant het contact ondanks Corona?
Zoals het nu verliep was het wel prima, geen groot verschil.

Aanpassing: Nu we richting de deadline werken is wekelijks vergaderen handig.

Louis wil toevoegen dat de tool conceptueel makkelijk lijkt, maar onderwater veel behoorlijk grote designkeuzes en beslissinen genomen moeten worden. Het is ook niet raar dat we in het laatste stadium nog een tweede versie van FA ontdekken. Hij denkt dat we een goede middenweg kiezen: schaalbaar en haalbaar.

## Product requirements collection sprint 3
Sprint 3 eindigt op 10 juni, we hebben dus nog 6 weken.

Komende twee weken gaan we investeren in testing. Dit maakt ons product robuuster en dus later makkelijker uit te bouwen.

Daarna is de FA2 af? Wij sluiten er op aan! Kern geïmplementeerd krijgen. Mogelijk ook tg als input.

Andere eisen?

 - Transcript verbeteren na de FA en praat scripts aanroepen.

 Is lastig om responsive praat scripts in te bouwen. Users kunnen nu alles downloaden op het einde en dan lokaal de praat scripts runnen.

 - LSA?

 Kunnen we bouwen, output als plaatje weergeven in tool. Staat nu op hold. Even afwegen hoe nuttig het is om enkel een non-responsive plaatje te hebben, want een student kan net zo goed alles downloaden en zelf aan de slag gaan.
 
 - Nog kijken naar login

 Is in principe al gebouwd, gewoon nog overheen gaan tijdens de volgende client meeting.
