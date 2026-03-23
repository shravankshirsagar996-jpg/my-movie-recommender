import streamlit as st
import pickle
import requests
import html as html_lib
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cinematic World",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Constants ─────────────────────────────────────────────────────────────────
TMDB_API_KEY   = "8265bd1679663a7ea12ac168da84d2e8"
TMDB_BASE      = "https://api.themoviedb.org/3"
TMDB_IMG_W500  = "https://image.tmdb.org/t/p/w500"
TMDB_IMG_W342  = "https://image.tmdb.org/t/p/w342"
YOUTUBE_EMBED  = "https://www.youtube.com/embed"
MOVIE_PKL      = r"C:\Users\H P\OneDrive\Desktop\projects\project no .6\movie_list.pkl"
SIMILARITY_PKL = r"C:\Users\H P\OneDrive\Desktop\projects\project no .6\model\similarity.pkl"
PLACEHOLDER    = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "width='300' height='450'%3E%3Crect width='300' height='450' fill='%231a1a1a'/%3E"
    "%3Ctext x='150' y='210' font-family='Arial' font-size='16' fill='%23E50914' "
    "text-anchor='middle'%3ENo Poster%3C/text%3E"
    "%3Ctext x='150' y='250' font-family='Arial' font-size='36' "
    "text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E"
)

# ── CSS + Splash ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --red:   #E50914;
    --red2:  #b20710;
    --black: #000000;
    --card:  #141414;
    --text:  #e5e5e5;
    --muted: #808080;
}

#MainMenu, footer, header { visibility:hidden; }
.block-container { padding:0 2rem 4rem !important; max-width:1400px !important; }
.stApp { background:var(--black) !important; color:var(--text); font-family:'Inter',sans-serif; }

/* ── Splash ── */
#splash {
    position:fixed; inset:0; background:#000; z-index:9999;
    display:flex; align-items:center; justify-content:center;
    animation:splashFade 0.5s ease 3.4s forwards;
    pointer-events:none;
}
#splash h1 {
    font-family:'Bebas Neue',sans-serif;
    font-size:clamp(2.5rem,8vw,7rem);
    letter-spacing:0.12em; color:var(--red);
    text-shadow:0 0 30px rgba(229,9,20,.9), 0 0 80px rgba(229,9,20,.5), 0 0 160px rgba(229,9,20,.25);
    animation:zoomIn 1.2s cubic-bezier(0.16,1,0.3,1) 0.3s both,
              textFade 0.8s ease 2.5s forwards;
    white-space:nowrap;
}
@keyframes zoomIn {
    from { opacity:0; transform:scale(0.35) translateY(24px); }
    to   { opacity:1; transform:scale(1) translateY(0); }
}
@keyframes textFade { to { opacity:0; } }
@keyframes splashFade { to { opacity:0; visibility:hidden; } }

/* ── Navbar ── */
.navbar {
    display:flex; align-items:center; gap:1rem; padding:1rem 0;
    background:linear-gradient(to bottom,rgba(0,0,0,.98) 0%,transparent 100%);
    position:sticky; top:0; z-index:100; margin-bottom:1rem;
}
.brand {
    font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--red);
    letter-spacing:.1em; text-shadow:0 0 20px rgba(229,9,20,.6);
}
.tagline {
    font-size:.72rem; color:var(--muted); letter-spacing:.06em;
    text-transform:uppercase; margin-top:2px;
}

/* ── Search input (st.text_input) — COMPLETE override ── */
/* Container */
div[data-testid="stTextInput"] { margin-bottom:0 !important; }
div[data-testid="stTextInput"] > div {
    background:#1a1a1a !important;
    border:1.5px solid #444 !important;
    border-radius:6px !important;
    padding:0 !important;
}
div[data-testid="stTextInput"] > div:focus-within {
    border-color:var(--red) !important;
    box-shadow:0 0 0 2px rgba(229,9,20,.3) !important;
}
/* The actual <input> tag */
div[data-testid="stTextInput"] input {
    color:#ffffff !important;
    -webkit-text-fill-color:#ffffff !important;
    caret-color:var(--red) !important;
    font-size:1rem !important;
    background:#1a1a1a !important;
    border:none !important;
    padding:.75rem 1rem !important;
    height:46px !important;
    opacity:1 !important;
}
/* Placeholder text */
div[data-testid="stTextInput"] input::placeholder {
    color:#666 !important;
    -webkit-text-fill-color:#666 !important;
    opacity:1 !important;
}
/* Hide label */
div[data-testid="stTextInput"] label { display:none !important; }

