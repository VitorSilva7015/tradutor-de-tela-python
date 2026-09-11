import sys
import tkinter as tk
from tkinter import messagebox
import pytesseract
from PIL import ImageGrab, Image
import cv2  # Usaremos OpenCV para pré-processar a imagem
import numpy as np
from deep_translator import GoogleTranslator

# --- CONFIGURAÇÃO ---
# Se você instalou o Tesseract em outro lugar, altere aqui.
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Idioma de origem (inglês) e destino (português)
LANG_SOURCE = 'eng'
LANG_TARGET = 'pt'
# --- FIM DA CONFIGURAÇÃO ---

# Tenta configurar o caminho do Tesseract
try:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
except Exception as e:
    print(f"Erro ao configurar Tesseract. Verifique o caminho:\n{e}")

class TradutorDeTela:
    def __init__(self, root):
        self.root = root
        self.root.title("Tradutor de Tela v2.0 - Super Precisão")
        self.root.geometry("350x150")
        self.root.attributes("-topmost", True)  # Mantém a janela sempre visível

        # Container para centralizar o botão
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(expand=True)

        self.btn_capturar = tk.Button(
            frame, 
            text="SELECIONAR ÁREA DA TELA", 
            command=self.iniciar_selecao,
            bg="#2ecc71",  # Verde mais vibrante
            fg="white", 
            font=("Segoe UI", 12, "bold"),
            padx=15, 
            pady=10,
            relief="raised",
            cursor="hand2"
        )
        self.btn_capturar.pack()
        
        lbl_info = tk.Label(frame, text="Desenhe um retângulo ao redor do texto.", font=("Segoe UI", 8), fg="gray")
        lbl_info.pack(pady=(5,0))

    def iniciar_selecao(self):
        self.root.iconify()  # Minimiza a janela principal
        
        # Cria uma janela transparente cobrindo toda a tela
        self.canvas_win = tk.Toplevel()
        self.canvas_win.attributes("-fullscreen", True)
        self.canvas_win.attributes("-alpha", 0.3) # Transparência
        self.canvas_win.attributes("-topmost", True)
        self.canvas_win.config(cursor="cross")

        self.canvas = tk.Canvas(self.canvas_win, cursor="cross", bg="grey")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.start_x = None
        self.start_y = None
        self.rect = None

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        # Cria o retângulo inicial
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="#e74c3c", width=3)

    def on_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        # Atualiza o tamanho do retângulo enquanto arrasta
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x, end_y = (event.x, event.y)
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        # Fecha a janela de seleção e restaura a principal
        self.canvas_win.destroy()
        self.root.deiconify()

        # Verifica se a seleção é grande o suficiente
        if x2 - x1 > 20 and y2 - y1 > 20:
            self.processar_traducao(x1, y1, x2, y2)
        else:
            messagebox.showwarning("Seleção Muito Pequena", "Por favor, selecione uma área maior ao redor do texto.")

    def processar_traducao(self, x1, y1, x2, y2):
        try:
            # Tira print da área selecionada
            imagem_pil = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # --- SUPER MELHORIA DE IMAGEM COM OPENCV ---
            # Converte imagem PIL para formato que o OpenCV entende (numpy array)
            imagem_np = np.array(imagem_pil)
            imagem_cv = cv2.cvtColor(imagem_np, cv2.COLOR_RGB2BGR)

            # 1. Converte para tons de cinza
            gray = cv2.cvtColor(imagem_cv, cv2.COLOR_BGR2GRAY)

            # 2. Aplica limiarização adaptativa para aumentar o contraste (letras pretas, fundo branco)
            # Isso ajuda MUITO quando o fundo não é uniforme (como no Discord)
            processed_img = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # 3. Aumenta a imagem (Redimensiona 2x) para o Tesseract ver melhor letras pequenas
            height, width = processed_img.shape
            processed_img = cv2.resize(processed_img, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
            # --- FIM DA MELHORIA ---

            # Extrai o texto da imagem MELHORADA em inglês
            # Usamos o idioma configurado e algumas configurações extras para melhor leitura de parágrafos
            config_extra = r'--oem 3 --psm 6' # OEM 3 (LSTM), PSM 6 (Supor um bloco de texto uniforme)
            texto_extraido = pytesseract.image_to_string(processed_img, lang=LANG_SOURCE, config=config_extra).strip()

            if not texto_extraido or len(texto_extraido) < 3:
                # Se não leu quase nada, mostra o que leu e avisa
                self.mostrar_resultado(f"[A leitura falhou. Texto lido: '{texto_extraido}']", "[Não foi possível traduzir]")
                return

            # Traduz para o português
            # 'auto' tenta detectar o idioma, caso o texto não seja estritamente inglês
            traducao = GoogleTranslator(source='auto', target=LANG_TARGET).translate(texto_extraido)

            # Exibe a tradução em uma janela de resultado
            self.mostrar_resultado(texto_extraido, traducao)

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro ao processar a tradução:\n{e}")

    def mostrar_resultado(self, original, traduzido):
        # Cria uma janela customizada para o resultado
        res_win = tk.Toplevel(self.root)
        res_win.title("Resultado da Tradução")
        res_win.geometry("500x400")
        res_win.attributes("-topmost", True)
        res_win.config(padx=15, pady=15)

        # Estilo para os labels
        lbl_style = {"font": ("Segoe UI", 10, "bold"), "anchor": "w"}

        # Texto Original
        tk.Label(res_win, text="Texto Original (Inglês):", **lbl_style).pack(fill="x", pady=(0, 5))
        txt_orig = tk.Text(res_win, height=6, wrap="word", font=("Consolas", 9), bg="#f8f9fa", padx=5, pady=5)
        txt_orig.insert("1.0", original)
        txt_orig.config(state="disabled") # Deixa apenas leitura
        txt_orig.pack(fill="x", pady=(0, 15))

        # Texto Traduzido
        tk.Label(res_win, text="Tradução (Português):", **lbl_style, fg="#27ae60").pack(fill="x", pady=(0, 5))
        
        # Container com barra de rolagem para a tradução
        frame_trad = tk.Frame(res_win)
        frame_trad.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(frame_trad)
        scrollbar.pack(side="right", fill="y")
        
        txt_trad = tk.Text(frame_trad, wrap="word", font=("Segoe UI", 10), bg="#eafaf1", padx=5, pady=5, yscrollcommand=scrollbar.set)
        txt_trad.insert("1.0", traduzido)
        txt_trad.config(state="disabled")
        txt_trad.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=txt_trad.yview)

        # Botão para fechar
        tk.Button(res_win, text="Fechar", command=res_win.destroy, font=("Segoe UI", 9), padx=10).pack(pady=(15, 0))

if __name__ == "__main__":
    root = tk.Tk()
    # Tenta definir um ícone padrão, se não conseguir, tudo bem
    try:
        root.iconbitmap(r'C:\Windows\System32\shell32.dll') # Usa um ícone do sistema
    except:
        pass
    app = TradutorDeTela(root)
    root.mainloop()