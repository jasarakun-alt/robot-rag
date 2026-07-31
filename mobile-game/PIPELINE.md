# 🏭 Game Factory — celoten pipeline (arhitektura)

End-to-end sistem: od izbire referenčne igre do objavljene lastne igre + portfolio
dashboardi. Zasnovan za "veliko poceni iger → testiraj → obdrži zmagovalce".
Vsi koraki spoštujejo pravilo **ideja, ne izraz** (glej `GAME_FACTORY.md`).

---

## Pregled toka

```
[0] CAPTURE APP ──► [1] LOCAL DB + scaffolding ──► [2] IMPLEMENT (Cursor)
   izbereš igro,        obogaten zapis +               iz spec+testov,
   snemaš, opišeš       per-game direktorij            build → auto na Android
        ▲                                                     │
        │  (korekcije, nova navodila)                         ▼
        └──────────────── [3] ITERACIJA na napravi ◄──── testable verzija
                                     │
                              [GATE 1] ✅ gameplay OK? (človek)
                                     ▼
                    [4] ASSET GEN (lokalno, avtonomno) ──► obvestilo
                                     │
                              [GATE 2] ✅ asseti + build OK? (človek)
                                     ▼
                       [5] PUBLISH (auto-submit v obe trgovini)
                                     │
                                     ▼
     [6] MANAGEMENT DASHBOARD  ◄──── dnevni ETL ────►  [7] MARKETING DASHBOARD
        status + metrike (DAU,                            creative intelligence +
        retention, ARPDAU, revenue)                       generacija oglasov
```

Tri **človeške zapore** (gates) so namerne — posebej pred objavo (store-policy tveganje).

---

## [0] Capture App (dedicirana aplikacija)

**Namen:** izbereš/logiraš referenčno igro, zajameš vedenje, dodajaš navodila in korekcije.

**Kaj je treba narediti:**
- Vnos igre: ime + store link (kot referenca) + tvoje opombe.
- **Screen capture** igranja (Android: `MediaProjection` API).
- **Log tvojih dotikov**: koordinate + timing + gesta (Android: overlay / `adb getevent` / "Pointer location").
- Beleženje korekcij in navodil per-igra (dnevnik).
- **Obogatitev:** video → vision AI → osnutek Mechanics Spec + vedenjski testi.
- Izhod: strukturiran zapis → **lokalna baza** + sproži scaffolding direktorija.

**Tech:** Android app (Kotlin) za capture; lokalna baza (SQLite/Postgres); vision model za obogatitev.

**⚠️ Meja:** zajemaš **samo opazljivi kanal** (video + tvoj input + AI-sklepanje iz videa).
NIKOLI hookov v proces app-a (Frida/memory) — to je dekompilacija in krši EULA.

---

## [1] Lokalna baza + scaffolding

**Kaj:** central "brain" sistema.
- Baza hrani: games, captures, specs, tests, korekcije, status, metrike.
- Ob novem zapisu **auto-ustvari per-game direktorij** iz predloge:
  `/games/<slug>/` → `spec.md`, `tests/`, `assets/` (placeholder), app skeleton (Expo/Flutter).

**Tech:** watcher/daemon (Node/Python) + template repo + DB.

---

## [2] Implementacija (Cursor / Claude)

**Kaj:** direktorij (spec + testi) predaš Cursorju (cenejši za implementacijo).
- TDD: implementira, da **prestane vedenjske teste**.
- Izhod: testable build.
- **Auto na Android:** build (EAS / `expo run:android` / gradle) → `adb install` na napravo.

**Tech:** Cursor + build/deploy skripta.

**⚠️ Meja:** implementacija iz **spec/testov (ideje)**, ne iz dekompilirane kode.

---

## [3] Iteracija na napravi

Igraš testable build, prek Capture App logiraš korekcije → nazaj v DB → nazaj Cursorju.
Ponavljaš, dokler gameplay ni dober.

**[GATE 1 — človek]:** gameplay OK? (ali prej poceni CPI/D1 test — placeholder-first princip).
Samo zmagovalci gredo na asset generacijo.

---

## [4] Asset generacija (lokalno, avtonomno)

**Kaj:** ob potrditvi → asset pipeline steče avtonomno.
- `asset-manifest.json` (seznam sprite-ov + stil) → lokalni SD (ComfyUI) → post-process
  (rembg brisanje ozadja, trim, palette-snap) → `assets/` + log prompt/seed/licenca.
- **Konsistenca stila:** fiksni style-prompt + seed + style LoRA / IP-Adapter.
- **Obvestilo** ko končano (push/email/desktop).

**Tech:** ComfyUI API orkestrator na Mac M4; rembg; notifier.

**[GATE 2 — človek]:** asseti + poln build OK?

