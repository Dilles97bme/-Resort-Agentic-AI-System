import pandas as pd
from backend.database import SessionLocal
from backend.models.menu import MenuItem


def load_menu_from_excel(path):
    df = pd.read_excel(path)
    db = SessionLocal()

    for _, row in df.iterrows():
        item = MenuItem(
            item_name=row["Item Name"],
            description=row["Description"],
            price=row["Price (₹)"],
            available=True
        )
        db.add(item)

    db.commit()
    db.close()
    print("Menu loaded successfully.")


if __name__ == "__main__":
    load_menu_from_excel("Restaurant_Menu.xlsx")
