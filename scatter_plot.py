from sentence_transformers import SentenceTransformer
import pickle
import pymysql.cursors
import sys
import numpy as np
import torch
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder


# Создание LabelEncoder
le = LabelEncoder()

# Массив для хранения жанров
ids = []

connection = pymysql.connect(host='localhost',
                             port=9306,
                             user='root',
                             password='',
                             database='',
                             cursorclass=pymysql.cursors.DictCursor)
# slone/LaBSE-en-ru-myv-v1
# sentence-transformers/all-MiniLM-L12-v2
model2 = SentenceTransformer(
    'DeepPavlov/xlm-roberta-large-en-ru', device='cuda')

def bert_encoder(nativeitemid, txt):
    embedding = model2.encode(txt.lower())
    genre = nativeitemid.split(',')
    ids.append(genre[0])

    return embedding

batch_size = 200

# Массив для хранения эмбеддингов
embeddings = []

with connection:
    i = 0
    with connection.cursor() as cursor:
        while True:
            sql = "SELECT nativeitemid, type, title, description, genretitles, agerating, year, personnames from datamart WHERE (title<>'' or title is not null) and type<>'CHANNEL' and type<>'EPISODE' and platformids=44 LIMIT " + str(batch_size) + " OFFSET %s OPTION max_matches=3000000"
            cursor.execute(sql, (i))
            result = cursor.fetchall()
            print(len(result), i)
            if len(result) < 1:
                break
            i = i + batch_size
            
            if i > batch_size:
                break

            for r in result:
                nativeitemid = r['genretitles']
                if r['genretitles'] != '':
                    txt = r['title']
                    age_18 = False
                    if r['agerating'] == 'R18':
                        age_18 = True

                    if txt != '':
#                        e = bert_encoder(nativeitemid, txt)
#                        embeddings.append(e)
                    
#                        if ":" in txt:
#                            parts = txt.split(":", 1)
#                            e = bert_encoder(nativeitemid, parts[0].strip())
#                            embeddings.append(e)
                                                         
#                        e = bert_encoder(nativeitemid, r['description'].split(".")[0].strip())
#                        embeddings.append(e)
                        for genre in r['genretitles'].split(','):
#                            if len(words) <= 2:
#                                e = bert_encoder(nativeitemid, genre + ' про ' + ' '.join(words))

#                            if age_18:
#                                e = bert_encoder(nativeitemid, genre + ' 18+')
#                                embeddings.append(e)
                            for person in r['personnames'].split(','):
                                e = bert_encoder(nativeitemid, genre + ' c ' + person)
                                embeddings.append(e)
                               

numeric_ids = le.fit_transform(ids)
# Создание словаря, который сопоставляет числовые метки с их строковыми эквивалентами
id_dict = dict(zip(numeric_ids, ids))

embeddings_np = np.array(embeddings)
tsne = TSNE(n_components=2, random_state=0)
reduced_embeddings = tsne.fit_transform(embeddings_np)

# Создание scatter plot
plt.figure(figsize=(10, 10))
for label in np.unique(numeric_ids):
    idx = np.where(numeric_ids == label)
    plt.scatter(reduced_embeddings[idx, 0], reduced_embeddings[idx, 1], label=id_dict[label])

plt.legend()
plt.savefig('scatter_genre_person_minilm.png')

plt.show()








