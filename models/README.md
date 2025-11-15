# Diretório de Modelos

Este diretório deve conter os modelos treinados no **Google Teachable Machine**.

## Arquivos Necessários

### Para Monitor EPI (monitor_epi.py)
- `keras_model.h5` - Modelo treinado
- `labels.txt` - Rótulos das classes

### Para Controle de Uniformes (controle_uniforme.py)
- `uniforme_model.h5` - Modelo treinado
- `uniforme_labels.txt` - Rótulos das classes

### Para Detector de Objetos (detector_objetos.py)
- `objeto_model.h5` - Modelo treinado
- `objeto_labels.txt` - Rótulos das classes

## Como Obter os Modelos

1. Acesse: https://teachablemachine.withgoogle.com/
2. Treine seu modelo (veja QUICK_START.md para instruções)
3. Exporte como **TensorFlow → Keras**
4. Baixe os arquivos
5. Coloque neste diretório
6. Renomeie conforme indicado acima

## Formato dos Arquivos de Rótulos

**labels.txt** (exemplo):
```
0 com_epi
1 sem_epi
```

**uniforme_labels.txt** (exemplo):
```
0 uniforme_correto
1 uniforme_incorreto
```

**objeto_labels.txt** (exemplo):
```
0 produto_limpo
1 objeto_estranho
```

## Notas Importantes

⚠️ **Não faça commit dos arquivos .h5 no Git!**
- São arquivos grandes (>5MB)
- Estão no .gitignore por isso
- Suba para Google Drive, Dropbox ou similares se precisar compartilhar

✅ **Arquivos de rótulos (.txt) PODEM ser versionados**
- São pequenos
- Ajudam a documentar as classes

## Tamanho Esperado

- `keras_model.h5`: ~5-10 MB
- `labels.txt`: < 1 KB

Se seus arquivos forem muito diferentes, algo pode estar errado!

## Troubleshooting

**Erro: "Modelo não encontrado"**
- Verifique se o arquivo está neste diretório
- Verifique o nome do arquivo (case-sensitive no Linux!)
- Certifique-se que baixou o formato Keras, não TFLite

**Erro: "Rótulos não encontrados"**
- O arquivo labels.txt vem junto com o modelo
- Está dentro do ZIP que você baixou do Teachable Machine
- Não renomeie ou edite, use como está

---

**Precisa de ajuda?** Veja QUICK_START.md ou README.md
