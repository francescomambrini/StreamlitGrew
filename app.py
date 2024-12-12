import streamlit as st
from grewpy import Corpus, CorpusDraft, Request, grew_web
from grewpy.grew_web import Grew_web
import conllu
import os


@st.cache_resource
def load_corpus(corpus_path):
    return Corpus(corpus_path)

st.title("StreamlitGrew")
st.subheader('A streamlit app to query you treebanks via Grew')

# Initialize session state for the corpus path if not set
if 'corpus_path' not in st.session_state:
    st.session_state['corpus_path'] = None

if 'current_result' not in st.session_state:
    st.session_state['current_result'] = None

if 'results' not in st.session_state:
    st.session_state['results'] = None

if 'current_index' not in st.session_state:
    st.session_state['current_index'] = 0


@st.cache_data(show_spinner=True)
def load_corpus(corpus_path):
    return Corpus(corpus_path)


def export_conllu():
    csents = []

    for res in st.session_state['results']:
        s = conllu.parse(corpus[res['sent_id']].to_conll())[0]
        for k,m in res['matching']['nodes'].items():
            i = int(m) - 1
            node = s[i]
            print(node['misc'])
            try:
                node['misc']['mark'] = k
            except TypeError:
                node['misc'] = {'mark' : k}
        csents.append(s.serialize())
    return ''.join(csents)

# def next_result():
#     if st.session_state.current_index + 1 >= len(st.session_state.results):
#         st.session_state.current_index = 0
#     else:
#         st.session_state.current_index += 1

# def previous_result():
#     if st.session_state.current_index > 0:
#         st.session_state.current_index -= 1

def go_to_result():
    i = st.session_state.go_to - 1
    st.session_state.current_index = int(i)

CorpusTab, QueryTab = st.tabs(["Load corpus", "Query"])
corpus = None
with CorpusTab:

    with CorpusTab.form(key='corpus_form'):
        corpus_path = st.text_input('Enter the path to the corpus directory')
        submit_button = st.form_submit_button(label='Submit')

    # If the user submits a new path via the form, update the session state
    if submit_button and corpus_path and corpus_path != st.session_state['corpus_path']:
        st.session_state['corpus_path'] = corpus_path
        
        # Display the current path
        st.write(f"Current corpus directory: {st.session_state['corpus_path']}")

    # Load and query the corpus only if the path is set
    if st.session_state['corpus_path']:
        if os.path.exists(st.session_state['corpus_path']):
            corpus = load_corpus(st.session_state['corpus_path'])
            st.success("Corpus loaded successfully.")
        else:
            st.error("Please provide a valid corpus path using the form.")

with QueryTab:
    with QueryTab.form(key='query_form'):
        query_pattern = st.text_area('Enter your GrewMatch patter')
        without = st.text_input('Pattern to exclude (optional)')
        # count = st.text_input('Group and count by')
        query_button = st.form_submit_button(label='Submit query')

    
    if query_button and query_pattern and corpus:
        req = Request(query_pattern)
        if without:
            req.without(without)
        # st.write(without)
        
        st.session_state['results'] = corpus.search(req, deco=True)
        st.session_state['current_index'] = 0
        if not st.session_state['results']:
            st.warning("No results found")


    if st.session_state['results']:
        st.success(f"There are {len(st.session_state['results'])} results!")
        prog = (st.session_state['current_index'] + 1) / len(st.session_state['results'])
        st.progress(prog, text=f"{st.session_state['current_index'] + 1}")
        r = st.session_state['results'][st.session_state['current_index']]
        s = corpus[r['sent_id']]
        deco = r['deco']
        x = s.to_svg(deco=deco).replace('style="fill:white;fill-opacity:0;', 'style="fill:white;')
        st.image(x)
        st.markdown(s.to_sentence(deco=deco).replace(
        '<span class="highlight">', '**:blue-background[').replace(
            '</span>',']**'))
        
        col1, col2, col3 = st.columns([1, 1, 1])
        # prev = QueryTab.button("Previous", on_click=previous_result())
        # next = QueryTab.button("Netxt", on_click=next_result())
        # with col1:
        #     if st.button("⏮️ Previous", on_click=previous_result):
        #         pass

        # with col2:
        #     if st.button("Next ⏭️", on_click=next_result):
        #         pass

    
        if st.number_input("Go to", 
                            min_value=1,
                            max_value=len(st.session_state.results),
                            step = 1,
                            key="go_to", on_change=go_to_result):
            pass

        
        st.markdown("### Export results")
        conllu_button = st.download_button(label='Conllu',
                                            data = export_conllu(),
                                            file_name="results.conllu")
        
        # treethtml_button = st.download_button(label='Text trees',
        #                                     data = export_textmodetrees(),
        #                                     file_name="results_texttrees.html")
        
            
