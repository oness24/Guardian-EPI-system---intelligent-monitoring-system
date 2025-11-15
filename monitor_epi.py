"""
Guardian EPI - Sistema de Monitoramento de Equipamentos de Proteção Individual
Autor: Sistema Guardian EPI
Data: 2025
Descrição: Sistema automatizado para detectar uso inadequado de EPIs na entrada da fábrica
"""

import os
import cv2
import numpy as np
from datetime import datetime
from tensorflow import keras
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging
import json

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS
# ==============================================================================

# Caminhos dos arquivos do modelo Teachable Machine
MODEL_PATH = "models/keras_model.h5"
LABELS_PATH = "models/labels.txt"

# Diretório para armazenar logs e imagens de ocorrências
LOGS_DIR = "logs"

# Configurações de email - TODO: Substituir com credenciais reais
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # TODO: Configurar servidor SMTP
    'smtp_port': 587,
    'sender_email': 'sistema@empresa.com',  # TODO: Configurar email remetente
    'sender_password': 'sua_senha_aqui',  # TODO: Configurar senha (usar variáveis de ambiente em produção!)
    'recipient_email': 'supervisor.area@empresa.com'
}

# Configurações do modelo
IMG_SIZE = 224  # Tamanho padrão do Teachable Machine
CONFIDENCE_THRESHOLD = 0.7  # Limiar de confiança para detecção

# ==============================================================================
# CONFIGURAÇÃO DE LOGGING
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==============================================================================
# CLASSE PRINCIPAL - MONITOR EPI
# ==============================================================================

