import os
import sys
import glob
from flask import Flask, send_file, abort, Response, render_template_string, url_for
import openslide
from openslide.deepzoom import DeepZoomGenerator
from io import BytesIO

app = Flask(__name__)

# Configurações
SLIDES_DIR = os.path.dirname(os.path.abspath(__file__))
TILE_SIZE = 256
OVERLAP = 0
FORMAT = 'jpeg'
QUALITY = 90

# Cache simples para objetos OpenSlide
slides_cache = {}

def get_slide_generator(filename):
    """Retorna o gerador DeepZoom para o arquivo solicitado, usando cache."""
    filepath = os.path.join(SLIDES_DIR, filename)
    
    # Segurança básica para evitar path traversal
    if '..' in filename or not os.path.isfile(filepath):
        return None
    
    if filename not in slides_cache:
        try:
            slide = openslide.open_slide(filepath)
            dz = DeepZoomGenerator(slide, tile_size=TILE_SIZE, overlap=OVERLAP, limit_bounds=False)
            slides_cache[filename] = (slide, dz)
            print(f"Carregado: {filename}")
        except Exception as e:
            print(f"Erro ao carregar {filename}: {e}")
            return None
            
    return slides_cache[filename][1]

def get_slide_object(filename):
    if get_slide_generator(filename):
        return slides_cache[filename][0]
    return None

# --- Templates HTML ---

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>Laminário Einstein</title>
  <style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; }
    header { text-align: center; margin-bottom: 40px; }
    h1 { color: #2c3e50; margin: 0; font-size: 2.5em; }
    p { color: #7f8c8d; }
    .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; max-width: 1400px; margin: 0 auto; }
    .card { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); overflow: hidden; transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; text-decoration: none; color: inherit; display: flex; flex-direction: column; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .thumb-container { height: 200px; background: #ecf0f1; display: flex; align-items: center; justify-content: center; overflow: hidden; }
    .thumb { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
    .card:hover .thumb { transform: scale(1.05); }
    .info { padding: 20px; border-top: 1px solid #eee; }
    .title { font-weight: 600; font-size: 1.1em; color: #34495e; display: block; margin-bottom: 8px; word-break: break-all; }
    .meta { font-size: 0.85em; color: #95a5a6; display: flex; align-items: center; gap: 5px; }
  </style>
</head>
<body>
  <header>
    <h1>Laminário Digital</h1>
    <p>Selecione uma lâmina para visualizar</p>
  </header>
  <div class="gallery">
    {% for slide in slides %}
    <a href="{{ url_for('view_slide', slug=slide.filename.replace('.svs', '')) }}" class="card">
      <div class="thumb-container">
        <img src="{{ url_for('thumbnail', filename=slide.filename) }}" class="thumb" loading="lazy" alt="Thumbnail">
      </div>
      <div class="info">
        <span class="title">{{ slide.filename.replace('.svs', '') }}</span>
        <span class="meta">🔍 Visualizar Lâmina</span>
      </div>
    </a>
    {% else %}
    <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #7f8c8d;">
      <h3>Nenhuma lâmina (.svs) encontrada.</h3>
    </div>
    {% endfor %}
  </div>
</body>
</html>
"""

VIEWER_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>{{ display_name }}</title>
  <script src="/static/openseadragon.min.js"></script>
  <style>
    body { margin:0; font-family: 'Segoe UI', sans-serif; background: #000; overflow: hidden; }
    #viewer { width:100vw; height:100vh; }
    .header-overlay { position: fixed; top: 0; left: 0; width: 100%; padding: 15px 20px; background: linear-gradient(to bottom, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%); z-index: 1000; display: flex; align-items: center; justify-content: space-between; pointer-events: none; }
    .back-btn { pointer-events: auto; background: rgba(255,255,255,0.2); backdrop-filter: blur(5px); color: white; text-decoration: none; padding: 8px 16px; border-radius: 20px; font-weight: 500; font-size: 14px; transition: background 0.2s; display: flex; align-items: center; gap: 5px; border: 1px solid rgba(255,255,255,0.1); margin-right: 50px; }
    .back-btn:hover { background: rgba(255,255,255,0.3); }
    .slide-title { color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 500; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
  </style>
</head>
<body>
<div class="header-overlay">
    <span class="slide-title">{{ display_name }}</span>
    <a href="{{ url_for('index') }}" class="back-btn">Voltar <span>❯</span></a>
</div>
<div id="viewer"></div>
<script>
  const viewer = OpenSeadragon({
    id: 'viewer',
    prefixUrl: 'https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/images/',
    tileSources: "{{ url_for('dzi', filename=filename) }}",
    showRotationControl: true,
    showNavigator: true,
    navigatorPosition: 'BOTTOM_RIGHT',
    animationTime: 0.5,
    blendTime: 0.1,
    constrainDuringPan: true,
    maxZoomPixelRatio: 2,
    minZoomImageRatio: 1,
    visibilityRatio: 1,
    zoomPerScroll: 2
  });
</script>
</body>
</html>
"""

# --- Rotas ---

@app.route('/')
def index():
    files = glob.glob(os.path.join(SLIDES_DIR, "*.svs"))
    slides_list = []
    for f in files:
        slides_list.append({'filename': os.path.basename(f)})
    slides_list.sort(key=lambda x: x['filename'])
    return render_template_string(INDEX_TEMPLATE, slides=slides_list)

@app.route('/<path:slug>')
def view_slide(slug):
    # Ignora rotas de sistema
    if slug.startswith('api/') or slug.startswith('static/') or slug == 'favicon.ico':
        abort(404)

    # Lógica de busca do arquivo
    filename = slug
    
    # 1. Tenta exato
    if os.path.isfile(os.path.join(SLIDES_DIR, filename)):
        pass
    # 2. Tenta adicionar .svs
    elif os.path.isfile(os.path.join(SLIDES_DIR, filename + '.svs')):
        filename = filename + '.svs'
    # 3. Tenta encontrar arquivo que COMEÇA com o slug (ex: 1460 -> 1460-09.svs)
    else:
        candidates = glob.glob(os.path.join(SLIDES_DIR, f"{slug}*.svs"))
        if candidates:
            filename = os.path.basename(candidates[0])
        else:
            abort(404)

    return render_template_string(VIEWER_TEMPLATE, filename=filename, display_name=slug)

@app.route('/thumbnail/<path:filename>')
def thumbnail(filename):
    slide = get_slide_object(filename)
    if not slide: abort(404)
    try:
        thumb = slide.get_thumbnail((400, 400))
        buf = BytesIO()
        thumb.save(buf, 'JPEG', quality=85)
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')
    except: abort(500)

@app.route('/api/<path:filename>.dzi')
def dzi(filename):
    dz = get_slide_generator(filename)
    if dz is None: abort(404)
    return Response(dz.get_dzi(FORMAT), mimetype='application/xml')

@app.route('/api/<path:filename>_files/<int:level>/<int:col>_<int:row>.jpeg')
def tile(filename, level, col, row):
    dz = get_slide_generator(filename)
    if dz is None: abort(404)
    try:
        tile_img = dz.get_tile(level, (col, row))
        buf = BytesIO()
        tile_img.save(buf, FORMAT, quality=QUALITY)
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')
    except: abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
