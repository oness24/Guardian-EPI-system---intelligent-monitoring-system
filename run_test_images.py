#!/usr/bin/env python3
"""
Script para testar o Guardian EPI com as imagens de teste
Processa amostras de ambas as categorias e gera relatório
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
CONFIDENCE_THRESHOLD = 0.7

# Diretórios de teste
TEST_DIR_COM_EPI = "test_images/epi/com_epi"
TEST_DIR_SEM_EPI = "test_images/epi/sem_epi"

print("=" * 70)
print("GUARDIAN EPI - TESTE COM IMAGENS REAIS")
print("=" * 70)
print()

# Carregar modelo
print("[1/3] Carregando modelo...")
try:
    modelo = keras.models.load_model(MODEL_PATH, compile=False)
    print(f"   ✅ Modelo carregado: {MODEL_PATH}")
    print(f"   📊 Input shape: {modelo.input_shape}")
    print(f"   📊 Output shape: {modelo.output_shape}")
except Exception as e:
    print(f"   ❌ Erro ao carregar modelo: {e}")
    sys.exit(1)

# Carregar labels
print("\n[2/3] Carregando labels...")
try:
    with open(LABELS_PATH, 'r', encoding='utf-8') as f:
        labels = [line.strip() for line in f.readlines()]
    print(f"   ✅ Labels carregadas: {labels}")
except Exception as e:
    print(f"   ❌ Erro ao carregar labels: {e}")
    sys.exit(1)

# Função de pré-processamento
def preprocess_image(image):
    """Pré-processa imagem para o modelo"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (IMG_SIZE, IMG_SIZE))
    image_normalized = image_resized.astype(np.float32) / 255.0
    image_batch = np.expand_dims(image_normalized, axis=0)
    return image_batch

# Função de predição
def predict_image(image_path):
    """Faz predição em uma imagem"""
    image = cv2.imread(image_path)
    if image is None:
        return None, None, None

    processed = preprocess_image(image)
    predictions = modelo.predict(processed, verbose=0)

    class_index = np.argmax(predictions[0])
    confidence = predictions[0][class_index]
    class_name = labels[class_index] if class_index < len(labels) else "unknown"

    return class_name, confidence, class_index

print("\n[3/3] Processando imagens de teste...")
print()

# Processar imagens COM EPI
print("=" * 70)
print("TESTE 1: Imagens COM EPI (esperado: detecção de 'com_EPI')")
print("=" * 70)

if os.path.exists(TEST_DIR_COM_EPI):
    images_com = [f for f in os.listdir(TEST_DIR_COM_EPI) if f.endswith('.jpg')][:20]
    print(f"Processando {len(images_com)} imagens de {TEST_DIR_COM_EPI}...\n")

    correct_com = 0
    total_com = len(images_com)

    for img_file in images_com:
        img_path = os.path.join(TEST_DIR_COM_EPI, img_file)
        class_name, confidence, class_idx = predict_image(img_path)

        if class_name:
            # Extrair apenas a parte relevante do label (remover número)
            label_clean = class_name.split()[-1] if ' ' in class_name else class_name

            # Verificar se a predição está correta
            is_correct = 'com' in label_clean.lower()
            status = "✅" if is_correct else "❌"

            if is_correct:
                correct_com += 1

            print(f"{status} {img_file:15} -> {label_clean:15} (confiança: {confidence:.1%})")

    accuracy_com = (correct_com / total_com * 100) if total_com > 0 else 0
    print(f"\n📊 Acurácia COM EPI: {correct_com}/{total_com} = {accuracy_com:.1f}%")
else:
    print(f"❌ Diretório não encontrado: {TEST_DIR_COM_EPI}")
    total_com = 0
    correct_com = 0

# Processar imagens SEM EPI
print("\n" + "=" * 70)
print("TESTE 2: Imagens SEM EPI (esperado: detecção de 'sem_EPI')")
print("=" * 70)

if os.path.exists(TEST_DIR_SEM_EPI):
    images_sem = [f for f in os.listdir(TEST_DIR_SEM_EPI) if f.endswith('.jpg')][:20]
    print(f"Processando {len(images_sem)} imagens de {TEST_DIR_SEM_EPI}...\n")

    correct_sem = 0
    total_sem = len(images_sem)

    for img_file in images_sem:
        img_path = os.path.join(TEST_DIR_SEM_EPI, img_file)
        class_name, confidence, class_idx = predict_image(img_path)

        if class_name:
            # Extrair apenas a parte relevante do label
            label_clean = class_name.split()[-1] if ' ' in class_name else class_name

            # Verificar se a predição está correta
            is_correct = 'sem' in label_clean.lower()
            status = "✅" if is_correct else "❌"

            if is_correct:
                correct_sem += 1

            print(f"{status} {img_file:15} -> {label_clean:15} (confiança: {confidence:.1%})")

    accuracy_sem = (correct_sem / total_sem * 100) if total_sem > 0 else 0
    print(f"\n📊 Acurácia SEM EPI: {correct_sem}/{total_sem} = {accuracy_sem:.1f}%")
else:
    print(f"❌ Diretório não encontrado: {TEST_DIR_SEM_EPI}")
    total_sem = 0
    correct_sem = 0

# Resumo final
print("\n" + "=" * 70)
print("RESUMO GERAL")
print("=" * 70)

total_images = total_com + total_sem
correct_total = correct_com + correct_sem

if total_images > 0:
    accuracy_total = (correct_total / total_images * 100)
    print(f"Total de imagens testadas: {total_images}")
    print(f"Predições corretas: {correct_total}")
    print(f"Predições incorretas: {total_images - correct_total}")
    print(f"\n🎯 ACURÁCIA TOTAL: {accuracy_total:.1f}%")

    if accuracy_total >= 90:
        print("\n✅ EXCELENTE! O modelo está funcionando muito bem!")
    elif accuracy_total >= 70:
        print("\n✓ BOM! O modelo está funcionando adequadamente.")
    else:
        print("\n⚠️ O modelo precisa de mais treinamento ou ajustes.")
else:
    print("❌ Nenhuma imagem foi processada.")

print("=" * 70)
print(f"\nTeste concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
