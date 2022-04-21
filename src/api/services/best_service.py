from typing import List


def best_comparison_max(dct: dict, name, value):
    if dct['work_data'][name] < value:
        dct['work_data'][name] = value


def create_steps(keys: List[str], dct: dict, steps: int):
    for key in list(keys):
        t = dct['work_data'][key]
        dct['work_data'][f'{key}__steps'] = []
        for i in range(steps+1):
            q = t / steps * i
            dct['work_data'][f'{key}__steps'].append(q)

        # dct['work_data'][f'{key}__steps'].append(t)
