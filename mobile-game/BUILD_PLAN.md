# 🗺️ Game Factory — celoten build plan (od začetka do konca)

**Namen tega dokumenta:** samostojen načrt za izgradnjo celotnega sistema. Vzemi ga v
nov (lokalen) chat z dediciranim direktorijem in gradi po fazah. Dokument je zasnovan
tako, da ga razume agent **brez konteksta prejšnjega pogovora**.

Spremljajoča dokumenta (ista mapa):
- `GAME_FACTORY.md` — legalni idea-vs-expression workflow + prompti za agente.
- `PIPELINE.md` — arhitektura sistema (komponente + tok).

---

## 0. Cilj sistema

Polavtomatska "tovarna iger": iz izbrane referenčne igre (kot **navdih**, ne kopija)
prideš do **lastne objavljive mobilne igre**, in to v velikem obsegu (portfolio model:
veliko poceni iger → testiraš → obdržiš zmagovalce). Sistem vključuje zajem, generacijo,
implementacijo, testiranje na napravi, generacijo assetov, objavo ter management in
marketing dashboard.

---

## 1. Temeljna pravila (PREBERI PRVO — pravna varnost)

Cel sistem stoji na eni ločnici: **kopiraš IDEJO (mehaniko/žanr), nikoli IZRAZA
(kodo/grafiko/glasbo/ime/videz).**

| ✅ Smeš (ideja) | ❌ Ne smeš (izraz) |
|---|---|
| isti žanr in mehanike | dekompilirati APK / brati tujo kodo |
| isti "game feel" | kopirati ali prevajati strukturo kode (tudi v drug jezik) |
| navdih iz igranja/videa | kopirati grafiko, glasbo, zvoke, ime |
| svoji liki, svet, twist | posnemati prepoznaven celoten videz (trade dress) |

**Štiri operativne zapore (nujno):**
1. **Capture:** samo opazljivi kanal (video + tvoji taps + AI-sklepanje iz videa). Brez
   hookov v proces app-a (Frida/memory) — to je dekompilacija.
2. **Igre:** klon žanra + **obvezna diferenciacija** (6-točkovni checklist spodaj).
3. **Store policy:** množica podobnih iger → Google "Copycat/Repetitive", Apple "Spam 4.3"
   → **ban računa**. Zato objava ostane **človeška zapora** + resnična diferenciacija.
4. **Oglasi:** analiziraš **vzorce** konkurentov → generiraš **izvirne** kreative iz
   **svojega** gameplaya (emulator). Nikoli ne kopiraj tuje kreative.

**Diferenciacijski checklist (per igra, pred objavo):**
- [ ] svoja umetniška smer (ne prebarvana kopija)
- [ ] svoje ime (preveri trademark / store)
- [ ] svoj level design (svoji nivoji ali proceduralno)
- [ ] svoj tuning (konstante po svojem občutku, ne prepisane)
- [ ] vsaj en svoj twist (mehanika, ki je original nima)
- [ ] svoj UI/UX layout + store metadata

---

## 2. Tehnološke odločitve (fiksne za ta plan)

| Področje | Izbira | Zakaj |
|---|---|---|
| Game framework | **Expo / React Native** | EAS zgradi **in odda** v obe trgovini iz ene kode; web preview za hiter test; že obstaja delujoč prototip (Robot Runner) |
| (alternativa) | Flutter + Flame | boljši za zahtevnejše igre; zamenljivo, a ni privzeto |
| Implementacija | **Cursor** (cenejši) za kodo, Claude za spec/plan | |
| Lokalna baza | **SQLite** (MVP) → Postgres (kasneje) | |
| Orkestrator | Node/TypeScript daemon + BullMQ (job queue) | |
| Asset gen | **ComfyUI** (API) na Mac M4 + Python orkestrator + `rembg` | |
| Dashboardi | **Next.js** (management + marketing, isti DB) | |
| Build & submit | **EAS Build + EAS Submit** / fastlane | |
| Capture app | **Android native (Kotlin)** — MediaProjection + touch log | |
| Vision/LLM | Claude API (obogatitev, spec), lokalni LLM opcijsko | |

---

## 3. Ciljna struktura repozitorija (monorepo)

