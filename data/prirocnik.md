# Priročnik izobraževalnega robota

Ta priročnik vsebuje osnovne informacije o senzorjih, motorjih, baterijah, varnosti in programiranju izobraževalnega robota. Namenjen je učencem, ki se učijo robotike. Vsako poglavje je zaokrožena celota.

## O robotu in priročniku

Izobraževalni robot je naprava, ki združuje senzorje, motorje, krmilnik (majhen računalnik) in baterijo. Senzorji zaznavajo okolico, krmilnik se na podlagi programa odloča, motorji pa izvedejo gibanje. Ta krog "zaznaj – odloči – ukrepaj" se ponavlja mnogokrat na sekundo. Robot sam po sebi ni pameten; naredi točno to, kar mu naročimo s programom. Zato je dobro razumeti vsak del posebej, preden jih povežemo v celoto.

## Senzorji – kaj so in čemu služijo

Senzor je naprava, ki neko fizikalno količino (razdaljo, svetlobo, dotik, temperaturo) pretvori v električni signal, ki ga krmilnik lahko prebere. Senzorji so robotu to, kar so človeku oči, ušesa in koža. Brez senzorjev bi se robot premikal "na slepo". Ločimo digitalne senzorje, ki vrnejo le vrednost 0 ali 1 (na primer gumb: pritisnjen ali ne), in analogne senzorje, ki vrnejo zvezno vrednost v nekem območju (na primer svetlobni senzor). Pri priklopu je vedno treba paziti na pravilno napajalno napetost senzorja (običajno 3,3 V ali 5 V) in na pravi podatkovni priključek.

## Ultrazvočni senzor

Ultrazvočni senzor meri razdaljo do ovire s pomočjo zvoka, ki ga človek ne sliši (frekvenca nad 20 kHz, pogosto okoli 40 kHz). Senzor odda kratek zvočni impulz in meri čas, ki ga odboj (eho) potrebuje za vrnitev. Ker je hitrost zvoka v zraku približno 343 metra na sekundo, lahko iz izmerjenega časa izračuna razdaljo. Pogost model HC-SR04 zanesljivo meri razdalje od približno 2 cm do 4 m. Robot ultrazvočni senzor uporablja, da se izogne trkom, da se ustavi pred steno ali da ohranja stalno razdaljo do predmeta. Senzor je manj natančen pri mehkih, tankih ali poševnih površinah, ki zvok razpršijo namesto da bi ga odbile.

## Infrardeči senzor in sledilnik črte

Infrardeči (IR) senzor oddaja in zaznava infrardečo svetlobo, ki je s prostim očesom ne vidimo. Uporablja se za zaznavanje bližnjih predmetov in zelo pogosto za sledenje črti. Sledilnik črte deluje tako, da temna podlaga infrardečo svetlobo vpije (malo odboja), svetla podlaga pa jo odbije (veliko odboja); iz razlike robot ugotovi, ali je nad črto ali ob njej. Z več IR senzorji v vrsti lahko robot vozi po črti in pravočasno popravi smer. IR senzorji so občutljivi na močno sončno svetlobo in na barvo ter sijaj podlage, zato jih je pogosto treba umeriti (kalibrirati) za prostor, v katerem robot vozi.

## Senzor dotika in svetlobni senzor

Senzor dotika je v osnovi stikalo: ko se robot dotakne ovire, se stikalo sklene in krmilnik dobi signal "dotik". Uporaben je kot zadnja varovalka pred trkom ali za zaznavanje robov in gumbov. Svetlobni senzor (fotoupor ali fototranzistor) meri jakost svetlobe v okolici in vrne analogno vrednost; robot ga lahko uporabi za sledenje svetlobi, zaznavanje dneva in noči ali razločevanje svetle in temne podlage. Oba senzorja sta preprosta in zanesljiva, zato sta primerna za prve projekte.

## Motorji – kako robot premika dele

Robot uporablja motorje za poganjanje koles, rok, prijemal in drugih gibljivih delov. Najpogosteje srečamo tri vrste. Enosmerni (DC) motor se hitro vrti in poganja kolesa; njegovo hitrost in smer krmilimo z napetostjo in njeno polariteto. Servo motor zavrti gred na natančno določen kot (običajno med 0 in 180 stopinjami) in je primeren za obračanje senzorja ali stiskanje prijemala. Koračni (stepper) motor se vrti po majhnih, natančno odmerjenih korakih in je uporaben, kadar potrebujemo natančen zasuk brez dodatnega senzorja položaja. Z dvema neodvisno gnanima kolesoma robot zavija tako, da eno kolo poganja hitreje od drugega (diferencialni pogon).

## Krmiljenje motorjev (hitrost in smer)

Krmilnik motorja ne napaja neposredno, saj motor potrebuje več toka, kot ga zmore dati priključek mikrokrmilnika. Zato med njiju vključimo gonilnik motorja (na primer čip H-most, kot je L298N). H-most omogoča, da motorju spremenimo smer vrtenja tako, da obrnemo polariteto napetosti. Hitrost krmilimo s pulzno-širinsko modulacijo (PWM): napajanje zelo hitro vklapljamo in izklapljamo, razmerje vklopljenega časa pa določa povprečno moč in s tem hitrost. Pri zagonu motor potegne največji (zagonski) tok, zato mora biti napajanje dovolj zmogljivo, da se napetost ne sesede.

## Baterije – vrste in osnovne lastnosti

