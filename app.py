Okay, vamos analisar o código da sua chave da API para identificar e corrigir possíveis problemas.

### Possíveis Problemas com a Chave da API e Soluções

Com base no código que você forneceu, aqui estão os principais pontos a serem verificados e como corrigi-los:

1.  **A chave da API está sendo carregada corretamente?**

      * **Problema:** O código tenta obter a chave da API de duas maneiras: diretamente na linha `api_key = "AIzaSyDag-9hsFQHH1cmnY9tasKMPPXP6SA9pWM"` e também usando `os.environ.get('YOUTUBE_API_KEY')`. Se a variável de ambiente `YOUTUBE_API_KEY` não estiver definida, o código usará a chave diretamente no código.
      * **Solução:**
          * **Opção 1 (Recomendada):** Defina a variável de ambiente `YOUTUBE_API_KEY` no seu sistema operacional ou no Streamlit Secrets (se estiver usando o Streamlit). Isso é mais seguro do que colocar a chave diretamente no código.
          * **Opção 2 (Menos Segura):** Certifique-se de que a chave `"AIzaSyDag-9hsFQHH1cmnY9tasKMPPXP6SA9pWM"` é a chave correta e válida para o seu projeto do YouTube Data API v3.
      * **Como verificar:**
          * Se você estiver usando a variável de ambiente, verifique se ela está definida corretamente. No Streamlit, você pode verificar isso nas configurações do aplicativo.
          * Se você estiver usando a chave diretamente no código, compare-a com a chave listada no Google Cloud Console.

2.  **A chave da API está sendo usada corretamente na construção do serviço YouTube?**

      * **Problema:** O código constrói o serviço YouTube duas vezes, potencialmente com configurações diferentes.

      * **Solução:** Remova a linha redundante de construção do serviço. O código deve ter apenas uma linha como esta:

        ```python
        youtube = build('youtube', 'v3', developerKey=api_key, http=http, cache_discovery=False)
        ```

      * **Como verificar:** Certifique-se de que você não está sobrescrevendo a variável `youtube` desnecessariamente.

