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
        resultado_str = ''
        search_results = google.search(f'{termo} site:{self.__search_from}', self.__number_of_pages)
        for result in search_results:
            results.append({'nome': result.name, 'url': result.link})

        for resultado in results:
            for valor in resultado.values():
                resultado_str = resultado_str + valor + '\n'

            resultado_str = resultado_str + '\n'

        return resultado_str


if __name__ == '__main__':  # para testes
    # search = Search()
    # resultados = search.search('flutter')
    # result = ''
    # print(resultados)
    # for resultado in resultados:
    #     for valor in resultado.values():
    #         result = result + valor + '\n'
    #
    #     result = result + '\n'

    # print(result)
    # print(len(resultado))
    pass
