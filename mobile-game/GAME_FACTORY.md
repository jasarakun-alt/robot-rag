# 🏭 Game Factory — legalni workflow za AI-podprto izdelavo iger

Ponovljiv postopek, kako iz **navdiha uspešne igre** prideš do **svoje objavljive
igre** — brez kršenja avtorskih pravic. Zasnovan za "portfolio" model (veliko
poceni iger → testiraš → obdržiš zmagovalce), poganjan z AI.

## Načelo v enem stavku

> Kopiraš **žanr in mehaniko** (ideje), nikoli **konkretne igre** (izraz).
> Vir je **igranje**, ne dekompilacija.

Ideje (mehanike, pravila, občutek) niso avtorsko zaščitene. Izraz (koda,
struktura, grafika, glasba, ime, prepoznaven videz) je. Ves workflow je zgrajen
tako, da skozi "firewall" prepusti samo ideje.

---

## Zeleno / rdeče

| ✅ Smeš (ideja) | ❌ Ne smeš (izraz) |
|---|---|
| Isti žanr (endless runner, match-3 …) | Dekompilirati APK in brati kodo |
| Iste mehanike in pravila | Kopirati/prevajati strukturo kode (tudi v drug jezik) |
| Isti "game feel" (juice, tempo) | Kopirati grafiko, glasbo, zvoke |
| Podobna težavnostna krivulja | Prevzeti ime igre (blagovna znamka) |
| Svoje like, svoj svet, svoj twist | Posnemati prepoznaven celoten videz (trade dress) |
| Navdih iz več iger hkrati | Rekreirati eno specifično igro 1:1 |

---

## Pipeline (0 → objava)

```
0. VIR        Igro IGRAŠ / gledaš gameplay posnetke.  NIKOLI dekompilacija.
                   │  (skozi firewall gredo samo IDEJE)
                   ▼
1. ANALYST    Agent napiše "Mechanics Spec" — samo vedenje/pravila, brez kode,
              brez imena, brez specifičnih nivojev, brez opisa vizualnega stila.
                   │
                   ▼
2. FILTER     Odstraniš vse, kar identificira KONKRETNO igro (ime, liki, točni
              nivoji, signature look). Ostane generična žanrska mehanika.
                   │
                   ▼
3. BUILDER    Agent implementira SVEŽO kodo (Flutter/Expo) iz speca.
                   │
                   ▼
4. ASSETS     Dodaš SVOJE grafike, glasbo, zvoke + svoj twist + svoje ime.
                   │
                   ▼
5. CLEARANCE  Legal checklist → objava kot tvoje.
```

Ključno: med korakoma 0 in 1 gre skozi **samo tisto, kar vidiš pri igranju**.
To je firewall, ki loči idejo od izraza.

---

## Faza 1 — Mechanics Spec (firewall dokument)

Za vsako igro izpolni tale predlogo. Pravilo: **opisuješ samo opazljivo vedenje.**
Če bi stavek lahko napisal nekdo, ki je igro le igral (ne videl kode) — je OK.

```markdown
# Mechanics Spec: <interno ime tvojega projekta>

## Žanr
<npr. endless runner, one-tap>

## Cilj igralca
<npr. preživeti čim dlje / zbrati čim več točk>

## Osnovni vhod (kontrole)
<npr. en tap = flap navzgor; brez taps = padec>

## Glavne mehanike (pravila vedenja)
- <mehanika 1: kaj se zgodi in kdaj>
- <mehanika 2>
- ...

## Napredovanje / težavnost
<kako igra postaja težja s časom>

## Točkovanje
<kako se štejejo točke / kaj daje bonus>

## Konec igre (fail pogoj)
<kdaj izgubiš>

## Game feel (občutek, ne izgled)
<npr. hitro odziven, "juicy" ob trku, screen-shake, particle>

## PREPOVEDANO v tem specu (preveri, da NI notri):
- [ ] ime originalne igre ali njenih likov
- [ ] opis strukture kode / imena razredov / funkcij
- [ ] točne postavitve konkretnih nivojev iz originala
- [ ] opis prepoznavnega vizualnega stila originala
```

---

## Faza 2 — Design Analyst (ponovljiv prompt za agenta)

> Deluješ kot **game design analyst**. Opisal ti bom mehaniko igre iz žanra
> `<žanr>`, tako kot jo vidim med IGRANJEM. Tvoja naloga: iz tega sestavi
> strukturiran **Mechanics Spec** po predlogi (žanr, cilj, kontrole, mehanike,
> težavnost, točkovanje, fail pogoj, game feel).
>
> STROGA PRAVILA:
> - Opisuj SAMO opazljivo vedenje in pravila (ideje), nikoli implementacije.
> - NE omenjaj imena nobene obstoječe igre, njenih likov ali blagovne znamke.
> - NE opisuj strukture kode, razredov, funkcij ali datotek.
> - NE opisuj prepoznavnega vizualnega stila konkretne igre.
> - Če ti dam kaj od naštetega, to izpusti in me opozori.
>
> Rezultat mora biti generičen za CEL žanr, ne za eno specifično igro.

---

