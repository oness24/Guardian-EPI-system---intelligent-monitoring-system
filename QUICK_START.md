# Guia Rápido - Guardian EPI

Este guia te leva de zero a rodando em **10 minutos**! ⚡

---

## Passo 1: Instale Python (se ainda não tem)

**Windows**:
- Baixe em: https://www.python.org/downloads/
- Durante instalação, marque "Add Python to PATH"

**Linux/Mac**:
```bash
# Já vem instalado, mas verifique a versão
python3 --version  # Precisa ser 3.8 ou superior
```

---

## Passo 2: Clone ou Baixe o Projeto

```bash
# Se tem Git instalado
git clone https://github.com/seu-usuario/guardian-epi.git
cd guardian-epi

# OU simplesmente baixe o ZIP e extraia
```

---

## Passo 3: Crie Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

Você verá `(venv)` no início do prompt - isso significa que está ativo! ✅

---

## Passo 4: Instale Dependências

```bash
pip install -r requirements.txt
```

☕ Vai demorar ~2-5 minutos. Hora do café!

---

## Passo 5: Treine seu Modelo (5 minutos)

1. Acesse: **https://teachablemachine.withgoogle.com/**

2. Clique em **"Get Started"** → **"Image Project"** → **"Standard Image Model"**

3. **Crie 2 classes**:
   - `com_epi` - Tire ~30 fotos suas usando boné e óculos
   - `sem_epi` - Tire ~30 fotos suas sem boné ou óculos

4. Clique em **"Train Model"** (aguarde ~1 minuto)

5. Clique em **"Export Model"** → **"TensorFlow"** → **"Keras"**

6. Baixe e extraia:
   - `keras_model.h5`
   - `labels.txt`

7. Coloque na pasta `models/` do projeto

---

## Passo 6: Configure Email (opcional)

Se quiser receber alertas por email:

```bash
# Copie o template
cp config/.env.template config/.env

# Edite config/.env e preencha:
# - SENDER_EMAIL=seu-email@gmail.com
# - SENDER_PASSWORD=sua_app_password
# - SUPERVISOR_EMAIL=destinatario@email.com
```

**Gmail**: Use "App Password", não sua senha normal!
- Instruções: https://support.google.com/accounts/answer/185833

---

## Passo 7: RODE! 🚀

```bash
python monitor_epi.py
```

**Menu aparece:**
```
1 - Processar imagens de um diretório
2 - Processar uma única imagem
3 - Capturar da webcam (EXTRA)
```

### Opção 3 é a mais divertida! 🎥

Escolha 3, pressione ESPAÇO para capturar!

---

## Testando Sem Treinar Modelo

Se não quiser treinar modelo agora, pode testar a estrutura:

```bash
# O código vai avisar que modelo não foi encontrado
# Mas você pode ver a estrutura funcionando
python monitor_epi.py
```

---

## Problemas Comuns

### "ModuleNotFoundError: No module named 'tensorflow'"

**Solução**: Você esqueceu de ativar o venv!
```bash
# Ative novamente
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### "FileNotFoundError: keras_model.h5"

**Solução**: Você precisa treinar e baixar o modelo do Teachable Machine primeiro (Passo 5)

### "Erro ao enviar email"

**Solução**:
1. Verifique se preencheu config/.env
2. Gmail? Use App Password, não senha normal
3. Pode comentar a parte de email se só quer testar

---

## Próximos Passos

Agora que está rodando:

1. ✅ Leia o **README.md** completo para detalhes
2. 🎓 Veja **docs/HISTORICO_PROMPTS.md** para entender o design
3. 📊 Leia **docs/RELATORIO_DESEMPENHO.md** para melhorias
4. 🚀 Experimente `controle_uniforme.py` e `detector_objetos.py`

---

## Precisa de Ajuda?

1. Leia o README.md
2. Verifique os comentários no código
3. Abra uma issue no GitHub
4. Busque no Google: "teachable machine python tutorial"

---

## Dica Pro 💡

Quer impressionar?

1. Treine modelos melhores (100+ fotos por classe)
2. Teste com diferentes iluminações
3. Adicione mais classes (sem_capacete, sem_oculos, sem_ambos)
4. Crie um dashboard web com Streamlit

---

**Boa sorte! Que a IA esteja com você!** 🤖🛡️

*Qualquer dúvida, consulte o README.md completo*
