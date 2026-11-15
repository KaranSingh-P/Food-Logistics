# KaranSingh-P-Food-Logistics
## Food Logistics: Food Inventory and Nutrition Tracker


To open the functional version, open the `app.py` and run the python file.

For Login create your own account.

Note: You need Flask(python) and PostgreSQL for this project.
Note: The project needs a .env file to access the DB. Check `.env.example`.

## Tables in PostgreSQL
(The following values are examples.)

### users
Stores registered user accounts.
| user_id | email         | password_hash     |
| --------|-------------- |-------------------|
| 1       |test@email.com | password(in hash) |

### allergies (Needs scaling)
Stores the available allergy types.
| allergy_id | allergy_name |
|------------|--------------|
| 1          | Peanuts      |
 
### user_allergies
Links users to their selected allergies.
| user_id | allergy_id|
|---------|-----------|
| 1       | 2         |
| 1       | 5         |

### user_settings
Stores user-specific preferences.
| user_id | username | theme |
|---------|----------|-------|
| 1       | Gamer    | Dark  |

### inventory
Stores food items added by users.
|inventory_id | user_id | item_name | category  | purchase_date | expiration_date | created_at |
|-------------|---------|-----------|-----------|---------------|-----------------|------------|
| 1           | 1       | Apple     | Perisable | 2026-11-13    | 2026-11-20      | 2026-11-13 20:15:34.786959 |

### food_suggestions (Needs scaling)
Stores recognized food items and their categories.
| food_id | food_name | category |
|---------|-----------|----------|
| 1       | Apple     | Highly perishable |

### food_allergens (Scales with food_suggestions)
Maps recognized food items to their associated allergens.
| food_id | allergy_id |
|---------|------------| 
| 2       | 3          |

### inventory_verifications
Stores manual allergen verification decisions for individual inventory items.
| inventory_id | verification_status | allergy_id | verified_at          |
|--------------|---------------------|------------|----------------------|
| 5            | allergen_free        | NULL       | 2026-11-15 12:00:00  |
| 6            | allergic            | 3          | 2026-11-15 12:05:00  |

### recipes (Needs Scaling)
Stores the main information about each recipe.
| recipe_id	| recipe_name |	meal_type |	preparation_time |	servings |
|-----------|-------------|-----------|------------------|-----------|
| 1         |	Paneer Butter Masala |	Dinner   | 35    |	4        |
| 2         |	Vegetable Sandwich   |	Breakfast| 15    |	2        |

Additional columns: description, dietary_preferences, calories, protein, carbohydrates, fat, created_at.

### recipe_ingredients (Scales with recipes)
Stores the ingredients required for each recipe, including their individual amounts.
| recipe_ingredient_id | recipe_id |	ingredient_name |	amount |
|----------------------|-----------|--------------------|----------|
| 1                    | 1         | Paneer             | 200 g    |
| 2                    | 1         | Tomatoes           | 3 medium |
| 3                    | 2         | Bread              | 4 slices |
| 4                    | 2         | Butter             | 2 tbsp   |

### recipe_instructions (Scales with recipes)
Stores the step-by-step cooking instructions for each recipe.
| instruction_id |	recipe_id |	step_number |	title |	description |
|----------------|------------|-------------|---------|-------------|
| 1 | 1 | 1 | Prepare ingredients |	Chop the tomatoes and paneer.|
|2 | 1 | 2 |Cook the gravy | Heat butter and prepare the gravy. |
|3 | 2 | 1 |Prepare bread | Apply butter to the bread slices. |

### user_recipe_history
Contains history of all generated recipe.
| history_id | user_id | recipe_id | generated_at |
|------------|---------|-----------|--------------|
|            |         |           |              |

### active_shopping_lists
Stores each user's current active shopping list. Each user can have only one active list.

| list_id | user_id | created_at | updated_at |
|---|---|---|---|
| 1 | 1 | 2026-11-15 12:00:00 | 2026-11-15 12:00:00 |

### active_shopping_items
Stores individual items belonging to an active shopping list.

| item_id | list_id | food_id | item_name | quantity | is_completed | created_at |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | Apple | 2 kg | FALSE | 2026-11-15 12:05:00 |
| 2 | 1 | NULL | Homemade Bread | 1 loaf | TRUE | 2026-11-15 12:06:00 |

### shopping_history
Stores saved snapshots of users' shopping lists.

| history_id | user_id | saved_at |
|---|---|---|
| 1 | 1 | 2026-11-15 12:10:00 |
| 2 | 1 | 2026-11-16 09:30:00 |

