# KaranSingh-P-Food-Logistics
## Food Logistics: Food Inventory and Nutrition Tracker

## Steps to run the website

    Install the required Python dependencies.
    Install and configure PostgreSQL.
    Create the .env file using .env.example.
    Initialize the database and required tables.
    Run app.py.

For Login create your own account.

## Technologies Used

Frontend       -> HTML, CSS, JavaScript
Backend        -> Python, Flask
Database       -> PostgreSQL
Database Driver -> Psycopg
Environment Variables -> python-dotenv

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

### essential_foods (Needs scaling)
Stores the predefined essential food items displayed in the shopping list suggestions section, along with their display order.

| food_id | display_order |
|---------|---------------|
| 1       | 1             |
| 2       | 2             |
| 3       | 3             |


### shopping_templates
Stores user-created shopping list templates for reusing frequently purchased food items.
|template_id | user_id | created_at | updated_at |
|------------|---------|---------------------|---------------------|
|1           | 1       | 2026-11-15 12:00:00 | 2026-11-15 12:05:00 |

### shopping_template_items
Stores individual food items belonging to saved shopping templates, including their names, quantities and frequency information.
|template_item_id | template_id | food_id | item_name       | quantity | frequency |
|-----------------|-------------|---------|-----------------|----------|----------- |
|1                | 1           | 1       | Apple           | 2 kg     | frequent |
|2                | 1           | 2       | Banana          | 1 dozen  | occasional |
|3                | 1           | NULL    | Homemade Bread  | 1 loaf   | frequent |

## Dashboard

## Dashboard

The Dashboard provides an overview of important food management information.

1. Allergen Alerts: Displays inventory items associated with the user's selected allergies or manually verified allergen information.
2. Expiring Soon: Displays inventory items approaching their expiration dates.
3. Shopping List Suggestions: Displays a selection of automatically generated shopping suggestions.

The Shopping List Suggestions section supports selecting multiple items and adding them directly to the active shopping list. It also automatically scrolls when the user has been inactive for three seconds and pauses when the user interacts with the website.

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
    Recipe Ingredients     -> recipe_ingredients
    Recipe Instructions    -> recipe_instructions
    Generated Recipe       -> user_recipe_history
    User ID                -> user_recipe_history (Foreign Key to users)
    Recipe ID              -> user_recipe_history (Foreign Key to recipes)

To do: Use AI to generate missing recipes and then add them in DB. 

## Shopping List Generation

The Shopping List system allows users to manually add food items or select from automatically generated suggestions. Users can specify quantities, edit or delete items, and mark items as completed. The system tracks shopping progress and displays a summary of total, completed, and remaining items.

The suggestion system generates recommendations from four categories:
1. Essential Items: Food items recommended as essential shopping additions.
2. Near Expiry: Items in the user's inventory that are approaching their expiration dates, allowing users to plan their next purchase accordingly.
3. Previously Bought: Food items the user has purchased before, helping them conveniently add frequently purchased products again.
4. Templates: Items from previously saved shopping templates, excluding items already present in the inventory or active shopping list.
Users can select multiple suggestions and add them to their active shopping list. Duplicate items are detected to prevent the same food item from being added twice.

The system maintains one active shopping list per user. Users can save their active lists to shopping history, view or delete historical lists, and download both active and historical lists as text files. Clearing the active list does not affect previously saved history.


    Food Suggestions          -> food_suggestions
    Active Shopping List      -> active_shopping_lists
    Active Shopping Items     -> active_shopping_items
    Saved Shopping Lists      -> shopping_history
    Historical List Items     -> shopping_history_items
    Shopping Templates        -> shopping_templates
    Shopping Template Items   -> shopping_template_items

    User ID                   -> active_shopping_lists (Foreign Key to users)
    User ID                   -> shopping_history (Foreign Key to users)
    User ID                   -> shopping_templates (Foreign Key to users)

    List ID                   -> active_shopping_items (Foreign Key to active_shopping_lists)
    History ID                -> shopping_history_items (Foreign Key to shopping_history)
    Template ID               -> shopping_template_items (Foreign Key to shopping_templates)

    Food ID                   -> active_shopping_items (Foreign Key to food_suggestions)
    Food ID                   -> shopping_history_items (Foreign Key to food_suggestions)
    Food ID                   -> shopping_template_items (Foreign Key to food_suggestions)

## User Settings

The User setting is stored in permanently using the PostgreSQL tables - users, user_allergies, user_settings

    Username -> user_settings 
    Email(Fixed) <- users 
    Password -> users 
    Theme -> user_settings
    Allergies -> user_allergies (as allergy_id of allergies table)

