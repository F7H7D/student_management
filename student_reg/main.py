"""Application entry point for Parishilon Academy."""

from __future__ import annotations


def main() -> None:
    try:
        from kivy_app.app import ParishilonAcademyApp
    except ModuleNotFoundError as exc:
        if exc.name != "kivy":
            raise

        from gui.dashboard import Dashboard

        app = Dashboard()
        app.mainloop()
        return

    ParishilonAcademyApp().run()


if __name__ == "__main__":
    main()