import streamlit as st
import pandas as pd

from model_transaction_costs import ModelParams, ExtraItem, calculate_scenarios


st.set_page_config(
    page_title="Модель трансакційних витрат інтернет-магазину",
    layout="wide",
)

st.title("Моделювання трансакційних витрат інтернет-магазину")


# === 1. Ініціалізація стану сесії для додаткових показників ===

if "extra_items" not in st.session_state:
    st.session_state.extra_items = []  # type: ignore[list-item]


# === 2. Блок введення параметрів моделі ===

st.header("Вихідні параметри моделі")

col1, col2, col3 = st.columns(3)

with col1:
    orders_per_month = st.number_input(
        "Кількість замовлень на місяць",
        min_value=0,
        value=10900,
        step=100,
    )
    avg_check = st.number_input(
        "Середній чек, грн",
        min_value=0.0,
        value=800.0,
        step=10.0,
        format="%.2f",
    )
    fixed_costs = st.number_input(
        "Постійні витрати на місяць, грн",
        min_value=0.0,
        value=100_000.0,
        step=1000.0,
        format="%.2f",
    )

with col2:
    share_online = st.slider(
        "Частка онлайн-оплат, %",
        min_value=0,
        max_value=100,
        value=60,
        step=5,
    )
    payment_commission = st.number_input(
        "Комісія платіжного сервісу, %",
        min_value=0.0,
        max_value=10.0,
        value=1.5,
        step=0.1,
        format="%.2f",
        help="Наприклад: LiqPay 1,5 %, WayForPay 2 % тощо",
    )
    return_rate = st.slider(
        "Частка повернень замовлень, %",
        min_value=0,
        max_value=50,
        value=5,
        step=1,
    )

with col3:
    variable_cost_per_order = st.number_input(
        "Змінні витрати на одне замовлення, грн",
        min_value=0.0,
        value=150.0,
        step=10.0,
        format="%.2f",
    )
    logistic_cost_per_order = st.number_input(
        "Логістичні витрати на одне замовлення, грн",
        min_value=0.0,
        value=90.0,
        step=5.0,
        format="%.2f",
    )


# Формуємо об'єкт параметрів моделі
model_params = ModelParams(
    orders_per_month=int(orders_per_month),
    avg_check=float(avg_check),
    share_online=share_online / 100.0,          # слайдер у %, в моделі 0..1
    payment_commission=payment_commission / 100.0,
    fixed_costs=float(fixed_costs),
    variable_cost_per_order=float(variable_cost_per_order),
    logistic_cost_per_order=float(logistic_cost_per_order),
    return_rate=return_rate / 100.0,
)


st.markdown("---")


# === 3. Блок «Додати показник» ===

st.header("Додаткові показники (витрати / доходи)")

with st.expander("Додати показник"):
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        new_name = st.text_input("Назва показника", placeholder="Наприклад, 'Додаткові витрати на пакування'")
    with col_b:
        new_value = st.number_input(
            "Сума, грн (+/-)",
            value=0.0,
            step=100.0,
            format="%.2f",
        )
    with col_c:
        type_choice = st.radio(
            "Тип показника",
            options=["Витрати (–)", "Доходи (+)"],
            horizontal=True,
        )

    col_d, col_e = st.columns([1, 2])
    with col_d:
        use_once = st.checkbox(
            "Використовувати лише для цього обрахунку",
            value=True,
            help="Якщо позначено – показник враховується в поточному розрахунку, "
                 "але не зберігається для наступних запусків.",
        )

    add_btn = st.button("Додати показник")

    if add_btn and new_name and new_value != 0.0:
        is_revenue = type_choice == "Доходи (+)"
        item = ExtraItem(
            name=new_name,
            value=float(new_value),
            is_revenue=is_revenue,
            use_only_once=use_once,
        )
        # Додаємо тільки до поточної сесії
        st.session_state.extra_items.append(item)  # type: ignore[attr-defined]
        st.success(f"Показник «{new_name}» додано.")


# Показуємо таблицю додаткових показників
if st.session_state.extra_items:  # type: ignore[truthy-function]
    st.subheader("Список доданих показників (для поточного розрахунку)")
    extra_data = []
    for item in st.session_state.extra_items:  # type: ignore[attr-defined]
        extra_data.append(
            {
                "Назва": item.name,
                "Сума, грн": item.value,
                "Тип": "Дохід (+)" if item.is_revenue else "Витрата (–)",
                "Лише для цього розрахунку": "Так" if item.use_only_once else "Ні",
            }
        )
    extra_df = pd.DataFrame(extra_data)
    st.dataframe(extra_df, use_container_width=True, hide_index=True)
