from background_task import background
from .services import generate_unique_link

@background(schedule=60)  # Планируем выполнение задачи каждые 60 секунд
def generate_unique_link_task():
    generate_unique_link()