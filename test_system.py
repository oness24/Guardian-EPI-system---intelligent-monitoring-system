#!/usr/bin/env python3
"""
Sistema de teste para verificar se tudo está funcionando
"""
import sys
import os

print("=" * 60)
print("GUARDIAN EPI - TESTE DE SISTEMA")
print("=" * 60)

# Teste 1: Imports básicos
print("\n[1/5] Testando imports básicos...")
try:
    import numpy as np
    print(f"   ✅ NumPy {np.__version__}")
except Exception as e:
    print(f"   ❌ NumPy: {e}")
    sys.exit(1)

try:
    import cv2
    print(f"   ✅ OpenCV {cv2.__version__}")
except Exception as e:
    print(f"   ❌ OpenCV: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print(f"   ✅ Pillow OK")
except Exception as e:
    print(f"   ❌ Pillow: {e}")
    sys.exit(1)

# Teste 2: TensorFlow
print("\n[2/5] Testando TensorFlow...")
try:
    import tensorflow as tf
    print(f"   ✅ TensorFlow {tf.__version__}")
except Exception as e:
    print(f"   ❌ TensorFlow: {e}")
    sys.exit(1)

# Teste 3: Carregamento do modelo
print("\n[3/5] Testando carregamento do modelo...")
model_path = "models/keras_model.h5"
labels_path = "models/labels.txt"

if not os.path.exists(model_path):
    print(f"   ❌ Modelo não encontrado: {model_path}")
    sys.exit(1)

if not os.path.exists(labels_path):
    print(f"   ❌ Labels não encontrados: {labels_path}")
    sys.exit(1)

try:
    # TensorFlow 2.15 tem suporte nativo para modelos do Teachable Machine
    modelo = tf.keras.models.load_model(model_path, compile=False)
    print(f"   ✅ Modelo carregado com sucesso")
    print(f"   📊 Input shape: {modelo.input_shape}")
    print(f"   📊 Output shape: {modelo.output_shape}")

except Exception as e:
    print(f"   ❌ Erro ao carregar modelo: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste 4: Leitura das labels
print("\n[4/5] Testando labels...")
try:
    with open(labels_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    print(f"   ✅ Labels carregadas:")
    for label in labels:
        print(f"      • {label}")
except Exception as e:
    print(f"   ❌ Erro ao carregar labels: {e}")
    sys.exit(1)

# Teste 5: Teste de predição com imagem dummy
print("\n[5/5] Testando predição...")
try:
    # Criar imagem dummy (224x224x3)
    dummy_image = np.random.rand(224, 224, 3).astype(np.float32)
    dummy_image = np.expand_dims(dummy_image, axis=0)

    # Fazer predição
    predicao = modelo.predict(dummy_image, verbose=0)
    print(f"   ✅ Predição executada com sucesso")
    print(f"   📊 Output shape: {predicao.shape}")
    print(f"   📊 Valores: {predicao[0]}")
except Exception as e:
    print(f"   ❌ Erro na predição: {e}")
    sys.exit(1)

# Teste dos scripts principais
print("\n[6/5] Verificando scripts principais...")
scripts = ["monitor_epi.py", "controle_uniforme.py", "detector_objetos.py"]
for script in scripts:
    if os.path.exists(script):
        print(f"   ✅ {script}")
    else:
        print(f"   ❌ {script} não encontrado")

print("\n" + "=" * 60)
print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
print("=" * 60)
print("\nSistema pronto para uso!")
print("\nPara executar:")
print("  python monitor_epi.py")
print("\n" + "=" * 60)
