import streamlit as st
import spotipy as spoti
import pandas as pd
from urllib.error import URLError
from spotipy.oauth2 import SpotifyClientCredentials


cid = '1c5eb54d90c1432e9cfdd15797a78f94'
secret = 'e55cf83e20304dc6bdc43760c2e2791c'

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spoti.Spotify(client_credentials_manager = client_credentials_manager)
columns_model = ['track.explicit','key','mode','loudness','danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence','tempo','track.duration_ms']

## Cargar modelo

try:
    st.write("""
    Conectados a Spotify
    """)

    ## Caja de texto en el lateral
    st.write("""
    Escribe una canción
    """)
    ## Boton

    search_results = sp.search(q='', limit=6,type='')
    dic_ids = {}
    dic_explicit = {}
    for i in range(0, 7):
        artist_i = search_results['tracks']['items'][i]['artists']
        song_i = search_results['tracks']['items'][0]['name']
        dic_ids[i] = search_results['tracks']['items'][0]['id']
        dic_explicit[i] = search_results['tracks']['items'][0]['explicit']
        st.write(f"{i+1.}")
        for j in artist_i:
            artist_i[j]['name']
        st.write(f"{song_i}")
    st.write("Selecciona cual canción buscabas")

    #Opciones del 1 al 6
    seleccion = 1
    #Agarrar ID De esa opcion
    audio_feat_track = sp.audio_features(dic_ids[seleccion])
    audio_feat_track[0]['track.explicit']=dic_explicit[seleccion]
    df = pd.DataFrame(audio_feat_track[0], index=[ 0])
    df.drop(['id', 'uri', 'track_href', 'analysis_url', 'type', 'time_signature'], axis=1, inplace=True)
    final_df = df[columns_model]
    #Mostrar abajo que se esta calculando
    #Llamar a modelo y calcular
    #EN grande resultado arriba, seguido de graficas comparando resultado con los valores deseados
    #Boton de borrar



except URLError as e:
        st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
