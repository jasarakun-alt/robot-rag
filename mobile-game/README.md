# 🤖 Robot Runner

Endless-runner mobilna igra (v slogu Flappy Bird), zgrajena z **Expo / React Native**.
Tapni za let, izogibaj se oviram in leti čim dlje. Ista koda teče na **Androidu**,
**iOS-u** in v **brskalniku**, kar omogoča objavo v Google Play in App Store iz enega
projekta.

> Status: **igrljiv prototip**. Igralna zanka, fizika, ovire, štetje točk, trki in
> shranjevanje najboljšega rezultata delujejo. Naslednji korak so ikone, splash screen
> in oddaja v trgovine (glej spodaj).

---

## Kako igraš

- **Tapni kamor koli** (ali klikni v brskalniku), da robot poleti navzgor.
- Gravitacija te vleče dol — tapkaj ritmično, da ostaneš v zraku.
- Leti skozi reže med ovirami. Vsaka prepotovana ovira = +1 točka.
- Dotik ovire, tal ali strehe = konec igre. Tapni za novo igro.

---

## Zaženi lokalno (razvoj)

Potrebuješ [Node.js](https://nodejs.org/) 18+.

```bash
cd mobile-game
npm install
```

**V brskalniku (najhitrejši preizkus):**

```bash
npm run web
```

**Na telefonu prek Expo Go:**

```bash
npm start
```

Nato skeniraj QR kodo z aplikacijo [Expo Go](https://expo.dev/go)
(Android / iOS). Igra se naloži takoj, brez namestitve.

---

## Zgradi pravo aplikacijo za trgovine

Objava poteka prek **EAS Build** (Expo Application Services) — zgradi native
`.aab` (Google Play) in `.ipa` (App Store) v oblaku, tako da ne potrebuješ Mac-a
za iOS build.

### 1. Priprava (enkratno)

```bash
npm install -g eas-cli
eas login                # potrebuješ brezplačen Expo račun
eas build:configure
```

### 2. Zamenjaj privzete vrednosti

V `app.json` posodobi:

- `expo.ios.bundleIdentifier` in `expo.android.package` — svoj enolični ID
  (npr. `com.tvojeime.robotrunner`).
- Dodaj ikone in splash screen v mapo `assets/` ter jih poveži v `app.json`
  (`icon`, `splash`). Priporočeno: `icon.png` 1024×1024.

### 3. Build

```bash
eas build --platform android --profile production   # ustvari .aab
eas build --platform ios --profile production       # ustvari .ipa
```

### 4. Oddaja v trgovine

```bash
eas submit --platform android   # naloži v Google Play Console
eas submit --platform ios       # naloži v App Store Connect
```

> **Kaj moraš priskrbeti sam:** razvijalski račun za
> [Google Play](https://play.google.com/console) (enkratnina 25 USD) in
> [Apple Developer Program](https://developer.apple.com/programs/) (99 USD/leto),
> ime aplikacije, opis, posnetke zaslona in oceno starostne primernosti.
> Claude te lahko vodi skozi vsak korak.

---

## Struktura

| Datoteka | Namen |
|----------|-------|
| `App.js` | Celotna igra: fizika, ovire, štetje točk, trki, zasloni |
| `app.json` | Konfiguracija Expo aplikacije (ime, ID-ji, orientacija) |
| `eas.json` | Build profili za EAS (development / preview / production) |
| `package.json` | Odvisnosti in skripte |
| `assets/` | Ikone in splash (dodaj pred objavo) |

## Nastavljivi parametri igre

Na vrhu `App.js` so konstante, s katerimi uravnavaš občutek igre:
`GRAVITY`, `FLAP_VELOCITY`, `OBSTACLE_SPEED`, `GAP_HEIGHT`, `OBSTACLE_SPACING` …
