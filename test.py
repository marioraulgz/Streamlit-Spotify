from os import sep
import streamlit as st
import spotipy as spoti
import pandas as pd
from urllib.error import URLError
from spotipy.oauth2 import SpotifyClientCredentials
import pickle
import sklearn
import time
import SessionState

# Definir Session State
session_state = SessionState.get(
    dic_ids={},
    dic_explicit={},
    dic_artists={},
    list_song_names=[],
    number_results=0,
    valid_search=False,
)

# Paraemtros Spotipy
CID = "1c5eb54d90c1432e9cfdd15797a78f94"
SECRET = "e55cf83e20304dc6bdc43760c2e2791c"
MODEL_FILENAME = "./tree.sav"
n_results = 6
number_results = 0

## Parametros modelo
tree_model = pickle.load(open(MODEL_FILENAME, "rb"))
columns_model = [
    "track.explicit",
    "key",
    "mode",
    "loudness",
    "danceability",
    "energy",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "track.duration_ms",
]

## Sesion Spotify API
client_credentials_manager = SpotifyClientCredentials(
    client_id=CID, client_secret=SECRET
)
sp = spoti.Spotify(client_credentials_manager=client_credentials_manager)


def search_results_fetch(query, n_results):
    search_results = sp.search(q=query, limit=n_results, type="track")
    dic_ids = {}
    dic_explicit = {}
    dic_artists = {}
    number_results = max(n_results, len(search_results["tracks"]["items"]))
    list_song_names = [0 for i in range(number_results)]
    for i in range(number_results):
        print(i)
        artist_i = search_results["tracks"]["items"][i]["artists"]
        list_song_names[i] = search_results["tracks"]["items"][i]["name"]
        dic_ids[i] = search_results["tracks"]["items"][i]["id"]
        dic_explicit[i] = search_results["tracks"]["items"][i]["explicit"]
        dic_artists[i] = [artist["name"] for artist in artist_i]
    return dic_ids, dic_explicit, dic_artists, list_song_names, number_results


def show_search_results(dic_artists, list_song_names, dic_explicit):
    for i in range(len(list_song_names)):
        st.write(f"{i+1}. {list_song_names[i]}")
        st.write(dic_artists[i], sep=",")
        if dic_explicit[i]:
            st.warning("Explicit")


def song_data_fetch(song_id, explicit):
    audio_feat_track = sp.audio_features(song_id)
    audio_feat_track[0]["track.explicit"] = explicit
    df = pd.DataFrame(audio_feat_track[0], index=[0])
    df.drop(
        ["id", "uri", "track_href", "analysis_url", "type", "time_signature"],
        axis=1,
        inplace=True,
    )
    df.rename(columns={"duration_ms": "track.duration_ms"}, inplace=True)
    final_df = df[columns_model]

    return final_df


try:
    st.title("La Fórmula de un Hit Musical")

    st.sidebar.header("Equipo 2")
    st.sidebar.write("BEDU")
    time.sleep(2.00)
    st.write(
        """
    Conectados a Spotify :white_check_mark:
    """
    )
    time.sleep(0.1)
    st.write(
        "Usa un modelo de Árbol de Decisión para predecir si una canción es popular o no"
    )
    with st.beta_expander("¿Árbol de Decisión?"):
        st.write(
            "Aprendizaje basado en árboles de decisión utiliza un árbol de decisión como un modelo predictivo que mapea observaciones sobre un artículo a conclusiones sobre el valor objetivo del artículo. Es uno de los enfoques de modelado predictivo utilizadas en estadísticas, minería de datos y aprendizaje automático. Los modelos de árbol, donde la variable de destino puede tomar un conjunto finito de valores se denominan árboles de clasificación. En estas estructuras de árbol, las hojas representan etiquetas de clase y las ramas representan las conjunciones de características que conducen a esas etiquetas de clase. Los árboles de decisión, donde la variable de destino puede tomar valores continuos (por lo general números reales) se llaman árboles de regresión. Los árboles de decisión se encuentran entre los algoritmos populares debido a su simplicidad.En análisis de decisión, un árbol de decisión se puede utilizar para representar visualmente y de forma explícita decisiones y toma de decisiones. En minería de datos, un árbol de decisión describe datos, pero no las decisiones; más bien el árbol de clasificación resultante puede ser un usado como entrada para la toma de decisiones."
        )

    ## Buscador de canciones
    st.subheader("Escribe una canción")
    with st.form(key="search_form"):
        query = st.text_input(label="Busqueda Cancion")
        submit_button_query = st.form_submit_button(label="Buscar")

    if submit_button_query:
        (
            dic_ids_var,
            dic_explicit_var,
            dic_artists_var,
            list_song_names_var,
            number_results_var,
        ) = search_results_fetch(query, n_results)
        show_search_results(dic_artists_var, list_song_names_var, dic_explicit_var)

        session_state.dic_ids = dic_ids_var
        session_state.dic_explicit = dic_explicit_var
        session_state.dic_artists = dic_artists_var
        session_state.list_song_names = list_song_names_var
        session_state.number_results = number_results_var
        session_state.valid_search = True
        # Opciones del 1 al 6
    if session_state.valid_search:
        st.subheader("Selecciona cual canción buscabas")
        with st.form(key="model_form"):
            param_modelo = st.radio(
                label="Numero de la cancion", options=range(1, n_results + 1)
            )
            submit_button_modelo = st.form_submit_button(label="Calcular")

        if submit_button_modelo:
            final_df = song_data_fetch(
                session_state.dic_ids[param_modelo - 1],
                session_state.dic_explicit[param_modelo - 1],
            )
            prediction = tree_model.predict(final_df)

            st.write("Empezando predicción")
            time.sleep(1)
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i in range(100):
                # Actualizamos la barra de progreso
                progress_bar.progress(i + 1)

                # Pretendamos que estamos gastando tiempo
                time.sleep(0.02)
            status_text.success("¡Listo!")
            st.header("Resultados de la **Inteligencia Artificial**")
            st.write(f"Para la canción {int(param_modelo)}")

            if prediction:
                st.balloons()
                st.write("La canción será exitosa!")
            else:
                st.write(":pensive: No te preocupes, las preferencias siempre cambian!")

            submit_button_reiniciar = st.button("Limpiar")
            if submit_button_reiniciar:
                session_state.valid_search = False
    # Agarrar ID De esa opcion

    # Mostrar abajo que se esta calculando
    # Llamar a modelo y calcular
    # EN grande resultado arriba, seguido de graficas comparando resultado con los valores deseados
    # Boton de borrar

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
