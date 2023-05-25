from sentence_transformers import SentenceTransformer
import pickle
import pymysql.cursors
import sys
import faiss
import numpy as np
import torch


# Создаем FAISS индекс
dimension = 768
index = faiss.IndexFlatL2(dimension)

# Массив для хранения идентификаторов
ids = []

connection = pymysql.connect(host='localhost',
                             port=9306,
                             user='root',
                             password='',
                             database='',
                             cursorclass=pymysql.cursors.DictCursor)

model2 = SentenceTransformer(
    'sentence-transformers/LaBSE', device='cuda')

def bert_encoder(nativeitemid, txt):
    embedding = model2.encode(txt.lower())
    ids.append(nativeitemid)

    return embedding

batch_size = 100
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
            
            if i > 21400:
                break
            # Массив для хранения эмбеддингов
            embeddings = []

            for r in result:
                nativeitemid = r['nativeitemid']
                if r['genretitles'] != '':
                    txt = r['title']
                    age_18 = False
                    if r['agerating'] == 'R18':
                        age_18 = True

                    if txt != '':
                        e = bert_encoder(nativeitemid, txt)
                        embeddings.append(e)
                        
                        if ":" in txt:
                            parts = txt.split(":", 1)
                            e = bert_encoder(nativeitemid, parts[0].strip())
                            embeddings.append(e)
                                                         
                        e = bert_encoder(nativeitemid, r['description'].split(".")[0].strip())
                        embeddings.append(e)
                        for genre in r['genretitles'].split(','):
#                            if len(words) <= 2:
#                                e = bert_encoder(nativeitemid, genre + ' про ' + ' '.join(words))

                            if age_18:
                                e = bert_encoder(nativeitemid, genre + ' 18+')
                                embeddings.append(e)
                            for person in r['personnames'].split(','):
                                e = bert_encoder(nativeitemid, genre + ' c ' + person)
                                embeddings.append(e)
                                

            embeddings_np = np.array(embeddings)
            # Добавляем эмбеддинги в FAISS индекс
            index.add(embeddings_np)

with open('ids.pkl', 'wb') as f:
    pickle.dump(ids, f)

# сохранить индекс
faiss.write_index(index, "films_labse_simicolon.faiss")
