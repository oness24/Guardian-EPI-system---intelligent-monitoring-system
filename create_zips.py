#!/usr/bin/env python3
"""
Script para criar arquivos ZIP para entrega do trabalho
"""
import zipfile
import os
from datetime import datetime

print("=" * 70)
print("CRIANDO ARQUIVOS ZIP PARA ENTREGA")
print("=" * 70)
print()

# 1. ZIP do modelo de EPIs
print("[1/2] Criando modelo_epi.zip...")
try:
    with zipfile.ZipFile('modelo_epi.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('models/keras_model.h5', 'keras_model.h5')
        zipf.write('models/labels.txt', 'labels.txt')
        zipf.write('models/README.md', 'README.md')

    size = os.path.getsize('modelo_epi.zip') / (1024 * 1024)
    print(f"   ✅ Criado: modelo_epi.zip ({size:.2f} MB)")
    print(f"   📁 Contém:")
    print(f"      - keras_model.h5")
    print(f"      - labels.txt")
    print(f"      - README.md")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print()

# 2. ZIP dos modelos das situações-problema
print("[2/2] Criando modelos_situacoes_problema.zip...")
try:
    with zipfile.ZipFile('modelos_situacoes_problema.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Modelo (o mesmo serve para todas as situações)
        zipf.write('models/keras_model.h5', 'modelo_compartilhado/keras_model.h5')
        zipf.write('models/labels.txt', 'modelo_compartilhado/labels.txt')

        # Scripts das situações-problema
        zipf.write('controle_uniforme.py', 'situacao_1_uniformes/controle_uniforme.py')
        zipf.write('detector_objetos.py', 'situacao_2_objetos/detector_objetos.py')

        # Documentação
        zipf.write('RELATORIO_PERFORMANCE.md', 'RELATORIO_PERFORMANCE.md')
        zipf.write('TEST_RESULTS.md', 'TEST_RESULTS.md')

    size = os.path.getsize('modelos_situacoes_problema.zip') / (1024 * 1024)
    print(f"   ✅ Criado: modelos_situacoes_problema.zip ({size:.2f} MB)")
    print(f"   📁 Contém:")
    print(f"      - modelo_compartilhado/")
    print(f"         - keras_model.h5")
    print(f"         - labels.txt")
    print(f"      - situacao_1_uniformes/")
    print(f"         - controle_uniforme.py")
    print(f"      - situacao_2_objetos/")
    print(f"         - detector_objetos.py")
    print(f"      - RELATORIO_PERFORMANCE.md")
    print(f"      - TEST_RESULTS.md")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print()
print("=" * 70)
print("ARQUIVOS ZIP CRIADOS COM SUCESSO!")
print("=" * 70)
print()
print("Arquivos criados no diretório atual:")
print("  1. modelo_epi.zip")
print("  2. modelos_situacoes_problema.zip")
print()
print("✅ Pronto para entrega!")
print()
