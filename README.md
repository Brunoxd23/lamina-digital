# Visualização de Lâmina (.svs) com Flask + OpenSlide + OpenSeadragon

Este projeto fornece um visualizador web simples para arquivos de lâmina digital em formato `SVS` (Aperio) usando:

- **OpenSlide** para leitura do arquivo de pirâmide.
- **DeepZoom** (tiles) servido pelo Flask.
- **OpenSeadragon** para navegação e zoom no navegador.

## 1. Pré-requisitos (Windows)

1. Instalar Python 3.10+.
2. (Opcional) Criar ambiente virtual:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

## 2. Instalar dependências

```bash
pip install -r requirements.txt
```

Isso instalará automaticamente os binários do OpenSlide via `openslide-bin`.

## 3. Executar o servidor

Assumindo que você possui o arquivo `1460-09.svs` na raiz do projeto.

```bash
python viewer.py 1460-09.svs --host 0.0.0.0 --port 5000
```

Abra no navegador: http://localhost:5000

## 4. Funcionalidades

- Zoom e navegação em mosaicos (tiles DeepZoom).
- Endpoint `/info` retorna metadados (níveis, dimensões).
- Extração de ROI via formulário (gera PNG em nova janela) ou chamando diretamente:
  - `GET /roi?x=1000&y=2000&w=512&h=512&level=0`

`x`, `y` são coordenadas relativas ao nível informado. O nível 0 é o de maior resolução.

## 5. Ajustes Possíveis

- Alterar `TILE_SIZE` e `QUALITY` em `viewer.py` conforme desempenho.
- Usar `limit_bounds=True` no `DeepZoomGenerator` para evitar áreas vazias se necessário.

## 6. Deploy Estático (GitHub Pages)

Devido à grande quantidade de arquivos gerados (tiles), o deploy no Vercel pode falhar (limite de arquivos). Recomenda-se usar o **GitHub Pages**.

### Como ativar o GitHub Pages:

1. Vá para o seu repositório no GitHub.
2. Clique em **Settings** (Configurações).
3. No menu lateral esquerdo, clique em **Pages**.
4. Em **Build and deployment** > **Source**, selecione **Deploy from a branch**.
5. Em **Branch**, selecione `main` e a pasta `/static_site` (se disponível) ou `/` (root).
   - **Nota**: Como o site estático está na pasta `static_site`, você precisará configurar o GitHub Pages para servir a partir dessa pasta.
   - Se o GitHub Pages não permitir selecionar subpastas além de `/` ou `/docs`, você pode precisar mover o conteúdo de `static_site` para a raiz ou usar uma GitHub Action.

### Opção Recomendada (GitHub Action para Pages):

Se não conseguir selecionar a pasta `static_site` diretamente:

1. Vá em **Actions** no GitHub.
2. Procure por "Static HTML" e configure.
3. Certifique-se de que o passo de upload aponte para a pasta `static_site`.

## 7. Problemas Comuns

| Problema                            | Causa                                      | Solução                                    |
| ----------------------------------- | ------------------------------------------ | ------------------------------------------ |
| `openslide.OpenSlideError`          | Arquivo corrompido ou formato incompatível | Verificar extensão / testar em QuPath      |
| Erro de DLL (`Cannot load library`) | Binários não estão no PATH                 | Reabrir terminal após ajustar PATH         |
| Lentidão inicial                    | Cache de tiles ainda não populado          | Primeiro uso gera mosaicos, depois acelera |

## 8. Próximos Passos

- Adicionar anotações (desenhos) usando overlay no OpenSeadragon.
- Exportar lista de ROIs definida pelo usuário.

Bom uso! Qualquer dúvida adicional, peça ajuda.
