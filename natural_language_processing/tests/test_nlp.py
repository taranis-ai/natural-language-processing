def test_app():
    from natural_language_processing.__init__ import create_app

    app = create_app()
    assert app
