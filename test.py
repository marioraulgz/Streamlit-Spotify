import streamlit as st
import spotipy as spoti
import pandas as pd
from urllib.error import URLError
from spotipy.oauth2 import SpotifyClientCredentials
import pickle
import sklearn
import time

# Paraemtros Spotipy
CID = "1c5eb54d90c1432e9cfdd15797a78f94"
SECRET = "e55cf83e20304dc6bdc43760c2e2791c"
MODEL_FILENAME = ""
n_results = 6

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
    search_results = sp.search(q="", limit=n_results, type="track")
    dic_ids = {}
    dic_explicit = {}
    dic_artists = {}
    list_song_names = []
    for i in range(0, n_results):
        artist_i = search_results["tracks"]["items"][i]["artists"]
        list_song_names[i] = search_results["tracks"]["items"][0]["name"]
        dic_ids[i] = search_results["tracks"]["items"][0]["id"]
        dic_explicit[i] = search_results["tracks"]["items"][0]["explicit"]
        dic_artists[i] = [artist["name"] for artist in artist_i]
    return dic_ids, dic_explicit, dic_artists, list_song_names


def show_search_results(dic_artists, list_song_names, dic_explicit):
    for i in range(len(list_song_names)):
        st.write(f"{i+1}. {list_song_names[i]}")
        st.write(dic_artists[i])


def song_data_fetch(song_id, explicit):
    audio_feat_track = sp.audio_features(song_id)
    audio_feat_track[0]["track.explicit"] = explicit
    df = pd.DataFrame(audio_feat_track[0], index=[0])
    df.drop(
        ["id", "uri", "track_href", "analysis_url", "type", "time_signature"],
        axis=1,
        inplace=True,
    )
    final_df = df[columns_model]

    return final_df


## Cargar modelo

try:
    st.title("Spotify Streamlit")
    st.write(
        """
    Conectados a Spotify
    """
    )

    ## Caja de texto en el lateral
    st.subheader("Escribe una canción")
    ## Boton
    with st.form(key="search_form"):
        query = st.text_input(label="Busqueda_Cancion")
        submit_button_query = st.form_submit_button(label="Submit_query")

    if submit_button_query:
        dic_ids, dic_explicit, dic_artists, list_song_names = search_results_fetch(
            query, n_results
        )
        show_search_results(dic_artists, list_song_names, dic_explicit)

    st.subheader("Selecciona cual canción buscabas")

    # Opciones del 1 al 6
    with st.form(key="model_form"):
        param_modelo = st.radio(
            label="Opciones_cancion", options=range(1, n_results + 1)
        )
        submit_button_modelo = st.form_submit_button(label="Submit_cancion")

    if submit_button_query:
        final_df = song_data_fetch(
            dic_ids[int(param_modelo + 1)], dic_explicit[int(param_modelo + 1)],
        )
        prediction = tree_model.predict(final_df)

        progress_bar = st.progress(0)
        status_text = st.empty()
        for i in range(100):
            # Actualizamos la barra de progreso
            progress_bar.progress(i + 1)

            # Pretendamos que estamos gastando tiempo
            time.sleep(0.09)
        status_text.text("¡Listo!")
        st.header("Resultados de la **Inteligencia Artificial**")
        st.write(f"Para la canción {int(param_modelo)+1}")

        if prediction:
            st.balloons()
        else:

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
