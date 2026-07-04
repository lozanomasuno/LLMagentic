"""
validate_e2e.py — Validación de extremo a extremo del flujo de cobertura.

Ejecutar con el backend corriendo (uvicorn o docker compose up):

    python validate_e2e.py
    python validate_e2e.py --base-url http://localhost:8000/api/v1
    python validate_e2e.py --verbose

Requiere: pip install httpx
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import httpx

BASE_URL = "http://localhost:8000/api/v1"

# ── Colores para terminal ─────────────────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ── Escenarios de prueba ──────────────────────────────────────────────────────
SCENARIOS = [
    {
        "id": 1,
        "name": "Servicio cubierto (afiliado activo, plan Premium)",
        "document": None,          # se completa con el primer doc activo encontrado
        "query": "¿Está cubierta una consulta de medicina general en mi plan?",
        "expected_result": "cubierto",
        "description": (
            "Afiliado activo, pagos al día, plan Premium. "
            "Consulta de medicina general — servicio base incluido en DOC1."
        ),
    },
    {
        "id": 2,
        "name": "Cubierto con condiciones (servicio con autorización previa)",
        "document": None,
        "query": "¿Está cubierta una resonancia magnética de rodilla? ¿Necesito autorización previa?",
        "expected_result": "cubierto_con_condiciones",
        "description": (
            "Afiliado activo. La RMN de rodilla requiere autorización previa (DOC2 §4) "
            "y aplica período de carencia si la antigüedad es menor a 6 meses."
        ),
    },
    {
        "id": 3,
        "name": "No cubierto (afiliado en mora o suspendido)",
        "document": None,          # se busca un afiliado en mora
        "query": "¿Está cubierta una cirugía de cadera para mi plan?",
        "expected_result": "no_cubierto",
        "description": (
            "Afiliado en mora o estado suspendido. "
            "Regla 1 del sistema: estado de pagos != 'Al día' → no_cubierto."
        ),
    },
]


def _color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def _result_color(result: str) -> str:
    colors = {
        "cubierto": GREEN,
        "cubierto_con_condiciones": YELLOW,
        "no_cubierto": RED,
    }
    return _color(result, colors.get(result, CYAN))


def check_health(client: httpx.Client) -> bool:
    try:
        r = client.get("/health", timeout=5)
        r.raise_for_status()
        data = r.json()
        print(f"  Backend: {_color('OK', GREEN)}  v{data.get('version', '?')}  "
              f"env={data.get('environment', '?')}")
        return True
    except Exception as exc:
        print(f"  {_color('ERROR', RED)}: {exc}")
        print(f"  Asegúrate de que el backend esté corriendo en {BASE_URL.replace('/api/v1','')}")
        return False


def find_affiliates(client: httpx.Client) -> tuple[str | None, str | None]:
    """Return (doc_active, doc_mora) — document numbers for the two affiliate types."""
    doc_active = None
    doc_mora = None

    # Hit the suggestions endpoint just to verify API is up
    try:
        r = client.get("/suggestions", params={"q": "consulta"}, timeout=5)
        r.raise_for_status()
    except Exception:
        pass  # non-critical

    # Try known document numbers that are usually present in BD_afiliados.xlsx
    # The script will prompt the user if none are found automatically.
    test_docs = [
        "1023456789", "987654321", "1122334455", "5544332211",
        "1234567890", "9876543210", "1111111111", "2222222222",
    ]

    for doc in test_docs:
        try:
            r = client.get(f"/affiliates/{doc}", timeout=5)
            if r.status_code == 200:
                affiliate = r.json()
                is_active = (
                    affiliate.get("estado_afiliacion") == "Activo"
                    and affiliate.get("estado_pagos") == "Al día"
                )
                is_mora = affiliate.get("estado_pagos") in ("En mora",)

                if is_active and doc_active is None:
                    doc_active = doc
                    print(f"  Afiliado activo encontrado: {doc} "
                          f"({affiliate.get('primer_nombre')} {affiliate.get('primer_apellido')}, "
                          f"plan {affiliate.get('plan')})")
                if is_mora and doc_mora is None:
                    doc_mora = doc
                    print(f"  Afiliado en mora encontrado: {doc} "
                          f"({affiliate.get('primer_nombre')} {affiliate.get('primer_apellido')})")

            if doc_active and doc_mora:
                break
        except Exception:
            continue

    return doc_active, doc_mora


def run_scenario(
    client: httpx.Client, scenario: dict, document: str, verbose: bool
) -> bool:
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}Escenario {scenario['id']}: {scenario['name']}{RESET}")
    print(f"  {scenario['description']}")
    print(f"  Documento: {document}")
    print(f"  Consulta:  {scenario['query']}")
    print(f"  Esperado:  {_result_color(scenario['expected_result'])}")

    t0 = time.perf_counter()
    try:
        r = client.post(
            "/coverage-analysis",
            json={"document_number": document, "query": scenario["query"]},
            timeout=60,
        )
        elapsed = int((time.perf_counter() - t0) * 1000)

        if r.status_code != 200:
            print(f"  {_color('FALLO', RED)} HTTP {r.status_code}: {r.text[:200]}")
            return False

        data = r.json()
        result = data.get("coverage_result", "unknown")
        passed = result == scenario["expected_result"]

        status_label = _color("✓ PASÓ", GREEN) if passed else _color("✗ FALLÓ", RED)
        print(f"\n  Resultado: {_result_color(result)}")
        print(f"  Estado:    {status_label}  ({elapsed} ms total)")

        if verbose:
            print(f"\n  Respuesta:")
            print(f"  {data.get('response_text', '')[:500]}")
            if data.get("sources"):
                print(f"\n  Fuentes utilizadas ({len(data['sources'])}):")
                for s in data["sources"][:3]:
                    print(f"    • {s.get('document')} — {s.get('section')}")
            if data.get("agent_trace"):
                print(f"\n  Traza del agente:")
                for step in data["agent_trace"]:
                    print(f"    [{step.get('step')}] {step.get('result')}  "
                          f"({step.get('duration_ms', '?')} ms)")

        return passed

    except httpx.TimeoutException:
        elapsed = int((time.perf_counter() - t0) * 1000)
        print(f"  {_color('TIMEOUT', RED)} después de {elapsed} ms")
        print("  Verifica que OPENAI_API_KEY esté configurada correctamente.")
        return False
    except Exception as exc:
        print(f"  {_color('ERROR', RED)}: {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Validación E2E del flujo de cobertura")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--doc-active", help="Número de documento de afiliado activo")
    parser.add_argument("--doc-mora", help="Número de documento de afiliado en mora")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Health Coverage AI — Validación E2E{RESET}")
    print(f"  Backend: {base}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    with httpx.Client(base_url=base) as client:
        # 1. Health check
        print(f"{BOLD}1. Verificando backend...{RESET}")
        if not check_health(client):
            sys.exit(1)

        # 2. Find affiliate documents
        print(f"\n{BOLD}2. Buscando afiliados de prueba...{RESET}")
        doc_active_auto, doc_mora_auto = find_affiliates(client)

        doc_active = args.doc_active or doc_active_auto
        doc_mora = args.doc_mora or doc_mora_auto

        if not doc_active:
            print(f"\n  {_color('AVISO', YELLOW)}: No se encontró afiliado activo automáticamente.")
            doc_active = input("  Ingresa el número de documento de un afiliado ACTIVO: ").strip()
        if not doc_mora:
            print(f"\n  {_color('AVISO', YELLOW)}: No se encontró afiliado en mora automáticamente.")
            doc_mora = input("  Ingresa el número de documento de un afiliado EN MORA (o Enter para omitir): ").strip()
            if not doc_mora:
                doc_mora = doc_active  # reuse active, scenario may still fail by query content

        # 3. Run scenarios
        print(f"\n{BOLD}3. Ejecutando escenarios...{RESET}")
        SCENARIOS[0]["document"] = doc_active
        SCENARIOS[1]["document"] = doc_active
        SCENARIOS[2]["document"] = doc_mora

        results = []
        for scenario in SCENARIOS:
            doc = scenario.pop("document")
            passed = run_scenario(client, scenario, doc, args.verbose)
            results.append(passed)

        # 4. Summary
        total = len(results)
        passed_count = sum(results)
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}  Resultados: {passed_count}/{total} escenarios pasaron{RESET}")
        for i, (scenario, passed) in enumerate(zip(SCENARIOS, results), 1):
            mark = _color("✓", GREEN) if passed else _color("✗", RED)
            print(f"  {mark} Escenario {i}: {scenario['name']}")
        print(f"{BOLD}{'='*60}{RESET}\n")

        if passed_count < total:
            print(f"{YELLOW}Nota: Los escenarios pueden diferir del resultado esperado según{RESET}")
            print(f"{YELLOW}los datos específicos del afiliado y el contenido de los documentos.{RESET}")
            print(f"{YELLOW}Revisa las respuestas con --verbose para verificar la calidad.{RESET}\n")

        sys.exit(0 if passed_count == total else 1)


if __name__ == "__main__":
    main()
