Beste Henk en Helmer,

Dank voor de meeting van gister, wij hebben hem als erg vruchtbaar en leuk ervaren. Het gaf ons beter zicht op het doel van het systeem, en waar jullie naartoe zouden willen gaan. Om dit helemaal zeker te weten zal ik eerst even kort samenvatten wat we gister gezamenlijk hebben besproken. Hierop volgend zal ik de uitkomst van onze brainstorm (met ons engineering team) naar jullie doorzetten zodat jullie inzicht krijgen in onze gang van zaken en waar we naartoe zouden willen bewegen aan de hand van de informatie die we van jullie door hebben gekregen.

Naar aanleiding van ons gesprek hebben we een MOSCOW (must have, should have, could have) analyse gedaan op de mogelijke eisen van het systeem. 

Must have A user friendly and intuitive user interface. All the individual parts working together, seamlessly. The option to export data at each part of the stage. User must be able to manually (re-)align text with modalities at each stage. Use the output of each stage automatically and seamlessly in the next stage.

Should have Support for Grapheenoneem (will get into later) Support various export formats (e.g. CSV) - this is different from the feature in must have, because we would need to convert filetypes.

Could have Automatic segmentation on ‘tone’ level Manipulate data in some ways in the tool (detail to be specified) Support various other variables like speech speed.

Aan de hand van deze eisen stellen wij voor dat we tijdens onze eerste sprint focussen op het opzetten van een eerste basis voor een werkend systeem. Idealiter loopt dit systeem voor de eerste sprint de pipeline door, in een scenario waar alle keuzen op YES vallen. Dit zorgt er dan voor dat we aan het einde van de eerste sprint een minimalistisch maar werken systeem hopen te hebben. Vervolgens is het dan voor toekomstige sprints om verder functionaliteiten van de scripts toe te voegen (daar maken we ons druk over als de tijd daar is).

_________________________________________________

Vervolgens hebben wij vandaag met onze engineers gezeten om te overleggen wat volgens hen de beste keuze zou zijn. We hebben hierbij gekeken naar meerdere oplossingen (virtual machine, lopend UNIX programma, windows application, etc.) en hierbij een afweging gemaakt tussen de twee sterkste spelers uit het lijstje. Aan de ene kant een windows applicatie en aan de andere kant een webserver / webportaal. Hierbij kwamen we op het volgende lijstje van voor- en nadelen:

Windows application
Pros
- Is it easier to code?

Con
- Manageability long term?
- Robustness?
- Have to install
- Manage dependencies of python (it's a 'large' issue - depending on who you ask)


Webserver / webportal
Pros
- User friendliness
- Accessibility

Cons
- Performance?
- Server upkeep, but computation is minimal (because models are pre trained)
- Is it easier to code?

Aan de hand van deze afwegingen is onze keuze gevallen op een Webserver / portal (ofwel een website). Voornamelijk omdat dependency management en version control voor een windows application mogelijk voor moeilijkheden in het onderhoud en de toekomst. Mochten jullie het hier mee eens zijn dan hoor ik het graag, verder kunnen we het tijdens onze meeting, volgende week op Dinsdag 18 Februari, verder hebben over de details van deze implementatie.

Tijdens onze meeting kwam naar voren dat we graag toegang zouden krijgen tot de server waar de scripts staan zodat we meer inzicht hebben in de input en output van de specifieke scripts. Bij deze een lijstje van de studenten die toegang zouden willen:

Lars van Rhijn - l.vanrhijn@student.ru.nl
Lars Willemsen - l.g.willemsen@student.ru.nl
Matti Eisenlohr - matthias.eisenlohr@web.de
David Logtenberg - davidlogtenbergdl@gmail.com
Michel de Boer - m.l.deboer@student.ru.nl
Valentijn Albertus - v.albertus@student.ru.nl

Job van Gerwen - Job.vanGerwen@student.ru.nl	
Wim Fechner - Wim.Fechner@student.ru.nl
Frank Gerlings - Frank.Gerlings@student.ru.nl

Verder werken wij uiteraard door aan het project en bereiden we ons weer voor op het gesprek van volgende week. Mocht het jullie lukken de toegang voor de script server te regelen voor volgende week, dan zou dat heel fijn zijn. Uiteraard begrijpen wij het ook goed als dit een beetje kort dag is allemaal. 

Bij vragen hoor ik het graag. En tot volgende week.

Groet,

Job van Gerwen
