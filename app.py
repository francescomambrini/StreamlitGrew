import streamlit as st
from grewpy import Corpus, CorpusDraft, Request, grew_web
from grewpy.grew_web import Grew_web
import tkinter as tk
from tkinter import filedialog

@st.cache_resource
def load_corpus(corpus_path):
    return Corpus(corpus_path)

def select_folder():
   root = tk.Tk()
   root.withdraw()
   folder_path = filedialog.askdirectory(master=root)
   root.destroy()
   return folder_path

st.title("StreamlitGrew")
st.subheader('A streamlit app to query you treebanks via Grew')


CorpusTab, QueryTab = st.tabs(["Load corpus", "Query"])
corpus = None
with CorpusTab:
    st.markdown("Load your corpus")
    selected_folder_path = st.session_state.get("folder_path", None)
    folder_select_button = st.button("Select Folder")
    if folder_select_button:
        selected_folder_path = select_folder()
        st.session_state.folder_path = selected_folder_path
    
    if selected_folder_path:
        st.write("Selected folder path:", selected_folder_path)
        corpus = load_corpus(selected_folder_path)

with QueryTab:
    ptrn = '''X [ lemma="amore" ] 
    '''

    req = Request(ptrn)
    # req.without("X -[case]-> V")
    if corpus:
        res = corpus.search(req, deco=True)
    else:
        res = None

    if res:
        st.success(f'There are {len(res)} results!')
        i = st.select_slider('Slide to select sentence', options=range(0, len(res)))
        r = res[i]
        s = corpus[r['sent_id']]
        deco = r['deco']
        x = s.to_svg(deco=deco).replace('style="fill:white;fill-opacity:0;', 'style="fill:white;')
        st.image(x)
        st.markdown(s.to_sentence(deco=deco).replace(
            '<span class="highlight">', '**:blue-background[').replace(
                '</span>',']**'))
    else:
        st.warning('There are no results!')