## Faza 3 — Builder (ponovljiv prompt za agenta)

> Deluješ kot **game developer**. Priložen je Mechanics Spec (samo ideje/pravila).
> Implementiraj **popolnoma novo igro v `<Flutter / Expo>`** od nič, ki uresniči
> te mehanike.
>
> PRAVILA:
> - Piši lastno, izvirno kodo; ne reproduciraj nobene tuje strukture.
> - Uporabi placeholder asete (barvni pravokotniki), dokler ne dodam svojih.
> - Koda naj bo modularna, da lahko preprosto menjam vrednosti (težavnost, hitrost).
> - Dodaj vsaj eno izvirno mehaniko, ki je v specu označena kot "twist".
>
> Vhod: <prilepi Mechanics Spec>

---

## Faza 4 — Tvoji asseti (legalni viri)

Grafika, glasba in zvok morajo biti **tvoji ali licencirani**:

| Vrsta | Legalni viri |
|---|---|
| Grafika | sam narediš; Kenney.nl (CC0); itch.io asset packi z licenco; AI-generirano |
| Glasba | Incompetech (CC), FreePD (CC0), licenca na Epidemic/Artlist, AI-glasba |
| Zvočni efekti | Freesound (preveri licenco!), Kenney (CC0), sfxr/bfxr (sam generiraš) |
| Pisave | Google Fonts (odprte licence) |

> Vedno shrani dokazilo o licenci (URL + licenca) za vsak asset — mapa `assets/LICENSES.md`.

---

## Faza 5 — Legal Clearance Checklist (pred objavo)

- [ ] Nisem dekompiliral nobene tuje igre; vir je bilo samo igranje.
- [ ] Koda je izvirna (agent Builder je pisal od nič, ne portal tuje strukture).
- [ ] Vsi asseti so moji ali licencirani (dokazila v `assets/LICENSES.md`).
- [ ] Ime igre ni obstoječa blagovna znamka (preveri Play Store / App Store / trademark register).
- [ ] Igra ne posnema prepoznavnega "look & feel" ene specifične igre (trade dress).
- [ ] Dodal sem vsaj en svoj izviren element (twist), likov/svet imam svoj.
- [ ] Store metadata (ikona, screenshoti, opis) so izvirni.

Če je vseh 7 kljukic → objaviš kot svoje.

---

## Obvezna diferenciacija (tvoj "twist")

Ne le pravno, tudi **poslovno** — čist klon brez razlike se v trgovini izgubi.
Vsaka igra naj ima vsaj eno stvar, ki je original nima. Primeri za endless runner:

- **near-miss bonus** (točke, ko tesno zgrešiš oviro),
- **combo multiplikator** (zaporedni uspehi večajo množitelj),
- **power-upi** (magnet, ščit, upočasnitev časa),
- **daily challenge** z drugačno oviro,
- **svoj karakter/svet** (tvoj robot, tvoja tema).

Twist te hkrati **oddalji od izraza originala** in **naredi igro tržno svojo**.

---

## Worked example: Endless Runner (žanrski spec, brez specifične igre)

```markdown
# Mechanics Spec: Robot Runner

## Žanr
Endless runner, one-tap.

## Cilj igralca
Preživeti čim dlje in nabrati čim več točk.

## Kontrole
Tap kamor koli = robot poskoči/poleti navzgor. Brez tapa = gravitacija ga vleče dol.

## Glavne mehanike
- Robot ostaja na fiksnem x, svet se pomika proti njemu.
- Ovire prihajajo z desne, imajo režo, skozi katero moraš leteti.
- Dotik ovire, tal ali strehe = konec.
- (twist) Near-miss: če tesno zgrešiš oviro, +2 bonus točki in kratek particle blesk.
- (twist) Combo: vsak zaporedni near-miss viša množitelj (x2, x3 ...).

## Napredovanje
Hitrost sveta se s časom rahlo povečuje; reže se postopoma ožajo.

## Točkovanje
+1 na prepotovano oviro; +2 na near-miss; množitelj iz comba.

## Konec igre
Trk z oviro, tlemi ali stropom. Prikaz rezultata + najboljši rezultat.

## Game feel
Takojšen odziv na tap; rahel nagib robota po hitrosti; screen-shake in
particle blesk ob trku; combo pospremi zvočni "ding" z višajočim tonom.
```

Ta spec je varen: opisuje **žanr**, ne konkretne igre, in že vsebuje **tvoja
twista** (near-miss + combo). Robot Runner ga lahko takoj uresniči.

---

## Kako to skalira v tvoj portfolio model

1. Za vsako idejo: 30-minutni Mechanics Spec (Faza 1–2).
2. Builder agent zgenerira igrljiv prototip (Faza 3) — ure, ne tedni.
3. Placeholder asseti → hitri organski test (TikTok/ASO) → CPI/D1 metrike.
4. Ubiješ 90 %, zmagovalcem dodaš prave asete + twist + monetizacijo.
5. Vsaka igra je od začetka **legalno tvoja** → brez tveganja pri skaliranju.

Rezultat: hitrost klon-pristopa, brez pravne izpostavljenosti.
```