3.  **A API do YouTube Data V3 está habilitada?**

      * **Problema:** Mesmo com uma chave válida, a API pode não estar habilitada para o seu projeto.
      * **Solução:**
          * Vá para o [Google Cloud Console](https://console.cloud.google.com/).
          * Selecione o seu projeto.
          * No menu, vá para "APIs e Serviços" -\> "Painel".
          * Procure por "YouTube Data API v3" e clique nela.
          * Certifique-se de que a API está habilitada. Se não estiver, clique em "Habilitar".

4.  **Restrições na chave da API:**

      * **Problema:** A chave da API pode ter restrições (por exemplo, restrições de referenciador de site ou endereço IP) que impedem o acesso do seu aplicativo.
      * **Solução:**
          * No [Google Cloud Console](https://console.cloud.google.com/), vá para "APIs e Serviços" -\> "Credenciais".
          * Clique na chave da API que você está usando.
          * Verifique a seção "Restrições de chave". Se houver alguma restrição, certifique-se de que ela permite o acesso do seu aplicativo Streamlit. Se você não tiver certeza, tente remover as restrições temporariamente para testar.

5.  **Cota de uso:**

      * **Problema:** Você pode ter excedido a cota diária ou por segundo para a API do YouTube.
      * **Solução:**
          * No Google Cloud Console, vá para "APIs e Serviços" -\> "Painel".
          * Procure pela API do YouTube Data API v3 e clique nela.
          * Vá para a aba "Cotas".
          * Verifique se você excedeu algum limite. Se sim, você pode precisar esperar até que a cota seja reiniciada ou solicitar um aumento de cota.

### Código Revisado

Aqui está uma versão revisada do seu código, incorporando algumas dessas correções:

```python
import os
from googleapiclient.discovery import build
import httplib2
import pandas

# Como fazer a conexão

# Opção 1 (Recomendada): Obter a chave da API da variável de ambiente
api_key = os.environ.get('YOUTUBE_API_KEY')

# Opção 2 (Menos Segura): Usar a chave diretamente no código (NÃO RECOMENDADO)
# api_key = "SUA_CHAVE_AQUI"

if not api_key:
    raise ValueError("A variável de ambiente YOUTUBE_API_KEY não está definida.")

# Construa o serviço do YouTube (apenas uma vez)
http = httplib2.Http()  # Crie um objeto http
youtube = build('youtube', 'v3', developerKey=api_key, http=http, cache_discovery=False)


def get_video_stats(youtube, video_ids):
    chamada = youtube.videos().list(
        part="snippet,statistics",
        id=','.join(video_ids)
    )
    response = chamada.execute()
    result = []
    for item in response.get("items", []):
        video = {
            "id": item["id"],
            "title": item["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "publishTime": item['snippet']['publishedAt'],
            "view_count": item["statistics"].get("viewCount"),
            "like_count": item["statistics"].get("likeCount"),
            "comment_count": item["statistics"].get("commentCount"),
            "tags": item['snippet'].get("tags"),
            "source": item
        }
        result.append(video)
    return result


SEARCH_TERM = 'python'

# Processe os resultados
video_ids = []
next_page_token = None
counter = 0
print(f"Vídeos encontrados para '{SEARCH_TERM}':")
while counter < 100:
    # https://developers.google.com/youtube/v3/docs/search/list?hl=pt-br
    request = youtube.search().list(
        part='snippet',
        q=SEARCH_TERM,
        type='video',
        order='viewCount',
        publishedAfter='2025-04-01T00:00:00Z',
        relevanceLanguage='pt',
        maxResults=50,
        pageToken=next_page_token
    )
    response = request.execute()
    for item in response['items']:
        video_ids.append(item['id']['videoId'])
        counter += 1
    next_page_token = response.get('nextPageToken')
    if next_page_token:
        print('Buscando nova página')
    else:
        break

print(f"\n{counter} vídeos foram obtidos.")

# A rotina não consegue obter mais do que 50 ids
videos = get_video_stats(youtube, video_ids[0:10])

import json

arquivo = open('yotube.json', 'w')
json.dump(videos, arquivo, indent=4)
arquivo.close()

# Rotina 2: Obter os vídeos de um determinado canal
#
# Para obter os vídeos de um determinado canal, é necessário ter o channelID
# que é um parâmetro que NÃO aparece na URL do canal.
#
# Para obter obter o channelID, é necessário buscar primeiro os dados de um dos canais do vídeo
# No retorno das estatísticas, um dos atributos é o channelID
#
video_id = 'DqJnmaLWnqQ'
request = youtube.videos().list(
    part="snippet,statistics",
    id=video_id
)
response = request.execute()
items = response.get("items", [])
if len(items) == 0:
    print('Video não encontrado')
else:
    channel_id = items[0]['snippet']['channelId']

print(channel_id)


# Traz as estatísticas de um determinado canal
def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()


# Obtem os vídeos mais acessados de um determinado canal
# channel_id = 'UCitie-To0pWGe5Qyk9SjWRA'
channel_id = 'UCmGSJVG3mCRXVOP4yZrU1Dw'
max_results = 100

request = youtube.search().list(
    part="id,snippet",
    channelId=channel_id,
    order="viewCount",
    type="video",
    maxResults=max_results
)

response = request.execute()

videos = {}
video_ids = []
for search_result in response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
        video_id = search_result["id"]["videoId"]
        videos[video_id] = {
            "title": search_result["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "publishTime": search_result['snippet']['publishedAt'],
        }
        video_ids.append(video_id)

# Aqui está o pulo do gato para minimizar o número de requests!
request = youtube.videos().list(
    part="snippet,statistics",
    id=','.join(video_ids)
)
response = request.execute()
for item in response.get("items", []):
    videos[item["id"]]['view_count'] = item["statistics"].get("viewCount")
    videos[item["id"]]['like_count'] = item["statistics"].get("likeCount")
    videos[item["id"]]['comment_count'] = item["statistics"].get("commentCount")
    videos[item["id"]]['tags'] = item['snippet'].get("tags")

# Grava os vídeos mais acessados em um arquivo CSV
import csv

arquivo = open('segundo.csv', 'w')
csv_file = csv.DictWriter(arquivo, fieldnames=['title', 'url', 'publishTime', 'view_count', 'like_count', 'comment_count', 'tags'])
csv_file.writeheader()
for video in videos:
    csv_file.writerow(videos[video])
arquivo.close()

from googleapiclient.discovery import build

# Função para buscar canais relacionados a podcasts
def search_tutorial_channels(query, max_results, region_code='BR'):
    request = youtube.search().list(
        q=query,
        type='channel',
        part='snippet',
        maxResults=max_results,
        regionCode=region_code
    )
    response = request.execute()

    channels = []
    for item in response['items']:
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['title']
        channels.append({'channel_id': channel_id, 'channel_title': channel_title})

    return channels


# Função para buscar canais relacionados a podcasts
def search_podcast_channels(query, max_results):
    request = youtube.search().list(
        q=query,
        type='channel',
        part='snippet',
        maxResults=max_results
    )
    response = request.execute()

    channels = []
    for item in response['items']:
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['title']
        channels.append({'channel_id': channel_id, 'channel_title': channel_title})

    return channels


# Buscando canais de podcast
podcast_channels = search_tutorial_channels('conversas', 20)
print(podcast_channels)

# prompt: quais os outros metodos da classe youtube?

print(dir(youtube))

# Buscando canais de podcast brasileiros

def search_tutorial_channels(query, max_results, region_code='BR'):
    request = youtube.search().list(
        q=query,
        type='channel',
        part='snippet',
        maxResults=max_results,
        regionCode=region_code  # Adicionando o código de região para o Brasil
    )
    response = request.execute()

    channels = []
    for item in response['items']:
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['title']
        channels.append({'channel_id': channel_id, 'channel_title': channel_title})

    return channels


# Buscando canais de podcast brasileiros
tutorial_channels_brazil = search_tutorial_channels('tecnologia', 20)
print(tutorial_channels_brazil)

# Obter os dados de acesso de cada canal

# Classificar os canais por número de inscritos
# A lista tutorial_channels_brazil não contém informações de inscritos, então esta parte será removida
# sorted_channels = sorted(tutorial_channels_brazil, key=lambda x: x['subscribers'], reverse=True)

# Selecionar os 10 melhores canais
# top_10_channels = sorted_channels[:10]

# Apenas processar a lista de canais obtida
channels_to_process = tutorial_channels_brazil

print(channels_to_process)

# Salvar os detalhes dos canais em um arquivo CSV
import pandas as pd

# Supondo que 'channels_to_process' seja a lista de dicionários com os detalhes dos canais
df = pd.DataFrame(channels_to_process)
df.to_csv('tutorial_tecnologia.csv', index=False)

# Função para buscar canais relacionados a podcasts
query = "python"

request = youtube.videos().list(
    part='snippet',
    chart='mostPopular',
    maxResults=10,
    # Quantidade de vídeos que você deseja recuperar
)

response = request.execute()

for item in response['items']:
    print(item['snippet']['title'])

# Função para buscar as categorias do Youtube
query = "tutorial"

request = youtube.videoCategories().list(
    part='snippet',
    regionCode='br'
)

response = request.execute()

for item in response['items']:
    print(item['id'], item['snippet']['title'])

from googleapiclient.discovery import build
# from google.colab import userdata
import os
import httplib2  # Import httplib2

# api_key = userdata.get('YOUTUBE_API_KEY')
api_key = os.environ.get('YOUTUBE_API_KEY')

if not api_key:
    print("Error: YOUTUBE_API_KEY environment variable not set.")
    # You might want to exit or raise an exception here in a real application
    # exit()

http = httplib2.Http()  # Crie um objeto http
youtube = build('youtube', 'v3', developerKey=api_key, http=http, cache_discovery=False)  # Passe o objeto http

SEARCH_TERM = 'python'

# Processe os resultados
video_ids = []
next_page_token = None
counter = 0
print(f"Vídeos encontrados para '{SEARCH_TERM}':")
while counter < 100:
    # https://developers.google.com/youtube/v3/docs/search/list?hl=pt-br
    request = youtube.search().list(
        part='snippet',
        q=SEARCH_TERM,
        type='video',
        order='viewCount',
        publishedAfter='2025-04-01T00:00:00Z',
        relevanceLanguage='pt',
        maxResults=50,
        pageToken=next_page_token
    )
    response = request.execute()
    for item in response['items']:
        video_ids.append(item['id']['videoId'])
        counter += 1
    next_page_token = response.get('nextPageToken')
    if next_page_token:
        print('Buscando nova página')
    else:
        break

print(f"\n{counter} vídeos foram obtidos.")

# Obter os dados de acesso de cada canal

# Classificar os canais por número de inscritos
# A lista tutorial_channels_brazil não contém informações de inscritos, então esta parte será removida
# sorted_channels = sorted(tutorial_channels_brazil, key=lambda x: x['subscribers'], reverse=True)

# Selecionar os 10 melhores canais
# top_10_channels = sorted_channels[:10]

# Apenas processar a lista de canais obtida
channels_to_process = tutorial_channels_brazil

print(channels_to_process)

"""# Task
Buscar, obter detalhes e salvar em CSV canais de tutorial de Python do YouTube.

## Buscar canais de tutorial sobre python

### Subtask:
Utilizar a API do YouTube para buscar canais relacionados a tutoriais de Python.

**Reasoning**:
Use the youtube object to search for channels related to 'tutorial python' and store the response.
"""

request = youtube.search().list(
    q='tutorial python',
    type='channel',
    part='snippet',
    maxResults=20
)
response = request.execute()

"""## Obter detalhes dos canais de python

### Subtask:
Para cada canal encontrado, obter informações adicionais como número de inscritos, visualizações totais, etc.

**Reasoning**:
Iterate through the search results to get channel IDs and then fetch detailed channel statistics for each channel.
"""

channel_ids = []
for item in response.get('items', []):
    channel_ids.append(item['snippet']['channelId'])

channel_details = []
for channel_id in channel_ids:
    request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    )
    channel_response = request.execute()
    if channel_response.get('items'):
        item = channel_response['items'][0]
        details = {
            'channel_id': item['id'],
            'channel_title': item['snippet']['title'],
            'subscriber_count': item['statistics'].get('subscriberCount'),
            'view_count': item['statistics'].get('viewCount'),
            'video_count': item['statistics'].get('videoCount')
        }
        channel_details.append(details)

print(channel_details)

"""## Salvar os detalhes dos canais de python

### Subtask:
Salvar os detalhes dos canais de Python em um arquivo CSV.

**Reasoning**:
Create a pandas DataFrame from the list of channel details and save it to a CSV file.
"""

import pandas as pd

df = pd.DataFrame(channel_details)
df.to_csv('python_tutorial_channels.csv', index=False)

"""## Explorar os dados dos canais de python

### Subtask:
Carregar o arquivo CSV e exibir os dados dos canais de Python para análise.

**Reasoning**:
Read the CSV file into a pandas DataFrame and display the first few rows and data types.
"""

df = pd.read_csv('python_tutorial_channels.csv')
display(df.head())
display(df.info())

"""## Summary:

### Data Analysis Key Findings

* The analysis successfully identified 20 YouTube channels related to Python tutorials.
* Detailed information for each channel was retrieved, including `channel_id`, `channel_title`, `subscriber_count`, `view_count`, and `video_count`.
* The collected channel details were successfully saved to a CSV file named `python_tutorial_channels.csv`.
* The loaded data from the CSV file confirmed the presence of 20 entries with the expected columns and data types.

### Insights or Next Steps

* Analyze the `subscriber_count`, `view_count`, and `video_count` to identify the most popular or prolific Python tutorial channels among the results.
* Consider expanding the search to include more results (increase `maxResults`) or refine the search query for broader or more specific channel discovery.

"""

# Removed Streamlit code as requested.
# The following cells contain the original code for fetching and saving YouTube channel data.

"""Para usar este código:

1.  Salve-o como um arquivo Python (por exemplo, `youtube_app.py`).
2.  Certifique-se de ter as bibliotecas `streamlit` e `google-api-python-client` instaladas no seu ambiente (`pip install streamlit google-api-python-client`).
3.  Crie um arquivo `.streamlit/secrets.toml` na mesma pasta do seu script ou use a interface de secrets do Streamlit Cloud para adicionar sua chave da API do YouTube:
"""

# Removed Streamlit installation as requested.

# Removed Streamlit code as requested.
# The following cells contain the original code for fetching and saving YouTube channel data.

"""# Removed Streamlit instructions as requested."""
```

Certifique-se de seguir estas etapas e verificar cada ponto cuidadosamente. Se o problema persistir, forneça mais detalhes sobre como você está executando o código (por exemplo, se é localmente, no Streamlit Cloud, etc.) e o erro completo que você está vendo.
