class PageOutOfRangeException(Exception):
    def __init__(self,book_pages, requested_pages):
        self.book_pages = book_pages
        self.requested_pages = requested_pages
        super().__init__(f"出错了，因为要求的页数({requested_pages})不在书的页数({book_pages})内")