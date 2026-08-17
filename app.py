import streamlit as st
from grewpy import Corpus
from grewpy.grew import GrewError
import os

from conllu_export import ConlluExportError, build_conllu_export
from request_builder import EmptyPatternError, build_request


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

if 'request_preview' not in st.session_state:
    st.session_state['request_preview'] = None


@st.cache_data(show_spinner=True)
def load_corpus(corpus_path):
    return Corpus(corpus_path)


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
        query_pattern = st.text_area(
            'GrewMatch pattern',
            help='Enter only the contents of pattern { ... }, for example: X [lemma="amore"]',
            placeholder='X [lemma="amore"]',
        )
        without = st.text_area(
            'Exclusion pattern (optional)',
            help=(
                'Enter the contents of one without { ... } block. All clauses in '
                'this block must match together for an occurrence to be excluded.'
            ),
            placeholder='X [upos=NOUN];\nX -[nsubj]-> Y',
        )
        # count = st.text_input('Group and count by')
        query_button = st.form_submit_button(
            label='Submit query',
            disabled=corpus is None,
        )


    if query_button and corpus:
        st.session_state['results'] = None
        st.session_state['current_index'] = 0
        st.session_state['request_preview'] = None

        try:
            req = build_request(query_pattern, without)
            st.session_state['request_preview'] = str(req)
            st.session_state['results'] = corpus.search(req, deco=True)
        except EmptyPatternError as error:
            st.warning(str(error))
        except GrewError as error:
            st.error(f"Invalid GrewMatch query: {error}")
        else:
            if not st.session_state['results']:
                st.warning("No results found")

    if st.session_state['request_preview']:
        with st.expander("Generated Grew request"):
            st.code(st.session_state['request_preview'], language="text")


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
        try:
            conllu_export = build_conllu_export(corpus, st.session_state['results'])
        except ConlluExportError as error:
            st.error(f"Could not export results: {error}")
        else:
            st.download_button(label='CoNLL-U',
                               data=conllu_export,
                               file_name="results.conllu")
        
        # treethtml_button = st.download_button(label='Text trees',
        #                                     data = export_textmodetrees(),
        #                                     file_name="results_texttrees.html")
        
            
