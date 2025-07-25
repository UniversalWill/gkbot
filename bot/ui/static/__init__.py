from services.static import StaticFile as _StaticFile


class Images:
    book_shelf = _StaticFile("./static/book_shelf.png")
    road_greet = _StaticFile("./static/road_greet.png")
    sort_documents = _StaticFile("./static/sort_documents.png")
    sorted_documents = _StaticFile("./static/sorted_documents.png")


class TextFiles:
    anecdotes = _StaticFile("./static/anecdots.txt", cache=False)