---

## [5] Publish (auto-submit)

**Kaj:** auto-oddaja v obe trgovini.
- Android: Google Play Developer API / fastlane `supply` / EAS Submit → `.aab`.
- iOS: App Store Connect API / fastlane `deliver` / EAS Submit → `.ipa`.

**⚠️ Realnost (pomembno):**
- "Auto-publish" = auto-**submit**. Obe trgovini še vedno **pregledata** (ure–dni).
- **Prva objava** rabi ročno nastavitev store listinga (ikona, opis, screenshoti, privacy
  policy, content rating, data-safety obrazec) — delno avtomatizirano, prvič delno ročno.
- **NAJVEČJE tveganje modela:** množična produkcija podobnih iger → Google
  "Repetitive Content / Copycat", Apple "Spam (4.3)" → **ban razvijalskega računa**.
  Blažitev: resnična diferenciacija + kakovostni prag + človeška zapora. To je razlog,
  da GATE pred objavo ostane človeški.

---

## [6] Management Dashboard

**Kaj:** portfolio pregled.
- Status vsake igre (spec → build → test → assets → published).
- Metrike: installs, DAU, retention (D1/D7/D30), ARPDAU, revenue.
- **Dnevni update** prek scheduled ETL.

**Viri podatkov (API):** Google Play Console API, App Store Connect API, ad-network API
(AdMob/ironSource/AppLovin), analytics (Firebase/GameAnalytics).

**Tech:** web dashboard (Next.js) + backend + cron ETL → DB.

---

## [7] Marketing Dashboard

**Kaj:** creative intelligence + generacija oglasov.
- **Ad intelligence:** iz javnih knjižnic (Meta Ad Library API, TikTok Creative Center)
  analiziraš **vzorce** uspešnih oglasov konkurentov (hook v prvih 2 s, dolžina, struktura).
- **Creative generator:** tvojo igro posnameš prek **emulatorja** → izrežeš gameplay klipe →
  AI sestavi **izvirne** oglasne variante (hook, tekst, glasba — vse tvoje/licencirano).
- **Test harness:** kreative na ad platforme → sledi CTR/CPI/IPM/ROAS, dnevno.

**⚠️ Meja (kritično):** "poveži Voodoo igro + njihove oglase, naredi **enake** oglase" =
kopiranje tuje kreative = **kršitev avtorskih pravic** (njihov posnetek, montaža, glasba).
Dovoljeno: **analiza vzorcev → izvirne kreative iz TVOJEGA gameplaya (emulator).** Ista
ideja/izraz črta kot pri igrah. Emulator-capture **lastne** igre je čisto.

**Tech:** Meta Ad Library API; emulator (Android Studio AVD) + ffmpeg za klipe; AI montaža.

---

## Cross-cutting (skupno)

- **Orkestracija:** central controller (n8n / Temporal / lasten daemon) koordinira faze + gate.
- **Obvestila:** push/email na vsaki zapori.
- **Storage:** lokalna DB + object storage za videe/assete.
- **Human-in-the-loop:** 3 zapore (gameplay, asseti, objava) — objava vedno človeška.

---

## Priporočen vrstni red gradnje (ne vsega naenkrat!)

Cel sistem je velik. Solo dev naj gradi inkrementalno — vsaka faza je uporabna sama zase:

| Faza | Zgradiš | Rezultat |
|---|---|---|
| **MVP** | ročni capture (opis+video) + Game Factory + 1 igra do objave | dokažeš cel tok ročno |
| **v1** | scaffolding + Cursor build + `adb install` | igra → telefon avtomatsko |
| **v2** | Capture App (Android) | zajem namesto ročnega opisa |
| **v3** | asset-pipeline (ComfyUI orkestrator) | avtonomni asseti |
| **v4** | management dashboard + ETL | dnevne metrike |
| **v5** | auto-submit (fastlane/EAS) | objava iz sistema |
| **v6** | marketing dashboard | creative pipeline |

> Pravilo: ne avtomatiziraj koraka, dokler ga nisi 2–3× naredil ročno. Večina vrednosti
> je v MVP + v1.

---

## Povzetek pravnih zapor (ne spreglej)

1. **Capture** = samo opazljivi kanal (video + tvoj input + AI-inference). Brez hookov.
2. **Igre** = klon žanra/mehanike + obvezna diferenciacija (6-točkovni checklist v `GAME_FACTORY.md`).
3. **Store policy** = copycat/spam/repetitive → ban računa. Kakovost + diferenciacija + človeška zapora.
4. **Oglasi** = analiza vzorcev, IZVIRNE kreative iz lastnega gameplaya. Ne kopiraj tujih.
5. **Auto-publish** = auto-submit; review še vedno velja; prvi listing delno ročno.
