import random
import time
from pathlib import Path

import streamlit as st

st.set_page_config(page_title='두더지 잡기 게임')

GAME_FOLDER = Path(__file__).parent
MOLE_SECONDS = 1.5


@st.cache_data(show_spinner=False)
def load_image(image_path):
    return image_path.read_bytes()


hole_image = load_image(GAME_FOLDER / 'hole.png')
mole_image = load_image(GAME_FOLDER / 'img.png')

if 'mole_hole' not in st.session_state:
    st.session_state.mole_hole = random.randrange(9)
if 'mole_number' not in st.session_state:
    st.session_state.mole_number = 1
if 'mole_appeared_at' not in st.session_state:
    st.session_state.mole_appeared_at = time.monotonic()
if 'processed_mole_number' not in st.session_state:
    st.session_state.processed_mole_number = 0
if 'caught_mole' not in st.session_state:
    st.session_state.caught_mole = False
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'lives' not in st.session_state:
    st.session_state.lives = 3
if 'game_over' not in st.session_state:
    st.session_state.game_over = False


def show_next_mole(previous_hole):
    possible_holes = [number for number in range(9) if number != previous_hole]
    st.session_state.mole_hole = random.choice(possible_holes)
    st.session_state.mole_number += 1
    st.session_state.mole_appeared_at = time.monotonic()


def miss_mole(mole_number, now):
    if (
        st.session_state.game_over
        or mole_number != st.session_state.mole_number
        or st.session_state.processed_mole_number == mole_number
        or now - st.session_state.mole_appeared_at < MOLE_SECONDS
    ):
        return

    st.session_state.processed_mole_number = mole_number
    st.session_state.lives = max(0, st.session_state.lives - 1)
    st.session_state.caught_mole = False
    if st.session_state.lives == 0:
        st.session_state.game_over = True
    else:
        show_next_mole(st.session_state.mole_hole)


def click_hole(hole_number, mole_number):
    if (
        st.session_state.game_over
        or mole_number != st.session_state.mole_number
        or st.session_state.processed_mole_number == mole_number
    ):
        return

    now = time.monotonic()
    if now - st.session_state.mole_appeared_at >= MOLE_SECONDS:
        miss_mole(mole_number, now)
        return

    if hole_number != st.session_state.mole_hole:
        st.session_state.caught_mole = False
        return

    st.session_state.processed_mole_number = mole_number
    st.session_state.score += 10
    st.session_state.caught_mole = True
    show_next_mole(hole_number)


st.title('두더지 잡기 게임')
st.write('두더지를 클릭해 보세요!')

st.markdown(
    '''
    <style>
    * {
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='36' height='36'%3E%3Ctext x='1' y='30' font-size='30'%3E%F0%9F%94%A8%3C/text%3E%3C/svg%3E") 2 2, pointer;
    }
    h1 {
        font-size: 3rem;
    }
    div[data-testid="stButton"] button {
        width: 100%;
        min-height: 76px;
        font-size: 24px;
    }
    div[data-testid="stImage"] img {
        max-width: 100%;
    }
    [data-testid="stMetricValue"] {
        font-size: 3rem;
    }
    .st-key-catch_message {
        min-height: 4rem;
    }
    </style>
    ''',
    unsafe_allow_html=True,
)


@st.fragment(run_every=0.1)
def render_game():
    now = time.monotonic()
    miss_mole(st.session_state.mole_number, now)
    now = time.monotonic()

    elapsed = now - st.session_state.mole_appeared_at
    remaining = max(0, MOLE_SECONDS - elapsed)

    score_column, lives_column, time_column = st.columns(3)
    score_column.metric('현재 점수', st.session_state.score)
    lives_column.metric('라이프', st.session_state.lives)
    time_column.metric('남은 시간', f'{remaining:.1f}초')
    st.caption(f'두더지 등장 번호: {st.session_state.mole_number} · 경과 시간: {elapsed:.2f}초')

    with st.container(key='catch_message'):
        if st.session_state.game_over:
            st.error('게임 종료!')
        elif st.session_state.caught_mole:
            st.success('두더지를 잡았습니다!')
        else:
            st.markdown('&nbsp;')

    for row in range(3):
        columns = st.columns(3)
        for column in range(3):
            hole_number = row * 3 + column
            is_mole = hole_number == st.session_state.mole_hole and not st.session_state.game_over
            image = mole_image if is_mole else hole_image
            with columns[column]:
                st.image(image, width=180)
                st.button(
                    f'{hole_number + 1}번 구멍',
                    key=f'hole_{st.session_state.mole_number}_{hole_number}',
                    on_click=click_hole,
                    args=(hole_number, st.session_state.mole_number),
                    disabled=st.session_state.game_over,
                )


render_game()