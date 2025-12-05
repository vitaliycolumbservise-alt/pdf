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

# прапорець для показу блоку порівняння
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

# Додатковий показник
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
    # При новому розрахунку вимикаємо порівняння і графік
    st.session_state["compare_clicked"] = False
    st.session_state["show_chart"] = False

    st.success(
        f"Сценарій №{len(st.session_state['scenarios'])} успішно розраховано."
    )

# Вивід останнього сценарію
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

    if res["extra_net"] != 0:
        sign = "+" if res["extra_net"] > 0 else "-"
        table.append(
            {
                "№": 5,
                "Стаття": "Додаткові показники",
                "Сума, грн": f"{res['extra_net']:.2f} ({sign})",
            }
        )
        row_total = 6
    else:
        row_total = 5

    table.append(
        {"№": row_total, "Стаття": "Разом", "Сума, грн": f"{res['total']:.2f}"}
    )
    df = pd.DataFrame(table).set_index("№")
    st.table(df)

    count = len(st.session_state["scenarios"])

    if count == 1:
        st.info(
            "Це перший розрахунок. Ви можете змінити показники та натиснути "
            "«Розрахувати» ще раз, щоб додати новий сценарій."
        )
    else:
        st.write(f"Всього розраховано сценаріїв: {count}")
        col1, col2 = st.columns(2)
        with col1:
            st.info(
                "Щоб додати ще один сценарій, змініть показники вище і натисніть «Розрахувати»."
            )
        with col2:
            if st.button("Провести порівняння"):
                st.session_state["compare_clicked"] = True
                st.session_state["show_chart"] = False

        # --- Блок порівняння сценаріїв ---
        if st.session_state["compare_clicked"]:
            st.subheader("Порівняння сценаріїв")

            comp_rows = []
            for s in st.session_state["scenarios"]:
                pr = s["params"]
                rr = s["result"]

                if pr.extra_items:
                    extras = "; ".join(
                        f"{item.name} ({'+' if item.kind=='cost' else '-'}{item.amount:.2f})"
                        for item in pr.extra_items
                    )
                else:
                    extras = "-"

                comp_rows.append(
                    {
                        "Сценарій": s["id"],
                        "Q (замовлення)": pr.Q,
                        "Середній чек, грн": f"{pr.avg_check:.2f}",
                        "Частка локальних доставок": f"{pr.p_loc:.3f}",
                        "Частка міжобласних": f"{pr.p_int:.3f}",
                        "Рівень повернень": f"{pr.return_rate:.4f}",
                        "Вартість локальної доставк., грн": f"{pr.c_loc:.2f}",
                        "Вартість міжобласної доставк., грн": f"{pr.c_int:.2f}",
                        "Повернення локал., грн": f"{pr.c_ret_loc:.2f}",
                        "Повернення міжобл., грн": f"{pr.c_ret_int:.2f}",
                        "Частка онлайн оплат": f"{pr.online_share:.3f}",
                        "Комісія платіжного сервісу, %": f"{pr.pay_commission*100:.2f}",
                        "Залучені клієнти": pr.n_new_customers,
                        "CAC, грн": f"{pr.cac:.2f}",
                        "Фіксовані витрати персонал, грн": f"{pr.staff_fixed:.2f}",
                        "Змінні витрати на замовлення, грн": f"{pr.staff_per_order:.2f}",
                        "Додаткові показники": extras,
                        "Логістика, грн": f"{rr['logistics']:.2f}",
                        "Платіжні сервіси, грн": f"{rr['payments']:.2f}",
                        "Маркетинг, грн": f"{rr['marketing']:.2f}",
                        "Персонал, грн": f"{rr['staff']:.2f}",
                        "Додаткові, грн": f"{rr['extra_net']:.2f}",
                        "Разом, грн": f"{rr['total']:.2f}",
                    }
                )

            comp_df = pd.DataFrame(comp_rows).set_index("Сценарій")
            st.dataframe(comp_df, use_container_width=True)

            # --- Графік: кілька X (вибір), Y = «Разом, грн», один графік ---
            st.subheader("Графік залежності загальних трансакційних витрат")

            # Формуємо окремий DataFrame з числовими значеннями по сценаріях
            plot_rows = []
            for s in st.session_state["scenarios"]:
                pr = s["params"]
                rr = s["result"]
                plot_rows.append(
                    {
                        "Сценарій": s["id"],
                        "Q (замовлення)": pr.Q,
                        "Середній чек, грн": pr.avg_check,
                        "Частка локальних доставок": pr.p_loc,
                        "Частка міжобласних": pr.p_int,
                        "Рівень повернень, %": pr.return_rate * 100,
                        "Частка онлайн оплат, %": pr.online_share * 100,
                        "Комісія платіжного сервісу, %": pr.pay_commission * 100,
                        "Залучені клієнти": pr.n_new_customers,
                        "CAC, грн": pr.cac,
                        "Фіксовані витрати персонал, грн": pr.staff_fixed,
                        "Змінні витрати на замовлення, грн": pr.staff_per_order,
                        "Логістика, грн": rr["logistics"],
                        "Платіжні сервіси, грн": rr["payments"],
                        "Маркетинг, грн": rr["marketing"],
                        "Персонал, грн": rr["staff"],
                        "Додаткові, грн": rr["extra_net"],
                        "Разом, грн": rr["total"],
                    }
                )

            plot_df = pd.DataFrame(plot_rows).set_index("Сценарій")
            metric_options = list(plot_df.columns)

            # фіксований Y
            y_metric = "Разом, грн" if "Разом, грн" in metric_options else metric_options[-1]

            # кнопка показу графіка
            if st.button("Створити графік"):
                st.session_state["show_chart"] = True

            if st.session_state["show_chart"]:
                options_for_x = [m for m in metric_options if m != y_metric]

                default_x = []
                if "Частка онлайн оплат, %" in options_for_x:
                    default_x.append("Частка онлайн оплат, %")
                elif "Q (замовлення)" in options_for_x:
                    default_x.append("Q (замовлення)")
                elif options_for_x:
                    default_x.append(options_for_x[0])

                x_candidates = st.multiselect(
                    "Показники, які аналізувати по осі X",
                    options=options_for_x,
                    default=default_x,
                )

                if not x_candidates:
                    st.info("Оберіть хоча б один показник по осі X, щоб побудувати графік.")
                else:
                    active_x = st.selectbox(
                        "Активний показник по осі X для відображення на графіку",
                        options=x_candidates,
                    )

                    chart_df = (
                        plot_df[[active_x, y_metric]]
                        .sort_values(active_x)
                        .set_index(active_x)
                    )
                    st.line_chart(chart_df)

                    st.caption(
                        f"На графіку показано залежність загальної суми трансакційних витрат "
                        f"(«{y_metric}») від вибраного показника по осі X («{active_x}») "
                        "для всіх розрахованих сценаріїв. За допомогою мультивибору "
                        "можна обрати кілька показників для аналізу та швидко перемикатися "
                        "між ними через список активного показника."
                    )

            # --- Висновок (твоє оригінальне текстове пояснення) ---

            best = min(
                st.session_state["scenarios"],
                key=lambda x: x["result"]["total"],
            )
            best_total = best["result"]["total"]
            base = st.session_state["scenarios"][0]
            base_total = base["result"]["total"]
            diff = base_total - best_total

            st.subheader("Висновок")

            text = []
            text.append(
                f"Найменші трансакційні витрати отримано у **сценарії №{best['id']}** "
                f"із загальною сумою **{best_total:.2f} грн**."
            )

            if diff > 0:
                text.append(
                    f"Порівняно з базовим сценарієм №1, економія становить "
                    f"**{diff:.2f} грн**, що свідчить про доцільність впровадження "
                    f"відповідних змін у параметрах моделі."
                )
            elif diff < 0:
                text.append(
                    f"Порівняно з базовим сценарієм №1, витрати зросли на "
                    f"**{-diff:.2f} грн**, тобто запропоновані зміни є економічно "
                    f"недоцільними."
                )
            else:
                text.append(
                    "Загальні витрати збігаються з базовим сценарієм, тобто суттєвий "
                    "економічний ефект від змін параметрів відсутній."
                )

            p = best["params"]
            text.append(
                "Найкращий сценарій характеризується такими ключовими параметрами: "
                f"кількість замовлень – {p.Q}, середній чек – {p.avg_check:.2f} грн, "
                f"частка локальних доставок – {p.p_loc:.2f}, рівень повернень – "
                f"{p.return_rate:.3f}, частка онлайн-оплат – {p.online_share:.2f}, "
                f"ставка комісії платіжного сервісу – {p.pay_commission * 100:.2f} %, "
                f"кількість нових клієнтів – {p.n_new_customers}, CAC – {p.cac:.2f} грн, "
                f"фіксовані витрати на персонал – {p.staff_fixed:.2f} грн, "
                f"змінні витрати на обробку одного замовлення – "
                f"{p.staff_per_order:.2f} грн."
            )

            if p.extra_items:
                extra_parts = []
                for item in p.extra_items:
                    mark = "+" if item.kind == "cost" else "-"
                    extra_parts.append(
                        f"{item.name} ({mark}{item.amount:.2f} грн)"
                    )
                text.append(
                    "У найкращому сценарії додатково враховано такі показники: "
                    + "; ".join(extra_parts)
                    + "."
                )

            text.append(
                "Таким чином, обраний сценарій забезпечує більш вигідне поєднання "
                "обсягу замовлень, структури доставки, рівня повернень, вартості "
                "залучення клієнтів та витрат на персонал, що в результаті знижує "
                "загальну суму трансакційних витрат інтернет-магазину BagShop."
            )

            st.write("\n\n".join(text))

            if st.button("Почати спочатку"):
                st.session_state["scenarios"] = []
                st.session_state["compare_clicked"] = False
                st.session_state["show_chart"] = False
                st.experimental_rerun()

else:
    st.info(
        "Заповніть параметри вище і натисніть кнопку **«Розрахувати»**."
    )



