"""
Guardian EPI - Módulo de Detecção de Objetos Estranhos (Departamento de Qualidade)
Autor: Sistema Guardian EPI
Data: 2025

PROBLEMA-SITUAÇÃO 2: Detecção de Objetos Estranhos na Linha de Produção

CONTEXTO:
Na indústria alimentícia, a presença de objetos estranhos no produto final é:
- CRÍTICA para segurança do consumidor
- CAUSA de recalls custosos
- VIOLAÇÃO de normas sanitárias (ANVISA, FDA)
- RISCO de processos legais

Objetos comuns que não devem estar na esteira:
- Canetas e lápis
- Ferramentas (chaves, alicates)
- Plásticos (embalagens, tampas)
- Metal (parafusos, arruelas)
- Vidro (quebra de lâmpadas)
- Objetos pessoais (celulares, relógios)

SOLUÇÃO:
Sistema de visão computacional que monitora a esteira transportadora em tempo
real, identificando objetos estranhos ANTES da embalagem final.

CLASSES DO MODELO:
- produto_limpo: Apenas produto na esteira, sem contaminação
- objeto_estranho: Objeto não-alimentício detectado na esteira

INTEGRAÇÃO:
- Sistema de parada automática da esteira
- Alertas sonoros e visuais
- Notificação imediata para supervisores
- Registro fotográfico para análise de causa raiz

NOTA: Para produção, usar câmeras industriais com alta taxa de frames (>30fps)
e iluminação controlada. Considerar usar YOLO ou EfficientDet para detecção
em tempo real com localização precisa do objeto.
"""

import os
import cv2
import numpy as np
from datetime import datetime
from tensorflow import keras
import logging
import json
import threading
import time

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================

# Caminhos do modelo
MODEL_PATH = "models/objeto_model.h5"
LABELS_PATH = "models/objeto_labels.txt"

# Diretório para logs
LOGS_DIR = "logs/deteccao_objetos"

# Configurações do modelo
IMG_SIZE = 224
CONFIDENCE_THRESHOLD = 0.80  # Alto para evitar falsos positivos

# Configurações de processamento
FRAME_RATE = 10  # Frames por segundo a processar (ajustar conforme hardware)

# ==============================================================================
# CONFIGURAÇÃO DE LOGGING
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE DETECTOR DE OBJETOS ESTRANHOS
# ==============================================================================

