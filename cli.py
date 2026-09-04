from datetime import date

from booking_system import (
    BookingSystem,
    NotAvailableError,
    PropertyNotFoundError,
)


def print_menu():
    print("\n==========================")
    print("     BOOKING CHECKER")
    print("==========================")
    print("1. Ցուցադրել properties")
    print("2. Ավելացնել property")
    print("3. Ստուգել availability")
    print("4. Ստեղծել booking")
    print("5. Exit")


def read_date(prompt: str) -> date:

    while True:

        raw = input(
            f"{prompt} (YYYY-MM-DD): "
        ).strip()

        try:
            return date.fromisoformat(raw)

        except ValueError:
            print(
                "❌ Սխալ ամսաթիվ։ "
                "Օրինակ՝ 2026-09-01"
            )


def read_price() -> float:

    while True:

        try:
            price = float(
                input("Գին / գիշեր: ").strip()
            )

            if price <= 0:
                print("❌ Գինը պետք է լինի 0-ից մեծ։")
                continue

            return price

        except ValueError:
            print("❌ Մուտքագրիր թիվ։")


def main():

    system = BookingSystem()

    while True:

        print_menu()

        choice = input(
            "\nԸնտրիր գործողություն (1-5): "
        ).strip()

        # -------------------------
        # List properties
        # -------------------------

        if choice == "1":

            properties = system.list_properties()

            if not properties:
                print("\nProperty դեռ չկա։")
                continue

            print("\n--- Properties ---")

            for property_obj in properties:

                print(
                    f"\nID: {property_obj.property_id}"
                )

                print(
                    f"Name: {property_obj.name}"
                )

                print(
                    f"Price: "
                    f"${property_obj.price_per_night}/night"
                )

                print(
                    f"Bookings: "
                    f"{len(property_obj.bookings)}"
                )

        # -------------------------
        # Add property
        # -------------------------

        elif choice == "2":

            property_id = input(
                "Property ID: "
            ).strip()

            name = input(
                "Property name: "
            ).strip()

            price = read_price()

            try:

                system.add_property(
                    property_id,
                    name,
                    price,
                )

                print(
                    "\n✅ Property successfully added!"
                )

            except ValueError as error:
                print(f"\n❌ {error}")

        # -------------------------
        # Availability
        # -------------------------

        elif choice == "3":

            property_id = input(
                "Property ID: "
            ).strip()

            check_in = read_date("Check-in")

            check_out = read_date("Check-out")

            try:

                available = system.is_available(
                    property_id,
                    check_in,
                    check_out,
                )

                if available:
                    print("\n✅ Property is AVAILABLE!")

                    price = system.calculate_price(
                        property_id,
                        check_in,
                        check_out,
                    )

                    print(
                        f"Estimated price: ${price}"
                    )

                else:
                    print("\n❌ Property is NOT AVAILABLE.")

            except (
                PropertyNotFoundError,
                ValueError,
            ) as error:

                print(f"\n❌ {error}")

        # -------------------------
        # Create booking
        # -------------------------

        elif choice == "4":

            property_id = input(
                "Property ID: "
            ).strip()

            guest_name = input(
                "Guest name: "
            ).strip()

            check_in = read_date("Check-in")

            check_out = read_date("Check-out")

            try:

                booking = system.book(
                    property_id,
                    guest_name,
                    check_in,
                    check_out,
                )

                price = system.calculate_price(
                    property_id,
                    check_in,
                    check_out,
                )

                print("\n🎉 BOOKING CREATED!")

                print(
                    f"Guest: {booking.guest_name}"
                )

                print(
                    f"Dates: "
                    f"{booking.check_in} → "
                    f"{booking.check_out}"
                )

                print(
                    f"Nights: {booking.nights()}"
                )

                print(
                    f"Total price: ${price}"
                )

            except (
                NotAvailableError,
                PropertyNotFoundError,
                ValueError,
            ) as error:

                print(f"\n❌ Booking failed: {error}")

        # -------------------------
        # Exit
        # -------------------------

        elif choice == "5":

            print("\n👋 Goodbye!")

            break

        else:

            print(
                "\n❌ Անվավեր ընտրություն։"
            )


if __name__ == "__main__":
    main()