/* ── Dropdown suggestion list ── */
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
ul[role="listbox"] li {
    color:#e5e5e5 !important; background:#1a1a1a !important;
    font-size:.95rem !important;
}
[data-baseweb="menu"] li:hover,
ul[role="listbox"] li:hover { background:#2d2d2d !important; color:#fff !important; }

/* ── Button ── */
.stButton > button {
    background:var(--red) !important; color:#fff !important; border:none !important;
    border-radius:6px !important; font-family:'Inter',sans-serif !important;
    font-weight:600 !important; font-size:1rem !important;
    padding:0 2rem !important; height:46px !important; width:100% !important;
    letter-spacing:.05em !important;
    box-shadow:0 4px 20px rgba(229,9,20,.4) !important;
    transition:background .2s,transform .15s,box-shadow .2s !important;
}
.stButton > button:hover {
    background:var(--red2) !important; transform:scale(1.02) !important;
    box-shadow:0 6px 28px rgba(229,9,20,.6) !important;
}

/* ── Suggestion dropdown for text_input ── */
.movie-dropdown {
    background:#1a1a1a; border:1px solid #333; border-radius:6px;
    max-height:260px; overflow-y:auto; position:absolute; z-index:1000;
    width:100%; box-shadow:0 8px 24px rgba(0,0,0,.8); margin-top:2px;
}
.movie-option {
    padding:.6rem 1rem; color:#e5e5e5; cursor:pointer;
    font-size:.95rem; border-bottom:1px solid #222;
    transition:background .15s;
}
.movie-option:hover { background:#2d2d2d; color:#fff; }
.movie-option:last-child { border-bottom:none; }

/* ── Section titles ── */
.section-title {
    font-family:'Bebas Neue',sans-serif; font-size:1.9rem;
    letter-spacing:.08em; color:#fff; margin:2rem 0 1rem;
    display:flex; align-items:center; gap:.6rem;
}
.section-title::after {
    content:''; flex:1; height:1px;
    background:linear-gradient(to right,#333,transparent);
}

/* ── Hero ── */
.hero-wrapper {
    display:flex; gap:2.5rem; align-items:flex-start;
    background:linear-gradient(135deg,#0d0d0d 0%,#200000 100%);
    border:1px solid #2a2a2a; border-radius:12px;
    padding:2rem; box-shadow:0 8px 40px rgba(0,0,0,.7);
}
.hero-poster { flex-shrink:0; }
.hero-poster img {
    border-radius:8px; width:220px; display:block;
    box-shadow:0 12px 40px rgba(229,9,20,.35),0 4px 16px rgba(0,0,0,.9);
}
.hero-info { flex:1; min-width:0; }
.hero-title {
    font-family:'Bebas Neue',sans-serif; font-size:3rem;
    color:#fff; letter-spacing:.06em; margin:0 0 .3rem; line-height:1.1;
}
.hero-meta {
    color:var(--muted); font-size:.83rem; letter-spacing:.04em;
    margin-bottom:.8rem; text-transform:uppercase;
}
.hero-overview {
    color:#c0c0c0; font-size:.95rem; line-height:1.75;
    max-width:640px; margin-top:.6rem;
}
.rating-badge {
    display:inline-block; background:var(--red); color:#fff;
    font-weight:700; font-size:.85rem; padding:.25rem .7rem;
    border-radius:4px; margin-bottom:.6rem;
}

/* ── Trailer ── */
.trailer-frame {
    width:100%; max-width:760px; aspect-ratio:16/9;
    border-radius:8px; border:1px solid #333; overflow:hidden;
    box-shadow:0 8px 32px rgba(0,0,0,.7); margin-top:.5rem;
}
.trailer-frame iframe { width:100%; height:100%; border:none; }

/* ── Rec grid ── */
.rec-grid {
    display:grid; grid-template-columns:repeat(5,1fr); gap:1rem; margin-top:.5rem;
}
.rec-card {
    position:relative; border-radius:6px; overflow:hidden;
    background:var(--card); border:1px solid #222;
    transition:transform .3s cubic-bezier(.34,1.56,.64,1),box-shadow .3s;
}
.rec-card:hover {
    transform:scale(1.07) translateY(-6px);
    box-shadow:0 16px 40px rgba(229,9,20,.45),0 4px 16px rgba(0,0,0,.9);
    z-index:10; border-color:var(--red);
}
.rec-card img { width:100%; aspect-ratio:2/3; object-fit:cover; display:block; }
.rec-overlay {
    position:absolute; bottom:0; left:0; right:0;
    background:linear-gradient(transparent,rgba(0,0,0,.92));
    padding:1.5rem .7rem .7rem; opacity:0; transition:opacity .25s;
}
.rec-card:hover .rec-overlay { opacity:1; }
.rec-title {
    font-size:.78rem; font-weight:600; color:#ddd;
    text-align:center; padding:.45rem .4rem;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    background:var(--card); border-top:1px solid #2a2a2a;
}
.play-icon {
    display:flex; align-items:center; justify-content:center;
    width:34px; height:34px; background:var(--red);
    border-radius:50%; margin:0 auto .4rem; font-size:.9rem;
}
.rec-rating { font-size:.7rem; color:#aaa; text-align:center; }

/* ── Empty state ── */
.empty-state { text-align:center; padding:5rem 2rem; color:var(--muted); }
.empty-state h3 {
    font-family:'Bebas Neue',sans-serif; font-size:2.4rem;
    color:#2a2a2a; letter-spacing:.1em;
}
.empty-state p { font-size:.9rem; margin-top:.5rem; }

hr { border-color:#1e1e1e !important; margin:1.8rem 0 !important; }
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#0d0d0d; }
::-webkit-scrollbar-thumb { background:#333; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:var(--red); }
</style>

<div id="splash"><h1>WELCOME TO CINEMATIC WORLD</h1></div>
""", unsafe_allow_html=True)

# Navbar
st.markdown("""
<div class="navbar">
  <div>
    <div class="brand">🎬 CINEMATIC WORLD</div>
    <div class="tagline">Find your next favourite film</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_data():
    # फाईल खरंच अस्तित्वात आहे का हे तपासतो
    if not os.path.exists(MOVIE_PKL) or not os.path.exists(SIMILARITY_PKL):
        raise FileNotFoundError("Model files are missing. Check your GitHub repository.")
        
    with open(MOVIE_PKL, "rb") as f:
        movies = pickle.load(f)
    with open(SIMILARITY_PKL, "rb") as f:
        similarity = pickle.load(f)
    return movies, similarity

try:
    movies_df, similarity = load_data()
    movie_titles = sorted(movies_df["title"].tolist())
    has_movie_id = "movie_id" in movies_df.columns
    data_ok = True
except Exception as e:
    # प्रोफेशनल एरर मेसेज जो युजरला कळवेल की ड्राइव्हवरून फाईल डाऊनलोड करायची आहे
    st.error(f"⚠️ **Attention:** AI Models not found on server.\n\n"
             f"If you are seeing this on Streamlit Cloud, please ensure `{MOVIE_PKL}` is uploaded to your GitHub repository. "
             f"If the file is too large, use the Google Drive link provided in the README.")
    data_ok = False
    movie_titles = []
    has_movie_id = False

# ── TMDB helpers ──────────────────────────────────────────────────────────────
def _tmdb_get(endpoint: str, extra: dict = {}) -> dict:
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    params.update(extra)
    r = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def _title_variants(title: str) -> list:
    """Return search strings to try — strips #, parens, colons."""
    seen, variants = set(), []
    for t in [
        title,
        re.sub(r'^#+\s*', '', title).strip(),
        re.sub(r'\s*\(.*?\)\s*$', '', re.sub(r'^#+\s*', '', title)).strip(),
        re.sub(r'^#+\s*', '', title).split(':')[0].strip(),
        title.split(':')[0].strip(),
    ]:
        if t and t not in seen:
            seen.add(t)
            variants.append(t)
    return variants


def _best_result(results: list, query: str) -> dict | None:
    """Pick best match: exact title > popularity-sorted first result."""
    if not results:
        return None
    ql = query.lower().strip()
    # Exact match, then pick most popular among ties
    exact = sorted(
        [r for r in results if r.get("title", "").lower().strip() == ql],
        key=lambda r: r.get("popularity", 0),
        reverse=True,
    )
    if exact:
        return exact[0]
    # No exact match → return most popular result overall
    return max(results, key=lambda r: r.get("popularity", 0))


def fetch_poster_by_tmdb_id(tmdb_id: int) -> str:
    """Fetch poster URL directly from TMDB movie ID (used for dataset movies)."""
    try:
        d = _tmdb_get(f"/movie/{tmdb_id}")
        if d.get("poster_path"):
            return TMDB_IMG_W500 + d["poster_path"]
    except Exception:
        pass
    return PLACEHOLDER


def fetch_movie_info(title: str, dataset_tmdb_id: int = None) -> dict:
    """
    Return full movie info dict.
    Priority: dataset_tmdb_id (direct ID lookup) → title search variants.
    """
    result = {
        "tmdb_id": None, "poster_url": PLACEHOLDER,
        "overview": "", "rating": 0.0,
        "release": "", "genres": "", "trailer_key": None,
    }

    search_hit = None

    # Strategy 1: use the TMDB ID from the dataset directly (most accurate)
    if dataset_tmdb_id:
        try:
            details = _tmdb_get(f"/movie/{dataset_tmdb_id}")
            result["tmdb_id"]    = dataset_tmdb_id
            result["overview"]   = details.get("overview", "")
            result["rating"]     = details.get("vote_average") or 0.0
            result["release"]    = (details.get("release_date") or "")[:4]
            result["genres"]     = ", ".join(g["name"] for g in details.get("genres", [])[:3])
            result["poster_url"] = (
                TMDB_IMG_W500 + details["poster_path"]
                if details.get("poster_path") else PLACEHOLDER
            )
            # Trailer
            vdata = _tmdb_get(f"/movie/{dataset_tmdb_id}/videos")
            for v in vdata.get("results", []):
                if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser"):
                    result["trailer_key"] = v["key"]
                    break
            return result
        except Exception:
            pass  # fall through to search

    # Strategy 2: text search with multiple title variants
    for query in _title_variants(title):
        try:
            data = _tmdb_get("/search/movie", {"query": query})
            hit  = _best_result(data.get("results", []), query)
            if hit:
                search_hit = hit
                break
        except Exception:
            continue

    if not search_hit:
        return result

    tmdb_id = search_hit.get("id")
    result["tmdb_id"]    = tmdb_id
    # Use search result poster as immediate fallback
    result["poster_url"] = (
        TMDB_IMG_W500 + search_hit["poster_path"]
        if search_hit.get("poster_path") else PLACEHOLDER
    )
    result["overview"] = search_hit.get("overview", "")

    # Full details call
    try:
        details = _tmdb_get(f"/movie/{tmdb_id}")
        if details.get("overview"):
            result["overview"] = details["overview"]
        result["rating"]  = details.get("vote_average") or 0.0
        result["release"] = (details.get("release_date") or "")[:4]
        result["genres"]  = ", ".join(g["name"] for g in details.get("genres", [])[:3])
        if details.get("poster_path"):
            result["poster_url"] = TMDB_IMG_W500 + details["poster_path"]
    except Exception:
        pass

    # Trailer
    try:
        vdata = _tmdb_get(f"/movie/{tmdb_id}/videos")
        for v in vdata.get("results", []):
            if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser"):
                result["trailer_key"] = v["key"]
                break
    except Exception:
        pass

    return result


def recommend(title: str) -> list:
    try:
        idx  = movies_df[movies_df["title"] == title].index[0]
        sims = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)[1:6]
        return [movies_df.iloc[i]["title"] for i, _ in sims]
    except Exception:
        return []


def get_dataset_tmdb_id(title: str):
    """Return the TMDB movie_id from the dataset if available."""
    if not has_movie_id:
        return None
    try:
        row = movies_df[movies_df["title"] == title]
        if not row.empty:
            val = row.iloc[0]["movie_id"]
            return int(val) if val else None
    except Exception:
        pass
    return None


# ── HTML builders ─────────────────────────────────────────────────────────────
def build_hero(info: dict, safe_title: str) -> str:
    badge = ""
    if info["rating"]:
        badge = '<span class="rating-badge">⭐ ' + f'{info["rating"]:.1f}' + ' / 10</span>'
    meta = " · ".join(x for x in [info["release"], info["genres"]] if x)
    ov   = html_lib.escape(info["overview"]) if info["overview"] else "No overview available."
    img  = (
        '<img src="' + info["poster_url"] + '" alt="' + safe_title + '" '
        'onerror="this.src=\'' + PLACEHOLDER + '\'" />'
    )
    return (
        '<div class="hero-wrapper">'
          '<div class="hero-poster">' + img + '</div>'
          '<div class="hero-info">'
            '<div class="hero-title">' + safe_title + '</div>'
            '<div class="hero-meta">' + html_lib.escape(meta) + '</div>'
            + badge
            + '<div class="hero-overview">' + ov + '</div>'
          '</div>'
        '</div>'
    )


def build_rec_card(title: str, info: dict) -> str:
    st_ = html_lib.escape(title)
    rr  = f"⭐ {info['rating']:.1f}" if info.get("rating") else ""
    img = '<img src="' + info["poster_url"] + '" alt="' + st_ + '" onerror="this.src=\'' + PLACEHOLDER + '\'" />'
    return (
        '<div class="rec-card">'
          + img
          + '<div class="rec-overlay">'
              '<div class="play-icon">▶</div>'
              '<div class="rec-rating">' + rr + '</div>'
            '</div>'
          '<div class="rec-title" title="' + st_ + '">' + st_ + '</div>'
        '</div>'
    )


# ── Search bar ────────────────────────────────────────────────────────────────
col_s, col_b = st.columns([5, 1])

with col_s:
    query_input = st.text_input(
        "movie_search",
        label_visibility="collapsed",
        placeholder="🔍  Type a movie name… e.g. Avatar, Inception, #Horror",
        key="search_query",
    )

with col_b:
    go = st.button("▶  Recommend", use_container_width=True)

# Autocomplete suggestions
selected = st.session_state.get("confirmed_title", "")

if query_input and not go:
    q = query_input.strip().lower()
    matches = [t for t in movie_titles if q in t.lower()][:8]
    if matches:
        st.markdown(
            '<div style="position:relative"><div class="movie-dropdown" id="suggestions">',
            unsafe_allow_html=True,
        )
        for m in matches:
            safe_m = html_lib.escape(m)
            # Each suggestion is a button that sets session state
            if st.button(m, key="sug_" + m[:40]):
                st.session_state["confirmed_title"] = m
                st.session_state["search_query"]    = m
                st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# When Recommend is clicked, lock in whatever is typed
if go:
    # Try exact match first, then case-insensitive
    typed = query_input.strip()
    exact = [t for t in movie_titles if t.lower() == typed.lower()]
    if exact:
        selected = exact[0]
    elif typed:
        # Closest prefix match
        prefix = [t for t in movie_titles if t.lower().startswith(typed.lower())]
        selected = prefix[0] if prefix else typed
    st.session_state["confirmed_title"] = selected

st.markdown("<hr>", unsafe_allow_html=True)

if not data_ok:
    st.stop()

# ── Main flow ─────────────────────────────────────────────────────────────────
if selected and go:

    dataset_id = get_dataset_tmdb_id(selected)

    with st.spinner("🎬 Fetching movie details…"):
        info = fetch_movie_info(selected, dataset_tmdb_id=dataset_id)

    safe_title = html_lib.escape(selected)

    st.markdown('<div class="section-title">🎬 SELECTED MOVIE</div>', unsafe_allow_html=True)
    st.markdown(build_hero(info, safe_title), unsafe_allow_html=True)

    if info["trailer_key"]:
        st.markdown('<div class="section-title">▶ OFFICIAL TRAILER</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="trailer-frame">'
              '<iframe src="' + YOUTUBE_EMBED + '/' + info["trailer_key"] + '?rel=0" '
              'allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture" '
              'allowfullscreen></iframe>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<p style="color:#555;font-size:.85rem;margin-top:.4rem;">No trailer available.</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    recs = recommend(selected)
    if recs:
        st.markdown('<div class="section-title">🍿 MORE LIKE THIS</div>', unsafe_allow_html=True)
        cards = ""
        with st.spinner("Loading recommendations…"):
            for rec_title in recs:
                rid = get_dataset_tmdb_id(rec_title)
                rec_info = fetch_movie_info(rec_title, dataset_tmdb_id=rid)
                cards += build_rec_card(rec_title, rec_info)
        st.markdown('<div class="rec-grid">' + cards + '</div>', unsafe_allow_html=True)
    else:
        st.warning("No recommendations found for this title.")

else:
    st.markdown("""
    <div class="empty-state">
        <h3>🎬 YOUR CINEMA AWAITS</h3>
        <p>Type a movie name above and hit <b>▶ Recommend</b> to discover what to watch next.</p>
    </div>""", unsafe_allow_html=True)
