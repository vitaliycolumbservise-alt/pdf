#Веб-моделювання трансакційних витрат.
import streamlit as st
import pandas as pd #для таблиць
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

#Пам'ять сценаріїв
if "scenarios" not in st.session_state:
    st.session_state["scenarios"] = []

# прапорець для показу блоку порівняння (щоб графік не зникав)
if "compare_clicked" not in st.session_state:
    st.session_state["compare_clicked"] = False

#Значення за замовчуванням (2024 рік)
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
    min_value=0._


