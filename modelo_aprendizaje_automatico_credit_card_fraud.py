# -*- coding: utf-8 -*-
"""Modelo_Aprendizaje_Automático_Credit_Card_Fraud.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11RcNYdm1pSUdb-aXbaLsww4iCHK3h0Ya

#Modelo de Aprendizaje Automático - Credit Card Fraud Project

##Descripción del modelo
Para la solución de este reto, se optó por implementar un modelo

##Tarea: **Clasificación**
Tarea de aprendizaje supervisado que con base en determinadas características, determina la clase a la que pertenece el objeto. Es decir, aunque el objeto tal cual no esté en las clases, lo clasifica en la clase con la cual comparta mayor número de características. Este tipo de algoritmos lo que hacen es aprender del "label" asignado a los datos de entrenamiento para, mediante la asociación de patrones, poder etiquetar los nuevos datos.

Se optó por esta tarea porque es fácil identificar el alcance de nuestro modelo,y el cómo desempeñará su tarea. Para nuestro caso tenemos solo dos posibilidades, la transacción es o no fraude, por lo que es un tipo de clasificación binaria. Es fácil evaluar la efectividad del mismo, así como identificar cuando el modelo ya está listo y podemos detener el entrenamiento del mismo.

##Técnica: **Árboles de decisión** 
Técnica de aprendizaje automático que crea el modelo con base en reglas, y estas reglas pueden ser fácilmente entendidas por el usuario. Lo podemos entender como un conjunto de condicionales las cuales con base en las características,  colocadas en el nodo de decisión, determina la clase a la que pertenence el objeto, ubicada en el nodo terminal.

Se optó por esta ténica porque este modelo puede manejar tanto características numéricas como nominales, y en nuestra base de datos tenemos ambas. Debido a la representación visual de estos, es fácil observar las relaciones de causa y efecto y a su vez la comprensión del funcionamiento es más sencilla para nosotros como usuario. Los datos utilizados para la creación de este tipo de modelo no necesitan de mucha preparación, lo cual también facilita su implementación. Y la razón más fuerte por la que decidimos usar este modelo es porque toma las mejor decisión de clasificación con base en información ya existente y de las mejores suposiciones.

##Modelo
"""

# Librerias
import pandas as pd
from sklearn.tree import DecisionTreeClassifier # librería para árboles de decisión
from sklearn.ensemble import RandomForestClassifier # librería para bosques aleatorios
from sklearn import tree # librería para poder visualizar el árbol
from sklearn.model_selection import GridSearchCV # librería para mejorar nuestros modelos
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import auc

"""Vamos a obtener nuestros datasets dentro de nuestro Drive"""

# Montamos los archivos de nuestro Drive para que puedan usarse en Colab
from google.colab import drive
drive.mount('/content/drive/')

# Establecemos el directorio de la base de datos
BASE_DIR = '/content/drive/My Drive/BasesDeDatos/proyecto/'

"""Obtenemos los datasets"""

#Cargamos la base de datos que se utilizará para entrenar el modelo
data_train = pd.read_csv(BASE_DIR + 'fraudTrainV2.csv')
#Visualización de la base de datos
data_train.head()

#Cargamos la base de datos que se utilizará para probar el modelo
data_test = pd.read_csv(BASE_DIR + 'fraudTest.csv', index_col=0)
#Visualización de la base de datos
data_test.head()

"""Limpiamos nuestros datasets para que sean de tipo numéricos"""