### shopping_history_items
Stores the individual items and their bought status at the time a shopping list was saved.

| history_item_id | history_id | food_id | item_name | quantity | is_completed |
|---|---|---|---|---|---|
| 1 | 1 | 1 | Apple | 2 kg | FALSE |
| 2 | 1 | NULL | Homemade Bread | 1 loaf | TRUE |

### essential_foods
Stores the predefined essential food items displayed in the shopping list suggestions section, along with their display order.

| food_id | display_order |
|---------|---------------|
| 1       | 1             |
| 2       | 2             |
| 3       | 3             |


## Dashboard

The allergen alerts Table is functioning.

The expiring soon Table in functional.

Dashboard has the table for shopping list suggestions, that are supposed to be generated by flask. And based on the check boxes when the user clicks the [Generate List] button a list is generated and stored in the shopping list page|history. 

## Inventory

To Do -> Image recognition is left

Items are added permanently in the Database.

Inventory Loads → Flask matches items with food_suggestions → Checks food_allergens against user's selected allergies → Matching allergens appear in Allergen Alerts → Unrecognized items appear in Unverified Items → User manually verifies an item as allergen-free or allergic → If allergic, user selects an allergy or Unspecified → Flask validates and saves the verification in inventory_verifications → Tables are refreshed.

Add Items -> User enters characters -> User is suggested item name(if available) -> User either chooses the suggestion or simply presses enter -> Item info section appears with details such as types and dates -> User adds item -> item is sent to flask -> flask adds item to DB after validating values

Inventory table show following values:

| S.No.↑ | Name | Tag |	Date of Purchase | Manufacture | Date of Expiration | Action |
|--------|------|-----|------------------|-------------|--------------------|--------|

The following columns have functional sorting ability:
1. S.No.
2. Name
3. Date of Expiration 

The delete button and edit button are functional.
Pagination works correctly.


Food suggestions and allergen detection:

    Food Name              -> food_suggestions
    Food Category          -> food_suggestions
    Food ID                -> food_suggestions (Primary Key)
    Food Allergens         -> food_allergens (food_id, allergy_id)
    Allergy ID             -> allergies
    Verification Status    -> inventory_verifications
    Inventory ID           -> inventory_verifications

Inventory:

    Food Item              -> inventory
    Quantity | Category    -> inventory
    Purchase Date          -> inventory
    Expiration Date        -> inventory
    User ID                -> inventory (Foreign Key to users)



## Recipe Generation

The recipe generation system first filters recipes according to user preferences, then scores them based on inventory availability and expiring ingredients, avoids recent repetitions where possible, and finally selects one using weighted randomness.

Curently it has very few recipes, causing the recipes to often repeat.

    Recipe Details         -> recipes
    Recipe Ingredients     -> Recipe Ingredients Table
    Recipe Instructions   -> Recipe Instructions Table
    Generated Recipe       -> recipe_history
    User ID                -> recipe_history (Foreign Key to users)
    Recipe ID              -> recipe_history (Foreign Key to recipes)

To do: Add an option to add missing recipes to active shopping list.
To do: Use AI to generate missing recipes and then add them in DB. 

## Shopping List Generation
To do: Add an option to add missing recipes to active shopping list.

The shopping list system allows users to manually add food items or select from suggestions, specify quantities, edit or delete items, and mark items as completed. It tracks shopping progress and provides a summary of total, completed, and remaining items. Users can save active shopping lists to history, view and delete historical lists, and download both active and historical lists as text files. Clearing the active list does not affect saved history.

    Food Suggestions        -> food_suggestions
    Active Shopping List    -> active_shopping_lists
    Active Shopping Items   -> active_shopping_items
    Saved Shopping Lists    -> shopping_history
    Historical List Items   -> shopping_history_items
    User ID                 -> active_shopping_lists (Foreign Key to users)
    User ID                 -> shopping_history (Foreign Key to users)
    List ID                 -> active_shopping_items (Foreign Key to active_shopping_lists)
    History ID              -> shopping_history_items (Foreign Key to shopping_history)
    Food ID                 -> active_shopping_items (Foreign Key to food_suggestions)
    Food ID                 -> shopping_history_items (Foreign Key to food_suggestions)

## User Settings

The User setting is stored in permanently using the PostgreSQL tables - users, user_allergies, user_settings

    Username -> user_setting 
    Email(Fixed) <- users 
    Password -> users 
    Theme -> user_setting 
    Allergies -> user_allergies (as allergy_id of allergies table)

