import json
import uuid
from datetime import date
from html import escape

import streamlit as st

st.set_page_config(page_title="MON JOURNAL 2026", page_icon="♡", layout="wide")

st.markdown("""
<style>
.stApp { background: #241019; color: #FFF0E9; }
[data-testid="stSidebar"] { background: #361827; }
h1, h2, h3, p, label { color: #FFF0E9; }
h1, h2 { font-family: Georgia, serif; }
.stTabs [data-baseweb="tab-list"] { gap: 5px; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] { background: #542238; color: #FFF0E9;
    border-radius: 10px; padding: 8px 12px; }
.stTabs [aria-selected="true"] { background: #D8A7B7 !important; color: #241019 !important; }
.stButton > button, .stDownloadButton > button,
.stFormSubmitButton > button { border-radius: 10px; border: 1px solid #D8A7B7;
    background: #74334D; color: #FFF0E9; }
.stButton > button:hover, .stFormSubmitButton > button:hover,
.stDownloadButton > button:hover { background: #D8A7B7; color: #241019; border-color: #D8A7B7; }
.hero { text-align: center; background: #351827; border: 1px solid #82435D;
    border-radius: 22px; padding: 48px 15px; margin: 14px 0 25px; }
.hero h1 { font-size: clamp(30px, 7vw, 64px); margin: 4px 0; }
.year { font: bold clamp(85px, 17vw, 160px) Georgia, serif; color: #D8A7B7;
    line-height: 1.15; }
.sub { letter-spacing: 3px; color: #DBB8C3; }
.card { padding: 15px; border: 1px solid #82435D; border-radius: 14px;
    background: #351827; margin: 8px 0; }
.small { color: #DBB8C3; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)


def fresh_data():
    return {
        "tasks": [], "board": [], "habits": [], "checks": {},
        "goals": [], "calendar": {}, "diary": "", "mood": {},
    }


if "journal" not in st.session_state:
    st.session_state.journal = fresh_data()

data = st.session_state.journal


def new_item(text, **extra):
    return {"id": uuid.uuid4().hex[:12], "text": text, **extra}


def redraw():
    st.rerun()


with st.sidebar:
    st.title("♡ MON JOURNAL")
    st.caption("Твой бордовый планер на 2026 год")
    st.info("Записи сохраняются только пока открыта эта сессия. Для сохранения надолго скачай резервную копию.")
    st.download_button(
        "♡ Скачать мои записи",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="mon_journal_2026.json",
        mime="application/json",
        use_container_width=True,
    )
    backup = st.file_uploader("Восстановить записи из JSON", type="json")
    if backup is not None and st.button("Загрузить мою копию", use_container_width=True):
        try:
            loaded = json.loads(backup.getvalue().decode("utf-8"))
            blank = fresh_data()
            if not isinstance(loaded, dict):
                raise ValueError("Файл должен содержать данные планера")
            for key, value in blank.items():
                candidate = loaded.get(key)
                if isinstance(candidate, type(value)):
                    blank[key] = candidate
            st.session_state.journal = blank
            for widget_key in list(st.session_state.keys()):
                if widget_key.startswith(("cal_note_", "diary_input_")):
                    del st.session_state[widget_key]
            redraw()
        except (ValueError, UnicodeError) as exc:
            st.error(f"Не получилось открыть файл: {exc}")
    st.caption("Не публикуй файл резервной копии: внутри могут быть личные записи.")

st.markdown("# MON JOURNAL 2026 ♡")
st.caption("Планы · мечты · привычки · маленькие победы")

cover, today_tab, board_tab, habit_tab, calendar_tab, diary_tab, goals_tab = st.tabs([
    "♡ Обложка", "☑ Мой день", "▤ Доска", "✿ Привычки",
    "▦ Календарь", "✎ Дневник", "☆ Цели",
])

with cover:
    st.markdown("""
    <div class="hero">
      <div class="sub">MY YEAR · MY STORY</div>
      <h1>MON JOURNAL</h1>
      <div class="year">2026</div>
      <div class="sub">ПЛАНЫ • МЕЧТЫ • ВДОХНОВЕНИЕ</div>
      <p style="margin-top:30px;color:#DBB8C3">Каждый маленький шаг имеет значение ♡</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("Выбери вкладку выше: «Мой день», «Доска», «Привычки», «Календарь», «Дневник» или «Цели».")

with today_tab:
    st.header("Мой день ♡")
    st.caption("Добавляй дела и отмечай выполненные")
    with st.form("add_task_form", clear_on_submit=True):
        text = st.text_input("Новое дело", placeholder="Например, сделать домашнее задание")
        submitted = st.form_submit_button("+ Добавить дело")
        if submitted and text.strip():
            data["tasks"].append(new_item(text.strip(), done=False))
            redraw()
    completed = sum(bool(item.get("done")) for item in data["tasks"])
    total = len(data["tasks"])
    st.progress(completed / total if total else 0)
    st.caption(f"Выполнено: {completed} из {total}")
    for task in data["tasks"][:]:
        left, right = st.columns([6, 1])
        with left:
            checked = st.checkbox(task["text"], value=task.get("done", False), key=f"task_{task['id']}")
            if checked != task.get("done", False):
                task["done"] = checked
                redraw()
        with right:
            if st.button("✕", key=f"del_task_{task['id']}"):
                data["tasks"].remove(task)
                redraw()

with board_tab:
    st.header("Моя доска планов")
    st.caption("Карточки можно передвигать между тремя колонками")
    with st.form("add_board_form", clear_on_submit=True):
        text = st.text_input("Новая карточка", placeholder="Например, начать вести блог")
        priority = st.selectbox("Приоритет", ["Обычный", "Важный", "Очень важный"])
        if st.form_submit_button("+ Добавить карточку") and text.strip():
            data["board"].append(new_item(text.strip(), stage=0, priority=priority))
            redraw()
    stages = ["Хочу сделать", "В процессе", "Готово"]
    cols = st.columns(3)
    for stage, col in enumerate(cols):
        with col:
            st.subheader(stages[stage])
            for item in data["board"][:]:
                if item.get("stage") != stage:
                    continue
                with st.container(border=True):
                    st.write(item["text"])
                    st.caption(item.get("priority", "Обычный"))
                    a, b, c = st.columns(3)
                    if stage > 0 and a.button("←", key=f"board_back_{item['id']}"):
                        item["stage"] -= 1
                        redraw()
                    if stage < 2 and b.button("→", key=f"board_next_{item['id']}"):
                        item["stage"] += 1
                        redraw()
                    if c.button("✕", key=f"board_del_{item['id']}"):
                        data["board"].remove(item)
                        redraw()

with habit_tab:
    st.header("Трекер привычек ✿")
    day = st.date_input("Выбери день", value=date.today(), key="habit_day").isoformat()
    checks = data["checks"].setdefault(day, [])
    with st.form("add_habit_form", clear_on_submit=True):
        habit_name = st.text_input("Новая привычка", placeholder="Например, читать 15 минут")
        if st.form_submit_button("+ Добавить привычку") and habit_name.strip():
            data["habits"].append(new_item(habit_name.strip()))
            redraw()
    for habit in data["habits"][:]:
        a, b = st.columns([6, 1])
        with a:
            checked = st.checkbox(habit["text"], value=habit["id"] in checks,
                                  key=f"habit_{day}_{habit['id']}")
            if checked and habit["id"] not in checks:
                checks.append(habit["id"])
                redraw()
            if not checked and habit["id"] in checks:
                checks.remove(habit["id"])
                redraw()
        with b:
            if st.button("✕", key=f"habit_del_{habit['id']}"):
                data["habits"].remove(habit)
                for old_checks in data["checks"].values():
                    if isinstance(old_checks, list) and habit["id"] in old_checks:
                        old_checks.remove(habit["id"])
                redraw()
    st.caption(f"Отмечено за {day}: {len(checks)} из {len(data['habits'])}")

with calendar_tab:
    st.header("Календарь 2026 ▦")
    chosen = st.date_input("Выбери дату для записи", value=date.today(), key="calendar_day")
    date_key = chosen.isoformat()
    st.write(f"Запись на {chosen.strftime('%d.%m.%Y')}")
    note = st.text_area("Что запланировано?", value=data["calendar"].get(date_key, ""),
                        key=f"cal_note_{date_key}", height=160)
    if st.button("♡ Сохранить планы на дату"):
        data["calendar"][date_key] = note
        st.success("Запись сохранена в текущей сессии")
    if date_key in data["calendar"]:
        st.caption("Для сохранения после закрытия приложения скачай резервную копию в боковом меню.")

with diary_tab:
    st.header("Мои мысли ✎")
    st.caption("Твоё место для идей, чувств и вдохновения")
    thoughts = st.text_area("Запиши свои мысли", value=data["diary"],
                            key="diary_input_main", height=350)
    if st.button("♡ Сохранить запись", key="save_diary"):
        data["diary"] = thoughts
        st.success("Дневник сохранён в текущей сессии")

with goals_tab:
    st.header("Мои цели на 2026 год ☆")
    with st.form("add_goal_form", clear_on_submit=True):
        goal_text = st.text_input("Новая цель", placeholder="Например, создать своё приложение")
        if st.form_submit_button("+ Добавить цель") and goal_text.strip():
            data["goals"].append(new_item(goal_text.strip(), done=False))
            redraw()
    achieved = sum(bool(goal.get("done")) for goal in data["goals"])
    all_goals = len(data["goals"])
    st.progress(achieved / all_goals if all_goals else 0)
    st.caption(f"Достигнуто целей: {achieved} из {all_goals}")
    for goal in data["goals"][:]:
        a, b = st.columns([6, 1])
        with a:
            checked = st.checkbox(goal["text"], value=goal.get("done", False),
                                  key=f"goal_{goal['id']}")
            if checked != goal.get("done", False):
                goal["done"] = checked
                redraw()
        with b:
            if st.button("✕", key=f"goal_del_{goal['id']}"):
                data["goals"].remove(goal)
                redraw()

st.divider()
st.caption("MON JOURNAL 2026 ♡ · Тестовая веб-версия · Личные записи не публикуются на общей странице")
