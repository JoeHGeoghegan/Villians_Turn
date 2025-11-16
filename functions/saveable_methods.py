import pandas as pd


def lookup_method(method_str):
    if method_str == "health_full_detail":
        return health_full_detail, ['health', 'max_health', 'temporary_health_function', 'temporary_health',
                                    'temporary_health_max']
    elif method_str == "health_curr_total":
        return health_curr_total, ['health', 'max_health', 'temporary_health_function', 'temporary_health',
                                   'temporary_health_max']
    elif method_str == "health_hp_and_max":
        return health_hp_and_max, ['health', 'max_health', 'temporary_health_function', 'temporary_health',
                                   'temporary_health_max']
    elif method_str == "health_pct":
        return health_pct, ['health', 'max_health', 'temporary_health_function', 'temporary_health',
                            'temporary_health_max']
    elif method_str == "health_vague":
        return health_vague, ['health', 'max_health', 'temporary_health_function', 'temporary_health',
                              'temporary_health_max']
    elif method_str == "armor_full_detail":
        return armor_full_detail, ['armor_class', 'ac_mod', 'ac_mod_function']
    elif method_str == "armor_total":
        return armor_total, ['armor_class', 'ac_mod', 'ac_mod_function']
    elif method_str == "armor_vague":
        return armor_vague, ['armor_class', 'ac_mod', 'ac_mod_function']
    elif method_str == "combo_initiative":
        return combo_initiative, ['initiative', 'initiative_bonus']
    else:
        raise ValueError(f"Unknown method string: {method_str}")


def health_full_detail(df_slice: pd.DataFrame,
                       show_set=True):  # ['health','max_health','temporary_health_function','temporary_health','temporary_health_max']
    def handle_row(row):
        if row['temporary_health_function'] == 'Set':
            health = row["temporary_health"] if row["temporary_health"] is not None else row["health"]
            health = f"*{health}*" if (row["temporary_health"] is not None and show_set) else f"{health}"
            max_health = row["temporary_health_max"] if row["temporary_health_max"] is not None else row["max_health"]
            max_health = f"*{max_health}*" if (
                        row["temporary_health_max"] is not None and show_set) else f"{max_health}"
            return f"{health}/{max_health}"
        else:  # Sum or None
            return f"({row['health']}+{row['temporary_health']})/({row['max_health']}+{row['temporary_health_max']})"

    return df_slice.apply(
        lambda row: handle_row(row),
        axis=1
    )


def health_curr_total(
        df_slice):  # ['health','max_health','temporary_health_function','temporary_health','temporary_health_max']
    def handle_row(row):
        if row['temporary_health_function'] == 'Set':
            return row["temporary_health"] if row["temporary_health"] is not None else row["health"]
        else:  # Sum but total isn't shown
            temp_health = row['temporary_health'] if row['temporary_health'] is not None else 0
            return row['health'] + temp_health

    return df_slice.apply(
        lambda row: handle_row(row),
        axis=1
    )


def health_hp_and_max(df_slice,
                      show_set=True):  # ['health','max_health','temporary_health_function','temporary_health','temporary_health_max']
    def handle_row(row):
        if row['temporary_health_function'] == 'Set':
            health = row["temporary_health"] if row["temporary_health"] is not None else row["health"]
            health = f"*{health}*" if (row["temporary_health"] is not None and show_set) else f"{health}"
            max_health = row["temporary_health_max"] if row["temporary_health_max"] is not None else row["max_health"]
            max_health = f"*{max_health}*" if (
                        row["temporary_health_max"] is not None and show_set) else f"{max_health}"
            return f"{health}/{max_health}"
        else:  # Sum or None
            temp_health = row['temporary_health'] if row['temporary_health'] is not None else 0
            temp_max = row['temporary_health_max'] if row['temporary_health_max'] is not None else 0
            return f"{row['health'] + temp_health}/{row['max_health'] + temp_max}"

    return df_slice.apply(
        lambda row: handle_row(row),
        axis=1
    )


