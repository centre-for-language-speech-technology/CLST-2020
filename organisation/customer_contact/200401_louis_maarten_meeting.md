# Meeting met Louis en Maarten

## Text file conversion
Text files dienen lowercase en zonder interpunctie te zijn. Onze webapp zal dit van de user input strippen. Het is technisch gezien mogelijk om de originele input aan de user te laten zien, maar dat wordt wat lastig bij het live bewerken net na de forced alignment, dus we laten het voorlopig achterwege.

## Dictionary updating
FA kan op dit moment nog maar één wav en één text file tegelijk aan. (Dit wordt op korte termijn uitgebreid tot lijsten.)
Kanttekening is dat de wav en text file dezelfde naam moeten hebben. Hier checken we in de webinterface al op.

Wanneer de FA wordt gerund met een text file waar niet alle woorden worden herkend, dan zal hij een lijst met Out Of Vocabulary (oov) woorden terugsturen in een .oov-file. (Op dit moment nog niet in werking, maar binnenkort wel.)

Deze .oov-file kan worden uitgebreid tot een .oov.dict-file, een dictionary die specifiek de missende woorden bevat. Dit doen we door hem door [de Grapheme2Phoneme converter](https://webservices-lst.science.ru.nl/g2pservice) te halen. Hierdoor voorkomen we ook dat de gebruiker het specifieke fonetische alfabet moet kennen. Upload je de .wav, text en .oov.dict, dan zal de .oov.dict toegevoegd worden aan de dictionary.

## Analysis
Labeled Segment Analysis op woord niveau bestaat al als CLAM service, dus die kunnen we waarschijnlijk snel toevoegen. Op foneem niveau bestaat hij nog niet, deze zullen op een lagere prioriteit zetten en eventueel op termijn zelf in een CLAM-server zetten.

Uitgebreide API documentatie is te vinden op [de info pages van iedere webservice](https://webservices-lst.science.ru.nl/forcedalignment/info/).