class DetectorObjetosEstranhos:
    """
    Sistema de detecção de objetos estranhos em esteira transportadora

    Funcionalidades:
    - Monitoramento contínuo da esteira
    - Detecção de objetos não-alimentícios
    - Parada automática da linha
    - Registro de incidentes com imagens
    - Geração de relatórios de qualidade
    """

    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH):
        """
        Inicializa o detector de objetos estranhos

        Args:
            model_path: Caminho para modelo keras
            labels_path: Caminho para rótulos
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

        # Contadores
        self.detections_count = 0
        self.false_alarms = 0
        self.line_stoppages = 0

        # Estado da linha
        self.line_running = True

        logger.info("Detector de Objetos Estranhos inicializado")

    def _load_model(self):
        """
        Carrega modelo de detecção de objetos estranhos

        DETALHES DO MODELO:
        O modelo Teachable Machine foi treinado com:
        - produto_limpo: Imagens do produto na esteira sem contaminação
        - objeto_estranho: Imagens com objetos como canetas, ferramentas, plástico

        LIMITAÇÕES DO PROTÓTIPO:
        - Dataset pequeno (necessário >500 imagens por classe em produção)
        - Iluminação variável não coberta adequadamente
        - Objetos pequenos podem não ser detectados
        - Não localiza precisamente onde está o objeto

        MELHORIAS PARA PRODUÇÃO:
        - Usar YOLO v8 ou EfficientDet para detecção em tempo real
        - Implementar segmentação para localização precisa
        - Treinar com imagens da linha real em diferentes horários
        - Incluir augmentation (rotação, blur, mudança de brilho)
        - Considerar usar múltiplas câmeras em diferentes ângulos
        """
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Modelo não encontrado em: {self.model_path}")
                logger.warning("Para usar este script, treine um modelo no Teachable Machine")
                logger.warning("Classes: produto_limpo, objeto_estranho")
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

            logger.info(f"Modelo carregado: {self.model_path}")

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
                # Rótulos padrão para demonstração
                self.labels = ['produto_limpo', 'objeto_estranho']
                return

            with open(self.labels_path, 'r', encoding='utf-8') as f:
                self.labels = [line.strip() for line in f.readlines()]

            logger.info(f"Rótulos: {self.labels}")

        except Exception as e:
            logger.error(f"Erro ao carregar rótulos: {e}")
            raise

    def preprocess_image(self, image):
        """
        Pré-processa imagem da esteira para inferência

        Args:
            image: Frame BGR da câmera

        Returns:
            Array normalizado para predição
        """
        try:
            # BGR para RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Redimensionar
            image_resized = cv2.resize(image_rgb, (IMG_SIZE, IMG_SIZE))

            # Normalizar
            image_normalized = image_resized.astype(np.float32) / 255.0

            # Batch dimension
            image_batch = np.expand_dims(image_normalized, axis=0)

            return image_batch

        except Exception as e:
            logger.error(f"Erro no pré-processamento: {e}")
            raise

    def detect_foreign_object(self, image):
        """
        Detecta presença de objeto estranho na imagem

        Args:
            image: Frame da esteira

        Returns:
            tuple: (has_foreign_object, class_name, confidence)
        """
        try:
            if self.model is None:
                logger.warning("Modelo não carregado - modo demonstração")
                # Simulação
                return False, "produto_limpo", 0.98

            # Pré-processar
            processed = self.preprocess_image(image)

            # Predição
            predictions = self.model.predict(processed, verbose=0)

            # Classe
            class_index = np.argmax(predictions[0])
            confidence = predictions[0][class_index]
            class_name = self.labels[class_index] if class_index < len(self.labels) else "unknown"

            # Verificar se é objeto estranho
            has_foreign_object = (
                'estranho' in class_name.lower() or 'foreign' in class_name.lower()
            ) and confidence >= CONFIDENCE_THRESHOLD

            return has_foreign_object, class_name, confidence

        except Exception as e:
            logger.error(f"Erro na detecção: {e}")
            raise

    def stop_production_line(self):
        """
        Simula parada emergencial da linha de produção

        Em produção real, isto seria integrado com:
        - PLC (Controlador Lógico Programável)
        - Sistema SCADA
        - Sirenes e luzes de alerta
        - Notificação push para supervisores
        """
        self.line_running = False
        self.line_stoppages += 1

        logger.critical("🛑 LINHA DE PRODUÇÃO PARADA - OBJETO ESTRANHO DETECTADO!")
        print("\n" + "="*70)
        print("🛑 EMERGÊNCIA: LINHA DE PRODUÇÃO PARADA")
        print("="*70)
        print("Motivo: Objeto estranho detectado na esteira")
        print("Ação: Supervisor deve remover o objeto e reiniciar manualmente")
        print(f"Total de paradas hoje: {self.line_stoppages}")
        print("="*70 + "\n")

    def restart_production_line(self):
        """
        Simula reinício da linha após inspeção
        """
        self.line_running = True
        logger.info("✓ Linha de produção reiniciada")
        print("✓ Linha de produção reiniciada\n")

    def log_detection(self, image, class_name, confidence):
        """
        Registra detecção de objeto estranho

        Args:
            image: Frame onde foi detectado
            class_name: Classe detectada
            confidence: Confiança da predição
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Salvar imagem
            image_filename = f"objeto_estranho_{timestamp}.jpg"
            image_path = os.path.join(LOGS_DIR, image_filename)
            cv2.imwrite(image_path, image)

            # Log em arquivo
            log_file = os.path.join(LOGS_DIR, "deteccoes_objetos.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                log_entry = (
                    f"[{timestamp}] - DETECÇÃO: Objeto estranho na esteira. "
                    f"Classe: {class_name}, Confiança: {confidence:.2%}, "
                    f"Imagem: {image_path}, Parada #{self.line_stoppages}\n"
                )
                f.write(log_entry)

            self.detections_count += 1

            logger.warning(f"⚠️ DETECÇÃO #{self.detections_count}: {class_name} ({confidence:.2%})")

        except Exception as e:
            logger.error(f"Erro ao registrar detecção: {e}")
            raise

    def process_single_image(self, image_path):
        """
        Processa uma única imagem (para testes)

        Args:
            image_path: Caminho da imagem
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Erro ao carregar: {image_path}")

            logger.info(f"Analisando: {image_path}")

            # Detectar
            has_foreign, class_name, confidence = self.detect_foreign_object(image)

            if has_foreign:
                print(f"\n⚠️ ALERTA: Objeto estranho detectado!")
                print(f"Classe: {class_name}")
                print(f"Confiança: {confidence:.2%}")
                self.log_detection(image, class_name, confidence)
                self.stop_production_line()
            else:
                print(f"\n✓ Esteira limpa - produção normal")
                print(f"Classe: {class_name} ({confidence:.2%})")

        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            raise

    def monitor_conveyor_belt(self, video_source=0, duration=60):
        """
        Monitora esteira transportadora em tempo real via webcam/câmera

        Args:
            video_source: 0 para webcam, ou caminho para vídeo
            duration: Duração do monitoramento em segundos
        """
        try:
            # Abrir câmera
            cap = cv2.VideoCapture(video_source)

            if not cap.isOpened():
                raise RuntimeError("Não foi possível abrir a câmera")

            logger.info(f"Iniciando monitoramento da esteira por {duration}s")
            logger.info("Pressione 'Q' para parar, 'R' para reiniciar linha")

            start_time = time.time()
            frame_count = 0

            while True:
                # Verificar tempo
                if time.time() - start_time > duration:
                    logger.info("Tempo de monitoramento concluído")
                    break

                # Capturar frame
                ret, frame = cap.read()
                if not ret:
                    logger.error("Erro ao capturar frame")
                    break

                frame_count += 1

                # Processar apenas em intervalos (economizar CPU)
                if frame_count % (30 // FRAME_RATE) == 0:

                    # Detectar objetos
                    has_foreign, class_name, confidence = self.detect_foreign_object(frame)

                    # Se linha parada, não processar
                    if not self.line_running:
                        cv2.putText(frame, "LINHA PARADA - Pressione R para reiniciar",
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        # Mostrar status
                        if has_foreign:
                            cv2.putText(frame, f"ALERTA: {class_name} ({confidence:.0%})",
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.putText(frame, "PARANDO LINHA...",
                                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                            # Registrar e parar
                            self.log_detection(frame, class_name, confidence)
                            self.stop_production_line()

                        else:
                            cv2.putText(frame, f"Operacao Normal - {class_name}",
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Mostrar estatísticas
                cv2.putText(frame, f"Deteccoes: {self.detections_count} | Paradas: {self.line_stoppages}",
                           (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Exibir frame
                cv2.imshow('Monitor de Esteira - Guardian EPI', frame)

                # Teclas
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q') or key == ord('Q'):
                    logger.info("Monitoramento interrompido pelo usuário")
                    break

                if key == ord('r') or key == ord('R'):
                    if not self.line_running:
                        self.restart_production_line()

            # Liberar recursos
            cap.release()
            cv2.destroyAllWindows()

            # Resumo
            print("\n" + "="*70)
            print("RESUMO DO MONITORAMENTO")
            print("="*70)
            print(f"Duração: {time.time() - start_time:.1f}s")
            print(f"Frames processados: {frame_count}")
            print(f"Objetos estranhos detectados: {self.detections_count}")
            print(f"Paradas de linha: {self.line_stoppages}")
            print("="*70)

        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
            raise

    def generate_quality_report(self):
        """
        Gera relatório de qualidade do turno
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            report_file = os.path.join(LOGS_DIR, f"relatorio_qualidade_{timestamp}.json")

            report = {
                "data_hora": timestamp,
                "total_deteccoes": self.detections_count,
                "paradas_linha": self.line_stoppages,
                "falsos_alarmes": self.false_alarms,
                "sistema": "Detector de Objetos Estranhos",
                "area": "Esteira de Embalagem",
                "threshold_confianca": CONFIDENCE_THRESHOLD,
                "status_linha": "EM OPERAÇÃO" if self.line_running else "PARADA"
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)

            logger.info(f"Relatório gerado: {report_file}")
            print(f"\n✓ Relatório salvo em: {report_file}")

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
    print("GUARDIAN EPI - Detector de Objetos Estranhos")
    print("Departamento de Qualidade - Linha de Produção")
    print("=" * 70)
    print()

    try:
        # Inicializar detector
        detector = DetectorObjetosEstranhos()

        # Menu
        print("Selecione o modo de operação:")
        print("1 - Analisar uma imagem única")
        print("2 - Monitorar esteira em tempo real (webcam)")
        print("3 - Gerar relatório de qualidade")
        print()

        choice = input("Escolha uma opção (1-3): ").strip()

        if choice == '1':
            image_path = input("Digite o caminho da imagem: ").strip()
            detector.process_single_image(image_path)

        elif choice == '2':
            duration = input("Duração do monitoramento em segundos (padrão: 60): ").strip()
            duration = int(duration) if duration else 60

            print(f"\nIniciando monitoramento por {duration}s...")
            print("Pressione 'Q' para parar, 'R' para reiniciar linha se parada")
            time.sleep(2)

            detector.monitor_conveyor_belt(video_source=0, duration=duration)
            detector.generate_quality_report()

        elif choice == '3':
            detector.generate_quality_report()

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
