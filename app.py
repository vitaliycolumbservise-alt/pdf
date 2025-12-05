#Веб-моделювання трансакційних витрат.
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

# прапорець для блоку порівняння
if "compare_clicked" not in st.session_state:
    st.session_state["compare_clicked"] = False

# Значення за замовчуванням (2024)
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

Q = st.number_input("Кількість замовлень", min_value=0, max_value=100000, value=default.Q, step=100)
avg_check = st.number_input("Середній чек (грн)", min_value=0.0, max_value=10000.0, value=float(default.avg_check), step=10.0)

p_loc = st.slider("Частка локальних доставок", 0.0, 1.0, float(default.p_loc), 0.05)
p_int = 1.0 - p_loc

return_rate = st.slider("Рівень повернень (частка)", 0.0, 1.0, float(default.return_rate), 0.001, format="%.3f")

c_loc = st.number_input("Вартість локальної доставки, грн", 0.0, 500.0, float(default.c_loc), 5.0)
c_int = st.number_input("Вартість міжобласної доставки, грн", 0.0, 500.0, float(default.c_int), 5.0)

c_ret_loc = st.number_input("Вартість повернення локальної доставки, грн", 0.0, 200.0, float(default.c_ret_loc), 1.0)
c_ret_int = st.number_input("Вартість повернення міжобласної доставки, грн", 0.0, 200.0, float(default.c_ret_int), 1.0)

online_share = st.slider("Частка онлайн-оплат", 0.0, 1.0, float(default.online_share), 0.05)

pay_commission_percent = st.number_input("Комісія платіжного сервісу (%)", 0.0, 10.0, float(default.pay_commission * 100), 0.1)
pay_commission = pay_commission_percent / 100.0

n_new_customers = st.number_input("Залучені клієнти", 0, 50000, default.n_new_customers, 100)
cac = st.number_input("CAC (грн)", 0.0, 200.0, float(default.cac), 1.0)

staff_fixed = st.number_input("Фіксовані витрати на персонал, грн", 0.0, 10000000.0, float(default.staff_fixed), 10000.0)
staff_per_order = st.number_input("Витрати на обробку одного замовлення, грн", 0.0, 200.0, float(default.staff_per_order), 1.0)

# --- ДОДАТКОВІ ПОКАЗНИКИ ---
st.subheader("Додатковий показник (за бажанням)")
add_extra = st.checkbox("Додати додатковий показник до поточного сценарію")
extra_items = []

if add_extra:
    extra_kind_label = st.radio(
        "Тип показника",
        ["Додаткові витрати (+ до витрат)", "Додатковий дохід (– до витрат)"],
    )
    extra_name = st.text_input("Назва показника")
    extra_amount = st.number_input("Сума показника, грн", min_value=0.0, value=0.0, step=10.0)

    if extra_name and extra_amount > 0:
        kind = "cost" if extra_kind_label.startswith("Додаткові витрати") else "revenue"
        extra_items.append(ExtraItem(name=extra_name.strip(), kind=kind, amount=extra_amount))

# --- РОЗРАХУНОК ---
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

    st.session_state["scenarios"].append(
        {"id": len(st.session_state["scenarios"]) + 1, "params": params, "result": result}
    )

    st.session_state["compare_clicked"] = False

    st.success(f"Сценарій №{len(st.session_state['scenarios'])} успішно розраховано.")

