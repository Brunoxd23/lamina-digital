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
    # slide_name vem como "../tiles/nome_do_slide"
    # Precisamos extrair apenas o nome para exibir no título
    display_name = os.path.basename(slide_name)
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{display_name}</title>
    <script src="https://openseadragon.github.io/openseadragon/openseadragon.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ margin: 0; background-color: #000; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }}
        #openseadragon1 {{ width: 100vw; height: 100vh; }}
        
        .top-bar {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
            box-sizing: border-box;
            z-index: 100;
            backdrop-filter: blur(5px);
        }}

        .title {{
            font-size: 1.2rem;
            font-weight: 500;
            color: #fff;
        }}

        .controls {{
            display: flex;
            gap: 15px;
        }}

        .btn {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
        }}

        .btn:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }}

        .btn-primary {{
            background: #0070f3;
            border-color: #0070f3;
        }}
        
        .btn-primary:hover {{
            background: #0060df;
        }}

    </style>
</head>
<body>
    <div class="top-bar">
        <div class="title">{display_name}</div>
        <div class="controls">
            <button id="rotate-btn" class="btn" onclick="rotateViewer()">
                <i class="fas fa-rotate-right"></i> Rotacionar
            </button>
            <a href="../index.html" class="btn btn-primary">
                <i class="fas fa-arrow-left"></i> Voltar
            </a>
        </div>
    </div>
    
    <div id="openseadragon1"></div>
    
    <script type="text/javascript">
        var viewer = OpenSeadragon({{
            id: "openseadragon1",
            prefixUrl: "https://openseadragon.github.io/openseadragon/images/",
            tileSources: "{slide_name}.dzi",
            showNavigator: true,
            navigatorPosition: "BOTTOM_RIGHT",
            showRotationControl: true,
            gestureSettingsMouse: {{
                clickToZoom: false
            }}
        }});

        function rotateViewer() {{
            var currentRotation = viewer.viewport.getRotation();
            viewer.viewport.setRotation(currentRotation + 90);
        }}
    </script>
</body>
</html>
    """
    return html_content

def create_index_html(slides):
    cards = ""
    for slide in slides:
        cards += f"""
        <a href="view/{slide}.html" class="card">
            <div class="card-icon">
                <i class="fas fa-microscope"></i>
            </div>
            <div class="card-content">
                <h2>{slide}</h2>
                <p>Visualizar lâmina digital</p>
            </div>
        </a>
        """
        
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Laminário Digital - Einstein</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0;
            padding: 0;
            background: #f5f7fa;
            color: #333;
        }}
        
        header {{
            background: #fff;
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        header h1 {{
            margin: 0;
            font-size: 1.5rem;
            color: #0070f3;
        }}

        .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            text-decoration: none;
            color: inherit;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            border: 1px solid #eaeaea;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 15px;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.08);
            border-color: #0070f3;
        }}

        .card-icon {{
            width: 60px;
            height: 60px;
            background: #e6f1ff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #0070f3;
            font-size: 24px;
        }}

        .card-content h2 {{
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
        }}

        .card-content p {{
            margin: 5px 0 0;
            font-size: 0.9rem;
            color: #666;
        }}
    </style>
</head>
<body>
    <header>
        <i class="fas fa-dna" style="font-size: 24px; color: #0070f3;"></i>
        <h1>Laminário Digital - Einstein</h1>
    </header>
    <div class="container">
        <div class="grid">
            {cards}
        </div>
    </div>
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
            
            # Verificar se já existe
            slide_output_dir = os.path.join(TILES_DIR, slide_name + "_files")
            dzi_path = os.path.join(TILES_DIR, slide_name + ".dzi")
            
            if os.path.exists(slide_output_dir) and os.path.exists(dzi_path):
                print(f"  Tiles já existem para {slide_name}. Pulando geração de imagens.")
            else:
                # Gerar Tiles
                creator = DeepZoomGenerator(slide, tile_size=254, overlap=1, limit_bounds=True)
                
                # DZI file
                with open(dzi_path, 'w') as f:
                    f.write(creator.get_dzi('jpeg'))
                    
                # Salvar tiles
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
            
            # Criar página HTML para este slide (Sempre recriar para atualizar layout)
            view_dir = os.path.join(OUTPUT_DIR, "view")
            ensure_dir(view_dir)
            
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
