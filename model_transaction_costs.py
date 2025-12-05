from dataclasses import dataclass
from typing import List
import pandas as pd


@dataclass
class ExtraItem:
    """
    Додатковий показник (витрата або дохід), який користувач може додати в інтерфейсі.
    """
    name: str
    value: float
    is_revenue: bool  # True = дохід (+), False = витрата (-)
    use_only_once: bool  # True = враховувати тільки в поточному розрахунку


@dataclass
class ModelParams:
    """
    Базові параметри моделі інтернет-магазину.
    Значення за замовчуванням – орієнтовні, їх можна налаштовувати в app.py.
    """
    orders_per_month: int = 10900          # кількість замовлень на місяць
    avg_check: float = 800.0               # середній чек, грн
    share_online: float = 0.6              # частка онлайн-оплат (0..1)
    payment_commission: float = 0.015      # комісія платіжного сервісу (LiqPay/WayForPay тощо)
    fixed_costs: float = 100_000.0         # постійні витрати (оренда, зарплата тощо)
    variable_cost_per_order: float = 150.0 # змінні витрати на одне замовлення
    logistic_cost_per_order: float = 90.0  # логістика на одне замовлення
    return_rate: float = 0.05              # частка повернень замовлень (0..1)


def _calc_for_one_scenario(
    name: str,
    params: ModelParams,
    orders_multiplier: float,
    return_multiplier: float,
    extra_items: List[ExtraItem],
) -> dict:
    """
    Розрахунок основних показників для одного сценарію.
    """
    orders = int(params.orders_per_month * orders_multiplier)
    avg_check = params.avg_check

    # Дохід
    revenue = orders * avg_check

    # Трансакційні витрати (комісія платіжного сервісу)
    online_orders = orders * params.share_online
    transaction_costs = online_orders * avg_check * params.payment_commission

    # Логістика та змінні витрати
    logistic_costs = orders * params.logistic_cost_per_order
    variable_costs = orders * params.variable_cost_per_order

    # Втрати від повернень
    returns_rate = params.return_rate * return_multiplier
    returns_costs = orders * returns_rate * avg_check

    # Постійні витрати
    fixed_costs = params.fixed_costs

    # Додаткові показники (витрати/доходи)
    extra_costs = 0.0
    extra_revenues = 0.0
    for item in extra_items:
        if item.is_revenue:
            extra_revenues += item.value
        else:
            extra_costs += item.value

    # Підсумок
    total_costs = (
        transaction_costs
        + logistic_costs
        + variable_costs
        + returns_costs
        + fixed_costs
        + extra_costs
    )
    total_revenue = revenue + extra_revenues
    profit = total_revenue - total_costs

    return {
        "Сценарій": name,
        "Замовлення, шт": orders,
        "Дохід, грн": round(total_revenue, 2),
        "Трансакційні витрати, грн": round(transaction_costs, 2),
        "Логістичні витрати, грн": round(logistic_costs, 2),
        "Інші змінні витрати, грн": round(variable_costs, 2),
        "Втрати від повернень, грн": round(returns_costs, 2),
        "Постійні витрати, грн": round(fixed_costs + extra_costs, 2),
        "Прибуток, грн": round(profit, 2),
    }


def calculate_scenarios(params: ModelParams, extra_items: List[ExtraItem]) -> pd.DataFrame:
    """
    Розрахунок трьох сценаріїв: песимістичний, базовий, оптимістичний.
    Повертає DataFrame, який зручно показувати у Streamlit.
    """
    scenarios = []

    # Песимістичний сценарій: менше замовлень, більше повернень
    scenarios.append(
        _calc_for_one_scenario(
            name="Песимістичний",
            params=params,
            orders_multiplier=0.8,
            return_multiplier=1.3,
            extra_items=extra_items,
        )
    )

    # Базовий сценарій
    scenarios.append(
        _calc_for_one_scenario(
            name="Базовий",
            params=params,
            orders_multiplier=1.0,
            return_multiplier=1.0,
            extra_items=extra_items,
        )
    )

    # Оптимістичний сценарій: більше замовлень, менше повернень
    scenarios.append(
        _calc_for_one_scenario(
            name="Оптимістичний",
            params=params,
            orders_multiplier=1.2,
            return_multiplier=0.7,
            extra_items=extra_items,
        )
    )

    df = pd.DataFrame(scenarios)
    return df
