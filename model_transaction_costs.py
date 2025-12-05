from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ExtraItem:
    # kind = "cost"    -> додається до витрат
    # kind = "revenue" -> віднімається від витрат
    name: str
    kind: str        # "cost" або "revenue"
    amount: float    # сума в грн


@dataclass
class ModelParams:
    Q: int
    avg_check: float
    p_loc: float
    p_int: float
    return_rate: float
    c_loc: float
    c_int: float
    c_ret_loc: float
    c_ret_int: float
    online_share: float
    pay_commission: float
    n_new_customers: int
    cac: float
    staff_fixed: float
    staff_per_order: float
    extra_items: List[ExtraItem] = field(default_factory=list)


def calc_logistics(params: ModelParams) -> float:
    delivery = params.Q * (params.p_loc * params.c_loc +
                           params.p_int * params.c_int)
    avg_ret_cost = params.p_loc * params.c_ret_loc + params.p_int * params.c_ret_int
    returns = params.Q * params.return_rate * avg_ret_cost
    return delivery + returns


def calc_payments(params: ModelParams) -> float:
    q_online = params.Q * params.online_share
    return q_online * params.avg_check * params.pay_commission


def calc_marketing(params: ModelParams) -> float:
    return params.n_new_customers * params.cac


def calc_staff(params: ModelParams) -> float:
    return params.staff_fixed + params.staff_per_order * params.Q


def calc_extra(params: ModelParams) -> Dict[str, float]:
    total_cost = 0.0
    total_revenue = 0.0
    for item in params.extra_items:
        if item.kind == "cost":
            total_cost += item.amount
        elif item.kind == "revenue":
            total_revenue += item.amount
    net = total_cost - total_revenue
    return {
        "extra_cost": total_cost,
        "extra_revenue": total_revenue,
        "extra_net": net,
    }


def calc_total(params: ModelParams) -> Dict[str, float]:
    logistics = calc_logistics(params)
    payments = calc_payments(params)
    marketing = calc_marketing(params)
    staff = calc_staff(params)
    extra = calc_extra(params)

    total = logistics + payments + marketing + staff + extra["extra_net"]

    return {
        "logistics": logistics,
        "payments": payments,
        "marketing": marketing,
        "staff": staff,
        "extra_cost": extra["extra_cost"],
        "extra_revenue": extra["extra_revenue"],
        "extra_net": extra["extra_net"],
        "total": total,
    }