# --- ВИВЕДЕННЯ РЕЗУЛЬТАТУ ---
if st.session_state["scenarios"]:
    last = st.session_state["scenarios"][-1]
    res = last["result"]

    st.subheader(f"Результати останнього розрахунку (сценарій №{last['id']})")

    table = [
        {"№": 1, "Стаття": "Логістика", "Сума, грн": f"{res['logistics']:.2f}"},
        {"№": 2, "Стаття": "Платіжні сервіси", "Сума, грн": f"{res['payments']:.2f}"},
        {"№": 3, "Стаття": "Маркетинг", "Сума, грн": f"{res['marketing']:.2f}"},
        {"№": 4, "Стаття": "Персонал", "Сума, грн": f"{res['staff']:.2f}"},
    ]

    if res["extra_net"] != 0:
        sign = "+" if res["extra_net"] > 0 else "-"
        table.append({"№": 5, "Стаття": "Додаткові показники", "Сума, грн": f"{res['extra_net']:.2f} ({sign})"})
        row_total = 6
    else:
        row_total = 5

    table.append({"№": row_total, "Стаття": "Разом", "Сума, грн": f"{res['total']:.2f}"})

    st.table(pd.DataFrame(table).set_index("№"))

    count = len(st.session_state["scenarios"])

    if count == 1:
        st.info("Це перший розрахунок. Ви можете змінити показники та додати новий сценарій.")
    else:
        st.write(f"Всього розраховано сценаріїв: {count}")

        col1, col2 = st.columns(2)
        with col1:
            st.info("Щоб додати ще один сценарій, змініть показники і натисніть «Розрахувати».")
        with col2:
            if st.button("Провести порівняння"):
                st.session_state["compare_clicked"] = True

        # --- БЛОК ПОРІВНЯННЯ ---
        if st.session_state["compare_clicked"]:

            st.subheader("Порівняння сценаріїв")

            comp_rows = []
            for s in st.session_state["scenarios"]:
                pr = s["params"]
                rr = s["result"]
                extras = "; ".join(
                    f"{item.name} ({'+' if item.kind=='cost' else '-'}{item.amount:.2f})"
                    for item in pr.extra_items
                ) if pr.extra_items else "-"

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

            # --- ГРАФІК ---
            st.subheader("Графік залежності")

            numeric_rows = []
            for s in st.session_state["scenarios"]:
                pr = s["params"]
                rr = s["result"]
                numeric_rows.append(
                    {
                        "Сценарій": s["id"],
                        "Q": pr.Q,
                        "Середній чек": pr.avg_check,
                        "Локальні доставки": pr.p_loc,
                        "Повернення %": pr.return_rate * 100,
                        "Онлайн-оплати %": pr.online_share * 100,
                        "Комісія %": pr.pay_commission * 100,
                        "CAC": pr.cac,
                        "Фіксовані": pr.staff_fixed,
                        "Змінні": pr.staff_per_order,
                        "Разом": rr["total"],
                        "Логістика": rr["logistics"],
                        "Маркетинг": rr["marketing"],
                        "Платіжні": rr["payments"],
                        "Персонал": rr["staff"],
                    }
                )

            plot_df = pd.DataFrame(numeric_rows).set_index("Сценарій")

            x_metric = st.selectbox("Показник по осі X", plot_df.columns, index=list(plot_df.columns).index("Онлайн-оплати %"))
            y_metrics = st.multiselect("Показники по осі Y", plot_df.columns, default=["Разом"])

            if y_metrics:
                st.line_chart(plot_df[[x_metric] + y_metrics].set_index(x_metric).sort_index())

            # --- ВИСНОВОК ---
            best = min(st.session_state["scenarios"], key=lambda x: x["result"]["total"])
            best_total = best["result"]["total"]
            base_total = st.session_state["scenarios"][0]["result"]["total"]
            diff = base_total - best_total

            st.subheader("Висновок")

            if diff > 0:
                st.write(f"Найменші витрати у сценарії №{best['id']} ({best_total:.2f} грн). "
                         f"Економія відносно базового: {diff:.2f} грн.")
            elif diff < 0:
                st.write(f"Витрати у сценарії №{best['id']} зросли на {abs(diff):.2f} грн порівняно з базовим.")
            else:
                st.write("Витрати співпадають з базовим сценарієм.")

            if st.button("Почати спочатку"):
                st.session_state["scenarios"] = []
                st.session_state["compare_clicked"] = False
                st.experimental_rerun()

else:
    st.info("Заповніть параметри вище і натисніть кнопку **«Розрахувати»**.")
