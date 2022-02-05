from jinja2 import Environment


def settings_doc_initialize_environment(env: Environment) -> None:
    pass


def settings_doc_pre_render(render_kwargs: dict) -> dict:
    return render_kwargs
