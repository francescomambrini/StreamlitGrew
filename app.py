import streamlit as st
from grewpy import Corpus, CorpusDraft, Request, grew_web
from grewpy.grew_web import Grew_web


st.title("StreamlitGrew")
st.subheader('A streamlit app to query you treebanks via Grew')


CorpusTab, QueryTab = st.tabs(["Load corpus", "Query"])

with CorpusTab:
    st.markdown("Load your corpus")
    # test
    corpus = Corpus('test/it_old-ud-train.conllu')

with QueryTab:
    ptrn = '''X [ lemma="amore" ] 
    '''

    req = Request(ptrn)
    # req.without("X -[case]-> V")
    res = corpus.search(req, deco=True)

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
