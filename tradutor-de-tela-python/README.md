# 🌐 Tradutor de Tela Instantâneo (Python + OCR)

Uma ferramenta leve e prática desenvolvida em Python que permite selecionar qualquer trecho de texto em inglês na tela para reconhecê-lo via OCR e traduzi-lo instantaneamente para o português.

---

## 📸 Arquitetura e Estrutura do Código

![Estrutura do Código e Executável](print_codigo.png)

O projeto foi estruturado para garantir facilidade de uso e alta precisão:
- **`tradutor.py`**: Aplicação principal em Python que gerencia a interface gráfica (Tkinter), faz a captura de tela, executa a leitura OCR via Tesseract com suporte a DPI e chama a API de tradução.
- **`Abrir_Tradutor.bat`**: Script de automação no Windows que direciona a execução para o diretório local (`cd /d "%~dp0"`), permitindo rodar a aplicação com apenas dois cliques sem abrir o terminal manualmente.

---

## 🚀 Funcionalidades
- **Seleção Dinâmica:** Arraste e selecione qualquer área visível da tela.
- **DPI Aware:** Correção automática da escala do Windows para capturas precisas em qualquer monitor.
- **Processamento de Imagem:** Tratamento de contraste e escala para otimizar o reconhecimento pelo OCR.
- **Execução Simplificada:** Automação via script `.bat` para inicialização rápida.

---

## 🛠️ Tecnologias Utilizadas
- **Python 3.x**
- **Tkinter** (Interface Gráfica)
- **Tesseract OCR / `pytesseract`** (Reconhecimento de Texto)
- **OpenCV & NumPy** (Pré-processamento de Imagem)
- **Deep Translator** (Integração com Google Translate)
- **Windows Batch Script (`.bat`)** (Automação de Execução)

---

## 🔧 Como Executar o Projeto

1. Instale o **[Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)** no seu computador.
2. Instale as dependências executando no terminal:
   ```bash
   pip install pytesseract pillow deep-translator opencv-python numpy