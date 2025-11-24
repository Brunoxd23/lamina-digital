import os
import openslide
from openslide.deepzoom import DeepZoomGenerator
import shutil

# Configurações
SLIDE_DIR = "."
OUTPUT_DIR = "static_site"
TILES_DIR = os.path.join(OUTPUT_DIR, "tiles")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_html(slide_name, width, height):
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{slide_name}</title>
    <script src="https://openseadragon.github.io/openseadragon/openseadragon.min.js"></script>
    <style>
        body {{ margin: 0; background-color: #000; color: white; font-family: sans-serif; }}
        #openseadragon1 {{ width: 100vw; height: 100vh; }}
        .back-btn {{ position: absolute; top: 10px; left: 10px; z-index: 100; background: white; color: black; padding: 10px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-btn">Voltar</a>
    <div id="openseadragon1"></div>
    <script type="text/javascript">
        var viewer = OpenSeadragon({{
            id: "openseadragon1",
            prefixUrl: "https://openseadragon.github.io/openseadragon/images/",
            tileSources: "{slide_name}.dzi"
        }});
    </script>
</body>
</html>
    """
    return html_content

def create_index_html(slides):
    links = "\n".join([f'<li><a href="view/{slide}.html">{slide}</a></li>' for slide in slides])
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Laminário Digital</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; background: #f0f0f0; }}
        h1 {{ color: #333; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 10px 0; }}
        a {{ text-decoration: none; color: #0070f3; font-size: 1.2em; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Laminário Digital - Einstein</h1>
    <ul>
        {links}
    </ul>
</body>
</html>
    """
    return html_content

def convert_slides():
    ensure_dir(OUTPUT_DIR)
    ensure_dir(TILES_DIR)
    
    slides_processed = []
    
    files = [f for f in os.listdir(SLIDE_DIR) if f.lower().endswith('.svs')]
    print(f"Encontrados {len(files)} arquivos .svs")

    for filename in files:
        slide_name = os.path.splitext(filename)[0]
        print(f"Processando {slide_name}...")
        
        try:
            slide_path = os.path.join(SLIDE_DIR, filename)
            slide = openslide.OpenSlide(slide_path)
            
            # Gerar Tiles
            # Usar deepzoom generator
            creator = DeepZoomGenerator(slide, tile_size=254, overlap=1, limit_bounds=True)
            
            # O DeepZoomGenerator gera tiles e o arquivo .dzi
            # Vamos salvar diretamente na pasta do slide dentro de tiles
            # Mas o método .create() não existe, temos que iterar ou usar bibliotecas auxiliares?
            # O DeepZoomGenerator do openslide não tem um método 'save_all'.
            # Vamos usar uma abordagem mais simples: o DeepZoomGenerator gera tiles sob demanda ou podemos iterar.
            # Mas para facilitar, vamos usar o método get_dzi e salvar os tiles manualmente?
            # Não, o DeepZoomGenerator é para servir dinamicamente.
            # Para salvar estático, precisamos iterar sobre os níveis e tiles.
            
            # Felizmente, o openslide-python vem com um script deepzoom_tile.py de exemplo, mas não está exposto diretamente.
            # Vamos implementar um loop simples de salvamento.
            
            slide_output_dir = os.path.join(TILES_DIR, slide_name + "_files")
            # ensure_dir(slide_output_dir) # O deepzoom generator cria a estrutura
            
            # DZI file
            dzi_path = os.path.join(TILES_DIR, slide_name + ".dzi")
            with open(dzi_path, 'w') as f:
                f.write(creator.get_dzi('jpeg'))
                
            # Salvar tiles
            # Iterar níveis
            for level in range(creator.level_count):
                print(f"  Gerando nível {level}/{creator.level_count-1}")
                level_dir = os.path.join(slide_output_dir, str(level))
                ensure_dir(level_dir)
                
                cols, rows = creator.level_tiles[level]
                for col in range(cols):
                    for row in range(rows):
                        tile = creator.get_tile(level, (col, row))
                        tile_path = os.path.join(level_dir, f"{col}_{row}.jpeg")
                        tile.save(tile_path, "JPEG", quality=90)
            
            # Criar página HTML para este slide
            view_dir = os.path.join(OUTPUT_DIR, "view")
            ensure_dir(view_dir)
            
            # O HTML precisa apontar para o DZI. 
            # Estrutura:
            # static_site/
            #   index.html
            #   view/
            #     slide1.html
            #   tiles/
            #     slide1.dzi
            #     slide1_files/
            
            # No HTML dentro de view/, o dzi está em ../tiles/slide1.dzi
            
            html = create_html(f"../tiles/{slide_name}", slide.dimensions[0], slide.dimensions[1])
            with open(os.path.join(view_dir, f"{slide_name}.html"), 'w', encoding='utf-8') as f:
                f.write(html)
                
            slides_processed.append(slide_name)
            print(f"Concluído: {slide_name}")
            
        except Exception as e:
            print(f"Erro ao processar {filename}: {e}")

    # Criar index.html
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(create_index_html(slides_processed))

if __name__ == "__main__":
    convert_slides()
