# Веб-моделювання трансакційних витрат.
import streamlit as st
import pandas as pd  # для таблиць
from model_transaction_costs import (
    ModelParams,
    ExtraItem,
    calc_total,
)

st.set_page_config(
    page_title="Розрахунок транcакційних витрат",
    layout="centered",
)

st.title("Моделювання транcакційних витрат BagShop")
st.write(
    "Введіть параметри нижче та натисніть **«Розрахувати»**, "
    "щоб отримати структуру трансакційних витрат."
)

# Пам'ять сценаріїв
if "scenarios" not in st.session_state:
    st.session_state["scenarios"] = []

# прапорець для показу блоку порівняння (щоб графік не зникав)
if "compare_clicked" not in st.session_state:
    st.session_state["compare_clicked"] = False

# прапорець для показу графіка
if "show_chart" not in st.session_state:
    st.session_state["show_chart"] = False

# Значення за замовчуванням (2024 рік)
default = ModelParams(
    Q=10900,
    avg_check=870,
    p_loc=0.30,
    p_int=0.70,
    return_rate=0.061,
    c_loc=45,
    c_int=50,
    c_ret_loc=15,
    c_ret_int=20,
    online_share=0.50,
    pay_commission=0.0275,
    n_new_customers=12308,
    cac=52,
    staff_fixed=500000,
    staff_per_order=22,
    extra_items=[],
)

st.subheader("Вхідні дані")

Q = st.number_input(
    "Кількість замовлень",
    min_value=0,
    max_value=100000,
    value=default.Q,
    step=100,
)

avg_check = st.number_input(
    "Середній чек (грн)",
    min_value=0.0,
    max_value=10000.0,
    value=float(default.avg_check),
    step=10.0,
)

p_loc = st.slider(
    "Частка локальних доставок",
    min_value=0.0,
    max_value=1.0,
    value=float(default.p_loc),
    step=0.05,
)
p_int = 1.0 - p_loc

return_rate = st.slider(
    "Рівень повернень (частка)",
    min_value=0.00,
    max_value=1.00,
    value=float(default.return_rate),
    step=0.001,
    format="%.3f",
)

c_loc = st.number_input(
    "Вартість локальної доставки, грн",
    min_value=0.0,
    max_value=500.0,
    value=float(default.c_loc),
    step=5.0,
)
c_int = st.number_input(
    "Вартість міжобласної доставки, грн",
    min_value=0.0,
    max_value=500.0,
    value=float(default.c_int),
    step=5.0,
)

c_ret_loc = st.number_input(
    "Вартість повернення локальної доставки, грн",
    min_value=0.0,
    max_value=200.0,
    value=float(default.c_ret_loc),
    step=1.0,
)
c_ret_int = st.number_input(
    "Вартість повернення міжобласної доставки, грн",
    min_value=0.0,
    max_value=200.0,
    value=float(default.c_ret_int),
    step=1.0,
)

online_share = st.slider(
    "Частка онлайн-оплат",
    min_value=0.0,
    max_value=1.0,
    value=float(default.online_share),
    step=0.05,
)

pay_commission_percent = st.number_input(
    "Комісія платіжного сервісу (%)",
    min_value=0.0,
    max_value=10.0,
    value=float(default.pay_commission * 100),
    step=0.1,
)
pay_commission = pay_commission_percent / 100.0

n_new_customers = st.number_input(
    "Залучені клієнти",
    min_value=0,
    max_value=50000,
    value=default.n_new_customers,
    step=100,
)

cac = st.number_input(
    "CAC (грн)",
    min_value=0.0,
    max_value=200.0,
    value=float(default.cac),
    step=1.0,
)

staff_fixed = st.number_input(
    "Фіксовані витрати на персонал, грн",
    min_value=0.0,
    max_value=10000000.0,
    value=float(default.staff_fixed),
    step=10000.0,
)

staff_per_order = st.number_input(
    "Витрати на обробку одного замовлення, грн",
    min_value=0.0,
    max_value=200.0,
    value=float(default.staff_per_order),
    step=1.0,
)

# Додати показник
st.subheader("Додатковий показник (за бажанням)")
add_extra = st.checkbox("Додати додатковий показник до поточного сценарію")
extra_items = []
if add_extra:
    extra_kind_label = st.radio(
        "Тип показника",
        ["Додаткові витрати (+ до витрат)", "Додатковий дохід (– до витрат)"],
    )
    extra_name = st.text_input("Назва показника")
    extra_amount = st.number_input(
        "Сума показника, грн",
        min_value=0.0,
        value=0.0,
        step=10.0,
    )

    if extra_name and extra_amount > 0:
        if extra_kind_label.startswith("Додаткові витрати"):
            kind = "cost"
        else:
            kind = "revenue"
        extra_items.append(
            ExtraItem(name=extra_name.strip(), kind=kind, amount=extra_amount)
        )

if st.button("Розрахувати"):
    params = ModelParams(
        Q=Q,
        avg_check=avg_check,
        p_loc=p_loc,
        p_int=p_int,
        return_rate=return_rate,
        c_loc=c_loc,
        c_int=c_int,
        c_ret_loc=c_ret_loc,
        c_ret_int=c_ret_int,
        online_share=online_share,
        pay_commission=pay_commission,
        n_new_customers=n_new_customers,
        cac=cac,
        staff_fixed=staff_fixed,
        staff_per_order=staff_per_order,
        # тільки для цього розрахунку
        extra_items=extra_items,
    )
    result = calc_total(params)

    # Збереження сценарію
    st.session_state["scenarios"].append(
        {
            "id": len(st.session_state["scenarios"]) + 1,
            "params": params,
            "result": result,
        }
    )
    # При новому розрахунку вимикаємо режим порівняння і графік
    st.session_state["compare_clicked"] = False
    st.session_state["show_chart"] = False

    st.success(
        f"Сценарій №{len(st.session_state['scenarios'])} успішно розраховано."
    )

# Останній сценарій
if st.session_state["scenarios"]:
    last = st.session_state["scenarios"][-1]
    st.subheader(
        f"Результати останнього розрахунку (сценарій №{last['id']})"
    )
    res = last["result"]

    table = [
        {"№": 1, "Стаття": "Логістика", "Сума, грн": f"{res['logistics']:.2f}"},
        {"№": 2, "Стаття": "Платіжні сервіси", "Сума, грн": f"{res['payments']:.2f}"},
        {"№": 3, "Стаття": "Маркетинг", "Сума, грн": f"{res['marketing']:.2f}"},
        {"№": 4, "Стаття": "Персонал", "Сума, грн": f"{res['staff']:.2f}"},
    ]

    # Додаткові
    if res["extra_net"] != 0:
        sign = "+" if res["extra_net"] > 0 else "-"