class MonitorEPI:
    """
    Classe principal para monitoramento de EPIs

    Esta classe gerencia:
    - Carregamento do modelo de ML
    - Processamento de imagens
    - Detecção de não conformidades
    - Sistema de alertas
    """

    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH):
        """
        Inicializa o monitor de EPIs

        Args:
            model_path: Caminho para o arquivo keras_model.h5
            labels_path: Caminho para o arquivo labels.txt
        """
        self.model = None
        self.labels = []
        self.model_path = model_path
        self.labels_path = labels_path

        # Criar diretório de logs se não existir
        os.makedirs(LOGS_DIR, exist_ok=True)

        # Carregar modelo e rótulos
        self._load_model()
        self._load_labels()

        logger.info("Monitor EPI inicializado com sucesso")

    def _load_model(self):
        """
        Carrega o modelo Keras treinado no Teachable Machine

        Nota: O modelo foi treinado com objetos substitutos:
        - Boné representando capacete
        - Óculos de sol representando óculos de segurança
        Em produção, retreinar com EPIs reais!
        """
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Modelo não encontrado em: {self.model_path}")

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
        Carrega os rótulos das classes do modelo
        """
        try:
            if not os.path.exists(self.labels_path):
                raise FileNotFoundError(f"Arquivo de rótulos não encontrado: {self.labels_path}")

            with open(self.labels_path, 'r', encoding='utf-8') as f:
                self.labels = [line.strip() for line in f.readlines()]

            logger.info(f"Rótulos carregados: {self.labels}")

        except Exception as e:
            logger.error(f"Erro ao carregar rótulos: {e}")
            raise

    def preprocess_image(self, image):
        """
        Pré-processa a imagem para o formato esperado pelo modelo

        Args:
            image: Imagem em formato numpy array (BGR do OpenCV)

        Returns:
            numpy array normalizado e redimensionado
        """
        try:
            # Converter BGR para RGB (OpenCV usa BGR, modelo espera RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Redimensionar para o tamanho esperado pelo modelo
            image_resized = cv2.resize(image_rgb, (IMG_SIZE, IMG_SIZE))

            # Normalizar pixels para range [0, 1]
            image_normalized = image_resized.astype(np.float32) / 255.0

            # Adicionar dimensão de batch
            image_batch = np.expand_dims(image_normalized, axis=0)

            return image_batch

        except Exception as e:
            logger.error(f"Erro no pré-processamento: {e}")
            raise

    def predict(self, image):
        """
        Realiza a predição na imagem

        Args:
            image: Imagem em formato numpy array

        Returns:
            tuple: (classe_predita, confiança)
        """
        try:
            # Pré-processar imagem
            processed_image = self.preprocess_image(image)

            # Realizar predição
            predictions = self.model.predict(processed_image, verbose=0)

            # Obter índice da classe com maior probabilidade
            class_index = np.argmax(predictions[0])
            confidence = predictions[0][class_index]

            # Obter nome da classe
            class_name = self.labels[class_index] if class_index < len(self.labels) else "unknown"

            logger.info(f"Predição: {class_name} (confiança: {confidence:.2%})")

            return class_name, confidence

        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            raise

    def create_log_entry(self, timestamp, image_path):
        """
        Cria entrada no arquivo de log

        Args:
            timestamp: String com timestamp formatado
            image_path: Caminho da imagem salva
        """
        try:
            log_file = os.path.join(LOGS_DIR, "ocorrencias_epi.log")

            with open(log_file, 'a', encoding='utf-8') as f:
                log_message = f"[{timestamp}] - ALERTA: Funcionário sem EPI detectado. Imagem: {image_path}\n"
                f.write(log_message)

            logger.info(f"Log criado: {log_message.strip()}")

        except Exception as e:
            logger.error(f"Erro ao criar log: {e}")
            raise

    def save_alert_image(self, image, timestamp):
        """
        Salva a imagem que gerou o alerta

        Args:
            image: Imagem em formato numpy array
            timestamp: String com timestamp formatado

        Returns:
            Caminho completo da imagem salva
        """
        try:
            filename = f"imagem_ocorrencia_{timestamp}.jpg"
            image_path = os.path.join(LOGS_DIR, filename)

            # Salvar imagem
            cv2.imwrite(image_path, image)

            logger.info(f"Imagem de alerta salva: {image_path}")

            return image_path

        except Exception as e:
            logger.error(f"Erro ao salvar imagem: {e}")
            raise

    def send_email_alert(self, timestamp, image_path):
        """
        Envia email de alerta para o supervisor

        Args:
            timestamp: String com timestamp formatado
            image_path: Caminho da imagem a ser anexada
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['recipient_email']
            msg['Subject'] = 'ALERTA SEGURANCA: Funcionario sem EPI detectado'

            # Corpo do email
            body = f"""
            Um funcionário foi detectado sem o EPI correto na entrada da fábrica em {timestamp}.

            Verifique o arquivo de log e a imagem anexada.

            Sistema Guardian EPI
            """
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Anexar imagem
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data, name=os.path.basename(image_path))
                    msg.attach(image)

            # Enviar email
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                server.send_message(msg)

            logger.info(f"Email enviado para: {EMAIL_CONFIG['recipient_email']}")

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            logger.warning("Sistema continuará funcionando, mas notificação por email falhou")

    def trigger_alert(self, image):
        """
        Aciona sequência completa de alerta

        Args:
            image: Imagem que gerou o alerta
        """
        try:
            # Gerar timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Salvar imagem
            image_path = self.save_alert_image(image, timestamp)

            # Criar entrada no log
            self.create_log_entry(timestamp, image_path)

            # Enviar email (com tratamento de erro para não bloquear o sistema)
            try:
                self.send_email_alert(timestamp, image_path)
            except Exception as email_error:
                logger.warning(f"Falha no envio de email: {email_error}")

            logger.warning("ALERTA: Funcionário sem EPI detectado!")

        except Exception as e:
            logger.error(f"Erro na sequência de alerta: {e}")
            raise

    def process_image_file(self, image_path):
        """
        Processa uma imagem de arquivo

        Args:
            image_path: Caminho do arquivo de imagem
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

            # Carregar imagem
            image = cv2.imread(image_path)

            if image is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image_path}")

            logger.info(f"Processando imagem: {image_path}")

            # Realizar predição
            class_name, confidence = self.predict(image)

            # Verificar se é sem EPI e confiança é suficiente
            if 'sem_epi' in class_name.lower() and confidence >= CONFIDENCE_THRESHOLD:
                logger.warning(f"⚠️ Detectado: {class_name} (confiança: {confidence:.2%})")
                self.trigger_alert(image)
            else:
                logger.info(f"✓ EPI adequado detectado (classe: {class_name}, confiança: {confidence:.2%})")

        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            raise

    def process_directory(self, directory_path):
        """
        Processa todas as imagens em um diretório

        Args:
            directory_path: Caminho do diretório com imagens
        """
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Diretório não encontrado: {directory_path}")

            # Extensões de imagem suportadas
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

            # Listar arquivos de imagem
            image_files = [
                f for f in os.listdir(directory_path)
                if os.path.splitext(f)[1].lower() in valid_extensions
            ]

            if not image_files:
                logger.warning(f"Nenhuma imagem encontrada em: {directory_path}")
                return

            logger.info(f"Encontradas {len(image_files)} imagens para processar")

            # Processar cada imagem
            for image_file in image_files:
                image_path = os.path.join(directory_path, image_file)
                self.process_image_file(image_path)

        except Exception as e:
            logger.error(f"Erro ao processar diretório: {e}")
            raise

    def capture_from_webcam(self):
        """
        MÉTODO EXTRA: Captura imagem em tempo real da webcam e processa

        Uso: Pressione ESPAÇO para capturar, ESC para sair
        """
        try:
            # Inicializar webcam
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                raise RuntimeError("Não foi possível abrir a webcam")

            logger.info("Webcam ativada. Pressione ESPAÇO para capturar, ESC para sair")

            while True:
                # Capturar frame
                ret, frame = cap.read()

                if not ret:
                    logger.error("Erro ao capturar frame da webcam")
                    break

                # Mostrar preview
                cv2.putText(frame, "Pressione ESPACO para capturar, ESC para sair",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('Guardian EPI - Webcam', frame)

                # Aguardar tecla
                key = cv2.waitKey(1) & 0xFF

                # ESC para sair
                if key == 27:
                    logger.info("Saindo do modo webcam")
                    break

                # ESPAÇO para capturar
                if key == 32:
                    logger.info("Capturando imagem da webcam...")

                    # Realizar predição
                    class_name, confidence = self.predict(frame)

                    # Verificar se é sem EPI
                    if 'sem_epi' in class_name.lower() and confidence >= CONFIDENCE_THRESHOLD:
                        logger.warning(f"⚠️ Detectado: {class_name} (confiança: {confidence:.2%})")
                        self.trigger_alert(frame)

                        # Feedback visual
                        cv2.putText(frame, "ALERTA: SEM EPI!", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                        cv2.imshow('Guardian EPI - Webcam', frame)
                        cv2.waitKey(2000)  # Mostrar alerta por 2 segundos
                    else:
                        logger.info(f"✓ EPI adequado (classe: {class_name}, confiança: {confidence:.2%})")

                        # Feedback visual
                        cv2.putText(frame, "EPI OK!", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        cv2.imshow('Guardian EPI - Webcam', frame)
                        cv2.waitKey(1000)  # Mostrar por 1 segundo

            # Liberar recursos
            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            logger.error(f"Erro no modo webcam: {e}")
            raise


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def main():
    """
    Função principal do programa
    """
    print("=" * 70)
    print("GUARDIAN EPI - Sistema de Monitoramento de EPIs")
    print("=" * 70)
    print()

    try:
        # Inicializar monitor
        monitor = MonitorEPI()

        # Menu de opções
        print("Selecione o modo de operação:")
        print("1 - Processar imagens de um diretório")
        print("2 - Processar uma única imagem")
        print("3 - Capturar da webcam (EXTRA)")
        print()

        choice = input("Escolha uma opção (1-3): ").strip()

        if choice == '1':
            directory = input("Digite o caminho do diretório com imagens: ").strip()
            monitor.process_directory(directory)

        elif choice == '2':
            image_path = input("Digite o caminho da imagem: ").strip()
            monitor.process_image_file(image_path)

        elif choice == '3':
            print("\nIniciando modo webcam...")
            monitor.capture_from_webcam()

        else:
            print("Opção inválida!")
            return

        print("\nProcessamento concluído!")
        print(f"Logs salvos em: {os.path.abspath(LOGS_DIR)}")

    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        print(f"\n❌ Erro: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