# Preparación de data de entrenamiento
# Reemplazamos datos tipo string a datos tipo int
data_train['gender'] = data_train['gender'].replace(['M', 'F'], [0, 1])
data_train['category'] = data_train['category'].replace(
    ['entertainment', 'food_dining', 'misc_net', 'grocery_pos', 'gas_transport', 
     'misc_pos', 'grocery_net', 'shopping_net', 'shopping_pos', 'personal_care', 
     'health_fitness', 'travel', 'kids_pets', 'home'], 
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
# Hacemos split para obtener la parte de mayor peso de la variable 'dob'
f = lambda x: x['dob'].split("/")[2]
data_train['dob'] = data_train.apply(f, axis=1)
# Dividimos la variable 'trans_date_trans_time' para obtener la hora (variable de interés)
data_train[['date', 'time']] = data_train.trans_date_trans_time.str.split(" ", expand=True,)
data_train = data_train.drop(['trans_date_trans_time', 'cc_num', 'merchant', 
                              'first', 'last', 'city', 'state', 'zip', 'street', 
                              'city_pop', 'job', 'trans_num', 'merch_lat', 
                              'merch_long', 'date'], axis = 1)
f = lambda x: x['time'].split(":")[0]
data_train['time'] = data_train.apply(f, axis=1)
# Acomodamos columna 'is_fraud' al final
data_train = data_train[[c for c in data_train if c not in ['is_fraud']] + ['is_fraud']]
# Imprimimos head()
data_train.head()

"""Obtenemos los mejores parámetros para el árbol de decisión con GridSearchCV"""

# Data de entrenamiento
x_train = data_train.drop('is_fraud', axis = 1)
y_train = data_train['is_fraud']
# Parámetros
params = {'criterion' : ['gini', 'entropy'],
          'splitter' : ['best', 'random']}
#Configuración de la rejilla
grid_search_cv = GridSearchCV(DecisionTreeClassifier(random_state = 42), params, verbose = 1, cv = 2, n_jobs = 8, scoring = 'accuracy')
#se hacen todas las combinaciones posibles y se queda con el que tiene el mejor resultado en el "accuracy"
#Generación de los modelos 
grid_search_cv.fit(x_train, y_train)
#Visualizamos la mejor configuración para el modelo
print(grid_search_cv.best_estimator_)

#Visualización de la configuración elegida como la mejor
dt_mejorado = grid_search_cv.best_estimator_
dt_mejorado.get_params()

"""Limpiamos dataset de testeo para evaluar modelo entrenado"""

# Preparación de datos test
data_test['gender'] = data_test['gender'].replace(['M', 'F'], [0, 1])
data_test['category'] = data_test['category'].replace(['entertainment', 'food_dining', 'misc_net', 'grocery_pos', 'gas_transport', 'misc_pos', 'grocery_net', 'shopping_net', 'shopping_pos', 'personal_care', 'health_fitness', 'travel', 'kids_pets', 'home'], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
f = lambda x: x['dob'].split("-")[0]
data_test['dob'] = data_test.apply(f, axis=1)
data_test[['date', 'time']] = data_test.trans_date_trans_time.str.split(" ", expand=True,)
data_test = data_test.drop(['trans_date_trans_time', 'cc_num', 'merchant', 'first', 'last', 'city', 'state', 'zip', 'street', 'city_pop', 'job', 'trans_num', 'merch_lat', 'merch_long', 'date'], axis = 1)
f = lambda x: x['time'].split(":")[0]
data_test['time'] = data_test.apply(f, axis=1)
data_test = data_test[[c for c in data_test if c not in ['is_fraud']] + ['is_fraud']]
data_train.head()

"""Hacemos un test del mejor modelo"""

# Data test
x_test = data_test.drop('is_fraud', axis = 1)
y_test = data_test['is_fraud']
# Prueba del modelo mejorado con lo obtenido en el paso anterior
dt_mejorado.score(x_test, y_test)

predictions = dt_mejorado.predict(x_test)
# print("Score : \n", accuracy_score(y_test, predictions))

print("Confusion Matrix : \n", confusion_matrix(y_test, predictions))
fpr, tpr, thresholds = roc_curve(y_test, predictions)
print("AUC : \n", auc(fpr, tpr))

"""Representación gráfica de nuestro árbol de decisión"""

tree.plot_tree(dt_mejorado)

# Parámetros
params = {'criterion' : ['gini', 'entropy']}
#Configuración de la rejilla
grid_search_cv = GridSearchCV(RandomForestClassifier(random_state = 42), params, verbose = 1, cv = 2, n_jobs = 8, scoring = 'accuracy')
#se hacen todas las combinaciones posibles y se queda con el que tiene el mejor resultado en el "accuracy"
#Generación de los modelos 
grid_search_cv.fit(x_train, y_train)
#Visualizamos la mejor configuración para el modelo
print(grid_search_cv.best_estimator_)

#Visualización de la configuración elegida como la mejor
dt_mejorado = grid_search_cv.best_estimator_
dt_mejorado.get_params()

# Data test
x_test = data_test.drop('is_fraud', axis = 1)
y_test = data_test['is_fraud']
# Prueba del modelo mejorado con lo obtenido en el paso anterior
dt_mejorado.score(x_test, y_test)

predictions = dt_mejorado.predict(x_test)
# print("Score : \n", accuracy_score(y_test, predictions))

print("Confusion Matrix : \n", confusion_matrix(y_test, predictions))
fpr, tpr, thresholds = roc_curve(y_test, predictions)
print("AUC : \n", auc(fpr, tpr))