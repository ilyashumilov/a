from core.celery import app


@app.task
def test_task(string_to_print: str):
    i = 0
    while i < 1:
        print(string_to_print)
        i += 1