else:
    st.info("Додаткові показники поки що не додано.")


st.markdown("---")


# === 4. Розрахунок сценаріїв ===

st.header("Результати моделювання за сценаріями")

# Для простоти всі extra_items використовуємо тільки в поточному розрахунку,
# а після натискання кнопки можна їх очистити, якщо потрібно.
extra_items_for_calc = list(st.session_state.extra_items)  # type: ignore[attr-defined]

calculate_btn = st.button("Перерахувати модель")

if calculate_btn or True:
    results_df = calculate_scenarios(model_params, extra_items_for_calc)

    # Визначаємо найкращий сценарій за прибутком
    best_idx = results_df["Прибуток, грн"].idxmax()
    best_row = results_df.loc[best_idx]

    st.subheader("Підсумкова таблиця результатів")
    st.dataframe(results_df, use_container_width=True, hide_index=True)

    st.success(
        f"Найкращий сценарій за прибутком: **{best_row['Сценарій']}** "
        f"з прибутком **{best_row['Прибуток, грн']:.2f} грн**."
    )

    st.markdown("---")

    # === 5. Візуалізація результатів ===

    st.header("Візуалізація результатів моделі")

    # 5.1. Графік прибутку за сценаріями
    st.subheader("Графік 1. Порівняння прибутку за сценаріями")

    profit_chart_df = results_df[["Сценарій", "Прибуток, грн"]].set_index("Сценарій")
    st.bar_chart(profit_chart_df)

    st.caption(
        "На графіку показано порівняння прибутку за трьома сценаріями моделі "
        "(песимістичний, базовий, оптимістичний), що дозволяє наочно оцінити, "
        "який з них є фінансово найпривабливішим."
    )

    # 5.2. Структура витрат (трансакційні + інші) за сценаріями
    st.subheader("Графік 2. Структура витрат за сценаріями")

    # Об'єднуємо всі витрати, крім трансакційних, у "Інші витрати"
    other_costs = (
        results_df["Логістичні витрати, грн"]
        + results_df["Інші змінні витрати, грн"]
        + results_df["Втрати від повернень, грн"]
        + results_df["Постійні витрати, грн"]
    )

    costs_chart_df = pd.DataFrame(
        {
            "Сценарій": results_df["Сценарій"],
            "Трансакційні витрати, грн": results_df["Трансакційні витрати, грн"],
            "Інші витрати, грн": other_costs,
        }
    ).set_index("Сценарій")

    st.bar_chart(costs_chart_df)

    st.caption(
        "Графік демонструє структуру витрат за сценаріями, з акцентом на частку "
        "трансакційних витрат у загальній сумі витрат інтернет-магазину."
    )

    # 5.3. Залежність трансакційних витрат від частки онлайн-оплат
    st.subheader("Графік 3. Залежність трансакційних витрат від частки онлайн-оплат")

    shares = [0, 20, 40, 60, 80, 100]
    tc_values = []

    for s in shares:
        tmp_params = ModelParams(
            orders_per_month=model_params.orders_per_month,
            avg_check=model_params.avg_check,
            share_online=s / 100.0,
            payment_commission=model_params.payment_commission,
            fixed_costs=model_params.fixed_costs,
            variable_cost_per_order=model_params.variable_cost_per_order,
            logistic_cost_per_order=model_params.logistic_cost_per_order,
            return_rate=model_params.return_rate,
        )
        df_s = calculate_scenarios(tmp_params, extra_items_for_calc)
        base_row = df_s[df_s["Сценарій"] == "Базовий"].iloc[0]
        tc_values.append(base_row["Трансакційні витрати, грн"])

    tc_dep_df = pd.DataFrame(
        {
            "Частка онлайн-оплат, %": shares,
            "Трансакційні витрати, грн": tc_values,
        }
    ).set_index("Частка онлайн-оплат, %")

    st.line_chart(tc_dep_df)

    st.caption(
        "Графік ілюструє залежність трансакційних витрат від частки онлайн-оплат. "
        "При зростанні частки онлайн-платежів зростає база нарахування комісії платіжного сервісу, "
        "що відображається у зміні обсягу трансакційних витрат."
    )

    # (Необов'язково) очистити показники, які відмічені як 'лише для цього розрахунку'
    st.markdown("---")
    if st.button("Очистити показники 'лише для цього розрахунку'"):
        st.session_state.extra_items = [
            item for item in st.session_state.extra_items  # type: ignore[attr-defined]
            if not item.use_only_once
        ]
        st.experimental_rerun()