def health_pct(
        df_slice):  # ['health','max_health','temporary_health_function','temporary_health','temporary_health_max']
    def handle_row(row):
        if row['temporary_health_function'] == 'Set':
            health = row["temporary_health"] if row["temporary_health"] is not None else row["health"]
            max_health = row["temporary_health_max"] if row["temporary_health_max"] is not None else row["max_health"]
            return "???" if (max_health <= 0
                             ) else f"{health / max_health * 100:.0f}%"
        else:  # Sum or None
            temp_health = float(row['temporary_health'] if row['temporary_health'] is not None else 0)
            temp_max = float(row['temporary_health_max'] if row['temporary_health_max'] is not None else 0)
            return "???" if ((row['max_health'] + temp_max) <= 0
                             ) else f"{float(row['health'] + temp_health) / float(row['max_health'] + temp_max) * 100:.0f}%"

    return df_slice.apply(
        lambda row: handle_row(row),
        axis=1
    )


def health_vague(
        df_slice):  # ['health','max_health','temporary_health_function','temporary_health','temporary_health_max']
    def vague(row):
        if row['temporary_health_function'] == 'Set':
            health = row["temporary_health"] if row["temporary_health"] is not None else row["health"]
            max_health = row["temporary_health_max"] if row["temporary_health_max"] is not None else row["max_health"]
            temp_health = 0
            temp_max = 0
        else:  # Sum or None
            health = row["health"]
            max_health = row["max_health"]
            temp_health = float(row['temporary_health'] if row['temporary_health'] is not None else 0)
            temp_max = float(row['temporary_health_max'] if row['temporary_health_max'] is not None else 0)

        hp_curr = float(health + temp_health)
        hp_max = float(max_health + temp_max)
        if hp_max == 0: return "???"
        pct = hp_curr / hp_max * 100
        if pct >= 100:
            return "Healthy"
        elif pct >= 90:
            return "Fine"
        elif pct >= 75:
            return "Lightly Injured"
        elif pct >= 50:
            return "Injured"
        elif pct >= 25:
            return "Heavily Injured"
        elif pct > 0:
            return "Near Death"
        else:
            return "Lost"

    return df_slice.apply(vague, axis=1)


def armor_full_detail(df_slice, show_set=False):  # ['armor_class','ac_mod','ac_mod_function']
    def handle_row(row):
        if row['ac_mod_function'] == 'Set':
            armor_class = row["ac_mod"] if row["ac_mod"] is not None else row["armor_class"]
            armor_class = f"*{armor_class}*" if (row["ac_mod"] is not None and show_set) else f"{armor_class}"
            return armor_class
        else:  # Sum or None
            return f"{row['armor_class']}+{row['ac_mod']}"

    return df_slice.apply(
        lambda row: handle_row(row),
        axis=1
    )


def armor_total(df_slice, show_set=True):  # ['armor_class','ac_mod','ac_mod_function']
    def handle_row(row):
        if row['ac_mod_function'] == 'Set':
            armor_class = row["ac_mod"] if row["ac_mod"] is not None else row["armor_class"]
            armor_class = f"*{armor_class}*" if (row["ac_mod"] is not None and show_set) else f"{armor_class}"
        else:  # Sum or None
            armor_class = row['armor_class'] + row['ac_mod']
        return armor_class

    return df_slice.apply(
        lambda row: handle_row(row),
        axis=1
    )


def armor_vague(df_slice):  # ['armor_class','ac_mod','ac_mod_function']
    def vague(row):
        if row['ac_mod_function'] == 'Set':
            defense = row["ac_mod"] if row["ac_mod"] is not None else row["armor_class"]
        else:  # Sum or None
            defense = row["armor_class"] + (float(row['ac_mod'] if row['ac_mod'] is not None else 0))
        if defense <= 5:
            return "Helpless"
        elif defense <= 8:
            return "Weak"
        elif defense <= 10:
            return "Unprepared"
        elif defense <= 12:
            return "Average"
        elif defense <= 14:
            return "Focused"
        elif defense <= 16:
            return "Sturdy"
        elif defense <= 18:
            return "Steadfast"
        elif defense <= 20:
            return "Ironclad"
        elif defense <= 22:
            return "Reinforced"
        elif defense < 25:
            return "Impregnable"
        elif defense >= 25:
            return "Invincible"
        else:
            return "Lost"

    return df_slice.apply(vague, axis=1)


def combo_initiative(df_slice):  # ['initiative','initiative_bonus']
    def handle_row(row):
        return f"{row['initiative_bonus']}->Rolled({row['initiative']})"

    return df_slice.apply(
        lambda row: handle_row(row),
        axis=1
    )
