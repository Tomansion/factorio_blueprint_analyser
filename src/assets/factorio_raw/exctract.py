import ujson as json

# -----------------------------------------------------------
# Treat the big factorio_raw Json file,
# select the relevant data and store it in a new Json file
#
# It's easier to work with a more readable Json file
# -----------------------------------------------------------

data_file_path = "src/assets/factorio_raw/factorio_raw.json"
data_file_export_path = "src/assets/factorio_raw/factorio_raw_min.json"

key_to_keep = [
    "recipe",
    # "splitter",
    # "item-group",
    "underground-belt",
    # "infinity-container",
    "item",
    "container",
    "transport-belt",
    # "logistic-container",
    "recipe-category",
    "assembling-machine",
    # "furnace",
    "inserter"
]

entity_to_remove = [
    "big-ship",
    "crash-site",
    "factorio-logo"
]

key_to_remove = [
    "structure_patch",
    "close_sound",
    "open_sound",
    "working_sound",
    "vehicle_impact_sound",
    "resistances",
    "damaged_trigger_effect",
    "collision_box",
    "icon",
    "icons",
    "icon_mipmaps",
    "icon_size",
    "minable",
    "structure",
    "dying_explosion",
    "animation_speed_coefficient",
    "animation_sound",
    "animation",
    "belt_animation_set",
    "always_draw_idle_animation",
    "idle_animation",
    "water_reflection",
    "corpse",
    "health",
    "structure_animation_movement_cooldown",
    "max_health",
    "fast_replaceable_group",
    "structure_animation_speed_coefficient",
    "circuit_wire_max_distance",
    "circuit_connector_sprites",
    "circuit_wire_connection_point",
    "circuit_wire_connection_points",
    "picture",
    "order",
    "integration_patch",
    "logistic_mode",
    "opened_duration",
    "energy_source",
    "energy_usage",
    "drawing_box",
    "working_visualisations",
    "alert_icon_shift",
    "hand_base_picture",
    "default_stack_control_input_signal",
    "hand_base_shadow",
    "platform_picture",
    "hand_closed_shadow",
    "hand_open_shadow",
    "hand_closed_picture",
    "energy_per_movement",
    "energy_per_rotation",
    "hand_open_picture",
    "localised_name",
    "underground_sprite",
    "underground_remove_belts_sprite",
    "mined_sound",
    "repair_sound",
    "connector_frame_sprites",
]

with open(data_file_path, 'r') as f:
    raw_data = json.load(f)
    export_dict = {}

    # First we keep the firt level keys we want
    for key in key_to_keep:
        if key in raw_data:
            export_dict[key] = raw_data[key]
        else:
            print("Warning! Key not found: " + key)

    # Then we remove some of the entities
    for category in export_dict:
        entities = export_dict[category].keys()
        for entity in entities:
            for ent_to_rem in entity_to_remove:
                if ent_to_rem in entity:
                    del export_dict[category][entity]

    # Then we remove, in the object level 2, the keys we don't want
    for category in export_dict:
        for entity in export_dict[category]:
            for key in key_to_remove:
                if key in export_dict[category][entity]:
                    del export_dict[category][entity][key]

    with open(data_file_export_path, 'w') as f:
        json.dump(export_dict, f, indent=4)
