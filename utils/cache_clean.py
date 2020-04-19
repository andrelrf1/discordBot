import os


class CacheClean:
    __cache_path = None

    def __init__(self, cache_path: str):
        self.cache_path = cache_path

    @property
    def cache_path(self):
        return self.__cache_path

    @cache_path.setter
    def cache_path(self, path: str):
        if not isinstance(path, str):
            raise TypeError('O valor esperado é um str, não um int')

        if not os.path.isdir(path):
            raise FileNotFoundError(f'O sistema não encontrou o caminho especificado: "{path}"')

        self.__cache_path = path

    def cache_size(self):
        size = len(os.listdir(self.__cache_path))
        return size

    def cache_list(self):
        content_list = os.listdir(self.__cache_path)
        return content_list

    def cache_clean(self):
        files = self.cache_list()
        [os.remove(self.__cache_path + file) for file in files]


if __name__ == '__main__':  # Para testes
    if not os.path.isdir('coisa'):
        os.mkdir('coisa')
        print('path criado')

    teste = CacheClean('coisa')
    print(teste.cache_path)
    print(teste.cache_size())
