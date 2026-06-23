"""Sestava promptov: odgovarjanje (samo-iz-konteksta) in prevajanje."""
from __future__ import annotations

from typing import Dict, List

SYSTEM_RULES = (
    "Si prijazen pomočnik, ki učencem pomaga pri učenju robotike. "
    "Spodaj dobiš KONTEKST – odlomke iz priročnika, izbrane kot najbolj relevantne za vprašanje. "
    "Odgovori na vprašanje IZKLJUČNO na podlagi tega konteksta in si ne izmišljuj podatkov. "
    "Če kontekst vsebuje odgovor (tudi delno), ga uporabi in odgovori jasno. "
    "Samo če kontekst z vprašanjem res ni povezan, napiši: 'Tega v priročniku ne najdem.' "
    "in prijazno predlagaj, naj učenec vpraša učitelja. Odgovori kratko in jasno."
)


def _language_line(language: str) -> str:
    return f"Piši VEDNO v jeziku: {language}. Nikoli ne preklapljaj v drug jezik."


def format_context(contexts: List[Dict]) -> str:
    if not contexts:
        return "(ni najdenega konteksta)"
    parts = []
    for i, c in enumerate(contexts, 1):
        parts.append(f"[{i}] {c['title']}\n{c['text']}")
    return "\n\n".join(parts)


def _user_turn(contexts_text: str, question: str, language: str) -> str:
    return (
        f"KONTEKST (odlomki iz priročnika):\n{contexts_text}\n\n"
        f"VPRAŠANJE: {question}\n\n"
        f"Navodilo: odgovori IZKLJUČNO v jeziku '{language}' in samo na podlagi konteksta zgoraj.\n"
        "ODGOVOR:"
    )


# Few-shot primera (pomagata predvsem majhnim modelom): pogovorno vprašanje z
# relevantnim kontekstom -> ODGOVORI; nepovezano vprašanje -> ZAVRNI.
def _fewshot(language: str) -> List[Dict[str, str]]:
    return [
        {"role": "user", "content": _user_turn(
            "[1] Baterije\nBaterijo polnimo z ustreznim polnilnikom in pazimo na pravilno polariteto.",
            "ej a veš kako se polni baterija", language)},
        {"role": "assistant", "content": "Baterijo polniš z ustreznim polnilnikom za njeno vrsto in paziš na pravilno polariteto."},
        {"role": "user", "content": _user_turn(
            "[1] Motorji\nRobot uporablja motorje za gibanje koles in rok.",
            "kakšno je danes vreme", language)},
        {"role": "assistant", "content": "Tega v priročniku ne najdem. Vprašaj učitelja."},
    ]


def build_messages(question: str, contexts: List[Dict], language: str = "slovenščina") -> List[Dict[str, str]]:
    system = SYSTEM_RULES + " " + _language_line(language)
    user = _user_turn(format_context(contexts), question, language)
    return [
        {"role": "system", "content": system},
        *_fewshot(language),
        {"role": "user", "content": user},
    ]


def build_translation_messages(text: str, target_language: str) -> List[Dict[str, str]]:
    system = (
        f"Si natančen prevajalec. Prevedi uporabnikovo besedilo v jezik: {target_language}. "
        "Vrni IZKLJUČNO prevod – brez razlage, brez navedkov, brez dodatnega besedila."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": text},
    ]
