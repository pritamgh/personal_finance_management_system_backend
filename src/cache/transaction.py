from sqlalchemy.orm import Session

from src.models import ExpenseCategory, ExpenseSubCategory, IncomeCategory


class CacheCategories:
    """
    A class that loads and caches all categories (income, expense, and expense subcategories)
    in memory to reduce the need for frequent database calls when accessing category names.

    This class serves as a caching layer to avoid querying the database every time
    category names are required. Once categories are loaded into memory, they can
    be accessed quickly without hitting the database again.

    Attributes:
        income_categories (dict): A dictionary where the key is the income category ID
                                   and the value is the income category name.
        expense_categories (dict): A dictionary where the key is the expense category ID
                                    and the value is the expense category name.
        expense_sub_categories (dict): A dictionary where the key is the expense subcategory ID
                                       and the value is the expense subcategory name.

    Methods:
        load_categories(db: Session):
            Loads income categories, expense categories, and expense subcategories from the database
            into the class's in-memory dictionaries.
    """

    def __init__(self):
        """
        Initializes the CacheCategories object with empty dictionaries for each category type:
        income, expense, and expense subcategories.
        """
        self.income_categories = {}
        self.expense_categories = {}
        self.expense_sub_categories = {}

    def load_categories(self, db: Session):
        """
        Loads all categories (income, expense, and expense subcategories) from the database
        into the in-memory dictionaries. This method performs a database query to retrieve
        the categories and stores them in the corresponding dictionaries for quick access.

        Args:
            db (Session): The SQLAlchemy database session used to interact with the database.

        Populates the following attributes:
            - income_categories
            - expense_categories
            - expense_sub_categories
        """
        queryset = db.query(IncomeCategory.id, IncomeCategory.category).all()
        for obj in queryset:
            self.income_categories[obj.id] = obj.category

        queryset = db.query(ExpenseCategory.id, ExpenseCategory.category).all()
        for obj in queryset:
            self.expense_categories[obj.id] = obj.category

        queryset = db.query(
            ExpenseSubCategory.id, ExpenseSubCategory.sub_category
        ).all()
        for obj in queryset:
            self.expense_sub_categories[obj.id] = obj.sub_category


cache_categories = CacheCategories()
