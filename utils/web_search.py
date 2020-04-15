from google import google


class Search:
    __search_from = 'stackoverflow.com'
    __number_of_pages = 1

    @property
    def search_from(self):
        return self.__search_from

    @search_from.setter
    def search_from(self, url: str):
        self.__search_from = url

    @property
    def number_of_pages(self):
        return self.__number_of_pages

    @number_of_pages.setter
    def number_of_pages(self, number):
        self.__number_of_pages = number

    def search(self, termo: str):
        results = []
        search_results = google.search(f'{termo} site:{self.__search_from}', self.__number_of_pages)
        for result in search_results:
            results.append({'nome': result.name, 'url': result.link})

        return results


if __name__ == '__main__':  # para testes
    search = Search()
    resultado = search.search('flutter')
    print(resultado)
    print(len(resultado))
