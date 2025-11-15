# Diretório de Imagens de Teste

Este diretório é para você colocar imagens de teste para experimentar os sistemas.

## Estrutura Sugerida

```
test_images/
├── epi/                    # Para testar monitor_epi.py
│   ├── com_epi/
│   │   ├── pessoa_com_bone_oculos_1.jpg
│   │   ├── pessoa_com_bone_oculos_2.jpg
│   │   └── ...
│   └── sem_epi/
│       ├── pessoa_sem_epi_1.jpg
│       ├── pessoa_sem_epi_2.jpg
│       └── ...
│
├── uniformes/              # Para testar controle_uniforme.py
│   ├── correto/
│   │   ├── pessoa_com_uniforme_1.jpg
│   │   └── ...
│   └── incorreto/
│       ├── pessoa_sem_uniforme_1.jpg
│       └── ...
│
└── objetos/                # Para testar detector_objetos.py
    ├── limpo/
    │   ├── esteira_limpa_1.jpg
    │   └── ...
    └── estranho/
        ├── esteira_com_caneta.jpg
        ├── esteira_com_ferramenta.jpg
        └── ...
```

## Como Criar Suas Imagens de Teste

### Para Monitor EPI

**Com EPI** (boné + óculos):
1. Tire selfies usando boné e óculos de sol
2. Varie ângulo: frontal, 45°, perfil
3. Varie distância: perto, médio, longe
4. Varie iluminação: clara, normal, escura
5. Mínimo: 10 imagens

**Sem EPI**:
1. Tire selfies sem boné ou sem óculos
2. Pode ser: sem nada, só boné, só óculos
3. Mesmas variações de ângulo, distância, luz
4. Mínimo: 10 imagens

### Para Controle de Uniformes

**Uniforme Correto**:
1. Vista algo que simule uniforme (camisa branca, por exemplo)
2. Use algum item na cabeça (touca, lenço)
3. Tire fotos de corpo inteiro ou meio corpo
4. Mínimo: 10 imagens

**Uniforme Incorreto**:
1. Mesma pessoa sem o "uniforme"
2. Ou com uniforme incompleto
3. Mínimo: 10 imagens

### Para Detector de Objetos

**Produto Limpo**:
1. Fotografe uma superfície (mesa, tapete)
2. Coloque algum "produto" (caixa, pacote)
3. Vista de cima, bem iluminado
4. Mínimo: 10 imagens

**Objeto Estranho**:
1. Mesma cena, mas adicione:
   - Caneta
   - Chave
   - Parafuso
   - Pedaço de plástico
   - Qualquer objeto pequeno
2. Mínimo: 10 imagens (diferentes objetos)

## Dicas para Boas Imagens de Teste

✅ **Boa Iluminação**
- Luz natural é melhor
- Evite sombras fortes
- Sem flash direto (cria reflexos)

✅ **Foco**
- Imagem nítida, sem blur
- Câmera estável

✅ **Resolução**
- Mínimo: 640x480
- Ideal: 1280x720 ou maior
- Formato: JPG ou PNG

✅ **Variedade**
- Diferentes pessoas (se possível)
- Diferentes ângulos
- Diferentes fundos
- Diferentes horários do dia

❌ **Evite**
- Imagens muito escuras
- Imagens tremidas (motion blur)
- Objetos muito pequenos na foto
- Ângulos muito extremos

## Formatos Suportados

Os scripts aceitam:
- `.jpg` / `.jpeg`
- `.png`
- `.bmp`

## Tamanhos Recomendados

- **Mínimo**: 224x224 (o modelo redimensiona)
- **Ideal**: 640x480 a 1920x1080
- **Máximo**: Sem limite, mas arquivos grandes demoram mais

## Como Usar

### Testar Monitor EPI

```bash
python monitor_epi.py
# Escolha opção 1
# Digite: test_images/epi/sem_epi
```

### Testar Controle de Uniformes

```bash
python controle_uniforme.py
# Escolha opção 2
# Digite: test_images/uniformes/incorreto
```

### Testar Detector de Objetos

```bash
python detector_objetos.py
# Escolha opção 1
# Digite: test_images/objetos/estranho/esteira_com_caneta.jpg
```

## Onde Conseguir Imagens de Teste

**Se não quiser tirar fotos:**

1. **Unsplash** (gratuito, sem direitos autorais)
   - https://unsplash.com/
   - Busque: "worker helmet", "factory worker", "conveyor belt"

2. **Pexels** (gratuito)
   - https://www.pexels.com/
   - Busque: "safety equipment", "industrial worker"

3. **Google Images** (cuidado com direitos!)
   - Use filtro: "Usage rights" → "Labeled for reuse"

## Privacidade

⚠️ **IMPORTANTE**:
- Não tire fotos de pessoas sem permissão
- Não use fotos de rostos identificáveis sem consentimento
- Em produção, siga LGPD/GDPR
- Para testes, use suas próprias fotos ou de voluntários

## Organização

Crie subpastas para manter organizado:

```
test_images/
└── epi/
    ├── dataset_001/     # Primeiro conjunto de testes
    ├── dataset_002/     # Segundo conjunto
    └── producao_real/   # Dados de ambiente real (se tiver)
```

---

**Dica**: Quanto mais variadas suas imagens de teste, melhor você entenderá as limitações do modelo!

**Precisa de ajuda?** Veja QUICK_START.md ou README.md
