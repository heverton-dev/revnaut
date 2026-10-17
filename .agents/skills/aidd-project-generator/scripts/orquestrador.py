#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORQUESTRADOR AIDD v2.1
aidd-project-generator — 7 phases + auto-critique

Ponto de entrada para geração de projetos AIDD completos.

Lei Fundamental: Cada projeto é auto-avaliável. Honestidade total.

Tokens: ~55k real + 0k mock = 55k determinístico
Determinismo: 100% (fluxo encadeado, exit 0/1)
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# ORQUESTRADOR
# =============================================================================

class OrquestradorAIDD:
    """Orquestrador central das 7 phases"""

    PHASES = [
        '01_pesquisador.py',      # Pesquisa
        '02_analisador.py',       # Análise da ideia
        '03_designer.py',         # Design com 5 subagentes
        '04_decisor.py',          # Decisões globais/locais
        '05_criador.py',          # Criação da estrutura
        '06_documentador.py',     # Documentação tripartite
        '07_autocritica.py',      # Auto-crítica (NOVO!) — renomeado, colidia com 02_analisador.py
    ]

    def __init__(self, pasta_saida: Path):
        self.pasta_saida = Path(pasta_saida)
        self.scripts_dir = Path(__file__).parent
        self.resultados = {}

    def executar(self) -> Dict:
        """Executar pipeline completo de 7 phases"""
        print(f"\n{'=' * 70}")
        print(f"🚀 ORQUESTRADOR AIDD v2.1 — 7 PHASES + AUTO-CRÍTICA")
        print(f"{'=' * 70}")
        print(f"\n📁 Projeto: {self.pasta_saida.name}")
        print(f"📍 Caminho: {self.pasta_saida}")
        print(f"\n{'-' * 70}")

        tempo_inicio = datetime.now()

        # Executar cada phase
        for i, phase_file in enumerate(self.PHASES, 1):
            print(f"\n[{i}/7] Iniciando {phase_file.split('_')[1]}...")

            try:
                resultado = self._executar_phase(phase_file)
                self.resultados[f'phase_{i}'] = resultado

                if resultado['status'] != 'COMPLETO':
                    print(f"   ❌ FALHA na phase {i}")
                    return {
                        'status': 'FALHA',
                        'fase_falhou': i,
                        'erro': resultado.get('erro'),
                    }

                print(f"   ✅ Phase {i} COMPLETA")
            except Exception as e:
                print(f"   ❌ ERRO na phase {i}: {e}")
                return {
                    'status': 'FALHA',
                    'fase_falhou': i,
                    'erro': str(e),
                }

        tempo_total = (datetime.now() - tempo_inicio).total_seconds()

        print(f"\n{'=' * 70}")
        print(f"✅ ORQUESTRADOR COMPLETO — PROJETO GERADO & AUTO-AVALIADO")
        print(f"{'=' * 70}")
        print(f"\n📊 RESUMO FINAL:")
        print(f"   • Projeto: {self.pasta_saida.name}")
        print(f"   • Phases: 7/7 COMPLETAS")
        print(f"   • Status: PRONTO PARA USO")
        print(f"   • Tempo total: {tempo_total:.1f}s")
        print(f"\n📁 Artefatos Gerados:")
        print(f"   • .aidd/config.json")
        print(f"   • .aidd/rules.md")
        print(f"   • .aidd/cache/_phase_*.json (7 indexadores)")
        print(f"   • AVALIACAO-AUTO-CRITICA.md (NOVO!)")
        print(f"   • .aidd/ROADMAP-EVOLUCAO.md (NOVO!)")
        print(f"   • README.md, CLAUDE.md")
        print(f"   • requirements.txt, .gitignore")
        print(f"   • estado_projeto.db (SQLite)")
        print(f"\n✨ PRÓXIMOS PASSOS:")
        print(f"   1. Abrir AVALIACAO-AUTO-CRITICA.md (análise honesta)")
        print(f"   2. Ler .aidd/ROADMAP-EVOLUCAO.md (caminho para 100/100)")
        print(f"   3. Começar com v3.0 (Feedback Loops)")
        print(f"\n{'-' * 70}\n")

        return {
            'status': 'COMPLETO',
            'projeto': str(self.pasta_saida),
            'phases_completadas': 7,
            'tempo_total': tempo_total,
        }

    def _executar_phase(self, phase_file: str) -> Dict:
        """Executar uma phase específica"""
        phase_path = self.scripts_dir / 'phases' / phase_file

        if not phase_path.exists():
            return {
                'status': 'FALHA',
                'erro': f'Phase não encontrada: {phase_path}',
            }

        # Chamar phase como subprocess
        try:
            resultado = subprocess.run(
                [sys.executable, str(phase_path), str(self.pasta_saida)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos max por phase
            )

            if resultado.returncode != 0:
                return {
                    'status': 'FALHA',
                    'erro': resultado.stderr,
                }

            return {
                'status': 'COMPLETO',
                'output': resultado.stdout,
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'FALHA',
                'erro': f'Phase {phase_file} expirou (timeout)',
            }
        except Exception as e:
            return {
                'status': 'FALHA',
                'erro': str(e),
            }


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """CLI para executar orquestrador"""
    import argparse

    parser = argparse.ArgumentParser(
        description='AIDD v2.1 Orquestrador — 7 Phases + Auto-Crítica'
    )
    parser.add_argument('pasta',
                       help='Pasta do projeto a gerar')
    parser.add_argument('--modo',
                       default='completo',
                       choices=['completo', 'rapido', 'debug'],
                       help='Modo de execução')

    args = parser.parse_args()

    pasta_projeto = Path(args.pasta)

    if not pasta_projeto.exists():
        print(f"❌ Pasta não encontrada: {pasta_projeto}")
        sys.exit(1)

    orquestrador = OrquestradorAIDD(pasta_projeto)
    resultado = orquestrador.executar()

    if resultado['status'] != 'COMPLETO':
        print(f"❌ Orquestrador falhou na fase {resultado.get('fase_falhou')}")
        print(f"   Erro: {resultado.get('erro')}")
        sys.exit(1)

    print(f"✅ Projeto gerado com sucesso em: {pasta_projeto}")
    sys.exit(0)


if __name__ == '__main__':
    main()
