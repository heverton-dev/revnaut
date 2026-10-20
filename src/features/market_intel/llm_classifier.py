# -*- coding: utf-8 -*-
"""
Classificador de Sinais de Mercado e Extrator Tático de Ofertas Concorrentes (TICKET-MKTINTEL-04).

Motor primário: LLM local via Ollama (/api/generate, format=json, qwen2.5:7b ou llama3.1:8b)
ou gateway LiteLLM (OpenAI-compatível). Quando nenhum motor está configurado ou acessível,
aplica o classificador NLP odontológico determinístico (regras explícitas, mesma entrada -> mesma saída).
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

import httpx

DEFAULT_OLLAMA_MODEL = "qwen2.5:7b"
LLM_TIMEOUT_SECONDS = 20.0

ENGINE_DETERMINISTIC = "deterministic_dental_nlp"

# (tópico clínico, padrão de detecção, especialidades associadas)
TOPIC_RULES: List[Tuple[str, re.Pattern[str], Tuple[str, ...]]] = [
    ("Cone Morse", re.compile(r"cone\s*morse|grand\s*morse", re.I), ("Implantodontia",)),
    ("Carga Imediata", re.compile(r"carga\s+imediata|immediate\s+load", re.I), ("Implantodontia", "Protese Digital")),
    ("CAD/CAM", re.compile(r"\bcad\s*/?\s*cam\b|fresagem|milling|scanner\s+intraoral|fluxo\s+digital", re.I), ("Protese Digital",)),
    ("Zirconia", re.compile(r"zirc[oô]nia|zirconia|zirconium", re.I), ("Protese Digital",)),
    ("Biomateriais", re.compile(r"biomateria|enxerto|bone\s+graft|xenoenxerto|membrana\s+de\s+col[aá]geno|regenera[çc][ãa]o\s+[oó]ssea", re.I), ("Cirurgia Bucomaxilofacial", "Implantodontia", "Periodontia")),
    ("Rastreabilidade UDI ANVISA", re.compile(r"\budi\b|rastreabilidade|\brdc\b", re.I), ("Implantodontia",)),
    ("Superficie Hidrofilica", re.compile(r"hidrof[ií]lic|hydrophilic|\bsla\b", re.I), ("Implantodontia",)),
    ("Peri-implantite", re.compile(r"peri-?implantit", re.I), ("Periodontia", "Implantodontia")),
]

TREND_RULES: List[Tuple[str, re.Pattern[str]]] = [
    ("Expansao de demanda regional", re.compile(r"expans|crescim|surge|aument|growth|alta\s+de", re.I)),
    ("Endurecimento regulatorio", re.compile(r"\brdc\b|anvisa|\bfda\b|510\s*\(k\)|regulat|obrigat[oó]ri", re.I)),
    ("Digitalizacao do fluxo protetico", re.compile(r"\bcad\s*/?\s*cam\b|fluxo\s+digital|scanner\s+intraoral|digital", re.I)),
    ("Pressao de preco concorrencial", re.compile(r"desconto|promo[çc]|pre[çc]o|price|discount", re.I)),
    ("Nova evidencia clinica", re.compile(r"meta-?an[aá]lis|ensaio\s+cl[ií]nico|clinical\s+trial|estudo\s+(cl[ií]nico|multic)|revis[aã]o\s+sistem", re.I)),
    ("Consolidacao de redes corporativas", re.compile(r"redes?\s+(corporativ|de\s+cl[ií]nicas)|\bdso\b|chains?\b|franquia", re.I)),
]

VALID_SPECIALTIES = ("Implantodontia", "Protese Digital", "Periodontia", "Cirurgia Bucomaxilofacial")

_OFFER_PATTERN = re.compile(
    r"(?P<product>(?:implante|kit|enxerto|biomaterial|coroa|bloco|componente|membrana|pilar|abutment|scanner)"
    r"[^\n\r;|]{0,70}?)\s*(?:por|:|-|a\s+partir\s+de)?\s*(?P<currency>R\$|US\$|\$)\s*(?P<price>\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)",
    re.I,
)
_DISCOUNT_PATTERN = re.compile(r"(\d{1,2}(?:[.,]\d)?)\s*%\s*(?:off|de\s+desconto|desconto)?", re.I)


def _strip_accents(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))


def _parse_price(raw: str) -> float:
    s = raw.strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        s = s.replace(".", "")
    return round(float(s), 2)


def _call_ollama(prompt: str) -> Optional[Dict[str, Any]]:
    base_url = os.getenv("OLLAMA_BASE_URL")
    if not base_url:
        return None
    model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    try:
        resp = httpx.post(
            f"{base_url.rstrip('/')}/api/generate",
            json={"model": model, "prompt": prompt, "format": "json", "stream": False, "options": {"temperature": 0}},
            timeout=LLM_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = json.loads(resp.json().get("response") or "{}")
        if isinstance(data, dict):
            data["_engine"] = f"ollama:{model}"
            return data
    except Exception:
        return None
    return None


def _call_litellm(prompt: str) -> Optional[Dict[str, Any]]:
    api_key = os.getenv("LITELLM_API_KEY")
    if not api_key:
        return None
    base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000").rstrip("/")
    model = os.getenv("LITELLM_MODEL", DEFAULT_OLLAMA_MODEL)
    try:
        resp = httpx.post(
            f"{base_url}/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "Responda somente com JSON valido."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=LLM_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        if isinstance(data, dict):
            data["_engine"] = f"litellm:{model}"
            return data
    except Exception:
        return None
    return None


def _call_llm(prompt: str) -> Optional[Dict[str, Any]]:
    return _call_ollama(prompt) or _call_litellm(prompt)


def _as_str_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def classify_market_signal_deterministic(title: str, raw_content: str) -> Dict[str, Any]:
    text = f"{title}\n{raw_content}"
    topics: List[str] = []
    specialties: List[str] = []
    for topic, pattern, specs in TOPIC_RULES:
        if pattern.search(text):
            topics.append(topic)
            for sp in specs:
                if sp not in specialties:
                    specialties.append(sp)
    trends = [name for name, pattern in TREND_RULES if pattern.search(text)]
    if not specialties:
        specialties = ["Implantodontia"]
    return {
        "topics": topics,
        "detected_trends": trends,
        "target_specialties": specialties,
        "engine": ENGINE_DETERMINISTIC,
    }


def classify_market_signal(title: str, raw_content: str) -> Dict[str, Any]:
    """Extrai {topics, detected_trends, target_specialties} de um sinal de mercado odontológico."""
    prompt = (
        "Voce e um analista de inteligencia de mercado odontologico B2B. Extraia do texto um JSON com as chaves "
        "'topics' (lista de topicos clinicos como Cone Morse, Carga Imediata, CAD/CAM, Zirconia, Biomateriais, "
        "Rastreabilidade UDI ANVISA), 'detected_trends' (lista de tendencias de mercado) e 'target_specialties' "
        f"(lista entre {list(VALID_SPECIALTIES)}).\n\nTITULO: {title}\n\nTEXTO: {raw_content[:6000]}"
    )
    llm = _call_llm(prompt)
    if llm:
        topics = _as_str_list(llm.get("topics"))
        trends = _as_str_list(llm.get("detected_trends"))
        specialties = [s for s in _as_str_list(llm.get("target_specialties")) if _strip_accents(s) in VALID_SPECIALTIES]
        if topics or trends or specialties:
            return {
                "topics": topics,
                "detected_trends": trends,
                "target_specialties": [_strip_accents(s) for s in specialties] or ["Implantodontia"],
                "engine": llm["_engine"],
            }
    return classify_market_signal_deterministic(title, raw_content)


def extract_offers_deterministic(raw_text: str) -> List[Dict[str, Any]]:
    offers: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for line in re.split(r"[\n\r]+|(?<=[.!])\s+", raw_text):
        for m in _OFFER_PATTERN.finditer(line):
            product = re.sub(r"\s+", " ", m.group("product")).strip(" -:,")
            try:
                price = _parse_price(m.group("price"))
            except ValueError:
                continue
            tail = line[m.end(): m.end() + 60]
            head = line[max(0, m.start() - 40): m.start()]
            disc_match = _DISCOUNT_PATTERN.search(tail) or _DISCOUNT_PATTERN.search(head)
            discount = f"{disc_match.group(1).replace(',', '.')}%" if disc_match else "0%"
            key = f"{product.lower()}|{price}"
            if key in seen:
                continue
            seen.add(key)
            offers.append({"product": product, "price": price, "discount": discount})
    return offers


def _discount_value(discount: str) -> float:
    try:
        return float(discount.rstrip("%"))
    except ValueError:
        return 0.0


def build_tactical_summary(competitor_name: str, offers: List[Dict[str, Any]]) -> str:
    if not offers:
        return (
            f"{competitor_name}: nenhuma oferta de preco detectada nesta captura. Manter monitoramento passivo "
            "de lancamentos e conteudo clinico; reforcar com consultores o pacote de valor REVNAULT "
            "(garantia ANVISA com rastreabilidade UDI, entrega DENTGO em 45 min e suporte cirurgico)."
        )
    top = max(offers, key=lambda o: (_discount_value(str(o.get("discount", "0%"))), -float(o.get("price", 0.0))))
    return (
        f"{competitor_name} anuncia {top['product']} a R$ {float(top['price']):.2f} (desconto {top['discount']}). "
        "Contra-ataque B2B: nao disputar preco unitario; ofertar pacote cirurgico com garantia ANVISA e "
        "rastreabilidade UDI, entrega DENTGO em 45 min e suporte de consultor no dia da cirurgia; priorizar "
        "contas da praca com recompra prevista nos proximos 30 dias e aprovar condicao comercial via tabela de preco."
    )


def extract_competitor_offers_and_tactics(competitor_name: str, raw_text: str) -> Dict[str, Any]:
    """Extrai ofertas [{product, price, discount}] e gera resumo tatico B2B de contra-ataque."""
    prompt = (
        "Extraia ofertas comerciais odontologicas do texto de um concorrente. Responda JSON com a chave "
        "'detected_offers' (lista de objetos {product: string, price: number em BRL, discount: string como '18%'}) "
        f"e 'tactical_summary' (string com contra-ataque B2B).\n\nCONCORRENTE: {competitor_name}\n\nTEXTO: {raw_text[:6000]}"
    )
    llm = _call_llm(prompt)
    if llm and isinstance(llm.get("detected_offers"), list):
        offers: List[Dict[str, Any]] = []
        for item in llm["detected_offers"]:
            if not isinstance(item, dict) or not item.get("product"):
                continue
            try:
                price = float(item.get("price"))
            except (TypeError, ValueError):
                continue
            discount = str(item.get("discount") or "0%").strip()
            if not discount.endswith("%"):
                discount = f"{discount}%"
            offers.append({"product": str(item["product"]).strip(), "price": round(price, 2), "discount": discount})
        summary = str(llm.get("tactical_summary") or "").strip() or build_tactical_summary(competitor_name, offers)
        return {"detected_offers": offers, "tactical_summary": summary, "engine": llm["_engine"]}

    offers = extract_offers_deterministic(raw_text)
    return {
        "detected_offers": offers,
        "tactical_summary": build_tactical_summary(competitor_name, offers),
        "engine": ENGINE_DETERMINISTIC,
    }