```
game-factory/
├── apps/
│   ├── capture-android/       # Kotlin capture app            (Faza v2)
│   └── dashboard/             # Next.js management+marketing  (Faze v4, v6)
├── packages/
│   ├── core/                 # DB, schema, orkestrator, tipi
│   ├── asset-pipeline/       # ComfyUI orkestrator + rembg    (Faza v3)
│   └── game-template/        # Expo per-game predloga         (Faza v1)
├── games/
│   ├── robot-runner/         # prva igra                      (MVP)
│   └── <slug>/               # generirane igre
└── docs/
    ├── GAME_FACTORY.md
    ├── PIPELINE.md
    └── BUILD_PLAN.md         # ta dokument
```

---

## 4. Skica podatkovne baze (jedro)

```
games(id, slug, ref_name, ref_link, status, created_at)
captures(id, game_id, video_path, input_log_path, notes, created_at)
specs(id, game_id, mechanics_md, created_at)
tests(id, game_id, test_path, kind)               -- behavioral
corrections(id, game_id, text, created_at, resolved)
builds(id, game_id, platform, artifact_path, status, installed_at)
assets(id, game_id, path, prompt, seed, license, created_at)
publications(id, game_id, platform, store_status, submitted_at, live_at)
metrics_daily(id, game_id, date, installs, dau, d1, d7, d30, arpdau, revenue)
ad_creatives(id, game_id, path, hook_type, status)
ad_metrics_daily(id, creative_id, date, impressions, ctr, cpi, ipm, roas)
```

---

## 5. Faze (od začetka do konca)

> Pravilo: **ne avtomatiziraj koraka, dokler ga nisi 2–3× naredil ročno.** Vsaka faza je
> uporabna sama zase. Večina vrednosti je v MVP + v1.

### Faza 0 — Setup
**Cilj:** prazen monorepo, ki se zgradi in požene.
- [ ] init monorepo (pnpm workspaces ali turborepo)
- [ ] `packages/core`: SQLite + shema (poglavje 4) + migracije
- [ ] skupni tipi (TypeScript) za game/spec/test/build
- [ ] CLI skeleton (`gf <command>`) za ročno vodenje pipelinea
- **Done-when:** `gf init-db` ustvari bazo; `gf list` deluje.

### Faza MVP — Game Factory ročno + 1 igra do objave
**Cilj:** dokazati **cel tok** ročno na eni igri (Robot Runner).
- [ ] napiši **Mechanics Spec** (glej `GAME_FACTORY.md`, worked example) za endless runner
- [ ] napiši **vedenjske teste** (žanrski: gravitacija, flap, trk, točkovanje, near-miss)
- [ ] implementiraj igro v Expo, da prestane teste (near-miss + combo twist)
- [ ] placeholder asseti → preizkusi na napravi (`expo start` / dev build)
- [ ] generiraj prave assete (ročno, ComfyUI) + ikono + splash
- [ ] `app.json` (bundle ID-ji), EAS build (`.aab` + `.ipa`)
- [ ] ročno oddaj v Google Play (internal testing) + TestFlight
- **Done-when:** igra je igrljiva na tvojem Androidu in oddana vsaj v internal testing.

### Faza v1 — Scaffolding + Cursor build + auto-deploy
**Cilj:** iz spec/testov avtomatsko do buildane igre na telefonu.
- [ ] `packages/game-template`: parametriziran Expo template
- [ ] `gf new <slug>`: ustvari `games/<slug>/` iz template + zapis v DB
- [ ] handoff paket za Cursor (spec + testi + template) v direktoriju
- [ ] build+deploy skripta: `gf build <slug>` → EAS/gradle → `adb install`
- **Done-when:** `gf new x` → (Cursor implementira) → `gf build x` → igra na telefonu.

### Faza v2 — Capture App (Android)
**Cilj:** zajem namesto ročnega opisa.
- [ ] `apps/capture-android` (Kotlin): MediaProjection screen record
- [ ] touch logging (overlay / getevent) → časovni žigi
- [ ] vnos igre + opombe + dnevnik korekcij
- [ ] upload v lokalni DB (video + input log + notes)
- [ ] obogatitev: pošlji video Claude vision API → osnutek spec + testi
- **Done-when:** posnetek igranja → obogaten zapis + `games/<slug>/` direktorij samodejno.

