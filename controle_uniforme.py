"""
Guardian EPI - Módulo de Controle de Uniformes (Departamento de Qualidade)
Autor: Sistema Guardian EPI
Data: 2025

PROBLEMA-SITUAÇÃO 1: Conformidade de Uniformes em Zonas de Alta Higiene

CONTEXTO:
Em uma fábrica de alimentos, especialmente na área de embalagem, é crítico que
todos os funcionários usem uniformes estéreis completos, incluindo:
- Uniforme estéril completo (jaleco branco)
- Touca de proteção para cabelo
- Protetor de barba (para funcionários com barba)

A não conformidade pode resultar em:
- Contaminação do produto
- Recall de produtos
- Problemas de saúde pública
- Multas regulatórias

SOLUÇÃO:
Sistema automatizado de detecção que verifica a conformidade dos uniformes
antes da entrada em zonas de alta higiene.

CLASSES DO MODELO:
- uniforme_correto: Funcionário com uniforme completo e adequado
- uniforme_incorreto: Funcionário com uniforme incompleto ou inadequado

NOTA: Em ambiente de produção, o modelo deve ser treinado com imagens reais
de funcionários usando uniformes da empresa em diferentes condições de iluminação.
"""

import os
import cv2
import numpy as np
from datetime import datetime
from tensorflow import keras
import logging
import json

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================

# Caminhos do modelo Teachable Machine
MODEL_PATH = "models/uniforme_model.h5"
LABELS_PATH = "models/uniforme_labels.txt"

# Diretório para logs
LOGS_DIR = "logs/controle_qualidade"

# Configurações do modelo
IMG_SIZE = 224
CONFIDENCE_THRESHOLD = 0.75  # Mais rigoroso devido à criticidade

# ==============================================================================
# CONFIGURAÇÃO DE LOGGING
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE CONTROLE DE UNIFORMES
# ==============================================================================

