from PIL import Image, ImageOps  # ALTERAÇÃO: ImageOps permite espelhar cada frame
import os
import re  # ALTERAÇÃO: identifica arquivos frame_000.png, frame_001.png...

# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA_FRAME = 346
ALTURA_FRAME = 400

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# procura 1.png, 2.png, 3.png...
# ALTERAÇÃO: também reconhece frame_000.png, frame_001.png... (padrão Ludo)
def numero_frame(nome):
    base, extensao = os.path.splitext(nome)
    if extensao.lower() != ".png":
        return None
    if base.isdigit():
        return int(base)
    correspondencia = re.fullmatch(r"frame_(\d+)", base, re.IGNORECASE)
    return int(correspondencia.group(1)) if correspondencia else None


arquivos_frames = [
    f for f in os.listdir(PASTA_SCRIPT)
    if numero_frame(f) is not None
]

arquivos_frames.sort(
    key=lambda f: (numero_frame(f), f.lower())
)

quantidade_frames = len(arquivos_frames)

if quantidade_frames == 0:
    print("Nenhum frame encontrado.")
    raise SystemExit


# ============================================================
# CRIA SPRITESHEET TRANSPARENTE
# ============================================================

spritesheet = Image.new(
    "RGBA",
    (LARGURA_FRAME * quantidade_frames, ALTURA_FRAME),
    (0, 0, 0, 0)
)

# ALTERAÇÃO: cria a spritesheet da esquerda com o mesmo tamanho e transparência
spritesheet_esquerda = Image.new(
    "RGBA",
    (LARGURA_FRAME * quantidade_frames, ALTURA_FRAME),
    (0, 0, 0, 0)
)


# ============================================================
# INSERE OS FRAMES
# ============================================================

# ALTERAÇÃO: guarda apenas os frames válidos para poder inverter sua ordem
frames_validos = []

for i, nome in enumerate(arquivos_frames):

    caminho = os.path.join(PASTA_SCRIPT, nome)

    img = Image.open(caminho).convert("RGBA")

    # garante exatamente o tamanho padrão
    if img.size != (LARGURA_FRAME, ALTURA_FRAME):
        print(
            f"ATENÇÃO: {nome} possui tamanho {img.size}. "
            f"O esperado é {LARGURA_FRAME} x {ALTURA_FRAME}."
        )
        continue

    # ALTERAÇÃO: insere o frame válido sem criar lacunas quando houver arquivo inválido
    x = len(frames_validos) * LARGURA_FRAME

    spritesheet.alpha_composite(
        img,
        (x, 0)
    )

    # ALTERAÇÃO: conserva a imagem original em memória para montar o sentido inverso
    frames_validos.append(img)


# ALTERAÇÃO: espelha cada frame individualmente e insere na ordem inversa
for i, img in enumerate(reversed(frames_validos)):
    x = i * LARGURA_FRAME
    img_espelhada = ImageOps.mirror(img)
    spritesheet_esquerda.alpha_composite(img_espelhada, (x, 0))

# ALTERAÇÃO: garante largura ajustada ao total de quadros válidos
if not frames_validos:
    print("Nenhum frame com as dimensões esperadas foi encontrado.")
    raise SystemExit

largura_final = LARGURA_FRAME * len(frames_validos)
spritesheet = spritesheet.crop((0, 0, largura_final, ALTURA_FRAME))
spritesheet_esquerda = spritesheet_esquerda.crop((0, 0, largura_final, ALTURA_FRAME))


# ============================================================
# SALVA
# ============================================================

saida = os.path.join(
    PASTA_SCRIPT,
    "spritesheet_direita.png"  # ALTERAÇÃO: identifica a direção no nome do arquivo
)

spritesheet.save(saida)

print("Spritesheet criado:")
print(saida)
print(
    f"Tamanho: {largura_final} x "
    f"{ALTURA_FRAME}"
)

# ALTERAÇÃO: salva a versão espelhada, com sequência do maior para o menor frame
saida_esquerda = os.path.join(PASTA_SCRIPT, "spritesheet_esquerda.png")
spritesheet_esquerda.save(saida_esquerda)

print("Spritesheet para a esquerda criado:")
print(saida_esquerda)
print(f"Tamanho: {largura_final} x {ALTURA_FRAME}")
