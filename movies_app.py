import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

#configurar credenciales y conectar notebook a firestore
import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="reto-final-movies")
dbMovies = db.collection("names")

#-----------------------------
#Pagina principal
#-----------------------------

#trear datos del csv
@st.cache_data
def load_data():
    data_ref = list(db.collection(u'movies').stream())
    data_dict = list(map(lambda x: x.to_dict(), data_ref))
    data = pd.DataFrame(data_dict)
    return data
  
data_load_state = st.text('Loading movie data...')
data = load_data()
st.title('Netflix app')
data_load_state.text("Done! (using st.cache)")

#-----------------------------
#Sidebar
#-----------------------------

#mostrar filmes cuando se de en el checkbox
if st.sidebar.checkbox("Mostrar todos los filmes"):
    st.subheader('Todos los filmes')
    st.dataframe(data)


#Buscar por nombre de pelicula
nameSearch = st.sidebar.text_input("Titulo de filme: ")
btnFiltrar = st.sidebar.button("Buscar filmes")

if btnFiltrar and nameSearch:
    #pasar a minusculas
    search_query = nameSearch.lower()

    #buscar por el nombre
    results = []
    docs = db.collection(u'movies').stream()
    for doc in docs:
        movie_data = doc.to_dict()
        if 'name' in movie_data and search_query in movie_data['name'].lower():
            results.append(movie_data)

    if results:
        # Mostrar la cantidad de filmes y mostrar el DataFrame
        st.write(f"Total filmes mostrados: {len(results)}")
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning(f"No se encontraron filmes con el nombre '{nameSearch}'.")

#Buscar por director de pelicula
#dropbox de los directores
director_list = data['director'].dropna().unique()
selected_director = st.sidebar.selectbox("Seleccionar director", director_list)
btn_director_search = st.sidebar.button("Filtrar director")

if btn_director_search and selected_director:    
    # Buscar por el director
    director_movies = data[data['director'] == selected_director]
    
    # Mostrar el total de filmes encontrados segun el director
    st.write(f"Total filmes: {len(director_movies)}")
    
    st.dataframe(director_movies)

#Formulario para un nuevo registro
st.sidebar.header("Nuevo Filme")
new_movie_name = st.sidebar.text_input("Name: ")

company_list = data['company'].dropna().unique()
new_movie_company = st.sidebar.selectbox("Company", company_list)

director_list = data['director'].dropna().unique()
new_movie_director = st.sidebar.selectbox("Director", director_list)

genre_list = data['genre'].dropna().unique()
new_movie_genre = st.sidebar.selectbox("Genre", genre_list)

btnRegistro = st.sidebar.button("Crear nuevo filme")

if btnRegistro:
     # Crea un diccionario con los datos del nuevo filme
     new_movie_data = {
         "name": new_movie_name,
         "company": new_movie_company,
         "director": new_movie_director,
         "genre": new_movie_genre
     }

     try:
         movies_ref = db.collection(u'movies')
         movies_ref.add(new_movie_data)
         st.sidebar.write("Registro insertado correctamente")
         
     except Exception as e:
         st.sidebar.error(f"Ocurrió un error al agregar el filme: {e}")