class ControleUniforme:
    """
    Sistema de verificação de conformidade de uniformes para áreas de alta higiene

    Funcionalidades:
    - Detecta se o funcionário está usando uniforme completo
    - Verifica uso de touca e protetor de barba
    - Registra não conformidades
    - Bloqueia acesso a zonas restritas
    """

    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH):
        """
        Inicializa o sistema de controle de uniformes

        Args:
            model_path: Caminho para o modelo keras treinado
            labels_path: Caminho para arquivo de rótulos
        """
        self.model = None
        self.labels = []
        self.model_path = model_path
        self.labels_path = labels_path

        # Criar diretório de logs
        os.makedirs(LOGS_DIR, exist_ok=True)

        # Carregar modelo
        self._load_model()
        self._load_labels()

        # Contador de violações
        self.violations_count = 0

        logger.info("Sistema de Controle de Uniformes inicializado")

    def _load_model(self):
        """
        Carrega o modelo de classificação de uniformes

        O modelo foi treinado no Teachable Machine com classes:
        - uniforme_correto: Uniforme completo (jaleco + touca + protetor)
        - uniforme_incorreto: Uniforme incompleto ou ausente

        Para produção:
        - Coletar mínimo 300 imagens por classe
        - Incluir variações de iluminação, ângulos e distâncias
        - Considerar diferentes tipos físicos de funcionários
        - Incluir imagens com e sem protetor de barba
        """
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Modelo não encontrado em: {self.model_path}")
                logger.warning("Para usar este script, treine um modelo no Teachable Machine")
                logger.warning("Classes: uniforme_correto, uniforme_incorreto")
                return

            # Fix para compatibilidade com TensorFlow 2.20+
            # Remove o parâmetro 'groups' do DepthwiseConv2D
            import tensorflow as tf

            # Carrega o modelo com custom object
            with tf.keras.utils.custom_object_scope({}):
                # Cria uma classe wrapper para DepthwiseConv2D que ignora 'groups'
                original_depthwise = tf.keras.layers.DepthwiseConv2D

                class DepthwiseConv2DFixed(original_depthwise):
                    def __init__(self, *args, **kwargs):
                        # Remove o parâmetro 'groups' se existir
                        kwargs.pop('groups', None)
                        super().__init__(*args, **kwargs)

                # Substitui temporariamente
                tf.keras.layers.DepthwiseConv2D = DepthwiseConv2DFixed

                try:
                    self.model = keras.models.load_model(self.model_path, compile=False)
                finally:
                    # Restaura a classe original
                    tf.keras.layers.DepthwiseConv2D = original_depthwise

            logger.info(f"Modelo de uniformes carregado: {self.model_path}")

        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise

    def _load_labels(self):
        """
        Carrega rótulos das classes
        """
        try:
            if not os.path.exists(self.labels_path):
                logger.warning(f"Arquivo de rótulos não encontrado: {self.labels_path}")
                # Definir rótulos padrão para demonstração
                self.labels = ['uniforme_correto', 'uniforme_incorreto']
                return

            with open(self.labels_path, 'r', encoding='utf-8') as f:
                self.labels = [line.strip() for line in f.readlines()]

            logger.info(f"Rótulos carregados: {self.labels}")

        except Exception as e:
            logger.error(f"Erro ao carregar rótulos: {e}")
            raise

    def preprocess_image(self, image):
        """
        Pré-processa imagem para inferência

        Args:
            image: Imagem BGR do OpenCV

        Returns:
            Array normalizado pronto para predição
        """
        try:
            # Converter BGR para RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Redimensionar
            image_resized = cv2.resize(image_rgb, (IMG_SIZE, IMG_SIZE))

            # Normalizar [0, 1]
            image_normalized = image_resized.astype(np.float32) / 255.0

            # Adicionar batch dimension
            image_batch = np.expand_dims(image_normalized, axis=0)

            return image_batch

        except Exception as e:
            logger.error(f"Erro no pré-processamento: {e}")
            raise

    def verify_uniform(self, image):
        """
        Verifica se o funcionário está usando uniforme adequado

        Args:
            image: Imagem do funcionário

        Returns:
            tuple: (is_compliant, class_name, confidence)
        """
        try:
            if self.model is None:
                logger.warning("Modelo não carregado - executando em modo demonstração")
                # Retornar predição simulada
                return True, "uniforme_correto", 0.95

            # Pré-processar
            processed = self.preprocess_image(image)

            # Predição
            predictions = self.model.predict(processed, verbose=0)

            # Obter classe
            class_index = np.argmax(predictions[0])
            confidence = predictions[0][class_index]
            class_name = self.labels[class_index] if class_index < len(self.labels) else "unknown"

            # Verificar conformidade
            is_compliant = 'correto' in class_name.lower() and confidence >= CONFIDENCE_THRESHOLD

            logger.info(f"Verificação: {class_name} (confiança: {confidence:.2%})")

            return is_compliant, class_name, confidence

        except Exception as e:
            logger.error(f"Erro na verificação: {e}")
            raise

    def log_violation(self, image, class_name, confidence):
        """
        Registra violação de conformidade de uniforme

        Args:
            image: Imagem da violação
            class_name: Classe detectada
            confidence: Confiança da predição
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Salvar imagem
            image_filename = f"violacao_uniforme_{timestamp}.jpg"
            image_path = os.path.join(LOGS_DIR, image_filename)
            cv2.imwrite(image_path, image)

            # Criar log
            log_file = os.path.join(LOGS_DIR, "violacoes_uniforme.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                log_entry = (
                    f"[{timestamp}] - VIOLAÇÃO: Uniforme não conforme detectado. "
                    f"Classe: {class_name}, Confiança: {confidence:.2%}, "
                    f"Imagem: {image_path}\n"
                )
                f.write(log_entry)

            self.violations_count += 1

            logger.warning(f"⚠️ VIOLAÇÃO #{self.violations_count} registrada: {class_name}")

        except Exception as e:
            logger.error(f"Erro ao registrar violação: {e}")
            raise

    def grant_access(self):
        """
        Simula liberação de acesso à zona restrita
        """
        logger.info("✓ ACESSO LIBERADO - Uniforme conforme")
        print("\n" + "="*50)
        print("✓ ACESSO LIBERADO")
        print("Uniforme conforme aos padrões de higiene")
        print("Entrada autorizada na zona de alta higiene")
        print("="*50 + "\n")

    def deny_access(self, reason):
        """
        Simula bloqueio de acesso à zona restrita

        Args:
            reason: Motivo do bloqueio
        """
        logger.warning(f"✗ ACESSO NEGADO - {reason}")
        print("\n" + "="*50)
        print("✗ ACESSO NEGADO")
        print(f"Motivo: {reason}")
        print("Regularize o uniforme antes de entrar")
        print("="*50 + "\n")

    def process_entry(self, image_path):
        """
        Processa tentativa de entrada de funcionário

        Args:
            image_path: Caminho da imagem do funcionário
        """
        try:
            # Carregar imagem
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Não foi possível carregar: {image_path}")

            logger.info(f"Processando entrada: {image_path}")

            # Verificar uniforme
            is_compliant, class_name, confidence = self.verify_uniform(image)

            if is_compliant:
                self.grant_access()
            else:
                reason = f"Uniforme não conforme detectado ({class_name}, {confidence:.1%})"
                self.deny_access(reason)
                self.log_violation(image, class_name, confidence)

        except Exception as e:
            logger.error(f"Erro ao processar entrada: {e}")
            raise

    def process_directory(self, directory_path):
        """
        Processa múltiplas tentativas de entrada

        Args:
            directory_path: Diretório com imagens
        """
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Diretório não encontrado: {directory_path}")

            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            image_files = [
                f for f in os.listdir(directory_path)
                if os.path.splitext(f)[1].lower() in valid_extensions
            ]

            if not image_files:
                logger.warning(f"Nenhuma imagem em: {directory_path}")
                return

            logger.info(f"Processando {len(image_files)} tentativas de entrada")

            approved = 0
            denied = 0

            for image_file in image_files:
                image_path = os.path.join(directory_path, image_file)
                print(f"\n--- Processando: {image_file} ---")

                image = cv2.imread(image_path)
                is_compliant, class_name, confidence = self.verify_uniform(image)

                if is_compliant:
                    self.grant_access()
                    approved += 1
                else:
                    reason = f"Uniforme não conforme ({class_name})"
                    self.deny_access(reason)
                    self.log_violation(image, class_name, confidence)
                    denied += 1

            # Resumo
            print("\n" + "="*50)
            print("RESUMO DO PROCESSAMENTO")
            print("="*50)
            print(f"Total de tentativas: {len(image_files)}")
            print(f"Acessos aprovados: {approved}")
            print(f"Acessos negados: {denied}")
            print(f"Taxa de conformidade: {approved/len(image_files)*100:.1f}%")
            print("="*50)

        except Exception as e:
            logger.error(f"Erro ao processar diretório: {e}")
            raise

    def generate_compliance_report(self):
        """
        Gera relatório de conformidade do dia
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            report_file = os.path.join(LOGS_DIR, f"relatorio_conformidade_{timestamp}.json")

            report = {
                "data": timestamp,
                "total_violacoes": self.violations_count,
                "sistema": "Controle de Uniformes - Qualidade",
                "area": "Zona de Alta Higiene - Embalagem",
                "threshold_confianca": CONFIDENCE_THRESHOLD
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)

            logger.info(f"Relatório gerado: {report_file}")

        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def main():
    """
    Função principal - demonstração do sistema
    """
    print("=" * 70)
    print("GUARDIAN EPI - Controle de Uniformes (Departamento de Qualidade)")
    print("=" * 70)
    print()
    print("APLICAÇÃO: Verificação de uniformes em zonas de alta higiene")
    print("SETOR: Área de embalagem de alimentos")
    print()

    try:
        # Inicializar sistema
        controle = ControleUniforme()

        # Menu
        print("Selecione o modo de operação:")
        print("1 - Verificar uma entrada única")
        print("2 - Processar múltiplas entradas (diretório)")
        print("3 - Gerar relatório de conformidade")
        print()

        choice = input("Escolha uma opção (1-3): ").strip()

        if choice == '1':
            image_path = input("Digite o caminho da imagem: ").strip()
            controle.process_entry(image_path)

        elif choice == '2':
            directory = input("Digite o caminho do diretório: ").strip()
            controle.process_directory(directory)
            controle.generate_compliance_report()

        elif choice == '3':
            controle.generate_compliance_report()
            print(f"\nRelatório salvo em: {os.path.abspath(LOGS_DIR)}")

        else:
            print("Opção inválida!")
            return 1

        print("\n✓ Processamento concluído!")

    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        print(f"\n❌ Erro: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