### Faza v3 — Asset pipeline (lokalno, avtonomno)
**Cilj:** avtonomni asseti za potrjene igre.
- [ ] `packages/asset-pipeline`: `asset-manifest.json` shema
- [ ] ComfyUI API orkestrator (prompt → gen → best-of-N)
- [ ] post-process: `rembg` (ozadje), trim, palette-snap
- [ ] konsistenca stila: fiksni style-prompt + seed + LoRA/IP-Adapter
- [ ] obvestilo ob koncu (desktop/push)
- **Done-when:** `gf assets <slug>` → mapa `assets/` napolnjena + obvestilo.

### Faza v4 — Management dashboard
**Cilj:** dnevni pregled portfolia.
- [ ] `apps/dashboard` (Next.js), bere skupni DB
- [ ] pogled: status vsake igre (spec→build→test→assets→published)
- [ ] metrike: installs, DAU, D1/D7/D30, ARPDAU, revenue
- [ ] ETL (cron): Google Play Console API + App Store Connect API + ad-network API
- **Done-when:** dashboard kaže dnevno osvežene metrike vseh iger.

### Faza v5 — Auto-submit
**Cilj:** objava iz sistema (za človeško zaporo).
- [ ] EAS Submit / fastlane `supply` (Android) + `deliver` (iOS)
- [ ] store metadata generator (naslov, opis, screenshoti iz emulatorja)
- [ ] `gf publish <slug>` — po ročni potrditvi
- **Done-when:** potrjena igra se odda v obe trgovini z enim ukazom.
- **⚠️ Opomni:** auto-**submit**, ne instant-live; review velja; prvi listing delno ročen.

### Faza v6 — Marketing dashboard
**Cilj:** creative intelligence + generacija izvirnih oglasov.
- [ ] ad intelligence: Meta Ad Library API / TikTok Creative Center — **analiza vzorcev**
- [ ] emulator (Android Studio AVD) capture tvoje igre → gameplay klipi (ffmpeg)
- [ ] AI montaža **izvirnih** kreativ (hook, tekst, glasba — tvoje/licencirano)
- [ ] test harness: kreative → ad platforme → CTR/CPI/IPM/ROAS, dnevno
- **Done-when:** dashboard generira ready-to-publish izvirne kreative + sledi metrikam.
- **⚠️ Meja:** samo vzorci + tvoj gameplay; nikoli tuja kreativa.

---

## 6. Cross-cutting (skozi vse faze)

- **Orkestracija:** central daemon + job queue; 3 človeške zapore (gameplay, asseti, objava).
- **Obvestila:** ob vsaki zapori (desktop/push, kasneje email).
- **Secrets:** store API ključi, ad-network ključi — v `.env`, nikoli v git.
- **Licenčni log:** vsak asset → `assets/LICENSES.md` (vir + licenca; self-generated velja).

---

## 7. Prvi konkretni koraki za novi chat

1. Ustvari dediciran direktorij + git repo `game-factory/`.
2. Kopiraj `GAME_FACTORY.md`, `PIPELINE.md`, `BUILD_PLAN.md` v `docs/`.
3. Začni **Fazo 0** (monorepo + DB shema + CLI skeleton).
4. Nato **Faza MVP** na Robot Runnerju (spec → testi → implementacija → asseti → oddaja).
5. Šele ko MVP teče od začetka do konca, pojdi na v1.

> Robot Runner prototip (Expo) že obstaja kot izhodišče za MVP — glej `App.js` v tej mapi.

---

## 8. Definicija končanega sistema

- Iz Capture App posnameš navdih → dobiš spec + testi + direktorij.
- Cursor implementira → testable igra se sama namesti na Android.
- Prek Capture App logiraš popravke; ob potrditvi stečejo asseti (obvestilo).
- Po pregledu potrdiš → auto-submit v obe trgovini.
- Management dashboard kaže dnevne metrike; marketing dashboard generira izvirne oglase.
- Vse ob spoštovanju 4 pravnih zapor in diferenciacijskega checklista.
```
