### CSV Format Details

OUT OF DATE - With character editor, this is likely no longer needed.

| Column           | Description                            | Data Type                   | Additional Details                                                                                                                     |
|------------------|----------------------------------------|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| name             | Character name                         | String                      | Required. No need for ""                                                                                                               |
| max_health       | Character's Max HP                     | Integer                     | Required.                                                                                                                              |
| current_health   | Character's Current HP                 | Integer                     | Useful for saving encounters, if blank will be set to Max HP                                                                           |
| temporary_health | Any Temporary Hit Points               | List of Length 2 or Integer | See Note                                                                                                                               |
| armor_class      | Character's Armor Class                | Integer                     | Required.                                                                                                                              |
| ac_mod           | If Character has modified Armor Class. | List of Length 2 or Integer | See Note                                                                                                                               |
| initiative       | Rolled initiative (For Saved Fights)   | Integer                     | Useful for saving encounters, if blank will be set to 0                                                                                |
| initiative_bonus | Character's Initiative Bonus           | Integer                     | If blank will be set to 0                                                                                                              |
| team             | Name of Team                           | String                      | Characters/Enemies have to be on the same team to be grouped                                                                           |
| group            | Name of Group                          | String                      | Useful for saving encounters, if blank will be set to individual group                                                                 |
| attributes       | Attributes associated with Character   | Dictionary of Lists         | Allows for Tracking Weapons, Feats, Magic, Inventory, Pets…Anything basically. Can be selected for contextual audit logging in actions |

Note: Can be Integer (positive or negative) or "SET:_VALUE_" where _VALUE_ will replace the max health or armor class
