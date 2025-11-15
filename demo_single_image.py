#!/usr/bin/env python3
"""
Demo: Process a single image with Guardian EPI
"""
import os
import sys
import cv2
import numpy as np
from tensorflow import keras
from datetime import datetime

# Configurações
MODEL_PATH = "models/keras_model.h5"
LABELS_PATH = "models/labels.txt"
IMG_SIZE = 224

print("=" * 70)
print("GUARDIAN EPI - DEMO: PROCESSAMENTO DE IMAGEM ÚNICA")
print("=" * 70)
print()

# Carregar modelo
print("[1/3] Carregando modelo...")
try:
    modelo = keras.models.load_model(MODEL_PATH, compile=False)
    print(f"   ✅ Modelo carregado com sucesso")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Carregar labels
print("\n[2/3] Carregando labels...")
try:
    with open(LABELS_PATH, 'r', encoding='utf-8') as f:
        labels = [line.strip() for line in f.readlines()]
    print(f"   ✅ Labels: {labels}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Selecionar imagens de exemplo
print("\n[3/3] Processando imagens de exemplo...")
print()

test_images = [
    ("test_images/epi/com_epi/1000.jpg", "COM EPI"),
    ("test_images/epi/sem_epi/1000.jpg", "SEM EPI"),
]

def preprocess_image(image):
    """Pré-processa imagem"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (IMG_SIZE, IMG_SIZE))
    image_normalized = image_resized.astype(np.float32) / 255.0
    image_batch = np.expand_dims(image_normalized, axis=0)
    return image_batch

for img_path, expected in test_images:
    print("=" * 70)
    print(f"IMAGEM: {img_path}")
    print(f"ESPERADO: {expected}")
    print("-" * 70)

    if not os.path.exists(img_path):
        print(f"❌ Imagem não encontrada: {img_path}")
        continue

    # Carregar e processar imagem
    image = cv2.imread(img_path)
    if image is None:
        print(f"❌ Erro ao carregar imagem")
        continue

    print(f"✓ Imagem carregada: {image.shape}")

    # Fazer predição
    processed = preprocess_image(image)
    predictions = modelo.predict(processed, verbose=0)

    # Obter resultado
    class_index = np.argmax(predictions[0])
    confidence = predictions[0][class_index]
    class_name = labels[class_index] if class_index < len(labels) else "unknown"

    # Extrair nome limpo
    label_clean = class_name.split()[-1] if ' ' in class_name else class_name

    # Verificar se está correto
    # Remove underscores para comparação
    expected_clean = expected.replace(" ", "_")
    is_correct = (expected_clean in label_clean.upper())
    status = "✅ CORRETO" if is_correct else "❌ INCORRETO"

    print(f"\n🔍 RESULTADO DA PREDIÇÃO:")
    print(f"   Classe detectada: {label_clean}")
    print(f"   Confiança: {confidence:.2%}")
    print(f"   Status: {status}")

    # Mostrar todas as probabilidades
    print(f"\n📊 PROBABILIDADES DETALHADAS:")
    for i, prob in enumerate(predictions[0]):
        label = labels[i].split()[-1] if i < len(labels) else f"classe_{i}"
        bar_length = int(prob * 50)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"   {label:10} {bar} {prob:.2%}")

    print()

# Demonstração com imagem fornecida pelo usuário
print("\n" + "=" * 70)
print("TESTE COM SUA PRÓPRIA IMAGEM")
print("=" * 70)
print()
print("Para testar com sua própria imagem, use:")
print()
print("  python demo_single_image.py <caminho_da_imagem>")
print()
print("Exemplo:")
print("  python demo_single_image.py minha_foto.jpg")
print()

if len(sys.argv) > 1:
    user_image = sys.argv[1]
    print(f"Processando: {user_image}")
    print("-" * 70)

    if os.path.exists(user_image):
        image = cv2.imread(user_image)
        if image is not None:
            processed = preprocess_image(image)
            predictions = modelo.predict(processed, verbose=0)

            class_index = np.argmax(predictions[0])
            confidence = predictions[0][class_index]
            class_name = labels[class_index] if class_index < len(labels) else "unknown"
            label_clean = class_name.split()[-1] if ' ' in class_name else class_name

            print(f"\n🔍 RESULTADO:")
            print(f"   Imagem: {user_image}")
            print(f"   Detecção: {label_clean}")
            print(f"   Confiança: {confidence:.2%}")

            if 'sem' in label_clean.lower():
                print("\n⚠️  ALERTA: FUNCIONÁRIO SEM EPI DETECTADO!")
                print("   Acesso à zona restrita NEGADO")
            else:
                print("\n✅ EPI ADEQUADO DETECTADO")
                print("   Acesso à zona restrita LIBERADO")
        else:
            print(f"❌ Não foi possível carregar: {user_image}")
    else:
        print(f"❌ Arquivo não encontrado: {user_image}")

print("\n" + "=" * 70)
print("DEMONSTRAÇÃO CONCLUÍDA")
print("=" * 70)