Baterija je vir energije, ki robotu omogoča delovanje brez kabla. Pri izobraževalnih robotih so pogoste alkalne baterije (za enkratno uporabo), NiMH polnilne baterije (varne in trpežne) ter litij-ionske in LiPo baterije (lahke in zmogljive, a zahtevajo več previdnosti). Dve glavni oznaki sta napetost v voltih (V), ki mora ustrezati robotu, in kapaciteta v miliamperskih urah (mAh), ki pove, kako dolgo bo robot deloval. Višja kapaciteta pomeni daljše delovanje, a tudi večjo in težjo baterijo. Vedno uporabimo baterijo s pravo napetostjo, saj previsoka napetost lahko poškoduje elektroniko, prenizka pa povzroči nezanesljivo delovanje.

## Baterije – varnost in polnjenje

Pri bateriji je treba paziti na nekaj pomembnih stvari. Polov baterije nikoli ne smemo kratko stikati (povezati plus in minus neposredno), saj se baterija močno segreje in lahko zagori. Baterijo vstavimo s pravilno polariteto (plus na plus, minus na minus), sicer lahko uničimo robota. Polnilne baterije polnimo le z ustreznim polnilnikom za njihovo vrsto; navadnih (alkalnih) baterij za enkratno uporabo nikoli ne polnimo. Baterije ne prebadamo, ne segrevamo in ne potapljamo v vodo, LiPo baterij pa ne puščamo napihnjenih ali poškodovanih v uporabi. Pred sestavljanjem ali popravljanjem robota baterijo vedno odklopimo, baterije pa hranimo na suhem in pri sobni temperaturi. Iztrošene baterije oddamo v zbiralnik za baterije in ne med navadne odpadke.

## Varna uporaba robota v razredu

Robota v razredu vedno uporabljamo pod nadzorom učitelja in po dogovorjenih pravilih. Pred sestavljanjem ali spreminjanjem vezja odklopimo baterijo, da se izognemo kratkemu stiku. Prste, lase in ohlapna oblačila držimo stran od koles, zobnikov in drugih gibljivih delov, ki lahko ujamejo. Delovno mizo imejmo pospravljeno in suho; hrane in pijače ne postavljamo blizu elektronike, saj tekočina povzroči kratek stik. Robota ne postavljamo na rob mize, da ne pade in koga ne poškoduje. Pri spajkanju nosimo zaščitna očala in pazimo na vroč spajkalnik. Po končanem delu robota izklopimo, baterijo po potrebi odklopimo in pospravimo dele na svoje mesto.

## Osnove programiranja robota

Program je zaporedje navodil, ki robotu pove, kaj naj naredi. Večina programov za robote sledi zanki "zaznaj – odloči – ukrepaj": robot prebere senzorje, se na podlagi vrednosti odloči in nato krmili motorje. Pri odločanju uporabljamo pogojne stavke (če je razdalja manjša od 10 cm, zavij), za ponavljanje pa zanke (dokler je gumb pritisnjen, vozi naprej). Vrednosti senzorjev shranjujemo v spremenljivke, ponavljajoče se postopke pa zapišemo v funkcije, da je program preglednejši. Začetniki pogosto programirajo v blokovnih okoljih (na primer Scratch ali podobno), naprednejši pa v jezikih, kot sta Python ali C++. Dober postopek je, da program pišemo po majhnih korakih in vsakega sproti preizkusimo.

## Povezovanje komponent – kaj smemo in česa ne

Pri povezovanju komponent je najpomembnejše pravilo, da se ujemata napetost in polariteta. Senzor s 3,3 V se ne sme priključiti neposredno na 5 V priključek, če tega izrecno ne dopušča, sicer se lahko pokvari. Motorjev nikoli ne priključimo neposredno na podatkovni priključek krmilnika, saj ta ne zmore dovolj toka; vedno uporabimo gonilnik motorja z lastnim napajanjem. Skupna masa (GND) vseh delov mora biti povezana, sicer signali ne delujejo pravilno. Plusa in minusa napajanja nikoli ne povežemo neposredno skupaj (kratek stik). Spodnja preglednica povzema nekaj osnovnih pravil.

| Želim povezati | Pravilno | Pozor / ne počni |
| --- | --- | --- |
| Senzor (3,3 V) | Na 3,3 V napajanje in podatkovni priključek | Ne na 5 V, če ni izrecno dovoljeno |
| DC motor | Prek gonilnika (H-most) z ločenim napajanjem | Ne neposredno na priključek krmilnika |
| Servo motor | Signal na PWM priključek, napajanje ločeno | Ne napajaj velikega serva iz krmilnika |
| Baterija | Plus na plus, minus na minus, prek stikala | Nikoli ne kratko stikaj polov |
| Več naprav | Vse mase (GND) poveži skupaj | Ne mešaj napetostnih nivojev brez pretvornika |

## Pogosta vprašanja (FAQ)

Zakaj se robot ne premika? Najprej preverimo baterijo (napetost in ali je vključena), nato priklop motorjev in gonilnika ter ali program sploh pošilja ukaz motorjem. Zakaj senzor vrača čudne vrednosti? Pogosto je kriva napačna napetost, slab stik ali motnje iz okolice; pomaga umerjanje (kalibracija) in preverjanje žic. Kako dolgo zdrži baterija? Odvisno od kapacitete (mAh) in porabe motorjev; več motorjev in večja hitrost pomenita krajše delovanje. Ali lahko robota pustim vključenega? Ne; po uporabi ga izklopimo, da varčujemo z baterijo in se izognemo pregrevanju.
